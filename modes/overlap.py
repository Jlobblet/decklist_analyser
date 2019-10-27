from os import listdir
from os.path import isfile, join

from config.CONFIG import CONFIG
from .functions import create_set_from_file

decklist_directory = CONFIG["decklist_directory"]
basics = CONFIG["basics"]


def check_no_duplicates(*args):
    """Take any number of sets and return the duplicates, by pair, in all of the sets.

    *args is any number of sets containing any values. The union of each pair
    of sets is generated and if nonempty appended to a dictionary. These are
    numbered by the order the sets were provided in and then returned.
    Parameters:
    -----------
    *args: sets to check for duplicates.
    Returns:
    --------
    duplicates: dict - keys are string of the form f"{index1}, {index2}" and
    values are the union of those sets, if nonempty. Empty unions are omitted.
    """
    duplicates = {
        f"{index1}, {index2}": args[index1] & args[index2]
        for index1 in range(len(args) - 1)
        for index2 in range(index1 + 1, len(args))
        if args[index1] & args[index2]
    } - basics
    return duplicates


def calculate_overlap():
    """Open all the files in a given directory and then check all of them for
    duplicate cards with each other.
    Returns:
    ------
    duplicates: dict - keys are string of the form f"{index1}, {index2}" and
    values are the union of those sets, if nonempty. Empty unions are omitted.
    See also:
    ------
    check_no_duplicates
    """
    decklists = [
        _file
        for _file in listdir(decklist_directory)
        if isfile(join(decklist_directory, _file))
    ]
    set_decklists = [create_set_from_file(decklist) for decklist in decklists]
    print(check_no_duplicates(*set_decklists))
