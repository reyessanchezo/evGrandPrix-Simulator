from tqdm import tqdm
from threading import Thread, Event
import time
import sys
import math

TOTALDISTANCE = 123.5
CURRDISTANCE = 0
NUM_LAPS = 3

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def tqdmDistanceConverter(currDistance, totalDistance) -> int:
    return int(math.ceil(num_to_range(currDistance, 0, totalDistance, 0, 100)))

def tqdmLoop() -> None:
    pbar = tqdm(range(100), desc="Progress...", ascii=True, dynamic_ncols=True)
    while True:
        pbar.n = tqdmDistanceConverter(CURRDISTANCE)
        pbar.refresh()
        time.sleep(0.05)


def DistanceIncrement() -> None:
    global CURRDISTANCE
    global TOTALDISTANCE
    for i in range(100000):
        CURRDISTANCE += 1.1
        time.sleep(0.05)
        #print(f'Distance: {tqdmDistanceConverter(CURRDISTANCE)}')

def tqdmDistanceLoop(raceLength) -> None:
    global NUM_LAPS
    global CURRDISTANCE
    odometer = CURRDISTANCE
    odTrack = odometer % raceLength
    pbarLapDistance = tqdm(range(100), desc="Progress in lap...", ascii=True, dynamic_ncols=True)
    pbarTotalDistance = tqdm(range(100), desc="Total progress in race...", ascii=True, dynamic_ncols=True)
    while odometer < raceLength * NUM_LAPS:
        pbarLapDistance.n = tqdmDistanceConverter(odTrack, raceLength)
        pbarTotalDistance.n = tqdmDistanceConverter(odometer, (raceLength * NUM_LAPS))
        pbarLapDistance.refresh()
        pbarTotalDistance.refresh()
        
        odometer = CURRDISTANCE
        odTrack = odometer % raceLength
        
        time.sleep(0.1)
    
if __name__ == '__main__':
    TOTALDISTANCE = 123.5
    
    t1 = Thread(target=DistanceIncrement, daemon=True)
    #t2 = Thread(target=tqdmLoop, daemon=False)
    t3 = Thread(target=tqdmDistanceLoop, daemon=False, args=(TOTALDISTANCE,))
    t1.start()
    #t2.start()
    t3.start()
    print(f'please wait...')
    #time.sleep(2)
    #print(f'Distance In Main: {CURRDISTANCE}')
    
