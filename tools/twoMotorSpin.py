from pyvesc import VESC
import time
from comport_detection import choose_port
from multiprocessing import Process

def rpm_spin(motor, rpm):
    motor.serial_port.flush()
    motor.set_rpm(rpm)

def close_motor(motor):
    motor.set_rpm(rpm)
    motor.serial_port.flush()
    motor.serial_port.close()
    

def run_two_independent(acceleration_motor_serial, brake_motor_serial):
    print(f"accelation, brake: {accMotor}, {brkMotor}")
    
    return
    # we shouldn't need anything past this until we have two motors
    print("ANYTHING BEYOND THIS POINT ASSUMES THE TWO MOTORS ARE NOT CONNECTED\nCONFIRM THEY ARE NOT CONNECTED TO EACH OTHER")
    cn = input("Type: CONFIRM to continue: ")

    if cn is not "CONFIRM":
        print("RETURNING")
        return
    
    accRPMs = [2000, 3000, 4000]
    brkRPMs = [4000, 3000, 2000]

    with VESC(serial_port=acceleration_motor_serial) as accMotor:
        with VESC(serial_port=brake_motor_serial) as brkMotor:
            try:
                for i in range(30):
                    for idx in range(arrRPMs):
                        m1 = Process(target=rpm_spin, args=(accMotor,accRPMs[idx],))
                        m2 = Process(target=rpm_spin, args=(brkMotor,brkRPMs[idx],))
                        m1.start()
                        m2.start()
                        m1.join()
                        m2.join()
                        time.sleep(0.5)

                print("It finshed")
                m1 = Process(target=close_motor, args=(accMotor,))
                m2 = Process(target=close_motor, args=(brkMotor,))
                m1.start()
                m2.start()
                m1.join()
                m2.join()
                return
            except KeyboardInterrupt:
                m1 = Process(target=close_motor, args=(accMotor,))
                m2 = Process(target=close_motor, args=(brkMotor,))
                m1.start()
                m2.start()
                m1.join()
                m2.join()
                return


if __name__ == "__main__":
    print("ACCELERATION MOTOR")
    accMotor = choose_port()
    print("BRAKE MOTOR")
    brkMotor = choose_port()
    run_two_independent(acceleration_motor_serial=accMotor, brake_motor_serial=brkMotor)
