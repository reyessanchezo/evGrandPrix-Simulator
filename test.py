import threading
import time

import numpy as np
from pyvesc import VESC, GetRotorPosition

from tools.comport_detection import choose_port

global motor1, motor2

MAX_RPM = 4500

# 40% for 10 seconds
# 80% for 10 seconds
# Coast down to 40%
# When it reaches 40%, keep it at 40%
# Coast down to 0%
# When it reaches 0%, stop the motor

# TODO: Need to simulate coasting the motor.
final = [[], []]
rpms_m1 = [np.multiply(MAX_RPM, 0.4), np.multiply(MAX_RPM, 0.8), 0]
duration = [10, 10, 10]
rpms_m2 = rpms_m1[::-1]
rpms = [rpms_m1, rpms_m2]


# TODO: Make the motor run at different rpms.
# TODO: Figure out how often to take measurements.
# FIX: This function is not called at the end of the program.

# def end():
#     motor1.join()
#     motor2.join()
#     m1_n = len(final[0])
#     m2_n = len(final[2])
#     n = max(m1_n, m2_n)
#     print("Motor 1 measurements:" + str(final[0][:n]))
#     print("Motor 2 measurements:" + str(final[1][:n]))


# FIX: The program does not print rpm values every cycle. Check output.
#      GetMeasurements() is returning the wrong number of bytes and therefore measurements is of type GetRopotPosition, which does not have rpm as a value.


def run(serial_port, n):
    with VESC(serial_port=serial_port) as motor:
        try:
            for n, rpm in enumerate(rpms[n - 1]):
                rpm = int(rpm)
                motor.set_rpm(rpm)
                measurements = motor.get_measurements()
                if measurements is not None:
                    if not isinstance(measurements, GetRotorPosition):
                        final[n - 1].append(measurements.rpm)
                        print(measurements.rpm)

                time.sleep(duration[n])
        except KeyboardInterrupt:
            # end() # FIX: This function is not called at the end of the program.
            motor.set_current(0)
            motor.serial_port.flush()
            motor.serial_port.close()


if __name__ == "__main__":
    s1 = choose_port()
    s2 = choose_port()
    motor1 = threading.Thread(target=run, args=(s1, 1))
    # motor2 = threading.Thread(target=run, args=(s2, 2))
    motor1.start()
    # motor2.start()
