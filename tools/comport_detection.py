import serial.tools.list_ports


def _serial_ports():
    pyserialPorts = serial.tools.list_ports.comports()
    result = []
    for port, desc, hwid in sorted(pyserialPorts):
        result.append((port, desc, hwid))
    return result


# code based off of an example from:
# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python


def choose_port():
    detected_ports = _serial_ports()
    if not detected_ports:
        raise Exception("There were no ports detected.")
    for i in range(len(detected_ports)):
        print(
            f"{i}: {detected_ports[i][0]}, {detected_ports[i][1]}, {detected_ports[i][2]}"
        )
    serial_port = -1
    while serial_port < 0 or serial_port > len(detected_ports):
        serial_port = int(input("Choose an index for the COM port: "))
    return f"{detected_ports[serial_port][0]}"


if __name__ == "__main__":
    print(choose_port())
