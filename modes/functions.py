from os.path import join

import regex as re

decklist_line_1 = r"^([\w '\-,/]*[^\s(\n]) x\d+"
decklist_line_2 = r"^\d+x?[^\S\n\r]+([\w '\-,/]*[^\s(\n])"
basics = {"Plains", "Island", "Swamp", "Mountain", "Forest"}


def create_set(text):

    text = re.sub("['`]", "'", text)

    names = (
        set(re.findall(decklist_line_1, text, flags=re.MULTILINE)) | set(re.findall(decklist_line_2, text, flags=re.MULTILINE)) - basics
    )

    names = {name.title() for name in names}

    return names


def create_set_from_file(dir):
    with open(join(decklist_directory, dir)) as decklist:
        return create_set(decklist.read())
