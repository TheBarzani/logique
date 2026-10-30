"""Optional adapter for the unchanged Saha-Belletti comparison dependency."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from logique.coloring import ColoringProblem

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

VARIANTS = ("original", "simple", "minimal", "balanced")


def comparison_circuit(
    problem: ColoringProblem,
    variant: str = "balanced",
    *,
    iterations: int = 1,
    preserve_labels: bool = False,
    measure: bool = False,
):
    """Build a Grover circuit; optionally preserve labels for historical replay.

    Defaults normalize vertex labels and omit measurements. Historical replay
    can retain the original indexing and measured dependency output explicitly.
    This backend does not implement precolors.
    """
    if problem.precolored:
        raise ValueError(
            "Saha-Belletti does not support precolored vertices; use an unprecolored comparison input"
        )
    if variant not in VARIANTS or problem.colors < 2 or not problem.vertices:
        raise ValueError(
            "Saha-Belletti requires a known variant, vertices, and at least two colors"
        )
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be nonnegative")
    import networkx as nx
    from saha_belletti.core import generate_circuit

    graph = problem.to_networkx()
    if not preserve_labels:
        graph = nx.relabel_nodes(graph, {v: i for i, v in enumerate(problem.vertices)})
    circuit = generate_circuit(
        graph, problem.colors, oracle_type=variant, grover_iterations=iterations
    )
    return circuit if measure else circuit.remove_final_measurements(inplace=False)


@dataclass(frozen=True)
class BaselineOracle:
    """One Saha-Belletti oracle call, separated from preparation and diffusion.

    ``circuit`` applies the variant's ancilla initialization, its compute block,
    the multi-controlled X on the kick-back ``target``, the recorded
    uncomputation, and the inverse initialization, so every qubit other than the
    target starts and ends in |0>. ``compute`` spans the compute block
    (instruction indices) for transformations that rely on its mirror.
    ``data`` lists the data qubits in Logique's order: vertex by vertex, least
    significant color bit first; the dependency stores the most significant bit
    first within each vertex.
    """

    circuit: "QuantumCircuit"
    compute: tuple[int, int]
    data: list[int]
    target: int
    ancillas: list[int]
    colors: int
    variant: str


def baseline_oracle(
    problem: ColoringProblem, variant: str, *, domain_checks: bool = True
) -> BaselineOracle:
    """Build a baseline oracle with normalized labels.

    Vertices are relabeled 0, ..., n - 1 in the problem's vertex order. Without
    ``domain_checks`` the oracle is built for 2^c colors, which removes its
    invalid-color checks while keeping the edge comparators; it is then correct
    only for preparations that exclude unused codes.
    """
    if problem.precolored:
        raise ValueError("Saha-Belletti does not support precolored vertices")
    if variant not in VARIANTS or problem.colors < 2 or not problem.vertices:
        raise ValueError(
            "Saha-Belletti requires a known variant, vertices, and at least two colors"
        )
    import networkx as nx
    from qiskit import QuantumCircuit
    from saha_belletti.balanced import balanced_system
    from saha_belletti.minimal import minimal_system
    from saha_belletti.original import original_system
    from saha_belletti.problem import decompose, make_problem
    from saha_belletti.simple import simple_system

    systems = {
        "original": original_system,
        "simple": simple_system,
        "minimal": minimal_system,
        "balanced": balanced_system,
    }
    qubit_count, init, compose = systems[variant]
    bits = (problem.colors - 1).bit_length()
    colors = problem.colors if domain_checks else 1 << bits
    graph = nx.relabel_nodes(
        problem.to_networkx(), {v: i for i, v in enumerate(problem.vertices)}
    )
    instance = make_problem(graph, colors)
    width = qubit_count(instance)
    circuit = QuantumCircuit(width)
    init(circuit, instance)
    initialization = list(circuit.data)
    start = len(circuit.data)
    controls = compose(circuit, instance)
    stop = len(circuit.data)
    circuit.mcx(list(controls), width - 1)
    decompose(instance)
    for inst in reversed(initialization):
        circuit.append(inst.operation.inverse(), inst.qubits, inst.clbits)
    data = [
        i * bits + (bits - 1 - bit)
        for i in range(len(problem.vertices))
        for bit in range(bits)
    ]
    ancillas = list(range(len(problem.vertices) * bits, width - 1))
    return BaselineOracle(
        circuit, (start, stop), data, width - 1, ancillas, colors, variant
    )
