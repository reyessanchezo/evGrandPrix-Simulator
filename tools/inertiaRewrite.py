import numpy as np
from NumClass import Num

##STATIC Globals  
TRANSMISSIONEFFICIENCY = Num(0.9)
TIREDIAMETER = Num(0.8) ##m
GEARINGRATIO = Num(1.0) ##tire rev / motor rev
ROLLINGRESISTANCE = Num(1.0) ##Nm
MASS = Num(100.0) ##kg
GRAVACCELLERATIONCONST = Num(-9.8) ##m/s^2
TIREPRESSURE = Num(2.0) ##barr
DRAGCOEFF = Num(0.8) ##unitless
MAXCROSSSECTIONALAREA = Num(0.5) ##m^2
AIRDENSITY = Num(1.2) ##kg/m^3

##DYNAMIC Globals
MOTORSPEED = Num(1.0) ##rev/s ???
TORQUE = Num(1.0) ##Nm
VELOCITY = Num(20.0) ##m/s
WHEELSPEED = Num(1.0) ##rev/s ???
TIME = Num(110.0) ##s??

##PREVIOUS Globals
V_PREV = Num(18.0) ##dv
T_PREV = Num(109.0) ##dt

##acceleration over small time step - used regulary
def dVdT(): 
    dV = VELOCITY - V_PREV
    dT  = TIME - T_PREV
    return (dV / dT) ##returns the difference in speed over small time step

##Aerodynamic Drag Force
def dragForce():
    return ((Num(1) / Num(2)) * DRAGCOEFF * MAXCROSSSECTIONALAREA * AIRDENSITY * (VELOCITY ** Num(2)))

##Inertia/Acceleration Force
def intertiaForce():
    return (MASS * dVdT())

##Rolling Resistance Force
def rollingResistanceForce():
    c = Num(0.005) + (Num(1) / TIREPRESSURE) * (Num(0.01) + Num(0.0095) * ((Num(3.6) * VELOCITY)/ Num(100))**Num(2))
    return (c * MASS * GRAVACCELLERATIONCONST)

##uses current globals to calc acceleration and outputs torque
def accelerationTorque(): ##probable inputs
    a = dragForce() + intertiaForce() + rollingResistanceForce()
    T = a * TIREDIAMETER / (MOTORSPEED * WHEELSPEED) / Num(2) / TRANSMISSIONEFFICIENCY
    return T

##i dont know what this is im returning the difference in speed over small dt ??
def coasting(): ##im not sure about this one, it may be wrong
    dv = rollingResistanceForce() + dragForce() * (TIME - T_PREV) / MASS
    return dv

##uses current globals to calc and output torque
def constVelocityTorque():
    a = rollingResistanceForce() + dragForce()
    T = a * TIREDIAMETER / (MOTORSPEED * WHEELSPEED) / Num(2) / TRANSMISSIONEFFICIENCY
    return T

##proof of concept, all the functions work it seems like since im using a class, if you want to export the value of a Num object, you have to use the .out attribute where it is stored.

