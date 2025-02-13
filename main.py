import time
from multiprocessing import Process

from pyvesc import VESC
from pyvesc.VESC.messages.getters import GetValues
from tools import acceleration_torque, choose_port, rpm_to_motorspeed

prev_erpm = 0


def run(kart_port) -> None:
    with VESC(serial_port=kart_port) as motor:
        try:
            while True:
                motor.serial_port.flush()
                motor.set_duty_cycle(0.25)
                time.sleep(0.5)

        except KeyboardInterrupt:
            motor.serial_port.close()


def test_dyno(dyno_port) -> None:
    global prev_erpm
    with VESC(serial_port=dyno_port) as dyno:
        try:
            n = 50
            while True:
                measurements = dyno.get_measurements()

                if isinstance(measurements, GetValues):
                    erpm = measurements.rpm
                    print("Dyno RPM:", erpm / 3)

                    bp = acceleration_torque(erpm / 3, prev_erpm / 3)
                    prev_erpm = erpm

                    print("Breaking watts:", bp)
                    amps = bp / measurements.v_in
                    print("Breaking amps:", amps)
                    if n < 0:
                        dyno.set_ib_current(amps.out)
                    n -= 1

                time.sleep(0.1)
        except KeyboardInterrupt:
            dyno.serial_port.close()

def test_dyno_breaking_amps(dyno_port, amps) -> None:
    global prev_rpm
    with VESC(serial_port=dyno_port) as dyno:
        try:
            measurements = dyno.get_measurements()
            
            if isinstance(measurements, GetValues):
                erpm = measurements.rpm
                rpm = erpm / 3
                print("Dyno RPM:", erpm / 3)
                
                bp = acceleration_torque(rpm, prev_rpm / 3)
                prev_rpm = rpm
                
                print("Breaking watts:", bp)
                amps = bp / measurements.v_in
                print("Breaking amps:", amps)
                dyno.set_ib_current(amps.out)
        except KeyboardInterrupt:
            dyno.serial_port.close()


if __name__ == "__main__":
    # KART PID=0483:5740
    kart_port = choose_port()
    dyno_port = choose_port()

    kart_motor = Process(target=run, args=(kart_port,))
    dyno_motor = Process(target=test_dyno, args=(dyno_port,))

    kart_motor.start()
    dyno_motor.start()
    kart_motor.join()
    dyno_motor.join()
