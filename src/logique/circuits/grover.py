"""Amplitude amplification with explicit data wires and restored workspace."""

from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation
import numpy as np
from logique.coloring import ColoringEncoding
from logique.synthesis.result import SynthesisResult


def coloring_preparation(encoding: ColoringEncoding) -> QuantumCircuit:
    """Prepare valid colors, fixing precolored vertices to their specified value."""
    qc = QuantumCircuit(encoding.input_count)
    for vertex, wires in encoding.input_mapping.items():
        if vertex in encoding.problem.precolored:
            color = encoding.problem.precolored[vertex]
            for bit, q in enumerate(wires):
                if (color >> bit) & 1:
                    qc.x(q)
        else:
            amplitudes = np.zeros(1 << len(wires))
            amplitudes[: encoding.problem.colors] = 1 / np.sqrt(encoding.problem.colors)
            qc.append(StatePreparation(amplitudes), wires)
    return qc


def grover_circuit(
    result: SynthesisResult,
    *,
    preparation: QuantumCircuit | None = None,
    iterations: int = 1,
) -> QuantumCircuit:
    """Alternate a clean phase oracle with reflection about the prepared state."""
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be a nonnegative integer")
    wires = result.metadata["input_qubits"]
    n = len(wires)
    if n == 0:
        raise ValueError("Grover search requires at least one input qubit")
    if preparation is None:
        preparation = QuantumCircuit(n)
        preparation.h(range(n))
    if preparation.num_qubits != n or preparation.num_clbits:
        raise ValueError("Preparation must act on exactly the input register")
    reflection = QuantumCircuit(n)
    reflection.compose(preparation.inverse(), inplace=True)
    reflection.x(range(n))
    if n == 1:
        reflection.z(0)
    else:
        reflection.h(n - 1)
        reflection.mcx(list(range(n - 1)), n - 1)
        reflection.h(n - 1)
    reflection.x(range(n))
    reflection.compose(preparation, inplace=True)
    reflection.global_phase += np.pi
    circuit = QuantumCircuit(result.circuit.num_qubits)
    circuit.compose(preparation, wires, inplace=True)
    for _ in range(iterations):
        circuit.compose(result.phase_oracle(), inplace=True)
        circuit.compose(reflection, wires, inplace=True)
    return circuit
