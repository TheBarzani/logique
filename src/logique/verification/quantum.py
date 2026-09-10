"""Small quantum checks of values, phases, and restored workspace."""

import numpy as np
from qiskit import QuantumCircuit
from .classical import input_assignments, truth_outputs


def verify_small_quantum(result):
    """Cross-check the actual Qiskit oracle and phase oracle on a superposition."""
    from qiskit.quantum_info import Statevector

    qc = result.oracle()
    if qc.num_qubits > 16:
        raise ValueError("Statevector check limited to 16 qubits")
    md = result.metadata
    n = len(md["input_qubits"])
    assignments = input_assignments(n)
    values = truth_outputs(md["source_network"], assignments)
    prep = QuantumCircuit(qc.num_qubits)
    for q in md["input_qubits"]:
        prep.h(q)
    # Test a nonzero target, too; all other clean workspace stays zero.
    prep.x(result.circuit.num_qubits)
    state = Statevector.from_instruction(prep).evolve(qc)
    expected = np.zeros(1 << qc.num_qubits, dtype=complex)
    for x in range(1 << n):
        index = sum(
            int(assignments[i, x]) << q for i, q in enumerate(md["input_qubits"])
        )
        for i in range(values.shape[0]):
            index |= int(values[i, x] ^ (i == 0)) << (result.circuit.num_qubits + i)
        expected[index] = 1 / np.sqrt(1 << n)
    if not np.allclose(state.data, expected, atol=1e-9):
        raise AssertionError("Qiskit oracle differs in values, phases, or restoration")
    phase = result.phase_oracle()
    prep = QuantumCircuit(phase.num_qubits)
    for q in md["input_qubits"]:
        prep.h(q)
    expected = np.zeros(1 << phase.num_qubits, dtype=complex)
    for x in range(1 << n):
        index = sum(
            int(assignments[i, x]) << q for i, q in enumerate(md["input_qubits"])
        )
        expected[index] = (-1 if values[0, x] else 1) / np.sqrt(1 << n)
    if not np.allclose(
        Statevector.from_instruction(prep).evolve(phase).data, expected, atol=1e-9
    ):
        raise AssertionError("Phase oracle differs from (-1)^f(x)")
    return "Qiskit superposition, phase action, and restoration passed"
