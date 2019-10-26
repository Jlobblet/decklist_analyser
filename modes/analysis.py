import pandas as pd
import igraph as ig
import louvain as lv

#from config.CONFIG import CONFIG
from .functions import create_set

data_loc = r"data/aggregate/week1.csv"


def read_raw_data(data_loc=data_loc):
    df = pd.read_csv(data_loc)
    df = df.dropna().reset_index().loc[:, ["Deck 1 List", "Deck 2 List", "Deck 3 List"]]
    df = df.replace("’", "'")
    df = df.applymap(create_set)

    # print(df)
    return df


def main():
    df = read_raw_data()
    all_cards = set()
    for index, row in df.iterrows():
        for deck in row:
            all_cards = all_cards | deck
    card_data_df = pd.DataFrame(all_cards, columns=["Card"]).sort_values(by="Card")
    card_data_df["Count"] = 0
    # card_data_df["Decks"]
    # card_data_df["Decks"] = card_data_df["Decks"].astype(object)
    print(card_data_df)
