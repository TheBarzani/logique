"""Native optimization must retain input order and prove every transformation."""

import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from logique.synthesis.balancing import optimize_verilog


@pytest.mark.parametrize(
    "kwargs",
    [
        {"passes": "xag_balance"},
        {"passes": None},
        {"passes": ["unknown"]},
        {"timeout": -1},
        {"timeout": float("nan")},
        {"cec_conflict_limit": True},
        {"cec_conflict_limit": -1},
    ],
)
def test_balancing_rejects_invalid_controls_before_running(
    tmp_path, monkeypatch, kwargs
):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid control reached the native process")

    monkeypatch.setattr(subprocess, "run", forbidden)
    with pytest.raises(ValueError):
        optimize_verilog(tmp_path / "input.v", **kwargs)


def test_failed_equivalence_evidence_never_returns_a_successful_optimization(
    tmp_path, monkeypatch
):
    source = tmp_path / "input.v"
    tool = tmp_path / "tool"
    source.write_text("module top(x,y); input x; output y; assign y=x; endmodule")
    tool.write_text("tool")
    payload = {
        "verilog": "incorrect",
        "cleanup_equivalent": True,
        "serialization_equivalent": True,
        "passes": [{"name": "xag_balance", "equivalent": False}],
    }
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=json.dumps(payload), stderr=""
        ),
    )
    with pytest.raises(RuntimeError, match="equivalence"):
        optimize_verilog(source, executable=tool)


@pytest.fixture
def native_tools():
    from logique.paths import native_executable

    tool = os.environ.get("LOGIQUE_BALANCER_EXECUTABLE")
    if not tool or not Path(tool).is_file():
        pytest.skip("Configure the separate native balancing tool")
    try:
        bridge = native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native synthesis bridge for cross-version exchange")
    return tool, bridge


@pytest.mark.integration
@pytest.mark.parametrize(
    "passes",
    [
        [],
        ["xag_balance"],
        ["algebraic"],
        ["esop"],
        ["xag_balance", "algebraic", "esop"],
    ],
)
@pytest.mark.parametrize(
    "source",
    [
        """module top(b, a, c, y);
input b, a, c;
output y;
wire t;
assign t = a & ~c;
assign y = b ^ t;
endmodule
""",
        """module top(a, b, y);
input a, b;
output y;
assign y = 1'b1;
endmodule
""",
        """module top(y);
output y;
assign y = 1'b0;
endmodule
""",
    ],
)
def test_balancing_roundtrip_matches_independent_truth_and_old_native_parser(
    native_tools, tmp_path, passes, source
):
    np = pytest.importorskip("numpy")
    from logique.synthesis.native import run_native
    from logique.verification.classical import input_assignments, truth_outputs

    tool, bridge = native_tools
    original = tmp_path / "original.v"
    # Both pinned Lorina frontends accept structural, line-oriented Verilog.
    original.write_text(source)
    result = optimize_verilog(original, passes, executable=tool)
    optimized = tmp_path / "optimized.v"
    optimized.write_text(result["verilog"])
    before = run_native(original, "xag", executable=bridge)["source_network"]
    after = run_native(optimized, "xag", executable=bridge)["source_network"]
    inputs = input_assignments(len(before["inputs"]))
    assert len(after["inputs"]) == len(before["inputs"])
    np.testing.assert_array_equal(
        truth_outputs(before, inputs), truth_outputs(after, inputs)
    )
    assert result["cleanup_equivalent"] and result["serialization_equivalent"]
    assert [p["name"] for p in result["passes"]] == passes
    assert all(p["equivalent"] for p in result["passes"])
    assert result["native"]["build"]["dependency_sources_clean"]


@pytest.mark.integration
def test_native_balancing_reduces_multiplicative_depth(native_tools, tmp_path):
    from logique import ColoringProblem, encode_coloring

    tool, _ = native_tools
    problem = ColoringProblem(tuple(range(9)), tuple((i, i + 1) for i in range(8)), 2)
    source = encode_coloring(problem).write_verilog(tmp_path / "path.v")
    result = optimize_verilog(source, executable=tool)
    assert result["input_statistics"]["multiplicative_depth"] == 7
    assert result["output_statistics"]["multiplicative_depth"] == 3
    assert result["output_statistics"]["and_count"] == 7
