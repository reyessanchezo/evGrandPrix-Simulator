# Torque Sensor

This folder covers a few files that bridge the gap between the main program/pc and the integrated torque sensor from ATO.

ArtemisMain contains the project file to upload to an Artemis Nano. This folder is currently missing an electrical diagram, but datasheet and configuration images are included.

## ArtemisMain

This program serves as the bridge between the main program and torque sensor. It has additional functionality, including Serial communication to output a throttle signal (0-3.3V).

## OLD

This folder contains test programs that were used in the development of the communication between the Serial Artemis Nano and the RS-485 
