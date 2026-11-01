"""Bounded complete-predicate C5 best-fit experiment; independent review pending.

Run with the existing research interpreter and candidate src on PYTHONPATH.
Every invocation creates fresh evidence. No noise harness or historical result
is modified. Components are flattened to U/CX before statevector evolution.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

from logique.paths import new_dump_directory

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/Users/mar/codex-work/logique/.venv/bin/python")
NATIVE = Path(
    "/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/"
    "worktrees/native-contract/dump/1025025511-native-contract/"
    "build/boolean_synthesis"
)
NATIVE_SHA = "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
SEED = 37
TOLERANCE = 1e-10
THREADS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "RAYON_NUM_THREADS",
    "QISKIT_NUM_PROCS",
    "CMAKE_BUILD_PARALLEL_LEVEL",
)
BUDGET = {
    "child_seconds": 120,
    "cumulative_seconds": 900,
    "declared_process_bytes": 6 * 1024**3,
    "max_statevector_qubits": 18,
    "dense_operator": "none",
    "memory_enforcement": (
        "preallocation width guard and sampled direct-child RSS; terminate on "
        "observed excess; not a hard OS/process-group allocation cap; "
        "wait4 high water may include reaped descendants"
    ),
    "parallelism": 1,
}


def write_json(path: Path, value: object) -> None:
    """Write only a new JSON artifact, preserving partial and failed evidence."""
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def digest(path: Path) -> str:
    """Hash the actual bytes of one evidence or source file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_source() -> None:
    """Reject accidental installed/root-source imports in this worker."""
    import logique
    import logique.coloring.encoding
    import logique.circuits.grover
    import logique.synthesis.result

    for module in (
        logique,
        logique.coloring.encoding,
        logique.circuits.grover,
        logique.synthesis.result,
    ):
        assert Path(module.__file__).resolve().is_relative_to(ROOT / "src")


def problem():
    """Return the unprecolored five-cycle with deterministic vertex order."""
    from logique.coloring import ColoringProblem

    return ColoringProblem((0, 1, 2, 3, 4), ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4)), 3)


def preflight(metadata: dict, max_qubits: int = 18) -> tuple[int, list[int]]:
    """Validate native width and ordered data mapping BEFORE quantum arrays."""
    width = metadata["num_qubits"]
    wires = metadata["input_qubits"]
    outputs = metadata["output_qubits"]
    if type(max_qubits) is not int or not 1 <= max_qubits <= 18:
        raise ValueError("statevector cap must be an integer <=18")
    if type(width) is not int or not 10 <= width <= max_qubits:
        raise ValueError(f"actual native width {width} exceeds cap {max_qubits}")
    if (
        len(wires) != 10
        or any(type(q) is not int or not 0 <= q < width for q in wires)
        or len(set(wires)) != 10
        or len(outputs) != 1
        or type(outputs[0]) is not int
        or not 0 <= outputs[0] < width
        or outputs[0] in wires
    ):
        raise ValueError("invalid native input/output allocation")
    return width, wires


def packed_classes() -> tuple[list[bool], list[bool]]:
    """Independently classify all 1024 LSB-first words without encoder helpers."""
    good, valid = [], []
    for word in range(1024):
        colors = [(word >> (2 * vertex)) & 3 for vertex in range(5)]
        codes = all(color < 3 for color in colors)
        valid.append(codes)
        good.append(codes and all(colors[v] != colors[(v + 1) % 5] for v in range(5)))
    return good, valid


def physical_indices(width: int, wires: list[int]) -> list[int]:
    """Embed each logical data word into the emitted physical wire allocation."""
    if len(set(wires)) != len(wires) or any(not 0 <= q < width for q in wires):
        raise ValueError("invalid physical mapping")
    return [
        sum(((word >> i) & 1) << q for i, q in enumerate(wires))
        for word in range(1 << len(wires))
    ]


def flatten_component(circuit):
    """Lower a reusable component without assuming its input data is zero.

    Qiskit's zero-initialized default is a program-entry assumption. Applying
    it to an oracle component permits clean-ancilla synthesis to borrow data
    that will actually be in superposition when the component is called.
    """
    from qiskit import transpile
    from logique.benchmarks.coloring_study import _resolved_qpy_circuit

    resolved, _ = _resolved_qpy_circuit(circuit)
    return transpile(
        resolved,
        basis_gates=["u", "cx"],
        optimization_level=0,
        seed_transpiler=SEED,
        qubits_initially_zero=False,
        num_processes=1,
    )


def preparation_pair(preparation):
    """Emit A once and invert those exact emitted gates for every A dagger."""
    emitted = flatten_component(preparation)
    return emitted, emitted.inverse()


def compile_candidate(run: Path) -> None:
    """Save exact native request, response, diagnostics and width preflight."""
    from logique.coloring import encode_coloring

    assert_source()
    if digest(NATIVE) != NATIVE_SHA:
        raise AssertionError("prescribed native binary changed")
    source = encode_coloring(problem()).write_verilog(run / "predicate.v")
    request = {
        "path": str(source.resolve()),
        "method": "best_fit",
        "outer_cut": 16,
        "inner_cut": 4,
    }
    write_json(run / "native-request.json", request)
    proc = subprocess.run(
        [str(NATIVE)],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=110,
    )
    (run / "native-stdout.json").write_text(proc.stdout)
    (run / "native-stderr.log").write_text(proc.stderr)
    write_json(run / "native-exit.json", {"returncode": proc.returncode})
    proc.check_returncode()
    metadata = json.loads(proc.stdout)
    try:
        width, wires = preflight(metadata)
    except ValueError as error:
        write_json(
            run / "preflight.json", {"status": "infeasible", "reason": str(error)}
        )
        return
    write_json(
        run / "preflight.json",
        {
            "status": "feasible",
            "width": width,
            "data_qubits": wires,
            "output_qubits": metadata["output_qubits"],
            "budget": BUDGET,
            "profile": "unbalanced complete encoder; legacy best_fit refactoring default; cuts16/4",
            "predicate_sha256": digest(source),
        },
    )


def simulate(run: Path, regime: str) -> None:
    """Validate compiled marking and execute every first-lobe row from QPY."""
    assert_source()
    metadata = json.loads((run / "native-stdout.json").read_text())
    width, wires = preflight(metadata)
    # Width and budgets above precede imports that might allocate quantum arrays.
    import numpy as np
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Statevector
    from logique.benchmarks.ideal_iterations import (
        count_coloring_support,
        ideal_iteration_ledger,
    )
    from logique.benchmarks.coloring_study import _qpy_semantic_signature
    from logique.circuits.grover import coloring_preparation, _reflection
    from logique.circuits.records import records_to_qiskit
    from logique.coloring import encode_coloring
    from logique.synthesis.result import SynthesisResult
    from logique.verification.phase import verify_phase_oracle
    from logique.verification.classical import (
        validate,
        input_assignments,
        _apply_record,
    )

    if regime not in ("R1", "R2"):
        raise ValueError("only complete-predicate R1/R2 supported")
    output = run / regime
    output.mkdir(exist_ok=False)
    encoding = encode_coloring(problem())
    raw = records_to_qiskit(metadata["gates"], width)
    native_result = SynthesisResult(raw, metadata)
    oracle = native_result.phase_oracle()
    raw_validation = validate(native_result)
    phase_validation = verify_phase_oracle(native_result, encoding=encoding)
    assert phase_validation["assignments"] == 1024
    assert phase_validation["marked_assignments"] == 30
    count = count_coloring_support(problem(), regime=regime)
    ledger = ideal_iteration_ledger(
        count.marked, count.support, max_rows=130, max_iterations=129
    )
    good_list, valid_list = packed_classes()
    assert sum(good_list) == count.marked == (3 - 1) ** 5 - (3 - 1) == 30
    assert sum(valid_list) == 3**5 == 243
    good, valid = np.array(good_list), np.array(valid_list)
    compiled_bits = np.zeros((width, 1024), dtype=bool)
    compiled_bits[wires] = input_assignments(10)
    compiled_phases = np.ones(1024, dtype=complex)
    for record in metadata["gates"]:
        _apply_record(compiled_bits, compiled_phases, record)
    assert np.array_equal(compiled_bits[metadata["output_qubits"][0]], good)
    support = np.ones(1024, dtype=bool) if regime == "R1" else valid
    assert int(support.sum()) == count.support
    indices = np.array(physical_indices(width, wires))
    dirty = np.ones(1 << width, dtype=bool)
    dirty[indices] = False
    preparation = QuantumCircuit(10)
    if regime == "R1":
        preparation.h(range(10))
    else:
        preparation = coloring_preparation(encoding)
    preparation, preparation_inverse = preparation_pair(preparation)
    diffusion = _reflection(preparation)
    diffusion.global_phase += math.pi
    components, artifacts = {}, {}
    # Raw emitted A is saved together with its ACTUAL inverse; flattening uses
    # exact logical U/CX, not a finite-precision Clifford+T compiler.
    for name, circuit in (
        ("raw", raw),
        ("oracle", oracle),
        ("preparation", preparation),
        ("preparation_inverse", preparation_inverse),
        ("diffusion", diffusion),
    ):
        flat = flatten_component(circuit)
        assert all(item.operation.num_qubits <= 2 for item in flat.data)
        path = output / f"{name}.qpy"
        with path.open("xb") as stream:
            qpy.dump(flat, stream)
        with path.open("rb") as stream:
            loaded = qpy.load(stream)[0]
        assert _qpy_semantic_signature(loaded) == _qpy_semantic_signature(flat)
        components[name] = loaded
        artifacts[name] = {
            "sha256": digest(path),
            "qubits": loaded.num_qubits,
            "instructions": len(loaded.data),
            "global_phase": float(loaded.global_phase),
        }
    # Compiled positive witnesses and every invalid/edge-negative are checked
    # above by exhaustive monomial tracking, then explicit saved-QPY basis probes.
    witnesses = {
        "positive": next(i for i, value in enumerate(good_list) if value),
        "invalid_code": next(i for i in range(1024) if not valid_list[i]),
        "edge_violation": next(
            i for i in range(1024) if valid_list[i] and not good_list[i]
        ),
    }
    witness_results = {}
    for name, word in witnesses.items():
        state = Statevector.from_int(int(indices[word]), 1 << width)
        raw_state = state.copy().evolve(components["raw"])
        output_one = sum(
            float(abs(a) ** 2)
            for i, a in enumerate(raw_state.data)
            if (i >> metadata["output_qubits"][0]) & 1
        )
        marked = int(good[word])
        assert abs(output_one - marked) <= TOLERANCE
        phased = state.copy().evolve(components["oracle"])
        residual = float(
            np.max(np.abs(phased.data - (-1 if marked else 1) * state.data))
        )
        assert residual <= TOLERANCE
        witness_results[name] = {
            "logical_word": word,
            "colors": [(word >> (2 * v)) & 3 for v in range(5)],
            "physical_basis": int(indices[word]),
            "raw_output_one_probability": output_one,
            "expected_marked": marked,
            "phase_restoration_residual": residual,
        }
    # Arbitrary complex coherent data checks absolute phase and full workspace,
    # without alignment; diffusion checked independently as 2|s><s|-I.
    rng = np.random.default_rng(SEED)
    amplitudes = rng.normal(size=1024) + 1j * rng.normal(size=1024)
    amplitudes /= np.linalg.norm(amplitudes)
    probe = np.zeros(1 << width, dtype=complex)
    probe[indices] = amplitudes
    expected = probe.copy()
    expected[indices[good]] *= -1
    oracle_residual = float(
        np.max(
            np.abs(
                Statevector(probe.copy()).evolve(components["oracle"]).data - expected
            )
        )
    )
    s = support.astype(complex) / math.sqrt(count.support)
    expected_data = 2 * s * np.vdot(s, amplitudes) - amplitudes
    expected.fill(0)
    expected[indices] = expected_data
    reflection_residual = float(
        np.max(
            np.abs(
                Statevector(probe.copy()).evolve(components["diffusion"], wires).data
                - expected
            )
        )
    )
    inverse_residual = float(
        np.max(
            np.abs(
                Statevector(probe.copy())
                .evolve(components["preparation"], wires)
                .evolve(components["preparation_inverse"], wires)
                .data
                - probe
            )
        )
    )
    write_json(
        output / "coherent-validation.json",
        {
            "oracle": oracle_residual,
            "reflection": reflection_residual,
            "A_actual_inverse": inverse_residual,
            "raw_validation": raw_validation,
            "phase_validation": phase_validation,
            "witnesses": witness_results,
        },
    )
    assert max(oracle_residual, reflection_residual, inverse_residual) <= TOLERANCE
    np.savez(
        output / "coherent-probe.npz",
        input=probe,
        oracle_expected=probe
        * np.where(np.isin(np.arange(1 << width), indices[good]), -1, 1),
        diffusion_expected=expected,
    )
    state = Statevector.from_int(0, 1 << width).evolve(components["preparation"], wires)
    p = Fraction(count.marked, count.support)
    u = v = Fraction(1)
    rows = []
    for row in ledger.rows:
        j = row.iterations
        if j:
            state = state.evolve(components["oracle"]).evolve(
                components["diffusion"], wires
            )
            u, v = (1 - 2 * p) * u + 2 * (1 - p) * v, -2 * p * u + (1 - 2 * p) * v
        expected = np.zeros(1 << width, dtype=complex)
        expected[indices[support & good]] = float(u) / math.sqrt(count.support)
        expected[indices[support & ~good]] = float(v) / math.sqrt(count.support)
        residual = float(np.max(np.abs(state.data - expected)))
        probabilities = np.abs(state.data) ** 2
        marginal = np.zeros(1024)
        # Sum over ALL workspace values using actual input mapping.
        for physical, probability in enumerate(probabilities):
            word = sum(((physical >> q) & 1) << i for i, q in enumerate(wires))
            marginal[word] += probability
        success = float(marginal[good].sum())
        leakage = float(marginal[~valid].sum())
        predicted_leakage = (
            float(Fraction(781, 1024) * v * v) if regime == "R1" else 0.0
        )
        restored = float(probabilities[indices].sum())
        norm = float(probabilities.sum())
        error = max(
            residual,
            abs(success - float(p * u * u)),
            abs(leakage - predicted_leakage),
            abs(restored - 1),
            abs(norm - 1),
            abs(success - row.analytical_success_probability),
        )
        record = {
            "iterations": j,
            "success": success,
            "unused_code_probability": leakage,
            "predicted_unused_code_probability": predicted_leakage,
            "restored_workspace_probability": restored,
            "dirty_workspace_probability": float(probabilities[dirty].sum()),
            "norm": norm,
            "analytical_success": row.analytical_success_probability,
            "rational_success": str(p * u * u),
            "signed_amplitude_residual": residual,
            "max_comparison_error": error,
            "passed": error <= TOLERANCE,
        }
        rows.append(record)
        np.savez(output / f"state-j{j}.npz", actual=state.data, expected=expected)
        write_json(output / f"row-j{j}.json", record)
    report = {
        "status": (
            "complete" if all(row["passed"] for row in rows) else "failed_comparison"
        ),
        "regime": regime,
        "width": width,
        "data_qubits": wires,
        "counts": asdict(count),
        "analytical_ledger": asdict(ledger),
        "phase_validation": phase_validation,
        "raw_validation": raw_validation,
        "witnesses": witness_results,
        "coherent_residuals": {
            "oracle": oracle_residual,
            "reflection": reflection_residual,
            "A_actual_inverse": inverse_residual,
        },
        "artifacts": artifacts,
        "rows": rows,
        "seed": SEED,
        "tolerance": TOLERANCE,
        "precision": "complex128 ideal U/CX; no rotation approximation/FT claim",
        "confidence_interval": None,
        "shots": None,
        "noise": None,
        "scope": "ideal complete-predicate best_fit C5 only; independent scientific review pending",
    }
    write_json(output / "result.json", report)
    assert report["status"] == "complete"


def supervised(command: list[str], run: Path, label: str, timeout: float) -> dict:
    """Run one child, kill its group on time/RSS excess, retain exact receipt."""
    import psutil

    env = os.environ.copy()
    env.update({key: "1" for key in THREADS})
    env.update(
        PYTHONPATH=str(ROOT / "src"),
        PYTHONDONTWRITEBYTECODE="1",
        QISKIT_PARALLEL="FALSE",
    )
    started = time.monotonic()
    sampled_peak = 0
    status = "finished"
    with (run / f"{label}.log").open("x") as log:
        proc = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        while True:
            pid, wait_status, usage = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                proc.returncode = os.waitstatus_to_exitcode(wait_status)
                break
            try:
                sampled_peak = max(
                    sampled_peak, psutil.Process(proc.pid).memory_info().rss
                )
            except psutil.NoSuchProcess:
                pass
            if (
                time.monotonic() - started > timeout
                or sampled_peak > BUDGET["declared_process_bytes"]
            ):
                status = (
                    "timeout"
                    if time.monotonic() - started > timeout
                    else "sampled_rss_exceeded"
                )
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, wait_status, usage = os.wait4(proc.pid, 0)
                proc.returncode = os.waitstatus_to_exitcode(wait_status)
                break
            time.sleep(0.05)
    receipt = {
        "command": command,
        "returncode": proc.returncode,
        "status": status,
        "seconds": time.monotonic() - started,
        "timeout_seconds": timeout,
        "sampled_direct_child_peak_rss_bytes": sampled_peak,
        "wait4_high_water_bytes": int(
            usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
        ),
        "rss_scope": BUDGET["memory_enforcement"],
        "thread_limits": {key: env[key] for key in THREADS},
        "PYTHONPATH": env["PYTHONPATH"],
        "log_sha256": digest(run / f"{label}.log"),
    }
    write_json(run / f"{label}-receipt.json", receipt)
    return receipt


def run_experiment() -> Path:
    """Create new evidence and supervise compile then two full ideal sweeps."""
    assert_source()
    run = new_dump_directory("c5-complete-best-fit", root=ROOT / "dump")
    write_json(run / "budget.json", BUDGET)
    build = NATIVE.parent / "build_provenance.json"
    write_json(
        run / "provenance.json",
        {
            "task": "c5-complete-execute-1030020413",
            "session": os.environ.get("CODEX_THREAD_ID", "not supplied"),
            "base": "e90adf3373236ef51a937480febd3cd7d669dce7",
            "HEAD": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "native": {
                "path": str(NATIVE),
                "sha256": digest(NATIVE),
                "build": json.loads(build.read_text()),
                "build_sha256": digest(build),
            },
            "python": str(PYTHON),
            "platform": platform.platform(),
            "seed": SEED,
            "seed_use": "deterministic logical statevector; seeded complex probe and transpiler; no sampling",
            "versions": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "qiskit", "tweedledum", "psutil")
            },
            "source_hashes": {
                str(path.relative_to(ROOT)): digest(path)
                for path in [
                    Path(__file__),
                    *sorted((ROOT / "src/logique").rglob("*.py")),
                ]
            },
            "dependency_gitlinks": subprocess.check_output(
                ["git", "ls-tree", "HEAD", "external/"], text=True
            ).splitlines(),
        },
    )
    started = time.monotonic()
    receipts = []
    for stage in ("compile", "R1", "R2"):
        remaining = BUDGET["cumulative_seconds"] - (time.monotonic() - started)
        if remaining <= 0:
            break
        receipts.append(
            supervised(
                [
                    str(PYTHON),
                    str(Path(__file__).resolve()),
                    "--child",
                    stage,
                    "--run",
                    str(run),
                ],
                run,
                stage,
                min(120, remaining),
            )
        )
        if receipts[-1]["returncode"] or receipts[-1]["status"] != "finished":
            break
        if (
            stage == "compile"
            and json.loads((run / "preflight.json").read_text())["status"] != "feasible"
        ):
            break
    complete = len(receipts) == 3 and all(
        r["returncode"] == 0 and r["status"] == "finished" for r in receipts
    )
    write_json(
        run / "manifest.json",
        {
            "status": "complete" if complete else "incomplete",
            "scientific_admission": "pending_independent_review",
            "receipts": receipts,
            "cumulative_seconds": time.monotonic() - started,
            "evidence_hashes": {
                str(path.relative_to(run)): digest(path)
                for path in sorted(run.rglob("*"))
                if path.is_file()
            },
            "next_action": "independent exact-source/evidence/QPY review; separately assess saved structure22 pilot; preserve historical exclusion",
        },
    )
    print(run, flush=True)
    if not complete:
        raise SystemExit(1)
    return run


def main() -> None:
    """Execute a fresh experiment or one supervisor-owned child stage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", choices=("compile", "R1", "R2"))
    parser.add_argument("--run", type=Path)
    args = parser.parse_args()
    if args.child:
        if args.run is None:
            parser.error("child requires --run")
        if args.child == "compile":
            compile_candidate(args.run)
        else:
            simulate(args.run, args.child)
    else:
        run_experiment()


if __name__ == "__main__":
    main()
