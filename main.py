import argparse

from modes import overlap, analysis

FUNCTION_MAP = {"overlap": overlap.calculate_overlap, "analysis": analysis.main}

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=FUNCTION_MAP.keys())

args = parser.parse_args()
print(FUNCTION_MAP[args.mode]())
