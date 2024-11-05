import os

import numpy as np
import pandas as pd


def generate_data(instructions: int) -> pd.DataFrame:
    np.random.seed(42)

    rpm = np.random.randint(1000, 5000, size=instructions)
    duration = np.random.uniform(1.0, 10.0, size=instructions)

    data = pd.DataFrame({"rpm": rpm, "duration": duration})

    # https://stackoverflow.com/questions/1274405/how-to-create-new-folder
    if not os.path.exists("./sample_data"):
        os.makedirs("./sample_data")

    data.to_csv("./sample_data/data.csv", index=False)

    print("Data saved successfully")
    return data


if __name__ == "__main__":
    _ = generate_data(100)
