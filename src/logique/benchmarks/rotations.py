"""Bounded, emitted Clifford+T approximations for static unitary searches.

This optional Qiskit module uses deterministic Solovay--Kitaev synthesis, not
optimal Ross--Selinger synthesis or ``costs.rotation_t_count`` estimates. At
most three-qubit local operators are formed. Component and search bounds use
triangle and unitary telescoping inequalities; no dense search operator is needed.

Global phases are retained as Qiskit circuit scalar bookkeeping, including in
inverses. These circuits must not subsequently be controlled by dropping that
phase. Numerical rotation errors include phase and a floating-point allowance;
they are numerical checks, not interval-arithmetic certificates. Numerical
lowering, snapping and scalar-phase assembly are charged before SK allocation.
The precision floor is 1e-12; angle parameters must lie in [-2*pi, 2*pi].
Unchanged standard Clifford+T gates are treated algebraically. Composite gates
mean their recursively resolved definitions, including StatePreparation (not
an independently certified ideal amplitude vector). Only one-qubit matrix
inputs are supported, with measured ||M†M-I||_2 <= 64*eps. This admission test
does not make stored floating matrices exactly unitary: their norm growth is
included in component/search bounds. Targets remain the original matrices, not
unitary projections. Other targets are the supplied numeric Qiskit operators, not
ideal real parameters before Qiskit stores them. No measurement, RUS, or assisted
uncomputation is admitted. The caller supplies the contracts for a clean oracle and
the zero-state reflection; this module does not prove those contracts.
"""

from dataclasses import dataclass
from functools import lru_cache
import math
from numbers import Real
from typing import Sequence

import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit import ControlledGate, Gate
from qiskit.circuit.library import RXGate, RZGate, StatePreparation, UnitaryGate
from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping
from qiskit.quantum_info import Operator
from qiskit.synthesis import SolovayKitaevDecomposition

from logique.benchmarks.costs import CLIFFORD_T_BASIS, clifford_t, ft_metrics

_SK_BASIS = ("h", "t", "tdg")
_NUMERICAL_FLOOR = 1e-12
_ROUNDOFF = 64 * np.finfo(float).eps
_STANDARD = {
    name: gate
    for name, gate in get_standard_gate_name_mapping().items()
    if isinstance(gate, Gate) and gate.num_qubits <= 3
}
_LIMITATIONS = (
    "Deterministic bounded Solovay-Kitaev, not optimal Ross-Selinger synthesis; "
    "precision is not guaranteed and emitted circuits can be very long. "
    "Numerical phase-sensitive errors with floating-point allowances, not "
    "certified interval bounds. Static unitary constructions with roundoff-sized "
    "stored-matrix deviations only; scalar circuit phases "
    "must be preserved. MCX gates must be decomposed before this API. "
    "Precision floor 1e-12; angle parameters limited to +/-2*pi; only "
    "one-qubit matrix inputs with measured unitarity defect <= 64*eps. "
    "Stored matrix norm growth is accounted; no unitary projection is used. "
    "Composites denote their recursive definitions. "
    "Oracle cleanup and zero-reflection semantics are caller contracts."
)


@dataclass(frozen=True)
class SynthesisOptions:
    """Finite work limits: try degrees 0..max_recursion on one fixed basis net.

    Hard caps of six recursion levels and depth twelve prevent accidental
    uncontrolled synthesis. The default stops at five; degree six is an
    explicit, more expensive opt-in. No tool installation or fallback occurs.
    """

    max_recursion: int = 5
    basic_approximation_depth: int = 12

    def __post_init__(self) -> None:
        for name, value, low, high in (
            ("max_recursion", self.max_recursion, 0, 6),
            ("basic_approximation_depth", self.basic_approximation_depth, 1, 12),
        ):
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer in [{low}, {high}]")


@dataclass
class CompiledComponent:
    """An emitted component and JSON-compatible synthesis/cost metadata.

    ``circuit`` is None only for an unused search component (zero iterations).
    """

    circuit: QuantumCircuit | None
    metadata: dict


@dataclass
class CompiledSearch:
    """Complete search, reusable components, and inverse of the emitted A."""

    circuit: QuantumCircuit
    preparation: CompiledComponent
    preparation_inverse: QuantumCircuit
    oracle: CompiledComponent
    zero_reflection: CompiledComponent
    metadata: dict


class PrecisionNotReachedError(ValueError):
    """A bounded emitted construction failed; ``metadata`` records every trial."""

    def __init__(self, message: str, metadata: dict):
        super().__init__(message)
        self.metadata = metadata


def _precision(value: float, name: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not math.isfinite(value)
        or not 0 < value < 1
    ):
        raise ValueError(f"{name} must be finite and strictly between 0 and 1")
    if value < _NUMERICAL_FLOOR:
        raise PrecisionNotReachedError(
            f"{name} is below the numerical precision floor {_NUMERICAL_FLOOR:g}",
            {"requested_precision": float(value), "precision_floor": _NUMERICAL_FLOOR},
        )
    return float(value)


def _provenance(options: SynthesisOptions, *, exact: bool = False) -> dict:
    return {
        "method": "exact_clifford_t" if exact else "qiskit_solovay_kitaev",
        "qiskit_version": qiskit.__version__,
        "basis_gates": list(_SK_BASIS),
        "basic_approximation_depth": options.basic_approximation_depth,
        "max_recursion": options.max_recursion,
        "matrix_unitarity_tolerance": _ROUNDOFF,
        "limitations": _LIMITATIONS,
    }


def _validate_static(circuit: QuantumCircuit) -> None:
    if not isinstance(circuit, QuantumCircuit):
        raise ValueError("components must be QuantumCircuit objects")
    if circuit.num_clbits or circuit.parameters:
        raise ValueError(
            "static unitaries require no classical bits or free parameters"
        )
    if not math.isfinite(float(circuit.global_phase)):
        raise ValueError("global phase must be finite")
    for item in circuit.data:
        if not isinstance(item.operation, Gate) or item.clbits:
            raise ValueError("static unitary gates only; no measurement or directives")
        if any(
            isinstance(p, Real) and not math.isfinite(p) for p in item.operation.params
        ):
            raise ValueError("gate parameters must be finite")


@dataclass
class _Lowering:
    circuit: QuantumCircuit
    error_bound: float
    trials: list
    source_norm_bound: float


def _norm_product_bound(values) -> float:
    """Bound source norm products (each factor >= 1), with outward rounding."""
    product = 1.0
    for value in values:
        if value > 1.0:
            product = math.nextafter(product * value, math.inf)
        if not math.isfinite(product):
            raise ValueError("source norm product exceeds finite numerical range")
    return product


def _same_definition(
    left: QuantumCircuit | None, right: QuantumCircuit | None, depth: int = 0
) -> bool:
    """Compare types and recursive definitions, not Qiskit's name equality."""
    if depth > 32:
        raise ValueError("recursive gate definition exceeds depth limit 32")
    if left is None or right is None:
        return left is right
    if (
        left.num_qubits != right.num_qubits
        or left.num_clbits != right.num_clbits
        or left.global_phase != right.global_phase
        or len(left) != len(right)
    ):
        return False
    for a, b in zip(left.data, right.data):
        x, y = a.operation, b.operation
        if (
            type(x) is not type(y)
            or x.name != y.name
            or len(x.params) != len(y.params)
            or any(not np.array_equal(p, q) for p, q in zip(x.params, y.params))
            or getattr(x, "ctrl_state", None) != getattr(y, "ctrl_state", None)
            or [left.find_bit(q).index for q in a.qubits]
            != [right.find_bit(q).index for q in b.qubits]
            or a.clbits
            or b.clbits
            or not _same_definition(x.definition, y.definition, depth + 1)
        ):
            return False
    return True


def _canonical_gate(operation: Gate) -> Gate | None:
    """Admit known concrete types; reconstruct their standard semantics."""
    if isinstance(operation, ControlledGate) and operation.num_ctrl_qubits >= 3:
        raise ValueError("Expand multi-controlled gates with decompose_mcx()")
    sample = _STANDARD.get(operation.name)
    if sample is not None and type(operation) in (type(sample), sample.base_class):
        kwargs = (
            {"ctrl_state": operation.ctrl_state}
            if isinstance(operation, ControlledGate)
            else {}
        )
        canonical = sample.base_class(*operation.params, **kwargs)
    elif (
        type(operation) is ControlledGate
        and operation.num_ctrl_qubits == 2
        and type(operation.base_gate) is RXGate
    ):
        canonical = RXGate(*operation.base_gate.params).control(
            2, ctrl_state=operation.ctrl_state
        )
    else:
        return None
    if not _same_definition(operation.definition, canonical.definition):
        raise ValueError("conflicting definition for a standard gate")
    return canonical


def _compose_phase_allowance(
    target: QuantumCircuit, block: QuantumCircuit, wires: Sequence
) -> float:
    # Circuit.compose adds/reduces numeric scalar phases. Reserve roundoff even
    # when one addend is zero; this is engineering allowance, not certification.
    allowance = _ROUNDOFF if float(block.global_phase) else 0.0
    target.compose(block, qubits=wires, inplace=True)
    return allowance


def _lower_component(circuit: QuantumCircuit, depth: int = 0) -> _Lowering:
    _validate_static(circuit)
    if depth > 32:
        raise ValueError("recursive gate definition exceeds depth limit 32")
    lowered = circuit.copy_empty_like()
    errors, trials, source_norms = [], [], []
    for item in circuit.data:
        operation = item.operation
        for parameter in operation.params:
            if isinstance(parameter, Real) and abs(parameter) > 2 * math.pi:
                raise ValueError("angle parameters must lie in [-2*pi, 2*pi]")
        canonical = _canonical_gate(operation)
        if canonical is None and type(operation) is not UnitaryGate:
            if operation.name in _STANDARD:
                raise ValueError("conflicting standard gate name/type")
            if type(operation) not in (Gate, StatePreparation):
                raise ValueError("unsupported gate type; supply a supported definition")
            definition = operation.definition
            if definition is None or definition.num_qubits != operation.num_qubits:
                raise ValueError("opaque or inconsistent gate definition")
            child = _lower_component(definition, depth + 1)
            source_norms.append(child.source_norm_bound)
            errors.append(child.error_bound)
            errors.append(_compose_phase_allowance(lowered, child.circuit, item.qubits))
            trials.extend(child.trials)
            continue
        matrix_info = {}
        if type(operation) is UnitaryGate:
            if (
                operation.num_qubits != 1
                or not np.isfinite(operation.to_matrix()).all()
            ):
                raise ValueError("only finite one-qubit matrix inputs are supported")
            matrix = operation.to_matrix()
            defect = float(np.linalg.norm(matrix.conj().T @ matrix - np.eye(2), 2))
            # Qiskit's default allclose admission is much too permissive for
            # unitary telescoping. Keep only roundoff-sized deviations, then
            # account for their norms rather than asserting exact unitarity.
            if not math.isfinite(defect) or defect > _ROUNDOFF:
                raise ValueError(
                    "matrix unitarity defect exceeds numerical admission tolerance "
                    f"({_ROUNDOFF:g})"
                )
            # ||M|| <= sqrt(1 + ||M†M-I||). The same engineering allowance as
            # local lowering covers the 2x2 product/SVD used to measure defect.
            norm_bound = math.nextafter(math.sqrt(1 + defect + _ROUNDOFF), math.inf)
            source_norms.append(norm_bound)
            matrix_info = {
                "unitarity_defect": defect,
                "source_norm_bound": norm_bound,
            }
            canonical = UnitaryGate(matrix)
            if not _same_definition(operation.definition, canonical.definition):
                raise ValueError("conflicting matrix gate definition")
        assert canonical is not None
        if canonical.name in CLIFFORD_T_BASIS:
            lowered.append(canonical, item.qubits)
            continue
        source = QuantumCircuit(operation.num_qubits)
        source.append(canonical, range(operation.num_qubits))
        local = clifford_t(source, tolerance=0.0)
        # Qiskit's Euler identities can generate angles such as 5*pi/2 even
        # from small input angles. Reduce only bounded internal Rz angles;
        # compare the final result against source below, charging this too.
        normalized = local.copy_empty_like()
        for instruction in local.data:
            gate = instruction.operation
            if gate.name == "rz" and abs(float(gate.params[0])) > 2 * math.pi:
                angle = float(gate.params[0])
                if not math.isfinite(angle) or abs(angle) > 8 * math.pi:
                    raise ValueError("lowering produced an unsupported angle magnitude")
                normalized.rz(math.remainder(angle, 4 * math.pi), instruction.qubits[0])
            else:
                normalized.append(gate, instruction.qubits)
        local = clifford_t(normalized, tolerance=0.0)
        # Output must consist of actual standard leaves, never name-spoofed gates.
        for instruction in local.data:
            gate = instruction.operation
            trusted = _canonical_gate(gate)
            if trusted is None or gate.name not in (*CLIFFORD_T_BASIS, "rz"):
                raise ValueError("lowering left unsupported operations")
            if gate.name == "rz" and abs(float(gate.params[0])) > 2 * math.pi:
                raise ValueError("lowering produced an unsupported angle magnitude")
        if local.num_qubits != source.num_qubits:
            raise ValueError("lowering must preserve component width")
        unchanged = (
            canonical.name == "rz"
            and len(local) == 1
            and type(local.data[0].operation) is RZGate
            and local.data[0].operation.params == canonical.params
            and float(local.global_phase) == 0.0
        )
        measured = float(
            np.linalg.norm(Operator(local).data - Operator(source).data, 2)
        )
        allowance = 0.0 if unchanged else _ROUNDOFF * (len(local) + 1)
        bound = _sum_bound([measured, allowance])
        if not math.isfinite(bound):
            raise ValueError("nonfinite numerical lowering error")
        trials.append(
            {
                "gate": operation.name,
                "measured_error": measured,
                "numerical_allowance": allowance,
                "error_bound": bound,
                **matrix_info,
            }
        )
        errors.extend([bound, _compose_phase_allowance(lowered, local, item.qubits)])
    source_norm_bound = _norm_product_bound(source_norms)
    # In each telescoping term all preceding original factors have product
    # norm <= source_norm_bound; the lowered factors are algebraic unitaries.
    # Child errors are already bounded, so repeated scaling is conservative.
    error_bound = _sum_bound([source_norm_bound * _sum_bound(errors)])
    return _Lowering(lowered, error_bound, trials, source_norm_bound)


def lower_component(circuit: QuantumCircuit) -> QuantumCircuit:
    """Lower supported definitions, with no exactness claim for the result.

    Use synthesize_component/compile_search for accounted numerical bounds.
    No workspace is added; MCX policy is enforced recursively. Matrix input is
    limited to one qubit with measured ||M†M-I||_2 <= 64*eps; their stored
    norm growth is charged. Angles are limited to +/-2*pi and nesting to 32.
    """
    return _lower_component(circuit).circuit


@lru_cache(maxsize=2)
def _synthesizer(depth: int) -> SolovayKitaevDecomposition:
    return SolovayKitaevDecomposition(basis_gates=list(_SK_BASIS), depth=depth)


def _sum_bound(values) -> float:
    value = math.fsum(values)
    return math.nextafter(value, math.inf) if value else 0.0


def approximate_rz(
    angle: float,
    precision: float,
    *,
    options: SynthesisOptions = SynthesisOptions(),
) -> CompiledComponent:
    """Emit Rz(angle) within a phase-sensitive operator-norm precision.

    Try each bounded recursion degree and return the first passing construction.
    The SO(3) double-cover sign may be repaired by an explicit scalar pi phase;
    no continuous phase fitting or phase-insensitive equivalence check is used.
    Failure raises PrecisionNotReachedError with measured trial metadata.
    """
    precision = _precision(precision, "precision")
    if (
        isinstance(angle, bool)
        or not isinstance(angle, Real)
        or not math.isfinite(angle)
    ):
        raise ValueError("angle must be a finite real number")
    angle = float(angle)
    original = QuantumCircuit(1)
    original.rz(angle, 0)
    lowering = _lower_component(original)
    exact = lowering.circuit
    target = RZGate(angle).to_matrix()
    common = {"angle": angle, "precision": precision}
    if not exact.count_ops().get("rz", 0):
        if lowering.error_bound > precision:
            raise PrecisionNotReachedError(
                "numerical lowering exceeds precision",
                {**common, "error_bound": lowering.error_bound},
            )
        return CompiledComponent(
            exact,
            {
                **_provenance(options, exact=True),
                "method": "numerical_clifford_t_lowering",
                **common,
                "measured_error": float(
                    np.linalg.norm(Operator(exact).data - target, 2)
                ),
                "error_bound": lowering.error_bound,
                "numerical_allowance": _sum_bound(
                    row["numerical_allowance"] for row in lowering.trials
                ),
                "lowering": lowering.trials,
                "recursion_degree": None,
                "sign_correction": False,
                "metrics": ft_metrics(exact),
                "attempts": [],
            },
        )
    engine = _synthesizer(options.basic_approximation_depth)
    attempts = []
    for degree in range(options.max_recursion + 1):
        emitted = engine.run(target, recursion_degree=degree)
        matrix = Operator(emitted).data
        sign_correction = np.linalg.norm(matrix + target, 2) < np.linalg.norm(
            matrix - target, 2
        )
        if sign_correction:
            emitted.global_phase += math.pi
            matrix = Operator(emitted).data
        measured = float(np.linalg.norm(matrix - target, 2))
        # Reserve roundoff for the sequential 2x2 gate products and final SVD.
        allowance = _ROUNDOFF * (len(emitted) + 1)
        bound = _sum_bound([measured, allowance])
        trial = {
            "recursion_degree": degree,
            "sign_correction": bool(sign_correction),
            "measured_error": measured,
            "numerical_allowance": float(allowance),
            "error_bound": bound,
            "metrics": ft_metrics(emitted),
        }
        attempts.append(trial)
        if math.isfinite(bound) and bound <= precision:
            return CompiledComponent(
                emitted,
                {**_provenance(options), **common, **trial, "attempts": attempts},
            )
    metadata = {**_provenance(options), **common, "attempts": attempts}
    best = min(trial["error_bound"] for trial in attempts)
    raise PrecisionNotReachedError(
        f"Rz({angle}) needs {precision:g}; best bounded error {best:g} "
        f"through recursion {options.max_recursion}",
        metadata,
    )


def _compile_lowered(
    lowering: _Lowering,
    precision: float | None,
    occurrences: int,
    options: SynthesisOptions,
) -> CompiledComponent:
    lowered = lowering.circuit
    count = int(lowered.count_ops().get("rz", 0))
    info = {
        **_provenance(options, exact=count == 0),
        "occurrences": occurrences,
        "rotation_count": count,
        "rotation_occurrences": count * occurrences,
        "per_rotation_precision": precision if count and occurrences else None,
        "lowering_error_bound": lowering.error_bound,
        "source_norm_bound": lowering.source_norm_bound,
        "lowering_trials": lowering.trials,
        "assembly_error_bound": _ROUNDOFF * (count + 1) if count else 0.0,
    }
    if not count and lowering.error_bound:
        info["method"] = "numerical_clifford_t_lowering"
    if not occurrences:
        return CompiledComponent(
            None,
            {
                **info,
                "status": "unused",
                "rotations": [],
                "error_bound": 0.0,
                "weighted_error_bound": 0.0,
                "metrics": None,
            },
        )
    emitted = lowered.copy_empty_like()
    rotations = []
    for index, item in enumerate(lowered.data):
        if item.operation.name != "rz":
            emitted.append(item.operation, item.qubits, copy=False)
            continue
        assert precision is not None
        try:
            approximation = approximate_rz(
                float(item.operation.params[0]), precision, options=options
            )
        except PrecisionNotReachedError as error:
            error.metadata.update(
                lowered_instruction_index=index,
                qubit=lowered.find_bit(item.qubits[0]).index,
                occurrences=occurrences,
            )
            raise
        emitted.compose(approximation.circuit, qubits=item.qubits, inplace=True)
        rotations.append(
            {
                **approximation.metadata,
                "lowered_instruction_index": index,
                "qubit": lowered.find_bit(item.qubits[0]).index,
                "occurrences": occurrences,
            }
        )
    bound = _sum_bound(
        [lowering.error_bound, info["assembly_error_bound"]]
        + [row["error_bound"] for row in rotations]
    )
    return CompiledComponent(
        emitted,
        {
            **info,
            "status": "exact" if not bound else "approximated",
            "rotations": rotations,
            "error_bound": bound,
            "weighted_error_bound": _sum_bound([occurrences * bound]),
            "metrics": ft_metrics(emitted),
        },
    )


def _allocated_precision(
    budget: float, rotation_occurrences: int, preprocessing: float = 0.0
) -> float | None:
    if preprocessing > budget:
        raise PrecisionNotReachedError(
            "numerical preprocessing exceeds error budget",
            {"preprocessing_error_bound": preprocessing, "error_budget": budget},
        )
    if not rotation_occurrences:
        return None
    # Leave a small margin for rounding the sums/products of local bounds.
    precision = (budget - preprocessing) * (1 - 1e-12) / rotation_occurrences
    return _precision(precision, "allocated per-rotation precision")


def synthesize_component(
    circuit: QuantumCircuit,
    *,
    error_budget: float = 1e-3,
    options: SynthesisOptions = SynthesisOptions(),
) -> CompiledComponent:
    """Lower and approximate one component, equally allocating its error budget."""
    budget = _precision(error_budget, "error_budget")
    lowered = _lower_component(circuit)
    count = lowered.circuit.count_ops().get("rz", 0)
    preprocessing = _sum_bound(
        [lowered.error_bound, _ROUNDOFF * (count + 1) if count else 0.0]
    )
    precision = _allocated_precision(budget, count, preprocessing)
    result = _compile_lowered(lowered, precision, 1, options)
    if result.metadata["error_bound"] > budget:
        raise PrecisionNotReachedError(
            "accumulated bound exceeds budget", result.metadata
        )
    result.metadata["error_budget"] = budget
    return result


def compile_search(
    preparation: QuantumCircuit,
    oracle: QuantumCircuit,
    zero_reflection: QuantumCircuit,
    *,
    data_qubits: Sequence[int],
    iterations: int,
    error_budget: float = 1e-3,
    options: SynthesisOptions = SynthesisOptions(),
) -> CompiledSearch:
    """Emit A then j repetitions of O, A-dagger, S0, A, in time order.

    A and S0 have data width; ``data_qubits[i]`` maps their wire i into the full
    oracle width. They never act on auxiliary wires. The caller guarantees O is
    a clean phase oracle and S0 the desired zero-state reflection. A is compiled
    once and its actual emitted inverse is reused. Each residual Rz occurrence
    receives the budget remaining after numerical lowering and phase assembly,
    divided by ((1+2j)*n_A + j*n_O + j*n_S0), including rotations inside
    repeated inverse preparations. Unused O/S0 are validated and lowered but not
    approximated or costed; their returned circuit is None.

    Roundoff-sized nonunitarity of admitted stored matrices is retained in the
    target. A product of source norm bounds scales the weighted error sum and
    reduces the available budget before allocation; it also covers A's adjoint.
    """
    budget = _precision(error_budget, "error_budget")
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be a nonnegative integer")
    for component in (preparation, oracle, zero_reflection):
        _validate_static(component)
    try:
        mapping = list(data_qubits)
    except TypeError as error:
        raise ValueError(
            "data_qubits must be a sequence of oracle wire indices"
        ) from error
    if (
        not mapping
        or len(mapping) != preparation.num_qubits
        or len(mapping) != zero_reflection.num_qubits
        or any(type(q) is not int or not 0 <= q < oracle.num_qubits for q in mapping)
        or len(set(mapping)) != len(mapping)
    ):
        raise ValueError(
            "data_qubits must map each A/S0 wire to a distinct oracle wire"
        )
    sources = {
        "preparation": preparation,
        "oracle": oracle,
        "zero_reflection": zero_reflection,
    }
    occurrences = {
        "preparation": 1 + 2 * iterations,
        "oracle": iterations,
        "zero_reflection": iterations,
    }
    lowered = {name: _lower_component(value) for name, value in sources.items()}
    source_norm_product = _norm_product_bound(
        value.source_norm_bound ** occurrences[name] for name, value in lowered.items()
    )
    total = sum(
        occurrences[name] * value.circuit.count_ops().get("rz", 0)
        for name, value in lowered.items()
    )
    numerical_assembly = any(
        occurrences[name]
        and (
            value.error_bound
            or value.circuit.global_phase
            or value.circuit.count_ops().get("rz", 0)
        )
        for name, value in lowered.items()
    )
    # Includes scalar phase accumulation and forming the actual emitted inverse.
    assembly_bound = _ROUNDOFF * (4 * iterations + 2) if numerical_assembly else 0.0
    preprocessing = _sum_bound(
        [assembly_bound]
        + [
            occurrences[name]
            * _sum_bound(
                [
                    value.error_bound,
                    (
                        _ROUNDOFF * (value.circuit.count_ops().get("rz", 0) + 1)
                        if value.circuit.count_ops().get("rz", 0)
                        else 0.0
                    ),
                ]
            )
            for name, value in lowered.items()
        ]
    )
    # Algebraic unitary inputs keep the original weighted allocation exactly.
    # For stored matrices use norm-aware telescoping, without changing targets.
    available = (
        math.nextafter(budget / source_norm_product, 0.0)
        if source_norm_product > 1.0
        else budget
    )
    precision = _allocated_precision(available, total, preprocessing)
    compiled = {}
    for name, value in lowered.items():
        try:
            compiled[name] = _compile_lowered(
                value, precision, occurrences[name], options
            )
        except PrecisionNotReachedError as error:
            error.metadata.update(
                component=name,
                error_budget=budget,
                rotation_occurrences=total,
                occurrence_counts=occurrences,
            )
            raise
    a = compiled["preparation"].circuit
    assert a is not None
    inverse = a.inverse()
    search = QuantumCircuit(oracle.num_qubits)
    search.compose(a, qubits=mapping, inplace=True)
    for _ in range(iterations):
        search.compose(compiled["oracle"].circuit, inplace=True)
        search.compose(inverse, qubits=mapping, inplace=True)
        search.compose(
            compiled["zero_reflection"].circuit, qubits=mapping, inplace=True
        )
        search.compose(a, qubits=mapping, inplace=True)
    unscaled_bound = _sum_bound(
        [assembly_bound]
        + [value.metadata["weighted_error_bound"] for value in compiled.values()]
    )
    bound = _sum_bound([source_norm_product * unscaled_bound])
    if bound > budget:
        raise PrecisionNotReachedError(
            "accumulated bound exceeds budget", {"bound": bound}
        )
    metadata = {
        **_provenance(options, exact=total == 0),
        "iterations": iterations,
        "data_qubits": mapping,
        "occurrence_counts": occurrences,
        "preparation_forward_occurrences": 1 + iterations,
        "preparation_inverse_occurrences": iterations,
        "inverse_reused": True,
        "rotation_occurrences": total,
        "per_rotation_precision": precision,
        "error_budget": budget,
        "error_bound": bound,
        "preprocessing_error_bound": _sum_bound([source_norm_product * preprocessing]),
        "unscaled_preprocessing_error_bound": preprocessing,
        "source_norm_product_bound": source_norm_product,
        "norm_adjusted_error_budget": available,
        "unscaled_error_bound": unscaled_bound,
        "assembly_error_bound": assembly_bound,
        "bound_derivation": (
            "||U-V|| <= N*((1+2j)*e_A + j*e_O + j*e_S0 + e_assembly), "
            "N = n_A**(1+2j)*n_O**j*n_S0**j with n_X >= max(1, ||X||); "
            "norm-aware telescoping, triangle inequality, and "
            "||A_dagger-V_dagger|| = ||A-V||"
        ),
        "components": {name: value.metadata for name, value in compiled.items()},
        "metrics": ft_metrics(search),
    }
    if not total and preprocessing:
        metadata["method"] = "numerical_clifford_t_lowering"
    return CompiledSearch(
        search,
        compiled["preparation"],
        inverse,
        compiled["oracle"],
        compiled["zero_reflection"],
        metadata,
    )
