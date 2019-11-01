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

import argparse

from config.help import HELP
from modes import overlap, analysis

FUNCTION_MAP = {
    "overlap": overlap.calculate_overlap,
    "analysis": analysis.main,
}

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(
    title="mode", help=HELP["mode"], required=True, dest="mode"
)
overlap_parser = subparsers.add_parser("overlap")
# overlap_parser.add("overlap", action="store_true")
analysis_parser = subparsers.add_parser("analysis")
group = analysis_parser.add_mutually_exclusive_group()
group.add_argument(
    "--profile", "-p", type=float, nargs=2, help=HELP["profile"]
)
group.add_argument(
    "--resolution_parameter", "-r", type=float, help=HELP["rp"]
)
analysis_parser.add_argument(
    "--graph", "-g", action="store_true", help=HELP["graph"]
)
analysis_parser.add_argument(
    "--no-lands", action="store_true", help=HELP["no-lands"]
)
analysis_parser.add_argument("--label", action="store_true")

args = parser.parse_args()
ARG_MAP = {
    "overlap": tuple(),
    "analysis": (
        args.profile,
        args.resolution_parameter,
        args.graph,
        args.no_lands,
        args.label,
    ),
}
print(
    """
    decklist_analyser  Copyright (C) 2019 John Blundell/Jlobblet
    This program comes with ABSOLUTELY NO WARRANTY; license is included
    as LICENSE.
    """
)
FUNCTION_MAP[args.mode](*ARG_MAP[args.mode])
