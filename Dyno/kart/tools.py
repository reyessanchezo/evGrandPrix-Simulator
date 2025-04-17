import math

# import pandas as pd
import serial.tools.list_ports


# Ports
def choose_port():
    serial_ports = sorted(serial.tools.list_ports.comports())
    if not serial_ports:
        raise Exception("There were no ports detected.")

    for idx, port in enumerate(serial_ports):
        print(f"{idx}: {port[0]}, {port[1]}, {port[2]}")

    serial_port = -1
    while serial_port < 0 or serial_port > len(serial_ports):
        serial_port = int(input("Choose an index for the COM port: "))

    return str(serial_ports[serial_port][0])


# Read CSV
# def process_data(path: str) -> list[list[float]]:
#     """
#     Open csv file as pandas dataframe and return a list of tuples of the values for each column.
#     """
#     race_info: pd.DataFrame = pd.read_csv(path)
#     race_info.fillna(0, inplace=True)
#     data: list[list[float]] = race_info.values.tolist()

#     return data


# Others
def rpm_to_dist(rpm: float, diameter: float, time: float = 1):
    circumference = math.pi * diameter
    distance = rpm * circumference * time
    return distance


def scale(ele: float, min_val: float, max_value: float, a: float, b: float):
    return a + (ele - min_val) * (b - a) / (max_value - min_val)
