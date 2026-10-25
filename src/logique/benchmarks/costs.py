"""Explicit decompositions and fault-tolerant cost models.

Multi-controlled X gates are expanded by a named construction before anything is
counted, so workspace and T gates come from explicit circuits rather than
analytical weights. Clifford+T lowering uses fixed phase-polynomial gadgets with
exact T counts; arbitrary-angle rotations are counted separately and priced only
through a stated synthesis estimate.
"""

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Callable

from qiskit import AncillaRegister, QuantumCircuit, transpile
from qiskit.circuit import ControlledGate
from qiskit.circuit.library import CHGate
from qiskit.synthesis.multi_controlled import mcx_synthesis as _mcx

CLIFFORD_T_BASIS = ("h", "s", "sdg", "t", "tdg", "x", "y", "z", "sx", "sxdg", "cx")
TOFFOLI_GATES = ("ccx", "rccx", "rccx_dg", "ccrx")
_DIRECTIVES = ("barrier", "measure", "reset", "delay")


@dataclass(frozen=True)
class MCXDecomposition:
    """A construction acting on controls, then the target, then its ancillas."""

    name: str
    workspace: str  # "none", "clean", "dirty" or "throwaway"
    reference: str
    build: Callable[[int], QuantumCircuit]


def _tree(controls: int, *, uncompute: bool) -> QuantumCircuit:
    """Combine controls pairwise into n - 2 clean ancillas, then the target."""
    qc = QuantumCircuit(2 * controls - 1)
    layer = list(range(controls))
    ancillas = iter(range(controls + 1, 2 * controls - 1))
    computed = []
    while len(layer) > 2:
        merged = []
        for left, right in zip(layer[::2], layer[1::2]):
            node = next(ancillas)
            qc.ccx(left, right, node)
            computed.append((left, right, node))
            merged.append(node)
        layer = merged + ([layer[-1]] if len(layer) % 2 else [])
    qc.ccx(layer[0], layer[1], controls)
    if uncompute:
        for left, right, node in reversed(computed):
            qc.ccx(left, right, node)
    return qc


_KG24 = "Khattar and Gidney, Quantum 9, 1752 (2025)"
MCX_DECOMPOSITIONS = {
    item.name: item
    for item in (
        MCXDecomposition(
            "noaux_v24",
            "none",
            "Vale et al., arXiv:2302.06377",
            _mcx.synth_mcx_noaux_v24,
        ),
        MCXDecomposition(
            "gray_code",
            "none",
            "Barenco et al., Phys. Rev. A 52, 3457 (1995)",
            _mcx.synth_mcx_gray_code,
        ),
        MCXDecomposition(
            "1_clean_b95",
            "clean",
            "Barenco et al. (1995); Iten et al., Phys. Rev. A 93, 032318 (2016)",
            _mcx.synth_mcx_1_clean_b95,
        ),
        MCXDecomposition(
            "n_clean_m15",
            "clean",
            "Maslov, Phys. Rev. A 93, 022311 (2016)",
            _mcx.synth_mcx_n_clean_m15,
        ),
        MCXDecomposition(
            "n_dirty_i15",
            "dirty",
            "Iten et al., Phys. Rev. A 93, 032318 (2016)",
            _mcx.synth_mcx_n_dirty_i15,
        ),
        MCXDecomposition("1_clean_kg24", "clean", _KG24, _mcx.synth_mcx_1_clean_kg24),
        MCXDecomposition("1_dirty_kg24", "dirty", _KG24, _mcx.synth_mcx_1_dirty_kg24),
        MCXDecomposition("2_clean_kg24", "clean", _KG24, _mcx.synth_mcx_2_clean_kg24),
        MCXDecomposition("2_dirty_kg24", "dirty", _KG24, _mcx.synth_mcx_2_dirty_kg24),
        MCXDecomposition(
            "clean_tree",
            "clean",
            "Toffoli tree with uncomputation",
            lambda n: _tree(n, uncompute=True),
        ),
        MCXDecomposition(
            "throwaway_tree",
            "throwaway",
            "Toffoli tree without uncomputation (manuscript Figure 1)",
            lambda n: _tree(n, uncompute=False),
        ),
    )
}


@lru_cache(maxsize=256)
def _construction(method: str, controls: int) -> QuantumCircuit:
    return MCX_DECOMPOSITIONS[method].build(controls)


def _is_mcx(operation, min_controls: int) -> bool:
    return (
        isinstance(operation, ControlledGate)
        and operation.base_gate.name == "x"
        and operation.num_ctrl_qubits >= min_controls
    )


def decompose_mcx(
    circuit: QuantumCircuit, method: str, *, clean_wires=(), min_controls: int = 3
) -> tuple[QuantumCircuit, dict]:
    """Expand every X gate with at least ``min_controls`` controls.

    ``clean_wires`` are qubits the caller guarantees to be |0> whenever such a
    gate acts, for example restored oracle workspace during diffusion. Clean
    constructions use them before appended ancillas, which they also reuse;
    dirty constructions borrow wires outside the gate. A throwaway tree leaves
    garbage on fresh ancillas, so its result is valid only inside a block that
    is later inverted, which restores every ancilla.
    """
    if method not in MCX_DECOMPOSITIONS:
        raise ValueError(f"method must be one of {sorted(MCX_DECOMPOSITIONS)}")
    workspace = MCX_DECOMPOSITIONS[method].workspace
    clean = [circuit.qubits[q] if isinstance(q, int) else q for q in clean_wires]
    if workspace == "throwaway" and clean:
        raise ValueError("A throwaway tree leaves garbage; it cannot use clean_wires")
    gates = [
        (inst, inst.operation.num_ctrl_qubits)
        for inst in circuit.data
        if _is_mcx(inst.operation, min_controls)
    ]
    needs = [
        _construction(method, controls).num_qubits - controls - 1
        for _, controls in gates
    ]
    for inst, _ in gates:
        if set(inst.qubits) & set(clean):
            raise ValueError("clean_wires must not act as controls or targets")
    if workspace == "clean":
        fresh = max([0, *(need - len(clean) for need in needs)])
    elif workspace == "dirty":
        fresh = max(
            [
                0,
                *(
                    need - (circuit.num_qubits - c - 1)
                    for need, (_, c) in zip(needs, gates)
                ),
            ]
        )
    elif workspace == "throwaway":
        fresh = sum(needs)
    else:
        fresh = 0
    result = circuit.copy_empty_like()
    appended = []
    if fresh:
        register = AncillaRegister(fresh, "mcx_ancilla")
        result.add_register(register)
        appended = list(register)
    cursor = 0
    borrowed = 0
    for inst in circuit.data:
        operation = inst.operation
        if not _is_mcx(operation, min_controls):
            result.append(operation, inst.qubits, inst.clbits, copy=False)
            continue
        controls = operation.num_ctrl_qubits
        construction = _construction(method, controls)
        need = construction.num_qubits - controls - 1
        involved = set(inst.qubits)
        if workspace == "clean":
            ancillas = (clean + appended)[:need]
        elif workspace == "dirty":
            spare = [q for q in result.qubits if q not in involved]
            ancillas = spare[:need]
            borrowed = max(borrowed, sum(q not in appended for q in ancillas))
        elif workspace == "throwaway":
            ancillas = appended[cursor : cursor + need]
            cursor += need
        else:
            ancillas = []
        opened = [
            q
            for i, q in enumerate(inst.qubits[:controls])
            if not (operation.ctrl_state >> i) & 1
        ]
        if opened:
            result.x(opened)
        result.compose(
            construction, qubits=[*inst.qubits[: controls + 1], *ancillas], inplace=True
        )
        if opened:
            result.x(opened)
    info = {
        "mcx_method": method,
        "mcx_workspace": workspace,
        "mcx_reference": MCX_DECOMPOSITIONS[method].reference,
        "mcx_gates": len(gates),
        "max_controls": max((c for _, c in gates), default=0),
        "appended_ancillas": fresh,
        "borrowed_dirty_wires": borrowed,
        "clean_wires_used": (
            min(len(clean), max(needs, default=0)) if workspace == "clean" else 0
        ),
        "garbage_ancillas": fresh if workspace == "throwaway" else 0,
    }
    return result, info


def _ccz() -> QuantumCircuit:
    """Exact CCZ with seven T gates in three T layers."""
    qc = QuantumCircuit(3)
    a, b, c = range(3)
    qc.t([a, b, c])
    qc.cx(a, b)
    qc.cx(a, c)
    qc.cx(b, a)
    qc.cx(c, a)  # wires hold a^b^c, a^b, a^c
    qc.t(a)
    qc.tdg([b, c])
    qc.cx(b, c)  # c holds b^c
    qc.tdg(c)
    qc.cx(b, c)
    qc.cx(c, a)
    qc.cx(b, a)
    qc.cx(a, c)
    qc.cx(a, b)
    return qc


def _ccrz_pi(sign: int) -> QuantumCircuit:
    """Exact doubly controlled Rz(sign * pi) with four T gates in two T layers."""
    qc = QuantumCircuit(3)
    c1, c2, t = range(3)
    plus, minus = (qc.t, qc.tdg) if sign > 0 else (qc.tdg, qc.t)
    qc.cx(t, c1)
    qc.cx(t, c2)  # wires hold c1^t, c2^t, t
    minus(c1)
    minus(c2)
    plus(t)
    qc.cx(c2, c1)
    qc.cx(t, c1)  # c1 holds c1^c2^t
    plus(c1)
    qc.cx(t, c1)
    qc.cx(c2, c1)
    qc.cx(t, c2)
    qc.cx(t, c1)
    return qc


@lru_cache(maxsize=None)
def _gadget(name: str) -> QuantumCircuit:
    qc = QuantumCircuit(3 if name != "ch" else 2)
    if name == "ccx":
        qc.h(2)
        qc.compose(_ccz(), inplace=True)
        qc.h(2)
    elif name in ("ccrx+", "ccrx-"):
        qc.h(2)
        qc.compose(_ccrz_pi(1 if name == "ccrx+" else -1), inplace=True)
        qc.h(2)
    elif name == "rccx":
        qc.h(2)
        qc.compose(_ccrz_pi(1), inplace=True)
        qc.cx(0, 2)
        qc.h(2)
    elif name == "rccx_dg":
        qc = _gadget("rccx").inverse()
    elif name == "ch":
        qc = CHGate().definition
    return qc


def _gadget_name(operation) -> str | None:
    name = operation.name
    if name in ("rccx", "rccx_dg"):
        return name
    if not isinstance(operation, ControlledGate):
        return None
    base, controls = operation.base_gate.name, operation.num_ctrl_qubits
    if base == "x" and controls == 2:
        return "ccx"
    if base == "h" and controls == 1:
        return "ch"
    if base == "rx" and controls == 2:
        angle = float(operation.base_gate.params[0])
        if math.isclose(abs(angle), math.pi, abs_tol=1e-12):
            return "ccrx+" if angle > 0 else "ccrx-"
    return None


def _snap_rotations(circuit: QuantumCircuit, tolerance: float) -> QuantumCircuit:
    """Replace rz rotations by multiples of pi/4 with exact Clifford+T gates."""
    phases = {1: ["t"], 2: ["s"], 3: ["s", "t"], 4: ["z"], 5: ["z", "t"]}
    phases.update({6: ["sdg"], 7: ["tdg"]})
    result = circuit.copy_empty_like()
    for inst in circuit.data:
        operation = inst.operation
        if operation.name != "rz":
            result.append(operation, inst.qubits, inst.clbits, copy=False)
            continue
        angle = float(operation.params[0])
        steps = angle / (math.pi / 4)
        if abs(steps - round(steps)) > tolerance:
            result.append(operation, inst.qubits, inst.clbits, copy=False)
            continue
        # rz(angle) equals the phase gate p(angle) up to exp(-i angle / 2).
        result.global_phase -= angle / 2
        for gate in phases.get(round(steps) % 8, []):
            getattr(result, gate)(inst.qubits[0])
    return result


def clifford_t(circuit: QuantumCircuit, *, tolerance: float = 1e-9) -> QuantumCircuit:
    """Lower to Clifford+T, leaving only arbitrary-angle rotations as rz gates.

    Toffoli, relative-phase Toffoli, controlled-Rx(±pi) and controlled-Hadamard
    gates use fixed exact gadgets (7, 4, 4 and 2 T gates). Multi-controlled X
    gates must first be expanded with decompose_mcx(); other gates are
    translated by Qiskit, and rotations by multiples of pi/4 become T, S and Z.
    """
    staged = circuit.copy_empty_like()
    for inst in circuit.data:
        operation = inst.operation
        if _is_mcx(operation, 3):
            raise ValueError("Expand multi-controlled X gates with decompose_mcx()")
        name = _gadget_name(operation)
        if name is None:
            staged.append(operation, inst.qubits, inst.clbits, copy=False)
            continue
        opened = (
            [
                q
                for i, q in enumerate(inst.qubits[: operation.num_ctrl_qubits])
                if not (operation.ctrl_state >> i) & 1
            ]
            if isinstance(operation, ControlledGate)
            else []
        )
        if opened:
            staged.x(opened)
        staged.compose(_gadget(name), qubits=inst.qubits, inplace=True)
        if opened:
            staged.x(opened)
    lowered = transpile(
        staged, basis_gates=[*CLIFFORD_T_BASIS, "rz"], optimization_level=0
    )
    return _snap_rotations(lowered, tolerance)


def weighted_depth(circuit: QuantumCircuit, weights: dict, default: float = 0) -> float:
    """Longest dependency path, weighting each gate by its name; directives are ignored."""
    level = [0.0] * circuit.num_qubits
    for inst in circuit.data:
        if inst.operation.name in _DIRECTIVES:
            continue
        wires = [circuit.find_bit(q).index for q in inst.qubits]
        if not wires:
            continue
        reached = max(level[w] for w in wires) + weights.get(
            inst.operation.name, default
        )
        for w in wires:
            level[w] = reached
    return max(level, default=0.0)


def toffoli_metrics(circuit: QuantumCircuit) -> dict:
    """Toffoli-family counts and depth after multi-controlled gates are expanded."""
    counts = {
        name: count
        for name, count in circuit.count_ops().items()
        if name not in _DIRECTIVES
    }
    family = {
        name: count
        for name, count in counts.items()
        if name.split("_o")[0] in TOFFOLI_GATES
    }
    return {
        "qubits": circuit.num_qubits,
        "toffoli_count": sum(family.values()),
        "toffoli_depth": weighted_depth(circuit, {name: 1 for name in family}),
        "toffoli_types": family,
        "metric_level": "toffoli",
    }


def ft_metrics(circuit: QuantumCircuit, *, rotation_t: int | None = None) -> dict:
    """Count a Clifford+T circuit whose remaining rz gates are rotations.

    With ``rotation_t`` (T gates per synthesized rotation), totals also price
    the rotations; without it, rotations are reported only as counts.
    """
    counts = {
        name: count
        for name, count in circuit.count_ops().items()
        if name not in _DIRECTIVES
    }
    unknown = set(counts) - {*CLIFFORD_T_BASIS, "rz"}
    if unknown:
        raise ValueError(f"Lower to Clifford+T first; found {sorted(unknown)}")
    t_count = counts.get("t", 0) + counts.get("tdg", 0)
    rotations = counts.get("rz", 0)
    metrics = {
        "qubits": circuit.num_qubits,
        "t_count": t_count,
        "t_depth": weighted_depth(circuit, {"t": 1, "tdg": 1}),
        "rotation_count": rotations,
        "rotation_depth": weighted_depth(circuit, {"rz": 1}),
        "cx_count": counts.get("cx", 0),
        "gates": sum(counts.values()),
        "depth": weighted_depth(circuit, {}, default=1),
        "metric_level": "fault-tolerant",
    }
    if rotation_t is not None:
        metrics["rotation_t"] = rotation_t
        metrics["total_t_count"] = t_count + rotations * rotation_t
        metrics["total_t_depth"] = weighted_depth(
            circuit, {"t": 1, "tdg": 1, "rz": rotation_t}
        )
    return metrics


def rotation_t_count(epsilon: float) -> int:
    """Leading-order T count of one z-rotation approximated to precision epsilon.

    Ross and Selinger (arXiv:1403.2975) report 3 log2(1/epsilon) +
    O(log log(1/epsilon)) T gates in the typical case for ancilla-free
    Clifford+T approximation; the lower-order term is omitted here.
    """
    if not 0 < epsilon < 1:
        raise ValueError("epsilon must lie strictly between 0 and 1")
    return math.ceil(3 * math.log2(1 / epsilon))


def grover_success(p: float, iterations: int) -> float:
    """Ideal success probability after a number of iterations from success p."""
    if not 0 <= p <= 1 or type(iterations) is not int or iterations < 0:
        raise ValueError("p must lie in [0, 1] and iterations must be nonnegative")
    theta = math.asin(math.sqrt(p))
    return math.sin((2 * iterations + 1) * theta) ** 2


def optimal_iterations(p: float) -> int:
    """Iteration count reaching the first maximum of the ideal success probability."""
    if not 0 < p <= 1:
        raise ValueError("A positive initial success probability is required")
    best = math.pi / (4 * math.asin(math.sqrt(p))) - 0.5
    candidates = sorted({max(0, math.floor(best)), max(0, math.ceil(best))})
    return max(candidates, key=lambda j: grover_success(p, j))
