import time
import matplotlib.pyplot as plt
from simple_pid import PID

MAX_VOLTAGE = 3.3
MAX_MOTOR_RPM = 4500
POLLING_RATE = 0.1

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
    return num_to_range(rpm, 0, MAX_MOTOR_RPM, 0.0, MAX_VOLTAGE)

def PIDInit(reach_rpm : int, ):
    object = KartVoltage()

    currentRPM = 1000
    currentVoltage = RPMtoVoltage(currentRPM)
    object.current = currentVoltage
    #print(f'CURRENT VOLTAGE {currentVoltage}')

    goalRPM = 2000
    
    #i dont think this is working.
    goalVoltage = RPMtoVoltage(goalRPM)
    #print(f'GOAL VOLTAGE: {goalVoltage}')

    #print(f'Second GOAL VOLTAGE: {RPMtoVoltage(2500)}')

    pid = PID(3, 0.01, 0.1, setpoint=goalVoltage)
    pid.output_limits = (0, MAX_VOLTAGE)

    startTime = time.time()
    lastTime = startTime

    while time.time() - startTime < 10:
        currentTme = time.time()
        dt = currentTme - lastTime
        #print(f'DT: {dt}')
        power = pid(currentVoltage)
        #print('POWER: ', power)
        currentVoltage = object.update(power, dt)
        print('CURRENT: ', currentVoltage)

        lastTime = time.time()
        time.sleep(abs(POLLING_RATE - (lastTime - currentTme)))
        
def PIDRPMInit(reach_rpm : int, ):
    object = KartVoltage()

    currentRPM = 1000
    object.current = currentRPM
    #print(f'CURRENT VOLTAGE {currentVoltage}')

    goalRPM = reach_rpm
    
    #i dont think this is working.
    #print(f'GOAL VOLTAGE: {goalVoltage}')

    #print(f'Second GOAL VOLTAGE: {RPMtoVoltage(2500)}')

    pid = PID(5, 0.01, 0.1, setpoint=goalRPM)
    pid.output_limits = (0, MAX_MOTOR_RPM)

    startTime = time.time()
    lastTime = startTime

    while time.time() - startTime < 10:
        currentTme = time.time()
        dt = currentTme - lastTime
        #print(f'DT: {dt}')
        power = pid(currentRPM)
        currentRPM = object.update(power, dt)
        #print('POWER: ', power)
        print('CURRENT: ', currentRPM)

        lastTime = time.time()
        time.sleep(abs(POLLING_RATE - (lastTime - currentTme)))
        

PIDRPMInit(3000)