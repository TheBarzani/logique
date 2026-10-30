"""Coherent phase-oracle checks without exponential workspace statevectors."""

import numpy as np
from logique.circuits.records import _qiskit_records
from .classical import _apply_record, input_assignments, truth_outputs


def _inputs(n, assignments, sampled, samples, seed):
    """Explicit, sampled or exhaustive input columns, with their status."""
    if assignments is not None:
        assignments = np.asarray(assignments, dtype=bool)
        if assignments.ndim != 2 or assignments.shape[0] != n:
            raise ValueError(f"assignments must have shape ({n}, count)")
        return assignments, "explicit"
    if sampled:
        return (
            np.random.default_rng(seed).integers(0, 2, (n, samples)).astype(bool),
            "sampled",
        )
    return input_assignments(n), "exhaustive"


def _predicate(encoding, assignments):
    return np.array(
        [
            encoding.problem.is_valid(
                encoding.decode(sum(int(bit) << i for i, bit in enumerate(bits)))
            )
            for bits in assignments.T
        ],
        dtype=bool,
    )


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
    proof. Explicit ``assignments`` (inputs × columns) replace both, for
    example to include known solutions. X, controlled-X, Z and controlled
    Rx(+/-pi) gates are supported.
    """
    if samples < 1:
        raise ValueError("samples must be positive")
    md = result.metadata
    inputs = md["input_qubits"]
    n = len(inputs)
    if encoding is not None and encoding.input_count != n:
        raise ValueError("Coloring encoding does not match the input register")
    assignments, status = _inputs(n, assignments, sampled, samples, seed)
    if encoding is None:
        expected = truth_outputs(md["source_network"], assignments)[0]
    else:
        expected = _predicate(encoding, assignments)
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
        "status": status,
        "assignments": assignments.shape[1],
        "marked_assignments": int(expected.sum()),
        "seed": seed if status == "sampled" else None,
        "reference": "coloring predicate" if encoding is not None else "source network",
        "phase_exact": True,
        "inputs_restored": True,
        "workspace_restored": True,
    }
    md["phase_validation"] = report
    return report


def verify_xor_oracle(
    circuit,
    *,
    data,
    target: int,
    encoding,
    sampled: bool = False,
    samples: int = 256,
    seed: int = 7,
    assignments=None,
) -> dict:
    """Check that a reversible circuit XORs the coloring predicate into a target.

    ``data`` lists the qubits that hold the encoding's inputs, in input order;
    every other qubit starts in |0>, except the target, which is tested with
    both values. The circuit must restore all qubits but the target and add no
    phase, which by linearity establishes phase kick-back on |-> in the target.
    X, controlled-X, Z and controlled Rx(+/-pi) gates are supported.
    """
    data = list(data)
    if encoding.input_count != len(data) or samples < 1:
        raise ValueError("XOR validation requires matching inputs")
    assignments, status = _inputs(len(data), assignments, sampled, samples, seed)
    expected = _predicate(encoding, assignments)
    records = _qiskit_records(circuit)
    for value in (False, True):
        bits = np.zeros((circuit.num_qubits, assignments.shape[1]), dtype=bool)
        bits[data] = assignments
        bits[target] = value
        final = bits.copy()
        final[target] ^= expected
        phases = np.full(assignments.shape[1], np.exp(1j * float(circuit.global_phase)))
        for record in records:
            _apply_record(bits, phases, record)
        if not np.array_equal(bits, final) or not np.allclose(phases, 1, atol=1e-9):
            raise AssertionError(
                f"Oracle fails clean XOR action for target={int(value)}"
            )
    return {
        "status": status,
        "assignments": assignments.shape[1],
        "target_initializations": [0, 1],
        "marked_assignments": int(expected.sum()),
        "seed": seed if status == "sampled" else None,
        "reference": "coloring predicate of the encoding",
        "phase_exact": True,
        "inputs_restored": True,
        "workspace_restored": True,
    }


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
    report = verify_xor_oracle(
        result.circuit,
        data=inputs,
        target=outputs[0],
        encoding=encoding,
        sampled=sampled,
        samples=samples,
        seed=seed,
        assignments=assignments,
    )
    report["reference"] = "edge-only coloring predicate over all encoded colors"
    md["kickback_validation"] = report
    return report
