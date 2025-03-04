import math, pathlib
import pandas as pd
from typing import Tuple
import time as tm

STATICFRICTION = 2.480847866
GRAV_ACCELLERATION = 9.8
NUM_LAPS = 50

#Race detail is a section made to designate a portion of the track
#This class contains a length of the section, a turn radius (if not a race then -1), and if its a turn what the max speed is.
class RaceDetail:
    def __init__(self, length, turnRadius=-1):
        self.length = abs(length)
        self.turnRadius = turnRadius
        if turnRadius > 0:
            self.calcMaxSpeed(turnRadius)
        
    def calcMaxSpeed(self, turnRadius):
        self.max_speed = math.sqrt(STATICFRICTION * GRAV_ACCELLERATION * turnRadius)

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

#tacTranslator changes the tacometer for distance traveled on the track to a segment ID for which section its in and also a current distance into the length of that section 
#Ex.: tacTranslator(thisRace, 38) --> distance into track (1.86906398) and the RaceDetail object the tacometer distance is currently driving in
def tacTranslator(thisRace: RaceInfo, tacometer: int | float) -> Tuple[float, RaceDetail]:
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

if __name__ == '__main__':
    thisRace = csv_to_raceinfo("raceCSV.csv")
    
    print(thisRace)
    currSegDistance, raceSeg = tacTranslator(thisRace, 38)
    print(f'Number of laps: {NUM_LAPS}')
    NUM_LAPS *= len(thisRace.RaceDetails)

    if thisRace.isLoop:
        for lap in range(NUM_LAPS):
            #main event loop for race
            start = tm.time()
            if raceSeg.turnRadius < 0:
                #print('Straight.')
                #if kart in straight away do a straight away !
                #probaby start seperate thread
                pass
            elif raceSeg.turnRadius > 0:
                #print('Turn.')
                #if kart is in turn do turn !
                #probaby start seperate thread
                pass
            else:
                raise ValueError("Race turn radius cannot be 0")
            
            end = tm.time()
            timer = end - start
            if 0.1 >= timer:
                tm.sleep(0.1 - timer)
            else:
                raise TimeoutError("Calculation time longer than polling rate.")

