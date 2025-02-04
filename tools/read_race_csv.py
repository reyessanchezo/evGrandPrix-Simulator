import csv
import os

def read_race_data(standardized = False):
    data = []
    
    data_path = os.path.join(os.getcwd(), "tools", "race_data.csv")
    
    with open(data_path, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)

    data.pop(0)
    data = sorted(data, key=lambda x: int(x[0]))
    if standardized:
        base = int(data[0][0])
        data = map(lambda x: [int(x[0]) - base, x[1]], data)
    return data

if __name__ == '__main__':
    # i don't know what metric we can read from the csv just yet. rpm is a placeholder.
    # we may need to do math that allows us to know what duty cycle we need to apply to reach the desired rpm.
    # we need to take speed, tire diameter, rpm. circumference is pi times diamater. multiply by rps to get velocity.
    # We know we can't go further than 12.824 m/s across the turn or we will slip.
    # if we can correlate duty cycle to the speeds we need to hit, we can create a function to feed the right duty cycle to the controller.
    # We can divide the desired rps by the max of the motor to find what duty cycle we may need, but we also need to account for the braking
    #     we need to overcome to reach the speeds. This may not be required depending on how the dyno works.
    data = read_race_data()
    for row in data:
        print(f"time: {row[0]}, rpm: {row[1]}")
