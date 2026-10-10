"""Plot freshly generated paper costs using the maintained plotting code."""

# ruff: noqa: E402

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from logique.visualization.results import plot_results


def plot(directory: Path) -> None:
    """Save the three log-scale benchmark comparisons next to the fresh CSV."""
    import matplotlib.pyplot as plt

    labels = {
        "logique": "Logique (XAG)",
        "sb_original": "Saha original",
        "sb_minimal": "Belletti minimal",
        "sb_simple": "Belletti simple",
        "sb_balanced": "Belletti balanced",
    }
    for metric, ylabel in (
        ("qubits", "Width with historical MCX allowance"),
        ("depth", "MCX tree-weighted depth estimate"),
        ("gates", "Logical gate count"),
    ):
        figure = plot_results(
            directory / "benchmark_results.csv",
            metric=metric,
            log=True,
            method_labels=labels,
        )
        figure.axes[0].set_ylabel(ylabel)
        figure.savefig(directory / f"{metric}_comparison_log.png", dpi=300)
        plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    plot(parser.parse_args().directory)
