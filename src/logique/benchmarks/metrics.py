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


def decomposed_metrics(circuit, *, basis_gates: list[str], seed: int = 7) -> dict:
    """Report separately labeled metrics in a caller-selected basis."""
    from qiskit import transpile

    lowered = transpile(
        circuit, basis_gates=basis_gates, seed_transpiler=seed, optimization_level=1
    )
    return {
        **circuit_metrics(lowered),
        "metric_level": "decomposed",
        "basis_gates": basis_gates,
        "seed": seed,
    }
