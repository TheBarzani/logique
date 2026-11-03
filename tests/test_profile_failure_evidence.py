"""Completed preprocessing survives each final mapping failure boundary."""

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from logique.synthesis import api
from logique.synthesis import research_profiles as profiles


@pytest.fixture
def tools():
    paths = [
        os.environ.get(key)
        for key in ("LOGIQUE_NATIVE_EXECUTABLE", "LOGIQUE_BALANCER_EXECUTABLE")
    ]
    if not all(path and Path(path).is_file() for path in paths):
        pytest.skip("Explicit native bridge and corrected balancer required")
    return paths


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "source.v"
    path.write_text(
        "module top(b, a, y);\ninput b, a;\noutput y;\n"
        "assign y = b & ~a;\nendmodule\n"
    )
    return path


def check_passes(evidence):
    assert evidence["status"] == "failed"
    assert len(evidence["passes"]) == 3
    assert [stage["passes"][0]["name"] for stage in evidence["passes"]] == [
        "xag_balance",
        "algebraic",
        "esop",
    ]
    for stage in evidence["passes"]:
        assert stage["verilog"]
        assert stage["exported_network"]
        assert stage["independent_equivalence"]["status"] == "exhaustive"
    assert evidence["independent_equivalence"]["serialization"] is True
    assert evidence["source_verilog"]


def save_failure(label, evidence):
    """Optionally retain regression payloads in the caller's fresh evidence run."""
    parent = os.environ.get("LOGIQUE_PROFILE_FAILURE_EVIDENCE")
    if parent:
        path = Path(parent) / f"{label}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as stream:
            json.dump(evidence, stream, indent=2)
            stream.write("\n")


@pytest.mark.integration
@pytest.mark.parametrize("failure_kind", ["native", "timeout", "serialization"])
def test_mapping_failure_keeps_original_exception_and_richer_evidence(
    tools, source, monkeypatch, failure_kind
):
    bridge, balancer = tools
    error = {
        "native": RuntimeError("Native synthesis failed: injected mapper error"),
        "timeout": subprocess.TimeoutExpired(["injected-final-mapper"], 0.01),
        "serialization": json.JSONDecodeError("injected invalid JSON", "!", 0),
    }[failure_kind]
    richer = {"diagnostics": {"solver": "retained"}, "passes": [{"extra": True}]}
    error.profile_evidence = deepcopy(richer)

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(api, "run_native", fail)
    with pytest.raises(type(error)) as caught:
        api.synthesize(
            source,
            "xag_bennett",
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    assert caught.value is error
    evidence = error.profile_evidence
    check_passes(evidence)
    assert evidence["failed_boundary"] == "mapping_native"
    assert evidence["original_exception"] == {
        "type": type(error).__name__,
        "reason": str(error),
    }
    assert evidence["diagnostics"] == richer["diagnostics"]
    assert evidence["existing_profile_evidence"]
    assert evidence["mapping_request"]["method"] == "xag_bennett"
    json.dumps(evidence)
    save_failure(f"injected-{failure_kind}", evidence)


@pytest.mark.integration
def test_real_native_rejection_retains_completed_profile(tools, source):
    bridge, balancer = tools
    with pytest.raises(RuntimeError, match="inner_cut") as caught:
        api.synthesize(
            source,
            "best_fit",
            outer_cut=1,
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    evidence = caught.value.profile_evidence
    check_passes(evidence)
    save_failure("real-native-rejection", evidence)
    assert evidence["mapping_request"]["outer_cut"] == 1
    assert evidence["failed_boundary"] == "mapping_native"


@pytest.mark.integration
@pytest.mark.parametrize(
    "damage", ["inputs", "nodes", "fanin", "signature", "mismatch", "circuit"]
)
def test_returned_mapping_networks_survive_signature_cap_and_circuit_failures(
    tools, source, monkeypatch, damage
):
    bridge, balancer = tools
    real = api.run_native
    returned = {}

    def damaged(*args, **kwargs):
        md = real(*args, **kwargs)
        graph = md["network"]
        if damage == "inputs":
            graph["inputs"] = list(range(11))
        elif damage == "nodes":
            graph["nodes"] *= 4097
        elif damage == "fanin":
            graph["nodes"].append({"id": 999, "kind": "lut", "fanins": [{}] * 7})
        elif damage == "signature":
            graph["outputs"][0]["node"] = 999
        elif damage == "mismatch":
            graph["outputs"][0]["inverted"] ^= True
        else:
            md["gates"] = [{"kind": "invalid"}]
        returned.update(deepcopy(md))
        return md

    monkeypatch.setattr(api, "run_native", damaged)
    with pytest.raises((RuntimeError, KeyError, ValueError)) as caught:
        api.synthesize(
            source,
            "xag_bennett",
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    evidence = caught.value.profile_evidence
    check_passes(evidence)
    save_failure(f"returned-network-{damage}", evidence)
    assert evidence["mapping_networks"] == {
        name: returned[name] for name in ("source_network", "network")
    }
    assert evidence["failed_boundary"] == (
        "mapping_circuit" if damage == "circuit" else "mapping_signature:network"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"method": "klut_bennett", "k": 7},
        {"method": "klut_bennett", "k": True},
        {"outputs": [-1]},
        {"outputs": [True]},
        {"outputs": [1.5]},
    ],
)
def test_invalid_controls_precede_preprocessing(monkeypatch, source, kwargs):
    monkeypatch.setattr(
        profiles, "preprocess_verilog", lambda *a, **k: pytest.fail("preprocessing")
    )
    with pytest.raises(ValueError):
        api.synthesize(source, optimization_profile="cut_esop_balancing", **kwargs)


@pytest.mark.integration
def test_out_of_range_output_fails_before_mapping(tools, source, monkeypatch):
    bridge, balancer = tools
    monkeypatch.setattr(api, "run_native", lambda *a, **k: pytest.fail("mapping"))
    with pytest.raises(ValueError, match="Output index") as caught:
        api.synthesize(
            source,
            outputs=[99],
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    check_passes(caught.value.profile_evidence)
    assert caught.value.profile_evidence["failed_boundary"] == "mapping_output_controls"


def test_sat_profile_composition_forwards_every_budget(monkeypatch, source):
    graph = {
        "inputs": [],
        "nodes": [{"id": 0, "kind": "constant", "value": False}],
        "outputs": [{"node": 0, "inverted": False}],
    }
    profile = {
        "before_network": graph,
        "after_network": graph,
        "verilog": "unused",
        "source_sha256": "fixture",
        "caps": {"inputs": 10, "nodes": 4096},
        "seconds": 0,
    }
    monkeypatch.setattr(profiles, "preprocess_verilog", lambda *a, **k: profile)
    budgets = dict(
        qubit_budget=8, sat_max_steps=12, sat_conflict_limit=20, sat_time_seconds=1
    )

    def mapped(path, method, params, executable, **kwargs):
        assert method == "xag_bennett"
        assert params == {
            "strategy": "sat_pebbling",
            "preprocessing": "none",
            **budgets,
        }
        assert all(kwargs["request"][key] == value for key, value in budgets.items())
        return SimpleNamespace(
            metadata={
                "parameters": params,
                "seconds": 0,
                "source_network": graph,
                "network": graph,
            }
        )

    monkeypatch.setattr(api, "_synthesize_file", mapped)
    result = api.synthesize(
        source,
        "xag_bennett",
        strategy="sat_pebbling",
        optimization_profile="cut_esop_balancing",
        **budgets,
    )
    assert result.metadata["parameters"]["optimization_profile"] == "cut_esop_balancing"


@pytest.mark.integration
def test_supported_study_mapping_timeout_saves_three_passes_without_costs(
    tools, monkeypatch, tmp_path
):
    from logique.benchmarks.coloring_study import run_coloring_study
    from logique.paths import dump_directory_name

    bridge, _ = tools
    parent = Path(os.environ.get("LOGIQUE_PROFILE_FAILURE_EVIDENCE", tmp_path))
    parent.mkdir(parents=True, exist_ok=True)
    source = parent / "edge.col"
    source.write_text("p edge 2 1\ne 1 2\nx colors 3\n")
    error = subprocess.TimeoutExpired(["injected-final-mapper"], 0.01)

    def timeout(*args, **kwargs):
        raise error

    monkeypatch.setattr(api, "run_native", timeout)
    output = run_coloring_study(
        {
            "inputs": [str(source)],
            "methods": ["xag_bennett"],
            "regimes": ["R1"],
            "iterations": [1],
            "seeds": [7],
            "validation": "exhaustive",
            "optimization_profile": "cut_esop_balancing",
            "common_basis": False,
            "output": str(parent / dump_directory_name("mapping-timeout-study")),
        },
        executable=bridge,
    )
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    (case,) = manifest["cases"]
    assert case["status"] == "failed"
    check_passes(case["profile_failure"])
    assert case["profile_failure"]["original_exception"]["type"] == "TimeoutExpired"
    assert case["profile_failure"]["mapping_request"]["method"] == "xag_bennett"
    assert case["profile_failure"]["independent_equivalence"]["inputs"] == 4
    assert case == json.loads((output / f'{case["name"]}.json').read_text())
    assert not list(output.glob("*.qpy"))
    assert not (output / "summary.csv").exists()


@pytest.mark.integration
@pytest.mark.parametrize("boundary", ["mapping_serialization", "mapping_metadata"])
def test_serialization_and_provenance_errors_keep_completed_evidence(
    tools, source, monkeypatch, boundary
):
    bridge, balancer = tools
    error = OSError("injected serialization/provenance failure")
    if boundary == "mapping_serialization":
        real = Path.write_text

        def write(path, *args, **kwargs):
            if path.name == "optimized.v":
                raise error
            return real(path, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", write)
    else:

        def environment(**kwargs):
            raise error

        monkeypatch.setattr(api, "environment", environment)
    with pytest.raises(OSError) as caught:
        api.synthesize(
            source,
            "xag_bennett",
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    assert caught.value is error
    evidence = error.profile_evidence
    check_passes(evidence)
    save_failure(boundary, evidence)
    assert evidence["failed_boundary"] == boundary
    if boundary == "mapping_metadata":
        assert set(evidence["mapping_networks"]) == {"source_network", "network"}


@pytest.mark.integration
def test_coloring_temporary_cleanup_error_retains_completed_profile(tools, monkeypatch):
    from logique.coloring import ColoringProblem, encode_coloring

    bridge, balancer = tools
    original = api.tempfile.TemporaryDirectory
    error = OSError("injected coloring temporary-directory cleanup failure")

    class Directory(original):
        def __exit__(self, *args):
            value = super().__exit__(*args)
            if Path(self.name).name.startswith("logique-coloring-"):
                raise error
            return value

    monkeypatch.setattr(api.tempfile, "TemporaryDirectory", Directory)
    with pytest.raises(OSError) as caught:
        api.synthesize(
            encode_coloring(ColoringProblem((1, 2), ((1, 2),), 3)),
            "xag_bennett",
            optimization_profile="cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    assert caught.value is error
    check_passes(error.profile_evidence)
    assert error.profile_evidence["failed_boundary"] == "coloring_metadata"
    assert set(error.profile_evidence["mapping_networks"]) == {
        "source_network",
        "network",
    }
    save_failure("coloring-cleanup", error.profile_evidence)
