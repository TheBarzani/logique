"""Coloring constraints with clean sequential or private parallel workspace.

This logical construction has no preparation, diffusion, MCX decomposition or
benchmark integration. Parallel emission uses vertex-disjoint edge layers and
private scratch within each layer; the default remains sequential.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from logique.coloring import ColoringEncoding, ColoringProblem

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


def edge_inequality(bits_per_color: int) -> QuantumCircuit:
    """Return a clean arbitrary-target XOR comparator on two LSB-first words.

    Layout: left [0,c), right [c,2c), target 2c, clean scratch thereafter
    (c-1 wires). The right word temporarily holds bitwise XNOR. A prefix AND
    chain computes equality, which is complemented into the target. Inverting
    the actual chain and XNOR block restores scratch and both words exactly.
    For c=1, two CNOTs suffice. This proves coherent XOR action by linearity
    on the clean-scratch subspace, including targets entangled with data.
    No contract is made for initially dirty scratch or overlapping words.
    """
    from qiskit import QuantumCircuit

    if type(bits_per_color) is not int or bits_per_color < 1:
        raise ValueError("bits_per_color must be a positive integer")
    c = bits_per_color
    target = 2 * c
    circuit = QuantumCircuit(3 * c, name="edge_inequality")
    if c == 1:
        circuit.cx(0, target)
        circuit.cx(1, target)
        return circuit
    xnor = QuantumCircuit(3 * c)
    for bit in range(c):
        xnor.cx(bit, c + bit)
        xnor.x(c + bit)
    chain = QuantumCircuit(3 * c)
    chain.ccx(c, c + 1, target + 1)
    for bit in range(2, c):
        chain.ccx(target + bit - 1, c + bit, target + bit)
    circuit.compose(xnor, inplace=True)
    circuit.compose(chain, inplace=True)
    circuit.x(target)
    circuit.cx(3 * c - 1, target)
    circuit.compose(chain.inverse(), inplace=True)
    circuit.compose(xnor.inverse(), inplace=True)
    return circuit


def disjoint_edge_layers(
    problem: ColoringProblem,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Greedily partition canonical edges into deterministic vertex-disjoint layers.

    First-fit placement uses the sorted, deduplicated edges of ColoringProblem.
    Each edge is placed once and a layer accepts it only if neither endpoint
    occurs there. Self-loops occupy their vertex, although their flag is false.
    This is a schedule only, with no optimality or emitted-depth claim.
    """
    layers: list[list[tuple[int, int]]] = []
    occupied: list[set[int]] = []
    for edge in problem.edges:
        endpoints = set(edge)
        for layer, used in zip(layers, occupied):
            if used.isdisjoint(endpoints):
                layer.append(edge)
                used.update(endpoints)
                break
        else:
            layers.append([edge])
            occupied.append(endpoints)
    return tuple(tuple(layer) for layer in layers)


def _toggle(circuit: QuantumCircuit, controls: list[int], target: int) -> None:
    if controls:
        circuit.mcx(controls, target)
    else:
        circuit.x(target)


def _pattern_toggle(
    circuit: QuantumCircuit, wires: list[int], value: int, target: int
) -> None:
    zeros = [q for bit, q in enumerate(wires) if not (value >> bit) & 1]
    for q in zeros:
        circuit.x(q)
    _toggle(circuit, wires, target)
    for q in reversed(zeros):
        circuit.x(q)


@dataclass(frozen=True)
class StructureOracle:
    """Logical coloring oracle with explicit disjoint wire roles.

    ``compute`` fills constraint flags and restores comparator scratch. All
    non-data wires except the XOR target must start at zero. ``circuit`` then
    toggles an arbitrary target by the conjunction and uncomputes flags.
    ``phase_oracle()`` also requires a zero target and restores every ancilla.
    Metadata records allocated logical workspace, excluding any future MCX
    decomposition ancillas. Validation is a caller obligation, not inferred
    from successful construction.
    """

    compute: QuantumCircuit
    circuit: QuantumCircuit
    metadata: dict[str, Any]

    def oracle(self) -> QuantumCircuit:
        """Return |x,0,t> -> |x,0,t XOR f(x)> for either target bit."""
        return self.circuit.copy()

    def phase_oracle(self) -> QuantumCircuit:
        """Return (-1)^f(x)|x,0> with exact clean-workspace restoration."""
        phase = self.compute.copy()
        flags = self.metadata["constraint_qubits"]
        target = self.metadata["output_qubits"][0]
        _toggle(phase, flags, target)
        phase.z(target)
        _toggle(phase, flags, target)
        phase.compose(self.compute.inverse(), inplace=True)
        return phase


def structure_oracle(
    problem: ColoringProblem,
    *,
    domain_policy: str = "complete",
    emission: str = "sequential",
) -> StructureOracle:
    """Build edge inequalities and, optionally, valid-code flags.

    Data uses ColoringEncoding's sorted labels and LSB-first contiguous words,
    including isolated vertices. ``complete`` checks x_v < k and every edge.
    ``domain_free`` checks only edge inequalities over ALL binary codes; it
    equals complete coloring only on the valid-code subspace (e.g. maintained
    coloring_preparation). Precolors are explicitly unsupported in this slice.
    Empty conjunctions are true; a self-loop supplies a constant-false flag.

    Each edge has one retained flag. ``emission="sequential"`` shares c-1 clean
    scratch wires, restored before the next edge. ``emission="parallel"`` emits
    deterministic vertex-disjoint layers with explicit barrier boundaries.
    The w non-loop comparators in a layer have private c-1-wire scratch slots,
    reused only after cleanup at the layer boundary. Their emitted gates touch
    disjoint wires, allowing concurrent logical execution within that layer.
    Slots across layers share an allocation of W(c-1), W=max(w).

    Valid-code flags remain sequential and use disjoint binary prefix patterns
    for x < k, at most c toggles per vertex, with no scratch. All flags are
    uncomputed using the actual emitted inverse, including layer boundaries.
    With F retained flags, allocated non-data width is exactly F+scratch+1,
    including the arbitrary XOR output (zero for phase). All scratch is clean
    at layer/domain/conjunction boundaries, while flags live until the inverse.
    No lowered MCX resources or physical duration are implied.
    """
    from qiskit import QuantumCircuit

    if problem.precolored:
        raise ValueError("Structure oracle does not support precolored vertices")
    if domain_policy not in ("complete", "domain_free"):
        raise ValueError("domain_policy must be 'complete' or 'domain_free'")
    if emission not in ("sequential", "parallel"):
        raise ValueError("emission must be 'sequential' or 'parallel'")
    encoding = ColoringEncoding(problem)
    c = encoding.bits_per_color
    mapping = encoding.input_mapping
    domains = (
        list(problem.vertices)
        if domain_policy == "complete" and problem.colors != 1 << c
        else []
    )
    count = len(problem.edges) + len(domains)
    n = encoding.input_count
    flags = list(range(n, n + count))
    layers = disjoint_edge_layers(problem)
    concurrent = max((sum(u != v for u, v in layer) for layer in layers), default=0)
    has_comparator = any(u != v for u, v in problem.edges)
    sequential_scratch = c - 1 if has_comparator else 0
    scratch_count = (
        concurrent * (c - 1) if emission == "parallel" else sequential_scratch
    )
    scratch = list(range(n + count, n + count + scratch_count))
    target = n + count + scratch_count
    compute = QuantumCircuit(target + 1, name="structure_compute")
    comparator = edge_inequality(c) if has_comparator else None
    emitted_layers: list[dict[str, Any]] = []
    if emission == "sequential":
        for flag, (u, v) in zip(flags, problem.edges):
            if u != v:
                compute.compose(
                    comparator, [*mapping[u], *mapping[v], flag, *scratch], inplace=True
                )
    else:
        edge_flags = dict(zip(problem.edges, flags))
        for index, layer in enumerate(layers):
            compute.barrier(label=f"edge_layer_{index}_start")
            start = len(compute.data)
            comparators: list[dict[str, Any]] = []
            for u, v in layer:
                if u == v:
                    continue  # Its retained zero flag makes the predicate false.
                slot = len(comparators)
                private = scratch[slot * (c - 1) : (slot + 1) * (c - 1)]
                wires = [*mapping[u], *mapping[v], edge_flags[u, v], *private]
                first = len(compute.data)
                compute.compose(comparator, wires, inplace=True)
                comparators.append(
                    {
                        "edge": (u, v),
                        "qubits": wires,
                        "scratch": private,
                        "instruction_range": (first, len(compute.data)),
                    }
                )
            emitted_layers.append(
                {
                    "edges": layer,
                    "instruction_range": (start, len(compute.data)),
                    "comparators": comparators,
                }
            )
            compute.barrier(label=f"edge_layer_{index}_end")
    for flag, vertex in zip(flags[len(problem.edges) :], domains):
        # x < k iff the first differing bit (from MSB down) has x=0,k=1.
        # These prefixes are disjoint, so XOR of their indicators equals OR.
        for bit in reversed(range(c)):
            if (problem.colors >> bit) & 1:
                wires = list(mapping[vertex][bit:])
                prefix = (problem.colors >> bit) ^ 1
                _pattern_toggle(compute, wires, prefix, flag)
    circuit = compute.copy()
    _toggle(circuit, flags, target)
    circuit.compose(compute.inverse(), inplace=True)
    roles = {
        "data": list(range(n)),
        "constraint": flags,
        "workspace": scratch,
        "target": [target],
    }
    metadata = {
        "method": f"structure_{emission}",
        "domain_policy": domain_policy,
        "bits_per_color": c,
        "input_mapping": {v: list(qs) for v, qs in mapping.items()},
        "input_qubits": roles["data"],
        "output_qubits": [target],
        "constraint_qubits": flags,
        "edge_constraint_qubits": flags[: len(problem.edges)],
        "domain_constraint_qubits": flags[len(problem.edges) :],
        "workspace_qubits": scratch,
        "num_qubits": target + 1,
        "qubit_roles": roles,
        "qubit_counts": {role: len(qs) for role, qs in roles.items()},
        "metric_level": "logical",
        "mcx_decomposition": "not lowered; additional ancillas not included",
        "sequential_comparator_scratch": sequential_scratch,
        "sequential_clean_ancillas": count + sequential_scratch + 1,
        "edge_layers": layers,
        "parallel_schedule_only": emission == "sequential",
        "parallel_max_active_comparators": concurrent,
        "parallel_comparator_scratch": concurrent * (c - 1),
        "parallel_clean_ancillas_requirement": count + concurrent * (c - 1) + 1,
        "parallel_logical_width_requirement": n + count + concurrent * (c - 1) + 1,
        "validation": {"status": "not run"},
    }
    if emission == "parallel":
        metadata.update(
            {
                "emitted_edge_layers": emitted_layers,
                "peak_workspace_including_flags_output": count + scratch_count + 1,
                "scratch_lifetime": (
                    "private within each layer; restored by each comparator's actual "
                    "inverse; shared slots reused across barrier-separated layers; "
                    "clean during sequential domains and conjunction"
                ),
                "flag_lifetime": "retained through conjunction until compute inverse",
            }
        )
    return StructureOracle(compute, circuit, metadata)
