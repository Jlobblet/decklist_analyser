import numpy as np
import pandas as pd
import igraph as ig
import louvain as lv

from config.CONFIG import CONFIG
from .functions import create_set

data_loc = r"data/aggregate/week1.csv"


def read_raw_data(data_loc=data_loc):
    """Collect data from a csv file to locate decklists in and return DataFrame
    of decklists.
    Parameters:
    -----------
    data_loc: string or filepath - location of the csv file to open.
    Returns:
    --------
    pandas DataFrame containing three columns ["Deck 1 List", "Deck 2 List",
    "Deck 3 List"], each of which contains a set detailing each card in that
    decklist as detected by create_set.
    See also:
    ---------
    create_set
    """
    df = pd.read_csv(data_loc)
    df = df.dropna().reset_index().loc[:, ["Deck 1 List", "Deck 2 List", "Deck 3 List"]]
    df = df.applymap(create_set)

    # print(df)
    return df


def main():
    """Handle taking input and then producing output.
    """
    df = read_raw_data()
    all_cards = set()
    # print(all_cards)
    # raise Exception
    for index, row in df.iterrows():
        for deck in row:
            all_cards = all_cards | deck
    card_data_df = pd.DataFrame(all_cards, columns=["Card"]).sort_values(by="Card")
    card_data_df["Count"] = 0
    card_data_df["Decks"] = [set(x) for x in np.empty((len(card_data_df), 0)).tolist()]
    decks = df.values.flatten().tolist()
    for card in card_data_df.index:
        for i in range(len(decks)):
            if card_data_df.at[card, "Card"] in decks[i]:
                card_data_df.at[card, "Decks"] = card_data_df.at[card, "Decks"] | {i}
    card_data_df["Count"] = card_data_df["Decks"].apply(len)
    card_data_df.sort_values(
        by=["Count", "Card"], inplace=True, ascending=[False, True]
    )
    card_data_df = card_data_df.reset_index().drop(["index"], axis=1)
    print(card_data_df)
