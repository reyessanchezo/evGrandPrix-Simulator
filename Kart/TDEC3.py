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

#Global variables for kart physics
STATICFRICTIONSIDELOADING = 1.102577574
STATICFRICTION = 0.5416306095

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
MAX_MOTOR_RPM = 5500 #rpm

#race parameters
NUM_LAPS = 2
POLLING_RATE = 0.03

#torque sensor variables
G_TACH = 0
G_TACH_START = 0
G_RPM = 0
G_V = 0
TORQS = 0

#segemnt of the race either straight or turn, inlcudes details for the segment
class RaceSeg:
    def __init__(self, length, turnRadius=-1):
        self.length = abs(length)
        self.turnRadius = turnRadius
        if turnRadius > 0:
            self.calcMaxSpeed(turnRadius)
        else:
            self.maxSpeed = MAX_MOTOR_RPM * (1 / 60) * (1 / (TIRE_DIAMETER * math.pi))
            self.maxRPM = MAX_MOTOR_RPM
        
    """TODO: Check if this math is correct with Jackson's math"""
    def calcMaxSpeed(self, turnRadius):
        self.maxSpeed = math.sqrt(STATICFRICTIONSIDELOADING * GRAV_ACCELLERATION * turnRadius)
        self.maxRPM = self.maxSpeed / (math.pi * TIRE_DIAMETER * GEARING_RATIO) * 60

#contains all the race segments and information about the race
class RaceInfo:
    def __init__(self, RaceArray, isLoop=True):
        self.RaceArray = RaceArray
        self.isLoop = True
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
"""TODO: Check if this should be 1/60 or if it involves something else"""
def readTach():
    """READ Tachometer"""
    global G_TACH
    return G_TACH * (1 / 60) * (TIRE_DIAMETER * math.pi * GEARING_RATIO)

#tachTranslator changes the tachometer for distance traveled on the track to a segment ID for which section its in and also a current distance into the length of that section 
#Ex.: tachTranslator(thisRace, 38) --> distance into track (1.86906398) and the RaceDetail object the tacometer distance is currently driving in
def tachTranslator(race: RaceInfo, tacometer: int | float) -> Tuple[float, RaceSeg]:
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

"""TODO: Check if this math is correct with Jackson's math"""
#used for finding the maximum acceleration the kart could do at given motorspeed
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

"""TODO: Check if this math is correct with Jackson's math"""
#used for finding the maximum braking the kart could do at given motorspeed
def max_braking(motor_speed):
    kartBreakAwayForce = 0.99 * GRAV_ACCELLERATION * STATICFRICTION
    ##chunk3 = 0.005 + (1 / TIRE_PRESSURE) * (0.01 + 0.0095 * ((3.6 * velocity(motor_speed)) / 100) ** 2) * GRAV_ACCELLERATION
    return (-1 * kartBreakAwayForce) #- chunk2 - chunk3

"""TODO: Check if this math is correct with Jackson's math"""
#used to find if the kart can brake at the current distance into a straight segment of the track
def brakePossible(curSegDistance, raceinfo, trackID) -> bool:
    if trackID == len(raceInfo.RaceArray):
        print("WARNING IN BRAKE POSSIBLE: TRACKID IS OUT OF RANGE")
    exitrpm = raceinfo.RaceArray[trackID + 1].maxRPM
    exitrps = rpm_to_motorspeed(exitrpm)

    y1 = velocity(rpm_to_motorspeed(readRPM()))

    y2 = velocity(exitrps)

    distance = ( (y2)**2 - (y1)**2 )/(2 * max_braking(0))

    return curSegDistance > distance

#one of the most useful functions ive ever seen. Very nice, good soup.
def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

"""TODO: can we assuem this is correct or does this need to be changed"""
#UPDATE THIS SHIT DONT WORK
"""
def RPMtoVoltage(rpm):
    return num_to_range(rpm, 0, MAX_MOTOR_RPM, 0.0, MAX_VOLTAGE)
"""

def readRPM():
    """READ MOTOR RPM"""
    global G_RPM
    return G_RPM

def clamp(val, minVal, maxVal):
    return max(minVal, min(val, maxVal))

#used to send the voltage to the arduino from this program
def sendRPM(rpm, rq):
    """SEND A VOLTAGE"""
    
    # THIS WORKING ?? MAYBE
    rpm = clamp(rpm, 0, MAX_MOTOR_RPM)
    
    out = round(num_to_range(rpm, 0, MAX_MOTOR_RPM, 0, 255))
    
    rq.put(out)
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

#used to make tqdm progress bar for the distance traveled on the track. When inside main, it looks bad and is not precise.
def tqdmDistanceLoop(raceLength) -> None:
    global NUM_LAPS
    timeoutHours = 5 # number of hours before the function times itself out
    timeoutSeconds = timeoutHours * 60 * 60
    
    tachometer = readTach()
    odTrack = tachometer % raceLength
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
    
    while tachometer < raceLength * NUM_LAPS and (curTime - timstart) < (timeoutSeconds):
        pbarLapDistance.n = tqdmDistanceConverter(odTrack, raceLength)
        pbarTotalDistance.n = tqdmDistanceConverter(tachometer, (raceLength * NUM_LAPS))
        pbarLapDistance.set_description(f"Progress in lap {lapNum}")
        pbarTotalDistance.set_description(f"Progress in race")
        pbarLapDistance.refresh()
        pbarTotalDistance.refresh()
        
        tachometer = readTach()
        odTrack = tachometer % raceLength
        lapNum = int(tachometer // raceLength) + 1
        
        curTime = tm.time()
        time.sleep(0.1)

"""TODO: Double check the speed math"""
def RPMtoMPH(rpm):
    rpm = rpm * GEARING_RATIO
    speed = rpm * (math.pi * TIRE_DIAMETER) / 60
    return speed * 2.237 

def RPMtoKPH(rpm):
    rpm = rpm * GEARING_RATIO
    speed = rpm * (math.pi * TIRE_DIAMETER) / 60
    return speed * 3.6
    
def ReadTorques() -> float:
    return TORQS

def ReadRPM() -> int:
    return G_RPM

def ReadVoltage() -> float:
    return G_V ##possibly not accurate

#a class used in the voltage PID loop
class KartRPM:
    def __init__(self):
        self.current = 0 #volts
    
    def update(self, power, dt):
        if power > 0:
            self.current += 1 * power * dt
        return self.current

if __name__ == '__main__':
    #translates csv file into our custom classes
    raceInfo = csv_to_raceinfo("tdec_track.csv")
    
    #initiates a new race log file
    createNewRacelogFile()
    appendToLog(f"Timestamp, Time, Race instructions, mph, kph, Torque, Voltage, Power, Last Lap Time, Current Lap, Total Laps, Last Segment Time, Current Segment, Distance into Segment, Tachometer, Brake Possible, PID Setpoint, Current RPM, Expected RPM")
    
    
    
    print(raceInfo)
    print(f'Number of laps: {NUM_LAPS}')
    print(f'Total Expected time: {POLLING_RATE * len(raceInfo.RaceArray) * NUM_LAPS}, Polling Rate: {POLLING_RATE}')

    #creates queues for the arduino to send and receive data
    sendQueue = Queue()
    receiveQueue = Queue()
    dynoQueue = Queue()
    sp = choose_port()

    #creates threads for the arduino to send and receive data
    updateThread = Thread(
        target=update_globals,
        args=(),
        daemon=True
    )

    #creates threads for the arduino to send and receive voltage data
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
    
    #used to initiate tqdm progress bar
    tqdmDistanceThread = Thread(
        target=tqdmDistanceLoop,
        args=(float(raceInfo.totalLength), ),
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

    #used for testing the tachometer
    odTestMode = 0
    if odTestMode == 1:
        for i in range(1000):
            tacometer_curr_distance = readTach()
            currSegDistance, trackID = tachTranslator(raceInfo, tacometer_curr_distance)
            print(f'Race segment: {trackID}, Distance into segment: {currSegDistance}')
    
    #used for checking lap time
    lapStart = tm.time()
    lapEnd = lapStart
    lapTime = 0
    
    #main loop for the race where the kart drives around the track a set number of laps
    for lap in range(NUM_LAPS):
        lapStart = tm.time()
        
        #loop for each segment of the track
        for seg in raceInfo.RaceArray:
            segstart = tm.time()
            if seg.turnRadius < 0:
                #straight away
                tqdm.write("Kart in straightaway")
                
                #outVoltage = None
                straight_speed = MAX_MOTOR_RPM

                tacometer_cur_distance = readTach()
                curSegDistance, origionalTrackID = tachTranslator(raceInfo, tacometer_cur_distance)
                currentRPM = readRPM()
                tqdm.write(f'Race segment: {origionalTrackID}, Distance into segment: {curSegDistance}')

                # tell dyno to run normal physics
                dynoMode(0, dynoQueue)

                #used to keep track of time
                startTime = tm.time()
                lastTime = startTime
                
                
                #used as an initial condition for the brake possible function
                brakePossibleBool = True
                
                #used to keep track of the track ID
                trackID = origionalTrackID
                tqdm.write(f'origional track id: {origionalTrackID}')
                
                #runs a loop until the kart leaves the segment
                while seg.length > curSegDistance and trackID == origionalTrackID:
                    tacometer_cur_distance = readTach()
                    curSegDistance, trackID = tachTranslator(raceInfo, tacometer_cur_distance)
                    #print(f'(FULL THROTTLE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                    
                    if trackID != origionalTrackID:
                        break

                    currentTme = tm.time()
                    segtime = currentTme
                    
                    dt = currentTme - lastTime
                    
                    #checks for if we can brake down to where we need to be if not, set the PID setpoint to 0 and holler about it
                    if not brakePossible(curSegDistance, raceInfo, trackID):
                        """TODO: If we cant use PID for straight away, then how can we guarantee that it will reach next segment?"""
                        brakePossibleBool = False
                        
                        # stop the throttle
                        straight_speed = 0
                        # tell the dyno to run full brakes
                        dynoMode(1, dynoQueue)
                    
                    #if we could brake down to where we need to be then we do not need to brake
                    if brakePossibleBool is True:
                        mph = RPMtoMPH(readRPM())
                        kph = RPMtoKPH(readRPM())
                        tqdm.write(f'(FULL THROTTLE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {round(curSegDistance, 3)}, Speed: {round(mph, 3)} mph, {round(kph, 3)} kph')
                        
                        straight_speed = MAX_MOTOR_RPM
                        dynoMode(0, dynoQueue)

                        #logging stuff
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tach = readTach()
                        rpm = readRPM()
                        appendToLog(f'{timestamp}, {time.time()}, Straight(Full Throttle), {mph}, {kph}, {TORQS}, {outVoltage}, {readRPM() * TORQS}, {lapTime}, {curLap}, {NUM_LAPS}, {segtime}, {trackID}, {curSegDistance}, {tach}, {brakePossibleBool}, {pid.setpoint}, {rpm}, --')
                        #tqdm.write(f'{timestamp}, {time.time()}, Straight(Full Throttle), {mph}, {kph}, {TORQS}, {outVoltage}, {readRPM() * TORQS}, {lapTime}, {curLap}, {NUM_LAPS}, {segtime}, {trackID}, {curSegDistance}, {tach}, {brakePossibleBool}, {pid.setpoint}, {rpm}, --')
                    
                    #if we could not brake down to where we need to be then we brake (it will catch this on the first hit)
                    elif brakePossibleBool is not True:
                        mph = RPMtoMPH(readRPM())
                        kph = RPMtoKPH(readRPM())
                        tqdm.write(f'(FULL BRAKE), Race instructions: Straight, Race segment: {trackID}, Distance into segment: {round(curSegDistance, 3)}, Speed: {round(mph, 3)} mph, {round(kph, 3)} kph')

                        #logging stuff
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        appendToLog(f'{timestamp}, {time.time()}, Straight(Full Brake), {mph}, {kph}, {TORQS}, {outVoltage}, {readRPM() * TORQS}, {lapTime}, {curLap}, {NUM_LAPS}, {segtime}, {trackID}, {curSegDistance}, {readTach()}, {brakePossibleBool}, {pid.setpoint}, {readRPM()}, --')
                    
                    #print(f'Out Voltage For Straight Away: {outVoltage}')
                    
                    if (readRPM() < (MAX_MOTOR_RPM * 0.05)):
                        straight_speed = MAX_MOTOR_RPM * 0.05

                    #used to send voltage to arduino
                    sendRPM(straight_speed, sendQueue)

                    lastTime = tm.time()
                    tm.sleep(abs(POLLING_RATE - (lastTime - currentTme)))

            elif seg.turnRadius > 0:
                #kart is in turn
                tqdm.write(f'Kart is in turn')

                #intializes the several variables
                tacometer_cur_distance = readTach()
                curSegDistance, origionalTrackID = tachTranslator(raceInfo, tacometer_cur_distance)
                currentRPM = readRPM()
                tqdm.write(f'Race segment: {origionalTrackID}, Distance into segment: {curSegDistance}')

                # tell dyno to run normal physics
                dynoMode(0, dynoQueue)
                
                #creates a PID controller for the voltage
                object = KartRPM()
                object.current = currentRPM
                goalRPM = seg.maxRPM
                pid = PID(0.004, 0.004, 0.0001, setpoint=goalRPM)
                pid.output_limits = (MAX_MOTOR_RPM*0.05, MAX_MOTOR_RPM)

                startTime = tm.time()
                lastTime = startTime

                trackID = origionalTrackID
                
                #runs a loop until the kart leaves the segment
                while seg.length > curSegDistance and trackID == origionalTrackID:
                    
                    currentRPM = readRPM()
                    
                    tacometer_cur_distance = readTach()
                    curSegDistance, trackID = tachTranslator(raceInfo, tacometer_cur_distance)
                    mph = RPMtoMPH(currentRPM)
                    kph = RPMtoKPH(currentRPM)
                    #print(f'THROTTLE: {currentVoltage * 20}%, Race segment: {trackID}, Distance into segment: {curSegDistance}')
                    
                    throttle = ''
                    
                    percentageError = 0.1
                    if G_RPM > (seg.maxRPM * (1 + percentageError)):
                        throttle = 'Less Throttle'
                    elif G_RPM < (seg.maxRPM * (1 - percentageError)):
                        throttle = 'More Throttle'
                    elif G_RPM > (seg.maxRPM * (1 - percentageError)) and G_RPM < (seg.maxRPM * (1 + percentageError)):
                        throttle = 'Ideal Throttle'
                    
                    tqdm.write(f'THROTTLE: {throttle}%, Race instructions: Turn, Race segment: {trackID}, Distance into segment: {round(curSegDistance, 3)}, Current RPM: {ReadRPM()}, Speed: {round(mph, 3)} mph, {round(kph, 3)} kph, Expected RPM: {round(seg.maxRPM, 3)}')
                    
                    #logging stuff
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    appendToLog(f'{timestamp}, {time.time()}, Turn, {mph}, {kph}, {TORQS}, {outVoltage}, {readRPM() * TORQS}, {lapTime}, {curLap}, {NUM_LAPS}, {segtime}, {trackID}, {curSegDistance}, {readTach()}, {brakePossibleBool}, {pid.setpoint}, {readRPM()}, {seg.maxRPM}')
                    
                    if trackID != origionalTrackID:
                        break

                    #PID loop for voltage, especially needed since the kart need to feather throttle around the turn
                    currentTme = tm.time()
                    dt = currentTme - lastTime
                    power = pid(currentRPM)
                    currentRPM = object.update(power, dt)

                    
                    #used to send voltage to arduino
                    sendRPM(currentRPM, sendQueue)

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
