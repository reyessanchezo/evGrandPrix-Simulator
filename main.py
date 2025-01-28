from pyvesc import VESC
import time
from pyvesc.VESC.messages.getters import GetValues
from tools import choose_port, acceleration_torque
from multiprocessing import Process

def run(kart_port) -> None:
    with VESC(serial_port=kart_port) as motor:
        try:
            while True:
                motor.serial_port.flush()
                motor.set_duty_cycle(0.1)
                time.sleep(0.5)

        except KeyboardInterrupt:
            motor.serial_port.close()


def test_dyno(dyno_port) -> None:
    with VESC(serial_port=dyno_port) as dyno:
        try:
            while True:
                measurements = dyno.get_measurements()

                if isinstance(measurements, GetValues):
                    erpm = measurements.rpm
                    bp = acceleration_torque(erpm / 3)
                    amps = bp / measurements.v_in
                    dyno.set_ib_current(amps)

                time.sleep(0.1)
        except KeyboardInterrupt:
            dyno.serial_port.close()

if __name__ == "__main__":
    serial_port = choose_port()
    
    kart_motor = Process(target=run, args=(serial_port,))
    kart_motor.start()
    kart_motor.join()

