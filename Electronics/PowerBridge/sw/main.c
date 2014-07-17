/**
 * Power H-Bridge Controller Fw
 *
 * Copyright (c) 2010-2014 Nuno João
 * http://www.EmbeddedDreams.com
 *
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include "i2c_slave.h"


//#define DISABLE_ADC
//#define DISABLE_PWM
//#define WHITEDOTCHIP


// This value can be read from an I2C register
#define FW_VERSION  0x13        // 0 x <major> <minor>

#define ON      1
#define OFF     0
#define true    1
#define false   0

#define word    unsigned short
#define bool    byte


// AVR ADC internal Vref - chip dependant
#ifdef WHITEDOTCHIP
#   define VREFx10  27     // white dot chip 2.73V
#else
#   define VREFx10  28     // no white dot chip
#endif

#define MIN_MOTOR_VCC           22  // V
#define MAX_CURRENT             20  // A
#define MAX_TEMPERATURE         60  //ºC

#define PWM_VALUE_HB1           OCR1A
#define PWM_VALUE_HB2           OCR1B


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
    // Debug/Test commands
    eCmd_Reset = 0,
    eCmd_GetPinA,
    eCmd_GetPinB,
    eCmd_GetAdc0,
    eCmd_GetAdc1,
    eCmd_GetAdc2,
    eCmd_GetAdc3,
    eCmd_GetAdc4,
    eCmd_GetAdc5,
    eCmd_SetPwmFreq5KHz,
    eCmd_SetPwmFreq8KHz,
    eCmd_SetPwmFreq10KHz,
    eCmd_SetPwmFreq12KHz,
    eCmd_SetPwmFreq15KHz,
    eCmd_SetPwmFreq18KHz,
    eCmd_SetPwmPres = 0xF0,
};


//static byte  gCtr = 0;

static byte  gCurrSpeed = 0;

static word  gAdc[8];


static void delayMs (unsigned short ms)
{
    while (ms--)
        _delay_ms(1);
}


static void clear_timer_flags (void)
{
    TIFR |= _BV(TOV1);
    TIFR |= _BV(OCF1A) | _BV(OCF1B);
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


static void GoFw (byte val)
{
    cli();
    if (val == 0)
    {
        AllOff();
    }
    else
    {
        if (val < 30)
            val = 30;
        else if (val > 255-30)
            val = 255 - 30;

        if (gCurrSpeed == 0 || !isFwd())     // is turning-on / reversing now?
        {
            DissipativeBreak();

            PWM_VALUE_HB2 = val - 15;
            TIMSK = (TIMSK & ~_BV(OCIE1B)) | _BV(TOIE1) | _BV(OCIE1A);

            BotHB1(OFF);
            BotHB2(OFF);
            _delay_us(1);
            TopHB2(ON);

            // Make TCNT1 overflow soon. It will then start the PWM cycle,
            // turning the bottom MOSFET ON, in the overflow interrupt.
            TCNT1 = 0xf1;
            clear_timer_flags();
        }
    }
    gCurrSpeed = val;
    sei();
}


static void GoBw (byte val)
{
    cli();
    if (val == 0)
    {
        AllOff();
    }
    else
    {
        if (val < 30)
            val = 30;
        else if (val > 255-30)
            val = 255 - 30;

        if (gCurrSpeed == 0 || isFwd())     // is turning-on / reversing now?
        {
            DissipativeBreak();

            PWM_VALUE_HB1 = val - 15;
            TIMSK = (TIMSK & ~_BV(OCIE1A)) | _BV(TOIE1) | _BV(OCIE1B);

            BotHB1(OFF);
            _delay_us(1);
            TopHB1(ON);
            BotHB2(OFF);

            // Make TCNT1 overflow soon. It will then start the PWM cycle,
            // turning the bottom MOSFET ON
            TCNT1 = 0xf1;
            clear_timer_flags();
        }
    }
    gCurrSpeed = val;
    sei();
}


// Check if we can remove this now that we have other periodic interrupts
ISR (TIMER0_OVF0_vect)
{
    //gCtr++;
}


#define PFWMODE  ON

ISR (TIMER1_OVF1_vect)
{
    if (isFwd())
    {
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        PWM_VALUE_HB1 = gCurrSpeed;
        //PWM_VALUE_HB2 = gCurrSpeed - 15;

        TopHB1(OFF);
        _delay_us(1.6);
        BotHB1(ON);
        /*/ very short duty cycle handled as special case...
        if (gCurrSpeed < 30)
        {
            while (TCNT1 < gCurrSpeed);     // waits up to (30/255)/8KHz ~ 14.7us
            BotHB1(OFF);
            _delay_us(0.1);
            TopHB1(PFWMODE);
        }*/
    }
    else
    {
        // Update duty cycle here, at the beginning of the PWM cycle.
        // This ensures glitch free PWM on duty cycle changes.
        PWM_VALUE_HB2 = gCurrSpeed;
        //PWM_VALUE_HB1 = gCurrSpeed - 15;

        TopHB2(OFF);
        _delay_us(1.6);
        BotHB2(ON);
        /*/ very short duty cycle handled as special case...
        if (gCurrSpeed < 30)
        {
            while (TCNT1 < gCurrSpeed);     // waits up to (30/255)/8KHz ~ 14.7us
            BotHB2(OFF);
            _delay_us(0.1);
            TopHB2(PFWMODE);
        }*/
    }
}


ISR (TIMER1_CMPA_vect)
{
    BotHB1(OFF);
    _delay_us(0.1);
    TopHB1(PFWMODE);
}


ISR (TIMER1_CMPB_vect)
{
    BotHB2(OFF);
    _delay_us(0.1);
    TopHB2(PFWMODE);
}


#if 0
//#ifndef DISABLE_ADC
ISR (ADC_vect)
{
    word  val = ADCW;       // Must be read with interrupts disabled!!!

    // This interrupt can be veeeery long, so we enable interrupts.
    // The ADC interrupt is re-triggered at the end of this handler,
    // so there's no danger in getting nested ADC interrupts.
    sei();

    byte  admux = ADMUX;
    byte  next_chn;

    gAdc[admux & 0x07] = val;

    switch (admux & 0x07)
    {
        case 1 :    // eBridgeTemp
            next_chn = 2;
            ADMUX = (admux & 0xF0) | next_chn;

            {
                // 25ºC ~ 0.7V, -2.3mV/ºC
                // diode temp -> T = 25 - (Vd - T25) / 0.0023
                // VREFx10 * val / 1024 = Vt * 10
                // (Vt*10 - 0.7*10) / 0.0023 = T*10
                short Cnt700mV = (7 * 1024 +VREFx10/2) / VREFx10;  // 25ºC diode Vfw - diode dependant
                long  CntTemp  = (short)val - Cnt700mV;            // val - 0.7V
                short DiffDegC = (VREFx10 * CntTemp + 13) / 23;    // diff * 10000 / (0.0023 * 10000)
                                                                   // x10(Vref) x1024(CntTemp) ~ x10000
                val = (short)25 - DiffDegC;

                i2c_Set_Reg(eI2cReg_Temperature, (byte)val);
            }

            if (val > MAX_TEMPERATURE)
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overtemp_Limiter);
            }
            else
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overtemp_Limiter) );
            }
            break;

        case 2 :    // eMotorTemp
            next_chn = 4;
            ADMUX = (admux & 0xF0) | next_chn;

            // LM35 -> 10mV/ºC
            val = (VREFx10 * val * 10 + 512) / 1024;  // no overflow; val = Vadc * 100
            //if ((admux & 0xF) == 1)
            //    i2c_Set_Reg(eI2cReg_Temperature, (byte)val);
            //else
            {
                //if (val > i2c_Get_Reg(eI2cReg_Temperature))
                //    i2c_Set_Reg(eI2cReg_Temperature, (byte)val);

                /*if (i2c_Get_Reg(eI2cReg_Temperature) > MAX_TEMPERATURE)
                {
                    i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overtemp_Limiter);
                }
                else
                {
                    i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overtemp_Limiter) );
                }*/
            }
            break;

        case 4 :    // eVccSense
            next_chn = 5;     //Isens
            ADMUX = (admux & 0xF0) | next_chn;

            // Vadc = Vcc * 1K / 11K
            // adc * VREFx10 / 1024 = Vcc * 10 / 11
            // Vcc * 10 = adc * VREFx10 * 11 / 1024;
            //val = (VREFx10 * val +512) / 1024;      // no overflow; val = Vadc * 10
            //val = (val * 11 * 104 +50) / 100;       // Motor Vcc * 10
            val = (long)val * VREFx10 * 11 / 1024;
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

            // 8KHz PWM -> 125us / 256 = 0.488us
            // ADC 125KHz 1 conv S&H 1.5clk ~ 1/125K * 1.75 = 14us
            // 14 us / 0.488 us ~ 29
            // ADC 250KHz 1 conv S&H 1.5clk ~ 1/250K * 1.6 ~ 6.5us
            // 6.5 us / 0.488 us ~ 13
            //if ( (PWM_VALUE_HB1 > 18) && (TCNT1 < PWM_VALUE_HB1 - 18) )
            {
            }
            //else if ( (PWM_VALUE_HB2 > 18) && (TCNT1 < PWM_VALUE_HB2 - 18) )
            {
            }
            //else
            {
                next_chn = 1;
                ADMUX = (admux & 0xF0) | next_chn;
                _delay_us(1);
                //if (i2c_Get_Reg(eI2cReg_MotorCurrent))
                //    i2c_Set_Reg(eI2cReg_MotorCurrent, i2c_Get_Reg(eI2cReg_MotorCurrent) - 1);
            }
            break;

        case 5 :    // eIsense
            next_chn = 1;
            ADMUX = (admux & 0xF0) | next_chn;

            i2c_Set_Reg(eI2cReg_Temperature, (byte)val);

            // 5mOhm current sense resistor -> 5 mV/A
            val = VREFx10 * val;            // no overflow; val ~ Vadc * 1000
            val = (val + 2) / 5;            // Motor current, in A x 10

            // average the value into the register
            if (val > 5 || i2c_Get_Reg(eI2cReg_MotorCurrent) < 20)
            {
                val = (i2c_Get_Reg(eI2cReg_MotorCurrent) + val) / 2;
                i2c_Set_Reg(eI2cReg_MotorCurrent, (byte)val);
            }
            else if (i2c_Get_Reg(eI2cReg_MotorCurrent))
                i2c_Set_Reg(eI2cReg_MotorCurrent, i2c_Get_Reg(eI2cReg_MotorCurrent) - 1);

            if (val > MAX_CURRENT * 10)
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) | eStatus_Overcurrent_Limiter);
            }
            else
            {
                i2c_Set_Reg(eI2cReg_Status, i2c_Get_Reg(eI2cReg_Status) & (~eStatus_Overcurrent_Limiter) );
            }
            break;

        default :
            next_chn = 0;
            break;
    }

    ADCSR |= _BV(ADSC);
}
#endif



/** 
 * \brief Timer 0 initialisation
 */
static void start_timer_0 (void)
{
    // TIMER0: Normal 8-bit Mode 0
    // Set Clock prescaler to 16.3ms period interrupt
    TCCR0 = _BV(CS02);

    // Enable OVF interrupt
    TIMSK |= _BV(TOIE0);
}


/**
 * \brief ADC initialisation
 *
 * ADC frequency is set to 125KHz for 10-bit resolution
 */
static void adc_init (void)
{
#ifndef DISABLE_ADC
    // Select 1st channel to sample.
    ADMUX |= 1;
    // Select internal 2.7V Vref with decoupling cap at AREF.
    ADMUX |= _BV(REFS1) | _BV(REFS0);
    // Set ADC prescaler to 32
    // Fadc = 125KHz (sysclock divided by 32 -> 4MHz / 32 = 125KHz -> 8us)
    ADCSR |= _BV(ADPS2) | _BV(ADPS0);
    // Set ADC prescaler to 16
    // Fadc = 250KHz (sysclock divided by 16 -> 4MHz / 16 = 250KHz -> 4us)
    //ADCSR |= _BV(ADPS2);
    // Enable ADC conversion complete interrupt.
//    ADCSR |= _BV(ADIE);
    // Enable continuous conversions.
    //ADCSR |= _BV(ADFR);
    // Enable ADC. It will always be enabled.
    ADCSR |= _BV(ADEN);
    // Start a conversion to trigger conversion chain.
//    ADCSR |= _BV(ADSC);
#endif
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

    // Enable pull-ups on unused pins, to have stable inputs.
    PORTA |= ePA3;
    PORTB |= ePB6;
}


static void pwm_init (void)
{
#ifndef DISABLE_PWM
    //const unsigned char  ePwmCompareModeMask = 0x3;

    // PWM outputs inverted signal because N-MOSFET drivers are inverting.
    TCCR1A = 0  //(TCCR1A & ~(ePwmCompareModeMask << COM1A0)) |
             // OC1x set one prescaled cycle after compare match. Cleared when TCNT = $00.
             // ~OC1x not connected.
             //(1 << COM1A1) | (1 << COM1A0) |
             //_BV(PWM1A)        // Enable PWM
             ;
    //TCCR1A = (TCCR1A & ~(ePwmCompareModeMask << COM1B0)) |
             //(1 << COM1B1) | (1 << COM1B0) |
             //_BV(PWM1B)        // Enable PWM
             ;
    // Nominal frequency: 1: 16KHz, 2: 8KHz, 3: 4KHz, 4: 2KHz
    TCCR1B = (TCCR1B & 0xF0) | 2;
    OCR1C = 0xFF;
#endif
}


byte volatile gI2C_RegFile[I2C_REGISTER_FILE_SIZE];


static void twi_init (void)
{
#ifdef WHITEDOTCHIP
    byte  my_i2c_addr = 0x23;
#else
    byte  my_i2c_addr = 0x22;   //PortRead(A, eI2CaddrSel)? 0x22 : 0x23;        // autoset addr not working, I think is'cause I forgot to set the hw jumper
#endif

    i2c_Set_Reg(eI2cReg_SwRevision, FW_VERSION);

    i2c_Set_Reg_Access(eI2cReg_Command, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Speed, eI2c_RW);
    i2c_Set_Reg_Access(eI2cReg_Acceleration, eI2c_RW);

    i2c_Slave_Initialise(my_i2c_addr);
}




static inline void ReadMotorCurrent (void)
{
    byte  failed = 0;
    word  val;

    if (PWM_VALUE_HB1 <= 30)
        return;

    // Set the channel and then
    ADMUX = (ADMUX & 0xF0) | 5;     // Isens channel
    // wait for the right moment...
    byte  trigger_point = PWM_VALUE_HB1 - 15;
    // Note: Only the i2c register reflects the user set current speed.
    if (TCNT1 > trigger_point)
        while (TCNT1 > trigger_point);
    while (TCNT1 < trigger_point);
    // Start the conversion
    ADCSR |= _BV(ADSC);
    // Now we need to check if we were not interrupted and thus lost the moment.
    // We do the check and start the conversion with interrupts disabled so we
    // know we nailed the right moment.
    if ((TCNT1 > trigger_point + 8) || !i2c_Get_Reg(eI2cReg_Speed))
    {
        if (!i2c_Get_Reg(eI2cReg_Speed))
        {
            i2c_Set_Reg(eI2cReg_MotorCurrent, 0);
        }
        // failed to start at the right time, so skip, try again next time
        failed = 1;
    }
    while ( !(ADCSR & _BV(ADIF)) );     // wait end of conversion
    ADCSR |= _BV(ADIF);                 // clear ADC interrupt flag
    if (failed)
        return;

    cli();
    val = ADCW;       // Must be read with interrupts disabled!!!
    sei();
    // 5mOhm current sense resistor -> 5 mV/A
    val = VREFx10 * val;            // no overflow; val ~ Vadc * 1000
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

    cli();
    val = ADCW;       // Must be read with interrupts disabled!!!
    sei();
    return val;
}


/**
 * \brief Main loop
 */
int __attribute__((noreturn)) main(void)
{
    ports_init();
    pwm_init();
    // Init i2c slave interface (do it while interrupts are disabled)
    twi_init();
    adc_init();
    // Initialize TIMER0 to be used as timetick
    start_timer_0();
    set_sleep_mode(SLEEP_MODE_IDLE);

    byte  i;
    for (i = 0; i < 2; i++)
    {
        PortToggle(A, eLED);
        //delayMs(250);
        delayMs(1);
    }
    i2c_Set_Reg(eI2cReg_MotorCurrent, 31);
    GoFw(31);
    //delayMs(1);

    // Enable interrupts
    sei();
    //pwm(ON);
    /*GoFw(0x80);
    delayMs(2);
    GoBw(0x80);*/

    while(1)
    {
        sleep_mode();
        // simple "I'm alive"
        i2c_Set_Reg(eI2cReg_Temperature, i2c_Get_Reg(eI2cReg_Temperature) + 1);

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
                    /*case eCmd_SetPwmFreq5KHz :
                    //    pwm_SetFrequency(5000);
                        break;
                    case eCmd_SetPwmFreq8KHz :
                    //    pwm_SetFrequency(8000);
                        break;
                    case eCmd_SetPwmFreq10KHz :
                        pwm_SetFrequency(10000);
                        break;
                    case eCmd_SetPwmFreq12KHz :
                    //    pwm_SetFrequency(12000);
                        break;
                    case eCmd_SetPwmFreq15KHz :
                        pwm_SetFrequency(15000);
                        break;
                    case eCmd_SetPwmFreq18KHz :
                    //    pwm_SetFrequency(18000);
                        break;*/

                    case eCmd_Reset :
                        ports_init();
                        i2c_Set_Reg(eI2cReg_Speed, 0);
                        cmdVal = 69;  // confirmation value
                        break;

                    // Debug Commands //

                    case eCmd_GetPinA :
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
                        break;

                    default :
                        if ((cmd & 0xF0) == eCmd_SetPwmPres)
                        {
                            cmdVal = cmd & 0x0F;
                            TCCR1B = (TCCR1B & 0xF0) | cmdVal;
                        }
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
                byte  val = i2c_Get_Reg(eI2cReg_Speed);
                if (i2c_Get_Reg(eI2cReg_Acceleration) == 0)
                    GoFw(val);
                else
                    GoBw(val);
            }
        }

        // ADC readings.
        // The most demanding reading is motor current. It must be sampled
        // right before the duty cycle ends (it ends at the compare match
        // interrupt, when TCNT == OCRA/B). The ADC samples 1.5 ADC-clocks
        // after conversion start, which means that the ADC conversion must
        // be triggered ...
        //  @Fadc=250KHz and @Fpwm=8KHz,
        //      1 / 250KHz * 1.5 = 6us
        //      6us / (1/8KHz / 256) = 12.288 ~ 13 TCNT counts
        // ... 13 TCNT counts before TCNT reaches OCRA/B.
        //ReadMotorCurrent();
        // After reading motor current, we read the remaining inputs, one
        // every loop. None of these need to be updated very frequently,
        // in, facto, motor current doesn't need high update rate either
        // (20sps is enough for now, 100sps in the future).
        {
            word  val = ReadAdc(4);
            // Vadc = Vcc * 1K / 11K
            // adc * VREFx10 / 1024 = Vcc * 10 / 11
            // Vcc * 10 = adc * VREFx10 * 11 / 1024;
            val = (long)val * VREFx10 * 11 / 1024;
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

        /*/ Only update if there are no limiting conditions.
        if ( (i2c_Get_Reg(eI2cReg_Status) & eStatus_Limiter_Mask) == 0 )
        {
            byte  val = i2c_Get_Reg(eI2cReg_Speed);
            if (gDir == 0)
            {
                GoFw(val);
            }
            else
            {
                GoBw(val);
            }
        }
        else
        {
            PortSet(A, eLED);
            AllOff();
        }*/

        // LED on if any limiting condition ocurring.
        /*if (i2c_Get_Reg(eI2cReg_Status))
        {
            PortSet(A, eLED);
        }
        else
        {
            PortClear(A, eLED);
        }*/
    }
}
