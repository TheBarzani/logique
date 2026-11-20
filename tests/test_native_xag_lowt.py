"""Exact emitted action of the pinned XAG cone mapping, without T-cost claims."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

from logique.synthesis import synthesize
from logique.synthesis.native import METHODS, run_native
from logique.verification.classical import input_assignments
from tests.test_native_mapping_strategies import check_action, write_source

POLICIES = ("none", "refactoring")
IMPLEMENTATION = "caterpillar::xag_mapping_strategy"


def lowt(path, policy, **kwargs):
    return synthesize(
        path, "xag_bennett", strategy="xag_low_t", preprocessing=policy, **kwargs
    )


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("complement", [False, True])
def test_equal_and_complement_cones(tmp_path, policy, complement):
    path = write_source(
        tmp_path,
        "c,a,b,unused",
        "y",
        "wire p,q,l,r; assign p=a^b; assign q=b^c; "
        "assign l=p^c; assign r=a^q; "
        f"assign y=l&{'~' if complement else ''}r;",
    )
    result = lowt(path, policy)
    c, a, b, _unused = input_assignments(4)
    expected = np.zeros(16, dtype=bool) if complement else a ^ b ^ c
    report = check_action(result, np.array([expected]))
    assert report["raw_inputs_restored"] and report["raw_workspace_zero"]
    md = result.metadata
    for gate in md["gates"]:
        assert len(gate["controls"]) == len(set(gate["controls"]))
        assert gate["target"] not in gate["controls"]
        assert all(0 <= q < md["num_qubits"] for q in gate["controls"])
        assert 0 <= gate["target"] < md["num_qubits"]
    if policy == "none":
        normalizations = md["physical_control_normalization"]
        assert len(normalizations) == 1
        event = normalizations[0]
        assert event["controls"] == [0, 0]
        assert event["polarity"] == [True, not complement]
        assert event["rule"] == (
            "zero_conjunction" if complement else "idempotent_literals"
        )
        assert event["emitted_gate_count"] == (0 if complement else 1)
        audit = md["xag_schedule_audit"]["actions"]
        assert [row["action"] for row in audit] == [
            "compute_inplace",
            "buffer",
            "compute",
            "buffer",
            "compute_inplace",
        ]
        assert audit[0]["physical_target"] == audit[-1]["physical_target"] == 0
        assert audit[0]["physical_leaves"] == audit[-1]["physical_leaves"] == [0, 1, 2]


@pytest.mark.parametrize(
    "field", ["physical_control_normalization", "xag_schedule_audit"]
)
def test_reject_bridge_without_alias_policy(tmp_path, monkeypatch, field):
    from logique.synthesis import native

    response = {
        "network": {},
        "steps": [],
        "mapping_strategy": {
            "name": "xag_low_t",
            "explicit": True,
            "implementation": IMPLEMENTATION,
        },
        "physical_control_normalization": [],
        "xag_schedule_audit": {
            "policy": "pinned_lhrs_live_stacks_explicit_leaf_targets",
            "actions": [],
        },
    }
    del response[field]
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(response)),
    )
    with pytest.raises(RuntimeError, match="alias handling"):
        run_native(
            "unused.v", "xag_bennett", strategy="xag_low_t", executable=executable
        )


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize(
    "fixture",
    ["xor", "chain", "overlap", "included", "buffer", "fanout", "intermediate"],
)
def test_independent_expressions(tmp_path, policy, fixture):
    b, a, c, d, e, unused = input_assignments(6)
    cases = {
        "xor": ("assign y=a^~b;", [a ^ ~b]),
        "chain": (
            "wire p,q,r; assign p=a^b; assign q=p^c; assign r=q^d; assign y=r&e;",
            [(a ^ b ^ c ^ d) & e],
        ),
        "overlap": (
            "wire p,q; assign p=a^b; assign q=b^c; assign y=p&q;",
            [(a ^ b) & (b ^ c)],
        ),
        "included": (
            "wire p,q; assign p=a^b; assign q=p^c; assign y=p&q;",
            [(a ^ b) & (a ^ b ^ c)],
        ),
        "buffer": (
            "wire p,q; assign p=a^b; assign q=p^b; assign y=q&c;",
            [a & c],
        ),
        "fanout": (
            "wire p,q,r; assign p=a&~b; assign q=p^~c; assign r=p&d; " "assign y=q|r;",
            [((a & ~b) ^ ~c) | ((a & ~b) & d)],
        ),
        "intermediate": (
            "wire p,q,r; assign p=a&b; assign q=p^c; assign y=q&d; "
            "assign r=p^d; assign z=r&c; assign w=~p; assign v=p;",
            [((a & b) ^ c) & d, ((a & b) ^ d) & c, ~(a & b), a & b],
        ),
    }
    text, expected = cases[fixture]
    path = write_source(
        tmp_path,
        "b,a,c,d,e,unused",
        "y,z,w,v" if fixture == "intermediate" else "y",
        text,
    )
    result = lowt(path, policy)
    assert result.metadata["mapping_strategy"] == {
        "name": "xag_low_t",
        "explicit": True,
        "implementation": IMPLEMENTATION,
    }
    assert result.metadata["parameters"]["strategy"] == "xag_low_t"
    assert not any("level" in s["action"] for s in result.metadata["steps"])
    check_action(result, np.array(expected))


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
def test_aliases_projection_unused_order(tmp_path, policy):
    path = write_source(
        tmp_path,
        "b,a,unused",
        "u,v,w,x,z",
        "wire p; assign p=a&~b; assign u=~b; assign v=p; assign w=~p; "
        "assign x=1'b0; assign z=1'b1;",
    )
    result = lowt(path, policy, outputs=[4, 1, 0, 1, 3, 2])
    b, a, unused = input_assignments(3)
    check_action(
        result,
        np.array([np.ones(8), a & ~b, ~b, a & ~b, np.zeros(8), ~(a & ~b)], dtype=bool),
    )


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("value", [False, True])
def test_zero_input_constant(tmp_path, policy, value):
    path = tmp_path / "constant.v"
    path.write_text(
        f"module top(y);\noutput y;\nassign y = 1'b{int(value)};\nendmodule\n"
    )
    check_action(lowt(path, policy), np.array([[value]]))


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("case", ["edge", "isolated", "empty", "unsatisfiable"])
def test_coloring_independent_predicate(policy, case):
    from logique import ColoringProblem, encode_coloring
    from logique.verification import verify_phase_oracle

    problems = {
        "edge": ColoringProblem((1, 7), ((1, 7),), 2),
        "isolated": ColoringProblem((9,), (), 3),
        "empty": ColoringProblem((), (), 2),
        "unsatisfiable": ColoringProblem((9,), ((9, 9),), 2),
    }
    encoding = encode_coloring(problems[case])
    result = lowt(encoding, policy)
    assert verify_phase_oracle(result, encoding=encoding)["phase_exact"]


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
def test_tiny_coherent_action(tmp_path, policy):
    from logique.verification import verify_small_quantum

    path = write_source(tmp_path, "b,a", "y", "assign y=a&~b;")
    result = lowt(path, policy)
    assert result.oracle().num_qubits <= 5
    verify_small_quantum(result)


@pytest.mark.parametrize("method", [m for m in METHODS if m != "xag_bennett"])
def test_reject_other_methods_before_launch(tmp_path, monkeypatch, method):
    from logique.synthesis import api

    monkeypatch.setattr(api, "run_native", lambda *a, **kw: pytest.fail("launched"))
    with pytest.raises(ValueError, match="strategy"):
        synthesize(tmp_path / "unused.v", method, strategy="xag_low_t")


@pytest.mark.integration
@pytest.mark.parametrize("method", [m for m in METHODS if m != "xag_bennett"])
def test_native_reject_other_methods(tmp_path, method):
    path = write_source(tmp_path, "a,b", "y", "assign y=a&b;")
    with pytest.raises(RuntimeError, match="only for"):
        run_native(path, method, strategy="xag_low_t")


@pytest.mark.parametrize(
    "strategy",
    [
        "low_t",
        "xag_fast_lowt",
        "xag_low_depth",
        "fast_low_t",
        "low_depth",
        "sat",
        "level",
        "xag_mapping_strategy",
    ],
)
def test_reject_unsupported_controls(tmp_path, strategy):
    path = write_source(tmp_path, "a,b", "y", "assign y=a&b;")
    with pytest.raises(ValueError, match="strategy"):
        synthesize(path, "xag_bennett", strategy=strategy)
    with pytest.raises(RuntimeError, match="strategy"):
        run_native(path, "xag_bennett", strategy=strategy)


@pytest.mark.parametrize("field", ["name", "explicit", "implementation", "steps"])
def test_require_exact_native_confirmation(tmp_path, monkeypatch, field):
    from logique.synthesis import native

    response = {
        "network": {},
        "steps": [],
        "mapping_strategy": {
            "name": "xag_low_t",
            "explicit": True,
            "implementation": IMPLEMENTATION,
        },
    }
    if field == "steps":
        del response["steps"]
    else:
        response["mapping_strategy"][field] = {
            "name": "bennett",
            "explicit": False,
            "implementation": "caterpillar::bennett_mapping_strategy",
        }[field]
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(response)),
    )
    with pytest.raises(RuntimeError, match="did not confirm"):
        run_native(
            "unused.v", "xag_bennett", strategy="xag_low_t", executable=executable
        )


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
def test_explicit_leaves_emit_actual_input_target_gates(tmp_path, policy):
    path = write_source(
        tmp_path,
        "a,b,c,d,e",
        "y",
        "wire p,q,r; assign p=a^b; assign q=p^c; assign r=q^d; assign y=r&e;",
    )
    result = lowt(path, policy)
    md = result.metadata
    # The cone root 8 overwrites PI node 1, physically wire 0. Both outer
    # actions are compute_inplace, even though the second restores the input.
    cone = {
        "action": "compute_inplace",
        "node": 8,
        "target_index": 1,
        "explicit_leaves": [1, 2, 3, 4],
        "leaves": [1, 2, 3, 4],
    }
    assert md["steps"] == [
        cone,
        {
            "action": "compute",
            "node": 9,
            "explicit_leaves": None,
            "cell_override": None,
        },
        cone,
    ]
    cx = [
        {"kind": "x", "controls": [c], "polarity": [True], "target": 0}
        for c in (1, 2, 3)
    ]
    assert (
        md["gates"]
        == cx
        + [{"kind": "x", "controls": [4, 0], "polarity": [True, True], "target": 5}]
        + cx
    )
    a, b, c, d, e = input_assignments(5)
    report = check_action(result, np.array([(a ^ b ^ c ^ d) & e]))
    assert report["raw_inputs_restored"] and report["raw_workspace_zero"]


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
def test_gate_node_target_and_exact_and_cleanup(tmp_path, policy):
    path = write_source(
        tmp_path,
        "a,b,c,d,e",
        "y",
        "wire f,g,p; assign f=a&b; assign g=c&d; assign p=f^g; assign y=p&e;",
    )
    result = lowt(path, policy)
    md = result.metadata
    inplace = [s for s in md["steps"] if s["action"] == "compute_inplace"]
    assert len(inplace) == 2
    assert all(
        s["target_index"] == 6 and s["explicit_leaves"] == [6, 7] for s in inplace
    )
    # Node 6 lives on physical wire 5. Four exact Toffolis implement the
    # two inner ANDs and their cleanup; the fifth computes the output.
    rows = [(g["controls"], g["target"], g["polarity"]) for g in md["gates"]]
    first, second = ([0, 1], [2, 3]) if policy == "none" else ([2, 3], [0, 1])
    assert rows == [
        (first, 5, [True, True]),
        (second, 6, [True, True]),
        ([6], 5, [True]),
        ([4, 5], 7, [True, True]),
        ([6], 5, [True]),
        (second, 6, [True, True]),
        (first, 5, [True, True]),
    ]
    a, b, c, d, e = input_assignments(5)
    report = check_action(result, np.array([((a & b) ^ (c & d)) & e]))
    assert report["raw_inputs_restored"] and report["raw_workspace_zero"]


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
def test_xor_intermediate_output_preserves_cone_boundary(tmp_path, policy):
    path = write_source(
        tmp_path,
        "a,b,c,d",
        "y,z,w",
        "wire p; assign p=a^b; assign y=p; assign z=p^c; assign w=z&d;",
    )
    a, b, c, d = input_assignments(4)
    check_action(lowt(path, policy), np.array([a ^ b, a ^ b ^ c, (a ^ b ^ c) & d]))
