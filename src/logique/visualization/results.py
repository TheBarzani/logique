"""Consistent plots for current and historical experiment tables."""

from pathlib import Path
from logique.benchmarks.results import load_results


def plot_results(
    source,
    *,
    metric: str = "qubits",
    output: str | Path | None = None,
    normalize: bool = False,
    log: bool = False,
):
    """Plot one comparable logical metric; optionally normalize to XAG/LOGIQUE."""
    import matplotlib.pyplot as plt

    if metric not in ("qubits", "gates", "depth", "seconds"):
        raise ValueError("Choose qubits, gates, depth, or seconds")
    frame = load_results(source)
    table = frame.pivot_table(
        index="benchmark", columns="method", values=metric, aggfunc="mean"
    )
    if normalize:
        baseline = "xag" if "xag" in table else "logique"
        if baseline not in table or (table[baseline] <= 0).any():
            raise ValueError(
                "Normalization requires a positive XAG or LOGIQUE baseline"
            )
        table = table.div(table[baseline], axis=0)
    fig, ax = plt.subplots(figsize=(max(7, len(table) * 1.1), 4))
    table.plot.bar(ax=ax, logy=log)
    ax.set_ylabel(f"Relative {metric}" if normalize else metric.capitalize())
    ax.set_xlabel("Benchmark")
    fig.tight_layout()
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
    return fig
