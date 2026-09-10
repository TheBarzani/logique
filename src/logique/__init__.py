"""Graph-coloring and Boolean-oracle research, with optional quantum backends."""

from .coloring import ColoringProblem, ColoringEncoding, read_dimacs, encode_coloring

__version__ = "0.2.0"
__all__ = ["ColoringProblem", "ColoringEncoding", "read_dimacs", "encode_coloring"]
