"""Deterministic executed coloring tests, including absolute phase failures."""

import json
from pathlib import Path

import pytest

pytest.importorskip("qiskit")
from qiskit.quantum_info import Statevector
from logique.benchmarks.iteration_study import (
    _check_phase,
    _problem,
    simulate_case,
    validate_config,
)
from logique.circuits.structure import structure_oracle


@pytest.fixture
def config():
    return json.loads(Path("configs/iteration_pilot.json").read_text())


@pytest.mark.parametrize("regime", ["R1", "R2", "R3"])
@pytest.mark.parametrize(
    "case",
    [
        {"name": "edge", "vertices": [-3, 17], "edges": [[-3, 17]], "colors": 3},
        {"name": "unsat", "vertices": [7], "edges": [[7, 7]], "colors": 2},
        {"name": "empty", "vertices": [], "edges": [], "colors": 3},
        {"name": "isolates", "vertices": [-9, 22], "edges": [], "colors": 3},
    ],
)
def test_actual_coloring_sweep(case, regime, config, tmp_path):
    result = simulate_case(case, regime, config, tmp_path / "case")
    assert result["status"] == "complete"
    assert result["validation"]["phase_alignment"].startswith("none")
    assert (
        len(result["rows"]) == result["analytical_ledger"]["first_peak_iteration"] + 2
    )
    assert all(row["comparison_passed"] for row in result["rows"])
    assert result["confidence_interval"] is None
    if case["name"] == "edge":
        assert result["counts"]["marked"] == 6
        assert result["binary_witnesses"]["invalid_code_witness"] is not None
        assert result["binary_witnesses"]["edge_violation_witness"] is not None
        assert result["counts"]["positive_witness"] is not None
        if regime != "R1":
            assert (
                max(r["simulated_unused_code_leakage"] for r in result["rows"]) < 1e-20
            )
    if case["name"] == "unsat":
        assert all(
            r["simulated_valid_solution_probability"] == 0 for r in result["rows"]
        )


def test_cap_precedes_statevector_allocation(config, tmp_path, monkeypatch):
    case = next(c for c in config["cases"] if c["name"] == "C5_k3")

    def forbidden(*args, **kwargs):
        pytest.fail("Statevector allocated before width rejection")

    monkeypatch.setattr(Statevector, "from_int", forbidden)
    result = simulate_case(case, "R2", config, tmp_path / "case")
    assert result["status"] == "infeasible"
    assert result["construction"]["width"] == 22
    assert result["counts"]["marked"] == 30
    assert result["rows"] == []


def test_absolute_oracle_phase_rejects_opposite_scalar():
    case = {"name": "edge", "vertices": [0, 1], "edges": [[0, 1]], "colors": 2}
    problem = _problem(case)
    oracle = structure_oracle(problem).phase_oracle()
    oracle.global_phase += 3.141592653589793
    with pytest.raises(AssertionError, match="global phase"):
        _check_phase(oracle, problem, "R1")


def test_signed_diffusion_error_cannot_hide_in_probabilities(
    config, tmp_path, monkeypatch
):
    import logique.circuits.grover as grover

    original = grover._reflection

    def wrong_sign(preparation):
        result = original(preparation)
        result.global_phase += 3.141592653589793
        return result

    monkeypatch.setattr(grover, "_reflection", wrong_sign)
    case = {"name": "edge", "vertices": [0, 1], "edges": [[0, 1]], "colors": 2}
    result = simulate_case(case, "R1", config, tmp_path / "case")
    assert result["status"] == "failed_comparison"
    assert result["rows"][1]["absolute_probability_error"] < 1e-12
    assert result["rows"][1]["signed_amplitude_max_error_no_alignment"] > 0.9


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_qubits", 19),
        ("timeout_seconds", 181),
        ("budget_seconds", 901),
        ("tolerance", float("nan")),
    ],
)
def test_resource_contract_rejects(config, field, value):
    config[field] = value
    with pytest.raises(ValueError):
        validate_config(config)


def test_supervisor_preserves_timeout_and_budget_exclusions(
    config, tmp_path, monkeypatch
):
    from types import SimpleNamespace
    import logique.benchmarks.iteration_study as study

    config["cases"] = [config["cases"][0]]
    config["regimes"] = ["R1", "R2"]
    config["timeout_seconds"] = 1
    config["budget_seconds"] = 3
    monkeypatch.setattr(study.platform, "platform", lambda: "mock-platform")
    monkeypatch.setattr(study.subprocess, "check_output", lambda *a, **kw: "mock-git")
    ticks = iter(range(20))
    monkeypatch.setattr(study.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(
        study.subprocess, "Popen", lambda *a, **kw: SimpleNamespace(pid=42)
    )
    waits = iter([(0, 0, None), (42, 9, SimpleNamespace(ru_maxrss=123))])
    monkeypatch.setattr(study.os, "wait4", lambda *a: next(waits))
    killed = []
    monkeypatch.setattr(study.os, "killpg", lambda pid, sig: killed.append((pid, sig)))
    output = study.run_study(config, root=tmp_path)
    manifest = json.loads((output / "manifest.json").read_text())
    assert [r["status"] for r in manifest["cases"]] == ["timeout", "budget_excluded"]
    assert killed == [(42, study.signal.SIGKILL)]
    assert manifest["cases"][0]["returncode"] == -9
    assert manifest["cases"][0]["peak_rss_bytes"] > 0
    assert manifest["preservation"]


def test_unknown_supplied_count_rejects(config):
    config["marked"] = None
    with pytest.raises(ValueError, match="Unknown or missing"):
        validate_config(config)
