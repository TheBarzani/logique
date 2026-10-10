"""Notebook illustrations of measured phase oracles and their actual mappings."""

from pathlib import Path

METHOD_LABELS = {
    "xag": "Specialized XAG",
    "aig_bennett": "AIG + Bennett",
    "xag_bennett": "XAG + Bennett",
    "klut_bennett": "4-LUT + Bennett",
    "best_fit": "Best-fit LHRS",
}


def show_svg(svg: str, *, height: int = 650) -> None:
    """Display a vector drawing at its readable natural size with scrolling."""
    from IPython.display import HTML, SVG, display

    display(
        HTML(
            f'<div style="overflow:auto;max-height:{height}px;border:1px solid #ddd;'
            'padding:12px;margin:12px 0">' + SVG(svg).data + "</div>"
        )
    )


def phase_walkthrough(result, directory: str | Path) -> None:
    """Show the source representation, mapping evidence, and full phase circuit.

    Circuit drawings add two stage-separation barriers to a copy; the measured
    oracle has no drawing barriers. The three-block overview is explanatory.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import pandas as pd
    from IPython.display import display, Markdown
    from .boolean import graphviz_graph, graph_stats, lut_table

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    md = result.metadata
    method = md["method"]
    title = METHOD_LABELS[method]
    graph = md["network"]
    suffix = (
        "underlying XAG (cell schedule below)"
        if method == "best_fit"
        else "exported network"
    )
    dot = graphviz_graph(graph, f"K3 · {title} · {suffix}")
    dot.save(str(directory / f"{method}_network.dot"))
    svg = dot.pipe(format="svg").decode()
    (directory / f"{method}_network.svg").write_text(svg)
    show_svg(svg)
    display(pd.DataFrame([graph_stats(graph)]))
    if method == "klut_bennett":
        display(
            Markdown(
                "**Actual LUT definitions.** Port 0 is the least-significant truth-table input."
            )
        )
        display(pd.DataFrame(lut_table(graph)))
    if md["steps"]:
        display(
            Markdown(
                "**Native mapping schedule for F.** This is the raw computation's "
                "schedule; the phase wrapper subsequently applies Z and the complete inverse F†. "
                "Node and leaf numbers refer to the exported logic graph."
            )
        )
        steps = pd.DataFrame(md["steps"])
        steps.index.name = "step"
        with pd.option_context("display.max_rows", None):
            display(steps)
        steps.to_csv(directory / f"{method}_mapping_steps.csv", index=True)
    else:
        display(
            Markdown(
                "**Specialized mapping.** XOR-aware synthesis produces the circuit below, "
                "including controlled Rx(±π) operations whose phases matter. This backend "
                "does not export a node-by-node schedule; none is inferred from gate order."
            )
        )
    if method == "best_fit":
        cells = [
            {
                "gate": i,
                "target wire": gate["target"],
                "control wires": gate["controls"],
                "control polarity": gate["polarity"],
                "truth (MSB first)": gate["truth"],
            }
            for i, gate in enumerate(md["gates"])
            if gate["kind"] == "lut"
        ]
        display(
            Markdown(
                "**Actual emitted LUT operations.** These refer to quantum wires, while "
                "the schedule above refers to logic nodes. The underlying XAG is not a drawing "
                "of the best-fit LUT covering. LUTs are expanded by PPRM synthesis."
            )
        )
        display(pd.DataFrame(cells))
    inputs, outputs = md["input_qubits"], md["output_qubits"]
    scratch = sorted(set(range(result.circuit.num_qubits)) - set(inputs) - set(outputs))
    display(
        pd.DataFrame(
            [
                {"role": "Color inputs (preserved)", "wires": inputs},
                {
                    "role": "Computed output (clean initially and finally)",
                    "wires": outputs,
                },
                {"role": "Scratch (clean initially and finally)", "wires": scratch},
            ]
        )
    )
    fig, ax = plt.subplots(figsize=(11, 2.5), constrained_layout=True)
    ax.set(xlim=(0, 10), ylim=(0, 2))
    ax.axis("off")
    ax.set_title(f"K3 · {title} · phase-oracle structure", loc="left", weight="bold")
    for x, label in (
        (0.6, "F\nCompute"),
        (3.9, f"Z on q{outputs[0]}\nMark"),
        (7.2, "F†\nUncompute"),
    ):
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.65),
                2.2,
                0.8,
                boxstyle="round,pad=0.1",
                facecolor="#e7eef7",
                edgecolor="#42607e",
            )
        )
        ax.text(x + 1.1, 1.05, label, ha="center", va="center")
    for x in (2.9, 6.2):
        ax.annotate(
            "", xy=(x + 0.8, 1.05), xytext=(x, 1.05), arrowprops={"arrowstyle": "->"}
        )
    ax.text(
        5,
        0.2,
        f"{len(inputs)} input qubits · {len(outputs) + len(scratch)} auxiliary qubits restored to zero",
        ha="center",
    )
    for ext in ("svg", "png"):
        fig.savefig(
            directory / f"{method}_overview.{ext}", dpi=150, bbox_inches="tight"
        )
    display(fig)
    plt.close(fig)
    annotated = result.circuit.copy()
    annotated.barrier(label="Mark")
    annotated.z(outputs[0])
    annotated.barrier(label="Uncompute")
    annotated.compose(result.circuit.inverse(), inplace=True)
    figure = annotated.draw("mpl", idle_wires=True, fold=-1)
    target = directory / f"{method}_phase_circuit.svg"
    figure.savefig(target, format="svg", bbox_inches="tight")
    plt.close(figure)
    display(
        Markdown(
            "**Complete logical phase oracle.** Scroll horizontally to inspect all gates. "
            "Two drawing-only barriers separate F, Z, and F†; they are absent from "
            "the measured and exported phase circuits."
        )
    )
    show_svg(target.read_text())
    display(pd.DataFrame([md["phase_validation"]]))


def phase_charts(run: str | Path, directory: str | Path) -> None:
    """Display and export consistently ordered logical and U/CX resource charts."""
    import matplotlib.pyplot as plt
    from IPython.display import display
    from .results import plot_results
    from logique.benchmarks.results import load_results

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    frame = load_results(run)
    for level in ("logical", "decomposed"):
        for metric in ("depth", "qubits", "gates"):
            values = frame.loc[frame.metric_level == level, metric]
            logarithmic = bool(
                (values > 0).all() and values.max() / values.min() >= 100
            )
            fig = plot_results(
                run,
                metric=metric,
                metric_level=level,
                method_labels=METHOD_LABELS,
                log=logarithmic,
            )
            ax = fig.axes[0]
            if logarithmic:
                ax.set_ylabel(ax.get_ylabel() + " (log scale)")
                ax.set_ylim(bottom=values.min() / 2)
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, which="major", alpha=0.2)
            ax.set_title(
                "Phase oracle · "
                + (
                    "as synthesized"
                    if level == "logical"
                    else "U/CX · optimization level 1 · seed 7"
                )
            )
            ax.legend(title="Method", fontsize=8)
            ax.tick_params(axis="x", labelrotation=35)
            for label in ax.get_xticklabels():
                label.set_ha("right")
            fig.tight_layout()
            for ext in ("png", "svg", "pdf"):
                fig.savefig(
                    directory / f"{level}_{metric}.{ext}", dpi=180, bbox_inches="tight"
                )
            display(fig)
            plt.close(fig)
