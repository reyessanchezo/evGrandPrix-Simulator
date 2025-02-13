import numpy as np
from NumClass import Num

##STATIC Globals
TRANSMISSIONEFFICIENCY = Num(0.85)
TIREDIAMETER = Num(1.0)  ##m
GEARINGRATIO = Num(1.0)  ##tire rev / motor rev
ROLLINGRESISTANCE = Num(1.0)  ##Nm
MASS = Num(110.0)  ##kg
GRAVACCELLERATIONCONST = Num(1.0)  ##m/s^2
TIREPRESSURE = Num(1.0)  ##barr
DRAGCOEFF = Num(1.0)  ##unitless
MAXCROSSSECTIONALAREA = Num(1.0)  ##m^2
AIRDENSITY = Num(1.0)  ##kg/m^3

##DYNAMIC Globals
MOTORSPEED = Num(1.0)  ##rev/s
TORQUE = Num(1.0)  ##Nm
VELOCITY = Num(10.0)  ##m/s
WHEELSPEED = Num(1.0)  ##rev/s ???
TIME = Num(110.0)  ##s??

##PREVIOUS Globals
V_PREV = Num(12.0)  ##dv
T_PREV = Num(109.0)  ##dt


##acceleration over small time step - used regulary
def dVdT():
    dV = VELOCITY - V_PREV
    dT = TIME - T_PREV
    return dV / dT  ##returns the difference in speed over small time step


##Aerodynamic Drag Force
def drag_force():
    return (
        (Num(1) / Num(2))
        * DRAGCOEFF
        * MAXCROSSSECTIONALAREA
        * AIRDENSITY
        * (VELOCITY ** Num(2))
    )


##Inertia/Acceleration Force
def intertia_force():
    return MASS * dVdT()


##Rolling Resistance Force
def rolling_resistance_force():
    c = Num(0.005) + (Num(1) / TIREPRESSURE) * (
        Num(0.01) + Num(0.0095) * ((Num(3.6) * VELOCITY) / Num(100)) ** Num(2)
    )
    return c * MASS * GRAVACCELLERATIONCONST


##uses current globals to calc acceleration and outputs torque
def acceleration_torque():  ##probable inputs
    a = drag_force() + intertia_force() + rolling_resistance_force()
    T = a * TIREDIAMETER / (MOTORSPEED * WHEELSPEED) / Num(2) / TRANSMISSIONEFFICIENCY
    return T


##i dont know what this is im returning the difference in speed over small dt ??
def coasting():  ##im not sure about this one, it may be wrong
    dv = rolling_resistance_force() + drag_force() * (TIME - T_PREV) / MASS
    return dv


##uses current globals to calc and output torque
def const_velocity_torque():
    a = rolling_resistance_force() + drag_force()
    T = a * TIREDIAMETER / (MOTORSPEED * WHEELSPEED) / Num(2) / TRANSMISSIONEFFICIENCY
    return T


##proof of concept, all the functions work it seems like since im using a class, if you want to export the value of a Num object, you have to use the .out attribute where it is stored.

if __name__ == "__main__":
    e = np.add(3.0, 3)
    b = Num(3.0) + e + 5
    print("b: ", b.out)

    print("intertiaForce: ", intertia_force().out)
    print("rollingResistanceForce: ", rolling_resistance_force().out)
    print("dragForce: ", drag_force().out)
    print("accelerationTorque: ", acceleration_torque().out)
    print("coasting: ", coasting().out)
    print("constVelocityTorque: ", const_velocity_torque().out)
