"""Local measurements and coloring success analysis."""

from vcgc.coloring import ColoringEncoding


def measured_circuit(circuit, input_qubits: list[int]):
    """Measure only the ordered input register into a named data register."""
    from qiskit import ClassicalRegister

    if circuit.num_clbits:
        raise ValueError("Supply an unmeasured circuit")
    if not input_qubits or len(set(input_qubits)) != len(input_qubits):
        raise ValueError("Input qubits must be nonempty and distinct")
    if any(q < 0 or q >= circuit.num_qubits for q in input_qubits):
        raise ValueError("Input qubit out of range")
    measured = circuit.copy()
    register = ClassicalRegister(len(input_qubits), "data")
    measured.add_register(register)
    measured.measure(input_qubits, register)
    return measured


def success_probability(counts: dict[str, int], encoding: ColoringEncoding) -> float:
    """Evaluate complete measured colorings using the declared input mapping."""
    if (
        not counts
        or any(type(n) is not int or n < 0 for n in counts.values())
        or sum(counts.values()) == 0
    ):
        raise ValueError("Counts must contain a positive total of nonnegative integers")
    total = 0
    for bits, count in counts.items():
        if len(bits) != encoding.input_count or any(b not in "01" for b in bits):
            raise ValueError("Bitstrings must match the ordered input register")
        total += count * encoding.problem.is_valid(encoding.decode(int(bits, 2)))
    return total / sum(counts.values())


def simulate(
    circuit, input_qubits: list[int], *, shots: int = 1024, seed: int = 7
) -> dict[str, int]:
    """Sample locally with an explicit deterministic simulator seed."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    if shots < 1:
        raise ValueError("shots must be positive")
    backend = AerSimulator(seed_simulator=seed)
    prepared = transpile(
        measured_circuit(circuit, input_qubits), backend, seed_transpiler=seed
    )
    return backend.run(prepared, shots=shots).result().get_counts()
