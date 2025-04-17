import time
from multiprocessing import Process

from pyvesc import VESC
from pyvesc.VESC.messages.getters import GetValues
from tools import acceleration_torque, choose_port, rpm_to_motorspeed

RATE = 0.001  # Necessary for dv dt.
prev_rpm = 0
lamp = [0.0] * 1000


def run(kart_port) -> None:
    with VESC(serial_port=kart_port) as motor:
        try:
            while True:
                motor.serial_port.flush()
                motor.set_duty_cycle(0.70)
                time.sleep(0.5)

        except KeyboardInterrupt:
            motor.serial_port.close()


def test_dyno(dyno_port) -> None:
    global prev_rpm
    with VESC(serial_port=dyno_port) as dyno:
        try:
            while True:
                measurements = dyno.get_measurements()

                if isinstance(measurements, GetValues):
                    erpm = measurements.rpm
                    rpm = erpm / 3
                    dvdt = (rpm - prev_rpm) / RATE

                    print("Dyno RPM:", rpm)
                    print("dv/dt:", rpm)

                    bp = acceleration_torque(rpm, dvdt)
                    prev_rpm = erpm

                    print("B Watts:", bp)
                    amps = bp / measurements.v_in

                    if amps >= 70:
                        amps = 70
                    elif amps <= -70:
                        amps = -70

                    lamp.append(float(amps))
                    lamp.pop(0)

                    avg = sum(lamp) / len(lamp)
                    print("B Amps:", avg)

                    if avg >= 0:
                        dyno.set_ib_current(avg)
                    else:
                        dyno.set_current(avg)

                time.sleep(RATE)
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
    kart_port = choose_port()
    dyno_port = choose_port()

    kart_motor = Process(target=run, args=(kart_port,))
    dyno_motor = Process(target=test_dyno, args=(dyno_port,))

    kart_motor.start()
    dyno_motor.start()
    kart_motor.join()
    dyno_motor.join()
