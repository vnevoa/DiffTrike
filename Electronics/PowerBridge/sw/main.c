/**
 * Power H-Bridge Controller Fw
 *
 * Copyright (c) 2010-2014 Nuno João
 * http://www.EmbeddedDreams.com
 *
 * This file is part of DiffTrike.
 *
 * DiffTrike is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * DiffTrike is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with DiffTrike. If not, see <http://www.gnu.org/licenses/>.
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include <util/delay.h>
#include "i2c_slave.h"


//#define SIMULATOR
#define DISABLE_EEPROM_WRITE
//#define DISABLE_TIMER_TICK
//#define DISABLE_ADC
//#define DISABLE_PWM


// This value can be read from an I2C register
#define FW_VERSION  0x16        // 0 x <major> <minor>

#define ON      1
#define OFF     0
#define true    1
#define false   0

#define word    uint16_t
#define bool    byte


/*/ AVR ADC internal Vref - chip dependant
#ifdef WHITEDOTCHIP
#   define VREFx10  27     // white dot chip 2.73V
#else
#   define VREFx10  28     // no white dot chip
#endif*/

#define MIN_MOTOR_VCC           22  // V
#define MAX_CURRENT             20  // A
#define MAX_TEMPERATURE         60  //ºC

#define PWM_VALUE_HB1           OCR1A
#define PWM_VALUE_HB2           OCR1B

#define MIN_PWM     29

#define PFWMODE     ON

#define PortRead(port_letter, bits)     (PIN ## port_letter & (bits))
#define PortSet(port_letter, bits)      PORT ## port_letter |= (bits)
#define PortClear(port_letter, bits)    PORT ## port_letter &= ~(bits)
#define PortToggle(port_letter, bits)   PORT ## port_letter ^= (bits)


enum {
    eI2CaddrSel     = _BV(PA0),
    eBridgeTemp     = _BV(PA1),
    eMotorTemp      = _BV(PA2),
    ePA3            = _BV(PA3),
    eOCA            = _BV(PA4),
    eVccSense       = _BV(PA5),
    eIsense         = _BV(PA6),
    eLED            = _BV(PA7),

    eSDA            = _BV(PB0),
    eHB1_L          = _BV(PB1),     // PWM OC1A
    eSCL            = _BV(PB2),
    eHB2_L          = _BV(PB3),     // PWM OC1B
    eHB1_H          = _BV(PB4),
    eHB2_H          = _BV(PB5),
    ePB6            = _BV(PB6),
    eRESET          = _BV(PB7),
};


// The registers we support. Can be read, some written, through I2C:
enum {
    eI2cReg_Command         = 0,    // R/W   command
    eI2cReg_Status          = 1,    //   R   status
    eI2cReg_Speed           = 2,    // R/W   speed
    eI2cReg_Acceleration    = 3,    // R/W   acceleration
    eI2cReg_Temperature     = 4,    //   R   temperature
    eI2cReg_MotorCurrent    = 5,    //   R   motor current
    eI2cReg_MotorVcc        = 6,    //   R   motor Vcc
    eI2cReg_SwRevision      = 7,    //   R   sw revision
};

// Status register bit flags
enum {
    eStatus_Accelerating            = _BV(0),
    eStatus_Overcurrent_Limiter     = _BV(1),
    eStatus_Overtemp_Limiter        = _BV(2),
    eStatus_UnderVcc_Limiter        = _BV(3),

    eStatus_Limiter_Mask            = eStatus_Overcurrent_Limiter
                                    | eStatus_Overtemp_Limiter
                                    | eStatus_UnderVcc_Limiter
};

// Commands for the Command Register
enum {
    // Util commands
    eCmd_Reset = 0,
    eCmd_SetI2cAddr,
    eCmd_SetVref,
    eCmd_GetVref,
    // Debug commands
    eCmd_GetPinA,
    eCmd_GetPinB,
    eCmd_GetAdc0,
    eCmd_GetAdc1,
    eCmd_GetAdc2,
    eCmd_GetAdc3,
    eCmd_GetAdc4,
    eCmd_GetAdc5,
    eCmd_SetPwmFreq8KHz,
    eCmd_SetPwmFreq15KHz,
    eCmd_SetPwmPres = 0xF0,
};


// Configuration params data structure.
typedef struct {
    byte    adcVrefx10;
    byte    i2cAddr;
} TEECfg;


// Configuration parameters.
static TEECfg  gCfg;

static byte  gCurrSpeed = 0;
static byte  gCurrAcc = 0;


// Our own sleep function. AVR libc's sleep_mode() will always enable sleep mode on
// entry and disable it on exit, which takes up 4 instructions. We need that time.
static inline void sleep (void)
{
    asm volatile("sleep");
}


static void delayMs (unsigned short ms)
{
#  ifndef SIMULATOR
    while (ms--)
        _delay_ms(1);
#  endif
}


static void clear_timer_flags (void)
{
    TIFR |= _BV(TOV1);
    TIFR |= _BV(OCF1A) | _BV(OCF1B);
}


static inline void OCAInterrupt (bool on)
{
    if (on)
        GIMSK |= _BV(PCIE1);
    else
        GIMSK &= ~_BV(PCIE1);
}


static inline void TopHB1 (bool on)
{
    if (on)
    {
        PORTB |=  eHB1_H;
    }
    else
    {
        PORTB &= ~eHB1_H;
    }
}

static inline void TopHB2 (bool on)
{
    if (on)
    {
        PORTB |=  eHB2_H;
    }
    else
    {
        PORTB &= ~eHB2_H;
    }
}

static inline void BotHB1 (bool on)
{
    // bottom drivers are inverting
    if (on)
    {
        PORTB &= ~eHB1_L;
    }
    else
    {
        PORTB |=  eHB1_L;
    }
}

static inline void BotHB2 (bool on)
{
    // bottom drivers are inverting
    if (on)
    {
        PORTB &= ~eHB2_L;
    }
    else
    {
        PORTB |=  eHB2_L;
    }
}


static void AllOff (void)
{
    // Disable interrupts Overflow, OutputCompare A and B
    TIMSK &= ~ (_BV(TOIE1) | _BV(OCIE1A) | _BV(OCIE1B));
    TopHB1(OFF);
    TopHB2(OFF);
    BotHB1(OFF);
    BotHB2(OFF);
}


static void DissipativeBreak (void)
{
    TopHB1(OFF);
    TopHB2(OFF);
    _delay_us(1);
    BotHB1(ON);
    BotHB2(ON);
}


static inline byte isFwd (void)
{
    return TIMSK & _BV(OCIE1A);
}


static void FwOff (void)
{
    BotHB1(OFF);
    _delay_us(1.5);
    TopHB1(PFWMODE);
}


static void BkwOff (void)
{
    BotHB2(OFF);
    _delay_us(1.5);
    TopHB2(PFWMODE);
}


// Note: to be invoked with interrupts disabled
static inline void GoFw (byte val)
{
    if (gCurrSpeed == 0 || !isFwd())     // is turning-on / reversing now?
    {
        DissipativeBreak();

        TIMSK = (TIMSK & ~_BV(OCIE1B)) | _BV(TOIE1) | _BV(OCIE1A);

        BotHB1(OFF);
        BotHB2(OFF);
        _delay_us(1.6);
        TopHB2(ON);

        // Make TCNT1 overflow soon. It will then start the PWM cycle,
        // turning the bottom MOSFET ON, in the overflow interrupt.
        TCNT1 = 0xf0;
        clear_timer_flags();
    }
    gCurrSpeed = val;
}


// Note: to be invoked with interrupts disabled
static inline void GoBw (byte val)
{
    if (gCurrSpeed == 0 || isFwd())     // is turning-on / reversing now?
    {
        DissipativeBreak();

        TIMSK = (TIMSK & ~_BV(OCIE1A)) | _BV(TOIE1) | _BV(OCIE1B);

        BotHB1(OFF);
        _delay_us(1.6);
        TopHB1(ON);
        BotHB2(OFF);

        // Make TCNT1 overflow soon. It will then start the PWM cycle,
        // turning the bottom MOSFET ON
        TCNT1 = 0xf0;
        clear_timer_flags();
    }
    gCurrSpeed = val;
}


ISR (TIMER1_OVF1_vect)
{
    // Don't turn ON OCA still active.
    if ((PINA & eOCA) == 0)
    {
        return;
    }

    if (isFwd())
    {
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        PWM_VALUE_HB1 = gCurrSpeed;

        TopHB1(OFF);
        _delay_us(1.3);
        BotHB1(ON);
    }
    else
    {
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        PWM_VALUE_HB2 = gCurrSpeed;

        TopHB2(OFF);
        _delay_us(1.3);
        BotHB2(ON);
    }

    i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overcurrent_Limiter));
}


ISR (TIMER1_CMPA_vect)
{
    FwOff();
}


ISR (TIMER1_CMPB_vect)
{
    BkwOff();
}


ISR(IO_PINS_vect)
{
    // We'll get also interrupts due to other pins. Filter the state we're
    // interested in, which is OCA active (= 0).
    if ((PINA & eOCA) == 0)
    {
        // End the current PWM duty ON.
        if (isFwd())
        {
            FwOff();
        }
        else
        {
            BkwOff();
        }
        // Signal OCA. Bit is reset on the start of every PWM period.
        i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overcurrent_Limiter);
    }
}


#ifndef DISABLE_TIMER_TICK
EMPTY_INTERRUPT (TIMER0_OVF0_vect)
#endif


/** 
 * Timer 0 initialisation
 */
static void start_timer_0 (void)
{
# ifndef DISABLE_TIMER_TICK
#   if F_CPU==4000000
    // TIMER0: Normal 8-bit Mode 0
    // Set Clock prescaler to count at F_CPU/256 -> 4MHz/256/256 ~ 61Hz -> 16.38ms
    TCCR0 = _BV(CS02);

#   elif F_CPU==8000000
    // TIMER0: Normal 8-bit Mode 0
    // Set Clock prescaler to count at F_CPU/1024 -> 8MHz/1024/256 ~ 30.5Hz -> 32.77ms
    TCCR0 = _BV(CS02) | _BV(CS00);
#   endif

    // Enable OVF interrupt
    TIMSK |= _BV(TOIE0);
# endif
}


/**
 * ADC initialisation
 */
static void adc_init (void)
{
# ifndef DISABLE_ADC
    // Select 1st channel to sample.
    ADMUX |= 1;

    // Select internal 2.7V Vref with decoupling cap at AREF.
    ADMUX |= _BV(REFS1) | _BV(REFS0);

#   if F_CPU==4000000
    // Fadc = 125KHz (adc-prescaler = 32 -> 4MHz / 32 = 125KHz -> 8us)
    ADCSR |= _BV(ADPS2) | _BV(ADPS0);
    // Fadc = 250KHz (adc-prescaler = 16 -> 4MHz / 16 = 250KHz -> 4us)
    //ADCSR |= _BV(ADPS2);

#   elif F_CPU==8000000
    // Fadc = 125KHz (adc-prescaler = 64 -> 8MHz / 64 = 125KHz -> 8us)
    //ADCSR |= _BV(ADPS2) | _BV(ADPS1);
    // Fadc = 250KHz (adc-prescaler = 32 -> 8MHz / 32 = 250KHz -> 4us)
    ADCSR |= _BV(ADPS2) | _BV(ADPS0);
#   endif

    // Enable ADC conversion complete interrupt.
    //ADCSR |= _BV(ADIE);

    // Enable continuous conversions.
    //ADCSR |= _BV(ADFR);

    // Enable ADC. It will always be enabled.
    ADCSR |= _BV(ADEN);

    // Start a conversion to trigger conversion chain.
    //ADCSR |= _BV(ADSC);
# endif
}


/**
 * \brief Ports initialisation
 */
static void ports_init (void)
{
    // Keep in mind that this routine can be called just to re-init the ports,
    // and therefore it must not assume any initial state, and must not change
    // things it doesn't use.

    // H-bridge pins as outputs, starting all off.
    PORTB |=  (eHB1_L | eHB2_L);    // bottom MOSFETs off (inverter MOSFET driver)
        // At this point, the pull-ups are ON and we're already actively turning
        // OFF the bottom MOSFETs. Nevertheless, the bottom drivers keep the MOSFETs
        // off when not driven.
        // The top MOSFETs are OFF because the drivers are not being driven.
    DDRB  |=  (eHB1_L | eHB2_L | eHB1_H | eHB2_H);
        // Now that all pins are made outputs, the top MOSFETs are being actively
        // driven off. The bottom MOSFETs are gone from pull-up driven off to
        // actively driven off.

    AllOff();  // inits some state

    // Enable pull-up for base i2c address selector.
    PORTA |= eI2CaddrSel;
    // LED pin as output.
    DDRA  |= eLED;

    // Enable pull-up on OCA (Over Current Alarm) pin.
    PORTA |= eOCA;
    // Enable pin change interrupt to catch the OverCurrent Alarm.
    // Need to disable the VCOMP for the interrupt to trigger on OCA's pin.
    ACSR |= _BV(ACD);

    // Enable pull-ups on unused pins, to have stable inputs.
    PORTA |= ePA3;
    PORTB |= ePB6;
}


static void pwm_init (void)
{
#   ifndef DISABLE_PWM
    // Counter only works as a counter.
    TCCR1A = 0;
    // Overflow happens at (sysclock / prescaler / (OCRC + 1))
    // Prescaler: 1: /1, 2: /2, 3: /4, 4: /8
#   if F_CPU==4000000
    // Ctr overflow freq: 4MHz / 1 / (255 + 1) = 15.625KHz
    //                    4MHz / 2 / (255 + 1) =  7.813KHz
    //                    4MHz / 2 / (249 + 1) =  8.000KHz
    TCCR1B = (TCCR1B & 0xF0) | 2;
#   elif F_CPU==8000000
    // Ctr overflow freq: 8MHz / 2 / (255 + 1) = 15.625KHz
    //                    8MHz / 4 / (255 + 1) =  7.813KHz
    //                    8MHz / 4 / (249 + 1) =  8.000KHz
    //                    8MHz / 4 / (199 + 1) = 10.000KHz
    TCCR1B = (TCCR1B & 0xF0) | 3;
#   endif
    OCR1C = 0xFF;
#   endif
}


byte volatile gI2C_RegFile[I2C_REGISTER_FILE_SIZE];


static void twi_init (void)
{
/*#ifdef WHITEDOTCHIP
    byte  my_i2c_addr = 0x23;
#else
    byte  my_i2c_addr = 0x22;   //PortRead(A, eI2CaddrSel)? 0x22 : 0x23;        // autoset addr not working, I think is'cause I forgot to set the hw jumper
#endif
*/
    i2c_Set_Reg(eI2cReg_SwRevision, FW_VERSION);

    i2c_Set_Reg_Access(eI2cReg_Command, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Speed, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Acceleration, eI2c_RW);

    i2c_Slave_Initialise(gCfg.i2cAddr);
}



// This is not good at all and needs further work, but is what I can do now.
static inline void ReadMotorCurrent (void)
{
    byte  failed = 0;
    word  val;

    // TCNT1 OVFL interrupt takes ~15 TCNT1 cnts, therefore the 0-15 cnt zone
    // will never be able to get caught by this routine. This means the duty
    // 0+14 .. 15+14 = 14 .. 29
    if (gCurrSpeed >= 14 && gCurrSpeed <= 29)
        return;

    // Set the channel and then
    ADMUX = (ADMUX & 0xF0) | 5;     // Isens channel

    // wait for the right moment.
    // The most demanding reading is motor current. It must be sampled
    // right before the duty cycle ends (it ends at the compare match
    // interrupt, when TCNT == OCRA/B). The ADC samples 1.5 ADC-clocks
    // after conversion start, which means that the ADC conversion must
    // be triggered ...
    //  @Fadc=250KHz and @Fpwm=8KHz,
    //      1 / 250KHz * 1.5 = 6us
    //      6us / (1/7812.5Hz / 256) = 12 TCNT counts
    // ... 12 TCNT counts before TCNT reaches OCRA/B.
    byte  trigger_point = PWM_VALUE_HB1 - 14;
    // Note: Only the i2c register reflects the user set current speed.
    if (TCNT1 > trigger_point)
        while (TCNT1 > trigger_point);
    while (TCNT1 < trigger_point);
    // Start the conversion
    ADCSR |= _BV(ADSC);
    // Now we need to check if we were not interrupted and thus lost the moment.
    // We do the check and start the conversion with interrupts disabled so we
    // know we nailed the right moment.
    if (TCNT1 > (byte)(trigger_point + 6))
    {
        // failed to start at the right time, so skip, try again next time
        failed = 1;
    }
    while ( !(ADCSR & _BV(ADIF)) )      // wait end of conversion
        ;//sleep();
    ADCSR |= _BV(ADIF);                 // clear ADC interrupt flag
    if (failed)
    {
        return;
    }
    if (!i2c_Get_Reg(eI2cReg_Speed))
    {
        return;
    }

    byte  prevSREG = SREG;
    cli();
    val = ADCW;       // Must be read with interrupts disabled!!!
    SREG = prevSREG;
    // 5mOhm current sense resistor -> 5 mV/A
    val = gCfg.adcVrefx10 * val;    // no overflow; val ~ Vadc * 1000
    val = (val + 2) / 5;            // Motor current, in A x 10

    // average the value into the register
    //if (val > 5 || i2c_Get_Reg(eI2cReg_MotorCurrent) < 20)
    {
    //    val = (i2c_Get_Reg(eI2cReg_MotorCurrent) + val) / 2;
        i2c_Set_Reg(eI2cReg_MotorCurrent, (byte)val);
    }
    //else if (i2c_Get_Reg(eI2cReg_MotorCurrent))
    //    i2c_Set_Reg(eI2cReg_MotorCurrent, i2c_Get_Reg(eI2cReg_MotorCurrent) - 1);

    /* current limit is done by the OCA...
    if (val > MAX_CURRENT * 10)
    {
        i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overcurrent_Limiter);
    }
    else
    {
        i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overcurrent_Limiter) );
    }*/
}


static word ReadAdc (uint8_t chn)
{
    word  val;

    // Set the channel and then
    ADMUX = (ADMUX & 0xF0) | chn;
    chn = ADMUX;        // consume some time after switching channels...
    // Start the conversion
    ADCSR |= _BV(ADSC);
    while ( !(ADCSR & _BV(ADIF)) );     // wait end of conversion
    ADCSR |= _BV(ADIF);                 // clear ADC interrupt flag

    byte  prevSREG = SREG;
    cli();
    val = ADCW;       // Must be read with interrupts disabled!!!
    SREG = prevSREG;
    return val;
}


static byte CalcChecksum (void* ptr, byte size)
{
    byte  chksum = 0;
    while (size > 0)
    {
        size--;
        chksum += ((byte*)ptr)[size];
    }
    return chksum;
}


// EEPROM start addr of the config
#define EepromCfgAddr   3
// 1st byte of the config must be this magic number
#define EEPROM_MAGIC_NUMBER  0x69


static void SaveCfgToEeprom (void)
{
#  ifndef DISABLE_EEPROM_WRITE
    cli();
    eeprom_busy_wait();
    eeprom_write_byte((byte*)EepromCfgAddr, EEPROM_MAGIC_NUMBER);
    eeprom_busy_wait();
    eeprom_write_block(&gCfg, (byte*)(EepromCfgAddr + 1), sizeof(gCfg));
    eeprom_busy_wait();
    eeprom_write_byte((byte*)(EepromCfgAddr + 1 + sizeof(gCfg)),
                      CalcChecksum(&gCfg, sizeof(gCfg)));
    sei();
#  endif
}


// Read config data from the EEPROM.
// If unable to read config (no config, corrupted, etc) use a default config
// and return 0, otherwise 1.
static byte ReadCfgFromEeprom (void)
{
    byte  magic = eeprom_read_byte((byte*)EepromCfgAddr);
    if (magic == EEPROM_MAGIC_NUMBER)
    {
        eeprom_read_block(&gCfg, (byte*)(EepromCfgAddr + 1), sizeof(gCfg));
        byte  stored_chksum = eeprom_read_byte((byte*)(EepromCfgAddr + 1 + sizeof(gCfg)));
        if (CalcChecksum(&gCfg, sizeof(gCfg)) == stored_chksum)
        {
            return 1;     // success
        }
    }
    // Else set a default config.

    // This i2c addr is reserved for the default config.
    gCfg.i2cAddr = 0x20;
    gCfg.adcVrefx10 = 28;

    SaveCfgToEeprom();
    return 0;
}


/**
 * \brief Main loop
 */
int __attribute__((noreturn)) main(void)
{
    ports_init();

    // Load config params from EEPROM
    byte  i = ReadCfgFromEeprom();

    pwm_init();
    // Init i2c slave interface (do it while interrupts are disabled)
    twi_init();
    adc_init();
    // Initialize TIMER0 to be used as timetick
    start_timer_0();

    set_sleep_mode(SLEEP_MODE_IDLE);

    // Initial short LED blink, or long if using the default config.
    for (i = i? 2 : 8; i; i--)
    {
        PortToggle(A, eLED);
        delayMs(250);
    }

#   ifdef SIMULATOR
    i = MIN_PWM;
    i2c_Set_Reg(eI2cReg_Speed, i);
    GoFw(i);
#   endif

    // Sleep mode always ON
    MCUCR |= _BV(SE);

    // Enable interrupts
    sei();

    while(1)
    {
        //sleep();
        // simple "I'm alive"
        //i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) ^ eStatus_Accelerating);

        /*if (gCtr == 6)       // 16.3x6 97.8ms ~ 100ms
        {
            if (gSpeed / 32 < i2c_Get_Reg(eI2cReg_Speed))
            {
                gSpeed += i2c_Get_Reg(eI2cReg_Acceleration);
            }

            gCtr = 0;
        }*/

        // Handle I2C commands
        byte  chg_mask = i2c_Get_Changed_Mask();
        if (chg_mask)
        {
            if (chg_mask & _BV(eI2cReg_Command))        // Command register
            {
                byte  cmdVal = 0;
                byte  cmd = i2c_Get_Reg(eI2cReg_Command);

                switch (cmd)
                {
                    // Util Commands //

                    case eCmd_Reset :
                        ports_init();
                        i2c_Set_Reg(eI2cReg_Speed, 0);
                        cmdVal = 69;  // confirmation value
                        break;

#                   ifndef DISABLE_EEPROM_WRITE
                    case eCmd_SetI2cAddr :
                        if (gCurrAcc >= 0x20 && gCurrAcc <= 0x28)
                        {
                            gCfg.i2cAddr = gCurrAcc;
                            SaveCfgToEeprom();
                            cmdVal = gCurrAcc;  // confirmation value
                        }
                        break;

                    case eCmd_SetVref :
                        //if (gCurrAcc >= 22 && gCurrAcc <= 32)
                        {
                            gCfg.adcVrefx10 = gCurrAcc;
                            SaveCfgToEeprom();
                            cmdVal = gCurrAcc;  // confirmation value
                        }
                        break;
#                   endif

                    case eCmd_GetVref :
                        cmdVal = gCfg.adcVrefx10;
                        break;

                    // Debug Commands //

                    /*case eCmd_SetPwmFreq8KHz :
                        pwm_SetFrequency(8000);
                        break;
                    case eCmd_SetPwmFreq15KHz :
                        pwm_SetFrequency(15000);
                        break;*/

                    /*case eCmd_GetPinA :
                        cmdVal = PINA;
                        break;
                    case eCmd_GetPinB :
                        cmdVal = PINB;
                        break;
                    case eCmd_GetAdc0 :
                    case eCmd_GetAdc1 :
                    case eCmd_GetAdc2 :
                    case eCmd_GetAdc3 :
                    case eCmd_GetAdc4 :
                    case eCmd_GetAdc5 :
                        cmdVal = gAdc[(cmd - eCmd_GetAdc0) & 0x07] >> 2;
                        break;*/

                    /*default :
                        if ((cmd & 0xF0) == eCmd_SetPwmPres)
                        {
                            cmdVal = cmd & 0x0F;
                            TCCR1B = (TCCR1B & 0xF0) | cmdVal;
                        }*/
                }

                i2c_Set_Reg(eI2cReg_Command, cmdVal);
            }
            byte  update = 0;
            if (chg_mask & _BV(eI2cReg_Speed))          // Speed register
            {
                update = 1;
            }
            if (chg_mask & _BV(eI2cReg_Acceleration))   // Acceleration register
            {
                update = 1;
            }
            if (update)
            {
                cli();
                gCurrAcc = i2c_Get_Reg(eI2cReg_Acceleration);
                byte  val = i2c_Get_Reg(eI2cReg_Speed);
                if (val == 0)
                {
                    OCAInterrupt(OFF);
                    AllOff();
                    i2c_Set_Reg(eI2cReg_MotorCurrent, 0);
                    i2c_Set_Reg(eI2cReg_Status, 0);
                }
                else
                {
                    OCAInterrupt(ON);
                    if (val < MIN_PWM)
                        val = MIN_PWM;
                    else if (val > 255-MIN_PWM)
                        val = 255 - MIN_PWM;

                    if (gCurrAcc == 0)
                        GoFw(val);
                    else
                        GoBw(val);
                }
                sei();
                // wait for the new values (speed) to be set on the TCNT1 OVFL
                // interrupt, otherwise we can get blocked while reading motor
                // current.
                delayMs(10);
            }
        }

        // ADC readings.

        ReadMotorCurrent();

        // After reading motor current, we read the remaining inputs, one
        // every loop. None of these need to be updated very frequently,
        // in, facto, motor current doesn't need high update rate either
        // (20sps is enough for now, 100sps in the future).
        {
            word  val = ReadAdc(4);
            // Vadc = Vcc * 1K / 11K
            // adc * adcVrefx10 / 1024 = Vcc * 10 / 11
            // Vcc * 10 = adc * adcVrefx10 * 11 / 1024;
            val = (long)val * gCfg.adcVrefx10 * 11 / 1024;
            val = (val < 100? 0 : val - 100);       // subtract 10V otherwise won't fit 8 bits
            i2c_Set_Reg(eI2cReg_MotorVcc, (byte)val);
    
            if (val < MIN_MOTOR_VCC * 10)
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_UnderVcc_Limiter);
            }
            else
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_UnderVcc_Limiter) );
            }
        }
    }
}
