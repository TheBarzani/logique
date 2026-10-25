"""Coherent phase-oracle checks without exponential workspace statevectors."""

import numpy as np
from logique.circuits.records import _qiskit_records
from .classical import _apply_record, verification_assignments, truth_outputs


def verify_phase_oracle(
    result,
    *,
    encoding=None,
    circuit=None,
    sampled: bool = False,
    samples: int = 256,
    seed: int = 7,
    assignments=None,
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
    assignments, coverage = verification_assignments(
        n, sampled=sampled, samples=samples, seed=seed, assignments=assignments
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
        **coverage,
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


def verify_kickback_oracle(
    result,
    *,
    encoding,
    sampled: bool = False,
    samples: int = 256,
    seed: int = 7,
    assignments=None,
) -> dict:
    """Check raw XOR action, clean workspace, and exact phase for both target bits.

    Testing target zero and one establishes kickback on |minus> by linearity.
    Internal XAG cleanup alone is not a sufficient guarantee: the synthesizer
    can borrow an output as workspace assuming that output starts at zero.
    """
    md = result.metadata
    inputs, outputs = md["input_qubits"], md["output_qubits"]
    if len(outputs) != 1 or encoding.input_count != len(inputs) or samples < 1:
        raise ValueError("Kickback validation requires one output and matching inputs")
    assignments, coverage = verification_assignments(
        len(inputs),
        sampled=sampled,
        samples=samples,
        seed=seed,
        assignments=assignments,
    )
    expected = np.array(
        [
            encoding.problem.is_valid(
                encoding.decode(sum(int(bit) << i for i, bit in enumerate(bits)))
            )
            for bits in assignments.T
        ],
        dtype=bool,
    )
    for target in (False, True):
        bits = np.zeros((result.circuit.num_qubits, assignments.shape[1]), dtype=bool)
        bits[inputs] = assignments
        bits[outputs[0]] = target
        final = bits.copy()
        final[outputs[0]] ^= expected
        phases = np.full(
            assignments.shape[1], np.exp(1j * float(result.circuit.global_phase))
        )
        for record in _qiskit_records(result.circuit):
            _apply_record(bits, phases, record)
        if not np.array_equal(bits, final) or not np.allclose(phases, 1, atol=1e-9):
            raise AssertionError(
                f"Raw oracle fails clean XOR action for target={int(target)}"
            )
    report = {
        **coverage,
        "status": "sampled" if sampled else "exhaustive",
        "assignments": assignments.shape[1],
        "target_initializations": [0, 1],
        "marked_assignments": int(expected.sum()),
        "seed": seed if sampled else None,
        "reference": "edge-only coloring predicate over all encoded colors",
        "phase_exact": True,
        "inputs_restored": True,
        "workspace_restored": True,
    }
    md["kickback_validation"] = report
    return report
