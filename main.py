import pyvesc
from pyvesc import VESC

# Waiting for function that recognizes usb port
# serial_port = "COM3"
serial_port = ""
print(dir(pyvesc))


def get_info():
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        print("Measurements: ", motor.get_measurements())


if __name__ == "__main__":
    get_info()
