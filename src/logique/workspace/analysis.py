"""Conditional-state facts; these are not certified borrowing rewrites."""

import numpy as np
from logique.verification.classical import input_assignments, _apply_record
from logique.circuits.records import _qiskit_records


def workspace_analysis(result, *, expanded=False):
    """Find conjunction-derived facts on reachable states, not automatic rewrites.

    Intervals end conservatively at the next write to either the protecting
    qubit or a proposed borrowed qubit. No permission to borrow is implied.
    """
    md = result.metadata
    assignments = input_assignments(len(md["input_qubits"]))
    bits = np.zeros((md["num_qubits"], assignments.shape[1]), dtype=bool)
    bits[md["input_qubits"]] = assignments
    phases = np.ones(assignments.shape[1], dtype=complex)
    records = _qiskit_records(result.circuit) if expanded else md["gates"]
    workspace = sorted(
        set(range(bits.shape[0])) - set(md["input_qubits"]) - set(md["output_qubits"])
    )
    candidates, occupancy = [], []
    for index, rec in enumerate(records):
        clean_target = not bits[rec["target"]].any()
        _apply_record(bits, phases, rec)
        occupancy.append(int(np.any(bits[workspace], axis=1).sum()))
        if (
            rec["kind"] not in ("x", "rx")
            or len(rec["controls"]) < 2
            or not clean_target
        ):
            continue
        branch = bits[rec["target"]]
        if not branch.any():
            continue
        for q, known in zip(rec["controls"], rec["polarity"]):
            if not np.all(bits[q, branch] == known):
                continue
            end = next(
                (
                    j
                    for j in range(index + 1, len(records))
                    if records[j]["target"] in (q, rec["target"])
                ),
                len(records),
            )
            candidates.append(
                {
                    "after_gate": index,
                    "before_gate": end,
                    "condition": f"q{rec['target']} = 1",
                    "borrow_candidate": f"q{q}",
                    "known_value": int(known),
                    "proof": "exhaustive reachable states",
                }
            )
    return {
        "candidates": candidates,
        "occupancy": occupancy,
        "peak_nonzero_workspace": max(occupancy, default=0),
        "granularity": (
            "expanded Qiskit gates" if expanded else "native gate/LUT records"
        ),
        "scope": "Conjunction-derived facts only; consumption and restoration still require proof.",
    }
