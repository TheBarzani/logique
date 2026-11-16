"""Reorder commuting gates so that a circuit's T-depth approaches its dependency bound.

Gates are never changed, only reordered. Two gates may swap when, on every wire
they share, both act diagonally in the same basis: both in the Z basis (controls,
Z-type phases) or both in the X basis (targets of X, CX, Toffoli or Rx gates).
Gates of any other kind, and barriers, keep their relative order. A greedy list
scheduler then places the gates in time steps of T-depth, giving priority to the
gate with the longest remaining T-path, and never places two gates on one wire
in the same step. Qiskit's depth counts any two gates on a wire as ordered, so
the order of commuting gates changes the measured T-depth.
"""

import heapq
from typing import Callable

from qiskit import QuantumCircuit
from qiskit.circuit import ControlledGate, Instruction

_Z_TYPE = {"z", "rz", "s", "sdg", "t", "tdg", "p", "u1"}
_X_TYPE = {"x", "rx"}


def _wire_kinds(circuit: QuantumCircuit, inst) -> dict[int, str | None]:
    """Basis in which the gate acts diagonally on each of its wires, or None."""
    op = inst.operation
    wires = [circuit.find_bit(q).index for q in inst.qubits]
    if isinstance(op, ControlledGate):
        base = op.base_gate.name
        target = "X" if base in _X_TYPE else "Z" if base in _Z_TYPE else None
        controls = {w: "Z" for w in wires[: op.num_ctrl_qubits]}
        return {**controls, **{w: target for w in wires[op.num_ctrl_qubits :]}}
    if op.name in _X_TYPE:
        return {wires[0]: "X"}
    if op.name in _Z_TYPE:
        return {wires[0]: "Z"}
    return {w: None for w in wires}


def t_depth_duration(operation: Instruction) -> int:
    """T-depth of one gate in the study's Clifford+T lowering (cached by gate)."""
    if operation.name in ("barrier", "measure", "reset", "delay"):
        return 0
    if operation.num_qubits == 1 and operation.name not in ("t", "tdg"):
        return 0
    if operation.name in ("cx", "cz", "swap"):
        return 0
    key = (
        operation.name,
        operation.num_qubits,
        tuple(float(p) for p in operation.params if isinstance(p, (int, float))),
        getattr(operation, "ctrl_state", None),
    )
    return _cached(key, operation)


_DEPTHS: dict = {}


def _cached(key, operation) -> int:
    if key not in _DEPTHS:
        from .costs import clifford_t, ft_metrics

        circuit = QuantumCircuit(operation.num_qubits)
        circuit.append(operation, range(operation.num_qubits))
        _DEPTHS[key] = int(ft_metrics(clifford_t(circuit))["t_depth"])
    return _DEPTHS[key]


def _dependencies(circuit: QuantumCircuit, instructions) -> list[set[int]]:
    """Predecessors of every gate in the commutation DAG."""
    groups: dict[int, tuple] = {}  # wire -> (kind, current group, previous group)
    preds = []
    for index, inst in enumerate(instructions):
        mine: set[int] = set()
        for wire, kind in _wire_kinds(circuit, inst).items():
            current_kind, current, previous = groups.get(wire, (None, [], []))
            if kind is not None and kind == current_kind:
                # Joins the current group of commuting gates on this wire.
                mine.update(previous)
                current.append(index)
                groups[wire] = (current_kind, current, previous)
            else:
                mine.update(current)
                groups[wire] = (kind, [index], current)
        preds.append(mine)
    return preds


def schedule_order(
    circuit: QuantumCircuit,
    instructions=None,
    duration: Callable[[Instruction], int] = t_depth_duration,
) -> tuple[list[int], int]:
    """Greedy list schedule of the instructions (default: all of the circuit's).

    Returns the new order as indices into the instructions and the dependency
    bound: the longest chain of non-commuting gates, weighted by duration.
    """
    instructions = list(circuit.data if instructions is None else instructions)
    n = len(instructions)
    if n == 0:
        return [], 0
    preds = _dependencies(circuit, instructions)
    succs: list[list[int]] = [[] for _ in range(n)]
    for j, ps in enumerate(preds):
        for i in ps:
            succs[i].append(j)
    dur = [duration(inst.operation) for inst in instructions]
    wires = [[circuit.find_bit(q).index for q in inst.qubits] for inst in instructions]
    tail = [0] * n  # longest remaining path, including the gate itself
    for i in reversed(range(n)):
        tail[i] = dur[i] + max((tail[j] for j in succs[i]), default=0)
    head = [0] * n
    for j in range(n):
        head[j] = max((head[i] + dur[i] for i in preds[j]), default=0)
    bound = max(head[i] + dur[i] for i in range(n))

    missing = [len(p) for p in preds]
    earliest = [0] * n
    ready = [i for i in range(n) if missing[i] == 0]
    free: dict[int, int] = {}
    order: list[int] = []
    start: dict[int, int] = {}
    t = 0
    events: list[int] = []
    while len(order) < n:
        placed = True
        while placed:
            placed = False
            ready.sort(key=lambda i: (-tail[i], i))
            waiting = []
            for i in ready:
                if earliest[i] <= t and all(free.get(w, 0) <= t for w in wires[i]):
                    start[i] = t
                    order.append(i)
                    finish = t + dur[i]
                    for w in wires[i]:
                        # A zero-duration gate still occupies its wires in order.
                        free[w] = max(free.get(w, 0), finish)
                    if finish > t:
                        heapq.heappush(events, finish)
                    for j in succs[i]:
                        earliest[j] = max(earliest[j], finish)
                        missing[j] -= 1
                        if missing[j] == 0:
                            waiting.append(j)
                            placed = True
                else:
                    waiting.append(i)
            ready = waiting
        if len(order) == n:
            break
        future = [e for e in events if e > t]
        future += [earliest[i] for i in ready if earliest[i] > t]
        future += [free[w] for i in ready for w in wires[i] if free.get(w, 0) > t]
        t = min(future)
    position = {i: k for k, i in enumerate(order)}
    order.sort(key=lambda i: (start[i], position[i]))
    return order, bound


def makespan(
    circuit: QuantumCircuit,
    order=None,
    duration: Callable[[Instruction], int] = t_depth_duration,
) -> int:
    """Duration of the circuit's gates in the given order, each started as early
    as its wires allow: the scheduling model of the T-depth."""
    free: dict[int, int] = {}
    end = 0
    for i in range(len(circuit.data)) if order is None else order:
        inst = circuit.data[i]
        wires = [circuit.find_bit(q).index for q in inst.qubits]
        finish = max((free.get(w, 0) for w in wires), default=0)
        finish += duration(inst.operation)
        for w in wires:
            free[w] = finish
        end = max(end, finish)
    return end


def reschedule(
    block: QuantumCircuit, duration: Callable[[Instruction], int] = t_depth_duration
) -> QuantumCircuit:
    """The same gates as ``block``, reordered; the unitary is unchanged.

    The greedy schedule is a heuristic, so the original order is kept when the
    schedule is not shorter under the same timing model.
    """
    order, _ = schedule_order(block, duration=duration)
    if makespan(block, order, duration) >= makespan(block, None, duration):
        order = list(range(len(block.data)))
    result = block.copy_empty_like()
    for i in order:
        inst = block.data[i]
        result.append(inst.operation, inst.qubits, inst.clbits)
    return result


def _letter(circuit: QuantumCircuit, inst) -> tuple:
    op = inst.operation
    return (
        op.name,
        tuple(round(float(p), 12) for p in op.params if isinstance(p, (int, float))),
        getattr(op, "ctrl_state", None),
        tuple(circuit.find_bit(q).index for q in inst.qubits),
    )


def reschedule_mirrored(
    circuit: QuantumCircuit,
    middle: int,
    duration: Callable[[Instruction], int] = t_depth_duration,
) -> QuantumCircuit:
    """Reorder an oracle B, G, U whose second half U uncomputes the first half B.

    ``middle`` is the position of the single gate G. B is rescheduled into S(B),
    which equals B as a unitary, and U is replaced by the exact inverse of S(B),
    giving S(B), G, S(B)^-1. U must consist of exactly the gates of B^-1 (a
    synthesized oracle may undo independent blocks of B in another order), which
    is checked; whether U equals B^-1 as a unitary is not, so the caller verifies
    the result against the predicate, as for any synthesized oracle.
    """
    data = circuit.data
    if not 0 <= middle < len(data) or 2 * middle + 1 != len(data):
        raise ValueError("The gate at the middle must split the circuit in halves")
    block = circuit.copy_empty_like()
    for inst in data[:middle]:
        block.append(inst.operation, inst.qubits, inst.clbits)
    inverse = block.inverse()
    if sorted(_letter(inverse, inst) for inst in inverse.data) != sorted(
        _letter(circuit, inst) for inst in data[middle + 1 :]
    ):
        raise ValueError("The second half does not consist of the inverse gates")
    scheduled = reschedule(block, duration)
    result = scheduled.copy()
    result.append(data[middle].operation, data[middle].qubits, data[middle].clbits)
    result.compose(scheduled.inverse(), inplace=True)
    return result


def mirrored_middle(circuit: QuantumCircuit, output: int) -> int | None:
    """Position of the single gate on ``output`` when the circuit mirrors around it."""
    touching = [
        k
        for k, inst in enumerate(circuit.data)
        if output in (circuit.find_bit(q).index for q in inst.qubits)
    ]
    if len(touching) != 1 or 2 * touching[0] + 1 != len(circuit.data):
        return None
    return touching[0]
