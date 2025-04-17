import os
from datetime import datetime

def create_new_testlog_filename(directory="tools/testlogs"):
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if f.startswith("testLog") and f.endswith(".log")]
    
    if not files:
        # If no files exist, start with testLog1.log
        return "testLog1.log"
    
    # Extract numbers from existing filenames
    numbers = []
    for file in files:
        try:
            # Extract number between "testLog" and ".log"
            num = int(file.replace("testLog", "").replace(".log", ""))
            numbers.append(num)
        except ValueError:
            continue
    
    # Get the next number in sequence
    next_num = max(numbers) + 1 if numbers else 1
    
    return f"testLog{next_num}.log"

def create_new_testlog_file(directory="tools/testlogs"):
    filename = create_new_testlog_filename(directory)
    filepath = os.path.join(directory, filename)
    
    # Create an empty file
    with open(filepath, 'w') as f:
        pass
    
    return filepath

def append_to_log(message, directory="tools/testlogs"):
    # Get the latest log file
    files = [f for f in os.listdir(directory) if f.startswith("testLog") and f.endswith(".log")]
    if not files:
        raise FileNotFoundError("No log files found in the specified directory")
    
    # Extract numbers and find the latest file
    latest_file = max(
        files,
        key=lambda x: int(x.replace("testLog", "").replace(".log", ""))
    )
    
    # Construct full file path
    filepath = os.path.join(directory, latest_file)
    
    # Append message to the file
    with open(filepath, 'a') as f:
        # Add a newline before the message if the file is not empty
        if os.path.getsize(filepath) > 0:
            f.write('\n')
        f.write(message)

# Example usage:
#create_new_testlog_file()
append_to_log("This is a new log entry")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
append_to_log(f"This is a log entry with a timestamp: {timestamp}")