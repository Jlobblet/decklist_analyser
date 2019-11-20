HELP = {
    "mode": """Whether the program runs on overlap or analysis:\n
    overlap - Discover all files in the decklist_directory specified by CONFIG.py and return the cards that they share.\n
    analysis - Cluster decklists""",
    "all": "Check for overlap in all decks of specifed aggregate location.",
    "profile": "Run a profile and create a graph of number of clusters against resolution_parameter. The lower and upper bounds are specified after the parameter is passed. This disables the standard output.",
    "rp": "Set the resolution_parameter used in the program to the value passed.",
    "graph": "Produce a visual for the clusters and a .graphml file in graphml_location (config).",
    "no-lands": "Remove all land cards from the decks to produce clusters of only nonland cards.",
    "label": "Ask the user for names for each cluster detected",
    "colour": "Ask the user for colours to plot each cluster's wedge in.",
    "init": "Where initial card cluster membership is stored.",
}
