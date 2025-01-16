import os
import sys
import threading
import time
from multiprocessing import Process

import matplotlib.pyplot as plt

from pyvesc import VESC, GetValues, GetVersion
from tools import aerodynamic_drag_power, choose_port

motor_measurements = []
dyno_measurements = []
lock1 = threading.Lock()
finished = False


def tech_demo_data() -> list[float]:
    interval = [3.0 for _ in range(10)]
    return interval


def close_motor(motor) -> None:
    motor.serial_port.flush()
    motor.serial_port.close()


def read_measurements(motor) -> None:
    while not finished:
        with lock1:
            measurements = motor.get_measurements()

            if isinstance(measurements, GetValues):
                last_rpm = measurements.rpm
                print("Kart RPM:", last_rpm)
                record = {}
                for field in measurements.fields:
                    record[field[0]] = getattr(measurements, field[0])

                # motor_measurements.append(record)

        time.sleep(0.5)


def plot_rpm(data) -> None:
    rpm = [x["rpm"] for x in data]
    plt.figure()
    plt.plot(rpm)
    plt.title("RPM vs Time")
    plt.xlabel("Time (.1 s)")
    plt.ylabel("RPM")
    plt.savefig("rpm_vs_time.png")
    plt.show()


def run_motor(serial_port, speeds) -> None:
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

            for s in speeds:
                s = round(s)
                with lock1:
                    motor.set_current(s)
                time.sleep(1)

            thread.join()
            print("Done")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            with lock1:
                close_motor(motor)


def test_dyno(dyno_port) -> None:
    with VESC(serial_port=dyno_port) as dyno:
        while True:
            measurements = dyno.get_measurements()
            if isinstance(measurements, GetValues):
                print("Dyno RPM:", measurements.rpm)
                # bp = aerodynamic_drag_power(measurements.rpm / 3)
                # amps = bp / measurements.v_in
                dyno.set_ib_current(0)

            time.sleep(0.1)


if __name__ == "__main__":
    # Choose the serial ports
    s1 = choose_port()
    s2 = choose_port()

    # Get tech demo data (rpm and time per rpm)
    rpm = tech_demo_data()

    motor1 = threading.Thread(
        target=run_motor,
        args=(
            s2,
            rpm,
        ),
    )

    motor2 = threading.Thread(target=test_dyno, args=(s2,))

    motor1.start()
    motor2.start()
    motor1.join()
    motor2.join()
