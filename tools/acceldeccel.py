import numpy as np
import matplotlib.pyplot as plt

##STATIC Globals
TRANSMISSION_EFFICIENCY = 0.9
TIRE_DIAMETER = 0.3  ##m
GEARING_RATIO = 1.0  ##tire rev / motor rev
ROLLING_RESISTANCE = 1.0  ##Nm
MASS = 150.0  ##kg
GRAV_ACCELLERATION = 9.8  ##m/s^2
TIRE_PRESSURE = 2.0  ##barr
DRAG_COEFF = 0.8  ##unitless
MAX_CROSSSECTIONAL_AREA = 0.5  ##m^2
AIR_DENSITY = 1.2  ##kg/m^3

MOTORTORQUE = 3.7 * 3  ##Nm
TIRETORQUE = 0.0
STATICFRICTION = 2.480847866 

MOTOR_SPEED = 21.220659078940496  ##rev/s for vel = 20m/s ##motorspeed is rotations per second

def rpm_to_motorspeed(rpm):
    rpmNum = rpm
    return rpmNum * 60

def velocity(motorspeed):  ##probable inputs
    return GEARING_RATIO * rpm_to_motorspeed(motorspeed) * TIRE_DIAMETER * np.pi


def max_acceleration (motor_speed):
    kartMaxForce = (2 * MOTORTORQUE * GEARING_RATIO * TRANSMISSION_EFFICIENCY) / (MASS * TIRE_DIAMETER)
    kartBreakAwayForce = 0.99 * GRAV_ACCELLERATION * STATICFRICTION
    vel = velocity(motor_speed)
    chunk2 = (DRAG_COEFF * MAX_CROSSSECTIONAL_AREA * AIR_DENSITY * velocity(motor_speed) ** 2) / (MASS * 2)
    chunk3 = 0.005 + (1 / TIRE_PRESSURE) * (0.01 + 0.0095 * ((3.6 * velocity(motor_speed)) / 100) ** 2) * GRAV_ACCELLERATION
    if kartMaxForce > kartBreakAwayForce:
        return kartBreakAwayForce - chunk2 - chunk3
    else:
        return kartMaxForce - chunk2 - chunk3
    
def max_braking(motor_speed):
    kartBreakAwayForce = 0.99 * GRAV_ACCELLERATION * STATICFRICTION
    chunk2 = (DRAG_COEFF * MAX_CROSSSECTIONAL_AREA * AIR_DENSITY * velocity(motor_speed) ** 2) / (MASS * 2)
    chunk3 = 0.005 + (1 / TIRE_PRESSURE) * (0.01 + 0.0095 * ((3.6 * velocity(motor_speed)) / 100) ** 2) * GRAV_ACCELLERATION
    return (-1 * kartBreakAwayForce) - chunk2 - chunk3

if __name__ == '__main__':    
    rpm = 3000
    rps = rpm_to_motorspeed(rpm)
    print(f'RPM: {rpm} RPS: {rps}')
    speed = [] #motor speed
    for i in range(0, int(rpm)):
        speed.append(i)
    a = []
    for s in speed:
        srps = rpm_to_motorspeed(s)
        a.append(max_braking(srps))
        
    plt.plot(speed, a)
    plt.xlabel("Motor Speed (RPS)")
    plt.ylabel("Max Deceleration (N)")
    plt.show()
