import threading
import time

import matplotlib.pyplot as plt
import pandas as pd

from pyvesc import VESC, GetValues, GetVersion
from tools import aerodynamic_drag_power, choose_port

lock1 = threading.Lock()
lock2 = threading.Lock()

# TODO: Need to simulate coasting the motor (Descending function).
# TODO: Figure out how often to take measurements.
# FIX: The program does not print rpm values every cycle. Check output.
#      GetMeasurements() is returning the wrong number of bytes and therefore measurements is of type GetRopotPosition, which does not have rpm as a value.
finished = False


def close_motor(motor) -> None:
    motor.set_current(0)
    motor.stop_heartbeat()
    motor.serial_port.flush()
    motor.serial_port.close()


def read_measurements(motor) -> None:
    global finished
    global last_rpm
    while not finished:
        with lock1:
            # if motor.serial_port.in_waiting > 0:
            measurements = motor.get_measurements()

            if isinstance(measurements, GetValues):
                last_rpm = measurements.rpm
                record = {}
                for field in measurements.fields:
                    record[field[0]] = getattr(measurements, field[0])
                print("RPM:", last_rpm)

        time.sleep(0.05)


def run_motor(serial_port) -> None:
    global finished

    with VESC(serial_port=serial_port) as motor:
        try:
            # Get firmware version and print it
            version = motor.get_firmware_version()
            if isinstance(version, GetVersion):
                print("Version: ", version)

            thread = threading.Thread(target=read_measurements, args=(motor,))
            thread.start()

            with lock1:
                motor.set_rpm(2000)
                time.sleep(30)

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
    breaking_force = 500
    with VESC(serial_port=dyno_port) as dyno:
        print("Dyno connected")
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
                    dyno.set_ib_current(breaking_force)
                    data["rpm"].append(measurements.rpm)
                    data["duty_cycle_now"].append(measurements.duty_cycle_now)
                    data["avg_motor_current"].append(measurements.avg_motor_current)
                    data["avg_input_current"].append(measurements.avg_input_current)

                    print(
                        "RPM:",
                        measurements.rpm / 3,
                        "| Milliamps",
                        breaking_force,
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

    # Start thread
    motor1 = threading.Thread(
        target=run_motor,
        args=(s1,),
    )

    motor2 = threading.Thread(target=test_dyno, args=(s2,))
    motor1.start()
    motor2.start()
    motor1.join()
    motor2.join()

    # Create dataframe and save results as csv file
    final_data = pd.DataFrame(motor_measurements)
    final_data.to_csv("motor_measurements.csv")
