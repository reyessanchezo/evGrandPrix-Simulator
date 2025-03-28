from tqdm import tqdm
from threading import Thread
import time
import math
import time as tm

RACELENGTH = 153.5
CURRDISTANCE = 0
NUM_LAPS = 3

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def tqdmDistanceConverter(currDistance, RACELENGTH) -> int:
    return int(math.ceil(num_to_range(currDistance, 0, RACELENGTH, 0, 100)))

def tqdmLoop() -> None:
    pbar = tqdm(range(100), desc="Progress...", ascii=True, dynamic_ncols=True)
    while True:
        pbar.n = tqdmDistanceConverter(CURRDISTANCE)
        pbar.refresh()
        time.sleep(0.1)


def DistanceIncrement() -> None:
    global CURRDISTANCE
    global RACELENGTH
    for i in range(100000):
        CURRDISTANCE += 1.1
        time.sleep(0.03)
        #print(f'Distance: {tqdmDistanceConverter(CURRDISTANCE)}')

def tqdmDistanceLoop(raceLength) -> None:
    global NUM_LAPS
    global CURRDISTANCE
    timeout = 5 # in hours
    odometer = CURRDISTANCE
    odTrack = odometer % raceLength
    lapNum = 1
    timstart = tm.time()
    curTime = timstart
    pbarLapDistance = tqdm(range(100), 
                           desc=f"Progress in lap", 
                           ascii=' █', 
                           dynamic_ncols=True, 
                           bar_format='{desc:<20} {percentage:3.0f}%|\033[34m{bar}\033[0m|')  # Green bar
    pbarRaceLength = tqdm(range(100), 
                          desc="Progress in race", 
                          ascii=' █', 
                          dynamic_ncols=True, 
                          bar_format='{desc:<20} {percentage:3.0f}%|\033[32m{bar}\033[0m|')  # Blue bar
    while odometer < raceLength * NUM_LAPS and (curTime - timstart) < (timeout * 60 * 60):
        pbarLapDistance.n = tqdmDistanceConverter(odTrack, raceLength)
        pbarRaceLength.n = tqdmDistanceConverter(odometer, (raceLength * NUM_LAPS))
        pbarLapDistance.set_description(f'Progress in lap {lapNum}')
        pbarRaceLength.set_description(f"Progress in race")
        pbarLapDistance.refresh()
        pbarRaceLength.refresh()
        
        odometer = CURRDISTANCE
        odTrack = odometer % raceLength
        lapNum = int(odometer // raceLength) + 1
        curTime = tm.time()
        time.sleep(0.01)
    
if __name__ == '__main__':
    RACELENGTH = 123.5
    
    t1 = Thread(target=DistanceIncrement, daemon=True)
    #t2 = Thread(target=tqdmLoop, daemon=False)
    t3 = Thread(target=tqdmDistanceLoop, daemon=False, args=(RACELENGTH,))
    t1.start()
    #t2.start()
    t3.start()
    print(f'please wait...')
    #time.sleep(2)
    #print(f'Distance In Main: {CURRDISTANCE}')
    while CURRDISTANCE < RACELENGTH * NUM_LAPS:
        tqdm.write(f'Distance In Main: {CURRDISTANCE}')
        time.sleep(0.1)
    
