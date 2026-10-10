"""Optional synthesis backends, imported only when requested."""

from .native import METHODS

__all__ = ["METHODS", "synthesize", "synthesize_expression", "SynthesisResult"]


def __getattr__(name):
    if name == "synthesize":
        from .api import synthesize

        return synthesize
    if name == "SynthesisResult":
        from .result import SynthesisResult

        return SynthesisResult
    if name == "synthesize_expression":
        from .api import synthesize_expression

        return synthesize_expression
    raise AttributeError(name)
