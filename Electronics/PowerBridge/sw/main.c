/**
 * Power H-Bridge Controller Fw
 *
 * Copyright (c) 2010-2014 Nuno Jo�o
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


// This value can be read from one of the I2C registers
#define FW_VERSION  24


/// ---- Compilation flags BEGIN ------------

// Use this to control what to compile to run in the AVR simulator. Currently
// it disables some non-critical delays.
//#define SIMULATOR

// The output stage double pulse test mode.
//#define ENABLE_DOUBLE_PULSE

// Some compile modes need more code space, which can be obtained by dropping
// things like the ADC code.
//#define DISABLE_ADC

// Control of the OverCurrentAlarm code. Disabling it disables current
// limiting, which may toast the controller if abused.
//#define DISABLE_OCA

// Code to write the params to EEPROM is not always needed so we remove it for space.
#define DISABLE_EEPROM_WRITE

// Enable the tick if you need a regular timming tick
#define DISABLE_TIMER_TICK

// Auto config for double pulse test mode.
#ifdef ENABLE_DOUBLE_PULSE
#   define DISABLE_ADC
#   define DISABLE_EEPROM_WRITE
#endif

/// ---- Compilation flags END --------------


#define ON      1
#define OFF     0
#define true    1
#define false   0

#define word    uint16_t
#define bool    byte

#define MIN_MOTOR_VCC           22  // V
#define MAX_CURRENT             20  // A
#define MAX_TEMPERATURE         60  //�C

#define PWM_VALUE_HB1           OCR1A
#define PWM_VALUE_HB2           OCR1B

#define MIN_PWM     20

#define PFWMODE     ON

#define PortRead(port_letter, bits)     (PIN ## port_letter & (bits))
#define PortSet(port_letter, bits)      PORT ## port_letter |= (bits)
#define PortClear(port_letter, bits)    PORT ## port_letter &= ~(bits)
#define PortToggle(port_letter, bits)   PORT ## port_letter ^= (bits)


// AVR pin assigned functions
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


// ADC channels
enum {
    // goes to the add-on to be "split" into 2 sensors, 1 for each heatsink
    eADC_Temp1Bridge = 1,
    // this goes to the power board where there's a doide connection "socket"
    eADC_Temp2Motor = 2,
    eADC_VccSens = 4,
    eADC_MotorDriveCurrent = 5,

    eADC_NumOfChannels
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
    eCmd_DoDoublePulseTest,
    eCmd_GetPinA,
    eCmd_GetPinB,
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

static volatile word  gAdc[eADC_NumOfChannels];


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


static inline void OCAInterrupt (bool on)
{
#  ifndef DISABLE_OCA
    if (on)
        GIMSK |= _BV(PCIE1);
    else
        GIMSK &= ~_BV(PCIE1);
#  endif
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


static inline void BkwOff (void)
{
    BotHB2(OFF);
    _delay_us(1.5);
    TopHB2(PFWMODE);
}


static inline void FwOff (void)
{
    BotHB1(OFF);
    _delay_us(1.5);
    TopHB1(PFWMODE);
}


static void clear_timer_flags (void)
{
    TIFR |= _BV(TOV1);
    TIFR |= _BV(OCF1A) | _BV(OCF1B);
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
#  ifndef DISABLE_OCA
    // Don't turn ON while OCA is active.
    if ((PINA & eOCA) == 0)
    {
        return;
    }
#  endif

    if (isFwd())
    {
        TopHB1(OFF);
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        // 3 cycles (0.375us @ 8MHz)
        PWM_VALUE_HB1 = gCurrSpeed;
        _delay_us(1.3 - 0.375);
        BotHB1(ON);
    }
    else
    {
        TopHB2(OFF);
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        PWM_VALUE_HB2 = gCurrSpeed;
        _delay_us(1.3 - 0.375);
        BotHB2(ON);
    }

    // We can clear the current limiting status flag, as here we know
    // we're not limiting.
    // 5 cycles (0.625us @ 8MHz)
    i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overcurrent_Limiter));

    // Start the ADC to read the (motor driving) current. Result to be processed
    // on the ADC interrupt.
    if ((ADMUX & 0x0F) == eADC_MotorDriveCurrent)
        ADCSR |= _BV(ADSC);         // 2 cycles (0.25us @ 8MHz)
}


ISR (TIMER1_CMPA_vect)
{
    FwOff();
}


ISR (TIMER1_CMPB_vect)
{
    BkwOff();
}


#ifndef DISABLE_OCA
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
        // Signal OCA. Bit is reset on every PWM period start (if eOCA is inactive).
        i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overcurrent_Limiter);
    }
}
#endif


#ifndef DISABLE_TIMER_TICK
EMPTY_INTERRUPT (TIMER0_OVF0_vect)
#endif


#ifndef DISABLE_ADC
ISR(ADC_vect)
{
    word  val = ADCW;       // must be read with interrupts disabled!

    sei();

    byte  admux = ADMUX;
    byte  chn = admux & 0x0F;
    admux &= 0xF0;

    switch (chn)
    {
        case eADC_MotorDriveCurrent :
        {
            ADMUX = admux | eADC_Temp1Bridge;
            gAdc[eADC_MotorDriveCurrent] = val;
            // Start next conversion.
            ADCSR |= _BV(ADSC);
            break;
        }
        case eADC_Temp1Bridge :
        {
            ADMUX = admux | eADC_Temp2Motor;
            gAdc[eADC_Temp1Bridge] = val;
            // Start next conversion.
            ADCSR |= _BV(ADSC);
            break;
        }
        case eADC_Temp2Motor :
        {
            ADMUX = admux | eADC_VccSens;
            gAdc[eADC_Temp2Motor] = val;
            // Start next conversion.
            ADCSR |= _BV(ADSC);
            break;
        }
        case eADC_VccSens :
        {
            ADMUX = admux | eADC_MotorDriveCurrent;
            gAdc[eADC_VccSens] = val;
            // Do NOT start next conversion.
            // It will be started when at the start of the PWM period.
            break;
        }
    }
}
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
#  ifndef DISABLE_ADC
    ADMUX |= 0
        // Select internal 2.7V Vref with decoupling cap at AREF.
            | _BV(REFS1) | _BV(REFS0)
        // Select 1st channel to sample, motor drive current.
            | eADC_MotorDriveCurrent     // Isense
            ;

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
    ADCSR |= _BV(ADIE);

    // Enable ADC. It will always be enabled.
    ADCSR |= _BV(ADEN);
#  endif
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
    // Counter only works as a counter.
    TCCR1A = 0;
    // Overflow happens at (sysclock / prescaler / (OCRC + 1))
    // Prescaler: 1: /1, 2: /2, 3: /4, 4: /8
#  if F_CPU==4000000
    // Ctr overflow freq: 4MHz / 1 / (255 + 1) = 15.625KHz  (1)
    //                    4MHz / 2 / (255 + 1) =  7.813KHz  (2)
    //                    4MHz / 2 / (249 + 1) =  8.000KHz  (2)
    TCCR1B = (TCCR1B & 0xF0) | 2;
#  elif F_CPU==8000000
    // Ctr overflow freq: 8MHz / 2 / (255 + 1) = 15.625KHz  (2)
    //                    8MHz / 4 / (255 + 1) =  7.813KHz  (3)
    //                    8MHz / 4 / (249 + 1) =  8.000KHz  (3)
    //                    8MHz / 4 / (199 + 1) = 10.000KHz  (3)
    TCCR1B = (TCCR1B & 0xF0) | 3;
#  endif
    OCR1C = 0xFF;
}


byte volatile gI2C_RegFile[I2C_REGISTER_FILE_SIZE];


static void twi_init (void)
{
    i2c_Set_Reg(eI2cReg_SwRevision, FW_VERSION);

    i2c_Set_Reg_Access(eI2cReg_Command, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Speed, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Acceleration, eI2c_RW);

    i2c_Slave_Initialise(gCfg.i2cAddr);
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
// 1st byte of the config must be this magic number :)
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
    // Init the I/O ports as they control critical things and we must set
    // defined values ASAP.
    ports_init();

    // Load config params from EEPROM
    byte  i = ReadCfgFromEeprom();

    pwm_init();
    // Init i2c slave interface (do it while interrupts are disabled)
    twi_init();
    adc_init();
    // Initialize TIMER0 to be used as timetick
    start_timer_0();

    // Initial short LED blink, or long if using the default config.
#  ifndef SIMULATOR
    for (i = i? 2 : 8; i; i--)
    {
        PortToggle(A, eLED);
        delayMs(250);
    }
#  endif

#  ifdef SIMULATOR
    i = MIN_PWM;
    i2c_Set_Reg(eI2cReg_Speed, i);
    GoFw(i);
    delayMs(1);     // keep gcc happy :)
#  endif

#  ifndef DISABLE_TIMER_TICK
    set_sleep_mode(SLEEP_MODE_IDLE);
    // Sleep mode always ON
    MCUCR |= _BV(SE);
#  endif

#  ifdef ENABLE_DOUBLE_PULSE
    // More user friendly start values
    i2c_Set_Reg(eI2cReg_Command, eCmd_DoDoublePulseTest);   // DP test cmd nr.
    i2c_Set_Reg(eI2cReg_Speed, 50);                         // 1st pulse len (us)
    i2c_Set_Reg(eI2cReg_Acceleration, 10);                  // pause len (us)
#  endif

    // Enable interrupts
    sei();

    word  acc = 0;
    byte  num = 0;

    while(1)
    {
        //sleep();

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
                        i2c_Set_Reg(eI2cReg_MotorCurrent, 0);
                        i2c_Set_Reg(eI2cReg_Status, 0);

                        cmdVal = 69;  // confirmation value
                        break;

#                  ifndef DISABLE_EEPROM_WRITE
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
#                  endif

                    case eCmd_GetVref :
                        cmdVal = gCfg.adcVrefx10;
                        break;

                    // Debug Commands //

#                  ifdef ENABLE_DOUBLE_PULSE
                    case eCmd_DoDoublePulseTest :
                    {
                        byte  ctr;
                        gCurrAcc = 0;       // prevent compiler warning

                        // Lenght of 1st pulse in the SPEED reg, length of
                        // pause in the ACC reg, 2nd pulse len is fixed at 25us.
                        // All times in us.
                        
                        if (i2c_Get_Reg(eI2cReg_Speed) < 2)
                            i2c_Set_Reg(eI2cReg_Speed, 2);
                        cli();

                        AllOff();
                        _delay_us(100);
                        TopHB2(ON);

                        // Pulse #1
                        BotHB1(ON);
                        // -2 compensates for some delays and code
                        for (ctr = i2c_Get_Reg(eI2cReg_Speed) - 2; ctr; ctr--)
                        {
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                        }
                        FwOff();

                        // pause...
                        for (ctr = i2c_Get_Reg(eI2cReg_Acceleration) - 2; ctr; ctr--)
                        {
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                            asm volatile("nop");
                        }

                        // Pulse #2, fixed len
                        TopHB1(OFF);
                        _delay_us(2);
                        BotHB1(ON);
                        _delay_us(20);
                        FwOff();

                        _delay_us(500);
                        AllOff();

                        sei();
                        cmdVal = cmd;       // ready to repeat test
                        break;
                    }
#                  endif

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

#          ifndef ENABLE_DOUBLE_PULSE
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
            }
#          endif
        }

        // ADC readings.

#      ifndef DISABLE_ADC
        // Process power supply voltage.
        {
            word  val = gAdc[eADC_VccSens];
            // Vadc = Vcc * 1K / 11K
            // adc * adcVrefx10 / 1024 = Vcc * 10 / 11
            // Vcc * 10 = adc * adcVrefx10 * 11 / 1024;
            val = (long)val * gCfg.adcVrefx10 * 11 / 1024;
            val = (val < 100? 0 : val - 100);       // subtract 10V otherwise won't fit 8 bits
            i2c_Set_Reg(eI2cReg_MotorVcc, (byte)val);
        }
        // Process motor current readings. Average 8 samples.
        if (i2c_Get_Reg(eI2cReg_Speed) && gAdc[eADC_MotorDriveCurrent])
        {
            word  val = gAdc[eADC_MotorDriveCurrent];
            // 5mOhm current sense resistor -> 5 mV/A
            val = gCfg.adcVrefx10 * val;    // no overflow; val ~ Vadc * 1000
            val = (val + 2) / 5;            // Motor current, in A x 10
            byte  final = (byte)val;
            acc += final;
            num++;
            if (num >= 8)
            {
                final = (byte) ((acc + 2) / 8);
                i2c_Set_Reg(eI2cReg_MotorCurrent, final);
                acc = 0;
                num = 0;
            }
        }
        // Process temperature 1, "bridge temp".
        {
            word  val = gAdc[eADC_Temp1Bridge];
            // We have only 8 bits to report the temp. ADC resolution is ~2.6mV.
            // We need to measure a range ~ 0.2V..0.7V (2 schottky diode in series).
            // So we report 8bits from a base of 0.2V. 0.2V is ~ count 76.
            if (val < 76)
                val = 76;
            i2c_Set_Reg(eI2cReg_Temperature, (byte)((val - 76) & 0x00FF));     //@@TODO: make a register for the reading
        }
        // Process temperature 2, "motor temp".
        {
            word  val = gAdc[eADC_Temp2Motor];
            // We have only 8 bits to report the temp. ADC resolution is ~2.6mV.
            // We need to measure a range ~ 0.5V..0.8V (PN diode).
            // So we report 8bits from a base of 0.4V. 0.4V is ~ count 152.
            if (val < 152)
                val = 152;
            i2c_Set_Reg(eI2cReg_Temperature, (byte)((val - 152) & 0x00FF));
        }
#      endif
    }
}
