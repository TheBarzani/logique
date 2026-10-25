"""Optional adapter for the unchanged Saha-Belletti comparison dependency."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from typing import TYPE_CHECKING, Any

from logique.coloring import ColoringProblem

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

VARIANTS = ("original", "simple", "minimal", "balanced")


@dataclass(frozen=True)
class BaselineComponents:
    """Independent baseline blocks in maintained LSB-first data order.

    ``initializer``, ``compute`` and ``uncompute`` have the same wire layout.
    Compute requires the initializer state; uncompute restores that state.
    ``circuit`` includes initialization and its inverse and implements a clean
    arbitrary-target XOR oracle. All non-data wires except its target must start
    at zero. ``phase_oracle()`` requires the target at zero too and restores it.

    Metadata partitions wires into data, final constraint flags, other workspace,
    and kickback/target roles. Constraint flags are also ancillas; the disjoint
    ``workspace_qubits`` role excludes them to avoid double-counting width.
    No preparation, diffusion, measurement or MCX lowering is included.
    """

    initializer: QuantumCircuit
    compute: QuantumCircuit
    uncompute: QuantumCircuit
    circuit: QuantumCircuit
    metadata: dict[str, Any]

    def oracle(self) -> QuantumCircuit:
        """Return |x,0,t> -> |x,0,t XOR predicate(x)> for either target bit."""
        return self.circuit.copy()

    def phase_oracle(self) -> QuantumCircuit:
        """Mark satisfying inputs by -1 and restore every ancilla to zero."""
        from qiskit import QuantumCircuit

        target = self.metadata["kickback_qubit"]
        phase = QuantumCircuit(self.circuit.num_qubits, name="baseline_phase")
        phase.x(target)
        phase.h(target)
        phase.compose(self.circuit, inplace=True)
        phase.h(target)
        phase.x(target)
        return phase


def baseline_components(
    problem: ColoringProblem,
    variant: str = "balanced",
    *,
    domain_policy: str = "complete",
) -> BaselineComponents:
    """Build clean baseline oracles using the installed, unchanged dependency.

    ``complete`` checks edges and unused color codes. ``domain_free`` checks
    only edges, by passing ``2**bits_per_color`` colors to ``make_problem``.
    This is the R3 predicate on *all* binary inputs; equivalence to complete
    coloring requires valid-color preparation. Labels are always normalized.

    Empty constraints yield constant true and self-loops yield constant false.
    Other unsatisfiable inputs need no solution count and are built normally.
    Precolors and fewer than two colors are unsupported. For nonconstant
    predicates, the original variant requires each vertex to have at most one
    higher-index neighbor: its installed multi-edge branch can miscompute and
    misorder uncomputation.
    Unsupported cases raise before returning any circuit. Historical replay
    remains available separately through ``comparison_circuit``.
    """
    if problem.precolored:
        raise ValueError("Baseline components do not support precolored vertices")
    if variant not in VARIANTS:
        raise ValueError(
            f"Unknown baseline variant {variant!r}; choose from {VARIANTS}"
        )
    if problem.colors < 2:
        raise ValueError("Baseline components require at least two colors")
    if domain_policy not in ("complete", "domain_free"):
        raise ValueError("domain_policy must be 'complete' or 'domain_free'")

    import networkx as nx
    from qiskit import QuantumCircuit
    from saha_belletti import oracles
    from saha_belletti.problem import decompose, make_problem

    bits = (problem.colors - 1).bit_length()
    data_count = len(problem.vertices) * bits
    label_map = {v: i for i, v in enumerate(problem.vertices)}
    graph = problem.to_networkx()
    graph = nx.relabel_nodes(graph, label_map)
    effective_colors = problem.colors if domain_policy == "complete" else 1 << bits
    constraint_count = len(problem.edges) + len(problem.vertices) * (
        (1 << bits) - effective_colors
    )
    constant: bool | None = None
    if any(u == v for u, v in problem.edges):
        constant = False
    elif constraint_count == 0:
        constant = True
    if constant is None and variant == "original":
        for node in graph:
            if sum(other > node for other in graph.neighbors(node)) > 1:
                raise ValueError(
                    "The installed original baseline is unsupported when a vertex "
                    "has multiple higher-index neighbors: its multi-edge branch "
                    "can miscompute constraints and uncomputation; use simple, "
                    "minimal or balanced"
                )

    qubit_count, init, compose = getattr(oracles, f"{variant}_system")
    package_problem = make_problem(graph, effective_colors)
    width_adjustment = 0
    if constant is not None:
        width = data_count + 1
        initializer = QuantumCircuit(width, name="baseline_init")
        compute = QuantumCircuit(width, name="baseline_compute")
        uncompute = QuantumCircuit(width, name="baseline_uncompute")
        constraints = []
        permutation = list(range(width))
    else:
        width = qubit_count(package_problem)
        # minimal_init flips two ancillas even with only one constraint, when
        # the second would otherwise alias the package's reserved XOR target.
        width_adjustment = int(variant == "minimal" and constraint_count == 1)
        width += width_adjustment
        raw_init = QuantumCircuit(width)
        init(raw_init, package_problem)
        raw = QuantumCircuit(width)
        constraints = list(compose(raw, package_problem))
        split = len(raw.data)
        decompose(package_problem)
        raw_compute = raw.copy_empty_like()
        raw_compute.data = raw.data[:split]
        raw_uncompute = raw.copy_empty_like()
        raw_uncompute.data = raw.data[split:]
        # Package invalid_color interprets the first color wire as its MSB.
        # Remap the actual blocks, without inserting runtime SWAP gates.
        permutation = [
            q
            for start in range(0, data_count, bits)
            for q in reversed(range(start, start + bits))
        ] + list(range(data_count, width))
        initializer, compute, uncompute = (
            QuantumCircuit(width, name=name).compose(block, permutation)
            for name, block in (
                ("baseline_init", raw_init),
                ("baseline_compute", raw_compute),
                ("baseline_uncompute", raw_uncompute),
            )
        )

    target = width - 1
    circuit = QuantumCircuit(width, name=f"{variant}_baseline_xor")
    circuit.compose(initializer, inplace=True)
    circuit.compose(compute, inplace=True)
    if constant is True:
        circuit.x(target)
    elif constant is None:
        circuit.mcx(constraints, target)
    circuit.compose(uncompute, inplace=True)
    circuit.compose(initializer.inverse(), inplace=True)
    roles = {
        "data": list(range(data_count)),
        "constraint": constraints,
        "workspace": [q for q in range(data_count, target) if q not in constraints],
        "kickback": [target],
    }
    metadata = {
        "method": f"saha_belletti_{variant}",
        "variant": variant,
        "domain_policy": domain_policy,
        "colors": problem.colors,
        "effective_colors": effective_colors,
        "bits_per_color": bits,
        "label_map": label_map,
        "input_mapping": {
            v: list(range(i * bits, (i + 1) * bits)) for v, i in label_map.items()
        },
        "input_bit_order": "lsb_first",
        "package_bit_order": "msb_first",
        "package_to_input_qubits": permutation,
        "input_qubits": roles["data"],
        "constraint_qubits": roles["constraint"],
        "workspace_qubits": roles["workspace"],
        "output_qubits": roles["kickback"],
        "kickback_qubit": target,
        "qubit_roles": roles,
        "qubit_counts": {role: len(wires) for role, wires in roles.items()},
        "initializer_one_qubits": [
            initializer.find_bit(inst.qubits[0]).index for inst in initializer.data
        ],
        "constraint_count": constraint_count,
        "constant_predicate": constant,
        "component_source": "dependency" if constant is None else "constant_adapter",
        "width_adjustment": width_adjustment,
        "construction": "initialize_compute_mark_uncompute_inverse_initialize",
        "phase_construction": "clean_xor_kickback",
        "workspace_initial_state": "zero",
        "metric_level": "logical",
        "mcx_lowering": "none",
        "dependency": {
            "distribution": "saha-belleti",
            "version": version("saha-belleti"),
            "make_problem": "saha_belletti.problem.make_problem",
            "qubit_count": f"{qubit_count.__module__}.{qubit_count.__name__}",
            "initializer": f"{init.__module__}.{init.__name__}",
            "compose": f"{compose.__module__}.{compose.__name__}",
            "decompose": "saha_belletti.problem.decompose",
        },
        "validation": {"status": "not run"},
    }
    return BaselineComponents(initializer, compute, uncompute, circuit, metadata)


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
