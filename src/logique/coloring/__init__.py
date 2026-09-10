"""Graph-coloring inputs and deterministic Boolean encodings."""

from .model import ColoringProblem
from .dimacs import read_dimacs
from .encoding import ColoringEncoding, encode_coloring

__all__ = ["ColoringProblem", "ColoringEncoding", "read_dimacs", "encode_coloring"]
