import argparse

from modes import overlap, analysis

FUNCTION_MAP = {"overlap": overlap.calculate_overlap, "analysis": lambda x: None}

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("mode", choices=FUNCTION_MAP.keys())

args = parser.parse_args()
print(FUNCTION_MAP[args.mode]())
