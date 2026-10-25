"""Optional synthesis backends, imported only when requested."""

from .native import METHODS

__all__ = [
    "METHODS",
    "synthesize",
    "synthesize_expression",
    "SynthesisResult",
    "BaselineComponents",
    "baseline_components",
]


def __getattr__(name):
    if name in ("BaselineComponents", "baseline_components"):
        from .saha_belletti import BaselineComponents, baseline_components

        return {
            "BaselineComponents": BaselineComponents,
            "baseline_components": baseline_components,
        }[name]
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
