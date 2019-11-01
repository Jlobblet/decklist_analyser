#    decklist_analyser - Magic: the Gathering analsyis with graph theory.
#    Copyright (C) 2019 John Blundell/Jlobblet
#    Contact: jlobblet-github@gmx.co.uk
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import sys
import datetime

import numpy as np
import pandas as pd
import igraph as ig
import louvain as lv
import matplotlib.pyplot as plt

from config.CONFIG import CONFIG
from .functions import (
    Logger,
    create_set,
    filter_sets,
    get_terminal_size,
)

columns, rows = get_terminal_size()
sys.stdout = Logger(
    CONFIG["log_location"].format(
        datetime.date.today().strftime("%b-%d-%Y")
    )
)


def read_raw_data(no_lands, data_loc=CONFIG["aggregate_data_loc"]):
    """Collect data from a csv file to locate decklists in and return
    DataFrame of decklists.
    Parameters:
    -----------
    data_loc: string or filepath - location of the csv file to open.
    Returns:
    --------
    pandas DataFrame containing three columns ["Deck 1 List",
    "Deck 2 List", "Deck 3 List"], each of which contains a set
    detailing each card in that decklist as detected by create_set.
    See also:
    ---------
    create_set
    """
    df = pd.read_csv(data_loc)
    df = (
        df.dropna()
        .reset_index()
        .loc[:, ["Deck 1 List", "Deck 2 List", "Deck 3 List"]]
    )
    df = df.applymap(lambda x: create_set(x, no_lands))

    return df


def create_card_df(all_cards, df):
    """Take the set of all cards and all decklists and create a
    DataFrame containing as columns Card, Number of Decks in and which
    decks those are.
    Parameters:
    -----------
    all_cards: set containing string for each card name detected for a
    give data set.

    df: pandas DataFrame containing all decklists.
    Returns:
    --------
    card_data_df: pandas DataFrame as described above.
    """
    card_data_df = pd.DataFrame(
        list(all_cards), columns=["Card"]
    ).sort_values(by="Card")
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
    """Take a DataFrame containing card name and deck membership and
    create from it an igraph Graph.
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as columns card name and
    the decks that each card belongs to as a set.
    Returns:
    --------
    G: igraph Graph containing each card and an edge between each card
    weighted by the number of decks they are in together, if nonzero.
    See also:
    ---------
    create_card_df: function that creates card_data_df.
    """
    G = ig.Graph()
    G.add_vertices(len(card_data_df.index))
    for card1 in range(len(card_data_df.index) - 1):
        for card2 in range(card1 + 1, len(card_data_df.index)):
            union = (
                card_data_df.at[card1, "Decks"]
                & card_data_df.at[card2, "Decks"]
            )
            if union:
                G.add_edge(card1, card2, weight=len(union))
    G.vs["label"] = card_data_df["Card"].tolist()
    G.vs["name"] = G.vs["label"]
    G.simplify(multiple=True, loops=True, combine_edges=sum)
    return G


def plot_number_clusters(card_data_df, G, resolution_range):
    """Take a card_data_df and the graph that represents it as well as
    a range of resolution parameters, and plot a graph showing how the
    number of clusters changes with resolution parameter.
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    G: igraph Graph representation of card_data_df.

    resolution_range: tuple of two values to vary resolution_parameter
    between.
    See also:
    ---------
    create_card_df: function that creates card_data_df.

    create_graph: function that creates G.
    """
    optimiser = lv.Optimiser()
    profile = optimiser.resolution_profile(
        G,
        lv.RBERVertexPartition,
        resolution_range=resolution_range,
        node_sizes=card_data_df["Count"].tolist(),
    )
    x = np.linspace(
        resolution_range[0], resolution_range[1], len(profile)
    )
    y = np.array([len(partition) for partition in profile])
    plt.plot(x, y)
    plt.xlabel("resolution_parameter")
    plt.ylabel("Number of clusters")
    plt.show()


def create_partition(card_data_df, G, resolution_parameter=1):
    """Take a card_data_df and the graph that represents it and create
    clusters based on lv.RBERVertexPartition.
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    G: igraph Graph representation of card_data_df.

    resolution_parameter: float to pass to the RBERVertexPartition as
    represented by γ in the quality function
      Q=∑(ij) (A_ij−γp)δ(σi,σj).
    Returns:
    --------
    partition: the partition created by lv.find_partition.

    clusters: the number of clusters detected.
    See also:
    ---------
    create_card_df: function that creates card_data_df.

    create_graph: function that creates G.

    https://louvain-igraph.readthedocs.io/en/latest/reference.html#rbervertexpartition:
    information on the algorithm used.
    """
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

    return partition, clusters


def multi_cluster(card_data_df, G, clusters):
    """Take cards that have a high exterior weight and put them into
    additional clusters.
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    G: igraph Graph representation of card_data_df.

    clusters: int number of clusters detected.
    See also:
    ---------
    create_card_df: function that creates card_data_df.

    create_graph: function that creates G.

    CONFIG["cluster_percentage"]: percentage of weighted connections for
    each node that must be a member of its clusters set.
    """
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
                    adjclus[cluster] += G.es.select(
                        _within=(card, adjcard)
                    )[0]["weight"] / len(clus2)

            if (
                np.sum(adjclus[clusfilter]) / np.sum(adjclus)
                < CONFIG["cluster_percentage"]
            ):
                adjclus[clusfilter] = 0
                card_data_df.at[card, "Cluster"].add(np.argmax(adjclus))
                changed = True
    # return card_data_df


def create_graphml(card_data_df, G, filepath):
    """Save the graph to a given location.
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    G: igraph Graph representation of card_data_df.

    filepath: string or filepath object to save the graph to.
    See also:
    ---------
    create_card_df: function that creates card_data_df.

    create_graph: function that creates G.
    """
    for edge in G.es:
        src_clus = card_data_df.at[edge.source, "Cluster"]
        tar_clus = card_data_df.at[edge.target, "Cluster"]
        if src_clus & tar_clus:
            edge["interior"] = 1
        else:
            edge["interior"] = 0
    G.save(filepath)


def classify_decklist(card_data_df, clusters, decklist):
    """
    Parameters:
    -----------
    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    clusters: int number of clusters detected.

    decklist: set containing string names of cards.
    Returns:
    --------
    decks: set containing clusters that contain a given percentage of
    members of decklist.
    See also:
    ---------
    create_card_df: function that creates card_data_df.

    CONFIG["deck_percentage"]: percentage of deck that has to be
    accounted for.
    """
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


def analysis(df, card_data_df, G, resolution_parameter, graph, label):
    """Create % breakdown of what decks are being played.
    Parameters:
    -----------
    df: pandas DataFrame containing all decklists.

    card_data_df: pandas DataFrame containing as colu.mns card name and
    the decks that each card belongs to as a set.

    G: igraph Graph representation of card_data_df.
    See also:
    ---------
    create_partition

    multi_cluster

    classify_decklist
    """
    partition, clusters = create_partition(
        card_data_df, G, resolution_parameter
    )
    if graph:
        ig.plot(partition, bbox=(4000, 2000))
        G.vs["cluster"] = [
            item
            for sublist in card_data_df["Cluster"].tolist()
            for item in sublist
        ]
        create_graphml(card_data_df, G, CONFIG["graphml_location"])
    multi_cluster(card_data_df, G, clusters)

    decks = [
        classify_decklist(card_data_df, clusters, deck)
        for deck in df.to_numpy().flatten()
    ]
    breakdown = [
        len([y for y in decks if x in y]) for x in range(clusters)
    ]
    names = []
    with pd.option_context("display.max_rows", None):
        print({x: breakdown[x] for x in range(len(breakdown))})
        print("=" * columns)
        print(f"Full df: {card_data_df}")
        print("=" * columns)
        print("Cluster overview:")
        for cluster in range(clusters):
            print(f"Cluster {cluster}")
            authorities = (
                filter_sets(card_data_df, {cluster}, "Cluster")
                .sort_values(by="Authority Score", ascending=False)[
                    "Card"
                ]
                .head()
                .reset_index(drop=True)
            )
            hubs = (
                filter_sets(card_data_df, {cluster}, "Cluster")
                .sort_values(by="Hub Score", ascending=False)["Card"]
                .head()
                .reset_index(drop=True)
            )
            top_count = (
                filter_sets(card_data_df, {cluster}, "Cluster")
                .sort_values(by="Count", ascending=False)["Card"]
                .head()
                .reset_index(drop=True)
            )
            print(
                pd.DataFrame(
                    {
                        "Count": top_count,
                        "Authority": authorities,
                        "Hubs": hubs,
                    }
                )
            )
            if label:
                names.append(input("Name: "))
            else:
                names.append(cluster)
            print("=" * columns)
    fig, ax = plt.subplots(
        figsize=(6, 3), subplot_kw={"aspect": "equal"}
    )
    wedges, texts = plt.pie(
        breakdown, counterclock=False, wedgeprops={"width": 0.5}
    )
    bbox_props = {
        "boxstyle": "square,pad=0.3",
        "fc": "w",
        "ec": "k",
        "lw": 0.72,
    }
    kw = {
        "arrowprops": {"arrowstyle": "-"},
        "bbox": bbox_props,
        "zorder": 0,
        "va": "center",
    }

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        # horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        horizontalalignment = "center"
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(
            f"{names[i]}\n{round(100 * breakdown[i]/sum(breakdown), 1)}%",
            xy=(x, y),
            xytext=(1.35 * np.sign(x), 1.4 * y),
            horizontalalignment=horizontalalignment,
            **kw,
        )

    plt.show()


def meta_analysis(card_data_df, G, profile):
    """Wrapper for plot_number_clusters."""
    if profile[0] >= profile[1]:
        raise ValueError(
            f"The first profile value must be smaller than the second.\nPassed values: {profile[0]}, {profile[1]}"
        )
    plot_number_clusters(card_data_df, G, (profile[0], profile[1]))


def main(profile, resolution_parameter, graph, no_lands, label):
    """Run the functions provided in order to produce summary of data.
    """
    df = read_raw_data(no_lands)
    all_cards = set()
    for index, row in df.iterrows():
        for deck in row:
            all_cards = all_cards | deck

    card_data_df = create_card_df(all_cards, df)
    G = create_graph(card_data_df)
    if profile:
        meta_analysis(card_data_df, G, profile)
    else:
        if resolution_parameter is None:
            resolution_parameter = 1
        analysis(
            df, card_data_df, G, resolution_parameter, graph, label
        )
