import regex as re
from os import listdir
from os.path import isfile, join

from config.CONFIG import CONFIG

decklist_directory = CONFIG["decklist_directory"]
decklist_line = r"^\d+[^\S\n\r]+([\w \-,/]*[^ (\n])"
basics = {"Plains", "Island", "Swamp", "Mountain", "Forest"}


def create_set(file):
    with open(join(decklist_directory, file)) as decklist:
        names = set(re.findall(decklist_line, decklist.read(), flags=re.MULTILINE)) - basics
    return names


def check_no_duplicates(*args):
    duplicates = {
        str(index1) + ", " + str(index2): args[index1] & args[index2]
        for index1 in range(len(args) - 1)
        for index2 in range(index1 + 1, len(args))
        if args[index1] & args[index2]
    }
    return duplicates


def calculate_overlap():
    decklists = [
        file
        for file in listdir(decklist_directory)
        if isfile(join(decklist_directory, file))
    ]
    set_decklists = [create_set(decklist) for decklist in decklists]
    return check_no_duplicates(*set_decklists)
