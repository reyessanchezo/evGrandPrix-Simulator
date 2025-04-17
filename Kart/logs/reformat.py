"""
mylist = ['hello', 'world']

# evil print statement
print(f"mylist contains {'a' if len(mylist) == 1 else 'some'} word{'' if len(mylist) == 1 else 's'}")

exit()
"""

import pandas as pd

logfile = "raceLog82.log"

outLog = []
outHeaders = []
firstRead = True

with open(logfile, 'r') as file:
    for line in file:
        if firstRead:
            outHeaders = line.split(',')
            firstRead = False
            continue
        outLog.append(line.split(','))

df = pd.DataFrame(outLog, columns=outHeaders)

df.to_csv('output.csv', index=False)