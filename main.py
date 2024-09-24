import pyvesc
from pyvesc import VESC
from tools.comportDetection import choose_port

#defines a serial port using our tool.
serial_port = choose_port()

def get_info():
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        print("Measurements: ", motor.get_measurements())


if __name__ == "__main__":
    get_info()
