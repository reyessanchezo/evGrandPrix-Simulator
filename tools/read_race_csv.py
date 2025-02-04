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
    data = read_race_data(standardized=True)
    for row in data:
        print(f"time: {row[0]}, rpm: {row[1]}")
