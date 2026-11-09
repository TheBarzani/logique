"""Heralded k=3 RUS instruments for the single edge on two vertex registers.

This executes gates, projections and resets, never supplied Kraus matrices.
Successful records implement preparation, complete-predicate marking, or a
reflection; exhausted records are terminal flagged aborts. It is NOT a finite
cap deterministic unitary or a quantum-controlled RUS construction.

Data order is MSB (v0.high, v0.low, v1.high, v1.low, references). Event/Qiskit
wire labels are (retry, scratch, data..., references...). Each phase gadget
borrows a fresh zero scratch and restores it; each RUS invocation uses the
admitted primitive trial/extension with its own vertex and fresh zero retry
ancilla. Inverse E-dagger runs once on entry, including cap zero.

Only cap <=4, <=341 terminal records, <=3 reference wires, <=4 columns and
<=9 dynamic wires are supported. Dense extracted data maps are at most 16x16;
references use tensor action. NumPy and Qiskit remain optional lazy imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Literal, cast

from . import dynamic_rus as primitive

if TYPE_CHECKING:
    import numpy as np
    from qiskit import QuantumCircuit

Program = Literal["prepare", "mark", "reflect", "iterate", "search"]
MAX_BRANCHES = 341
MAX_REFERENCES = 3
Event = primitive.Event


@dataclass(frozen=True)
class Stage:
    """One classically sequenced operation, never a quantum control."""

    kind: str
    vertex: int = -1


@dataclass(frozen=True)
class Record:
    """Outcome word on an explicitly identified vertex invocation."""

    stage: int
    vertex: int
    direction: str
    outcomes: tuple[int, ...]


@dataclass(frozen=True)
class Branch:
    """Unnormalized amplitudes, reached records, events and terminal flag."""

    completed: bool
    stopped_at: int | None
    records: tuple[Record, ...]
    state: np.ndarray
    events: tuple[Event, ...]

    @property
    def resources(self) -> dict[str, int]:
        """Count executed primitives, retaining unpriced operation counts."""
        return primitive.Branch(True, (), self.state, self.events).resources

    @property
    def costs(self) -> dict[str, int | None]:
        """Price logical T only; non-T, reset and measurement remain null."""
        return {"t": self.resources["t"], **dict.fromkeys(primitive.UNPRICED)}


def stages(program: Program) -> tuple[Stage, ...]:
    """Return time-ordered operations for preparation or one Grover iteration.

    reflect is A S0 A-dagger in operator order, hence inverse vertices first
    in time. iterate marks then reflects an arbitrary supplied state. search
    additionally prepares the input (normally |0000>); its cap3/4 enumeration
    exceeds the branch ceiling and is rejected before allocation.
    """
    prepare = (Stage("forward", 0), Stage("forward", 1))
    reflect = (
        Stage("inverse", 1),
        Stage("inverse", 0),
        Stage("zero_reflection"),
        Stage("forward", 0),
        Stage("forward", 1),
    )
    programs = {
        "prepare": prepare,
        "mark": (Stage("mark"),),
        "reflect": reflect,
        "iterate": (Stage("mark"),) + reflect,
        "search": prepare + (Stage("mark"),) + reflect,
    }
    if not isinstance(program, str) or program not in programs:
        raise ValueError("Unsupported two-vertex program")
    return programs[program]


def preflight(program: Program, cap: int, max_branches: int) -> int:
    """Check exact branch count and scalar limits before imports/allocations."""
    schedule = stages(program)
    if type(cap) is not int or not 0 <= cap <= primitive.MAX_CAP:
        raise ValueError("cap must be an integer in [0, 4]")
    if type(max_branches) is not int or not 1 <= max_branches <= MAX_BRANCHES:
        raise ValueError("max_branches must be an integer in [1, 341]")
    loops = sum(s.kind in ("forward", "inverse") for s in schedule)
    count = cap**loops + sum(cap**i for i in range(loops))
    if count > max_branches:
        raise ValueError(f"{count} terminal branches exceed caller budget")
    return count


def _ccx(a: int, b: int, target: int) -> tuple[Event, ...]:
    # Exact standard seven-T Toffoli, including all relative phases.
    return tuple(
        Event(name, wires)
        for name, wires in (
            ("h", (target,)),
            ("cx", (b, target)),
            ("tdg", (target,)),
            ("cx", (a, target)),
            ("t", (target,)),
            ("cx", (b, target)),
            ("tdg", (target,)),
            ("cx", (a, target)),
            ("t", (b,)),
            ("t", (target,)),
            ("h", (target,)),
            ("cx", (a, b)),
            ("t", (a,)),
            ("tdg", (b,)),
            ("cx", (a, b)),
        )
    )


def phase_gates(kind: str) -> tuple[Event, ...]:
    """Emit full-predicate edge marking or exact S0 with clean scratch wire1.

    Six disjoint valid unequal color pairs are marked. A four-bit point phase
    computes two controls into scratch, applies CCZ, then uncomputes scratch.
    This deliberately unoptimized construction costs 21T per marked point.
    S0=2|0000><0000|-I includes an explicit XZXZ global minus (four Cliffords).
    """
    if kind == "mark":
        points = tuple(4 * a + b for a in range(3) for b in range(3) if a != b)
    elif kind == "zero_reflection":
        points = (0,)
    else:
        raise ValueError("Unsupported phase stage")
    gates: tuple[Event, ...] = ()
    for point in points:
        mask = tuple(
            Event("x", (2 + bit,)) for bit in range(4) if not (point >> (3 - bit)) & 1
        )
        compute = _ccx(2, 3, 1)
        ccz = (Event("h", (5,)),) + _ccx(1, 4, 5) + (Event("h", (5,)),)
        gates += mask + compute + ccz + compute + mask
    if kind == "zero_reflection":
        gates += tuple(Event(name, (2,)) for name in ("x", "z", "x", "z"))
    return gates


def _run_gates(state: np.ndarray, events: tuple[Event, ...], wires: int) -> np.ndarray:
    # The admitted elementary tensor/index gate action allocates no wide operator.
    for event in events:
        state = primitive._apply(state, event, wires)
    return state


def _vertex_events(events: tuple[Event, ...], vertex: int) -> tuple[Event, ...]:
    mapping = (0, 2 + 2 * vertex, 3 + 2 * vertex)
    return tuple(
        Event(e.name, tuple(mapping[w] for w in e.wires), e.outcome) for e in events
    )


def _active_events(events: tuple[Event, ...]) -> tuple[Event, ...]:
    # Only one helper is present in the amplitude tensor at any instant.
    # scratch-mode: physical1 -> tensor0, data2 -> tensor1; retry-mode: 0 -> 0.
    return tuple(
        Event(e.name, tuple(0 if w < 2 else w - 1 for w in e.wires), e.outcome)
        for e in events
    )


def _phase(branch: Branch, kind: str, refs: int) -> Branch:
    import numpy as np

    events = phase_gates(kind)
    state = np.concatenate((branch.state, np.zeros_like(branch.state)))
    state = _run_gates(state, _active_events(events), 5 + refs)
    half = len(state) // 2
    scale = max(1.0, float(np.max(np.abs(branch.state), initial=0)))
    if np.max(np.abs(state[half:]), initial=0) > 3e-13 * scale:
        raise ArithmeticError("Phase scratch was not restored")
    return Branch(True, None, branch.records, state[:half], branch.events + events)


def _loop(
    branch: Branch, stage: Stage, index: int, cap: int, refs: int
) -> list[Branch]:
    import numpy as np

    direction = cast(primitive.Direction, stage.kind)
    state = np.concatenate((branch.state, np.zeros_like(branch.state)))
    events = branch.events
    if direction == "inverse":
        prefix = _vertex_events(primitive.extension_gates("inverse"), stage.vertex)
        state = _run_gates(state, _active_events(prefix), 5 + refs)
        events += prefix
    word: tuple[int, ...] = ()
    outputs = []
    for attempt in range(cap):
        trial = _vertex_events(primitive.trial_gates(direction), stage.vertex)
        state = _run_gates(state, _active_events(trial), 5 + refs)
        events += trial
        half = len(state) // 2
        # Z project followed by conditional reset: each selected half is moved
        # to ancilla-zero without normalization, pruning, or phase fitting.
        success, failure = state[:half].copy(), state[half:].copy()
        measured = tuple(
            Event(n, (0,) if n != "feedforward" else (), 0)
            for n in ("measure", "reset", "feedforward")
        )
        success_events = events + measured
        if direction == "forward":
            suffix = _vertex_events(primitive.extension_gates("forward"), stage.vertex)
            success = _run_gates(
                np.concatenate((success, np.zeros_like(success))),
                _active_events(suffix),
                5 + refs,
            )[:half]
            success_events += suffix
        outputs.append(
            Branch(
                True,
                None,
                branch.records + (Record(index, stage.vertex, direction, word + (0,)),),
                success,
                success_events,
            )
        )
        state = np.concatenate((failure, np.zeros_like(failure)))
        events += tuple(Event(e.name, e.wires, 1) for e in measured)
        word += (1,)
        if attempt + 1 < cap:
            events += (Event("retry"),)
    record = Record(index, stage.vertex, direction, word)
    outputs.append(
        Branch(
            False, index, branch.records + (record,), state[: len(state) // 2], events
        )
    )
    return outputs


def execute(
    state: np.ndarray,
    program: Program,
    *,
    cap: int,
    max_branches: int,
    reference_wires: int = 0,
) -> tuple[Branch, ...]:
    """Execute every record on arbitrary data/reference vectors or <=4 columns.

    Aborts retain the exact reached prefix and never execute a later stage.
    Inputs need not be normalized; zero-norm records are retained. A completed
    branch is still trace-decreasing and must not be silently made deterministic.
    """
    preflight(program, cap, max_branches)
    if type(reference_wires) is not int or not 0 <= reference_wires <= MAX_REFERENCES:
        raise ValueError("reference_wires must be an integer in [0, 3]")
    import numpy as np

    if (
        not isinstance(state, np.ndarray)
        or state.ndim not in (1, 2)
        or state.shape[0] != 2 ** (4 + reference_wires)
        or (state.ndim == 2 and not 1 <= state.shape[1] <= 4)
        or state.dtype.kind not in "bifcu"
        or not np.isfinite(state).all()
    ):
        raise ValueError("Expected finite bounded graph/reference amplitudes")
    paths = [Branch(True, None, (), state.astype(complex, copy=True), ())]
    for index, stage in enumerate(stages(program)):
        next_paths = []
        for path in paths:
            if not path.completed:
                next_paths.append(path)
            elif stage.kind in ("forward", "inverse"):
                next_paths.extend(_loop(path, stage, index, cap, reference_wires))
            else:
                next_paths.append(_phase(path, stage.kind, reference_wires))
        paths = next_paths
    return tuple(paths)


def analytical_expectations(program: Program, cap: int) -> dict[str, Fraction]:
    """Predict unconditional stop resources, including reached abort prefixes."""
    preflight(program, cap, MAX_BRANCHES)
    reached = Fraction(1)
    totals = {
        key: Fraction()
        for key in ("t", "clifford", "measurement", "reset", "feedforward", "retry")
    }
    for stage in stages(program):
        if stage.kind in ("forward", "inverse"):
            local = primitive.analytical_expectations(
                cast(primitive.Direction, stage.kind), cap
            )
            for key in totals:
                totals[key] += reached * local[key]
            reached *= local["completion_probability"]
        else:
            events = phase_gates(stage.kind)
            counts = {key: 0 for key in totals}
            counts["t"] = sum(e.name in ("t", "tdg") for e in events)
            counts["clifford"] = len(events) - counts["t"]
            for key in totals:
                totals[key] += reached * counts[key]
    return {"completion_probability": reached, **totals}


def build_circuit(program: Program, *, cap: int, max_branches: int) -> QuantumCircuit:
    """Emit the same instrument as nested classical ifs on six quantum wires.

    Record slots are allocated per invocation; unused slots are not outcomes.
    Every all-one reached word is a terminal ABORT, and no continuation is
    emitted there. cap0 stops on the first loop (after inverse E-dagger if any).
    The flag is a classical function of reached records, not a data measurement.
    """
    preflight(program, cap, max_branches)
    from qiskit import QuantumCircuit

    schedule = stages(program)
    loops = sum(s.kind in ("forward", "inverse") for s in schedule)
    circuit = QuantumCircuit(6, cap * loops, name=f"edge_k3_{program}_c{cap}")
    circuit.metadata = {
        "program": program,
        "cap": cap,
        "schedule": [(s.kind, s.vertex) for s in schedule],
        "initial_helpers": [0, 0],
        "abort": "first reached loop with cap=0 or all-one outcome word; stop immediately",
        "completion": "all scheduled loops have a reached zero outcome",
        "static_unitary": False,
        "quantum_control_supported": False,
    }

    def emit(events: tuple[Event, ...]) -> None:
        for event in events:
            getattr(circuit, event.name)(*event.wires)

    def walk(index: int, loop_index: int) -> None:
        if index == len(schedule):
            return
        stage = schedule[index]
        if stage.kind not in ("forward", "inverse"):
            emit(phase_gates(stage.kind))
            walk(index + 1, loop_index)
            return
        if stage.kind == "inverse":
            emit(_vertex_events(primitive.extension_gates("inverse"), stage.vertex))

        def attempt(number: int) -> None:
            emit(
                _vertex_events(
                    primitive.trial_gates(cast(primitive.Direction, stage.kind)),
                    stage.vertex,
                )
            )
            bit = circuit.clbits[loop_index * cap + number]
            circuit.measure(0, bit)
            circuit.reset(0)
            with circuit.if_test((bit, 0)) as otherwise:
                if stage.kind == "forward":
                    emit(
                        _vertex_events(
                            primitive.extension_gates("forward"), stage.vertex
                        )
                    )
                walk(index + 1, loop_index + 1)
            with otherwise:
                if number + 1 < cap:
                    attempt(number + 1)

        if cap:
            attempt(0)

    walk(0, 0)
    return circuit
