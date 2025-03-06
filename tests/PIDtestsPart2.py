from simple_pid import PID
import math, pathlib
import pandas as pd
from typing import Tuple
import time as tm
import tqdm
import os
import matplotlib.pyplot as plt

vel = 15
POLLINGRATE = 0.1

pid = PID(5, 0.01, 0.1, setpoint=15)
pid.output_limits = (0, 30)

class Driver:
    """"
    Functions to simulate the actions of a hypothetical driver.
    """

    def __init__(self):
        self.velocity = 0
        self.voltage = 0
    
    def update(self):
        pass
    

# Keep track of values for plotting
setpoint, y, x = [], [], []

start_time = tm.time()
last_time = start_time

driver = Driver()

for i in tqdm.trange(100):
    current_time = tm.time()
    dt = current_time - last_time
    start = tm.time()
    power = pid(rpm)

    rpm = driver.update(power)

    x += [current_time - start_time]
    y += [water_temp]
    setpoint += [pid.setpoint]

    end = tm.time()
    timer = end - start

    last_time = current_time

    if POLLINGRATE >= timer:
        tm.sleep(POLLINGRATE - timer)
    else:
        raise TimeoutError("Calculation time longer than polling rate.")

plt.plot(x, y, label='measured')
plt.plot(x, setpoint, label='target')
plt.xlabel('time')
plt.ylabel('temperature')
plt.legend()
if os.getenv('NO_DISPLAY'):
    # If run in CI the plot is saved to file instead of shown to the user
    plt.savefig(f"result-py{'.'.join([str(x) for x in sys.version_info[:2]])}.png")
else:
    plt.show()