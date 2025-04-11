from tqdm import tqdm
from threading import Thread
import time
import math
import time as tm

RACELENGTH = 120.30
CURRDISTANCE = 0
NUM_LAPS = 3
BOOL = False

def DistanceIncrement() -> None:
    global CURRDISTANCE
    
    global BOOL
    while not BOOL:
        CURRDISTANCE += 1.1
        time.sleep(0.03)

def readTach():
    """READ Tachometer"""
    return CURRDISTANCE

#one of the most useful functions ive ever seen. Very nice, good soup.
def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def tqdmDistanceConverter(currDistance, totalDistance) -> int:
    return int(math.ceil(num_to_range(currDistance, 0, totalDistance, 0, 100)))

def tqdmDistanceLoop(raceLength) -> None:
    global NUM_LAPS
    timeoutHours = 5 # number of hours before the function times itself out
    timeoutSeconds = timeoutHours * 60 * 60
    
    tachometer = readTach()
    tqdm.write(f'Tachometer: {tachometer}')
    
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
        
if __name__ == '__main__':
    
    DistanceIncrementer = Thread(target=DistanceIncrement, daemon=True)
    
    tqdmDistanceThread = Thread(
        target=tqdmDistanceLoop, 
        args=(float(RACELENGTH), ),
        daemon=False #it does not work if it is a daemon, but it naturally stops when the program ends. unsure if this is a problem but i added a timeout to the function
    )
    DistanceIncrementer.start()
    tqdmDistanceThread.start()
        
    print(f'please wait...')
    while readTach() < RACELENGTH * NUM_LAPS:
        tqdm.write(f'Distance In Main: {CURRDISTANCE}')
        time.sleep(0.1)
    
    time.sleep(0.5)
    tqdm.write(f'Finished. Current distance: {CURRDISTANCE}')