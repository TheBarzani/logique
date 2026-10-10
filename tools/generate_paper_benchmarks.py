"""Replay the original paper methodology through src/logique and compare costs."""

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
    return {
        "width": circuit.num_qubits
        + sum(max(0, g.num_ctrl_qubits - 2) for g in mcx[:-1]),
        "depth": circuit.depth(mcx_decomposition=True),
        "gates": len(circuit),
    }


def generate(output: Path | None = None, graphs: list[str] | None = None) -> Path:
    """Synthesize and verify each graph, save circuits, and compare all old/new costs."""
    reference = pd.read_csv(REFERENCE).set_index("benchmark")
    names = list(reference.index) if graphs is None else graphs
    reference = reference.loc[names]
    output = new_run_directory(output)
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
    rows, measured_rows = [], []
    for name in names:
        print(name, flush=True)
        original = read_dimacs(ROOT / "datasets/graphs/benchmarks" / f"{name}.col")
        problem = replace(original, precolored={})
        expression, variables = edge_coloring_expression(problem)
        result = synthesize_expression(expression, variables, executable=executable)
        (output / f"{name}.v").write_text(result.metadata["source_verilog"])
        bits = (problem.colors - 1).bit_length()
        # The edge-only oracle accepts all binary colors, including unused codes.
        encoding = encode_coloring(replace(problem, colors=1 << bits))
        sampled = encoding.input_count > 12
        phase = verify_kickback_oracle(
            result, encoding=encoding, sampled=sampled, seed=7
        )
        manifest["cases"].append(
            {"benchmark": name, "removed_precolors": dict(original.precolored), **phase}
        )
        preparation = QuantumCircuit(encoding.input_count)
        uniform = QuantumCircuit(bits)
        uniform.append(UniformSuperpositionGate(problem.colors), range(bits))
        uniform = uniform.decompose()
        for start in range(0, encoding.input_count, bits):
            preparation.compose(uniform, range(start, start + bits), inplace=True)
        reflection = QuantumCircuit(encoding.input_count)
        reflection.h(range(encoding.input_count))
        row = {
            "benchmark": name,
            "nodes": len(problem.vertices),
            "edges": len(problem.edges),
            "colors": problem.colors,
        }
        measured_row = dict(row)
        for method in ("vcgc", *(f"sb_{variant}" for variant in VARIANTS)):
            circuit = (
                kickback_grover_circuit(
                    result,
                    preparation=preparation,
                    reflection_preparation=reflection,
                )
                if method == "vcgc"
                else comparison_circuit(
                    problem,
                    method[3:],
                    iterations=1,
                    preserve_labels=True,
                    measure=True,
                )
            )
            with (output / f"{name}_{method}.qasm").open("w") as stream:
                dump(circuit, stream)
            row.update(
                {
                    f"{method}_{key}": value
                    for key, value in paper_metrics(circuit).items()
                }
            )
            if method == "vcgc":
                circuit.add_register(ClassicalRegister(encoding.input_count, "creg"))
                circuit.barrier()
                circuit.measure(
                    range(encoding.input_count), range(encoding.input_count)
                )
                with (output / f"{name}_vcgc_measured.qasm").open("w") as stream:
                    dump(circuit, stream)
            measured_row.update(
                {
                    f"{method}_{key}": value
                    for key, value in paper_metrics(circuit).items()
                }
            )
        rows.append(row)
        measured_rows.append(measured_row)
        pd.DataFrame(rows).to_csv(
            output / "benchmark_results.csv", index=False, lineterminator="\r\n"
        )
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
    current = pd.DataFrame(rows).set_index("benchmark")
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
