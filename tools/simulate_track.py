import math, time

if __name__ == '__main__':
    TIRE_DIAMETER = 25 # centimeters
    LONG_LENGTH = 5000 # meters
    TURN_LENGTH = 500 # meters
    TOTAL_TRACK = (2 * LONG_LENGTH) + (2 * TURN_LENGTH)
    RPM = 3000 # we will read this live outside of this simulation.

    turning = False
    distance = 0 # The distance the kart has covered. We will use this to help the kart know when it should turn. Determined by RPM read through PyVesc.
    
    print(f"Simulating track assuming a straight length of {LONG_LENGTH} and a turn length of {TURN_LENGTH}.\nBasically This:\n")
    print(f"({TURN_LENGTH})\n ###\n#   #\n#   #\n#   # ({LONG_LENGTH})\n#   #\n#   #\n ###")

    while True:
        # RPM / 60 for RPS, times 0.1 for a 0.1 second sampling rate.
        # multiply by circumference (diameter times pi) to get actual distance covered
        distance += (((RPM / 60) * 0.1) * (TIRE_DIAMETER * math.pi))
        distance %= TOTAL_TRACK
        
        # Have to make the kart know what stretch its on so it knows if it should turn.
        # doesnt work right now. have to re-check logic.
        turning = ((distance > LONG_LENGTH) and (distance < (LONG_LENGTH + TURN_LENGTH))) or (distance > (2 * LONG_LENGTH) + TURN_LENGTH)
        
        print(f"Distance covered: {distance:0.2f}. ", end="")
        if turning:
            print("I must turn.", end="")
        print()
        time.sleep(0.1)