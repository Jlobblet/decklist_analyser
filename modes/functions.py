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
import os
from os.path import join

import regex as re
import pandas as pd

from config.CONFIG import CONFIG
from config.lands import LANDS

decklist_directory = CONFIG["decklist_directory"]
decklist_line_1 = r"^([\w '\-,/]*[^\s(\n]) x\d+"
decklist_line_2 = r"^\d+x?[^\S\n\r]+([\w '\-,/]*[^\s(\n])"


class Logger(object):
    """Object that writes to both sys.stdout and a file.
    Parameters:
    -----------
    filepath: location of log file to write to.
    """

    def __init__(self, filepath):
        """Instantiate the class."""
        self.terminal = sys.stdout
        self.log = open(filepath, "a+")

    def __del__(self):
        """Ensure the file is closed on deletion."""
        self.log.close()

    def write(self, message):
        """Write a message to both the terminal and file."""
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """Flush the terminal and file."""
        self.terminal.flush()
        self.log.flush()


def get_terminal_size(fallback=(72, 24)):
    """Attempt to determine the size of the terminal window.
    Parameters:
    -----------
    fallback: tuple of two ints to return if the terminal size cannot be
    determined.
    Returns:
    --------
    columns: int number of columns in the terminal window, if detected,
    else first fallback value.

    rows: int number of row in the terminal window, if detected, else
    second fallback value.
    """
    for i in range(0, 3):
        try:
            columns, rows = os.get_terminal_size(i)
        except OSError:
            continue
        break
    else:
        columns, rows = fallback
    return columns, rows


def create_set(text, no_lands=False):
    """Take a multiline string and return a set of card names detected.

    Parameters:
    -----------
    text: str - text to analyse to find card names in.

    no_lands: bool whether to eliminate all lands (True) or not.
    Returns:
    --------
    names: set - unordered set of detected names.
    """
    text = re.sub("['`]", "'", text)
    names = set(
        re.findall(decklist_line_1, text, flags=re.MULTILINE)
    ) | set(re.findall(decklist_line_2, text, flags=re.MULTILINE))
    names = {name.title().replace("'S", "'s") for name in names}
    if no_lands:
        names -= names & LANDS
    return names


def create_set_from_file(dir):
    """Wrapper for create_set that takes a file path to read and run
    create_set on.

    Parameters:
    ------
    dir: string or filepath object to look for decklists in. This is the
    file itself rather than the containing directory and should be
    decklist_directory as set in CONFIG.
    """
    with open(join(decklist_directory, dir)) as decklist:
        return create_set(decklist.read())


def filter_sets(df, filter, field, whitelist=True):
    """Take a dataframe and return it filtered based on whether a field
    of sets contains values in filter if whitelist is True, or not in
    filter if whitelist=False.
    Parameters:
    -----------
    df: pandas DataFrame to filter.

    filter: set containing values to filter on.

    field: string name of field to filter.

    whitelist: bool whether to exclude values not in filter (True) or
    exclude values in filter (False).
    Returns:
    --------
    df: pandas DataFrame with filter applied.
    """
    if whitelist:
        mask = df[field].map(lambda x: x & filter != set())
    else:
        mask = df[field].map(lambda x: x & filter == set())
    return df[mask]


def read_raw_data(
    no_lands, names=False, data_loc=CONFIG["aggregate_data_loc"]
):
    """Collect data from a csv file to locate decklists in and return
    DataFrame of decklists.
    Parameters:
    -----------
    no_lands: bool whether to exclude lands (True) or not (False).

    data_loc: string or filepath - location of the csv file to open.
    Returns:
    --------
    pandas DataFrame containing three columns ["Deck 1 List",
    "Deck 2 List", "Deck 3 List"], each of which contains a set
    detailing each card in that decklist as detected by create_set.
    Raises:
    -------
    ValueError: one of the column names could not be found in the
    DataFrame
    See also:
    ---------
    create_set
    """
    if names:
        cols = [
            "Team Name",
            "Deck 1 List",
            "Deck 2 List",
            "Deck 3 List",
        ]
    else:
        cols = ["Deck 1 List", "Deck 2 List", "Deck 3 List"]
    df = pd.read_csv(data_loc)
    for col_name in cols:
        if col_name not in df.columns:
            raise ValueError(f"Column {col_name} could not be found in csv - check headers are named appropriately.")
    df = df.dropna().reset_index().loc[:, cols]
    df[["Deck 1 List", "Deck 2 List", "Deck 3 List"]] = df[
        ["Deck 1 List", "Deck 2 List", "Deck 3 List"]
    ].applymap(lambda x: create_set(x, no_lands))

    return df
