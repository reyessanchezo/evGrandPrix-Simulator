import math, time

import RaceTurn

def fake_track():
    TIRE_DIAMETER = 0.3 # meters
    LONG_LENGTH = 500 # meters
    TURN_LENGTH = 50 # meters
    TOTAL_TRACK = (2 * LONG_LENGTH) + (2 * TURN_LENGTH)
    RPM = 3000 # we will read this live outside of this simulation.

    turning = False
    distance = 0 # The distance the kart has covered. We will use this to help the kart know when it should turn. Determined by RPM read through PyVesc.
    
    print(f"Simulating track assuming a straight length of {LONG_LENGTH} and a turn length of {TURN_LENGTH}.\nBasically This:\n")
    print(f"({TURN_LENGTH})\n ###\n#   #\n#   #\n#   # ({LONG_LENGTH})\n#   #\n#   #\n ###")

    try:
        while True:
            # RPM / 60 for RPS, times 0.1 for a 0.1 second sampling rate.
            # multiply by circumference (diameter times pi) to get actual distance covered
            distance += ((RPM / 60) * 0.1) * (TIRE_DIAMETER * math.pi)
            distance %= TOTAL_TRACK
            
            # Have to make the kart know what stretch its on so it knows if it should turn.
            # doesnt work right now. have to re-check logic.
            turning = ((distance > LONG_LENGTH) and (distance < (LONG_LENGTH + TURN_LENGTH))) or (distance > (2 * LONG_LENGTH) + TURN_LENGTH)
            
            print(f"Distance covered: {distance:0.2f}. ", end="")
            if turning:
                print("I must turn.", end="")
            print()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program terminated.")

def track_sim():
    RPM = 3000 # dummy number until we can read it live again.
    DUMMY_ACC = 12
    DUMMY_DEC = -21.575
    MAX_RPM = 4500

    MAX_DECEL = -21.575

    TIRE_DIAMETER = 0.3 # meters

    SPEED_TARGET = 12.824 # m/s
    # decel_req = (SPEED_TARGET - speed_current) / (DISTANCE_TARGET - distance_local)


    print(f"Simulating track assuming a straight length of {LONG_LENGTH:0.2f} and a turn length of {TURN_LENGTH:0.2f}.\nBasically This:\n")
    print(f"({TURN_LENGTH:0.2f})\n ###\n#   #\n#   #\n#   # ({LONG_LENGTH:0.2f})\n#   #\n#   #\n ###")

    turning = False

    try:
        while True:
            distance_global += ((RPM / 60) * 0.1) * (TIRE_DIAMETER * math.pi)
            distance_local = distance_global % TRACK_LENGTH

            

            print(f"current speed: {speed_current:0.3f}, decel required to reach exit speed: {decel_req:0.3f}, local distance: {distance_local:0.3f}, % along track: {(distance_local/TRACK_LENGTH):0.3f}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program Terminated.")

if __name__ == '__main__':
    track_sim()