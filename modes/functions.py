from os.path import join

import regex as re

decklist_line = r"^\d+[^\S\n\r]+([\w \-,/]*[^\s(\n])"
basics = {"Plains", "Island", "Swamp", "Mountain", "Forest"}


def create_set(text):
    names = (
        set(re.findall(decklist_line, text, flags=re.MULTILINE)) - basics
    )
    return names


def create_set_from_file(dir):
    with open(join(decklist_directory, dir)) as decklist:
        return create_set(decklist.read())
