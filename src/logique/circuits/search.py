"""Grover search instances under controlled preparation and domain regimes.

A search instance holds the three components of amplitude amplification on one
register: the preparation A, the oracle and the diffusion operator
A(2|0><0| - I)A^dagger. The regimes isolate the preparation from the domain
checks of the predicate:

* R1: Hadamard preparation and the complete predicate, which rejects unused
  color codes;
* R2: valid-color preparation and the complete predicate;
* R3: valid-color preparation without domain checks, which is correct only
  because the preparation never produces an unused code.
"""

from dataclasses import dataclass, field, replace
import time

from qiskit import QuantumCircuit
from qiskit.circuit import ControlledGate
from qiskit.circuit.library.data_preparation.state_preparation import (
    UniformSuperpositionGate,
)

from logique.coloring import ColoringEncoding, encode_coloring
from logique.coloring.model import ColoringProblem
from .grover import _reflection

REGIMES = {"R1": ("hadamard", True), "R2": ("valid", True), "R3": ("valid", False)}


@dataclass
class SearchInstance:
    """Preparation, oracle and diffusion on one full-width register.

    ``clean`` lists qubits in |0> before and after every oracle call, which
    MCX decompositions and measurement-based uncomputation may rely on.
    ``mirrored`` is the instruction span of an oracle's compute block whose
    exact inverse follows a kick-back gate or a phase flip, when the oracle has
    that structure.
    """

    method: str
    regime: str
    preparation: QuantumCircuit
    oracle: QuantumCircuit
    diffusion: QuantumCircuit
    data: list[int]
    roles: dict[str, list[int]]
    clean: list[int]
    form: str
    domain: int
    encoding: ColoringEncoding
    validation: dict
    mirrored: tuple[int, int] | None = None
    timings: dict = field(default_factory=dict)
    structure: dict = field(default_factory=dict)

    def grover(self, iterations: int) -> QuantumCircuit:
        """Prepare once, then alternate the oracle and the diffusion operator."""
        if type(iterations) is not int or iterations < 0:
            raise ValueError("iterations must be a nonnegative integer")
        circuit = self.preparation.copy()
        for _ in range(iterations):
            circuit.compose(self.oracle, inplace=True)
            circuit.compose(self.diffusion, inplace=True)
        return circuit


def data_preparation(problem: ColoringProblem, groups, kind: str) -> QuantumCircuit:
    """Prepare each vertex register; ``groups`` are its qubits, low bit first.

    The valid-color preparation uses the Shukla–Vedula construction, which is
    a Hadamard stack when the number of colors is a power of two; precolored
    vertices are set to their color. The Hadamard preparation covers all codes.
    """
    width = sum(len(group) for group in groups)
    circuit = QuantumCircuit(width)
    if kind == "valid":
        uniform = QuantumCircuit(len(groups[0]))
        uniform.append(UniformSuperpositionGate(problem.colors), range(len(groups[0])))
        uniform = uniform.decompose()
    for vertex, group in zip(problem.vertices, groups):
        if kind == "hadamard":
            circuit.h(group)
        elif vertex in problem.precolored:
            color = problem.precolored[vertex]
            for bit, q in enumerate(group):
                if (color >> bit) & 1:
                    circuit.x(q)
        else:
            circuit.compose(uniform, group, inplace=True)
    return circuit


def _assemble(problem, regime, data, width, target, kick_back):
    kind, _ = REGIMES[regime]
    bits = max(1, (problem.colors - 1).bit_length())
    groups = [
        list(range(i * bits, (i + 1) * bits)) for i in range(len(problem.vertices))
    ]
    local = data_preparation(problem, groups, kind)
    preparation = QuantumCircuit(width)
    preparation.compose(local, data, inplace=True)
    if kick_back:
        preparation.x(target)
        preparation.h(target)
    diffusion = QuantumCircuit(width)
    diffusion.compose(_reflection(local), data, inplace=True)
    free = [v for v in problem.vertices if v not in problem.precolored]
    domain = (
        (1 << (bits * len(problem.vertices)))
        if kind == "hadamard"
        else problem.colors ** len(free)
    )
    return preparation, diffusion, domain


def _mirror_span(circuit: QuantumCircuit) -> tuple[int, int] | None:
    """Span of a compute block that the circuit undoes exactly around one gate.

    The circuit must read B, G, B^-1, where the middle gate G changes no wire
    of B (an X gate with any controls whose target lies outside B, or a Z
    gate), so that relative phases inside B commute with G and cancel.
    """
    data = circuit.data
    if len(data) % 2 == 0:
        return None
    half = len(data) // 2
    for first, last in zip(data[:half], reversed(data[half + 1 :])):
        if first.qubits != last.qubits or first.operation != last.operation.inverse():
            return None
    middle = data[half]
    operation = middle.operation
    if operation.name == "z":
        written = set()
    elif isinstance(operation, ControlledGate) and operation.base_gate.name == "x":
        written = set(middle.qubits[operation.num_ctrl_qubits :])
    else:
        written = set(middle.qubits)
    if any(written & set(inst.qubits) for inst in data[:half]):
        return None
    return (0, half)


def _encoding(
    problem: ColoringProblem, regime: str, balanced: bool = False, tree: str = "input"
) -> ColoringEncoding:
    _, complete = REGIMES[regime]
    if complete:
        return encode_coloring(problem, balanced=balanced, tree=tree)
    bits = max(1, (problem.colors - 1).bit_length())
    return encode_coloring(
        replace(problem, colors=1 << bits), balanced=balanced, tree=tree
    )


def logique_instance(
    problem: ColoringProblem,
    method: str,
    regime: str,
    *,
    executable=None,
    parameters: dict | None = None,
    verification: dict | None = None,
    timeout: float = 180,
    balanced: bool = False,
    tree: str = "input",
    mc_reduction: bool = False,
    optimization: str = "refactor",
    schedule: bool = False,
) -> SearchInstance:
    """Synthesize the regime's predicate and wrap it as a verified oracle.

    The raw circuit is used directly with its output in |-> when it passes the
    kick-back check for both target values; otherwise the oracle is
    compute–phase–uncompute. ``verification`` holds keyword arguments for
    ``verification_assignments``; ``balanced``, ``tree``, ``mc_reduction`` and
    ``optimization`` select the encoder structure and the shape of its final
    conjunction, the multiplicative-complexity pass and the native bridge's
    optimization. With ``schedule``, a kick-back oracle is reordered to a lower
    T-depth with the same gates (``benchmarks.scheduling``): around its output
    gate when its second half undoes its first, otherwise as a whole. The new
    order is kept only when it prices shallower, and it is verified again;
    ``structure["scheduled"]`` records whether that happened.
    """
    from logique.synthesis import synthesize
    from logique.verification import (
        verification_assignments,
        verify_kickback_oracle,
        verify_phase_oracle,
    )

    if regime not in REGIMES:
        raise ValueError(f"regime must be one of {sorted(REGIMES)}")
    timings = {}
    started = time.perf_counter()
    encoding = _encoding(problem, regime, balanced, tree)
    result = synthesize(
        encoding,
        method,
        executable=executable,
        timeout=timeout,
        mc_reduction=mc_reduction,
        optimization=optimization,
        **(parameters or {}),
    )
    timings["synthesis_s"] = time.perf_counter() - started
    timings["native_s"] = result.metadata.get("native_seconds")
    started = time.perf_counter()
    assignments, coverage = verification_assignments(encoding, **(verification or {}))
    inputs = result.metadata["input_qubits"]
    output = result.metadata["output_qubits"][0]
    # Exhaustive coverage is reported as such rather than as explicit inputs.
    chosen = None if coverage["status"] == "exhaustive" else assignments
    try:
        report = verify_kickback_oracle(result, encoding=encoding, assignments=chosen)
        oracle, form, target = result.circuit, "kick-back", output
    except AssertionError:
        report = verify_phase_oracle(result, encoding=encoding, assignments=chosen)
        oracle, form, target = result.phase_oracle(), "phase", None
    scheduled = False
    from logique.benchmarks.costs import is_mcx

    # Multi-controlled gates are timed only once expanded: such oracles are
    # scheduled by the study after decomposition (``expand_oracle``).
    expandable = any(is_mcx(inst.operation, 3) for inst in oracle.data)
    if schedule and form == "kick-back" and not expandable:
        from logique.benchmarks.scheduling import (
            mirrored_middle,
            priced_t_depth,
            reschedule,
            reschedule_mirrored,
        )
        from logique.verification.phase import verify_xor_oracle

        candidate = None
        middle = mirrored_middle(oracle, output)
        if middle is not None:
            try:
                candidate = reschedule_mirrored(oracle, middle)
            except ValueError:
                candidate = None
        if candidate is None or candidate is oracle:
            # Without the mirrored structure, the whole oracle is reordered;
            # swapping commuting gates keeps it exactly.
            candidate = reschedule(oracle)
            if priced_t_depth(candidate) >= priced_t_depth(oracle):
                candidate = oracle
        if candidate is not oracle:
            verify_xor_oracle(
                candidate,
                data=inputs,
                target=output,
                encoding=encoding,
                assignments=chosen,
            )
            oracle, scheduled = candidate, True
    timings["verification_s"] = time.perf_counter() - started
    workspace = sorted(set(range(oracle.num_qubits)) - set(inputs) - {output})
    preparation, diffusion, domain = _assemble(
        problem, regime, inputs, oracle.num_qubits, target, form == "kick-back"
    )
    summary = result.summary()
    structure = {
        key: summary[key]
        for key in (
            "AND",
            "XOR",
            "LUT",
            "multiplicative_depth",
            "workspace",
            "gate_types",
        )
    }
    structure.update(tree=tree, scheduled=scheduled)
    return SearchInstance(
        method=method,
        regime=regime,
        preparation=preparation,
        oracle=oracle,
        diffusion=diffusion,
        data=list(inputs),
        roles={"data": list(inputs), "output": [output], "workspace": workspace},
        clean=workspace if form == "kick-back" else [*workspace, output],
        form=form,
        domain=domain,
        encoding=encoding,
        validation={**report, "coverage": coverage},
        timings=timings,
        structure=structure,
        mirrored=_mirror_span(oracle),
    )


def baseline_instance(
    problem: ColoringProblem,
    variant: str,
    regime: str,
    *,
    verification: dict | None = None,
) -> SearchInstance:
    """Wrap a Saha–Belletti oracle; R3 builds it without invalid-color checks."""
    from logique.synthesis.saha_belletti import baseline_oracle
    from logique.verification import verification_assignments, verify_xor_oracle

    if regime not in REGIMES:
        raise ValueError(f"regime must be one of {sorted(REGIMES)}")
    _, complete = REGIMES[regime]
    timings = {}
    started = time.perf_counter()
    oracle = baseline_oracle(problem, variant, domain_checks=complete)
    timings["synthesis_s"] = time.perf_counter() - started
    encoding = _encoding(problem, regime)
    started = time.perf_counter()
    assignments, coverage = verification_assignments(encoding, **(verification or {}))
    report = verify_xor_oracle(
        oracle.circuit,
        data=oracle.data,
        target=oracle.target,
        encoding=encoding,
        assignments=None if coverage["status"] == "exhaustive" else assignments,
    )
    timings["verification_s"] = time.perf_counter() - started
    width = oracle.circuit.num_qubits
    preparation, diffusion, domain = _assemble(
        problem, regime, oracle.data, width, oracle.target, True
    )
    return SearchInstance(
        method=f"sb_{variant}",
        regime=regime,
        preparation=preparation,
        oracle=oracle.circuit,
        diffusion=diffusion,
        data=oracle.data,
        roles={
            "data": oracle.data,
            "output": [oracle.target],
            "ancillas": oracle.ancillas,
        },
        clean=oracle.ancillas,
        form="kick-back",
        domain=domain,
        encoding=encoding,
        validation={**report, "coverage": coverage},
        timings=timings,
        mirrored=oracle.compute,
        structure={"gate_types": dict(oracle.circuit.count_ops())},
    )
