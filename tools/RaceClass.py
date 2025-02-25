import math
STATICFRICTION = 2.480847866
GRAV_ACCELLERATION = 9.8

class RaceDetail:
    def __init__(self, length, turnRadius=-1):
        self.length = abs(length)
        self.turnRadius = turnRadius
        if turnRadius > 0:
            self.calcMaxSpeed(turnRadius)
        
    def calcMaxSpeed(self, turnRadius):
        self.max_speed = math.sqrt(STATICFRICTION * GRAV_ACCELLERATION * turnRadius)

class RaceInfo:
    def __init__(self, RaceDetails, isLoop=True):
        self.RaceDetails = RaceDetails
        self.isLoop = isLoop
        self.calcTotalLength()
        self.currPositionTotal = 0
        self.currPositionTrack = 0
        
    def calcTotalLength(self):
        self.totalLength = 0
        for length in self.RaceDetails:
            self.totalLength += length.length
    
    def __str__(self):
        ret = []
        for raceDetail in self.RaceDetails:
            ret.append(f"Length: {raceDetail.length}, Turn Radius: {raceDetail.turnRadius}")
        ret.append(f"Total length: {self.totalLength}")
        ret.append(f"Current position total: {self.currPositionTotal}")
        ret.append(f"Current position on track: {self.currPositionTrack}")
        return "\n".join(ret)
        

if __name__ == '__main__':

    import pandas as pd
    data = pd.read_csv("raceCSV.csv")

    RaceArray = []

    for index, row in data.iterrows():
        if pd.isna(row['Turn Radius']):
            RaceArray.append(RaceDetail(length=row['Length']))
        else:
            RaceArray.append(RaceDetail(length=row['Length'], turnRadius=row['Turn Radius']))
    
    thisRace = RaceInfo(RaceArray)
    print(thisRace)