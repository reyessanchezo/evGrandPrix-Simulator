import serial.tools.list_ports

def serial_ports():
    pyserialPorts = serial.tools.list_ports.comports()
    result = []
    for port, desc, hwid in sorted(pyserialPorts):
        result.append((port, desc, hwid))
    return result

# code based off of an example from:
# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

def choose_port():
    detectedPorts = serial_ports()
    if not detectedPorts:
        raise Exception("There were no ports detected.")
    for i in range(len(detectedPorts)):
        print(f"{i}: {detectedPorts[i][0]}, {detectedPorts[i][1]}, {detectedPorts[i][2]}")
    serial_port = -1
    while (serial_port < 0 or serial_port > len(detectedPorts)):
        serial_port = int(input("Choose an index for the COM port: "))
    return f"{detectedPorts[i][0]}"

if __name__ == '__main__':
    print(f"{choose_port()}")
