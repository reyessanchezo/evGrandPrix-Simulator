import os
import pandas as pd

def read_race_data():
    
    #These two rows should remove the header and the row that shows the units (which both break pandas)
    data = pd.read_csv("imu_data.csv", skiprows=14)
    data.drop(0, inplace=True)

    #fill any NaN with a filler value for now. Ideally, we don't need this when we get better data.
    data.fillna(0, inplace=True)

    #For my purposes, I only kept these two. If more are needed, consult the CSV for relavent header names.
    #The garbage data we got from karting didn't record time, so I cannot ensure that row is working properly with what I have right now.
    #Since the IMU is recorded as acceleration, I need time before I can do math revolving around it. This will need work later.
    return data[['Time', 'InlineAcc', 'LateralAcc']]

if __name__ == '__main__':
    # i don't know what metric we can read from the csv just yet. rpm is a placeholder.
    # we may need to do math that allows us to know what duty cycle we need to apply to reach the desired rpm.
    # we need to take speed, tire diameter, rpm. circumference is pi times diamater. multiply by rps to get velocity.
    # We know we can't go further than 12.824 m/s across the turn or we will slip.
    # if we can correlate duty cycle to the speeds we need to hit, we can create a function to feed the right duty cycle to the controller.
    # We can divide the desired rps by the max of the motor to find what duty cycle we may need, but we also need to account for the braking
    #     we need to overcome to reach the speeds. This may not be required depending on how the dyno work while simulating intertia.
    data = read_race_data()
    print(data)
