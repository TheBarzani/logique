"""Boundaries for the unique missing common-lowering batch."""

import importlib.util
import json
from pathlib import Path

from logique.coloring import ColoringProblem

SOURCE = (
    Path(__file__).parents[1] / "tools/run_comparison_common_lowering_1101052342.py"
)
spec = importlib.util.spec_from_file_location("matched_lowering_batch", SOURCE)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
CONFIG = json.loads(batch.CONFIG.read_text())


def test_structural_preflight_excludes_wide_before_encoding():
    """Only elementary graph fields are needed, with no Qiskit constructors."""
    tiny = ColoringProblem((1, 2, 3), ((1, 2), (2, 3), (1, 3)), 3)
    assert batch.structural_gate(tiny, CONFIG["budget"])["accepted"]
    wide = ColoringProblem(tuple(range(74)), (), 4)
    result = batch.structural_gate(wide, CONFIG["budget"])
    assert not result["accepted"]
    assert result["data_bits"] == 148


def test_ledger_keeps_failed_regime_and_all_requested_axes():
    entries = [
        dict(
            benchmark="K3",
            method="xag",
            status="timeout",
            cases={"R1:logical": "complete", "R2:common_basis": "failed"},
        )
    ]
    rows = batch.ledger(CONFIG, entries)
    assert len(rows) == 9 * 10 * 5 * 3 * (3 + 5 + 3)
    selected = [
        r
        for r in rows
        if r["benchmark"] == "K3" and r["method"] == "xag" and r["profile"] == "none"
    ]
    assert (
        next(
            r
            for r in selected
            if r["metric_level"] == "common_basis" and r["regime"] == "R2"
        )["status"]
        == "failed"
    )
    assert {r["seed"] for r in selected if r["metric_level"] == "routed"} == {
        11,
        23,
        37,
        41,
        53,
    }
    assert {
        r["precision"] for r in selected if r["metric_level"] == "static_fault_tolerant"
    } == {0.001, 0.01, 0.0001}
    assert not any("cost" in r for r in rows)


def test_continuation_rejects_completed_groups():
    import pytest

    previous = [dict(benchmark="K3", method="xag", cases={"R1:logical": "complete"})]
    with pytest.raises(ValueError, match="overlap completed"):
        batch.reject_completed_requests(CONFIG, previous)
    k5_config = {**CONFIG, "graphs": ["K5"]}
    batch.reject_completed_requests(k5_config, previous)


def test_k5_gate_and_witnesses_preserve_sample_qualification():
    from logique.coloring import read_dimacs

    config = json.loads(
        (
            batch.WORKTREE
            / "configs/research/comparison_common_lowering_k5_1101052342.json"
        ).read_text()
    )
    original = read_dimacs(batch.WORKTREE / "datasets/graphs/benchmarks/K5.col")
    problem = ColoringProblem(original.vertices, original.edges, original.colors)
    gate = batch.structural_gate(problem, config["budget"])
    assert not gate["accepted"]
    assert gate["constraints"] == 25
    assert batch.structural_gate(
        ColoringProblem(original.vertices, original.edges, 8), config["budget"]
    )["accepted"]
    assert not batch.structural_gate(problem, CONFIG["budget"])["accepted"]
    report = batch.verified_witnesses(problem)
    assert report["positive_status"] == "verified"
    assert len(report["assignments"]) >= 3
    assert config["validation"] == "sampled"
    assert config["graphs"] == ["K5"]


def test_group_context_scalars_are_json_serializable():
    import numpy as np

    assert json.dumps(batch.native_scalar(np.int64(7))) == "7"
    assert batch.native_scalar(float("nan")) is None
