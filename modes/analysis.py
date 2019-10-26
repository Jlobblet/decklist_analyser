import pandas as pd

#from config.CONFIG import CONFIG
from .functions import create_set

data_loc = r"data/aggregate/week1.csv"


def read_raw_data(data_loc=data_loc):
    df = pd.read_csv(data_loc)
    df = df.dropna().reset_index().loc[:, ["Deck 1 List", "Deck 2 List", "Deck 3 List"]]

    print(df)


if __name__ == "__main__":
    read_raw_data()
