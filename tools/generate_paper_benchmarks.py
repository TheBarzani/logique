"""Regenerate paper circuits through src/logique and compare historical costs.

Run all nine graphs, or use ``--graphs K3`` for a small example. Each run saves
circuits, verification details, historical metrics, and an all-measured comparison.
"""

# ruff: noqa: E402

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
# Import the maintained checkout directly, rather than an installed copy.
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit.library.data_preparation.state_preparation import (
    UniformSuperpositionGate,
)
from qiskit.qasm3 import dump
from logique.coloring import read_dimacs, encode_coloring, edge_coloring_expression
from logique.synthesis import synthesize_expression
from logique.synthesis.saha_belletti import comparison_circuit
from logique.circuits.grover import kickback_grover_circuit
from logique.verification import verify_kickback_oracle
from logique.benchmarks.runner import new_run_directory
from logique.benchmarks.provenance import environment, checkout_revision

REFERENCE = ROOT / "experiments/manuscript/legacy/data/output/benchmark_results.csv"
VARIANTS = ("original", "minimal", "simple", "balanced")


def paper_metrics(circuit: QuantumCircuit) -> dict[str, int]:
    """Keep the original MCX width allowance, tree-weighted depth, and gate count."""
    mcx = [gate.operation for gate in circuit.data if gate.operation.name == "mcx"]

    # Historical width sums the n-2 ancillas for each MCX, excluding the last
    # MCX (assumed to belong to diffusion). This is an allowance, not allocated wires.
    extra_ancillas = sum(max(0, gate.num_ctrl_qubits - 2) for gate in mcx[:-1])
    return {
        "width": circuit.num_qubits + extra_ancillas,
        # The local Qiskit patch weights MCX by ceil(log2(n)) for n controls.
        "depth": circuit.depth(mcx_decomposition=True),
        # Match the original instruction count, including barriers and measurements.
        "gates": len(circuit),
    }


def generate(output: Path | None = None, graphs: list[str] | None = None) -> Path:
    """Synthesize and verify each graph, save circuits, and compare all old/new costs."""

    # Archived numbers supply graph names and comparison targets only. All new
    # metrics below come from freshly synthesized circuits.
    reference = pd.read_csv(REFERENCE).set_index("benchmark")
    names = list(reference.index) if graphs is None else graphs
    reference = reference.loc[names]
    output = new_run_directory(
        output, description="paper-benchmarks", root=ROOT / "dump"
    )
    executable = os.environ.get(
        "LOGIQUE_NATIVE_EXECUTABLE",
        str(ROOT / "external/native/boolean_synthesis/build/boolean_synthesis"),
    )
    manifest = {
        "implementation": "src/logique",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": environment(),
        "checkout": checkout_revision(ROOT),
        "precolors": "ignored as in the original generator",
        "encoding": "edge inequalities only; original expression-tree frontend",
        "preparation": "VCGC: valid-color superposition; baselines: Hadamards",
        "oracle": "single XAG application with output in |minus>; internal cleanup",
        "baseline_labels": "original one-based labels, without normalization",
        "measurements": {
            "benchmark_results.csv": "historical: VCGC unmeasured, baselines measured",
            "measurement_consistent_results.csv": "all five methods measured",
        },
        "iterations": 1,
        "depth_model": "logique.mcx_tree_bound.v1",
        "status": "running",
        "cases": [],
    }
    historical_rows, measured_rows = [], []
    for name in names:
        print(name, flush=True)
        original = read_dimacs(ROOT / "datasets/graphs/benchmarks" / f"{name}.col")

        # Replay the original predicate: edge inequalities, without precolors or
        # constraints excluding unused binary color codes.
        problem = replace(original, precolored={})
        expression, variables = edge_coloring_expression(problem)
        synthesis = synthesize_expression(expression, variables, executable=executable)
        (output / f"{name}.v").write_text(synthesis.metadata["source_verilog"])

        # Verification must accept the same unused codes as the edge-only oracle.
        bits_per_color = (problem.colors - 1).bit_length()
        reference_encoding = encode_coloring(
            replace(problem, colors=1 << bits_per_color)
        )
        input_count = reference_encoding.input_count

        # Exhaustively check small inputs; use a fixed sample for larger graphs.
        # Both output-target initializations are checked for clean XOR action.
        verification = verify_kickback_oracle(
            synthesis, encoding=reference_encoding, sampled=input_count > 12, seed=7
        )
        manifest["cases"].append(
            {
                "benchmark": name,
                "removed_precolors": dict(original.precolored),
                **verification,
            }
        )

        # Initially, VCGC gives each vertex a uniform superposition of valid colors.
        preparation = QuantumCircuit(input_count)
        vertex_preparation = QuantumCircuit(bits_per_color)
        vertex_preparation.append(
            UniformSuperpositionGate(problem.colors), range(bits_per_color)
        )
        vertex_preparation = vertex_preparation.decompose()
        for start in range(0, input_count, bits_per_color):
            preparation.compose(
                vertex_preparation, range(start, start + bits_per_color), inplace=True
            )

        # Historical diffusion instead reflects about the full binary superposition,
        # including unused codes. Preserve this distinction from initial preparation.
        reflection_preparation = QuantumCircuit(input_count)
        reflection_preparation.h(range(input_count))

        historical_row = {
            "benchmark": name,
            "nodes": len(problem.vertices),
            "edges": len(problem.edges),
            "colors": problem.colors,
        }
        measured_row = dict(historical_row)
        for method in ("vcgc", *(f"sb_{variant}" for variant in VARIANTS)):
            if method == "vcgc":

                # One oracle application with its output in |minus> supplies phase
                # kickback. The XAG cleans its workspace internally; no outer inverse.
                circuit = kickback_grover_circuit(
                    synthesis,
                    preparation=preparation,
                    reflection_preparation=reflection_preparation,
                )
            else:

                # Keep the original one-based labels, including their mismatch with
                # the baseline's indexing. Its Hadamard preparation is unchanged.
                circuit = comparison_circuit(
                    problem,
                    method[3:],
                    iterations=1,
                    preserve_labels=True,
                    measure=True,
                )

            # The original table measured baselines but left VCGC unmeasured.
            with (output / f"{name}_{method}.qasm").open("w") as stream:
                dump(circuit, stream)
            historical_row.update(
                {
                    f"{method}_{key}": value
                    for key, value in paper_metrics(circuit).items()
                }
            )
            if method == "vcgc":

                # Add the same final barrier and input measurements as the baselines
                # for the separate, measurement-consistent comparison.
                circuit.add_register(ClassicalRegister(input_count, "creg"))
                circuit.barrier()
                circuit.measure(range(input_count), range(input_count))
                with (output / f"{name}_vcgc_measured.qasm").open("w") as stream:
                    dump(circuit, stream)
            measured_row.update(
                {
                    f"{method}_{key}": value
                    for key, value in paper_metrics(circuit).items()
                }
            )
        historical_rows.append(historical_row)
        measured_rows.append(measured_row)

        # Save completed graphs as we go; CRLF matches the historical CSV format.
        pd.DataFrame(historical_rows).to_csv(
            output / "benchmark_results.csv", index=False, lineterminator="\r\n"
        )
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # Compare each freshly computed metric with the corresponding archived value.
    current = pd.DataFrame(historical_rows).set_index("benchmark")
    current = current[
        [
            column
            for column in current
            if column.endswith(("_width", "_depth", "_gates"))
        ]
    ]
    comparison = pd.concat(
        [
            reference[current.columns].stack().rename("old"),
            current.stack().rename("new"),
        ],
        axis=1,
    )
    comparison["delta"] = comparison["new"] - comparison["old"]
    comparison["exact"] = comparison["delta"] == 0
    comparison.index.names = ["benchmark", "metric"]
    comparison.to_csv(output / "comparison.csv")
    pd.DataFrame(measured_rows).to_csv(
        output / "measurement_consistent_results.csv", index=False
    )
    manifest["comparison"] = {
        "exact": bool(comparison.exact.all()),
        "values_compared": len(comparison),
        "values_matching": int(comparison.exact.sum()),
    }
    manifest["status"] = "complete"
    (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{comparison.exact.sum()}/{len(comparison)} metrics match: {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--graphs", nargs="+", help="Omit to run all nine paper graphs")
    arguments = parser.parse_args()
    generate(arguments.output, arguments.graphs)
