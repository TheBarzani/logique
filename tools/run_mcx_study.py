"""Execute one serial, externally supervised MCX study shard.

Use the existing research Python with an explicit candidate PYTHONPATH. Each
invocation creates fresh evidence. The dispatcher/supervisor owns process time
and cumulative budgets; this tool never launches a model or parallel worker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import time


def main() -> int:
    """Write bounded isolated controls or a tiny graph-policy shard."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("isolated", "whole"))
    parser.add_argument("--policy", required=True)
    parser.add_argument(
        "--fixture",
        choices=("edge3", "edge5", "isolated5", "triangle2"),
        default="edge3",
    )
    parser.add_argument("--root", type=Path, default=Path("dump"))
    args = parser.parse_args()
    from logique.benchmarks import mcx_study as s
    from logique.paths import new_dump_directory

    candidate = Path(__file__).resolve().parents[1]
    assert (
        Path(s.__file__).resolve() == candidate / "src/logique/benchmarks/mcx_study.py"
    )
    assert sys.executable == "/Users/mar/codex-work/logique/.venv/bin/python"
    if args.policy not in s.costs.MCX_DECOMPOSITIONS:
        parser.error("unknown MCX policy")
    # Freeze the plan before importing NumPy or allocating any numerical array.
    run = new_dump_directory(f"mcx-{args.kind}-{args.policy}", root=args.root)
    plan = {
        "child_seconds": 120,
        "cumulative_seconds": 900,
        "declared_process_bytes": 6 * 1024**3,
        "monitoring": "external supervisor terminal RSS; no hard aggregate cap",
        "statevector_qubits": 18,
        "dense_operator_qubits": 5,
        "max_statevector_bytes_each": 16 * (1 << 18),
        "max_simultaneous_vector_estimate": 8,
        "gray_operation_cap": s.GRAY_OPERATION_CAP,
        "estimates": [s.construction_estimate(args.policy, n) for n in range(3, 21)],
        "task": "mcx-whole-circuit-1030020413",
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=candidate, text=True
        ).strip(),
        "session": os.environ.get("CODEX_THREAD_ID", "not exposed"),
        "seed": 7,
        "candidate": str(candidate),
        "python": sys.executable,
        "source_hashes": {
            str(p.relative_to(candidate)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [
                candidate / "src/logique/benchmarks/mcx_study.py",
                candidate / "src/logique/benchmarks/costs.py",
                candidate / "src/logique/benchmarks/coloring_study.py",
                Path(__file__).resolve(),
            ]
        },
    }
    binary = Path(os.environ["LOGIQUE_NATIVE_EXECUTABLE"])
    plan["native"] = {
        "path": str(binary),
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    }
    assert (
        plan["native"]["sha256"]
        == "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
    )
    (run / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    import numpy as np
    import qiskit
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Statevector
    from logique.coloring import ColoringProblem
    from logique.benchmarks.coloring_study import _qpy_semantic_signature

    def save_circuit(path, circuit):
        with path.open("xb") as handle:
            qpy.dump(circuit, handle)
        with path.open("rb") as handle:
            loaded = qpy.load(handle)[0]
        assert _qpy_semantic_signature(loaded) == _qpy_semantic_signature(circuit)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def coherent(case, problem, regime):
        data = case.metadata["data_qubits"]
        n = len(data)
        oracle, search = case.circuits["oracle"], case.circuits["search"]
        if max(oracle.num_qubits, search.num_qubits) > 18:
            return {
                "status": "excluded_full_statevector",
                "reason": "physical width >18; source service validation plus small template tests only",
            }
        assert max(oracle.num_qubits, search.num_qubits) <= 18

        def predicate(x):
            c = (problem.colors - 1).bit_length()
            values = {
                v: (x >> (i * c)) & ((1 << c) - 1)
                for i, v in enumerate(problem.vertices)
            }
            return all(values[u] != values[v] for u, v in problem.edges) and (
                regime == "R3" or all(v < problem.colors for v in values.values())
            )

        def embed(v, width):
            assert width <= 18
            physical = np.zeros(1 << width, complex)
            for x, value in enumerate(v):
                physical[sum(((x >> b) & 1) << w for b, w in enumerate(data))] = value
            return physical

        uniform = np.full(1 << n, 1 / math.sqrt(1 << n), complex)
        expected = uniform.copy()
        mask = np.array([predicate(x) for x in range(1 << n)])
        expected[mask] *= -1
        actual = Statevector(embed(uniform, oracle.num_qubits)).evolve(oracle).data
        err = float(np.max(abs(actual - embed(expected, oracle.num_qubits))))
        assert err < 3e-10, err
        # Independent uniform valid-code preparation and amplification recurrence.
        c = (problem.colors - 1).bit_length()
        support = [
            x
            for x in range(1 << n)
            if regime == "R1"
            or all(
                ((x >> (i * c)) & ((1 << c) - 1)) < problem.colors
                for i in range(len(problem.vertices))
            )
        ]
        a = np.zeros(1 << n, complex)
        a[support] = 1 / math.sqrt(len(support))
        expected = a.copy()
        for _ in range(case.metadata["iterations"]):
            expected[mask] *= -1
            expected = 2 * a * np.vdot(a, expected) - expected
        initial = np.zeros(1 << search.num_qubits, complex)
        initial[0] = 1
        actual = Statevector(initial).evolve(search).data
        search_err = float(np.max(abs(actual - embed(expected, search.num_qubits))))
        assert search_err < 3e-10, search_err
        return {
            "status": "passed",
            "oracle_max_error": err,
            "search_max_error": search_err,
            "scope": "uniform superposition over ALL binary oracle inputs and independent full search recurrence; scratch restoration included; no phase alignment",
            "statevector_width": max(oracle.num_qubits, search.num_qubits),
        }

    import math

    rows = []
    start = time.monotonic()
    if args.kind == "isolated":
        requests = [(str(n), n) for n in range(3, 21)]
    else:
        requests = [
            (f"{method}-{regime}", (method, regime))
            for method in (
                "xag",
                "aig_bennett",
                "xag_bennett",
                "klut_bennett",
                "best_fit",
                "sb_original",
                "sb_simple",
                "sb_minimal",
                "sb_balanced",
                "structure_sequential",
                "structure_parallel",
            )
            for regime in ("R1", "R2", "R3")
        ]
    fixtures = {
        "edge3": ColoringProblem((-7, 20), ((-7, 20),), 3),
        "edge5": ColoringProblem((-7, 20), ((-7, 20),), 5),
        "isolated5": ColoringProblem((42,), (), 5),
        "triangle2": ColoringProblem((2, 8, 90), ((2, 8), (8, 90), (2, 90)), 2),
    }
    for key, request in requests:
        row = {
            "key": key,
            "policy": args.policy,
            "kind": args.kind,
            "fixture": args.fixture if args.kind == "whole" else None,
        }
        folder = run / key
        folder.mkdir()
        child_start = time.monotonic()
        try:
            if args.kind == "isolated":
                estimate = s.construction_estimate(args.policy, request)
                row["estimate"] = estimate
                if estimate["status"] == "excluded":
                    raise s.StudyExclusion(
                        "Gray preallocation cap; no constructor invoked"
                    )
                source = QuantumCircuit(2 * request - 1)
                source.mcx(list(range(request)), request)
                forward, info = s.lower_block(source, args.policy, mirrored=True)
                paired = forward.copy()
                paired.z(request)
                paired.compose(s._inverse(forward), inplace=True)
                circuits = {"forward": forward, "paired_phase": paired}
                row["workspace"] = info
                row["semantic_scope"] = (
                    "templates tested at 3/4 controls; above four representation/cost only, no whole-state proof"
                )
            else:
                method, regime = request
                problem = fixtures[args.fixture]
                row["input"] = {
                    "vertices": problem.vertices,
                    "edges": problem.edges,
                    "colors": problem.colors,
                }
                row["input_sha256"] = hashlib.sha256(
                    json.dumps(row["input"], sort_keys=True).encode()
                ).hexdigest()
                case = s.assemble_mcx_case(
                    problem, method, regime, args.policy, executable=str(binary)
                )
                row["metadata"] = case.metadata
                row["coherent_validation"] = coherent(case, problem, regime)
                circuits = case.circuits
            row["components"] = {}
            row["artifacts"] = {}
            for name, circuit in circuits.items():
                # Retain primary artifacts even if later cost translation fails.
                primary = folder / f"{name}-primary.qpy"
                row["artifacts"][primary.name] = save_circuit(primary, circuit)
                metrics, representations = s.component_costs(circuit)
                row["components"][name] = metrics
                for level, q in representations.items():
                    path = folder / f"{name}-{level}.qpy"
                    row["artifacts"][path.name] = save_circuit(path, q)
            row["status"] = "complete"
        except s.StudyExclusion as error:
            row.update(status="excluded", reason=str(error))
        except Exception as error:
            import traceback

            (folder / "failure.txt").write_text(traceback.format_exc())
            row.update(status="failed", reason=f"{type(error).__name__}: {error}")
        row["seconds"] = time.monotonic() - child_start
        rows.append(row)
        (folder / "result.json").write_text(json.dumps(row, indent=2) + "\n")
    (run / "dutta-analytical.json").write_text(
        json.dumps(s.analytical_dutta_rows(), indent=2) + "\n"
    )
    summary = {
        "rows": rows,
        "seconds": time.monotonic() - start,
        "versions": {"qiskit": qiskit.__version__, "numpy": np.__version__},
        "scientific_admission": "pending independent review",
        "losses": "no superiority aggregation; costs and excluded/failed rows retained",
    }
    (run / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {
                "run": str(run),
                "counts": {
                    status: sum(r["status"] == status for r in rows)
                    for status in ("complete", "excluded", "failed")
                },
                "seconds": summary["seconds"],
            }
        )
    )
    return int(any(r["status"] == "failed" for r in rows))


if __name__ == "__main__":
    raise SystemExit(main())
