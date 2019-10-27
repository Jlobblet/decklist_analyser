import sys
import datetime

import numpy as np
import pandas as pd
import igraph as ig
import louvain as lv
import matplotlib.pyplot as plt

from config.CONFIG import CONFIG
from .functions import Logger, create_set, filter_sets

sys.stdout = Logger(
    CONFIG["log_location"].format(datetime.date.today().strftime("%b-%d-%Y"))
)
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


def create_card_df(all_cards, df):
    card_data_df = pd.DataFrame(list(all_cards), columns=["Card"]).sort_values(
        by="Card"
    )
    card_data_df.set_index("Card", inplace=True)
    card_data_df["Count"] = 0
    card_data_df["Decks"] = [set() for _ in range(len(card_data_df))]

    decks = df.values.flatten().tolist()

    for i in range(len(decks)):
        for card in decks[i]:
            card_data_df.at[card, "Decks"].add(i)

    card_data_df["Count"] = card_data_df["Decks"].apply(len)
    card_data_df.sort_values(
        by=["Count", "Card"], inplace=True, ascending=[False, True]
    )
    card_data_df.reset_index(inplace=True)
    return card_data_df


def create_graph(card_data_df):
    G = ig.Graph()
    G.add_vertices(len(card_data_df.index))
    for card1 in range(len(card_data_df.index) - 1):
        for card2 in range(card1 + 1, len(card_data_df.index)):
            union = card_data_df.at[card1, "Decks"] & card_data_df.at[card2, "Decks"]
            if union:
                G.add_edge(card1, card2, weight=len(union))
    G.vs["label"] = card_data_df["Card"].tolist()
    G.vs["name"] = G.vs["label"]
    G.simplify(multiple=True, loops=True, combine_edges=sum)
    return G


def plot_number_clusters(card_data_df, G, resolution_range):
    optimiser = lv.Optimiser()
    profile = optimiser.resolution_profile(
        G,
        lv.RBERVertexPartition,
        resolution_range=resolution_range,
        node_sizes=card_data_df["Count"].tolist(),
    )
    x = np.linspace(resolution_range[0], resolution_range[1], len(profile))
    y = np.array([len(partition) for partition in profile])
    plt.plot(x, y)
    plt.xlabel("resolution_parameter")
    plt.ylabel("Number of clusters")
    plt.show()


def create_partition(card_data_df, G, resolution_parameter=1):
    partition = lv.find_partition(
        G,
        lv.RBERVertexPartition,
        weights="weight",
        resolution_parameter=resolution_parameter,
        node_sizes=card_data_df["Count"].tolist(),
    )

    clusters = 0
    card_data_df["Cluster"] = [set() for _ in card_data_df.index]
    card_data_df["Hub Score"] = G.hub_score("weight")
    card_data_df["Authority Score"] = G.authority_score("weight")

    for cluster in partition:
        for card in cluster:
            card_data_df.at[card, "Cluster"].add(clusters)
        clusters += 1

    G.vs["cluster"] = card_data_df["Cluster"].tolist()
    return partition, clusters


def multi_cluster(card_data_df, G, clusters):
    changed = True

    while changed:
        changed = False

        copy_df = card_data_df.copy()

        adjlist = G.get_adjlist()
        for card in copy_df.index:
            adjlist_card = adjlist[card]
            clus1 = copy_df.at[card, "Cluster"]
            clusfilter = [c in clus1 for c in range(clusters)]
            adjclus = np.zeros(clusters)
            # adjclus[clusfilter] = len(adjlist_card)

            for adjcard in adjlist_card:
                clus2 = copy_df.at[adjcard, "Cluster"]
                for cluster in clus2:
                    adjclus[cluster] += G.es.select(_within=(card, adjcard))[0][
                        "weight"
                    ] / len(clus2)

            if (
                np.sum(adjclus[clusfilter]) / np.sum(adjclus)
                < CONFIG["cluster_percentage"]
            ):
                adjclus[clusfilter] = 0
                card_data_df.at[card, "Cluster"].add(np.argmax(adjclus))
                changed = True
    # return card_data_df


def create_graphml(card_data_df, G, filepath):
    for edge in G.es:
        src_clus = card_data_df.at[edge.source, "Cluster"]
        tar_clus = card_data_df.at[edge.target, "Cluster"]
        if src_clus & tar_clus:
            edge["interior"] = 1
        else:
            edge["interior"] = 0
    G.save(filepath)


def classify_decklist(card_data_df, clusters, decklist):
    hits = np.zeros(clusters)
    copy_df = card_data_df.copy().set_index("Card")
    for card in decklist:
        card_clusters = copy_df.at[card, "Cluster"]
        for cluster in card_clusters:
            hits[cluster] += 1
    hits /= sum(hits)
    decks = set()
    deck_percentage = 0
    while deck_percentage < CONFIG["deck_percentage"]:
        cat = hits.argmax()
        decks.add(cat)
        deck_percentage += hits[cat]
        hits[cat] = 0
    return decks


def main():
    """Handle taking input and then producing output.
    """
    df = read_raw_data()
    all_cards = set()
    for index, row in df.iterrows():
        for deck in row:
            all_cards = all_cards | deck

    card_data_df = create_card_df(all_cards, df)
    G = create_graph(card_data_df)
    # plot_number_clusters(card_data_df, G, (0, 2))
    partition, clusters = create_partition(card_data_df, G, 1.5)
    multi_cluster(card_data_df, G, clusters)
    # ig.plot(partition, bbox=(4000, 2000))

    # with pd.option_context("display.max_rows", None):
    #     print(filter_sets(card_data_df, {0, 4}, "Cluster")["Card"])
    #     print(card_data_df)

    decks = [
        classify_decklist(card_data_df, clusters, deck)
        for deck in df.to_numpy().flatten()
    ]
    breakdown = [len([y for y in decks if x in y]) for x in range(clusters)]
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    wedges, texts = plt.pie(
        breakdown,
        labels=[
            f"{round(100 * breakdown[x]/sum(breakdown), 1)}%" for x in range(clusters)
        ],
        counterclock=False,
    )
    ax.legend(
        wedges,
        [f"{x}" for x in range(clusters)],
        title="Predominant Clusters",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
    )
    with pd.option_context("display.max_rows", None):
        print("Cluster overview:")
        for cluster in range(clusters):
            print(f"Cluster {cluster}")
            authorities = (
                filter_sets(card_data_df, {cluster}, "Cluster")
                .sort_values(by="Authority Score")["Card"]
                .head()
                .reset_index(drop=True)
            )
            print(pd.DataFrame({"Top Cards": authorities}))
            print("=" * 20)
    plt.show()
