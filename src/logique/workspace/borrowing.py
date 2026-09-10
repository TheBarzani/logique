"""Verified conditional-workspace demonstration."""

import numpy as np
from qiskit import QuantumCircuit


def borrowing_demo():
    """Exact four-control X with either two clean qubits or one plus borrowing.

    Qubits 0..3 are controls, 4 is the arbitrary target, 5.. are clean.
    The borrowed input b is known to be 1 only under the stored a AND b flag.
    """
    reference = QuantumCircuit(7, name="dedicated_workspace")
    reference.ccx(0, 1, 5)
    reference.ccx(5, 2, 6)
    reference.ccx(6, 3, 4)
    reference.ccx(5, 2, 6)
    reference.ccx(0, 1, 5)

    borrowed = QuantumCircuit(6, name="conditional_workspace")
    borrowed.ccx(0, 1, 5)
    borrowed.barrier(label="flag = a AND b")
    borrowed.x(1)
    borrowed.ccx(2, 3, 1)
    borrowed.barrier(label="borrow b")
    borrowed.ccx(5, 1, 4)
    borrowed.barrier(label="consume under flag")
    borrowed.ccx(2, 3, 1)
    borrowed.x(1)
    borrowed.ccx(0, 1, 5)
    return reference, borrowed


def verify_borrowing():
    """Check the entire valid subspace, plus an entangled-reference state."""
    from qiskit.quantum_info import Operator, Statevector

    checks = {}
    for qc in borrowing_demo():
        actual = Operator(qc).data[:, :32]
        expected = np.zeros_like(actual)
        for basis in range(32):
            output = basis ^ (16 if basis & 15 == 15 else 0)
            expected[output, basis] = 1
        if not np.allclose(actual, expected, atol=1e-10):
            raise AssertionError(
                "Borrowing demo failed subspace/phase/restoration check"
            )
        # A reference entangled with the inputs must retain its coherence.
        prep = QuantumCircuit(qc.num_qubits + 1)
        prep.h(0)
        prep.cx(0, qc.num_qubits)
        prep.h(1)
        prep.ry(0.71, 2)
        prep.h(3)
        prep.ry(0.39, 4)
        state = Statevector.from_instruction(prep)
        ideal = QuantumCircuit(qc.num_qubits + 1)
        ideal.mcx([0, 1, 2, 3], 4)
        if not np.allclose(
            state.evolve(qc, range(qc.num_qubits)).data,
            state.evolve(ideal).data,
            atol=1e-10,
        ):
            raise AssertionError("Entangled-reference check failed")
        checks[qc.name] = {
            "qubits": qc.num_qubits,
            "clean_workspace": qc.num_qubits - 5,
            "ccx": qc.count_ops().get("ccx", 0),
            "phase_and_restoration": "passed",
        }
    return checks
