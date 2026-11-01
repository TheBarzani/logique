"""Bounded ideal k=3 dynamic instruments executed from Clifford/T primitives.

This is separate from static_ft and rus_accounting. The executor propagates
unnormalized amplitudes through gates, Z projections, classical branches and
reset, retaining every terminal record (including aborts). It never uses a
supplied Kraus operator to advance a state. NumPy/Qiskit are lazy dependencies.

Wire order is MSB first: (ancilla, high color bit, low color bit, references).
References are untouched. Completed forward/inverse channels implement V/V†;
the inverse applies E† ONCE before its ZUZ retries. Reset follows every actual
measurement, including success and exhaustion; a retry event means a further
attempt was actually scheduled. Feedforward counts one outcome dispatch per
measurement, not processor instructions. Clifford counts include CX/CZ as one
each, exclude T/T†, and exclude the internal realization of ideal reset.

Ideal gates, fresh zero ancilla, noiseless Z measurement, reset and classical
control are assumed. Unbounded completion is an analytical limit, not executed.
Cap exhaustion is an explicitly flagged abort, never completed unitary action.
No quantum control, static A/A† substitution, graph/search correctness, hardware,
physical QEC, latency, T-depth or advantage certificate is provided. Controlling
only data gates can reveal the control in the measurement record and dephase it;
success alone on |00> also does not prove arbitrary-input inverse semantics.

Primitive provenance/derivation: rus_accounting.py and the exact analytical
rus_ledger_review/admission; Paetznick--Svore arXiv:1311.1074v2, Fig. 8. The
two-T controlled-H extension and coloring V are local derived constructions.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import numpy as np
    from qiskit import QuantumCircuit

Direction = Literal["forward", "inverse"]
MAX_CAP = 4
MAX_LOOPS = 3
MAX_BRANCHES = 85
MAX_REFERENCE_WIRES = 3
UNPRICED = ("clifford", "measurement", "reset", "feedforward", "retry", "runtime")


@dataclass(frozen=True)
class Event:
    """One executed primitive or classical action, in MSB wire numbering."""

    name: str
    wires: tuple[int, ...] = ()
    outcome: int | None = None


@dataclass(frozen=True)
class Branch:
    """Unnormalized output and complete record; state can hold operator columns.

    Ancilla is reset to zero and removed at loop boundaries. An operator-column
    run starts at I_4; its output is the actual phase-sensitive branch Kraus map.
    records has one outcome word per reached loop, not per requested loop.
    """

    completed: bool
    records: tuple[tuple[int, ...], ...]
    state: np.ndarray
    events: tuple[Event, ...]

    @property
    def resources(self) -> dict[str, int]:
        """Count observed events, without inferring counts from trial formulas."""
        counts = Counter(event.name for event in self.events)
        return {
            "t": counts["t"] + counts["tdg"],
            "clifford": sum(counts[g] for g in ("h", "s", "sdg", "x", "z", "cx", "cz")),
            "measurement": counts["measure"],
            "reset": counts["reset"],
            "feedforward": counts["feedforward"],
            "retry": counts["retry"],
        }

    @property
    def costs(self) -> dict[str, int | None]:
        """Logical T count only; observed unpriced counts are not zero costs."""
        return {"t": self.resources["t"], **dict.fromkeys(UNPRICED)}


def _integer(name: str, value: int, maximum: int) -> None:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [0, {maximum}]")


def preflight(directions: tuple[Direction, ...], cap: int, max_branches: int) -> int:
    """Bound terminal enumeration BEFORE importing NumPy or allocating arrays.

    For L reached-loop positions, c successes per loop plus one abort give
    c**L + sum(c**i for i=0..L-1) records. At c=0 only the first loop aborts.
    The empty program has one identity record. No branches are pruned.
    """
    _integer("cap", cap, MAX_CAP)
    _integer("max_branches", max_branches, MAX_BRANCHES)
    if not isinstance(directions, tuple) or len(directions) > MAX_LOOPS:
        raise ValueError("directions must be a tuple of at most three loops")
    if any(d not in ("forward", "inverse") for d in directions):
        raise ValueError("Only forward/inverse uncontrolled vertex loops supported")
    count = cap ** len(directions) + sum(cap**i for i in range(len(directions)))
    if count > max_branches:
        raise ValueError(f"{count} terminal branches exceed caller budget")
    return count


def trial_gates(direction: Direction = "forward") -> tuple[Event, ...]:
    """Emit H,T,CX,H,CX,T,H on a, controlled onto h; inverse uses ZUZ."""
    preflight((direction,), 1, 2)
    body = tuple(
        Event(name, wires)
        for name, wires in (
            ("h", (0,)),
            ("t", (0,)),
            ("cx", (0, 1)),
            ("h", (0,)),
            ("cx", (0, 1)),
            ("t", (0,)),
            ("h", (0,)),
        )
    )
    return (
        (Event("z", (1,)),) + body + (Event("z", (1,)),)
        if direction == "inverse"
        else body
    )


def extension_gates(direction: Direction = "forward") -> tuple[Event, ...]:
    """Emit E or its actual expanded inverse, using a two-T controlled H.

    C=H S† H is Rx(-pi/2) up to scalar phase. B=C T C† gives
    CH=(I tensor B) CZ (I tensor B†); the conjugating phases cancel.
    """
    preflight((direction,), 1, 2)
    c = (Event("h", (2,)), Event("sdg", (2,)), Event("h", (2,)))
    ci = (Event("h", (2,)), Event("s", (2,)), Event("h", (2,)))
    ch: tuple[Event, ...] = ci + (Event("tdg", (2,)),) + c
    ch += (Event("cz", (1, 2)),) + ci + (Event("t", (2,)),) + c
    forward = (Event("sdg", (1,)),) + ch + (Event("x", (1,)),)
    adjoint = {"s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t"}
    return (
        forward
        if direction == "forward"
        else tuple(
            Event(adjoint.get(g.name, g.name), g.wires) for g in reversed(forward)
        )
    )


def _apply(state: np.ndarray, event: Event, wires: int) -> np.ndarray:
    """Apply one actual primitive to vector or column amplitudes (<=6 wires)."""
    import numpy as np

    identity = np.eye(2, dtype=complex)
    x = identity[::-1]
    gates = {
        "h": (x + np.diag([1, -1])) / np.sqrt(2),
        "x": x,
        "z": np.diag([1, -1]),
        "s": np.diag([1, 1j]),
        "sdg": np.diag([1, -1j]),
        "t": np.diag([1, (1 + 1j) / np.sqrt(2)]),
        "tdg": np.diag([1, (1 - 1j) / np.sqrt(2)]),
    }
    if event.name in ("cx", "cz"):
        control, target = event.wires
        indices = np.arange(2**wires)
        active = (indices & (1 << (wires - 1 - control))) != 0
        bit = 1 << (wires - 1 - target)
        if event.name == "cx":
            permutation = indices.copy()
            permutation[active] ^= bit
            return state[permutation]
        result = state.copy()
        result[active & ((indices & bit) != 0)] *= -1
        return result
    target = event.wires[0]
    # Move a selected binary axis to the front; trailing axes hold columns.
    shape = (2,) * wires + state.shape[1:]
    tensor = np.moveaxis(state.reshape(shape), target, 0)
    result = (gates[event.name] @ tensor.reshape(2, -1)).reshape(tensor.shape)
    return np.moveaxis(result, 0, target).reshape(state.shape)


def _gates(state: np.ndarray, gates: tuple[Event, ...], wires: int) -> np.ndarray:
    for event in gates:
        state = _apply(state, event, wires)
    return state


def _loop(branch: Branch, direction: Direction, cap: int, wires: int) -> list[Branch]:
    import numpy as np

    # Fresh zero retry ancilla, never a supplied K0/K1 matrix.
    state = np.concatenate((branch.state, np.zeros_like(branch.state)), axis=0)
    events = branch.events
    if direction == "inverse":
        prefix = extension_gates("inverse")
        state = _gates(state, prefix, wires)
        events += prefix
    word: tuple[int, ...] = ()
    outputs = []
    for attempt in range(cap):
        gates = trial_gates(direction)
        state = _gates(state, gates, wires)
        events += gates
        projected = []
        for outcome in (0, 1):
            half = state.shape[0] // 2
            measured = np.zeros_like(state)
            measured[outcome * half : (outcome + 1) * half] = state[
                outcome * half : (outcome + 1) * half
            ]
            # Explicit conditional reset: move the measured-one sector to zero.
            reset = np.zeros_like(state)
            reset[:half] = measured[outcome * half : (outcome + 1) * half]
            path_events = events + (
                Event("measure", (0,), outcome),
                Event("reset", (0,), outcome),
                Event("feedforward", (), outcome),
            )
            projected.append((reset, path_events))
        success, success_events = projected[0]
        if direction == "forward":
            suffix = extension_gates("forward")
            success = _gates(success, suffix, wires)
            success_events += suffix
        outputs.append(
            Branch(
                True, branch.records + (word + (0,),), success[:half], success_events
            )
        )
        state, events = projected[1]
        word += (1,)
        if attempt + 1 < cap:
            events += (Event("retry"),)
    outputs.append(
        Branch(False, branch.records + (word,), state[: state.shape[0] // 2], events)
    )
    return outputs


def execute(
    state: np.ndarray,
    directions: tuple[Direction, ...],
    *,
    cap: int,
    max_branches: int,
    reference_wires: int = 0,
) -> tuple[Branch, ...]:
    """Execute every ideal branch, stopping at first cap exhaustion.

    state is a vector or <=4 operator/purification columns on (h,l,references),
    already allocated by the caller. <=3 references gives <=6 dynamic wires.
    No input normalization is imposed: unnormalized branch compositions and
    operator columns must retain their scalar phases. Nonfinite inputs reject.
    """
    preflight(directions, cap, max_branches)
    _integer("reference_wires", reference_wires, MAX_REFERENCE_WIRES)
    import numpy as np

    expected_rows = 2 ** (2 + reference_wires)
    if (
        not isinstance(state, np.ndarray)
        or state.ndim not in (1, 2)
        or state.shape[0] != expected_rows
        or (state.ndim == 2 and not 1 <= state.shape[1] <= 4)
        or state.dtype.kind not in "bifcu"
        or not np.isfinite(state).all()
    ):
        raise ValueError("state must be finite amplitudes with bounded shape/columns")
    paths = [Branch(True, (), state.astype(complex, copy=True), ())]
    for direction in directions:
        next_paths = []
        for path in paths:
            next_paths.extend(
                _loop(path, direction, cap, 3 + reference_wires)
                if path.completed
                else [path]
            )
        paths = next_paths
    return tuple(paths)


def enumerate_instrument(
    directions: tuple[Direction, ...], *, cap: int, max_branches: int
) -> tuple[Branch, ...]:
    """Execute all four input columns to extract phase-sensitive Kraus maps."""
    preflight(directions, cap, max_branches)
    import numpy as np

    return execute(
        np.eye(4, dtype=complex), directions, cap=cap, max_branches=max_branches
    )


def analytical_expectations(direction: Direction, cap: int) -> dict[str, Fraction]:
    """Return separate finite-cap predictions; these are not observed counts.

    Unlimited expected T=14/3, but no unlimited retry execution is offered.
    Clifford predictions refer only to this emitted unoptimized construction.
    """
    preflight((direction,), cap, MAX_BRANCHES)
    success = 1 - Fraction(1, 4) ** cap
    attempts = sum((Fraction(1, 4) ** r for r in range(cap)), Fraction())
    extension = success if direction == "forward" else Fraction(1)
    return {
        "completion_probability": success,
        "t": 2 * attempts + 2 * extension,
        "clifford": (5 if direction == "forward" else 7) * attempts + 15 * extension,
        "measurement": attempts,
        "reset": attempts,
        "feedforward": attempts,
        "retry": attempts - int(cap > 0),
    }


def build_circuit(direction: Direction, *, cap: int) -> QuantumCircuit:
    """Build the same capped program as a real Qiskit nested-if circuit.

    q[0]=ancilla,q[1]=h,q[2]=l. Qiskit's displayed basis is reversed from
    this module's MSB amplitude convention. Only reached measurement bits are
    records; later bits remain unused after success. All-one reached bits abort;
    cap=0 always aborts. This circuit is for an initially zero ancilla only.
    """
    preflight((direction,), cap, MAX_BRANCHES)
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(3, cap, name=f"k3_rus_{direction}_cap{cap}")
    circuit.metadata = {
        "direction": direction,
        "cap": cap,
        "abort": "cap=0 or every reached measurement is one",
        "initial_ancilla": 0,
        "quantum_control_supported": False,
        "static_substitution_supported": False,
    }

    def emit(events: tuple[Event, ...]) -> None:
        for event in events:
            getattr(circuit, event.name)(*event.wires)

    if direction == "inverse":
        emit(extension_gates("inverse"))

    def attempt(index: int) -> None:
        emit(trial_gates(direction))
        circuit.measure(0, index)
        circuit.reset(0)
        with circuit.if_test((circuit.clbits[index], 0)) as otherwise:
            if direction == "forward":
                emit(extension_gates("forward"))
        with otherwise:
            if index + 1 < cap:
                attempt(index + 1)

    if cap:
        attempt(0)
    return circuit
