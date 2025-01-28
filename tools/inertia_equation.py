from NumClass import Num
import numpy as np
import time as tm

##STATIC Globals
TRANSMISSION_EFFICIENCY = Num(0.9)
TIRE_DIAMETER = Num(0.3)  ##m
GEARING_RATIO = Num(1.0)  ##tire rev / motor rev
ROLLING_RESISTANCE = Num(1.0)  ##Nm
MASS = Num(100.0)  ##kg
GRAV_ACCELLERATION = Num(9.8)  ##m/s^2
TIRE_PRESSURE = Num(2.0)  ##barr
DRAG_COEFF = Num(0.8)  ##unitless
MAX_CROSSSECTIONAL_AREA = Num(0.5)  ##m^2
AIR_DENSITY = Num(1.2)  ##kg/m^3

##DYNAMIC Globals
MOTOR_SPEED = Num(21.220659078940496)  ##rev/s for vel = 20m/s

##PREVIOUS Globals
V_PREV = Num(0.0)  ##dv
T_PREV = Num(tm.time())  ##dt in seconds


def rpm_to_motorspeed(rpm):
    rpmNum = Num(rpm)
    return rpmNum / Num(60)


def velocity(motorspeed):  ##probable inputs
    return GEARING_RATIO * motorspeed * TIRE_DIAMETER * Num(np.pi)


def dVdT(velocity):
    global T_PREV
    global V_PREV

    time = Num(tm.time())  # time in seconds
    dV = velocity - V_PREV
    dT = time - T_PREV
    V_PREV = velocity
    T_PREV = time
    return dV / dT  ##returns the difference in speed over small time step in seconds


def acceleration_torque(motorspeed):  ##probable inputs
    c = Num(0.005) + (
        (Num(1) / TIRE_PRESSURE)
        * (
            Num(0.01)
            + Num(0.0095) * ((Num(3.6) * velocity(motorspeed)) / Num(100)) ** Num(2)
        )
    )
    fR = c * MASS * GRAV_ACCELLERATION
    fD = (
        Num(0.5)
        * DRAG_COEFF
        * MAX_CROSSSECTIONAL_AREA
        * AIR_DENSITY
        * (velocity(motorspeed) ** Num(2))
    )
    fI = MASS * dVdT(velocity(motorspeed))
    return fR + fD + fI * velocity(motorspeed) ##watts
