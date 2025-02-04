from typing import List, Tuple

import pandas as pd


def load_file(path: str) -> pd.DataFrame:
    """Loads CSV (only) file and returns a pandas dataframe."""
    return pd.read_csv(path)


def demo(df: pd.DataFrame) -> List[Tuple[float, float]]:
    """Takes a pandas dataframe and returns a list of pairs (speed, duration)."""
    return [(0.3, 0.4)]
