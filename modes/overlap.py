import regex as re
from os import listdir
from os.path import isfile, join

from config.CONFIG import CONFIG
from .functions import create_set_from_file

decklist_directory = CONFIG["decklist_directory"]


def check_no_duplicates(*args):
    duplicates = {
        f"{index1}, {index2}": args[index1] & args[index2]
        for index1 in range(len(args) - 1)
        for index2 in range(index1 + 1, len(args))
        if args[index1] & args[index2]
    }
    return duplicates


def calculate_overlap():
    decklists = [
        _file
        for _file in listdir(decklist_directory)
        if isfile(join(decklist_directory, _file))
    ]
    set_decklists = [create_set_from_file(decklist) for decklist in decklists]
    return check_no_duplicates(*set_decklists)
