"""Coherent phase-oracle checks without exponential workspace statevectors."""

import numpy as np
from logique.circuits.records import _qiskit_records
from .classical import _apply_record, input_assignments, truth_outputs


def verify_phase_oracle(
    result,
    *,
    encoding=None,
    circuit=None,
    sampled: bool = False,
    samples: int = 256,
    seed: int = 7,
) -> dict:
    """Check actual circuit phases and restoration on initially clean workspace.

    With an encoding, the reference is the independent graph predicate. Otherwise
    it is the imported Boolean network's first output. Exhaustive checks prove
    the coherent action on this input subspace by linearity; sampling is not a
    proof. X, controlled-X, Z and controlled Rx(+/-pi) gates are supported.
    """
    if samples < 1:
        raise ValueError("samples must be positive")
    md = result.metadata
    inputs = md["input_qubits"]
    n = len(inputs)
    if encoding is not None and encoding.input_count != n:
        raise ValueError("Coloring encoding does not match the input register")
    assignments = (
        np.random.default_rng(seed).integers(0, 2, (n, samples)).astype(bool)
        if sampled
        else input_assignments(n)
    )
    if encoding is None:
        expected = truth_outputs(md["source_network"], assignments)[0]
    else:
        expected = np.array(
            [
                encoding.problem.is_valid(
                    encoding.decode(sum(int(bit) << i for i, bit in enumerate(bits)))
                )
                for bits in assignments.T
            ],
            dtype=bool,
        )
    oracle = result.phase_oracle() if circuit is None else circuit
    if oracle.num_qubits != md["num_qubits"] or oracle.num_clbits:
        raise ValueError("Phase oracle must preserve the raw quantum register")
    bits = np.zeros((oracle.num_qubits, assignments.shape[1]), dtype=bool)
    bits[inputs] = assignments
    initial = bits.copy()
    phases = np.full(assignments.shape[1], np.exp(1j * float(oracle.global_phase)))
    for record in _qiskit_records(oracle):
        _apply_record(bits, phases, record)
    if not np.array_equal(bits, initial):
        raise AssertionError("Phase oracle does not restore inputs and workspace")
    expected_phases = np.where(expected, -1.0, 1.0)
    if not np.allclose(phases, expected_phases, atol=1e-9, rtol=0):
        raise AssertionError("Phase oracle has incorrect phase marking")
    report = {
        "status": "sampled" if sampled else "exhaustive",
        "assignments": assignments.shape[1],
        "marked_assignments": int(expected.sum()),
        "seed": seed if sampled else None,
        "reference": "coloring predicate" if encoding is not None else "source network",
        "phase_exact": True,
        "inputs_restored": True,
        "workspace_restored": True,
    }
    md["phase_validation"] = report
    return report
