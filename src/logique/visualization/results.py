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
    metric_level: str | None = None,
    method_labels: dict | None = None,
):
    """Plot one comparable logical metric; optionally normalize to XAG/LOGIQUE."""
    import matplotlib.pyplot as plt

    if metric not in ("qubits", "gates", "depth", "seconds"):
        raise ValueError("Choose qubits, gates, depth, or seconds")
    frame = load_results(source)
    if "metric_level" in frame:
        levels = frame["metric_level"].dropna().unique()
        if metric_level is None and len(levels) > 1:
            raise ValueError("Mixed metric levels: select metric_level explicitly")
        if metric_level is not None:
            frame = frame[frame["metric_level"] == metric_level]
    elif metric_level is not None:
        raise ValueError("Result table does not declare metric levels")
    if frame.empty:
        raise ValueError("No rows for the selected metric level")
    if "circuit_kind" in frame and frame["circuit_kind"].nunique() > 1:
        raise ValueError("Cannot compare different circuit kinds in one plot")
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
    table = table.reindex(index=frame["benchmark"].drop_duplicates())
    if method_labels:
        table = table.reindex(columns=[m for m in method_labels if m in table])
        table = table.rename(columns=method_labels)
    fig, ax = plt.subplots(figsize=(max(7, len(table) * 1.1), 4))
    table.plot.bar(ax=ax, logy=log)
    labels = {"qubits": "Width (total qubits)", "gates": "Gate count", "depth": "Depth"}
    ax.set_ylabel(
        f"Relative {metric}" if normalize else labels.get(metric, metric.capitalize())
    )
    if metric_level:
        ax.set_title(
            "Logical phase oracle"
            if metric_level == "logical" and "circuit_kind" in frame
            else metric_level.capitalize()
        )
    ax.set_xlabel("Benchmark")
    fig.tight_layout()
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
    return fig
