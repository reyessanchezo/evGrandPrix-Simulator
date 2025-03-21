import math, pathlib
import pandas as pd
from typing import Tuple
import time as tm
import tqdm
from simple_pid import PID

STATICFRICTION = 2.480847866
NUM_LAPS = 50
POLLING_RATE = 0.1

AIR_DENSITY = 1.2  # Air density (kg/m^3)
DRAG_COEFF = 0.8  # Drag Coefficient (unitless)
GRAV_ACCELLERATION = 9.8  # Gravity acceleration constant (m/s^2)
GEARING_RATIO = 1.0  # Gearing Ratio (Tire revolutions / Motor revolutions)
MASS = 100.0  # Kart mass (kg)
MAX_CROSSSECTIONAL_AREA = 0.5  # Maximum cross-sectional area (m^2)
TIRE_DIAMETER = 0.3  # Kart tire diameter (m)
TIRE_PRESSURE = 2.0  # Tire pressure (barr)
TRANSMISSION_EFFICIENCY = 0.9  # Need clarification!!!
ROLLING_RESISTANCE = 1.0  # Nm. Need clarification!!!

MOTORTORQUE = 3.7 * 3  ##Nm
#Race detail is a section made to designate a portion of the track
#This class contains a length of the section, a turn radius (if not a race then -1), and if its a turn what the max speed is.
class RaceDetail:
    def __init__(self, length, turnRadius=-1):
        self.length = abs(length)
        self.turnRadius = turnRadius
        if turnRadius > 0:
            self.calcMaxSpeed(turnRadius)
        
    def calcMaxSpeed(self, turnRadius):
        self.maxSpeed = math.sqrt(STATICFRICTION * GRAV_ACCELLERATION * turnRadius)
        self.maxRPM = self.maxSpeed / (math.pi * TIRE_DIAMETER * GEARING_RATIO) * 60

# The class that contains information pertaining to the entire track. 
# This includes the segments of the track, total length, and positional data.
# Also tells us if the track loops.
class RaceInfo:
    def __init__(self, RaceDetails, isLoop=True):
        self.RaceDetails = RaceDetails
        self.isLoop = isLoop
        self.calcTotalLength()
        self.currPositionTotal = 0
        self.currPositionTrack = 0
    
    def calcTotalLength(self):
        #self.totalLength = sum(self.RaceDetails) #causes issues "TypeError: unsupported operand type(s) for +: 'int' and 'RaceDetail'"
        self.totalLength = 0
        for RaceDetail in self.RaceDetails:
            self.totalLength += RaceDetail.length


    def __str__(self):
        ret = []
        for raceDetail in self.RaceDetails:
            ret.append(f"Length: {raceDetail.length}, Turn Radius: {raceDetail.turnRadius}")
        ret.append(f"Total length: {self.totalLength}")
        ret.append(f"Current position total: {self.currPositionTotal}")
        ret.append(f"Current position on track: {self.currPositionTrack}")
        return "\n".join(ret)

#this function is used to translate a csv into a filled out race info class also containing race details as an array
def csv_to_raceinfo(directory: str | pathlib.Path) -> RaceInfo:
    try:
        data = pd.read_csv(directory)
    except:
        raise ImportError("Race CSV Import Error -- Try Checking The CSV Integrity")

    RaceArray = []

    try:
        for index, row in data.iterrows():
            if pd.isna(row['Turn Radius']):
                RaceArray.append(RaceDetail(length=row['Length']))
            else:
                RaceArray.append(RaceDetail(length=row['Length'], turnRadius=row['Turn Radius']))
    except:
        raise ValueError("Race CSV Reading Error -- Try Checking Race CSV Format")

    
    thisRace = RaceInfo(RaceArray)
    return thisRace

#odTranslator changes the odometer for distance traveled on the track to a segment ID for which section its in and also a current distance into the length of that section 
#Ex.: odTranslator(thisRace, 38) --> distance into track (1.86906398) and the RaceDetail object the tacometer distance is currently driving in
def odTranslator(thisRace: RaceInfo, tacometer: int | float) -> Tuple[float, RaceDetail]:
    # From Oscar: the encoder pulses are unsigned long long
    trackPos = tacometer % thisRace.totalLength
    rollingTac = 0
    trackID = 0
    segPos = 0
    while rollingTac + thisRace.RaceDetails[trackID].length < trackPos:
        rollingTac += thisRace.RaceDetails[trackID].length
        trackID += 1
    
    rollingPos = 0
    for i in range(trackID):
        rollingPos += thisRace.RaceDetails[i].length
    
    segPos = trackPos - rollingPos
    return segPos, thisRace.RaceDetails[trackID]

def rpm_to_motorspeed(rpm):
    rpmNum = rpm
    return rpmNum * 60

def velocity(motorspeed):  ##probable inputs
    return GEARING_RATIO * rpm_to_motorspeed(motorspeed) * TIRE_DIAMETER * math.pi

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
    ##chunk3 = 0.005 + (1 / TIRE_PRESSURE) * (0.01 + 0.0095 * ((3.6 * velocity(motor_speed)) / 100) ** 2) * GRAV_ACCELLERATION
    return (-1 * kartBreakAwayForce) #- chunk2 - chunk3

def brakePossible(curSegDistance, raceinfo, trackID) -> bool:
    exitrpm = raceinfo.RaceDetials[trackID + 1].maxRPM
    exitrps = rpm_to_motorspeed(exitrpm)

    y1 = velocity(rpm_to_motorspeed(readRPM()))

    y2 = velocity(exitrps)

    distance = ( (y2)**2 - (y1)**2 )/(2 * max_braking(0))

    return curSegDistance > distance
    #STILL WORK IN PROGRESS

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def RPMtoVoltage(rpm):
    return num_to_range(rpm, 0, 4500, 0.9, 4.1)


#Read from kart. Must implement later when functionality is available.
# From Oscar: Tachometer measures RPM. Odometer measures distance
def readTach():
    """READ Tachometer"""
    #some how get pulses
    #60 pulses = 1 rotation
    motorPulses = 0 #???
    motorRotations = motorPulses / 60
    distance = motorRotations * TIRE_DIAMETER * math.pi

    return distance

def readRPM():
    """READ MOTOR RPM"""
    return 0

def sendVoltage(voltage):
    """SEND A VOLTAGE"""
    pass

#######

class KartVoltage:
    def __init__(self):
        self.current = 0 #volts
    
    def update(self, power, dt):
        if power > 0:
            # PROBLEM LIES HERE
            self.current += 1 * power * dt
        return self.current
    
if __name__ == '__main__':
    thisRace = csv_to_raceinfo("raceCSV.csv")
    
    print(thisRace)
    #currSegDistance, raceSeg = odTranslator(thisRace, 38)
    print(f'Number of laps: {NUM_LAPS}')
    print(f'Total Expected time: {POLLING_RATE * len(thisRace.RaceDetails) * NUM_LAPS}, Polling Rate: {POLLING_RATE}')

    lapCur = 0

    totalStart = tm.time()
    for lap in tqdm.tqdm(range (NUM_LAPS), desc="Running Race...", ascii=True, dynamic_ncols=True):
        for detail in thisRace.RaceDetails:
            start = tm.time()
            if detail.turnRadius < 0:
                #if kart in straight away do a straight away !
                print("KART IN STRAIGHT AWAY")
                #probaby start separate thread
                #if kart is in turn do turn !
                outVoltage = None

                #this needs to be set to the actual tachometer value every loop
                tacometer_curr_distance = readTach()
                currSegDistance, raceSeg = odTranslator(thisRace, tacometer_curr_distance)
                
                #PID LOOP
                object = KartVoltage()

                currentRPM = readRPM()
                currentVoltage = RPMtoVoltage(currentRPM)

                goalRPM = 1000000
                goalVoltage = RPMtoVoltage(goalRPM)

                pid = PID(3, 0.01, 0.1, setpoint=goalVoltage)
                pid.output_limits = (0, 5)

                startTime = tm.time()
                lastTime = startTime
                
                while detail.length > currSegDistance:
                    #set pid throttle
                    currentTme = tm.time()
                    dt = currentTme - lastTime
                    power = pid(currentVoltage)
                    currentVoltage = object.update(power, dt)

                    if not brakePossible(currSegDistance, thisRace, raceSeg):
                        pid.setpoint = 0

                    outVoltage = object.current
                    print(f'Out Voltage For Straight Away: {outVoltage}')
                    sendVoltage(outVoltage)

                    lastTime = tm.time()
                    tm.sleep(abs(0.1 - (lastTime - currentTme)))

            elif detail.turnRadius > 0:
                #if kart is in turn do turn !
                print("KART IN TURN")
                outVoltage = None

                #this needs to be set to the actual tacometer value every loop
                tacometer_curr_distance = readTach()
                currSegDistance, raceSeg = odTranslator(thisRace, tacometer_curr_distance)
                
                #PID LOOP
                object = KartVoltage()

                currentRPM = readRPM()
                currentVoltage = RPMtoVoltage(currentRPM)

                goalRPM = detail.maxRPM
                goalVoltage = RPMtoVoltage(goalRPM)

                pid = PID(3, 0.01, 0.1, setpoint=goalVoltage)
                pid.output_limits = (0, 5)

                startTime = tm.time()
                lastTime = startTime
                
                while detail.length > currSegDistance:
                    #set pid throttle
                    currentTme = tm.time()
                    dt = currentTme - lastTime
                    power = pid(currentVoltage)
                    currentVoltage = object.update(power, dt)

                    print(f'Out Voltage For Turn: {currentVoltage}')
                    sendVoltage(currentVoltage)

                    lastTime = tm.time()
                    tm.sleep(abs(0.1 - (lastTime - currentTme)))

            else:
                raise ValueError("Race turn radius cannot be 0")
            
        lapCur += 1
        #print(f'Current Lap: {lapCur}')
    totalEnd = tm.time()
    print(f'Total execution time: {totalEnd - totalStart}')
