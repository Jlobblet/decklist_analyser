import sys
from os.path import join

import regex as re

from config.CONFIG import CONFIG

decklist_directory = CONFIG["decklist_directory"]
decklist_line_1 = r"^([\w '\-,/]*[^\s(\n]) x\d+"
decklist_line_2 = r"^\d+x?[^\S\n\r]+([\w '\-,/]*[^\s(\n])"


class Logger(object):
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a+")

    def __del__(self):
        self.log.close()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def create_set(text):
    """Take a multiline string and return a set of card names detected.

    Parameters:
    -----------
    text: str - text to analyse to find card names in.
    Returns:
    --------
    names: set - unordered set of detected names.
    """
    text = re.sub("['`]", "'", text)
    names = set(re.findall(decklist_line_1, text, flags=re.MULTILINE)) | set(
        re.findall(decklist_line_2, text, flags=re.MULTILINE)
    )
    names = {name.title() for name in names}
    return names


def create_set_from_file(dir):
    """Wrapper for create_set that takes a file path to read and run create_set on.

    Parameters:
    ------
    dir: string or filepath object to look for decklists in. This is the file
    itself rather than the containing directory and should be relative to the
    decklist_directory as set in CONFIG.
    """
    with open(join(decklist_directory, dir)) as decklist:
        return create_set(decklist.read())


def filter_sets(df, filter, field, whitelist=True):
    if whitelist:
        mask = df[field].map(lambda x: x & filter != set())
    else:
        mask = df[field].map(lambda x: x & filter == set())
    return df[mask]
