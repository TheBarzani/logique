"""Logical circuit metrics; decomposition costs require an explicit basis."""


def circuit_metrics(circuit) -> dict:
    """Count operations without conflating MCX gates with T-gate estimates."""
    operations = {
        name: count
        for name, count in circuit.count_ops().items()
        if name not in ("barrier", "measure")
    }
    return {
        "qubits": circuit.num_qubits,
        "gates": sum(operations.values()),
        "depth": circuit.depth(),
        "gate_types": operations,
        "metric_level": "logical",
    }


def lower_circuit(
    circuit, *, basis_gates: list[str], seed: int = 7, optimization_level: int = 1
):
    """Lower into an explicit basis without a hardware target or routing."""
    from qiskit import transpile

    return transpile(
        circuit,
        basis_gates=basis_gates,
        seed_transpiler=seed,
        optimization_level=optimization_level,
    )


def decomposed_metrics(circuit, *, basis_gates: list[str], seed: int = 7) -> dict:
    """Report separately labeled metrics in a caller-selected basis."""
    lowered = lower_circuit(circuit, basis_gates=basis_gates, seed=seed)
    return {
        **circuit_metrics(lowered),
        "metric_level": "decomposed",
        "basis_gates": basis_gates,
        "seed": seed,
    }
