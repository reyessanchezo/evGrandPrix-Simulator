import time
import matplotlib.pyplot as plt
from simple_pid import PID

class KartVoltage:
    def __init__(self):
        self.current = 0 #volts
    
    def update(self, power, dt):
        if power > 0:
            # PROBLEM LIES HERE
            self.current += 1 * power * dt

        # Some heat dissipation
        #self.water_temp -= 0.02 * dt
        return self.current
    
def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

def RPMtoVoltage(rpm):
    return num_to_range(rpm, 0, 4500, 0.9, 4.1)

def PIDInit(reach_rpm : int, ):
    object = KartVoltage()

    currentRPM = object.current
    currentVoltage = RPMtoVoltage(currentRPM)
    #print(f'CURRENT VOLTAGE {currentVoltage}')

    goalRPM = 1000
    goalVoltage = RPMtoVoltage(goalRPM)
    #print(f'GOAL VOLTAGE: {goalVoltage}')

    #print(f'Second GOAL VOLTAGE: {RPMtoVoltage(2500)}')

    pid = PID(3, 0.01, 0.1, setpoint=goalVoltage)
    pid.output_limits = (0, 5)

    startTime = time.time()
    lastTime = startTime

    while time.time() - startTime < 10:
        currentTme = time.time()
        dt = currentTme - lastTime
        #print(f'DT: {dt}')
        power = pid(currentVoltage)
        #print('POWER: ', power)
        currentVoltage = object.update(power, dt)
        #print('CURRENT: ', currentVoltage)
        lastTime = time.time()
        time.sleep(abs(0.1 - (lastTime - currentTme)))
        if (lastTime - startTime) > 5:
                targetRPM = 2500
                pid.setpoint = RPMtoVoltage(targetRPM)