"""Profiles preserve ordered Boolean service before all representation mappings."""

import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

import logique
from logique.synthesis import research_profiles as profiles
from logique.synthesis.balancing import optimize_verilog

assert (
    Path(logique.__file__).resolve()
    == Path(__file__).resolve().parents[1] / "src/logique/__init__.py"
)
assert (
    Path(profiles.__file__).resolve()
    == Path(__file__).resolve().parents[1]
    / "src/logique/synthesis/research_profiles.py"
)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"profile": "refactoring"},
        {"timeout": 121},
        {"timeout": True},
        {"timeout": float("nan")},
        {"max_inputs": 11},
        {"max_inputs": True},
        {"max_nodes": 4097},
        {"max_nodes": 0},
    ],
)
def test_invalid_profile_controls_never_start_a_process(monkeypatch, tmp_path, kwargs):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid controls reached an executable")

    monkeypatch.setattr(subprocess, "run", forbidden)
    with pytest.raises(ValueError):
        profiles.preprocess_verilog(
            tmp_path / "absent.v",
            **{
                "profile": "cut_esop_balancing",
                **kwargs,
            },
        )


def test_mc_binding_does_not_certify_hidden_internal_passes(tmp_path):
    pytest.importorskip("tweedledum")
    source = tmp_path / "input.v"
    source.write_text("module top; endmodule\n")
    with pytest.raises(profiles.UnsupportedOptimizationProfile, match="per-pass CEC"):
        profiles.preprocess_verilog(source, "mc_reduction")


@pytest.mark.parametrize("field", ["cleanup_equivalent", "serialization_equivalent"])
@pytest.mark.parametrize("value", [None, "unknown", 1, False])
def test_unknown_cec_is_never_success(monkeypatch, tmp_path, field, value):
    source, tool = tmp_path / "input.v", tmp_path / "tool"
    source.write_text("module top; endmodule\n")
    tool.write_text("unused")
    payload = {
        "verilog": "unused",
        "cleanup_equivalent": True,
        "serialization_equivalent": True,
        "passes": [{"name": "xag_balance", "equivalent": True}],
        field: value,
    }
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0,
            stdout=json.dumps(payload),
            stderr="",
        ),
    )
    with pytest.raises(RuntimeError, match="equivalence evidence"):
        optimize_verilog(source, executable=tool)


def test_scalar_cec_preserves_asymmetric_position_output_order_and_polarity():
    graph = {
        "inputs": [4, 2, 9],
        "nodes": [
            {"id": 4, "kind": "input"},
            {"id": 2, "kind": "input"},
            {"id": 9, "kind": "input"},
            {"id": 0, "kind": "constant", "value": False},
            {
                "id": 8,
                "kind": "and",
                "truth": "1000",
                "fanins": [
                    {"node": 4, "inverted": False},
                    {"node": 2, "inverted": True},
                ],
            },
        ],
        "outputs": [
            {"node": 8, "inverted": True},
            {"node": 9, "inverted": False},
            {"node": 0, "inverted": True},
        ],
    }
    n, signatures = profiles._truth_signature(graph, 10, 4096)
    expected = tuple(
        sum(int(f(a)) << a for a in range(8))
        for f in (
            lambda a: not ((a & 1) and not ((a >> 1) & 1)),
            lambda a: (a >> 2) & 1,
            lambda a: True,
        )
    )
    assert (n, signatures) == (3, expected)
    with pytest.raises(profiles.UnsupportedOptimizationProfile, match="cap"):
        profiles._truth_signature(graph, 2, 4096)


@pytest.fixture
def native_tools():
    bridge = os.environ.get("LOGIQUE_NATIVE_EXECUTABLE")
    balancer = os.environ.get("LOGIQUE_BALANCER_EXECUTABLE")
    if not all(path and Path(path).is_file() for path in (bridge, balancer)):
        pytest.skip("Configure explicit synthesis bridge and standalone balancer")
    return bridge, balancer


SOURCES = [
    # Deliberately nonalphabetical primary inputs and unused input d.
    """module top(b, a, c, d, y);
input b, a, c, d;
output y;
wire t;
assign t = a & ~c;
assign y = b ^ t;
endmodule
""",
    """module top(b, a, y0, y1, y2, y3);
input b, a;
output y0, y1, y2, y3;
assign y0 = ~b;
assign y1 = 1'b0;
assign y2 = a;
assign y3 = 1'b1;
endmodule
""",
    """module top(y0, y1);
output y0, y1;
assign y0 = 1'b0;
assign y1 = 1'b1;
endmodule
""",
]


@pytest.mark.integration
@pytest.mark.parametrize("source", SOURCES)
@pytest.mark.parametrize(
    "method", ["xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit"]
)
def test_actual_profile_then_mapping_matches_original_function(
    native_tools, tmp_path, source, method
):
    pytest.importorskip("qiskit")
    import numpy as np
    from logique.synthesis import synthesize
    from logique.synthesis.native import run_native
    from logique.verification.classical import (
        input_assignments,
        truth_outputs,
        validate,
    )

    bridge, balancer = native_tools
    path = tmp_path / "original.v"
    path.write_text(source)
    original = run_native(path, "xag", executable=bridge, preprocessing="none")[
        "source_network"
    ]
    result = synthesize(
        path,
        method,
        executable=bridge,
        balancer_executable=balancer,
        optimization_profile="cut_esop_balancing",
    )
    md = result.metadata
    profile = md["research_profile"]
    assignments = input_assignments(len(original["inputs"]))
    np.testing.assert_array_equal(
        truth_outputs(original, assignments), truth_outputs(md["network"], assignments)
    )
    assert len(md["input_qubits"]) == len(original["inputs"])
    assert md["parameters"]["preprocessing"] == "none"
    assert [p["passes"][0]["name"] for p in profile["passes"]] == [
        "xag_balance",
        "algebraic",
        "esop",
    ]
    assert all(
        p["independent_equivalence"]["status"] == "exhaustive"
        for p in profile["passes"]
    )
    assert profile["independent_equivalence"]["serialization"] is True
    assert profile["mapping_equivalence"]["status"] == "exhaustive"
    assert validate(result)["wrapped_restoration"]


@pytest.mark.integration
@pytest.mark.parametrize("regime", ["R1", "R2", "R3"])
def test_study_profile_connects_asymmetric_k5_and_isolated_vertex(native_tools, regime):
    from logique.coloring import ColoringProblem
    from logique.benchmarks.coloring_study import assemble_case

    case = assemble_case(
        ColoringProblem((-3, 8, 12), ((-3, 8),), 5),
        "xag",
        regime,
        optimization_profile="cut_esop_balancing",
        validation="exhaustive",
    )
    application = case.metadata["profile_application"]
    assert application["status"] == "applied"
    assert application["native_preprocessing"] == "none"
    assert application["equivalence"]["status"] == "exhaustive"
    assert application["research_profile"]["independent_equivalence"]["inputs"] == 9


@pytest.mark.integration
def test_corrupted_pass_fails_at_that_boundary(native_tools, monkeypatch, tmp_path):
    bridge, balancer = native_tools
    source = tmp_path / "source.v"
    source.write_text(SOURCES[0])
    real = profiles.optimize_verilog
    calls = []

    def corrupt(path, passes, **kwargs):
        calls.append(passes)
        result = real(path, passes, **kwargs)
        result["verilog"] = SOURCES[0].replace("assign y = b ^ t;", "assign y = b & t;")
        return result

    monkeypatch.setattr(profiles, "optimize_verilog", corrupt)
    with pytest.raises(RuntimeError, match="after xag_balance") as failure:
        profiles.preprocess_verilog(
            source,
            "cut_esop_balancing",
            executable=bridge,
            balancer_executable=balancer,
        )
    assert calls == [["xag_balance"]]
    retained = failure.value.profile_evidence
    assert retained["status"] == "failed"
    assert retained["passes"][0]["verilog"].endswith("endmodule\n")
    assert retained["source_verilog"] == SOURCES[0]


@pytest.mark.integration
def test_above_input_cap_stops_before_balancing(native_tools, monkeypatch, tmp_path):
    from logique.coloring import ColoringProblem, encode_coloring

    source = encode_coloring(ColoringProblem(tuple(range(11)), (), 2)).write_verilog(
        tmp_path / "source.v"
    )
    monkeypatch.setattr(
        profiles, "optimize_verilog", lambda *a, **k: pytest.fail("above-cap balancing")
    )
    with pytest.raises(profiles.UnsupportedOptimizationProfile, match="cap"):
        profiles.preprocess_verilog(source, "cut_esop_balancing")


@pytest.mark.integration
@pytest.mark.parametrize(
    "method", ["xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit"]
)
def test_requested_output_permutation_survives_profile(native_tools, tmp_path, method):
    from logique.synthesis import synthesize
    from logique.verification.classical import (
        input_assignments,
        truth_outputs,
        validate,
    )
    import numpy as np

    bridge, balancer = native_tools
    source = tmp_path / "projection.v"
    source.write_text(SOURCES[1])
    result = synthesize(
        source,
        method,
        outputs=[3, 0, 2, 3],
        executable=bridge,
        balancer_executable=balancer,
        optimization_profile="cut_esop_balancing",
    )
    assignments = input_assignments(2)
    expected = np.array(
        [
            np.ones(4, dtype=bool),
            ~assignments[0],
            assignments[1],
            np.ones(4, dtype=bool),
        ]
    )
    np.testing.assert_array_equal(
        truth_outputs(result.metadata["network"], assignments), expected
    )
    assert validate(result)["wrapped_restoration"]


def test_connected_profile_ledger_keeps_original_manifests_historical():
    from logique.benchmarks.controlled_comparison import requested_ledger

    manifest = {
        "ledger": [
            {
                "benchmark": "tiny",
                "input_sha256": "fixture",
                "method": "xag",
                "optimization_profile": "none",
                "iteration": 1,
                "seed": 7,
                "regimes": ["R1"],
                "status": "not_run_budget",
                "common_status": "eligible",
            }
        ]
    }

    def unsupported(m):
        return {
            row["optimization_profile"]
            for row in requested_ledger(m)
            if row["status"] == "open_unsupported_profile"
        }

    assert unsupported(manifest) == {"mc_reduction", "cut_esop_balancing"}
    assert unsupported({**manifest, "connected_profiles": ["cut_esop_balancing"]}) == {
        "mc_reduction"
    }


@pytest.mark.integration
def test_timeout_preserves_completed_pass_and_never_runs_later_pass(
    native_tools, monkeypatch, tmp_path
):
    source = tmp_path / "source.v"
    source.write_text(SOURCES[0])
    real = profiles.optimize_verilog
    calls = []

    def interrupt(path, passes, **kwargs):
        calls.append(passes)
        if len(calls) == 2:
            raise subprocess.TimeoutExpired(["balancer"], 0.01)
        return real(path, passes, **kwargs)

    monkeypatch.setattr(profiles, "optimize_verilog", interrupt)
    with pytest.raises(subprocess.TimeoutExpired) as failure:
        profiles.preprocess_verilog(source, "cut_esop_balancing")
    assert calls == [["xag_balance"], ["algebraic"]]
    assert len(failure.value.profile_evidence["passes"]) == 1
    assert failure.value.profile_evidence["passes"][0]["verilog"]


def test_profile_mapping_guard_rejects_changed_output_order():
    graph = {
        "inputs": [],
        "nodes": [{"id": 0, "kind": "constant", "value": False}],
        "outputs": [{"node": 0, "inverted": False}, {"node": 0, "inverted": True}],
    }
    profile = {"before_network": graph, "caps": {"inputs": 10, "nodes": 4096}}
    changed = {**graph, "outputs": list(reversed(graph["outputs"]))}
    with pytest.raises(RuntimeError, match="mapping equivalence") as failure:
        profiles.verify_profile_mapping(
            profile, {"source_network": graph, "network": changed}
        )
    assert failure.value.profile_evidence["mapping_networks"]["network"] == changed
