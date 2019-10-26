from os.path import join

import regex as re

decklist_line = r"^\d+[^\S\n\r]+([\w \-,/]*[^\s(\n])"


def create_set(file):
    with open(join(decklist_directory, file)) as decklist:
        names = (
            set(re.findall(decklist_line, decklist.read(), flags=re.MULTILINE)) - basics
        )
    return names
