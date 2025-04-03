import os
from datetime import datetime

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

createNewRacelogFile()        
for i in range(1000):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    appendToLog(f"Timestamp: {timestamp}, Race instructions: Straight (Full Throttle), Torque: 10, RPM: 1000, Voltage: 3.4, Power: 10000, Last Lap Time: 125.3, Current Lap: 5, Total Laps: 50, Current Segment: 2, Distance into Segment: 5.345, Odometer: 123456, Brake Possible: True, PID Setpoint: 1000000")