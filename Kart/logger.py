import os
from datetime import datetime
import time

def createNewRacelogFilename(directory="logs"):
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if f.startswith("raceLog") and f.endswith(".log")]
    
    if not files:
        # If no files exist, start with raceLog1.log
        return "raceLog1.log"
    
    # Extract numbers from existing filenames
    numbers = []
    for file in files:
        try:
            # Extract number between "raceLog" and ".log"
            num = int(file.replace("raceLog", "").replace(".log", ""))
            numbers.append(num)
        except ValueError:
            continue
    
    # Get the next number in sequence
    next_num = max(numbers) + 1 if numbers else 1
    
    return f"raceLog{next_num}.log"

def createNewRacelogFile(directory="logs"):
    filename = createNewRacelogFilename(directory)
    filepath = os.path.join(directory, filename)
    
    # Create an empty file
    with open(filepath, 'w') as f:
        pass
    
    return filepath

def appendToLog(message, directory="logs"):
    # Get the latest log file
    files = [f for f in os.listdir(directory) if f.startswith("raceLog") and f.endswith(".log")]
    if not files:
        raise FileNotFoundError("No log files found in the specified directory")
    
    # Extract numbers and find the latest file
    latest_file = max(
        files,
        key=lambda x: int(x.replace("raceLog", "").replace(".log", ""))
    )
    
    # Construct full file path
    filepath = os.path.join(directory, latest_file)
    
    # Append message to the file
    with open(filepath, 'a') as f:
        # Add a newline before the message if the file is not empty
        if os.path.getsize(filepath) > 0:
            f.write('\n')
        f.write(message)


def readTach():
    """READ Tachometer"""
    return 0

def readRPM():
    """READ MOTOR RPM"""
    return 0

createNewRacelogFile()        
for i in range(1000):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mph = 0
    kph = 0
    TORQS = 0
    outVoltage = 0
    G_RPM = 0
    lapTime = 0
    curLap = 0
    NUM_LAPS = 0
    segtime = 0
    trackID = 0
    curSegDistance = 0
    brakePossibleBool = 0
    setpoint = 0
    appendToLog(f'{timestamp}, {time.time()}, Straight(Full Throttle), {mph}, {kph}, {TORQS}, {outVoltage}, {G_RPM * TORQS}, {lapTime}, {curLap}, {NUM_LAPS}, {segtime}, {trackID}, {curSegDistance}, {readTach()}, {brakePossibleBool}, {setpoint}, {readRPM()}, --')
