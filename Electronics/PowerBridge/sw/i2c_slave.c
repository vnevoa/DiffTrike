// This file has been prepared for Doxygen automatic documentation generation.
/*! \file ********************************************************************
*
* Based on ATMEL's AppNote AVR312 - Using the USI module as a TWI slave
*
****************************************************************************/

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include "i2c_slave.h"

// TWI state machine
#define USI_SLAVE_CHECK_ADDRESS                 0x00
#define USI_SLAVE_SEND_DATA                     0x01
#define USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA  0x02
#define USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA    0x03
#define USI_SLAVE_START_DATA_RX                 0x04
#define USI_SLAVE_GET_REG_FILE_INDEX            0x05
#define USI_SLAVE_REQUEST_DATA                  0x06
#define USI_SLAVE_GET_DATA_AND_SEND_ACK         0x07
 

//! Device dependent defines
#if defined(__AVR_ATtiny26__)
    #define DDR_USI             DDRB
    #define PORT_USI            PORTB
    #define PIN_USI             PINB
    #define PORT_USI_SDA        PORTB0
    #define PORT_USI_SCL        PORTB2
    #define PIN_USI_SDA         PINB0
    #define PIN_USI_SCL         PINB2
    #define USI_START_COND_INT  USISIF
    #define USI_START_VECTOR    USI_STRT_vect
    #define USI_OVERFLOW_VECTOR USI_OVF_vect
#endif

#if defined(__AVR_ATtiny2313__)
    #define DDR_USI             DDRB
    #define PORT_USI            PORTB
    #define PIN_USI             PINB
    #define PORT_USI_SDA        PORTB5
    #define PORT_USI_SCL        PORTB7
    #define PIN_USI_SDA         PINB5
    #define PIN_USI_SCL         PINB7
    #define USI_START_COND_INT  USISIF
    #define USI_START_VECTOR    USI_STRT_vect
    #define USI_OVERFLOW_VECTOR USI_OVF_vect
#endif

#if defined(__AVR_ATtiny25__) | defined(__AVR_ATtiny45__) | defined(__AVR_ATtiny85__)
    #define DDR_USI             DDRB
    #define PORT_USI            PORTB
    #define PIN_USI             PINB
    #define PORT_USI_SDA        PORTB0
    #define PORT_USI_SCL        PORTB2
    #define PIN_USI_SDA         PINB0
    #define PIN_USI_SCL         PINB2
    #define USI_START_COND_INT  USICIF
    #define USI_START_VECTOR    USI_START_vect
    #define USI_OVERFLOW_VECTOR USI_OVF_vect
#endif

#if defined(__AVR_ATmega165__) | \
    defined(__AVR_ATmega325__) | defined(__AVR_ATmega3250__) | \
    defined(__AVR_ATmega645__) | defined(__AVR_ATmega6450__) | \
    defined(__AVR_ATmega329__) | defined(__AVR_ATmega3290__) | \
    defined(__AVR_ATmega649__) | defined(__AVR_ATmega6490__)
    #define DDR_USI             DDRE
    #define PORT_USI            PORTE
    #define PIN_USI             PINE
    #define PORT_USI_SDA        PORTE5
    #define PORT_USI_SCL        PORTE4
    #define PIN_USI_SDA         PINE5
    #define PIN_USI_SCL         PINE4
    #define USI_START_COND_INT  USISIF
    #define USI_START_VECTOR    USI_START_vect
    #define USI_OVERFLOW_VECTOR USI_OVERFLOW_vect
#endif

#if defined(__AVR_ATmega169__)
    #define DDR_USI             DDRE
    #define PORT_USI            PORTE
    #define PIN_USI             PINE
    #define PORT_USI_SDA        PORTE5
    #define PORT_USI_SCL        PORTE4
    #define PIN_USI_SDA         PINE5
    #define PIN_USI_SCL         PINE4
    #define USI_START_COND_INT  USISIF
    #define USI_START_VECTOR    USI_STRT_vect
    #define USI_OVERFLOW_VECTOR USI_OVF_vect
#endif

//! Functions implemented as macros
#define SET_USI_TO_SEND_ACK()                                                                                 \
{                                                                                                             \
        USIDR    =  0;                                              /* Prepare ACK                         */ \
        DDR_USI |=  (1<<PORT_USI_SDA);                              /* Set SDA as output                   */ \
        USISR    =  (0<<USI_START_COND_INT)|(1<<USIOIF)|(1<<USIPF)|(1<<USIDC)|  /* Clear all flags, except Start Cond  */ \
                    (0x0E<<USICNT0);                                /* set USI counter to shift 1 bit. */ \
}

#define SET_USI_TO_READ_ACK()                                                                                 \
{                                                                                                             \
        DDR_USI &=  ~(1<<PORT_USI_SDA);                             /* Set SDA as input */                    \
        USIDR    =  0;                                              /* Prepare ACK        */                  \
        USISR    =  (0<<USI_START_COND_INT)|(1<<USIOIF)|(1<<USIPF)|(1<<USIDC)|  /* Clear all flags, except Start Cond  */ \
                    (0x0E<<USICNT0);                                /* set USI counter to shift 1 bit. */ \
}

#define SET_USI_TO_TWI_START_CONDITION_MODE()                                                                                     \
{                                                                                                                                 \
  USICR    =  (1<<USISIE)|(0<<USIOIE)|                        /* Enable Start Condition Interrupt. Disable Overflow Interrupt.*/  \
              (1<<USIWM1)|(0<<USIWM0)|                        /* Set USI in Two-wire mode. No USI Counter overflow hold.      */  \
              (1<<USICS1)|(0<<USICS0)|(0<<USICLK)|            /* Shift Register Clock Source = External, positive edge        */  \
              (0<<USITC);                                                                                                         \
  USISR    =  (0<<USI_START_COND_INT)|(1<<USIOIF)|(1<<USIPF)|(1<<USIDC)|  /* Clear all flags, except Start Cond               */  \
              (0x0<<USICNT0);                                                                                                     \
}

#define SET_USI_TO_SEND_DATA()                                                                               \
{                                                                                                            \
    DDR_USI |=  (1<<PORT_USI_SDA);                                  /* Set SDA as output                  */ \
    USISR    =  (0<<USI_START_COND_INT)|(1<<USIOIF)|(1<<USIPF)|(1<<USIDC)|      /* Clear all flags, except Start Cond */ \
                (0x0<<USICNT0);                                     /* set USI to shift out 8 bits        */ \
}

#define SET_USI_TO_READ_DATA()                                                                               \
{                                                                                                            \
    DDR_USI &= ~(1<<PORT_USI_SDA);                                  /* Set SDA as input                   */ \
    USISR    =  (0<<USI_START_COND_INT)|(1<<USIOIF)|(1<<USIPF)|(1<<USIDC)|      /* Clear all flags, except Start Cond */ \
                (0x0<<USICNT0);                                     /* set USI to shift out 8 bits        */ \
}


/*! Global Variables
 */


/*! Local variables
 */
static byte  sSlaveAddress;
static byte  sDrvState;
static byte  sRegIdx;
static byte  sWritableRegsMask = 0;

static volatile byte  sChangedRegMask;


//********** USI_TWI functions **********//

/*! \brief
 * Initialise USI for TWI Slave mode.
 */
void i2c_Slave_Initialise (byte ownAddress)
{
    sRegIdx = 0;
    sChangedRegMask = 0;

    sSlaveAddress = ownAddress;

    // Allow open colector outputs. When DDR on SCL/SDA are set to 1, they will
    // be open colector outputs (otherwise will be inputs).
    // This avoids having a moment during configuration of the pins where some
    // are set as totempole outputs (which can affect other communications
    // on-going on the bus).
    USICR = _BV(USIWM1);

    // Set the pins to the required config. Set the output value first to 1,
    // otherwise they will momentarly force a zero on the bus, which can disrupt
    // other communication going-on.
    // SCL must be output so that the SC detector can hold it low after a SC.
    PORT_USI |=  (1<< PORT_USI_SCL);     // Set SCL high
    PORT_USI |=  (1<< PORT_USI_SDA);     // Set SDA high
    DDR_USI  |=  (1<< PORT_USI_SCL);     // Set SCL as output
    DDR_USI  &= ~(1<< PORT_USI_SDA);     // Set SDA as input

    USICR = (1<<USISIE) | (0<<USIOIE) |                 // Enable Start Condition Interrupt. Disable Overflow Interrupt.
            (1<<USIWM1) | (0<<USIWM0) |                 // Set USI in Two-wire mode. No USI Counter overflow prior
                                                        // to first Start Condition (potential failure)
            (1<<USICS1) | (0<<USICS0) | (0<<USICLK) |   // Shift Register Clock Source = External, positive edge
            (0<<USITC);
    // Clear all interrupt flags and reset overflow counter
    USISR = _BV(USISIF) | _BV(USIOIF) | _BV(USIPF) | _BV(USIDC);
}


/*! \brief Return the mask of changed registers since previous call.
 *  Sets the internal mask to zeros.
 */
byte i2c_Get_Changed_Mask (void)
{
    uint8_t  prevSREG = SREG;
    cli();
    byte  tmp = sChangedRegMask;
    sChangedRegMask = 0;
    SREG = prevSREG;
    return tmp;
}


void i2c_Set_Reg_Access (byte idx, byte is_writable)
{
    if (is_writable)
        sWritableRegsMask |= _BV(idx);
    else
        sWritableRegsMask &= ~_BV(idx);
}


#define LON     PORTA |= _BV(PA7);      // LED ON
#define LOFF    PORTA &= ~_BV(PA7);     // LED OFF

/*! \brief Usi start condition ISR
 * Detects the USI_TWI Start Condition and intialises the USI
 * for reception of the "TWI Address" packet.
 */
ISR(USI_START_VECTOR)
{
    // Set default starting conditions for new TWI packet
    DDR_USI  &= ~_BV(PORT_USI_SDA);     // Set SDA as input

    // Wait for the start condition to complete. We're in start condition while
    // SCL is high and SDA is low.
    // This can take 5us (half I2C clock period @ 100KHz).
    while (
        ((PIN_USI & _BV(PIN_USI_SCL)) != 0) &&      // SCL is high
        ((PIN_USI & _BV(PIN_USI_SDA)) == 0)         // SDA is low
    );

    if ( !( PIN_USI & _BV(PIN_USI_SDA) ) )
    {
        // a Stop Condition did not occur
        USICR =
            // keep Start Condition Interrupt enabled to detect RESTART
            ( 1 << USISIE ) |
            // enable Overflow Interrupt
            ( 1 << USIOIE ) |
            // set USI in Two-wire mode, hold SCL low on USI Counter overflow
            ( 1 << USIWM1 ) | ( 1 << USIWM0 ) |
            // Shift Register Clock Source = External, positive edge
            // 4-Bit Counter Source = external, both edges
            ( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) |
            // no toggle clock-port pin
            ( 0 << USITC );
    }
    else
    {
        // a Stop Condition did occur
        USICR =
            // enable Start Condition Interrupt
            ( 1 << USISIE ) |
            // disable Overflow Interrupt
            ( 0 << USIOIE ) |
            // set USI in Two-wire mode, no USI Counter overflow hold
            ( 1 << USIWM1 ) | ( 0 << USIWM0 ) |
            // Shift Register Clock Source = external, positive edge
            // 4-Bit Counter Source = external, both edges
            ( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) |
            // no toggle clock-port pin
            ( 0 << USITC );
    } // end if

    USISR =
       // clear interrupt flags - resetting the Start Condition Flag will
       // release SCL
       ( 1 << USI_START_COND_INT ) | ( 1 << USIOIF ) |
       ( 1 << USIPF ) | ( 1 << USIDC ) |
       // set USI to sample 8 bits (count 16 external SCL pin toggles)
       ( 0 << USICNT0);

    sDrvState = USI_SLAVE_CHECK_ADDRESS;
}


/*! \brief USI counter overflow ISR
 * Handles all the comunication. Is disabled only when waiting
 * for new Start Condition.
 */
ISR(USI_OVERFLOW_VECTOR)
{
    switch (sDrvState)
    {
        // ---------- Address mode ----------
        // Check address and send ACK (and next USI_SLAVE_SEND_DATA) if OK, else reset USI.
        case USI_SLAVE_CHECK_ADDRESS :
            if (/*(USIDR == 0) ||*/ ((USIDR>>1) == sSlaveAddress))
            {
                LON
                if ( USIDR & 0x01 )
                {   // read from slave registers
                    sDrvState = USI_SLAVE_SEND_DATA;
                }
                else
                {   // write to slave's registers
                    sDrvState = USI_SLAVE_START_DATA_RX;
                }
                SET_USI_TO_SEND_ACK();
            }
            else
            {
                SET_USI_TO_TWI_START_CONDITION_MODE();
            }
            break;

        // ----- Write data to master ------

        // Check reply and goto USI_SLAVE_SEND_DATA if OK, else reset USI.
        case USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA :
            if ( USIDR ) // If NACK, the master does not want more data.
            {
                SET_USI_TO_TWI_START_CONDITION_MODE();
                LOFF
                return;
            }
            // From here we just drop straight into USI_SLAVE_SEND_DATA if the master sent an ACK

        // Copy data from buffer to USIDR and set USI to shift byte. Next USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA
        case USI_SLAVE_SEND_DATA :
            sRegIdx &= I2C_REGISTER_FILE_SIZE - 1;
            // Send one register from the register file and increase the index
            USIDR = gI2C_RegFile[sRegIdx++];
            sDrvState = USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA;
            SET_USI_TO_SEND_DATA();
            break;

        // Set USI to sample reply from master. Next USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA
        case USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA :
            sDrvState = USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA;
            SET_USI_TO_READ_ACK();
            break;

        // ----- Read data from master ------
        case USI_SLAVE_START_DATA_RX :
            sDrvState = USI_SLAVE_GET_REG_FILE_INDEX;
            SET_USI_TO_READ_DATA();
            break;

        case USI_SLAVE_GET_REG_FILE_INDEX :
            // (on invalid index, the read and write routines will take care of it)
            sRegIdx = USIDR;
            sDrvState = USI_SLAVE_REQUEST_DATA;
            SET_USI_TO_SEND_ACK();
            break;

        // Set USI to sample data from master. Next USI_SLAVE_GET_DATA_AND_SEND_ACK.
        case USI_SLAVE_REQUEST_DATA :
            sDrvState = USI_SLAVE_GET_DATA_AND_SEND_ACK;
            SET_USI_TO_READ_DATA();
            break;

        // Copy data from USIDR and send ACK. Next USI_SLAVE_REQUEST_DATA
        case USI_SLAVE_GET_DATA_AND_SEND_ACK :
            LOFF
            sRegIdx &= I2C_REGISTER_FILE_SIZE - 1;
            {
                byte  reg_mask = _BV(sRegIdx);
                if (reg_mask & sWritableRegsMask)
                {
                    gI2C_RegFile[sRegIdx] = USIDR;
                    sChangedRegMask |= reg_mask;    // flag the register as changed
                }
                sRegIdx++;

                sDrvState = USI_SLAVE_REQUEST_DATA;
                SET_USI_TO_SEND_ACK();
            }
            break;
    }
}
