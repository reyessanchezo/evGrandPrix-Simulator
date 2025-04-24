"""
mylist = ['hello', 'world']

# evil print statement
print(f"mylist contains {'a' if len(mylist) == 1 else 'some'} word{'' if len(mylist) == 1 else 's'}")

exit()
"""

import os
import pandas as pd

files = []
tmp = os.listdir(os.path.dirname(os.path.realpath(__file__)))
for file in tmp:
    if (file[-4:] == ".log"):
        files.append(file)

for i in range(len(files)):
    print(f"{i}: {files[i]}")

opt = -1
while opt > len(files) or opt < 0:
    opt = int(input("Enter the index of file you want to convert: "))
logfile = files[opt]

#logfile = "raceLog82.log"

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

newName = logfile.split('.')
del(newName[-1])
newName = '.'.join(newName)

df.to_csv(f'{newName}.csv', index=False)