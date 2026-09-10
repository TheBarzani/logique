"""
VCGC: Vertex Coloring Problem with Quantum Computing

A Python package for solving vertex coloring problems using quantum computing
techniques, including graph generation, boolean function synthesis, and
quantum circuit construction.
"""

# Import main classes and functions that users should have direct access to
from .network import VCPNetwork
from .boolean import BooleanFunction
from .dimacs import read_dimacs
from .synthesis import Synthesizer

__version__ = "0.1.0"
__author__ = "Ismael Barzani"

# Define what gets imported with "from vcgc import *"
__all__ = [
    "VCPNetwork",
    "BooleanFunction", 
    "read_dimacs",
    "Synthesizer",
]