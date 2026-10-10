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


def _reflection(preparation: QuantumCircuit) -> QuantumCircuit:
    n = preparation.num_qubits
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
    return reflection


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
    reflection = _reflection(preparation)
    reflection.global_phase += np.pi
    circuit = QuantumCircuit(result.circuit.num_qubits)
    circuit.compose(preparation, wires, inplace=True)
    for _ in range(iterations):
        circuit.compose(result.phase_oracle(), inplace=True)
        circuit.compose(reflection, wires, inplace=True)
    return circuit


def kickback_grover_circuit(
    result: SynthesisResult,
    *,
    preparation: QuantumCircuit,
    reflection_preparation: QuantumCircuit | None = None,
    iterations: int = 1,
) -> QuantumCircuit:
    """Apply a clean XOR oracle once per iteration with its output in |minus>.

    Verify arbitrary-target XOR action before using this construction. It adds
    no inverse of the oracle: internal cleanup must already restore workspace.
    An explicit reflection preparation allows replay of historical experiments
    whose initial preparation and diffusion reflection differed.
    """
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be a nonnegative integer")
    wires = result.metadata["input_qubits"]
    outputs = result.metadata["output_qubits"]
    if not wires or len(outputs) != 1:
        raise ValueError("Kickback requires data inputs and exactly one output target")
    reflection_preparation = (
        preparation if reflection_preparation is None else reflection_preparation
    )
    if any(
        p.num_qubits != len(wires) or p.num_clbits
        for p in (preparation, reflection_preparation)
    ):
        raise ValueError("Preparation must act on exactly the input register")
    circuit = QuantumCircuit(result.circuit.num_qubits)
    circuit.compose(preparation, wires, inplace=True)
    circuit.x(outputs[0])
    circuit.h(outputs[0])
    reflection = _reflection(reflection_preparation)
    for _ in range(iterations):
        circuit.barrier()
        circuit.compose(result.circuit, inplace=True)
        circuit.barrier()
        circuit.compose(reflection, wires, inplace=True)
    return circuit
