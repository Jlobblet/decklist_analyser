import regex as re
from os import listdir
from os.path import isfile, join

from config.CONFIG import CONFIG

decklist_directory = CONFIG["decklist_directory"]
decklist_line = r"\d+ (?P<name>[\w -]+([^ (\n]))( \(.{3}\) \d{1,3})?"
basics = {"Plains", "Island", "Swamp", "Mountain", "Forest"}


def create_set(file):
    with open(join(decklist_directory, file)) as decklist:
        names = []
        for line in decklist:
            match = re.match(decklist_line, line)
            if match is not None:
                names.append(match.group("name"))
    names = set(names) - basics
    return names


def check_no_duplicates(*args):
    duplicates = dict(())
    for index1 in range(len(args)):
        for index2 in range(len(args)):
            if index1 < index2:
                intersection = args[index1] & args[index2]
                if intersection:
                    duplicates[str(index1) + ", " + str(index2)] = intersection
    return duplicates


def calculate_overlap():
    decklists = [
        file
        for file in listdir(decklist_directory)
        if isfile(join(decklist_directory, file))
    ]
    set_decklists = [create_set(decklist) for decklist in decklists]
    return check_no_duplicates(*set_decklists)
