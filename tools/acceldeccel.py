import numpy as np
import matplotlib.pyplot as plt
from NumClass import Num

##STATIC Globals
TRANSMISSION_EFFICIENCY = Num(0.9)
TIRE_DIAMETER = Num(0.3)  ##m
GEARING_RATIO = Num(1.0)  ##tire rev / motor rev
ROLLING_RESISTANCE = Num(1.0)  ##Nm
MASS = Num(150.0)  ##kg
GRAV_ACCELLERATION = Num(9.8)  ##m/s^2
TIRE_PRESSURE = Num(2.0)  ##barr
DRAG_COEFF = Num(0.8)  ##unitless
MAX_CROSSSECTIONAL_AREA = Num(0.5)  ##m^2
AIR_DENSITY = Num(1.2)  ##kg/m^3

MOTORTORQUE = Num(3.7 * 3)  ##Nm
TIRETORQUE = Num(0.0)
STATICFRICTION = Num(2.480847866) 

MOTOR_SPEED = Num(21.220659078940496)  ##rev/s for vel = 20m/s

def rpm_to_motorspeed(rpm):
    rpmNum = Num(rpm)
    return rpmNum / Num(60)

def velocity(motorspeed):  ##probable inputs
    return GEARING_RATIO * rpm_to_motorspeed(motorspeed) * TIRE_DIAMETER * Num(np.pi)


def max_acceleration (motor_speed):
    kartMaxForce = (Num(2) * MOTORTORQUE * GEARING_RATIO * TRANSMISSION_EFFICIENCY) / (MASS * TIRE_DIAMETER)
    kartBreakAwayForce = Num(0.99) * GRAV_ACCELLERATION * STATICFRICTION
    vel = velocity(motor_speed)
    chunk2 = (DRAG_COEFF * MAX_CROSSSECTIONAL_AREA * AIR_DENSITY * velocity(motor_speed) ** Num(2)) / (MASS * Num(2))
    chunk3 = Num(0.005) + (Num(1) / TIRE_PRESSURE) * (Num(0.01) + Num(0.0095) * ((Num(3.6) * velocity(motor_speed)) / Num(100)) ** Num(2)) * GRAV_ACCELLERATION
    if kartMaxForce > kartBreakAwayForce:
        return kartBreakAwayForce - chunk2 - chunk3
    else:
        return kartMaxForce - chunk2 - chunk3
    
def max_braking(motor_speed):
    kartBreakAwayForce = Num(0.99) * GRAV_ACCELLERATION * STATICFRICTION
    chunk2 = (DRAG_COEFF * MAX_CROSSSECTIONAL_AREA * AIR_DENSITY * velocity(motor_speed) ** Num(2)) / (MASS * Num(2))
    chunk3 = Num(0.005) + (Num(1) / TIRE_PRESSURE) * (Num(0.01) + Num(0.0095) * ((Num(3.6) * velocity(motor_speed)) / Num(100)) ** Num(2)) * GRAV_ACCELLERATION
    return (Num(-1) * kartBreakAwayForce) - chunk2 - chunk3
    
    
speed = [] #motor speed
for i in range(0, 100):
    speed.append(i)
a = []
for s in speed:
    a.append(max_acceleration(s).out)
    
plt.plot(speed, a)
plt.xlabel("Motor Speed (RPM)")
plt.ylabel("Max Acceleration (N)")
plt.show()
