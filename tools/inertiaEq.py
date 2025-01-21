from NumClass import Num
import numpy as np
import time as tm

##STATIC Globals
TRANSMISSIONEFFICIENCY = Num(0.85)
TIREDIAMETER = Num(1.0) ##m
GEARINGRATIO = Num(1.0) ##tire rev / motor rev
ROLLINGRESISTANCE = Num(1.0) ##Nm
MASS = Num(110.0) ##kg
GRAVACCELLERATIONCONST = Num(1.0) ##m/s^2
TIREPRESSURE = Num(1.0) ##barr
DRAGCOEFF = Num(1.0) ##unitless
MAXCROSSSECTIONALAREA = Num(1.0) ##m^2
AIRDENSITY = Num(1.0) ##kg/m^3
POLLINGRATE = Num(0.1) ##10 x per second

##DYNAMIC Globals
MOTORSPEED = Num(5.0) ##rev/s
TORQUE = Num(1.0) ##Nm
WHEELSPEED = Num(1.0) ##rev/s ???

##PREVIOUS Globals
V_PREV = Num(0.0) ##dv
T_PREV = Num(tm.time()) ##dt in seconds

def rpm_to_motorspeed(rpm):
    rpmNum = Num(rpm)
    return (rpmNum / Num(60))

def velocity(motorspeed): ##probable inputs
    return GEARINGRATIO * motorspeed * TIREDIAMETER * Num(np.pi)

def dVdT(velocity):
    global T_PREV
    global V_PREV    

    time = Num(tm.time()) #time in seconds
    dV = velocity - V_PREV
    dT  = time - T_PREV
    #print("DT: ", dT)
    V_PREV = velocity
    T_PREV = time
    return (dV / dT) ##returns the difference in speed over small time step in seconds

def acceleration_torque(motorspeed): ##probable inputs
    c = Num(0.005) + ((Num(1) / TIREPRESSURE) * (Num(0.01) + Num(0.0095) * ((Num(3.6) * velocity(motorspeed))/ Num(100))**Num(2)))
    fR = c * MASS * GRAVACCELLERATIONCONST
    fD = Num(0.5) * DRAGCOEFF * MAXCROSSSECTIONALAREA * AIRDENSITY * (velocity(motorspeed) ** Num(2))
    fI = MASS * dVdT(velocity(motorspeed))
    return (fR + fD + fI) * velocity(motorspeed) ##watts
