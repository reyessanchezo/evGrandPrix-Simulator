import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyvesc import VESC, GetValues, GetVersion

from tools import choose_port

global motor1, motor2

MAX_RPM = 10000
motor_measurements = []
lock = threading.Lock()


# TODO: Need to simulate coasting the motor (Descending function).
# TODO: Figure out how often to take measurements.
# FIX: The program does not print rpm values every cycle. Check output.
#      GetMeasurements() is returning the wrong number of bytes and therefore measurements is of type GetRopotPosition, which does not have rpm as a value.


# 40% for 10 seconds
# 80% for 10 seconds
# Coast down to 40%
# When it reaches 40%, keep it at 40%
# Coast down to 0%
# When it reaches 0%, stop the motor
def tech_demo_data() -> list[float]:
    # 40% for 10 seconds, and 80% for 10 seconds
    rpm = [MAX_RPM* 0.4] * 100
    rpm.extend([MAX_RPM* 0.8] * 100)
    # duration = [5.0, 5.0]

    # 80% to 40% in 1/x descending steps
    a = np.linspace(0.8, 0.4, 50)

    # 40% to 0% in 1/x descending steps
    for i in range(len(a)):
        a[i] = a[i] / (i + 2) + 0.4

    a = a * MAX_RPM

    rpm.extend(a.tolist())
    # b = [0.1] * 50
    # duration.extend(b)

    # 40% for 10 seconds
    rpm.extend([MAX_RPM* 0.4] * 100)
    # duration.append(5)

    return rpm

def close_motor(motor) -> None:
    motor.set_current(0)
    motor.serial_port.flush()
    motor.serial_port.close()


def read_measurements(motor) -> None:
    while True:
        with lock:
            if motor.serial_port.in_waiting > 0:
                measurements = motor.get_measurements()

                if isinstance(measurements, GetValues):
                    record = {}
                    for field in measurements.fields:
                        record[field[0]] = getattr(measurements, field[0])

                    motor_measurements.append(record)

        time.sleep(0.1)



def plot_rpm(data) -> None:
    rpm = [x["rpm"] for x in data]
    plt.figure()
    plt.plot(rpm)
    plt.title("RPM vs Time")
    plt.xlabel("Time (.1 s)")
    plt.ylabel("RPM")
    plt.show()



def run(serial_port, rpm) -> None:
    with VESC(serial_port=serial_port) as motor:
        try:
            # Get firmware version and print it
            version = motor.get_firmware_version()
            if isinstance(version, GetVersion):
                print("Version: ", version)
            
            thread = threading.Thread(target=read_measurements, args=(motor,))
            thread.daemon = True
            thread.start()
            for rpm in rpm:
                rpm = round(rpm)
                with lock:
                    motor.set_rpm(rpm)

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            with lock:
                close_motor(motor)


if __name__ == "__main__":
    # Choose the serial ports
    s1 = choose_port()
    # s2 = choose_port()

    # Get tech demo data (rpm and time per rpm)
    rpm = tech_demo_data()
    
    # Start thread
    motor1 = threading.Thread(target=run, args=(s1, 1, rpm))
    # motor2 = threading.Thread(target=run, args=(s2, 2, rpm))
    motor1.start()
    # motor2.start()
    motor1.join()
    # motor2.join()

    # Plot the rpm of the results
    plot_rpm(motor_measurements)

    # Create dataframe and save results as csv file
    final_data = pd.DataFrame(motor_measurements)
    final_data.to_csv("motor_measurements.csv")

