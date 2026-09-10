"""Run from any directory: python examples/coloring.py /path/to/input.col."""

import sys
from vcgc import read_dimacs, encode_coloring
from vcgc.synthesis import synthesize
from vcgc.verification import validate

if __name__ == "__main__":
    result = synthesize(encode_coloring(read_dimacs(sys.argv[1])))
    print(validate(result))
    print(result.summary())
