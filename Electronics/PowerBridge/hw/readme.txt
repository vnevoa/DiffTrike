Here is the hardware design files for the DiffTrike h-bridge controller.
This is still work in progress, and the project is not yet totally decoupled
from my personal development environment, so you've been warned.

There are 4 boards in this project, developed with KiCAD:

 1) bridge-power
    The base board that holds the power switches (MOSFETs), DC-link capacitors,
    current sense resistors, fast current sens voltage comparator, 5V regulator
    and connectors for the controller and MOSFET driver boards.

 2) bridge-fet-drivers
    4 discreet MOSFET drivers, 2 for a N-channel and 2 for a P-channel, 24V
    power supply.

 3) bridge-ctrller
    Microcontroller and related support circuitry to control the bridge.

 4) bridge-ctrller-addon
    I2C isolation bridge, heatsink temperature sensing, motor temperature
    sensing support circuitry.
