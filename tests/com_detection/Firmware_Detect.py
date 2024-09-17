from pyvesc import VESC
import detectComPortC
# serial port that VESC is connected to. Something like "COM3" for windows and as below for linux/mac
#serial_port = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_301-if00'

def printFirmwareVersion(serial_port):
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())

if __name__ == '__main__':
    detectedPorts = detectComPortC.serial_ports()
    if not detectedPorts:
        print("No ports detected.")
        exit()
    for i in range(len(detectedPorts)):
        print(f"{i}: {detectedPorts[i]}")
    serial_port = int(input("Choose an index for the COM port: "))
    while (serial_port <= 0 or serial_port > len(detectedPorts)):
        serial_port = int(input("Choose an index for the COM port: "))
    print(f"{serial_port[i]}")
    #printFirmwareVersion()

# Based on the example found in the PyVESC library.