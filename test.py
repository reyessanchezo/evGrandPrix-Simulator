import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyvesc import VESC, GetValues, GetVersion

from tools import aerodynamic_drag_power, choose_port

MAX_RPM = 4400 * 3
battery_voltage = 0
motor_measurements = []
dyno_measurements = []
lock1 = threading.Lock()
lock2 = threading.Lock()
finished = False
motor_rpm = 0
break_power = 0


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
    rpm = [MAX_RPM * 0.5] * 100
    rpm.extend([MAX_RPM * 0.8] * 100)
    # duration = [5.0, 5.0]

    rpm.extend([MAX_RPM * 0.4] * 100)

    return rpm


def close_motor(motor) -> None:
    motor.set_current(0)
    motor.stop_heartbeat()
    motor.serial_port.flush()
    motor.serial_port.close()


def read_measurements(motor) -> None:
    global finished
    while not finished:
        with lock1:
            # if motor.serial_port.in_waiting > 0:
            measurements = motor.get_measurements()

            if isinstance(measurements, GetValues):
                record = {}
                for field in measurements.fields:
                    record[field[0]] = getattr(measurements, field[0])

                motor_measurements.append(record)

        time.sleep(0.05)


def plot_rpm(data) -> None:
    rpm = [x["rpm"] for x in data]
    plt.figure()
    plt.plot(rpm)
    plt.title("RPM vs Time")
    plt.xlabel("Time (.1 s)")
    plt.ylabel("RPM")
    plt.savefig("rpm_vs_time.png")
    plt.show()


def run_motor(serial_port, rpm) -> None:
    global finished
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
                with lock1:
                    motor.set_rpm(rpm)

                time.sleep(0.1)

            with lock1:
                finished = True
            return

        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            with lock1:
                close_motor(motor)


def test_dyno(dyno_port) -> None:
    global finished
    global dyno_measurements

    with VESC(serial_port=dyno_port) as dyno:
        try:
            data = {
                "rpm": [],
                "duty_cycle_now": [],
                "avg_motor_current": [],
                "avg_input_current": [],
            }
            while not finished:
                measurements = dyno.get_measurements()

                if isinstance(measurements, GetValues):
                    bp = aerodynamic_drag_power(measurements.rpm / 3)
                    milliamps = bp * 1000 / measurements.v_in
                    dyno.set_ib_current(milliamps)
                    dyno_measurements.append(milliamps)
                    data["rpm"].append(measurements.rpm)
                    data["duty_cycle_now"].append(measurements.duty_cycle_now)
                    data["avg_motor_current"].append(measurements.avg_motor_current)
                    data["avg_input_current"].append(measurements.avg_input_current)

                    print(
                        "RPM:",
                        measurements.rpm / 3,
                        "| Watts",
                        bp,
                        "| Milliamps",
                        milliamps,
                    )

                time.sleep(0.1)
            df = pd.DataFrame(data)
            df.to_csv("dyno_measurements.csv")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            close_motor(dyno)


if __name__ == "__main__":
    # Choose the serial ports
    s1 = choose_port()
    s2 = choose_port()

    # Get tech demo data (rpm and time per rpm)
    rpm = tech_demo_data()

    # Start thread
    motor1 = threading.Thread(
        target=run_motor,
        args=(
            s1,
            rpm,
        ),
    )
    motor2 = threading.Thread(target=test_dyno, args=(s2,))
    motor1.start()
    motor2.start()
    motor1.join()
    motor2.join()

    # Create dataframe and save results as csv file
    final_data = pd.DataFrame(motor_measurements)
    final_data.to_csv("motor_measurements.csv")

    # Plot the rpm of the results
    # plot_rpm(motor_measurements)
    rpm = [x["rpm"] for x in motor_measurements]
    rpm = [x / 3 for x in rpm]
    f, ax = plt.subplots(1, 2)
    ax[0].plot(rpm)
    ax[1].plot(dyno_measurements)
    plt.show()
