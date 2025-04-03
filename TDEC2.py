import math, pathlib
import pandas as pd
from typing import Tuple
import time as tm
from tqdm import tqdm
from simple_pid import PID

from tools import readingSerial, writeVoltage
from threading import Thread, Event
from queue import Queue, Empty
from tools import choose_port
from tools import dynoSwitch, dynoMode
import time

from logger import createNewRacelogFile, appendToLog
from datetime import datetime

#Global variables including
STATICFRICTIONSIDELOADING = 2.205155149
STATICFRICTION = 1.083261219 #2.480847866

AIR_DENSITY = 1.2  # Air density (kg/m^3)
DRAG_COEFF = 0.8  # Drag Coefficient (unitless)
GRAV_ACCELLERATION = 9.8  # Gravity acceleration constant (m/s^2)
GEARING_RATIO = 9.0 / 68.0  # Gearing Ratio (Tire revolutions / Motor revolutions)
MASS = 161.78  # Kart mass (kg)
MAX_CROSSSECTIONAL_AREA = 0.7  # Maximum cross-sectional area (m^2)
TIRE_DIAMETER = 0.254  # Kart tire diameter (m)
TIRE_PRESSURE = 1.0  # Tire pressure (barr)
TRANSMISSION_EFFICIENCY = 0.9  # not a perfect number

MOTORTORQUE = 5.5  ##Nm 

NUM_LAPS = 3
POLLING_RATE = 0.1

G_TACH = 0
G_TACH_START = 0
G_RPM = 0
G_V = 0
TORQS = 0

class RaceSeg:
    def __init__(self, length, turnRadius=-1):
        self.length = abs(length)
        self.turnRadius = turnRadius
        if turnRadius > 0:
            self.calcMaxSpeed(turnRadius)
        else:
            self.maxSpeed = 4500 * (1 / 60) * (1 / (TIRE_DIAMETER * math.pi))
            self.maxRPM = 4500
        
    def calcMaxSpeed(self, turnRadius):
        self.maxSpeed = math.sqrt(STATICFRICTIONSIDELOADING * GRAV_ACCELLERATION * turnRadius)
        self.maxRPM = self.maxSpeed / (math.pi * TIRE_DIAMETER * GEARING_RATIO) * 60

class RaceInfo:
    def __init__(self, RaceArray, isLoop=True):
        self.RaceArray = RaceArray
        self.isLoop = isLoop
        self.calcTotalLength()
        self.currPositionTotal = 0
        self.currPositionTrack = 0
    
    def calcTotalLength(self):
        #self.totalLength = sum(self.RaceSeg) #causes issues "TypeError: unsupported operand type(s) for +: 'int' and 'RaceDetail'"
        self.totalLength = 0
        for RaceSeg in self.RaceArray:
            self.totalLength += RaceSeg.length


    def __str__(self):
        ret = []
        for RaceSeg in self.RaceArray:
            ret.append(f"Length: {RaceSeg.length}, Turn Radius: {RaceSeg.turnRadius}")
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
                RaceArray.append(RaceSeg(length=row['Length']))
            else:
                RaceArray.append(RaceSeg(length=row['Length'], turnRadius=row['Turn Radius']))
    except:
        raise ValueError("Race CSV Reading Error -- Try Checking Race CSV Format")

    
    thisRace = RaceInfo(RaceArray)
    return thisRace

#Read from kart. Must implement later when functionality is available.
# From Oscar: Tachometer measures RPM. Odometer measures distance
def readTach():
    """READ Tachometer"""
    global G_TACH
    return G_TACH * (1 / 60) * (TIRE_DIAMETER * math.pi * GEARING_RATIO)

#odTranslator changes the odometer for distance traveled on the track to a segment ID for which section its in and also a current distance into the length of that section 
#Ex.: odTranslator(thisRace, 38) --> distance into track (1.86906398) and the RaceDetail object the tacometer distance is currently driving in
def odTranslator(race: RaceInfo, tacometer: int | float) -> Tuple[float, RaceSeg]:
    # From Oscar: the encoder pulses are unsigned long long
    trackPos = tacometer % race.totalLength
    rollingTac = 0
    trackID = 0
    segPos = 0
    while rollingTac + race.RaceArray[trackID].length < trackPos:
        rollingTac += race.RaceArray[trackID].length
        trackID += 1
    
    rollingPos = 0
    for i in range(trackID):
        rollingPos += race.RaceArray[i].length
    
    segPos = trackPos - rollingPos
    return segPos, trackID

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
    if trackID == len(raceInfo.RaceArray):
        print("WARNING IN BRAKE POSSIBLE: TRACKID IS OUT OF RANGE")
    exitrpm = raceinfo.RaceArray[trackID + 1].maxRPM
    exitrps = rpm_to_motorspeed(exitrpm)

    y1 = velocity(rpm_to_motorspeed(readRPM()))

    y2 = velocity(exitrps)

    distance = ( (y2)**2 - (y1)**2 )/(2 * max_braking(0))

    return curSegDistance > distance

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def RPMtoVoltage(rpm):
    return num_to_range(rpm, 0, 4500, 0.0, 3.3)

def readRPM():
    """READ MOTOR RPM"""
    global G_RPM
    return G_RPM

def clamp(val, minVal, maxVal):
    return max(minVal, min(val, maxVal))

def sendVoltage(voltage, vq):
    """SEND A VOLTAGE"""
    global G_V
    
    # For TDEC2, we are keeping below 2V due a concern over ratings that needs to be checked.

    voltage = clamp(voltage, 0, 1)
    
    # Printing instructions for the driver until we attach a throttle.
    #print(f"THROTTLE: {voltage * 20}%")
    vq.put(voltage)
    return

finished = False
def update_globals():
    global finished
    global G_RPM
    global G_TACH
    global G_TACH_START
    global TORQS
    while not finished:
        try:
            item = receiveQueue.get()
        except Empty:
            continue
        except KeyboardInterrupt:
            print("Ending program.")
            break
        else:
            #print(f"RPM: {item[0]}\tTotal Pulses: {item[4]}\tV: {item[3]}")
            try:
                if (G_TACH_START == 0):
                    G_TACH_START = float(item[1])
                G_RPM = float(item[0])
                G_TACH = float(item[1]) - G_TACH_START
                TORQS = float(item[2])
                #print(f'ARDUINO: (RPM: {G_RPM}, TACH: {G_TACH})')
            except Exception as e:
                print("By some miracle this worked but it shoudln't have")
            receiveQueue.task_done()

def tqdmDistanceConverter(currDistance, totalDistance) -> int:
    return int(math.ceil(num_to_range(currDistance, 0, totalDistance, 0, 100)))

def tqdmDistanceLoop(raceLength) -> None:
    global NUM_LAPS
    timeoutHours = 5 # in hours
    timeoutSeconds = timeoutHours * 60 * 60
    
    odometer = readTach()
    odTrack = odometer % raceLength
    lapNum = 1
    
    timstart = tm.time()
    curTime = timstart
    
    pbarLapDistance = tqdm(range(100), 
                           desc="Progress in lap", 
                           ascii=' █', 
                           dynamic_ncols=True, 
                           bar_format='{desc:<25} {percentage:3.0f}%|\033[34m{bar}\033[0m|')  # Blue bar
    pbarTotalDistance = tqdm(range(100), 
                            desc="Progress in race", 
                            ascii=' █', 
                            dynamic_ncols=True, 
                            bar_format='{desc:<25} {percentage:3.0f}%|\033[32m{bar}\033[0m|')  # Green bar
    
    while odometer < raceLength * NUM_LAPS and (curTime - timstart) < (timeoutSeconds):
        pbarLapDistance.n = tqdmDistanceConverter(odTrack, raceLength)
        pbarTotalDistance.n = tqdmDistanceConverter(odometer, (raceLength * NUM_LAPS))
        pbarLapDistance.set_description(f"Progress in lap {lapNum}")
        pbarTotalDistance.set_description(f"Progress in race")
        pbarLapDistance.refresh()
        pbarTotalDistance.refresh()
        
        odometer = readTach()
        odTrack = odometer % raceLength
        lapNum = int(odometer // raceLength) + 1
        
        curTime = tm.time()
        time.sleep(0.1)

def ReadTorques() -> float:
    return TORQS

def ReadRPM() -> int:
    return G_RPM

def ReadVoltage() -> float:
    return G_V

class KartVoltage:
    def __init__(self):
        self.current = 0 #volts
    
    def update(self, power, dt):
        if power > 0:
            self.current += 1 * power * dt
        return self.current

if __name__ == '__main__':
    raceInfo = csv_to_raceinfo("PurdueevGrandPrixTrackCSV.csv")
    
    createNewRacelogFile()
    
    print(raceInfo)
    print(f'Number of laps: {NUM_LAPS}')
    print(f'Total Expected time: {POLLING_RATE * len(raceInfo.RaceArray) * NUM_LAPS}, Polling Rate: {POLLING_RATE}')

    sendQueue = Queue()
    receiveQueue = Queue()
    dynoQueue = Queue()
    sp = choose_port()

    updateThread = Thread(
        target=update_globals,
        args=(),
        daemon=True
    )

    voltageThread = Thread(
        target=writeVoltage,
        args=(sp, sendQueue, receiveQueue),
        daemon=True
    )

    dynoThread = Thread(
        target=dynoSwitch,
        args=(dynoQueue,),
        daemon=True
    )
    
    tqdmDistanceThread = Thread(
        target=tqdmDistanceLoop,
        args=(raceInfo.totalLength),
        daemon=False #it does not work if it is a daemon, but it naturally stops when the program ends. unsure if this is a problem but i added a timeout to the function
    )

    updateThread.start()
    voltageThread.start()
    tqdmDistanceThread.start()
    # This was added to make sure the Arduino is on during testing. May not be required anymore.
    print("Please wait a moment...")
    time.sleep(2)

    
    curLap = 0
    raceStart = tm.time()

    odTestMode = 0
    if odTestMode == 1:
        for i in range(1000):
            tacometer_curr_distance = readTach()
            currSegDistance, trackID = odTranslator(raceInfo, tacometer_curr_distance)
            print(f'Race segment: {trackID}, Distance into segment: {currSegDistance}')
    
    #used for checking lap time
    lapStart = tm.time()
    lapEnd = lapStart
    lapTime = 0
    
    for lap in range(NUM_LAPS):
        lapStart = tm.time()
        for seg in raceInfo.RaceArray:
            segstart = tm.time()
            if seg.turnRadius < 0:
                #straight away
                tqdm.write("Kart in straight away")
                
                outVoltage = None

                tacometer_cur_distance = readTach()
                curSegDistance, origionalTrackID = odTranslator(raceInfo, tacometer_cur_distance)
                currentRPM = readRPM()
                currentVoltage = RPMtoVoltage(currentRPM)
                tqdm.write(f'Race segment: {origionalTrackID}, Distance into segment: {curSegDistance}')

                # tell dyno to run normal physics
                dynoMode(1, dynoQueue)

                object = KartVoltage()
                goalRPM = 1000000
                goalVoltage = RPMtoVoltage(goalRPM)
                pid = PID(1, 0.01, 0.1, setpoint=goalVoltage)
                pid.output_limits = (0, 3.3)

                startTime = tm.time()
                lastTime = startTime
                brakePossibleBool = True
                trackID = origionalTrackID
                tqdm.write(f'origional track id: {origionalTrackID}')
                while seg.length > curSegDistance and trackID == origionalTrackID:
                    tacometer_cur_distance = readTach()
                    curSegDistance, trackID = odTranslator(raceInfo, tacometer_cur_distance)
                    #print(f'(FULL THROTTLE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                    
                    if trackID != origionalTrackID:
                        break

                    currentTme = tm.time()
                    dt = currentTme - lastTime
                    power = pid(currentVoltage)
                    currentVoltage = object.update(power, dt)
                    
                    if brakePossibleBool is True:
                        tqdm.write(f'(FULL THROTTLE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                        
                        #logging stuff
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        appendToLog(f"Timestamp: {timestamp}, Race instructions: Straight (Full Throttle), Torque: {TORQS}, RPM: {G_RPM}, Voltage: {outVoltage}, Power: {G_RPM * TORQS}, Last Lap Time:{lapTime}, Current Lap: {curLap}, Total Laps: {NUM_LAPS}, Last Segment Time: {segtime}, Current Segment: {trackID}, Distance into Segment: {curSegDistance}, Odometer: {G_TACH}, Brake Possible: {brakePossibleBool}, PID Setpoint: {pid.setpoint}")
                    elif brakePossibleBool is not True:
                        tqdm.write(f'(FULL BRAKE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                        
                        #logging stuff
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        appendToLog(f"Timestamp: {timestamp}, Race instructions: Straight (Full Brake), Torque: {TORQS}, RPM: {G_RPM}, Voltage: {outVoltage}, Power: {G_RPM * TORQS}, Last Lap Time:{lapTime}, Current Lap: {curLap}, Total Laps: {NUM_LAPS}, Last Segment Time: {segtime}, Current Segment: {trackID}, Distance into Segment: {curSegDistance}, Odometer: {G_TACH}, Brake Possible: {brakePossibleBool}, PID Setpoint: {pid.setpoint}")
                    if not brakePossible(curSegDistance, raceInfo, trackID):
                        pid.setpoint = 0
                        brakePossibleBool = False

                        # tell the dyno to run full brakes
                        dynoMode(0, dynoQueue)

                    outVoltage = object.current
                    #print(f'Out Voltage For Straight Away: {outVoltage}')
                    sendVoltage(outVoltage, sendQueue)

                    lastTime = tm.time()
                    tm.sleep(abs(POLLING_RATE - (lastTime - currentTme)))

            elif seg.turnRadius > 0:
                tqdm.write(f'Kart is in turn')
                
                outVoltage = None

                tacometer_cur_distance = readTach()
                curSegDistance, origionalTrackID = odTranslator(raceInfo, tacometer_cur_distance)
                currentRPM = readRPM()
                currentVoltage = RPMtoVoltage(currentRPM)
                tqdm.write(f'Race segment: {origionalTrackID}, Distance into segment: {curSegDistance}')

                # tell dyno to run normal physics
                dynoMode(1, dynoQueue)

                object = KartVoltage()
                goalRPM = seg.maxRPM
                goalVoltage = RPMtoVoltage(goalRPM)
                pid = PID(1, 0.01, 0.1, setpoint=goalVoltage)
                pid.output_limits = (0, 3.3)

                startTime = tm.time()
                lastTime = startTime

                trackID = origionalTrackID
                while seg.length > curSegDistance and trackID == origionalTrackID:
                    tacometer_cur_distance = readTach()
                    curSegDistance, trackID = odTranslator(raceInfo, tacometer_cur_distance)
                    #print(f'THROTTLE: {currentVoltage * 20}%, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                    tqdm.write(f'THROTTLE: {num_to_range(currentVoltage, 0, 3.3, 0, 100)}%, Race instructions: Turn, Race segment: {trackID}, Distance into segment: {curSegDistance}, Expected RPM: {seg.maxRPM}')
                    
                    #logging stuff
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    appendToLog(f"Timestamp: {timestamp}, Race instructions: Turn, Torque: {TORQS}, RPM: {G_RPM}, Voltage: {outVoltage}, Power: {G_RPM * TORQS}, Last Lap Time:{lapTime}, Current Lap: {curLap}, Total Laps: {NUM_LAPS}, Last Segment Time: {segtime}, Current Segment: {trackID}, Distance into Segment: {curSegDistance}, Odometer: {G_TACH}, Brake Possible: {brakePossibleBool}, PID Setpoint: {pid.setpoint}, Expected RPM: {seg.maxRPM}")
                    
                    if trackID != origionalTrackID:
                        break

                    currentTme = tm.time()
                    dt = currentTme - lastTime
                    power = pid(currentVoltage)
                    currentVoltage = object.update(power, dt)

                    #print(f'Out Voltage For Turn: {currentVoltage}')
                    #print(f'Current position on turn: {TACTEST}')
                    sendVoltage(currentVoltage, sendQueue)

                    lastTime = tm.time()
                    tm.sleep(abs(POLLING_RATE - (lastTime - currentTme)))
            else:
                raise ValueError("Race turn radius cannot be 0")
            segend = tm.time()
            segtime = segend - segstart
        lapEnd = tm.time()
        lapTime = lapEnd - lapStart
        curLap += 1
        tqdm.write(f'Current lap: {curLap}')

    raceEnd = tm.time()
    print(f'Total execution time: {raceEnd - raceStart}')

    #close threads
    finished = True
