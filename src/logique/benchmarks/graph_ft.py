"""Bounded edge-graph static FT experiments using clean-subspace composition.

This separate harness leaves the original dense-four-qubit pilot unchanged.
For the fixed k=3 edge, exhaustive clean columns establish O|x,0> =
(-1)^f(x)|x,0>. Linearity extends this action to coherent data and a reference.
A and signed S0 act only on data, so their composition preserves clean scratch.
Local dense checks cover A, its actual emitted adjoint, and S0; full-width
checks use sequential statevectors only. No dirty-workspace theorem follows.

The unchanged rotation compiler bounds the ORIGINAL recursive numeric targets,
including repeated A and its actual emitted inverse. R3 removes code checks
only for the ideal valid-code support. Approximate leakage is measured, and R3
is compared to its own edge-only numeric target, never silently to R2. Numerical
checks and measured ideal gaps are not interval or ideal-amplitude certificates.
"""

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import resource
import time
from typing import Callable, Sequence

import numpy as np
import qiskit
from qiskit import QuantumCircuit, qpy
from qiskit.quantum_info import Operator, Statevector
from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping

from logique.benchmarks import rotations, static_ft
from logique.benchmarks.costs import CLIFFORD_T_BASIS, decompose_mcx, ft_metrics
from logique.benchmarks.preparation_breakeven import StaticCosts, compare_preparations
from logique.circuits.grover import coloring_preparation
from logique.coloring import ColoringEncoding, ColoringProblem
from logique.paths import new_dump_directory

TOLERANCE = 1e-10
_STANDARD_LEAVES = get_standard_gate_name_mapping()


@dataclass(frozen=True)
class GraphLimits:
    """Preallocation guards, not a hard aggregate OS memory limit.

    Eight simultaneous complex state buffers are conservatively reserved. SK
    has a finite depth/recursion ceiling and a conservative leaf-word estimate;
    post-emission checks enforce operation counts. The external supervisor must
    kill the process group at <=120s. RSS is observational, not enforcement.
    """

    statevector_qubits: int = 18
    local_operator_qubits: int = 5
    clean_columns: int = 32
    operations: int = 3_000_000
    state_gate_work: int = 20_000_000_000
    array_bytes: int = 64 * 1024**2
    process_bytes: int = 6 * 1024**3
    seconds: int = 110

    def __post_init__(self) -> None:
        caps = {
            "statevector_qubits": 18,
            "local_operator_qubits": 5,
            "clean_columns": 32,
            "operations": 3_000_000,
            "state_gate_work": 20_000_000_000,
            "array_bytes": 64 * 1024**2,
            "process_bytes": 6 * 1024**3,
            "seconds": 110,
        }
        for name, cap in caps.items():
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= cap:
                raise ValueError(f"{name} must be an integer in [1, {cap}]")


def preflight(width: int, data_width: int, limits: GraphLimits) -> dict:
    """Reject dimensions before shifts, arrays, native wrappers or simulation."""
    if (
        type(width) is not int
        or type(data_width) is not int
        or not 1 <= data_width <= limits.local_operator_qubits
        or not data_width <= width <= limits.statevector_qubits
    ):
        raise ValueError("Graph width exceeds local/statevector limits")
    columns = 1 << data_width
    if columns > limits.clean_columns:
        raise ValueError("Exhaustive clean-column budget exceeded")
    arrays = 8 * 16 * (1 << width) + 8 * 16 * (1 << (2 * data_width))
    if arrays > limits.array_bytes or arrays > limits.process_bytes:
        raise ValueError("Declared array budget exceeded")
    return {
        "width": width,
        "data_width": data_width,
        "columns": columns,
        "reserved_array_bytes": arrays,
    }


def _operations(circuit: QuantumCircuit, limits: GraphLimits) -> None:
    preflight(circuit.num_qubits, min(circuit.num_qubits, 5), limits)
    if len(circuit) > limits.operations:
        raise ValueError("Circuit operation budget exceeded")
    if len(circuit) * (1 << circuit.num_qubits) > limits.state_gate_work:
        raise ValueError("Statevector gate-work budget exceeded")


def local_matrix(circuit: QuantumCircuit, limits: GraphLimits) -> np.ndarray:
    """Form a dense operator only after enforcing the separate local limit."""
    preflight(circuit.num_qubits, circuit.num_qubits, limits)
    return np.asarray(Operator(circuit).data)


def clean_phase_check(
    circuit: QuantumCircuit,
    mapping: Sequence[int],
    predicate: Callable[[int], bool],
    limits: GraphLimits,
) -> dict:
    """Check every phase-sensitive clean column without storing a wide matrix.

    The square root of summed column squared errors bounds the clean-subspace
    spectral error by its Frobenius norm. No phase fitting is performed.
    """
    preflight(circuit.num_qubits, len(mapping), limits)
    _operations(circuit, limits)
    indices = static_ft.clean_indices(circuit.num_qubits, mapping)
    squared = scratch_squared = 0.0
    for x, index in enumerate(indices):
        state = Statevector.from_int(index, 1 << circuit.num_qubits).evolve(circuit)
        amplitudes = state.data.copy()
        amplitudes[index] -= -1 if predicate(x) else 1
        squared += float(np.vdot(amplitudes, amplitudes).real)
        amplitudes = state.data.copy()
        amplitudes[indices] = 0
        scratch_squared += float(np.vdot(amplitudes, amplitudes).real)
    error = math.sqrt(squared)
    scratch_error = math.sqrt(scratch_squared)
    if max(error, scratch_error) > TOLERANCE:
        raise ValueError("Clean phase/restoration contract failed")
    return {
        "columns": len(indices),
        "phase_frobenius_error": error,
        "scratch_frobenius_error": scratch_error,
        "coverage": "all clean columns, coherent by linearity; no dirty claim",
    }


def zero_reflection(width: int, limits: GraphLimits) -> QuantumCircuit:
    """Build signed S0 with explicit restoring Gray-code MCX and check locally."""
    preflight(width, width, limits)
    circuit = QuantumCircuit(width, global_phase=math.pi)
    circuit.x(range(width))
    if width == 1:
        circuit.z(0)
    else:
        circuit.h(width - 1)
        circuit.mcx(list(range(width - 1)), width - 1)
        circuit.h(width - 1)
    circuit.x(range(width))
    lowered, _ = decompose_mcx(circuit, "gray_code")
    expected = -np.eye(1 << width, dtype=complex)
    expected[0, 0] = 1
    if np.linalg.norm(local_matrix(lowered, limits) - expected, 2) > TOLERANCE:
        raise ValueError("Signed S0 contract failed")
    return lowered


def _write(path: Path, value: dict) -> None:
    # Only current fresh-run status files may evolve. QPY and row directories
    # are exclusive; candidate/review histories are never overwritten.
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _leaf_word(circuit: QuantumCircuit) -> tuple:
    """Identity of standard scalar gates, ordered wires and numeric parameters."""
    leaves = set(CLIFFORD_T_BASIS) | {"u", "p", "rx", "ry", "rz"}
    word = []
    for item in circuit.data:
        op = item.operation
        if op.name not in leaves or op.num_qubits > 2 or item.clbits:
            raise ValueError("QPY comparison requires standard expanded leaves")
        # Concrete types prevent spoofed same-name definitions from certifying
        # structural equivalence. Source lowering/compiler also validates types.
        canonical = _STANDARD_LEAVES[op.name]
        if type(op) not in (type(canonical), canonical.base_class):
            raise ValueError("Nonstandard leaf type")
        word.append(
            (
                op.name,
                tuple(float(p) for p in op.params),
                tuple(circuit.find_bit(q).index for q in item.qubits),
            )
        )
    return circuit.num_qubits, float(circuit.global_phase), tuple(word)


def save_circuit(
    directory: Path,
    name: str,
    circuit: QuantumCircuit,
    *,
    emitted: bool,
    limits: GraphLimits,
) -> tuple[QuantumCircuit, dict]:
    """Reload QPY and compare every standard leaf/wire/parameter/scalar phase.

    Original recursive definitions are expanded before QPY to avoid inverse
    StatePreparation serialization defects. This proves byte-roundtrip circuit
    semantics compositionally, without a full-width Operator allocation.
    """
    _operations(circuit, limits)
    serial = circuit if emitted else circuit.decompose(reps=32)
    _operations(serial, limits)
    if emitted and set(serial.count_ops()) - set(CLIFFORD_T_BASIS):
        raise ValueError("Unsynthesized emitted gates")
    before = _leaf_word(serial)
    path = directory / f"{name}.qpy"
    with path.open("xb") as stream:
        qpy.dump(serial, stream)
    with path.open("rb") as stream:
        loaded = qpy.load(stream)
    if len(loaded) != 1 or _leaf_word(loaded[0]) != before:
        raise ValueError("QPY leaf/wire/scalar phase readback failed")
    record = {
        "sha256": static_ft.sha256(path),
        "qubits": serial.num_qubits,
        "counts": dict(loaded[0].count_ops()),
        "global_phase": float(loaded[0].global_phase),
        "readback": "identical ordered standard leaves, wires, params, scalar",
        "source_definitions_expanded": not emitted,
    }
    if emitted:
        record["metrics"] = ft_metrics(loaded[0])
    _write(directory / f"{name}.json", record)
    return loaded[0], record


def build_components(
    regime: str, executable: Path, directory: Path, limits: GraphLimits
) -> dict:
    """Synthesize the actual noncontiguous-label edge; never substitute a pilot."""
    from logique.synthesis import synthesize

    if regime not in ("R1", "R2", "R3"):
        raise ValueError("regime must be R1, R2 or R3")
    problem = ColoringProblem(vertices=(7, 11), edges=((7, 11),), colors=3)
    encoding = ColoringEncoding(problem)
    preflight(4, 4, limits)  # before preparation arrays or native synthesis
    source = ColoringEncoding(
        ColoringProblem(
            vertices=problem.vertices,
            edges=problem.edges,
            colors=4 if regime == "R3" else 3,
        )
    )
    source_path = source.write_verilog(directory / "input.v")
    native = synthesize(
        source, "xag_bennett", preprocessing="none", executable=executable
    )
    _write(directory / "native.json", native.metadata)
    allocation = preflight(native.circuit.num_qubits, encoding.input_count, limits)
    _write(directory / "allocation.json", allocation)
    mapping = native.metadata["input_qubits"]
    if len(mapping) != encoding.input_count:
        raise ValueError("Input mapping width changed")
    original = native.phase_oracle()  # actual compute-Z-actual inverse
    oracle, lowering = decompose_mcx(original, "gray_code")
    opened = sorted({i.operation.name for i in oracle.data if "_o" in i.operation.name})
    if opened:
        oracle = oracle.decompose(gates_to_decompose=opened)
    _write(directory / "mcx.json", {**lowering, "open_controls_resolved": opened})
    if oracle.num_qubits != native.circuit.num_qubits:
        raise ValueError("Gray-code policy unexpectedly appended scratch")

    def predicate(x: int) -> bool:
        assignment = encoding.decode(x)
        if regime == "R3":
            return all(assignment[u] != assignment[v] for u, v in problem.edges)
        return problem.is_valid(assignment)

    contract: dict = {
        "original_O": clean_phase_check(original, mapping, predicate, limits),
        "lowered_O": clean_phase_check(oracle, mapping, predicate, limits),
    }
    preparation = coloring_preparation(encoding)
    if regime == "R1":
        preparation = QuantumCircuit(4)
        preparation.h(range(4))
    am = local_matrix(preparation, limits)
    contract["A_unitarity_defect"] = float(
        np.linalg.norm(am.conj().T @ am - np.eye(16), 2)
    )
    ideal = np.array(
        [
            (
                1 / 4
                if regime == "R1"
                else (1 / 3 if all(c < 3 for c in encoding.decode(x).values()) else 0)
            )
            for x in range(16)
        ],
        dtype=complex,
    )
    contract["recursive_A_to_ideal_initial_gap"] = float(
        np.linalg.norm(am[:, 0] - ideal)
    )
    if (
        max(
            contract["A_unitarity_defect"], contract["recursive_A_to_ideal_initial_gap"]
        )
        > TOLERANCE
    ):
        raise ValueError("Preparation contract failed")
    reflection = zero_reflection(4, limits)
    return dict(
        encoding=encoding,
        preparation=preparation,
        oracle=oracle,
        original_oracle=original,
        zero_reflection=reflection,
        mapping=mapping,
        contract=contract,
        input_sha256=static_ft.sha256(source_path),
        predicate=predicate,
        ideal_initial=ideal,
        allocation=allocation,
    )


def sk_preflight(
    parts: dict,
    iterations: int,
    options: rotations.SynthesisOptions,
    limits: GraphLimits,
) -> dict:
    """Bound work before SK; do not change the admitted compiler's allocation.

    A depth-d basis word has length <=2d; each SK recursion expands at most
    five previous words. A factor two safety margin covers inverse/conjugate
    words. This estimates leaf storage/work, not Python RSS or wall runtime.
    Rejected runs have no analytical replacement. Exact lowered counts and
    rotation occurrences are saved before compiling the original components.
    """
    if type(iterations) is not int or not 0 <= iterations <= 3:
        raise ValueError("iterations must be an integer in [0, 3]")
    lowered = [
        rotations.lower_component(parts[key])
        for key in ("preparation", "oracle", "zero_reflection")
    ]
    weights = [1 + 2 * iterations, iterations, iterations]
    occurrences = sum(w * c.count_ops().get("rz", 0) for w, c in zip(weights, lowered))
    max_word = 2 * options.basic_approximation_depth * 5**options.max_recursion
    upper = sum(
        w * (len(c) + c.count_ops().get("rz", 0) * max_word)
        for w, c in zip(weights, lowered)
    )
    work = upper * (1 << parts["oracle"].num_qubits)
    if upper > limits.operations or work > limits.state_gate_work:
        raise ValueError("SK estimated operation/statevector work budget exceeded")
    return {
        "options": asdict(options),
        "weighted_rotation_occurrences": occurrences,
        "estimated_search_operation_ceiling": upper,
        "estimated_state_gate_work": work,
        "lowered_operations": [len(c) for c in lowered],
        "limits": asdict(limits),
    }


def _assemble(
    a: QuantumCircuit,
    o: QuantumCircuit,
    s: QuantumCircuit,
    mapping: Sequence[int],
    iterations: int,
) -> QuantumCircuit:
    search = QuantumCircuit(o.num_qubits)
    search.compose(a, mapping, inplace=True)
    for _ in range(iterations):
        search.compose(o, inplace=True)
        search.compose(a.inverse(), mapping, inplace=True)
        search.compose(s, mapping, inplace=True)
        search.compose(a, mapping, inplace=True)
    return search


def execute_case(
    directory: Path,
    parts: dict,
    regime: str,
    iterations: int,
    budget: float,
    limits: GraphLimits,
    options: rotations.SynthesisOptions,
) -> dict:
    """Compile once, reload components/search, and execute bounded numeric checks."""
    a, o, s = [parts[k] for k in ("preparation", "oracle", "zero_reflection")]
    mapping = parts["mapping"]
    pre = sk_preflight(parts, iterations, options, limits)
    _write(directory / "sk-preflight.json", pre)
    for name, source in [
        ("target_A", a),
        ("target_O", parts["original_oracle"]),
        ("target_S0", s),
    ]:
        save_circuit(directory, name, source, emitted=False, limits=limits)
    target = _assemble(a, parts["original_oracle"], s, mapping, iterations)
    loaded_target, _ = save_circuit(
        directory, "target_search", target, emitted=False, limits=limits
    )
    out = rotations.compile_search(
        a,
        o,
        s,
        data_qubits=mapping,
        iterations=iterations,
        error_budget=budget,
        options=options,
    )
    if out.preparation_inverse != out.preparation.circuit.inverse():
        raise ValueError("Actual emitted preparation inverse not reused")
    _write(directory / "compiler.json", out.metadata)
    components = {
        "A": out.preparation.circuit,
        "A_inverse": out.preparation_inverse,
        "search": out.circuit,
    }
    if iterations:
        components.update(O=out.oracle.circuit, S0=out.zero_reflection.circuit)
        diffusion = QuantumCircuit(o.num_qubits)
        diffusion.compose(out.preparation_inverse, mapping, inplace=True)
        diffusion.compose(out.zero_reflection.circuit, mapping, inplace=True)
        diffusion.compose(out.preparation.circuit, mapping, inplace=True)
        components["diffusion"] = diffusion
    saved, records = {}, {}
    for name, circuit in components.items():
        saved[name], records[name] = save_circuit(
            directory, name, circuit, emitted=True, limits=limits
        )
    inverse_error = float(
        np.linalg.norm(
            local_matrix(saved["A_inverse"], limits)
            - local_matrix(saved["A"], limits).conj().T,
            2,
        )
    )
    a_error = float(
        np.linalg.norm(local_matrix(saved["A"], limits) - local_matrix(a, limits), 2)
    )
    if (
        inverse_error > TOLERANCE
        or a_error > out.preparation.metadata["error_bound"] + 1e-12
    ):
        raise ValueError("Emitted A/inverse phase-sensitive contract failed")
    if iterations:
        emitted_o = clean_phase_check(saved["O"], mapping, parts["predicate"], limits)
        reconstructed = _assemble(
            saved["A"], saved["O"], saved["S0"], mapping, iterations
        )
        if _leaf_word(reconstructed) != _leaf_word(saved["search"]):
            raise ValueError("Saved components fail full-search assembly")
    else:
        emitted_o = None
    target_state = Statevector.from_int(0, 1 << o.num_qubits).evolve(loaded_target).data
    emitted_state = (
        Statevector.from_int(0, 1 << o.num_qubits).evolve(saved["search"]).data
    )
    error = float(np.linalg.norm(emitted_state - target_state))
    if error > out.metadata["error_bound"] + 1e-12:
        raise ValueError("Clean-state numerical error exceeds whole-search bound")
    ideal = parts["ideal_initial"].copy()
    initial = ideal.copy()
    signs = np.array([-1 if parts["predicate"](x) else 1 for x in range(16)])
    for _ in range(iterations):
        ideal *= signs
        ideal = 2 * initial * np.vdot(initial, ideal) - ideal
    ideal_full = np.zeros(1 << o.num_qubits, dtype=complex)
    ideal_full[static_ft.clean_indices(o.num_qubits, mapping)] = ideal
    metrics = {name: row["metrics"] for name, row in records.items()}
    expected_t = (1 + 2 * iterations) * metrics["A"]["t_count"]
    if iterations:
        expected_t += iterations * (metrics["O"]["t_count"] + metrics["S0"]["t_count"])
    if metrics["search"]["t_count"] != expected_t:
        raise ValueError("Full-search T count differs from actual component word")
    target_gap = float(np.linalg.norm(target_state - ideal_full))
    if target_gap > TOLERANCE:
        raise ValueError("Recursive target disagrees with independent ideal recurrence")
    solution_count = sum(
        parts["encoding"].problem.is_valid(parts["encoding"].decode(x))
        for x in range(16)
    )
    if solution_count != 6:
        raise ValueError("Independent edge solution count changed")
    events = {
        name: static_ft.event_probabilities(state, parts["encoding"], mapping)
        for name, state in [
            ("recursive_target", target_state),
            ("emitted", emitted_state),
            ("ideal", ideal_full),
        ]
    }
    # Measured state gap covers the intended ideal experiment separately from
    # the compiler's original-target bound. No general ideal theorem is asserted.
    e = error + target_gap
    if (
        abs(
            events["emitted"]["proper_coloring_success"]
            - events["ideal"]["proper_coloring_success"]
        )
        > 2 * e + 1e-10
    ):
        raise ValueError("Success-event error check failed")
    if regime != "R1" and events["emitted"]["invalid_code_leakage"] > e**2 + 1e-10:
        raise ValueError("Invalid-code leakage check failed")
    if events["emitted"]["nonzero_scratch_probability"] > TOLERANCE:
        raise ValueError("Full search did not restore scratch")
    return {
        "status": "complete",
        "compiler_bound": out.metadata["error_bound"],
        "saved_metrics": metrics,
        "emitted_O_contract": emitted_o,
        "actual_inverse_operator_error": inverse_error,
        "A_operator_error": a_error,
        "original_target_clean_state_error": error,
        "recursive_to_ideal_state_gap": target_gap,
        "emitted_to_ideal_state_gap": float(np.linalg.norm(emitted_state - ideal_full)),
        "events": events,
        "M": solution_count,
        "N": 16 if regime == "R1" else 9,
        "known_M_method": "exhaustive independent proper-color reference on 16 assignments",
        "iterations_policy": "fixed supplied j, not claimed optimal",
        "achieved_break_even": None,
        "limitations": "Numerical clean-subspace evidence, not interval/general ideal admission",
    }


def compare_executed(hadamard: dict, valid: dict) -> dict:
    """Compare only completed matched-budget rows; never infer missing costs.

    A raw fixed-j T-charge loss/improvement is distinct from success-normalized
    break-even. Known M and measured comparable proper-color success are kept.
    This helper never prices failed/partial or mismatched precision rows.
    """
    if (
        hadamard.get("status") != "complete"
        or valid.get("status") != "complete"
        or hadamard.get("regime") != "R1"
        or valid.get("regime") not in ("R2", "R3")
        or hadamard.get("error_budget") != valid.get("error_budget")
        or hadamard.get("input_graph") != valid.get("input_graph")
    ):
        return {
            "achieved_break_even": None,
            "reason": "Missing comparable executed rows",
        }

    def costs(row):
        m = row["saved_metrics"]
        return StaticCosts(
            row["regime"],
            "same edge k3 proper-color event",
            row["iterations"],
            m["A"]["t_count"],
            m.get("O", {}).get("t_count"),
            m.get("S0", {}).get("t_count"),
        )

    comparison = compare_preparations(costs(hadamard), costs(valid))
    hp = hadamard["events"]["emitted"]["proper_coloring_success"]
    vp = valid["events"]["emitted"]["proper_coloring_success"]
    htotal = hadamard["saved_metrics"]["search"]["t_count"]
    vtotal = valid["saved_metrics"]["search"]["t_count"]
    return {
        "achieved_break_even": None,
        "raw_T_relation": comparison.relation,
        "raw_T_difference": str(comparison.difference_t),
        "raw_A_threshold": str(comparison.threshold.limit_t),
        "H_T_per_measured_success": htotal / hp if hp > 0 else None,
        "valid_T_per_measured_success": vtotal / vp if vp > 0 else None,
        "reason": "Fixed-j bounded numerical observations; no optimized-search advantage claim",
    }


def run_case(
    source_root: Path,
    executable: Path,
    *,
    regime: str,
    iterations: int = 1,
    error_budget: float = 1e-3,
    output_root: Path = Path("dump"),
    limits: GraphLimits = GraphLimits(),
    options: rotations.SynthesisOptions = rotations.SynthesisOptions(),
) -> Path:
    """Persist a single bounded actual edge experiment, including every failure."""
    identities = static_ft.verify_admission(source_root, executable)
    if (
        Path(__file__).resolve()
        != (source_root / "src/logique/benchmarks/graph_ft.py").resolve()
    ):
        raise ValueError("Graph harness import path differs from candidate")
    directory = new_dump_directory("graph-ft-edge", root=output_root)
    record = {
        "status": "running",
        "regime": regime,
        "iterations": iterations,
        "error_budget": error_budget,
        "limits": asdict(limits),
        "options": asdict(options),
        "identities": identities,
        "input_graph": {"vertices": [7, 11], "edges": [[7, 11]], "colors": 3},
        "native_executable": str(executable.resolve()),
        "seed": None,
        "seed_reason": "deterministic native none/Bennett and bounded SK",
        "source_root": str(source_root.resolve()),
        "harness_sha256": static_ft.sha256(Path(__file__)),
        "qiskit": qiskit.__version__,
        "numpy": np.__version__,
        "resource_scope": "one sequential numerical/native process; external group timeout required; RSS observational",
    }
    _write(directory / "result.json", record)
    start = time.monotonic()
    try:
        with static_ft._deadline(limits.seconds):
            parts = build_components(regime, executable, directory, limits)
            record.update(
                caller_contract=parts["contract"],
                allocation=parts["allocation"],
                input_sha256=parts["input_sha256"],
            )
            _write(directory / "result.json", record)
            record.update(
                execute_case(
                    directory, parts, regime, iterations, error_budget, limits, options
                )
            )
    except (ValueError, RuntimeError, OSError, TimeoutError) as error:
        record.update(
            status="failed",
            failure={
                "type": type(error).__name__,
                "message": str(error),
                "trials": getattr(error, "metadata", None),
            },
            achieved_break_even=None,
        )
    finally:
        record.update(
            seconds=time.monotonic() - start,
            self_ru_maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            children_ru_maxrss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            rss_scope="high-water self/reaped children, bytes Darwin/KiB Linux; no hard cap",
            identities_after=static_ft.verify_admission(source_root, executable),
        )
        _write(directory / "result.json", record)
    return directory


def main() -> None:
    """Execute one edge row with an explicit admitted binary and resource bounds."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--regime", choices=("R1", "R2", "R3"), required=True)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--error-budget", type=float, default=1e-3)
    parser.add_argument("--output-root", type=Path, default=Path("dump"))
    args = parser.parse_args()
    directory = run_case(
        Path(__file__).resolve().parents[3],
        args.executable,
        regime=args.regime,
        iterations=args.iterations,
        error_budget=args.error_budget,
        output_root=args.output_root,
    )
    print(directory, flush=True)
    if json.loads((directory / "result.json").read_text())["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
