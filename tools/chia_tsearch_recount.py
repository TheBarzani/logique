"""Recount T_search = T_A + j(2T_A + T_S0 + T_O) on saved logical circuits.

Usage: uv run --no-sync python tools/chia_tsearch_recount.py OUT.json DIR STEM [STEM ...]
STEM is e.g. 000_R2_xag_j1_s7 (files DIR/STEM_{preparation,oracle,diffusion,search}_logical.qpy).
T_S0 is obtained from the diffusion circuit alone as T_diff - 2 T_A, and
independently by costing a freshly built zero-reflection (X-wall, multi-controlled Z).
"""

import json
import sys
from pathlib import Path

from qiskit import QuantumCircuit, qpy

from logique.benchmarks import costs


def load(path: Path) -> QuantumCircuit:
    with path.open("rb") as handle:
        return qpy.load(handle)[0]


def metrics(circuit: QuantumCircuit) -> dict:
    # Decompose MCX with a clean-ancilla-free policy so T counts are defined.
    lowered, _ = costs.decompose_mcx(circuit, "noaux_v24")
    ft = costs.ft_metrics(costs.clifford_t(lowered))
    return {k: ft[k] for k in ("t_count", "t_depth", "rotation_count")}


def signature(circuit: QuantumCircuit) -> list:
    return [
        (i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits))
        for i in circuit.data
    ]


def fresh_zero_reflection(width: int) -> QuantumCircuit:
    qc = QuantumCircuit(width)
    qc.x(range(width))
    qc.h(width - 1)
    qc.mcx(list(range(width - 1)), width - 1)
    qc.h(width - 1)
    qc.x(range(width))
    return qc


def recount(directory: Path, stem: str) -> dict:
    meta = json.loads((directory / f"{stem}.json").read_text())
    j = meta["iteration"]
    parts = {
        name: load(directory / f"{stem}_{name}_logical.qpy")
        for name in ("preparation", "oracle", "diffusion", "search")
    }
    t = {name: metrics(c)["t_count"] for name, c in parts.items()}
    t_a, t_o, t_d, t_search = (t[k] for k in ("preparation", "oracle", "diffusion", "search"))
    t_s0_from_diffusion = t_d - 2 * t_a
    # Independent S0: reflection on the preparation's width, built from scratch.
    t_s0_fresh = metrics(fresh_zero_reflection(parts["preparation"].num_qubits))["t_count"]
    predicted = t_a + j * (2 * t_a + t_s0_from_diffusion + t_o)
    # Structural check: search = A, then j x (O, diffusion) as instruction sequences.
    expected_sig = signature(parts["preparation"]) + j * (
        signature(parts["oracle"]) + signature(parts["diffusion"])
    )
    actual_sig = signature(parts["search"])
    return {
        "stem": stem,
        "j": j,
        "T_A": t_a,
        "T_O": t_o,
        "T_diffusion": t_d,
        "T_S0_from_diffusion": t_s0_from_diffusion,
        "T_S0_fresh_reflection_on_A_width": t_s0_fresh,
        "T_search_measured": t_search,
        "T_search_formula": predicted,
        "formula_matches": predicted == t_search,
        "structure_matches_instruction_sequence": expected_sig == actual_sig,
        "widths": {k: v.num_qubits for k, v in parts.items()},
    }


def main() -> int:
    out, directory, *stems = sys.argv[1:]
    rows = [recount(Path(directory), s) for s in stems]
    Path(out).write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
