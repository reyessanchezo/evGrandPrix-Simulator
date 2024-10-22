from pyvesc import VESC
import time
from tools.comportDetection import choose_port
from examples.motor_example import run

DUTY_CYCLE = 0.6


def run(s):
    with VESC(serial_port=s) as motor:
        try:
            # motor.set_duty_cycle(DUTY_CYCLE)
            rpms = [2000, 5000]
            for i in range(30):
                for rpm in rpms:
                    motor.serial_port.flush()
                    motor.set_rpm(rpm)
                    time.sleep(0.5)

            print("It finshed")
            motor.set_rpm(0)
            motor.serial_port.flush()
            motor.serial_port.close()
            return
        except KeyboardInterrupt:
            motor.set_rpm(0)
            motor.serial_port.flush()
            motor.serial_port.close()


if __name__ == "__main__":
    serial_port = choose_port()
    run(serial_port)
