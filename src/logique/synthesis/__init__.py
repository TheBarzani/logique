"""Optional synthesis backends, imported only when requested."""

from .native import METHODS

__all__ = ["METHODS", "synthesize", "SynthesisResult"]


def __getattr__(name):
    if name == "synthesize":
        from .api import synthesize

        return synthesize
    if name == "SynthesisResult":
        from .result import SynthesisResult

        return SynthesisResult
    raise AttributeError(name)
