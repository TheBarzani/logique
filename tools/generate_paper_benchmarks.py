"""Rebuild the paper's nine-graph comparison using src/logique, without precolors."""

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
from qiskit import QuantumCircuit
from qiskit.qasm3 import dump
from logique.coloring import read_dimacs, encode_coloring
from logique.synthesis import synthesize
from logique.synthesis.saha_belletti import comparison_circuit
from logique.circuits.grover import grover_circuit
from logique.verification import validate, verify_phase_oracle
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
        "precolors": "removed for all five methods",
        "preparation": "all bitstrings",
        "iterations": 1,
        "depth_model": "logique.mcx_tree_bound.v1",
        "status": "running",
        "cases": [],
    }
    rows = []
    for name in names:
        print(name, flush=True)
        original = read_dimacs(ROOT / "datasets/graphs/benchmarks" / f"{name}.col")
        problem = replace(original, precolored={})
        encoding = encode_coloring(problem)
        encoding.write_verilog(output / f"{name}.v")
        result = synthesize(encoding, "xag", executable=executable)
        sampled = encoding.input_count > 12
        validate(result, sampled=sampled, seed=7)
        phase = verify_phase_oracle(result, encoding=encoding, sampled=sampled, seed=7)
        manifest["cases"].append(
            {"benchmark": name, "removed_precolors": dict(original.precolored), **phase}
        )
        row = {"benchmark": name}
        for method in ("vcgc", *(f"sb_{variant}" for variant in VARIANTS)):
            circuit = (
                grover_circuit(result, iterations=1)
                if method == "vcgc"
                else comparison_circuit(problem, method[3:], iterations=1)
            )
            with (output / f"{name}_{method}.qasm").open("w") as stream:
                dump(circuit, stream)
            row.update(
                {
                    f"{method}_{key}": value
                    for key, value in paper_metrics(circuit).items()
                }
            )
        rows.append(row)
        pd.DataFrame(rows).to_csv(output / "benchmark_results.csv", index=False)
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
    current = pd.DataFrame(rows).set_index("benchmark")
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
