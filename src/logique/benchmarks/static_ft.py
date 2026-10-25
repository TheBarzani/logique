"""Bounded static complete-search pilot, separate from the main study runner.

Only the hash-bound numerical rotation contract is used. This pilot neither
certifies ideal amplitudes nor admits dynamic/RUS costs or paper claims.
Run with ``python -m logique.benchmarks.static_ft --help`` in the research env.
"""

from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import resource
import signal
import time
from typing import Callable, Iterator, Sequence

import numpy as np
import qiskit
from qiskit import QuantumCircuit, qpy
from qiskit.quantum_info import Operator

from logique.benchmarks import rotations
from logique.benchmarks.costs import CLIFFORD_T_BASIS, decompose_mcx, ft_metrics
from logique.circuits.grover import coloring_preparation
from logique.coloring import ColoringEncoding, ColoringProblem
from logique.paths import new_dump_directory


ADMITTED_HASHES = {
    "src/logique/benchmarks/rotations.py": (
        "5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595"
    ),
    "tests/test_rotations.py": (
        "88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77"
    ),
    "docs/research/rotation_norm_admission.md": (
        "01776d3dcc4527d7914aa1893db18eea336b76ad3518071b83eb71ce2b1c4c2d"
    ),
}
NATIVE_SHA256 = "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
METHOD = "xag_bennett"
MCX_POLICY = "gray_code"  # Exact, no borrowed or appended scratch; restoring.
MAX_OPERATOR_QUBITS = 4
TOLERANCE = 1e-10


class ValidationLimitError(ValueError):
    """The instance exceeds this pilot's dense-validation domain."""


class PilotTimeoutError(TimeoutError):
    """The single sequential pilot exhausted its wall-clock allowance."""


def sha256(path: Path) -> str:
    """Return the identity of an input or saved artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_admission(source_root: Path, executable: Path) -> dict:
    """Fail closed on compiler, tests, review, import path or binary drift."""
    identities = {name: sha256(source_root / name) for name in ADMITTED_HASHES}
    if identities != ADMITTED_HASHES:
        raise ValueError("Exact reviewed rotation hashes do not match")
    expected = source_root / "src/logique/benchmarks/rotations.py"
    if Path(rotations.__file__).resolve() != expected.resolve():
        raise ValueError("PYTHONPATH does not resolve to the assigned worktree src")
    if sha256(executable) != NATIVE_SHA256:
        raise ValueError(
            "Native binary differs from admitted common-preprocessing build"
        )
    return {**identities, "native_executable": sha256(executable)}


def numeric_matrix(circuit: QuantumCircuit) -> np.ndarray:
    """Resolve the original recursive numeric target, with scalar phase intact.

    No rotation lowering, normalization, phase fitting or emitted approximation
    is used here. Qiskit's Operator resolves the original gate definitions.
    """
    if circuit.num_qubits > MAX_OPERATOR_QUBITS:
        raise ValidationLimitError("Dense operators are limited to four qubits")
    return np.asarray(Operator(circuit).data)


def zero_reflection(width: int) -> QuantumCircuit:
    """Construct signed S0 = 2|0><0| - I, then explicitly restore MCX scratch."""
    if not 1 <= width <= MAX_OPERATOR_QUBITS:
        raise ValidationLimitError("S0 width must be between one and four")
    circuit = QuantumCircuit(width, global_phase=math.pi)
    circuit.x(range(width))
    if width == 1:
        circuit.z(0)
    else:
        circuit.h(width - 1)
        circuit.mcx(list(range(width - 1)), width - 1)
        circuit.h(width - 1)
    circuit.x(range(width))
    lowered, _ = decompose_mcx(circuit, MCX_POLICY)
    return lowered


def _mapping(width: int, mapping: Sequence[int]) -> list[int]:
    wires = list(mapping)
    if (
        not wires
        or len(set(wires)) != len(wires)
        or any(type(q) is not int or not 0 <= q < width for q in wires)
    ):
        raise ValueError("Data mapping must contain distinct in-range integer wires")
    return wires


def clean_indices(width: int, mapping: Sequence[int]) -> list[int]:
    """Map logical little-endian data states into zero-initialized scratch."""
    wires = _mapping(width, mapping)
    return [
        sum(((x >> bit) & 1) << wire for bit, wire in enumerate(wires))
        for x in range(1 << len(wires))
    ]


def validate_contract(
    preparation: QuantumCircuit,
    oracle: QuantumCircuit,
    reflection: QuantumCircuit,
    mapping: Sequence[int],
    predicate: Callable[[int], bool],
) -> dict:
    """Independently check every data column, phase sign, mapping and scratch.

    All basis columns imply the coherent clean-subspace contract by linearity.
    No assumption is made about dirty initial workspace.
    """
    indices = clean_indices(oracle.num_qubits, mapping)
    if preparation.num_qubits != len(mapping) or reflection.num_qubits != len(mapping):
        raise ValueError("A and S0 must act on exactly the mapped data register")
    matrix = numeric_matrix(oracle)
    expected = np.zeros((len(matrix), len(indices)), dtype=complex)
    for x, index in enumerate(indices):
        expected[index, x] = -1 if predicate(x) else 1
    phase_error = float(np.linalg.norm(matrix[:, indices] - expected, 2))
    scratch = [i for i in range(len(matrix)) if i not in indices]
    scratch_error = (
        float(np.linalg.norm(matrix[np.ix_(scratch, indices)], 2)) if scratch else 0.0
    )
    signed = -np.eye(len(indices), dtype=complex)
    signed[0, 0] = 1
    reflection_error = float(np.linalg.norm(numeric_matrix(reflection) - signed, 2))
    a = numeric_matrix(preparation)
    unitary_defect = float(np.linalg.norm(a.conj().T @ a - np.eye(len(a)), 2))
    if max(phase_error, scratch_error, reflection_error, unitary_defect) > TOLERANCE:
        raise ValueError("Clean oracle, signed S0, restoration or A contract failed")
    return {
        "data_qubits": list(mapping),
        "clean_data_columns": len(indices),
        "phase_operator_error": phase_error,
        "scratch_operator_error": scratch_error,
        "signed_s0_operator_error": reflection_error,
        "preparation_unitarity_defect": unitary_defect,
        "coverage": "exhaustive coherent clean subspace; scratch initially zero",
    }


def original_search_matrix(
    preparation: QuantumCircuit,
    oracle: QuantumCircuit,
    reflection: QuantumCircuit,
    mapping: Sequence[int],
    iterations: int,
) -> np.ndarray:
    """Multiply original numeric targets and the numeric adjoint of original A."""
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be a nonnegative integer")
    _mapping(oracle.num_qubits, mapping)
    a = QuantumCircuit(oracle.num_qubits)
    a.compose(preparation, qubits=mapping, inplace=True)
    s = QuantumCircuit(oracle.num_qubits)
    s.compose(reflection, qubits=mapping, inplace=True)
    am, om, sm = numeric_matrix(a), numeric_matrix(oracle), numeric_matrix(s)
    result = am.copy()
    for _ in range(iterations):
        result = am @ sm @ am.conj().T @ om @ result
    return result


def event_probabilities(
    state: np.ndarray, encoding: ColoringEncoding, mapping: Sequence[int]
) -> dict:
    """Separate unused-code leakage, proper coloring and nonzero scratch events."""
    width = (len(state) - 1).bit_length()
    indices = set(clean_indices(width, mapping))
    success = invalid = scratch = 0.0
    for basis, amplitude in enumerate(state):
        data = sum(((basis >> wire) & 1) << bit for bit, wire in enumerate(mapping))
        colors = encoding.decode(data)
        probability = float(abs(amplitude) ** 2)
        if any(color >= encoding.problem.colors for color in colors.values()):
            invalid += probability
        if encoding.problem.is_valid(colors):
            success += probability
        if basis not in indices:
            scratch += probability
    return {
        "proper_coloring_success": success,
        "invalid_code_leakage": invalid,
        "nonzero_scratch_probability": scratch,
        "state_norm_squared": float(np.vdot(state, state).real),
    }


def _json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _serializable(circuit: QuantumCircuit, *, emitted: bool) -> QuantumCircuit:
    # Qiskit 2.1.1 QPY loses inverse StatePreparation semantics. Expand source
    # definitions to U/CX leaves; compare to the ORIGINAL target on reload.
    # Emitted circuits already have standard Clifford+T leaves and stay intact.
    return circuit if emitted else circuit.decompose(reps=32)


def save_circuit(
    directory: Path,
    name: str,
    circuit: QuantumCircuit,
    *,
    emitted: bool,
    metadata: dict | None = None,
) -> tuple[QuantumCircuit, dict]:
    """Save QPY, reload, check phase-sensitive semantics and recompute costs."""
    path = directory / f"{name}.qpy"
    before = numeric_matrix(circuit)
    with path.open("wb") as stream:
        qpy.dump(_serializable(circuit, emitted=emitted), stream)
    with path.open("rb") as stream:
        loaded = qpy.load(stream)
    if len(loaded) != 1:
        raise ValueError("Expected exactly one saved circuit")
    restored = loaded[0]
    error = float(np.linalg.norm(numeric_matrix(restored) - before, 2))
    if error > TOLERANCE:
        raise ValueError(f"QPY semantic failure for {name}: {error}")
    record = {
        "qpy_sha256": sha256(path),
        "qubits": restored.num_qubits,
        "global_phase": float(restored.global_phase),
        "counts": dict(restored.count_ops()),
        "roundtrip_operator_error": error,
        "source_definitions_expanded": not emitted,
        "synthesis": metadata,
    }
    if emitted:
        if set(restored.count_ops()) - set(CLIFFORD_T_BASIS):
            raise ValueError("Saved emitted circuit has unsynthesized gates")
        record["metrics"] = ft_metrics(restored)
    _json(directory / f"{name}.json", record)
    return restored, record


@contextmanager
def _deadline(seconds: float) -> Iterator[None]:
    if not math.isfinite(seconds) or not 0 < seconds <= 300:
        raise ValueError("Sequential pilot allowance must be in (0, 300] seconds")

    def expired(signum, frame):
        raise PilotTimeoutError("Sequential pilot wall-clock limit reached")

    previous = signal.signal(signal.SIGALRM, expired)
    old_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, *old_timer)
        signal.signal(signal.SIGALRM, previous)


def _components(problem: ColoringProblem, regime: str, executable: Path) -> dict:
    from logique.synthesis import synthesize

    encoding = ColoringEncoding(problem)
    # k=4 removes only the k=3 domain comparator while retaining all vertices,
    # two bits per vertex, and edge inequalities. Decoding/reference remain k=3.
    source = ColoringEncoding(
        ColoringProblem(
            vertices=problem.vertices,
            edges=problem.edges,
            colors=4 if regime == "R3" else 3,
        )
    )
    native = synthesize(source, METHOD, preprocessing="none", executable=executable)
    if native.circuit.num_qubits > MAX_OPERATOR_QUBITS:
        raise ValidationLimitError(
            f"Native {METHOD} {regime} uses {native.circuit.num_qubits} qubits; "
            "operator limit 4, statevector limit 5"
        )
    original_oracle = native.phase_oracle()
    oracle, lowering = decompose_mcx(original_oracle, MCX_POLICY)
    # Open-control CCX singleton classes lie outside the admitted compiler's
    # vocabulary. Resolve their exact X-conjugated closed-CCX definitions.
    # Retain the original oracle for independent target comparisons.
    opened = sorted(
        {item.operation.name for item in oracle.data if "_o" in item.operation.name}
    )
    if opened:
        oracle = oracle.decompose(gates_to_decompose=opened)
    preparation = coloring_preparation(encoding)
    if regime == "R1":
        preparation = QuantumCircuit(encoding.input_count)
        preparation.h(range(encoding.input_count))
    s0 = zero_reflection(encoding.input_count)
    mapping = native.metadata["input_qubits"]
    if len(mapping) != encoding.input_count:
        raise ValueError("Native input mapping width changed")

    def predicate(x: int) -> bool:
        assignment = encoding.decode(x)
        if regime != "R3":
            return problem.is_valid(assignment)
        return all(assignment[u] != assignment[v] for u, v in problem.edges)

    contract = validate_contract(preparation, oracle, s0, mapping, predicate)
    # Also check unlowered O against lowered O, without costing either yet.
    lowering_error = float(
        np.linalg.norm(numeric_matrix(oracle) - numeric_matrix(original_oracle), 2)
    )
    if lowering_error > TOLERANCE:
        raise ValueError("MCX lowering changed the oracle")
    return {
        "encoding": encoding,
        "preparation": preparation,
        "oracle": oracle,
        "original_oracle": original_oracle,
        "zero_reflection": s0,
        "mapping": mapping,
        "contract": contract,
        "native": native.metadata,
        "mcx": {
            **lowering,
            "open_controls_resolved": opened,
            "lowering_operator_error": lowering_error,
        },
    }


def _run_case(directory: Path, parts: dict, iterations: int, budget: float) -> dict:
    a, o, s = (parts[key] for key in ("preparation", "oracle", "zero_reflection"))
    mapping = parts["mapping"]
    original_o = parts.get("original_oracle", o)
    # Semantic caller checks precede synthesis and costing for every case.
    for name, circuit in [("target_A", a), ("target_O", original_o), ("target_S0", s)]:
        save_circuit(directory, name, circuit, emitted=False)
    target_circuit = QuantumCircuit(o.num_qubits)
    target_circuit.compose(a, mapping, inplace=True)
    for _ in range(iterations):
        target_circuit.compose(original_o, inplace=True)
        target_circuit.compose(a.inverse(), mapping, inplace=True)
        target_circuit.compose(s, mapping, inplace=True)
        target_circuit.compose(a, mapping, inplace=True)
    save_circuit(directory, "target_search", target_circuit, emitted=False)
    out = rotations.compile_search(
        a,
        o,
        s,
        data_qubits=mapping,
        iterations=iterations,
        error_budget=budget,
        options=rotations.SynthesisOptions(
            max_recursion=5, basic_approximation_depth=12
        ),
    )
    if out.preparation.circuit is None:
        raise ValueError("Compiler omitted the required preparation")
    if out.preparation_inverse != out.preparation.circuit.inverse():
        raise ValueError("Compiler did not reuse actual emitted A inverse")
    circuits = {
        "A": (out.preparation.circuit, out.preparation.metadata),
        "A_inverse": (out.preparation_inverse, {"actual_emitted_inverse": True}),
        "O": (out.oracle.circuit, out.oracle.metadata),
        "S0": (out.zero_reflection.circuit, out.zero_reflection.metadata),
        "search": (out.circuit, out.metadata),
    }
    saved = {}
    records = {}
    for name, (circuit, metadata) in circuits.items():
        if circuit is None:
            _json(directory / f"{name}.json", {"unused": True, "synthesis": metadata})
        else:
            saved[name], records[name] = save_circuit(
                directory, name, circuit, emitted=True, metadata=metadata
            )
    # Save diffusion and a reconstructed whole search from RELOADED components.
    reconstructed = QuantumCircuit(o.num_qubits)
    reconstructed.compose(saved["A"], mapping, inplace=True)
    if iterations:
        diffusion = QuantumCircuit(o.num_qubits)
        diffusion.compose(saved["A_inverse"], mapping, inplace=True)
        diffusion.compose(saved["S0"], mapping, inplace=True)
        diffusion.compose(saved["A"], mapping, inplace=True)
        _, records["diffusion"] = save_circuit(
            directory, "diffusion", diffusion, emitted=True
        )
        for _ in range(iterations):
            reconstructed.compose(saved["O"], inplace=True)
            reconstructed.compose(diffusion, inplace=True)
    assembly_error = float(
        np.linalg.norm(
            numeric_matrix(reconstructed) - numeric_matrix(saved["search"]), 2
        )
    )
    if assembly_error > TOLERANCE:
        raise ValueError("Saved components do not reconstruct saved search")
    if (
        np.linalg.norm(
            numeric_matrix(saved["A_inverse"]) - numeric_matrix(saved["A"]).conj().T, 2
        )
        > TOLERANCE
    ):
        raise ValueError("Saved inverse lost phase or adjoint semantics")
    costs = {name: row["metrics"] for name, row in records.items()}
    expected_t = costs["A"]["t_count"]
    if iterations:
        expected_t += iterations * (
            2 * costs["A"]["t_count"] + costs["O"]["t_count"] + costs["S0"]["t_count"]
        )
    if costs["search"]["t_count"] != expected_t:
        raise ValueError("Saved complete-search T-count composition failed")
    target = original_search_matrix(a, original_o, s, mapping, iterations)
    emitted = numeric_matrix(saved["search"])
    error = float(np.linalg.norm(emitted - target, 2))
    if error > out.metadata["error_bound"] + 1e-12:
        raise ValueError("Original recursive numeric target exceeds declared bound")
    # Independent ideal state recurrence; this is a measured target gap, NOT
    # an ideal-amplitude certificate or an extension of the compiler theorem.
    encoding = parts["encoding"]
    regime = parts["regime"]
    size = 1 << encoding.input_count
    ideal = np.ones(size) / math.sqrt(size)
    if regime != "R1":
        ideal = np.array(
            [
                float(all(c < 3 for c in encoding.decode(x).values()))
                for x in range(size)
            ]
        )
        ideal /= np.linalg.norm(ideal)
    ideal_initial = ideal.copy()
    for _ in range(iterations):
        marked = np.array(
            [
                (
                    encoding.problem.is_valid(encoding.decode(x))
                    if regime != "R3"
                    else all(
                        encoding.decode(x)[u] != encoding.decode(x)[v]
                        for u, v in encoding.problem.edges
                    )
                )
                for x in range(size)
            ]
        )
        ideal = ideal * np.where(marked, -1, 1)
        ideal = 2 * ideal_initial * np.vdot(ideal_initial, ideal) - ideal
    ideal_full = np.zeros(len(target), dtype=complex)
    ideal_full[clean_indices(o.num_qubits, mapping)] = ideal
    target_state, emitted_state = target[:, 0], emitted[:, 0]
    return {
        "status": "complete",
        "compiler": out.metadata,
        "saved_metrics": costs,
        "saved_assembly_operator_error": assembly_error,
        "original_target_operator_error": error,
        "ideal_target_state_gap": float(np.linalg.norm(target_state - ideal_full)),
        "emitted_to_ideal_state_gap": float(np.linalg.norm(emitted_state - ideal_full)),
        "recursive_target": event_probabilities(target_state, encoding, mapping),
        "emitted": event_probabilities(emitted_state, encoding, mapping),
        "ideal": event_probabilities(ideal_full, encoding, mapping),
        "limitations": "Numerical checks, not interval or ideal-amplitude certificates",
    }


def run_pilot(
    source_root: Path,
    executable: Path,
    *,
    output_root: Path = Path("dump"),
    seconds: float = 300,
) -> Path:
    """Run six primary rows and one R2/j=1 sensitivity, serially within 300s.

    Edge k=3 is attempted first. If its native width exceeds four qubits, all
    rows use one isolated vertex k=3 and explicitly carry no graph comparison.
    Every failed synthesis is retained with its trials, without analytic costs.
    """
    identities = verify_admission(source_root, executable)
    if not math.isfinite(seconds) or not 0 < seconds <= 300:
        raise ValueError("Sequential pilot allowance must be in (0, 300] seconds")
    directory = new_dump_directory("static-ft-pilot", root=output_root)
    start = time.monotonic()
    cases = [(r, j, 1e-3) for r in ("R1", "R2", "R3") for j in (0, 1)]
    cases.append(("R2", 1, 1e-2))
    manifest = {
        "status": "running",
        "identities": identities,
        "native_executable": str(executable.resolve()),
        "method": METHOD,
        "common_preprocessing": "none",
        "mcx_restoring_policy": MCX_POLICY,
        "options": {"max_recursion": 5, "basic_approximation_depth": 12},
        "basis_net": ["h", "t", "tdg"],
        "qiskit": qiskit.__version__,
        "numpy": np.__version__,
        "source_root": str(source_root.resolve()),
        "harness_sha256": sha256(Path(__file__)),
        "bounds": {"seconds": seconds, "dense_qubits": 4, "statevector_qubits": 5},
        "resource_policy": "one sequential job; bounded tiny arrays; no build/install",
        "scientific_scope": (
            "Restricted static numerical contract; no superiority, preparation "
            "break-even, RUS/dynamic, protocol freeze or paper approval"
        ),
        "rows": [],
    }
    _json(directory / "manifest.json", manifest)
    current: dict | None = None
    try:
        with _deadline(seconds):
            problem = ColoringProblem(vertices=(7, 11), edges=((7, 11),), colors=3)
            cache = {}
            try:
                cache["R1"] = _components(problem, "R1", executable)
                manifest["graph_comparison"] = "edge graph only; no baseline comparison"
            except ValidationLimitError as error:
                manifest["edge_failure"] = {
                    "type": type(error).__name__,
                    "message": str(error),
                }
                problem = ColoringProblem(vertices=(7,), edges=(), colors=3)
                manifest["graph_comparison"] = (
                    "NO GRAPH COMPARISON: one isolated vertex k=3"
                )
            manifest["problem"] = {
                "vertices": list(problem.vertices),
                "edges": list(problem.edges),
                "colors": 3,
            }
            for regime, iterations, budget in cases:
                current = {
                    "regime": regime,
                    "iterations": iterations,
                    "error_budget": budget,
                    "status": "running",
                }
                row_dir = directory / f"{regime}-j{iterations}-{budget:g}"
                row_dir.mkdir()
                current["artifacts"] = row_dir.name
                manifest["rows"].append(current)
                _json(directory / "manifest.json", manifest)
                row_start = time.monotonic()
                try:
                    if regime not in cache:
                        cache[regime] = _components(problem, regime, executable)
                    parts = cache[regime]
                    parts["regime"] = regime
                    current["caller_contract"] = parts["contract"]
                    _json(row_dir / "native.json", parts["native"])
                    _json(row_dir / "mcx.json", parts["mcx"])
                    current.update(_run_case(row_dir, parts, iterations, budget))
                except rotations.PrecisionNotReachedError as error:
                    current.update(
                        status="failed_precision",
                        failure={
                            "type": type(error).__name__,
                            "message": str(error),
                            "trials": error.metadata,
                        },
                    )
                except PilotTimeoutError:
                    raise
                except (ValueError, RuntimeError) as error:
                    current.update(
                        status="failed_validation",
                        failure={"type": type(error).__name__, "message": str(error)},
                    )
                finally:
                    current["seconds"] = time.monotonic() - row_start
                    _json(row_dir / "result.json", current)
                    _json(directory / "manifest.json", manifest)
            manifest["status"] = "bounded_complete"
    except PilotTimeoutError as error:
        manifest["status"] = "timeout"
        manifest["failure"] = {"type": type(error).__name__, "message": str(error)}
        if current is not None:
            current.update(
                status="timeout",
                failure={"type": type(error).__name__, "message": str(error)},
            )
            _json(directory / current["artifacts"] / "result.json", current)
    except (ValueError, RuntimeError, OSError) as error:
        manifest["status"] = "failed_preflight"
        manifest["failure"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        attempted = {
            (r["regime"], r["iterations"], r["error_budget"]) for r in manifest["rows"]
        }
        manifest["not_run_cases"] = [
            {"regime": r, "iterations": j, "error_budget": b}
            for r, j, b in cases
            if (r, j, b) not in attempted
        ]
        manifest["seconds"] = time.monotonic() - start
        manifest["self_ru_maxrss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        manifest["children_ru_maxrss"] = resource.getrusage(
            resource.RUSAGE_CHILDREN
        ).ru_maxrss
        manifest["rss_units"] = (
            "bytes on Darwin, KiB on Linux; high-water, not OS enforcement"
        )
        manifest["identities_after"] = verify_admission(source_root, executable)
        _json(directory / "manifest.json", manifest)
    return directory


def main() -> None:
    """Run this fixed pilot using an explicit admitted private native binary."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("dump"))
    parser.add_argument("--seconds", type=float, default=300)
    args = parser.parse_args()
    print(
        run_pilot(
            Path(__file__).resolve().parents[3],
            args.executable,
            output_root=args.output_root,
            seconds=args.seconds,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
