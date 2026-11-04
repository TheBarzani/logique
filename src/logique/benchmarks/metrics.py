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
    """Lower a reusable component, preserving arbitrary input states.

    Component entry is not program entry: data, targets and idle spectators
    can be nonzero or entangled when the emitted circuit is composed later.
    Explicit MCX clean-workspace promises belong to the construction layer.
    """
    from qiskit import transpile

    return transpile(
        circuit,
        basis_gates=basis_gates,
        seed_transpiler=seed,
        optimization_level=optimization_level,
        qubits_initially_zero=False,
        num_processes=1,
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
