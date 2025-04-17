from RaceClass import *
import numpy as np
import sys

# Adjust the constants and functions for your vehicle
gear_ratio = 1.0 / 5.0      # Motor shaft to wheel
wheel_diameter_inches = 6.0    # measure!!! TODO
braking_friction_coef = 0.7
turning_friction_coef = 2.48
car_mass_kg = 136.0 # 300lb

# Secondary calcuations
rpm_to_ms = (math.pi * wheel_diameter_inches) * gear_ratio * 60.0 / 12.0 / 5280 * 0.45
    # motor torque is in ft-lb.  1 ft-lb = 1.356 nm
motor_torque_to_N = 1.356 / (wheel_diameter_inches/12.0) / gear_ratio

dt = 0.01 # Time step for the simulation.

# Class to import a CSV file of measured RPM-to-Torque for a particular motor and allow querying of
# the torque at a specific motor RPM.  Interpolates
# Assumes RPM and ft-lb
class TorqueMeasured:
    def __init__(self, torqueCSV: str | pathlib.Path):
        try:
            data = pd.read_csv(torqueCSV)
        except:
            raise ImportError("Torque CSV Import Error -- Try Checking The CSV Integrity")
        #if('RPM') # TODO verify RPM and Torque are columns
        data = data.sort_values('RPM') # X needs to be increasing for interp
        #print(data)
        self.rpm = data['RPM'].to_numpy()
        self.torque = data['Torque'].to_numpy()
        
    def getTorque(self, rpm: float) -> float:
        # Will return 0 if the rpm is smaller or larger than specified in the CSV
        return np.interp([rpm], self.rpm, self.torque, left=0, right=0)[0]

    def __str__(self):
        ret = f"RPM(min): {self.rpm.min()} RPM(max): {self.rpm.max()}\n"
        ret += f"Torque (ft-lb)(min): {self.torque.min()}  Torque (ft-lb)(max): {self.torque.max()}\n"
        power_hp = (self.torque * self.rpm / 5252).max()
        ret += f"Max Power Measured (Watt): {power_hp * 745.7}    (HP): {power_hp}\n"
        rpm_test = np.linspace(0, self.rpm.max(), 500)
        torque_test = np.interp(rpm_test, self.rpm, self.torque)
        power_hp_test = (rpm_test * torque_test / 5252).max()
        ret += f"Max Power Interp (Watt): {power_hp_test * 745.7}    (HP): {power_hp_test}\n"
        return ret

def ms_to_mph(ms: float) -> float:
    return ms * 2.23694

if __name__ == "__main__":
    thisRace = csv_to_raceinfo('raceCSV.csv')
    torqueTable = TorqueMeasured('torque3000W.csv')
    print(thisRace)
    print(torqueTable)
    #print(torqueTable.getTorque(0) )
    #print(6000 * rpm_to_mph)
    print(thisRace)

    position = 0 # Units in meters
    speed = 0 # Units in m/s
    time = 0 # Units in seconds
    
    lap = 0
    last_lap_time = 0
    detail_i = 0
    detail_position = 0
    lap_distance = 0
    for section in thisRace.RaceDetails:
        lap_distance += section.length
    print(f"Lap distance (m): {lap_distance} (ft): {lap_distance * 3.28084}")
    #sys.exit(1)
    print("\n  ----Starting Simulation----\n")
    while lap < 3:
        # What stage are we in (RaceDetail)  - Check if advancing
        if detail_position > thisRace.RaceDetails[detail_i].length: # Just exited section
            detail_position = detail_position - thisRace.RaceDetails[detail_i].length
            detail_i += 1
            if detail_i >= len(thisRace.RaceDetails):  # We did a lap!
                print(f"---- Lap {lap + 1} Complete!  Total Time: {time}  Lap Time: {time - last_lap_time} ----")
                last_lap_time = time
                lap += 1
                detail_i = 0
        # Now we know we're in a valid section (Detail), at detail_position
        # Which case?  Hard accelerate straight, brake hard straight, in a turn?
        section = thisRace.RaceDetails[detail_i]
        
        if section.turnRadius > 0:  # In a turn
            # Assume max speed for that turn
            max_speed = math.sqrt(turning_friction_coef * GRAV_ACCELLERATION * section.turnRadius)
            if speed < max_speed:
                # Accelerate in the turn
                cur_rpm = speed / rpm_to_ms
                avail_torque = torqueTable.getTorque(cur_rpm)
                push_N = avail_torque * motor_torque_to_N
                # Assume no drag
                accel = push_N / car_mass_kg    # in m/s
                speed += accel * dt
                traveled = speed * dt
                detail_position += traveled
                position += traveled
                time += dt
                print(f"i:{detail_i}   Turn-accel  t:{time:3f} Speed: {speed:.2f} Percent done {detail_position / thisRace.RaceDetails[detail_i].length * 100:.1f}")
            else:
                speed = max_speed
                traveled = speed * dt
                detail_position += traveled
                position += traveled
                time += dt
                print(f"i:{detail_i}   Turn  t:{time:3f} Speed: {speed:.2f} Percent done {detail_position / thisRace.RaceDetails[detail_i].length * 100:.1f}")
        else:
            # Must be in a straightaway - Are we accelerating or braking?
            # If there is a straightaway next section - floor it and assume we can brake in the next section
            if thisRace.RaceDetails[(detail_i + 1) % len(thisRace.RaceDetails)].turnRadius <= 0:
                cur_rpm = speed / rpm_to_ms
                avail_torque = torqueTable.getTorque(cur_rpm)
                push_N = avail_torque * motor_torque_to_N
                # Assume no drag
                accel = push_N / car_mass_kg    # in m/s
                speed += accel * dt
                traveled = speed * dt
                detail_position += traveled
                position += traveled
                time += dt
                print(f"i:{detail_i}   S-fast  t:{time:3f} Speed: {speed:.2f} Percent done {detail_position / thisRace.RaceDetails[detail_i].length * 100:.1f}")
            else:
                # We have a turn next
                turn_max_speed = math.sqrt(turning_friction_coef * GRAV_ACCELLERATION * thisRace.RaceDetails[(detail_i + 1) % len(thisRace.RaceDetails)].turnRadius)
                dist_to_next = section.length - detail_position
                # Distance to a speed is (vfinal^2 - vinit^2)/ (2 frict  g)
                # https://en.wikipedia.org/wiki/Braking_distance#:~:text=Example%3A%20velocity%20%3D%2050%20MPH.,the%20diagram%20on%20the%20right).
                brake_distance = (speed * speed - turn_max_speed * turn_max_speed) / (2 * braking_friction_coef * GRAV_ACCELLERATION)
                #print(f"next: {dist_to_next:.2f} max turnspeed: {turn_max_speed:.2f} Brake distance: {brake_distance:.2f}")
                if brake_distance < 0 or brake_distance < dist_to_next:
                    # Keep accelerating!
                    cur_rpm = speed / rpm_to_ms
                    avail_torque = torqueTable.getTorque(cur_rpm)
                    push_N = avail_torque * motor_torque_to_N
                    # Assume no drag
                    accel = push_N / car_mass_kg    # in m/s
                    speed += accel * dt
                    traveled = speed * dt
                    detail_position += traveled
                    position += traveled
                    time += dt
                    print(f"i:{detail_i}   S-acc  t:{time:3f} Speed: {speed:.2f} Percent done {detail_position / thisRace.RaceDetails[detail_i].length * 100:.1f}")
                else:
                    # Brake!
                    brake_accel =  braking_friction_coef *GRAV_ACCELLERATION
                    # Assume no drag
                    speed += brake_accel * dt
                    traveled = speed * dt
                    detail_position += traveled
                    position += traveled
                    time += dt
                    print(f"i:{detail_i}   S-BR  t:{time:3f} Speed: {speed:2f} Percent done {detail_position / thisRace.RaceDetails[detail_i].length * 100:.1f}")
        #input("enter to continue")