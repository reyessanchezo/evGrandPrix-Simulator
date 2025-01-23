from NumClass import Num
import numpy as np
#import inertiaEq
import unittest
import math

##STATIC Globals
TRANSMISSIONEFFICIENCY = Num(0.9)
TIREDIAMETER = Num(0.3) ##m
GEARINGRATIO = Num(1.0) ##tire rev / motor rev
ROLLINGRESISTANCE = Num(1.0) ##Nm
MASS = Num(100.0) ##kg
GRAVACCELLERATIONCONST = Num(9.8) ##m/s^2
TIREPRESSURE = Num(2.0) ##barr
DRAGCOEFF = Num(0.8) ##unitless
MAXCROSSSECTIONALAREA = Num(0.5) ##m^2
AIRDENSITY = Num(1.2) ##kg/m^3



def round_down_6_decimals(number):
    factor = 10**6  # Shift decimal point 6 places
    return math.floor(number * factor) / factor

def v_mo_conversion(velocity):
    s = Num(1)/((GEARINGRATIO * TIREDIAMETER * np.pi) / velocity) 
    return s

def rpm_to_motorspeed(rpm):
    rpmNum = Num(rpm)
    return (rpmNum / Num(60))

def velocity(motorspeed): ##probable inputs
    return GEARINGRATIO * motorspeed * TIREDIAMETER * Num(np.pi)

def dVdT(velocity):
    return 0 #(dV / dT) ##non important for tests

def acceleration_torque(motorspeed): ##probable inputs
    c = Num(0.005) + ((Num(1) / TIREPRESSURE) * (Num(0.01) + Num(0.0095) * ((Num(3.6) * velocity(motorspeed))/ Num(100))**Num(2)))
    fR = c * MASS * GRAVACCELLERATIONCONST
    fD = Num(0.5) * DRAGCOEFF * MAXCROSSSECTIONALAREA * AIRDENSITY * (velocity(motorspeed) ** Num(2))
    fI = MASS * dVdT(velocity(motorspeed))
    return (fR + fD + fI) #* velocity(motorspeed) ##watts

print("vel to mtspd: ", v_mo_conversion(Num(10)))
#print("Accelleration torque: ", acceleration_torque(v_mo_conversion('hello')))

class TestAccellerationTorqueFunc(unittest.TestCase):
    def test_accelleration_torqueAt20(self):
        inputVelocity = Num(20)
        expectedOutput = Num(108.213152).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueAt10(self):
        inputVelocity = Num(10)
        expectedOutput = Num(34.403288).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueAt1(self):
        inputVelocity = Num(1)
        expectedOutput = Num(10.046032).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueAtNeg1(self):
        inputVelocity = Num(-1)
        expectedOutput = Num(10.046032).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueAtNeg10(self):
        inputVelocity = Num(-10)
        expectedOutput = Num(34.403288).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueAtNeg20(self):
        inputVelocity = Num(-20)
        expectedOutput = Num(108.213152).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)

    def test_accelleration_torqueWONumClass(self):
        inputVelocity = 20
        expectedOutput = Num(108.213152).out
        velocity = acceleration_torque(v_mo_conversion(inputVelocity)).out
        velocitySm = round_down_6_decimals(velocity)
        self.assertEqual(velocitySm, expectedOutput)
    

    

unittest.main()