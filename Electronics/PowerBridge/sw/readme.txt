Here is the software for the DiffTrike h-bridge controller.
This is still work in progress, and the project is not yet totally decoupled
from my personal development environment, so you've been warned.

The software implements an I2C interface of 8 registers of 1 byte and controls
the 4 switches (currently MOSFETs) of an h-bridge by providing speed (PWM) and
reporting motor current, temperatures and bridge supply voltage.
Synchronous rectification is employed for improved efficiency over the simpler
assynchronous method.
