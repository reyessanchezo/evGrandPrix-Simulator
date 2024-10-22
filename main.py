import pyvesc
from pyvesc import VESC
from tools.comportDetection import choose_port
from examples.motor_example import run_motor_using_with

#defines a serial port using our tool.
serial_port = choose_port()

def get_info():
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        print("Measurements: ", motor.get_measurements())


if __name__ == "__main__":
    print("0:get_info()\n1:set_duty_cycle(0.6) for 10s\n")
    c = int(input())
    if (c == 0):
        get_info()
    elif (c == 1):
        run_motor_using_with()
