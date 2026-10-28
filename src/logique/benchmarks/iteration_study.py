"""Executed ideal coloring iterations, with bounded serial child processes.

This is an ideal logical statevector study, not noise, routing or FT evidence.
The structure oracle's clean-workspace contract and actual emitted preparation
inverse are retained. Saved, resolved QPY components are the simulated objects.
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
import platform
from pathlib import Path
import signal
import subprocess
import sys
import time

from logique.benchmarks.ideal_iterations import (
    count_coloring_support,
    ideal_iteration_ledger,
    random_sampling_reference,
)
from logique.coloring import ColoringProblem, encode_coloring
from logique.paths import new_dump_directory


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _integer(value, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def validate_config(config: dict) -> None:
    """Reject unsupported controls and budgets before launching numerical work."""
    if set(config) != {
        "cases",
        "regimes",
        "max_qubits",
        "timeout_seconds",
        "budget_seconds",
        "tolerance",
        "seed",
    }:
        raise ValueError("Unknown or missing iteration-study config fields")
    _integer(config["max_qubits"], "max_qubits", 1, 18)
    _integer(config["timeout_seconds"], "timeout_seconds", 1, 180)
    _integer(config["budget_seconds"], "budget_seconds", 1, 900)
    _integer(config["seed"], "seed", 0, 2**32 - 1)
    tol = config["tolerance"]
    if type(tol) not in (int, float) or not math.isfinite(tol) or not 0 < tol <= 1e-8:
        raise ValueError("tolerance must be finite in (0, 1e-8]")
    if not config["regimes"] or len(set(config["regimes"])) != len(config["regimes"]):
        raise ValueError("regimes must be nonempty and unique")
    if any(r not in ("R1", "R2", "R3") for r in config["regimes"]):
        raise ValueError("Unknown regime")
    if not config["cases"]:
        raise ValueError("At least one case is required")
    names = []
    for case in config["cases"]:
        if set(case) != {"name", "vertices", "edges", "colors"}:
            raise ValueError("Each case requires name, vertices, edges, colors")
        name = case["name"]
        if (
            not isinstance(name, str)
            or not name
            or any(
                c
                not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                for c in name
            )
        ):
            raise ValueError("Case name must be a safe filename")
        names.append(name)
        problem = _problem(case)
        # Known exact counts only; this rejects oversized enumeration first.
        count_coloring_support(problem, regime="R1")
    if len(set(names)) != len(names):
        raise ValueError("Case names must be unique")


def _problem(case: dict) -> ColoringProblem:
    return ColoringProblem(
        tuple(case["vertices"]), tuple(tuple(e) for e in case["edges"]), case["colors"]
    )


def _word_classes(problem: ColoringProblem) -> tuple[list[bool], list[bool]]:
    """Decode packed words directly, independently of circuit/encoding evaluators."""
    c = max(1, (problem.colors - 1).bit_length())
    positions = {v: i for i, v in enumerate(problem.vertices)}
    good, valid = [], []
    for word in range(1 << (c * len(positions))):
        colors = [(word >> (c * i)) & ((1 << c) - 1) for i in range(len(positions))]
        codes = all(x < problem.colors for x in colors)
        valid.append(codes)
        good.append(
            codes
            and all(
                colors[positions[u]] != colors[positions[v]] for u, v in problem.edges
            )
        )
    return good, valid


def _check_phase(oracle, problem: ColoringProblem, regime: str) -> dict:
    """Exhaust every binary input using exact scalar X/MCX/Z semantics.

    No per-column phase alignment: the scalar must be exactly (-1)^predicate.
    This supplements the admitted compositional proof, without quantum arrays.
    """
    c = max(1, (problem.colors - 1).bit_length())
    n = c * len(problem.vertices)
    positions = {v: i for i, v in enumerate(problem.vertices)}
    operations = []
    for item in oracle.data:
        op = item.operation
        wires = [oracle.find_bit(q).index for q in item.qubits]
        if op.name not in ("x", "cx", "ccx", "mcx", "z", "barrier"):
            raise ValueError(f"Unsupported scalar oracle gate {op.name}")
        if (
            getattr(op, "ctrl_state", (1 << (len(wires) - 1)) - 1)
            != (1 << (len(wires) - 1)) - 1
        ):
            raise ValueError("Scalar validation requires closed controls")
        operations.append((op.name, wires))
    if float(oracle.global_phase) != 0:
        raise AssertionError("Structure oracle must retain zero scalar global phase")
    for word in range(1 << n):
        state, phase = word, 1
        for name, wires in operations:
            if name == "barrier":
                continue
            if name == "z":
                if (state >> wires[0]) & 1:
                    phase = -phase
            elif all((state >> q) & 1 for q in wires[:-1]):
                state ^= 1 << wires[-1]
        colors = [(word >> (i * c)) & ((1 << c) - 1) for i in range(len(positions))]
        expected = all(
            colors[positions[u]] != colors[positions[v]] for u, v in problem.edges
        )
        if regime != "R3":
            expected = expected and all(x < problem.colors for x in colors)
        if state != word or phase != (-1 if expected else 1):
            raise AssertionError(f"Absolute oracle phase/restoration failure at {word}")
    return {
        "status": "passed",
        "coverage": "exhaustive_all_binary_inputs",
        "columns": 1 << n,
        "phase_alignment": "none; absolute +/-1",
        "workspace": "every non-data wire restored to zero",
    }


def simulate_case(case: dict, regime: str, config: dict, output: Path) -> dict:
    """Execute j=0 through first peak+1, or retain a preallocation exclusion.

    Data occupies the low contiguous wires; all non-data wires start zero.
    Signed full-vector residuals compare to an independent exact rational
    good/bad recurrence; no fitted scalar or relative phase is allowed.
    """
    validate_config(config)
    from qiskit import QuantumCircuit, qpy, transpile
    from qiskit.quantum_info import Statevector
    import numpy as np
    from logique.circuits.grover import coloring_preparation, _reflection
    from logique.circuits.structure import structure_oracle
    from logique.benchmarks.coloring_study import (
        _resolved_qpy_circuit,
        _qpy_semantic_signature,
    )

    output.mkdir(parents=True, exist_ok=False)
    problem = _problem(case)
    count = count_coloring_support(problem, regime=regime)
    all_binary_count = count_coloring_support(problem, regime="R1")
    ledger = ideal_iteration_ledger(
        count.marked, count.support, max_rows=130, max_iterations=129
    )
    result = {
        "case": case,
        "regime": regime,
        "counts": asdict(count),
        "binary_witnesses": asdict(all_binary_count),
        "analytical_ledger": asdict(ledger),
        "rows": [],
        "probability_kind": "executed_ideal_logical_statevector",
        "confidence_interval": None,
        "confidence_interval_reason": "exact statevector probabilities; no shots",
        "seed": config["seed"],
        "tolerance": config["tolerance"],
    }
    oracle_result = structure_oracle(
        problem, domain_policy="domain_free" if regime == "R3" else "complete"
    )
    width = oracle_result.circuit.num_qubits
    result["construction"] = {
        "backend": oracle_result.metadata,
        "method": "structure_sequential",
        "oracle": "compute_conjunction_Z_conjunction_actual_compute_inverse",
        "preparation": "Hadamard" if regime == "R1" else "coloring_preparation",
        "diffusion": "A(2|0><0|-I)A_dagger; actual emitted inverse",
        "level": "ideal unrouted U/CX; exact logical MCX synthesis; no FT model",
        "workspace_policy": "all flags/comparator scratch/output initially zero",
        "width": width,
        "data_qubits": list(range(count.data_bits)),
        "wire_order": "sorted integer labels; vertex words LSB first; data low wires",
    }
    if width > config["max_qubits"]:
        result.update(
            status="infeasible",
            reason=f"{width} > cap {config['max_qubits']}",
            next_action="Use a separately admitted lower-workspace oracle or wider resource budget; retain this full regime sweep",
        )
        _write(output / "result.json", result)
        return result
    # Guard above precedes all exponential quantum arrays and preparation arrays.
    oracle = oracle_result.phase_oracle()
    result["validation"] = _check_phase(oracle, problem, regime)
    n = count.data_bits
    preparation = QuantumCircuit(n)
    if regime == "R1":
        if n:
            preparation.h(range(n))
    else:
        preparation = coloring_preparation(encode_coloring(problem))
    if n:
        diffusion = _reflection(preparation)
        diffusion.global_phase += math.pi
    else:
        # The zero-dimensional data register has D=2|empty><empty|-I=+1.
        diffusion = QuantumCircuit(0)
    components = {}
    artifacts = {}
    for name, circuit in (
        ("preparation", preparation),
        ("oracle", oracle),
        ("diffusion", diffusion),
    ):
        resolved, representation = _resolved_qpy_circuit(circuit)
        # Statevector.evolve may form a dense matrix for a wide gate. Flatten
        # to one/two-qubit U/CX instructions BEFORE any statevector execution.
        resolved = transpile(
            resolved,
            basis_gates=["u", "cx"],
            optimization_level=0,
            seed_transpiler=config["seed"],
        )
        if any(item.operation.num_qubits > 2 for item in resolved.data):
            raise AssertionError("Simulation requires at most two-qubit gates")
        path = output / f"{name}.qpy"
        with path.open("wb") as stream:
            qpy.dump(resolved, stream)
        with path.open("rb") as stream:
            loaded = qpy.load(stream)[0]
        if _qpy_semantic_signature(loaded) != _qpy_semantic_signature(resolved):
            raise AssertionError("QPY changed absolute scalar/gate semantics")
        components[name] = loaded
        artifacts[name] = {
            "file": path.name,
            "sha256": _digest(path),
            "resolution": representation,
            "signature": _qpy_semantic_signature(loaded),
        }
    result["artifacts"] = artifacts
    result["replay"] = (
        "zero full register; preparation on data; row j after j repetitions of oracle then diffusion on data; components loaded from QPY"
    )
    good, valid = _word_classes(problem)
    good = np.asarray(good, dtype=bool)
    valid = np.asarray(valid, dtype=bool)
    support_mask = np.ones(1 << n, dtype=bool) if regime == "R1" else valid
    if int(np.sum(good)) != count.marked or int(np.sum(support_mask)) != count.support:
        raise AssertionError("Independent packed-word counts disagree")
    state = Statevector.from_int(0, 1 << width)
    if n:
        state = state.evolve(components["preparation"], list(range(n)))
    p = Fraction(count.marked, count.support)
    u = v = Fraction(1)
    passed = True
    for row in ledger.rows:
        if row.iterations:
            state = state.evolve(components["oracle"])
            if n:
                state = state.evolve(components["diffusion"], list(range(n)))
            u, v = (1 - 2 * p) * u + 2 * (1 - p) * v, -2 * p * u + (1 - 2 * p) * v
        probabilities = np.abs(state.data.reshape((-1, 1 << n))) ** 2
        marginal = probabilities.sum(axis=0)
        expected = np.zeros(1 << n, dtype=complex)
        expected[support_mask & good] = float(u) / math.sqrt(count.support)
        expected[support_mask & ~good] = float(v) / math.sqrt(count.support)
        # Compare absolute amplitudes on clean workspace and all dirty amplitudes.
        clean = state.data[: 1 << n]
        residual = float(np.max(np.abs(clean - expected)))
        if width > n:
            residual = max(residual, float(np.max(np.abs(state.data[1 << n :]))))
        success = float(marginal[good].sum())
        leakage = float(marginal[~valid].sum())
        norm = float(probabilities.sum())
        restored = float(probabilities[0].sum())
        prediction = float(p * u * u)
        error = abs(success - prediction)
        ok = (
            max(
                residual,
                error,
                abs(norm - 1),
                abs(restored - 1),
                abs(prediction - row.analytical_success_probability),
                leakage if regime != "R1" else 0,
            )
            <= config["tolerance"]
        )
        passed = passed and ok
        result["rows"].append(
            {
                "iterations": row.iterations,
                "simulated_valid_solution_probability": success,
                "simulated_unused_code_leakage": leakage,
                "simulated_total_norm": norm,
                "simulated_restored_workspace_probability": restored,
                "independent_rational_prediction": prediction,
                "analytical_ledger_prediction": row.analytical_success_probability,
                "absolute_probability_error": error,
                "signed_amplitude_max_error_no_alignment": residual,
                "comparison_passed": ok,
                "random_sampling": asdict(
                    random_sampling_reference(
                        count.marked,
                        count.support,
                        trials=row.iterations + 1,
                        trial_cost=1,
                        cost_basis="one independent uniform support draw plus one classical predicate evaluation; j+1 trials; not quantum gate cost",
                    )
                ),
            }
        )
    result["status"] = "complete" if passed else "failed_comparison"
    _write(output / "result.json", result)
    return result


def run_study(config: dict, *, root: Path = Path("dump")) -> Path:
    """Run one child at a time with wait4 RSS, timeout and cumulative wall budget."""
    validate_config(config)
    output = new_dump_directory("executed-ideal-iterations", root=root)
    _write(output / "config.json", config)
    source = Path(__file__).resolve().parents[2]
    env = dict(
        os.environ,
        PYTHONPATH=str(source),
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
    )
    manifest = {
        "status": "running",
        "config": config,
        "cases": [],
        "python": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "source": str(source),
        "versions": {
            name: importlib.metadata.version(name) for name in ("numpy", "qiskit")
        },
        "seed_use": "deterministic exact statevector; fixed transpiler seed, no sampling",
        "thread_limits": {
            k: env[k]
            for k in env
            if k.endswith("NUM_THREADS") or k == "VECLIB_MAXIMUM_THREADS"
        },
        "protected_hashes": {},
        "scope": "ideal only; no noise/routing/FT/RUS claims",
    }
    repo = source.parent
    manifest["git_head"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()
    manifest["dependency_gitlinks"] = subprocess.check_output(
        ["git", "ls-tree", "HEAD", "external/"], cwd=repo, text=True
    ).splitlines()
    for relative in (
        "src/logique/benchmarks/iteration_study.py",
        "src/logique/benchmarks/ideal_iterations.py",
        "src/logique/circuits/structure.py",
        "src/logique/circuits/grover.py",
        "src/logique/benchmarks/coloring_study.py",
        "src/logique/coloring/model.py",
        "src/logique/coloring/encoding.py",
        "tests/test_iteration_study.py",
        "configs/iteration_pilot.json",
    ):
        path = repo / relative
        if path.is_file():
            manifest["protected_hashes"][str(path)] = _digest(path)
    native = env.get("LOGIQUE_NATIVE_EXECUTABLE")
    manifest["native"] = {
        "invoked": False,
        "path": native,
        "sha256": _digest(Path(native)) if native else None,
    }
    started = time.monotonic()
    for case in config["cases"]:
        for regime in config["regimes"]:
            remaining = config["budget_seconds"] - (time.monotonic() - started)
            name = f"{case['name']}_{regime}"
            record = {"name": name}
            manifest["cases"].append(record)
            if remaining <= 0:
                record.update(
                    status="budget_excluded",
                    next_action="Replay this case in a new budgeted run",
                )
                continue
            request = {
                "case": case,
                "regime": regime,
                "config": config,
                "output": str(output / name),
            }
            request_path = output / f"{name}_request.json"
            _write(request_path, request)
            command = [
                sys.executable,
                "-m",
                "logique.benchmarks.iteration_study",
                "--child",
                str(request_path),
            ]
            limit = min(config["timeout_seconds"], remaining)
            before = time.monotonic()
            with (output / f"{name}.log").open("w") as stream:
                child = subprocess.Popen(
                    command,
                    env=env,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                timed_out = False
                while True:
                    pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                    if pid:
                        break
                    if time.monotonic() - before >= limit:
                        timed_out = True
                        os.killpg(child.pid, signal.SIGKILL)
                        _, status, usage = os.wait4(child.pid, 0)
                        break
                    time.sleep(0.05)
                child.returncode = os.waitstatus_to_exitcode(status)
            result_path = output / name / "result.json"
            record.update(
                command=command,
                seconds=time.monotonic() - before,
                timeout_seconds=limit,
                returncode=child.returncode,
                peak_rss_bytes=int(
                    usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
                ),
            )
            if timed_out:
                record.update(
                    status="timeout",
                    next_action="Inspect retained log/construction and rerun in a new bounded study",
                )
            elif child.returncode:
                record.update(
                    status="failed", next_action="Diagnose retained child traceback"
                )
            else:
                record["status"] = json.loads(result_path.read_text())["status"]
                record["result"] = str(result_path.relative_to(output))
            _write(output / "manifest.json", manifest)
    manifest["seconds"] = time.monotonic() - started
    manifest["status"] = "finished_schedule"
    manifest["preservation"] = all(
        _digest(Path(p)) == h for p, h in manifest["protected_hashes"].items()
    )
    manifest["evidence_hashes"] = {
        str(p.relative_to(output)): _digest(p)
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }
    _write(output / "manifest.json", manifest)
    return output


def main() -> None:
    """Run a JSON-configured serial pilot, or one supervised child case."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--child", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        request = json.loads(args.child.read_text())
        simulate_case(
            request["case"],
            request["regime"],
            request["config"],
            Path(request["output"]),
        )
    elif args.config:
        print(run_study(json.loads(args.config.read_text())))
    else:
        parser.error("--config is required")


if __name__ == "__main__":
    main()
