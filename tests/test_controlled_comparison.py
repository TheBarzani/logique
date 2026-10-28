"""Profile boundaries, structure restoration and bounded comparison execution."""

import json
import sys

import pytest

from logique.benchmarks.controlled_comparison import supervise, witnesses
from logique.coloring import ColoringProblem, encode_coloring


def test_witnesses_exercise_positive_edge_and_invalid_code():
    problem = ColoringProblem((-8, 9, 27), ((-8, 9), (9, 27)), 5)
    found = witnesses(problem)
    encoding = encode_coloring(problem)
    assert problem.is_valid(encoding.decode(found["positive"]))
    assert not problem.is_valid(encoding.decode(found["edge_violation"]))
    assert encoding.decode(found["invalid_code"])[-8] == 5
    assert found["search_nodes"] <= found["search_node_cap"]


def test_supervisor_rejects_late_completion_and_preserves_logs(tmp_path):
    receipt = supervise(
        [sys.executable, "-c", "import time; time.sleep(2)"], tmp_path, 0.05
    )
    assert receipt["status"] == "timeout"
    assert receipt["seconds"] < 2
    assert (tmp_path / "stderr.log").is_file()
    assert "not isolated" in receipt["wait4_scope"]


@pytest.mark.parametrize("profile", ("mc_reduction", "esop", None, ""))
def test_unsupported_profile_rejects_before_io(profile):
    from logique.benchmarks.coloring_study import validate_study_config

    with pytest.raises(ValueError, match="optimization_profile"):
        validate_study_config(
            {"inputs": ["absent.col"], "optimization_profile": profile}
        )


@pytest.mark.parametrize("profile", ("none", "refactoring", "balanced"))
@pytest.mark.parametrize(
    "method", ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")
)
@pytest.mark.integration
def test_native_profile_boundaries_check_independent_predicate(profile, method):
    from logique.benchmarks.coloring_study import assemble_case

    case = assemble_case(
        ColoringProblem((-8, 9), ((-8, 9),), 5),
        method,
        "R2",
        optimization_profile=profile,
    )
    application = case.metadata["profile_application"]
    assert application["status"] == "applied"
    assert application["equivalence"]["status"] == "exhaustive"
    assert application["equivalence"]["boundaries"] == [
        "before_network",
        "after_network",
    ]
    assert case.metadata["backend_metadata"]["coloring"]["balanced_encoder"] == (
        profile == "balanced"
    )
    assert application["native_preprocessing"] == (
        "refactoring" if profile == "refactoring" else "none"
    )


def test_corrupt_profile_boundary_fails():
    from logique.benchmarks.coloring_study import _profile_equivalence
    from types import SimpleNamespace

    graph = {
        "inputs": [0],
        "outputs": [{"node": 1, "inverted": False}],
        "nodes": [
            {"id": 0, "kind": "input"},
            {"id": 1, "kind": "constant", "value": False},
        ],
    }
    result = SimpleNamespace(
        metadata={"preprocessing": {"before_network": graph, "after_network": graph}}
    )
    with pytest.raises(AssertionError, match="changed coloring"):
        _profile_equivalence(
            result,
            encode_coloring(ColoringProblem((8,), (), 2)),
            {"sampled": False, "samples": 4, "seed": 7},
        )


@pytest.mark.parametrize("emission", ("sequential", "parallel"))
@pytest.mark.parametrize("regime", ("R1", "R2", "R3"))
def test_structure_saved_restoring_components_and_roles(tmp_path, emission, regime):
    pytest.importorskip("qiskit")
    from qiskit import qpy
    from logique.benchmarks.coloring_study import run_coloring_study
    from logique.benchmarks.metrics import circuit_metrics

    source = tmp_path / "edge.col"
    source.write_text("p edge 2 1\nx colors 3\ne 1 2\n")
    output = run_coloring_study(
        {
            "inputs": [str(source)],
            "methods": [f"structure_{emission}"],
            "regimes": [regime],
            "optimization_profile": "none",
            "common_basis": True,
            "optimization_level": 0,
            "mcx_decomposition": "clean_tree",
            "mcx_workspace": "fresh_zero",
            "output": str(tmp_path / "1028000000-structure"),
        }
    )
    case = json.loads((output / "run.json").read_text())["cases"][0]
    assert case["status"] == "complete", case.get("reason")
    assert (
        case["profile_application"]["status"]
        == "not_applicable_hand_constructed_reference"
    )
    assert case["validation"]["workspace_restored"]
    for name, record in case["artifact_statistics"].items():
        with (output / name).open("rb") as stream:
            saved = qpy.load(stream)[0]
        assert circuit_metrics(saved)["gates"] == record["metrics"]["gates"]
        roles = record["workspace"]["roles"]
        wires = [q for pool in roles.values() for q in pool]
        assert sorted(wires) == list(range(saved.num_qubits))
        if record["metric_level"] == "common_basis":
            assert set(saved.count_ops()) <= {"u", "cx", "barrier"}


def test_requested_ledger_preserves_failed_cases_and_unsupported_axes():
    from logique.benchmarks.controlled_comparison import requested_ledger

    rows = requested_ledger(
        {
            "ledger": [
                {
                    "benchmark": "K3",
                    "input_sha256": "abc",
                    "method": "xag",
                    "optimization_profile": "none",
                    "iteration": 1,
                    "seed": 7,
                    "regimes": ["R1", "R2", "R3"],
                    "status": "timeout",
                    "common_status": "eligible",
                }
            ]
        }
    )
    actual = [row for row in rows if row["row_scope"] == "requested_component"]
    assert len(actual) == 45
    assert all(row["status"] == "timeout" for row in actual)
    assert {row["optimization_profile"] for row in rows} == {
        "none",
        "mc_reduction",
        "cut_esop_balancing",
    }
    assert {row["seed"] for row in rows} == {7, 11, 23, 37, 41, 53}
