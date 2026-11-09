"""Frozen missing common-lowering batch; no model or hardware execution."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path("/Users/mar/codex-work/logique")
WORKTREE = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
NATIVE = (
    ROOT
    / "dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis"
)
NATIVE_HASH = "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
CONFIG = WORKTREE / "configs/research/comparison_common_lowering_1101052342.json"


def digest(path: Path) -> str:
    """Hash an exact file without changing historical evidence."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict | list) -> None:
    """Atomically persist one current checkpoint within the new run."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def structural_gate(problem, budget: dict) -> dict:
    """Reject wide instances before encoding or any quantum gate constructor."""
    n = len(problem.vertices) * max(1, (problem.colors - 1).bit_length())
    constraints = len(problem.edges) + (
        len(problem.vertices)
        * ((1 << max(1, (problem.colors - 1).bit_length())) - problem.colors)
    )
    accepted = (
        2 <= problem.colors <= 8
        and n <= budget["max_data_bits"]
        and len(problem.vertices) <= budget["max_vertices"]
        and len(problem.edges) <= budget["max_edges"]
        and constraints <= budget["max_constraints"]
    )
    return dict(
        accepted=accepted,
        data_bits=n,
        constraints=constraints,
        reason=None if accepted else "pre-constructor structural subset cap",
    )


def assert_imports() -> dict:
    """Ensure every measured dependency comes from this deliberately composed branch."""
    import importlib

    modules = [
        "logique",
        "logique.benchmarks.coloring_study",
        "logique.benchmarks.metrics",
        "logique.benchmarks.costs",
        "logique.benchmarks.controlled_comparison",
        "logique.synthesis.api",
        "logique.synthesis.research_profiles",
        "logique.circuits.structure",
    ]
    result = {}
    for name in modules:
        path = Path(importlib.import_module(name).__file__).resolve()
        assert path.is_relative_to(WORKTREE / "src"), (name, path)
        result[name] = dict(path=str(path), sha256=digest(path))
    return result


def child(request: Path) -> None:
    """Execute fresh logical and matched restoring/common costs on the same inputs."""
    imports = assert_imports()
    from logique.benchmarks.coloring_study import run_coloring_study
    from logique.paths import dump_directory_name

    req = json.loads(request.read_text())
    base = request.parent
    write(base / "imports.json", imports)
    for label, extra in (
        ("logical", {}),
        (
            "common",
            dict(
                common_basis=True,
                optimization_level=0,
                mcx_decomposition="clean_tree",
                mcx_workspace="fresh_zero",
            ),
        ),
    ):
        output = run_coloring_study(
            {
                **req["study"],
                **extra,
                "output": str(base / dump_directory_name(label)),
            },
            executable=NATIVE,
        )
        write(base / f"{label}-result.json", dict(path=str(output)))


def ledger(config: dict, entries: list[dict]) -> list[dict]:
    """Retain every unrun graph/profile/target/precision axis without invented costs."""
    selected = {(e["benchmark"], e["method"]): e for e in entries}
    rows = []
    for graph, method, profile, regime in itertools.product(
        config["requested_graphs"],
        config["methods"],
        config["profiles"],
        config["regimes"],
    ):
        entry = selected.get((graph, method), {})
        context = dict(
            benchmark=graph,
            method=method,
            profile=profile,
            regime=regime,
            source_validation=entry.get("source_validation", "unrecorded"),
            headline_eligible=False,
            components=["raw", "preparation", "oracle", "diffusion", "search"],
            iteration=1,
            mcx_policy="clean_tree",
            workspace="fresh_zero",
        )
        for level in ("logical", "restoring_mcx", "common_basis"):
            rows.append(
                {
                    **context,
                    "metric_level": level,
                    "seed": 7,
                    "status": (
                        entry.get("cases", {}).get(
                            regime + ":" + level,
                            entry.get("status", "unrun_bounded_subset"),
                        )
                        if profile == "none"
                        else "unrun_profile"
                    ),
                    "scientific_admission": "pending_independent_review",
                    "reason": entry.get("reason") if profile == "none" else None,
                }
            )
        for seed in config["routing_seeds"]:
            rows.append(
                {
                    **context,
                    "metric_level": "routed",
                    "target": "FakeTorino",
                    "seed": seed,
                    "status": "unrun_no_routed_cost",
                }
            )
        for precision in config["ft_precisions"]:
            rows.append(
                {
                    **context,
                    "metric_level": "static_fault_tolerant",
                    "precision": precision,
                    "status": "unrun_no_ft_cost",
                }
            )
    return rows


def native_scalar(value):
    """Represent group keys as JSON-native scalars, retaining missing identities."""
    if hasattr(value, "item"):
        value = value.item()
    return None if isinstance(value, float) and math.isnan(value) else value


def summarize(
    output: Path, entries: list[dict], source_output: Path | None = None
) -> dict:
    """Recount saved circuits and report per-metric strongest available denominators."""
    import pandas as pd
    from qiskit import qpy
    from logique.benchmarks.metrics import circuit_metrics

    source = source_output or output
    frames, identities = [], []
    for entry in entries:
        if "directory" not in entry:
            continue
        for path in sorted((source / entry["directory"]).glob("*/summary.csv")):
            manifest = json.loads((path.parent / "run.json").read_text())
            frame = pd.read_csv(path)
            complete_artifacts = set()
            for case in manifest["cases"]:
                if case["status"] != "complete":
                    continue
                for name, record in case.get("artifact_statistics", {}).items():
                    assert record["status"] == "verified"
                    complete_artifacts.add(name)
                    artifact = path.parent / name
                    assert digest(artifact) == record["sha256"]
                    with artifact.open("rb") as stream:
                        circuits = qpy.load(stream)
                    assert len(circuits) == 1
                    actual = circuit_metrics(circuits[0])
                    for key in ("qubits", "gates", "depth", "gate_types"):
                        assert actual[key] == record["metrics"][key]
                    identities.append(
                        dict(
                            path=str(artifact.relative_to(source)),
                            sha256=digest(artifact),
                            metrics=actual,
                        )
                    )
            frame = frame[frame.artifact.isin(complete_artifacts)].copy()
            frame["artifact"] = frame.artifact.map(
                lambda n: str(path.parent.relative_to(source) / n)
            )
            # These are fresh finite/exhaustive source checks plus reviewed lowering,
            # not the unrelated wide CEC corpus or an independent new admission.
            frame["scientific_admission"] = "pending_independent_review"
            frame["headline_eligible"] = False
            frame["equivalence_scope"] = frame.validation.map(
                lambda value: (
                    "sample_qualified"
                    if value == "sampled"
                    else "full_input_source_check"
                )
            )
            frames.append(frame)
    write(output / "artifact-recount.json", identities)
    if not frames:
        return dict(rows=0)
    frame = pd.concat(frames, ignore_index=True)
    frame.to_csv(output / "summary.csv", index=False)
    details = []
    keys = ["benchmark", "regime", "component", "metric_level"] + [
        key
        for key in (
            "input_sha256",
            "iteration",
            "seed",
            "optimization_profile",
            "mcx_method",
            "basis_identity",
            "target",
            "precision",
            "representation",
            "workspace_policy",
            "optimization_level",
        )
        if key in frame.columns
    ]
    for context, group in frame[frame.component != "raw"].groupby(keys, dropna=False):
        baseline = group[group.method.str.startswith("sb_")]
        if baseline.empty:
            continue
        for _, candidate in group[~group.method.str.startswith("sb_")].iterrows():
            for metric in ("qubits", "gates", "depth"):
                best = baseline.loc[baseline[metric].idxmin()]
                ratio = float(candidate[metric]) / float(best[metric])
                details.append(
                    dict(
                        (
                            (key, native_scalar(value))
                            for key, value in zip(keys, context)
                        ),
                        method=candidate["method"],
                        metric=metric,
                        source_validation=candidate["validation"],
                        equivalence_scope=candidate["equivalence_scope"],
                        scientific_admission="pending_independent_review",
                        headline_eligible=False,
                        cost=int(candidate[metric]),
                        baseline=best["method"],
                        baseline_cost=int(best[metric]),
                        available_baselines=sorted(baseline.method.tolist()),
                        ratio=ratio,
                        outcome="win" if ratio < 1 else "loss" if ratio > 1 else "tie",
                    )
                )
    write(output / "strongest-details.json", details)
    return dict(
        rows=len(frame),
        artifacts=len(identities),
        details=len(details),
        outcomes={
            v: sum(d["outcome"] == v for d in details) for v in ("win", "tie", "loss")
        },
        scope="descriptive new observations; independent source/evidence review pending",
    )


def load_previous(config: dict) -> list[dict]:
    """Bind prior completed evidence without editing or recounting historical QPY."""
    result = []
    for record in config.get("previous_checkpoints", []):
        path = WORKTREE / record["path"]
        if digest(path) != record["sha256"]:
            raise ValueError("Previous checkpoint identity changed")
        prior = json.loads(path.read_text())
        result.extend(prior["entries"])
    return result


def reject_completed_requests(config: dict, previous: list[dict]) -> None:
    """Prevent a follow-up config from rerunning any complete earlier group."""
    completed = {
        (entry["benchmark"], entry["method"])
        for entry in previous
        if entry.get("cases") and set(entry["cases"].values()) == {"complete"}
    }
    requested = set(itertools.product(config["graphs"], config["methods"]))
    if completed & requested:
        raise ValueError("Frozen requests overlap completed matched groups")


def verified_witnesses(problem) -> dict:
    """Include a verified proper coloring and independent invalid boundary cases."""
    from logique.benchmarks.controlled_comparison import witnesses

    report = witnesses(problem)
    if report["positive_status"] != "verified":
        raise ValueError("No independently verified positive witness")
    return {
        **report,
        "assignments": list(
            dict.fromkeys(
                report[key]
                for key in ("positive", "edge_violation", "invalid_code", "boundary")
                if report[key] is not None
            )
        ),
    }


def run(config_path: Path = CONFIG) -> Path:
    """Freeze resource/input identities first, then execute one bounded child at a time."""
    from logique.paths import new_dump_directory
    from logique.coloring import ColoringProblem, read_dimacs
    from logique.benchmarks.controlled_comparison import supervise, BUDGET

    config = json.loads(config_path.read_text())
    assert digest(NATIVE) == NATIVE_HASH
    assert Path(sys.executable).absolute() == PYTHON
    imports = assert_imports()
    output = new_dump_directory("comparison-common-lowering", root=WORKTREE / "dump")
    write(output / "frozen-config.json", config)
    BUDGET["group_rss_bytes"] = config["budget"]["process_bytes"]
    entries = []
    manifest = dict(
        task=config["task"],
        budget=config["budget"],
        allocation=config["allocation"],
        source=imports,
        native_sha256=digest(NATIVE),
        config_sha256=digest(config_path),
        entries=entries,
        scientific_admission="pending independent review",
        inherited_commits=[
            "253e85089a28552cc6c0138ae8333a15d021a16b",
            "cf678f72a0a293a7c1b97956565c8f50176fc313",
        ],
    )
    previous = load_previous(config)
    reject_completed_requests(config, previous)
    manifest["previous_checkpoints"] = config.get("previous_checkpoints", [])
    # Classical preflight across all nine graphs precedes every quantum constructor.
    inputs = {}
    for graph in config["requested_graphs"]:
        source = WORKTREE / f"datasets/graphs/benchmarks/{graph}.col"
        original = read_dimacs(source)
        problem = ColoringProblem(original.vertices, original.edges, original.colors)
        inputs[graph] = dict(
            path=str(source),
            sha256=digest(source),
            removed_precolors=dict(original.precolored),
            gate=structural_gate(problem, config["budget"]),
            witnesses=(
                verified_witnesses(problem)
                if graph in config["graphs"] and config.get("validation") == "sampled"
                else None
            ),
        )
    manifest["inputs"] = inputs
    write(output / "checkpoint.json", manifest)
    started = time.monotonic()
    for graph, method in itertools.product(config["graphs"], config["methods"]):
        entry = dict(
            benchmark=graph,
            method=method,
            status="not_run",
            source_validation=config.get("validation", "exhaustive"),
            headline_eligible=False,
        )
        entries.append(entry)
        if not inputs[graph]["gate"]["accepted"]:
            entry.update(
                status="excluded_structural", reason=inputs[graph]["gate"]["reason"]
            )
            continue
        remaining = (
            config["budget"]["cumulative_seconds"] - (time.monotonic() - started) - 60
        )
        if remaining <= 0:
            entry.update(status="unrun_budget", reason="reserve recount time")
            continue
        directory = output / f"case-{len(entries):03d}"
        directory.mkdir()
        entry["directory"] = directory.name
        study = dict(
            inputs=[inputs[graph]["path"]],
            methods=[method],
            regimes=config["regimes"],
            iterations=[1],
            seeds=[7],
            optimization_profile="none",
            remove_precolors=True,
            validation=config.get("validation", "exhaustive"),
            **(
                {
                    "verification_assignments": {
                        inputs[graph]["path"]: inputs[graph]["witnesses"]["assignments"]
                    }
                }
                if inputs[graph]["witnesses"] is not None
                else {}
            ),
            samples=32,
            **{
                k: v
                for k, v in config["budget"].items()
                if k.startswith("max_component_")
            },
        )
        write(directory / "request.json", dict(study=study))
        entry.update(
            supervise(
                [
                    str(PYTHON),
                    str(Path(__file__).resolve()),
                    "--child",
                    str(directory / "request.json"),
                ],
                directory,
                min(remaining, config["budget"]["child_seconds"]),
            )
        )
        entry["cases"] = {}
        for run_file in sorted(directory.glob("*/run.json")):
            saved = json.loads(run_file.read_text())
            primary = (
                "restoring_mcx" if "mcx_decomposition" in saved["config"] else "logical"
            )
            for case in saved["cases"]:
                for level in (
                    [primary, "common_basis"]
                    if primary == "restoring_mcx"
                    else [primary]
                ):
                    entry["cases"][case["regime"] + ":" + level] = case["status"]
        write(output / "checkpoint.json", manifest)
    write(output / "requested-open-ledger.json", ledger(config, previous + entries))
    manifest["execution_seconds"] = time.monotonic() - started
    # Recount runs in its own bounded ordinary child, preserving failures/partial data.
    directory = output / "recount"
    directory.mkdir()
    manifest["recount"] = supervise(
        [str(PYTHON), str(Path(__file__).resolve()), "--recount", str(output)],
        directory,
        min(
            60,
            max(
                0.001,
                config["budget"]["cumulative_seconds"] - manifest["execution_seconds"],
            ),
        ),
    )
    manifest["total_seconds"] = time.monotonic() - started
    manifest["next_action"] = (
        "Exact independent review of new harness and evidence; extend only missing axes after admission. No repeat of 44 completed wide groups."
    )
    write(output / "checkpoint.json", manifest)
    return output


if __name__ == "__main__":
    os.environ["PYTHONPATH"] = str(WORKTREE / "src")
    for variable in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "RAYON_NUM_THREADS",
        "CMAKE_BUILD_PARALLEL_LEVEL",
        "QISKIT_NUM_PROCS",
    ):
        os.environ[variable] = "1"
    os.environ["QISKIT_PARALLEL"] = "FALSE"
    os.environ["LOGIQUE_NATIVE_EXECUTABLE"] = str(NATIVE)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--child", type=Path)
    parser.add_argument("--recount", type=Path)
    parser.add_argument("--recount-source", type=Path)
    args = parser.parse_args()
    if args.child:
        child(args.child)
    elif args.recount:
        assert_imports()
        source = args.recount_source or args.recount
        entries = json.loads((source / "checkpoint.json").read_text())["entries"]
        write(
            args.recount / "recount-result.json",
            summarize(args.recount, entries, source),
        )
    else:
        print(run(args.config))
