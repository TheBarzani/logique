"""Constructions that prepare the valid colors of every vertex.

The Shukla–Vedula circuit prepares the uniform superposition over k codes with
one y-rotation per vertex when k = 2^l·3 or 2^l·5, which covers the numbers of
colors of the benchmark graphs. The alternatives below make that rotation
cheaper or exact:

* exact repeat-until-success rotations, built from Clifford+T circuits whose
  success branch applies the rotation exactly and whose failure branch is
  undone by a Clifford gate before the next attempt;
* Hamming-weight phasing (Gidney, arXiv:1709.06648), which applies the same
  rotation to n vertices with about log2(n) rotations and an adder network;
* amplitude-amplified preparation (Babbush et al., arXiv:1805.03662), which
  prepares the 2^c codes with Hadamard gates and removes the unused ones with
  one exact round of amplitude amplification.

Every construction returns its ancillas clean and acts coherently, so it can be
used both as the preparation and inside the diffusion operator.
"""

from dataclasses import dataclass
from fractions import Fraction
import math

from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RCCXGate
from qiskit.circuit.library.data_preparation.state_preparation import (
    UniformSuperpositionGate,
)

PREPARATIONS = (
    "shukla_vedula",
    "exact_rus",
    "hamming_weight",
    "amplitude_amplified",
)


@dataclass(frozen=True)
class ExactRotation:
    """A repeat-until-success circuit for one z-rotation of the preparation.

    ``attempt`` acts on the target (qubit 0) and its ancillas, which start in
    |0>. Measuring the ancillas gives ``success`` (ancilla bits, first ancilla
    last) with probability ``probability``; the target then holds Rz(angle) up
    to a global phase. Any other outcome leaves the target unchanged, or
    requires the Clifford ``recovery``, and the attempt is repeated.
    """

    denominator: int
    angle: float
    attempt: QuantumCircuit
    success: str
    probability: Fraction
    recovery: str | None
    t_per_attempt: int
    t_depth_per_attempt: int
    reference: str

    @property
    def expected_t(self) -> float:
        return self.t_per_attempt / float(self.probability)

    @property
    def expected_t_depth(self) -> float:
        return self.t_depth_per_attempt / float(self.probability)


def _split_angle(denominator: int) -> float:
    """The Shukla–Vedula angle that leaves 1/denominator on the upper code."""
    return -2 * math.acos(math.sqrt(1 / denominator))


def _attempt_three() -> QuantumCircuit:
    """Two-T attempt found by an exhaustive T-count search over Pauli rotations.

    The unitary is (1/2)[[B, -I], [I, B^dagger]] with B = I + i·sqrt(2)·Z, so
    the ancilla outcome 0 applies B/sqrt(3) and the outcome 1 the identity.
    """
    qc = QuantumCircuit(2)
    target, ancilla = 0, 1
    qc.sdg(ancilla)
    qc.h(ancilla)
    qc.tdg(ancilla)
    qc.h(ancilla)
    qc.sdg(ancilla)
    qc.cx(target, ancilla)
    qc.t(ancilla)
    qc.cx(target, ancilla)
    qc.z(target)
    qc.s(target)
    qc.x(ancilla)
    qc.s(ancilla)
    qc.h(ancilla)
    qc.s(ancilla)
    qc.cx(target, ancilla)
    return qc


def _attempt_five() -> QuantumCircuit:
    """Jones's single-AND attempt for V3 (Paetznick and Svore, Figure 1b).

    Two ancillas in |+> drive a temporary logical-AND into a third; a
    CNOT–S–CNOT on the target then applies S or X·S·X depending on the AND.
    The X-basis outcome 00 applies Rz(arccos(3/5)); the others apply Z. The
    trailing Z turns the rotation into the Shukla–Vedula angle and the failure
    branches into the identity.
    """
    qc = QuantumCircuit(4)
    target, a, b, t = range(4)
    qc.h([a, b])
    qc.append(RCCXGate(), [a, b, t])
    qc.cx(t, target)
    qc.s(target)
    qc.cx(t, target)
    qc.append(RCCXGate().inverse(), [a, b, t])
    qc.h([a, b])
    qc.z(target)
    return qc


EXACT_ROTATIONS = {
    3: ExactRotation(
        denominator=3,
        angle=_split_angle(3),
        attempt=_attempt_three(),
        success="0",
        probability=Fraction(3, 4),
        recovery=None,
        t_per_attempt=2,
        t_depth_per_attempt=2,
        reference="Exact synthesis over Z[i, 1/sqrt(2)] (Paetznick and Svore, arXiv:1311.1074, Section 3.1)",
    ),
    5: ExactRotation(
        denominator=5,
        angle=_split_angle(5),
        attempt=_attempt_five(),
        success="000",
        probability=Fraction(5, 8),
        recovery=None,
        t_per_attempt=4,
        t_depth_per_attempt=2,
        reference="Jones's circuit for V3 (Paetznick and Svore, arXiv:1311.1074, Figure 1b)",
    ),
}


class ExactRotationGate(Gate):
    """Ry(±angle) realized by an exact repeat-until-success circuit.

    The gate's definition is the exact rotation, so simulations and operator
    checks see the intended unitary; cost models read ``expected_t`` and
    ``expected_t_depth`` instead of lowering it. Ry(angle) equals
    S·H·Rz(angle)·H·S^dagger, and its inverse is X·Ry(angle)·X.
    """

    def __init__(self, denominator: int, inverse: bool = False):
        rotation = EXACT_ROTATIONS[denominator]
        self.denominator = denominator
        self.inverted = inverse
        self.expected_t = rotation.expected_t
        self.expected_t_depth = rotation.expected_t_depth
        name = f"rus_ry{denominator}" + ("_dg" if inverse else "")
        super().__init__(name, 1, [], label=name)

    def _define(self):
        angle = EXACT_ROTATIONS[self.denominator].angle
        qc = QuantumCircuit(1)
        qc.ry(-angle if self.inverted else angle, 0)
        self.definition = qc

    def inverse(self, annotated: bool = False):
        return ExactRotationGate(self.denominator, not self.inverted)


def _exact_denominator(angle: float) -> tuple[int, bool] | None:
    for denominator, rotation in EXACT_ROTATIONS.items():
        if math.isclose(angle, rotation.angle, abs_tol=1e-9):
            return denominator, False
        if math.isclose(angle, -rotation.angle, abs_tol=1e-9):
            return denominator, True
    return None


def shukla_vedula(colors: int) -> QuantumCircuit:
    """The Shukla–Vedula circuit over the codes 0, ..., colors - 1, low bit first."""
    width = max(1, (colors - 1).bit_length())
    qc = QuantumCircuit(width)
    if colors > 1:
        qc.append(UniformSuperpositionGate(colors), range(width))
    return qc.decompose()


def with_exact_rotations(circuit: QuantumCircuit) -> QuantumCircuit:
    """Replace every uncontrolled y-rotation that has an exact circuit."""
    result = circuit.copy_empty_like()
    for inst in circuit.data:
        operation = inst.operation
        match = (
            _exact_denominator(float(operation.params[0]))
            if operation.name == "ry"
            else None
        )
        if match is None:
            result.append(operation, inst.qubits, inst.clbits)
        else:
            result.append(ExactRotationGate(*match), inst.qubits)
    return result


def _adders(n: int) -> list[tuple]:
    """Gidney's reduction of n weight-one wires to a binary Hamming weight.

    Returns the adders as ("full", a, b, c, carry) or ("half", a, b, carry)
    over wire labels, where targets are 0..n-1 and carries are numbered from n,
    followed by ("weight", w, wire) entries for the bits of the weight.
    """
    pools: dict[int, list[int]] = {1: list(range(n))}
    steps: list[tuple] = []
    carry = n
    weight = 1
    while weight in pools:
        wires = pools[weight]
        while len(wires) >= 3:
            a, b, c = wires.pop(), wires.pop(), wires.pop()
            steps.append(("full", a, b, c, carry))
            wires.insert(0, c)
            pools.setdefault(2 * weight, []).append(carry)
            carry += 1
        if len(wires) == 2:
            a, b = wires.pop(), wires.pop()
            steps.append(("half", a, b, carry))
            wires.append(b)
            pools.setdefault(2 * weight, []).append(carry)
            carry += 1
        steps.extend(("weight", weight, wire) for wire in wires)
        weight *= 2
    return steps


def hamming_weight_ancillas(n: int) -> int:
    """Clean ancillas needed to phase n wires by their Hamming weight."""
    return sum(step[0] in ("full", "half") for step in _adders(n))


def hamming_weight_phasing(n: int, angle: float) -> QuantumCircuit:
    """Rz(angle) on wires 0..n-1, up to a global phase, through their weight.

    The adders compute the Hamming weight with temporary logical-AND gates
    into clean ancillas (wires n onward), Rz(angle·w) acts on the bit of
    weight w, and the adders are undone. The AND gates use relative phases,
    which cancel because only diagonal gates act between computation and
    uncomputation.
    """
    steps = _adders(n)
    compute = QuantumCircuit(n + hamming_weight_ancillas(n))
    for step in steps:
        if step[0] == "full":
            _, a, b, c, carry = step
            compute.cx(c, a)
            compute.cx(c, b)
            compute.append(RCCXGate(), [a, b, carry])
            compute.cx(c, carry)
            compute.cx(a, c)
            compute.cx(b, c)
        elif step[0] == "half":
            _, a, b, carry = step
            compute.append(RCCXGate(), [a, b, carry])
            compute.cx(a, b)
    qc = compute.copy()
    for step in steps:
        if step[0] == "weight":
            qc.rz(angle * step[1], step[2])
    qc.compose(compute.inverse(), inplace=True)
    return qc


def _lockstep(local: QuantumCircuit, groups, width: int, phased: bool):
    """Apply one vertex circuit to every group, phasing its y-rotations jointly.

    The circuit is cut at each uncontrolled y-rotation; every segment runs on
    all groups, and each rotation layer becomes one Hamming-weight phasing on
    the rotated wires (conjugated from z to y by S·H), with ancillas appended
    after ``width`` data wires.
    """
    segments: list[list] = [[]]
    angles: list[tuple[float, int]] = []
    for inst in local.data:
        if phased and inst.operation.name == "ry" and len(groups) > 1:
            angles.append(
                (float(inst.operation.params[0]), local.find_bit(inst.qubits[0]).index)
            )
            segments.append([])
        else:
            segments[-1].append(inst)
    ancillas = hamming_weight_ancillas(len(groups)) if angles else 0
    qc = QuantumCircuit(width + ancillas)
    for index, segment in enumerate(segments):
        for group in groups:
            for inst in segment:
                wires = [group[local.find_bit(q).index] for q in inst.qubits]
                qc.append(inst.operation, wires)
        if index < len(angles):
            angle, position = angles[index]
            rotated = [group[position] for group in groups]
            layer = hamming_weight_phasing(len(groups), angle)
            qc.sdg(rotated)
            qc.h(rotated)
            qc.compose(layer, [*rotated, *range(width, width + ancillas)], inplace=True)
            qc.h(rotated)
            qc.s(rotated)
    return qc


def _comparator(width: int, bound: int) -> QuantumCircuit:
    """Flag (wire ``width``) the codes x < bound on wires 0..width-1.

    x >= bound exactly when x first differs from bound - 1, scanning from the
    top bit, at a bit where x is 1 and bound - 1 is 0. These cases are
    disjoint, so each contributes one multi-controlled X on the flag; the final
    X turns the flag into x < bound.
    """
    qc = QuantumCircuit(width + 1)
    flag = width
    limit = bound - 1
    for i in reversed(range(width)):
        if (limit >> i) & 1:
            continue
        controls = list(range(i, width))
        state = 1 << 0  # bit i must be 1
        for j, wire in enumerate(controls[1:], start=1):
            if (limit >> wire) & 1:
                state |= 1 << j
        qc.mcx(controls, flag, ctrl_state=state)
    qc.x(flag)  # flag x < bound
    return qc


def amplitude_amplified(colors: int) -> QuantumCircuit:
    """Uniform superposition over colors codes by one exact amplification round.

    For colors = 2^l·m with m odd, l low wires receive Hadamard gates and the m
    codes of the upper wires are prepared as in Babbush et al. (Figure 12):
    Hadamard gates and Ry(phi) on an extra wire give the good states (x < m,
    extra wire |0>) total probability 1/4, so one Grover iteration reaches them
    exactly. Wires: data (low bit first), the extra wire, then the comparator
    flag; both extra wires end in |0>.
    """
    width = max(1, (colors - 1).bit_length())
    low = (colors & -colors).bit_length() - 1
    odd = colors >> low
    high = width - low
    qc = QuantumCircuit(width + 2)
    if low:
        qc.h(range(low))
    if odd == 1:
        return qc
    data = list(range(low, width))
    extra, flag = width, width + 1
    phi = 2 * math.acos(math.sqrt((1 << high) / (4 * odd)))

    def initial(circuit, inverse=False):
        circuit.ry(-phi if inverse else phi, extra)
        circuit.h(data)

    comparator = _comparator(high, odd)
    initial(qc)
    # Reflect about the good states: phase -1 on x < odd with the extra wire 0.
    qc.compose(comparator, [*data, flag], inplace=True)
    qc.x(extra)
    qc.cz(flag, extra)
    qc.x(extra)
    qc.compose(comparator.inverse(), [*data, flag], inplace=True)
    # Reflect about the initial state.
    initial(qc, inverse=True)
    qc.x([*data, extra])
    qc.h(extra)
    qc.mcx(data, extra)
    qc.h(extra)
    qc.x([*data, extra])
    initial(qc)
    qc.global_phase += math.pi
    return qc


def search_preparation(problem, groups, method: str) -> QuantumCircuit:
    """Prepare every vertex register; ancillas follow the data wires.

    ``groups`` lists each vertex's wires, low bit first, in vertex order. The
    method chooses the construction; precolored vertices are set to their
    color. The returned circuit acts on the data wires and the ancillas the
    method needs, all of which start and end in |0>.
    """
    if method not in PREPARATIONS:
        raise ValueError(f"method must be one of {PREPARATIONS}")
    width = max((q for group in groups for q in group), default=-1) + 1
    free = [
        group
        for vertex, group in zip(problem.vertices, groups)
        if vertex not in problem.precolored
    ]
    if method == "amplitude_amplified":
        local = amplitude_amplified(problem.colors)
        extra = local.num_qubits - len(groups[0])
        qc = QuantumCircuit(width + extra)
        for group in free:
            qc.compose(local, [*group, *range(width, width + extra)], inplace=True)
    else:
        local = shukla_vedula(problem.colors)
        if method == "exact_rus":
            local = with_exact_rotations(local)
        qc = _lockstep(local, free, width, phased=method == "hamming_weight")
    for vertex, group in zip(problem.vertices, groups):
        color = problem.precolored.get(vertex)
        if color is not None:
            for bit, q in enumerate(group):
                if (color >> bit) & 1:
                    qc.x(q)
    return qc
