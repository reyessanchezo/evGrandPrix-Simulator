import time

from pyvesc import VESC

# serial port that VESC is connected to. Something like "COM3" for windows and as below for linux/mac

"""
serial_port = (
    "/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_301-if00"
)
"""

serial_port = "COM3"

# a function to show how to use the class with a with-statement
DUTY_CYCLE = 0.6
def run_motor_using_with():
    with VESC(serial_port=serial_port, timeout=0.5) as motor:
        #print("Firmware: ", motor.get_firmware_version())
        motor.set_duty_cycle(DUTY_CYCLE)
        #motor.set_rpm(1000)
        for i in range(100):
            time.sleep(0.1)
            motor.set_duty_cycle(DUTY_CYCLE)
            #motor.set_rpm(1000)
#square of rpm times some constant is the negative current to slow the motor

# a function to show how to use the class as a static object.
def run_motor_as_object():
    motor = VESC(serial_port=serial_port)
    print("Firmware: ", motor.get_firmware_version())

    # sweep servo through full range
    for i in range(100):
        time.sleep(0.01)
        motor.set_servo(i / 100)

    # IMPORTANT: YOU MUST STOP THE HEARTBEAT IF IT IS RUNNING BEFORE IT GOES OUT OF SCOPE. Otherwise, it will not
    #            clean-up properly.
    motor.stop_heartbeat()


def time_get_values():
    with VESC(serial_port=serial_port) as motor:
        start = time.time()
        motor.get_measurements()
        stop = time.time()
        print("Getting values takes ", stop - start, "seconds.")


if __name__ == "__main__":
    run_motor_using_with()
    run_motor_as_object()
    time_get_values()
