import serial.tools.list_ports
ports = serial.tools.list_ports.comports()


"""
for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))
"""


def serial_ports():
    pyserialPorts = serial.tools.list_ports.comports()
    result = []
    for port, desc, hwid in sorted(pyserialPorts):
        result.append(f"{port}")
    return result

#https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

if __name__ == '__main__':
    print(serial_ports())