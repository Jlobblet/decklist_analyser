import argparse

from modes import overlap, analysis

FUNCTION_MAP = {
    "overlap": overlap.calculate_overlap,
    "analysis": analysis.main,
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode", "-m", type=str, required=True, choices=FUNCTION_MAP.keys()
)
group = parser.add_mutually_exclusive_group()
group.add_argument("--profile", "-p", type=float, nargs=2)
group.add_argument("--resolution_parameter", "-r", type=float)
parser.add_argument("--graph", "-g", action="store_true")
parser.add_argument("--no-lands", action="store_true")

args = parser.parse_args()
ARG_MAP = {
    "overlap": tuple(),
    "analysis": (
        args.profile,
        args.resolution_parameter,
        args.graph,
        args.no_lands,
    ),
}
FUNCTION_MAP[args.mode](*ARG_MAP[args.mode])
