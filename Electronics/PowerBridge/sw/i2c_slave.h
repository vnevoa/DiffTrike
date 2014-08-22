// This file has been prepared for Doxygen automatic documentation generation.
/*! \file ********************************************************************
*
* Based on ATMEL's AppNote AVR312 - Using the USI module as a TWI slave
*
****************************************************************************/

#define byte  unsigned char

#define TRUE                1
#define FALSE               0


#ifndef I2C_REGISTER_FILE_SIZE      // from Makefile, must be power of 2!
#   define I2C_REGISTER_FILE_SIZE  (8)
#else
#   if I2C_REGISTER_FILE_SIZE != 2
#       if I2C_REGISTER_FILE_SIZE != 4
#           if I2C_REGISTER_FILE_SIZE != 8
#               if I2C_REGISTER_FILE_SIZE != 16
#                   if I2C_REGISTER_FILE_SIZE != 32
#                       error "invalid I2C_REGISTER_FILE_SIZE!"
#                   endif
#               endif
#           endif
#       endif
#   endif
#endif


enum {
    eI2c_ROnly  = 0,
    eI2c_RW     = 1,
};

extern volatile byte  gI2C_RegFile[I2C_REGISTER_FILE_SIZE];


//! Prototypes
void i2c_Slave_Initialise (byte ownAddress);
byte i2c_Get_Changed_Mask (void);
void i2c_Set_Reg_Access (byte idx, byte is_writable);
//void i2c_Process_Overflow_intr (void);


inline static byte i2c_Get_Reg (byte idx)
{
    return gI2C_RegFile[idx];
};

inline static void i2c_Set_Reg (byte idx, byte val)
{
    gI2C_RegFile[idx] = val;
};

