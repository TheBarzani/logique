"""Pinned AIG/XAG mappings: independent values and actual coherent gate action."""

import json
from pathlib import Path
import re
from types import SimpleNamespace

import numpy as np
import pytest

from logique.synthesis import synthesize
from logique.synthesis.native import METHODS, run_native
from logique.verification import truth_outputs, validate, verify_phase_oracle
from logique.verification.classical import _apply_record, input_assignments
from logique.circuits.records import _qiskit_records

METHODS_BENNETT = ("aig_bennett", "xag_bennett")
STRATEGIES = ("bennett", "bennett_inplace", "eager")
POLICIES = ("none", "refactoring")


@pytest.fixture
def native():
    from logique.paths import native_executable

    return native_executable()  # Acceptance must fail rather than skip a build.


def write_source(tmp_path, inputs, outputs, assignments):
    # The pinned structural Verilog reader expects token separators and lines.
    inputs, outputs = inputs.replace(",", ", "), outputs.replace(",", ", ")
    assignments = re.sub(r"([=^&|])", r" \1 ", assignments)
    assignments = assignments.replace(",", ", ").replace(";", ";\n")
    path = tmp_path / "fixture.v"
    path.write_text(
        f"module top({inputs}, {outputs});\ninput {inputs};\noutput {outputs};\n"
        + assignments
        + "\nendmodule\n"
    )
    return path


def check_action(result, expected):
    """Track emitted raw, XOR and phase gates without a dense statevector."""
    md = result.metadata
    inputs = input_assignments(len(md["input_qubits"]))
    for graph in (
        md["source_network"],
        md["preprocessing"]["after_network"],
        md["network"],
    ):
        np.testing.assert_array_equal(truth_outputs(graph, inputs), expected)
    report = validate(result)
    assert report["wrapped_restoration"] and report["raw_phase_exact"]
    # All joint target patterns, rather than only all-zero/all-one targets.
    n, m = len(inputs), len(expected)
    assignments = input_assignments(n + m)
    bits = np.zeros((result.oracle().num_qubits, 1 << (n + m)), dtype=bool)
    bits[md["input_qubits"]] = assignments[:n]
    bits[md["num_qubits"] :] = assignments[n:]
    initial = bits.copy()
    phases = np.ones(bits.shape[1], dtype=complex)
    for record in _qiskit_records(result.oracle()):
        _apply_record(bits, phases, record)
    initial[md["num_qubits"] :] ^= np.tile(expected, (1, 1 << m))
    np.testing.assert_array_equal(bits, initial)
    np.testing.assert_array_equal(phases, 1)
    for output, values in enumerate(expected):
        bits = np.zeros((md["num_qubits"], 1 << n), dtype=bool)
        bits[md["input_qubits"]] = inputs
        initial = bits.copy()
        phases = np.ones(1 << n, dtype=complex)
        for record in _qiskit_records(result.phase_oracle(output=output)):
            _apply_record(bits, phases, record)
        np.testing.assert_array_equal(bits, initial)
        np.testing.assert_array_equal(phases, np.where(values, -1, 1))
    return report


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("fixture", ["chain", "fanout", "asymmetric"])
def test_independent_boolean_and_coherent_action(
    native, tmp_path, method, strategy, policy, fixture
):
    b, a, c, d, e, _unused = input_assignments(6)
    cases = {
        "chain": (
            "wire p,q,r; assign p=a^b; assign q=p^c; assign r=q^d; assign y=r&e;",
            [(a ^ b ^ c ^ d) & e],
        ),
        "fanout": (
            "wire p,q,r; assign p=a&~b; assign q=p^c; assign r=p&d; " "assign y=q|r;",
            [((a & ~b) ^ c) | (a & ~b & d)],
        ),
        "asymmetric": (
            "wire p,q,r; assign p=a&~b; assign q=p^~c; assign r=q^d; " "assign y=r&e;",
            [(((a & ~b) ^ ~c) ^ d) & e],
        ),
    }
    text, expected = cases[fixture]
    path = write_source(tmp_path, "b,a,c,d,e,unused", "y", text)
    result = synthesize(
        path, method, strategy=strategy, preprocessing=policy, executable=native
    )
    assert result.metadata["parameters"]["strategy"] == strategy
    assert result.metadata["mapping_strategy"] == {
        "name": strategy,
        "explicit": True,
        "implementation": f"caterpillar::{strategy}_mapping_strategy",
    }
    report = check_action(result, np.array(expected))
    assert report["raw_inputs_restored"]
    assert report["raw_workspace_zero"]
    if method == "aig_bennett":
        assert all("inplace" not in s["action"] for s in result.metadata["steps"])


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("policy", POLICIES)
def test_projection_alias_complements_and_constants(
    native, tmp_path, method, strategy, policy
):
    path = write_source(
        tmp_path,
        "b,a,unused",
        "u,v,w,x,z",
        "wire p; assign p=a&b; assign u=~b; assign v=p; assign w=~p; "
        "assign x=1'b0; assign z=1'b1;",
    )
    result = synthesize(
        path,
        method,
        outputs=[4, 1, 0, 1, 3, 2],
        strategy=strategy,
        preprocessing=policy,
        executable=native,
    )
    b, a, _unused = input_assignments(3)
    expected = np.array([np.ones(8), a & b, ~b, a & b, np.zeros(8), ~(a & b)])
    check_action(result, expected.astype(bool))


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("case", ["edge", "isolated", "unsatisfiable", "empty"])
def test_independent_coloring(native, method, strategy, policy, case):
    from logique import ColoringProblem, encode_coloring

    problems = {
        "edge": ColoringProblem((1, 7), ((1, 7),), 2),
        "isolated": ColoringProblem((9,), (), 3),
        "unsatisfiable": ColoringProblem((9,), ((9, 9),), 2),
        "empty": ColoringProblem((), (), 2),
    }
    encoding = encode_coloring(problems[case])
    result = synthesize(
        encoding, method, strategy=strategy, preprocessing=policy, executable=native
    )
    assert result.metadata["parameters"]["strategy"] == strategy
    assert validate(result)["wrapped_restoration"]
    assert verify_phase_oracle(result, encoding=encoding)["phase_exact"]


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("policy", POLICIES)
def test_tiny_superposition(native, tmp_path, method, strategy, policy):
    from logique.verification import verify_small_quantum

    path = write_source(tmp_path, "b,a", "y", "assign y=a&~b;")
    result = synthesize(
        path, method, strategy=strategy, preprocessing=policy, executable=native
    )
    assert result.oracle().num_qubits <= 5
    verify_small_quantum(result)


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("value", [False, True])
def test_zero_input_constants(native, tmp_path, method, policy, value):
    path = tmp_path / "constant.v"
    path.write_text(
        f"module top(y);\noutput y;\nassign y = 1'b{int(value)};\nendmodule\n"
    )
    for strategy in STRATEGIES:
        result = synthesize(
            path, method, strategy=strategy, preprocessing=policy, executable=native
        )
        check_action(result, np.array([[value]]))


@pytest.mark.integration
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("target_kind", ["input", "gate"])
def test_inplace_steps_emit_on_live_input_and_gate_targets(
    native, tmp_path, policy, target_kind
):
    first = "a^b" if target_kind == "input" else "a&b"
    path = write_source(
        tmp_path,
        "a,b,c,d",
        "y",
        f"wire p,q,r; assign p={first}; assign q=p^c; assign r=q^d; assign y=r&a;",
    )
    result = synthesize(
        path,
        "xag_bennett",
        strategy="bennett_inplace",
        preprocessing=policy,
        executable=native,
    )
    steps = result.metadata["steps"]
    inplace = [s for s in steps if s["action"] == "compute_inplace"]
    assert len(inplace) >= 2
    assert all(s["explicit_leaves"] is None for s in inplace)
    graph = result.metadata["network"]
    # Node indices differ from qubit indices (constant node 0 has no wire here).
    if target_kind == "input":
        assert inplace[0]["target_index"] in graph["inputs"]
    else:
        assert inplace[0]["target_index"] not in graph["inputs"]
    for step in inplace:
        node = next(n for n in graph["nodes"] if n["id"] == step["node"])
        assert step["target_index"] in [f["node"] for f in node["fanins"]]
    inverses = [s for s in steps if s["action"] == "uncompute_inplace"]
    assert [(s["node"], s["target_index"]) for s in inplace] == [
        (s["node"], s["target_index"]) for s in reversed(inverses)
    ]
    baseline = synthesize(path, "xag_bennett", preprocessing=policy, executable=native)
    assert result.circuit.num_qubits < baseline.circuit.num_qubits
    a, b, c, d = input_assignments(4)
    p = a ^ b if target_kind == "input" else a & b
    assert check_action(result, np.array([(p ^ c ^ d) & a]))["raw_inputs_restored"]


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("policy", POLICIES)
def test_eager_cleanup_precedes_later_output_computation(
    native, tmp_path, method, policy
):
    path = write_source(
        tmp_path,
        "a,b,c,d",
        "y,z",
        "wire p,q; assign p=a&b; assign y=p&c; assign q=a&d; assign z=q&b;",
    )
    result = synthesize(
        path, method, strategy="eager", preprocessing=policy, executable=native
    )
    actions = [s["action"] for s in result.metadata["steps"]]
    assert "compute" in actions[actions.index("uncompute") + 1 :]
    assert set(actions) == {"compute", "uncompute"}
    baseline = synthesize(path, method, preprocessing=policy, executable=native)
    assert result.circuit.num_qubits < baseline.circuit.num_qubits
    a, b, c, d = input_assignments(4)
    check_action(result, np.array([a & b & c, a & d & b]))


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS_BENNETT)
@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("policy", POLICIES)
def test_shared_fanout_and_intermediate_output_stay_live(
    native, tmp_path, method, strategy, policy
):
    path = write_source(
        tmp_path,
        "a,b,c,d",
        "y,z,w,v",
        "wire p,q,r; assign p=a&b; assign q=p^c; assign y=q&d; "
        "assign r=p^d; assign z=r&c; assign w=~p; assign v=p;",
    )
    result = synthesize(
        path, method, strategy=strategy, preprocessing=policy, executable=native
    )
    a, b, c, d = input_assignments(4)
    p = a & b
    check_action(result, np.array([(p ^ c) & d, (p ^ d) & c, ~p, p]))
    # Neither admitted schedule recomputes a node or requests multiple live copies.
    computed = [
        s["node"]
        for s in result.metadata["steps"]
        if s["action"] in ("compute", "compute_inplace")
    ]
    assert len(computed) == len(set(computed))


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("strategy", ["low_t", "low_depth", "sat", "", False, {}, []])
def test_python_rejects_unsupported_before_launch(monkeypatch, method, strategy):
    from logique.synthesis import api

    monkeypatch.setattr(api, "run_native", lambda *a, **kw: pytest.fail("launched"))
    with pytest.raises(ValueError, match="strategy"):
        synthesize(Path("unused.v"), method, strategy=strategy)


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("strategy", ["low_t", "low_depth", "sat", None, False, {}, []])
def test_native_rejects_unsupported(native, tmp_path, method, strategy):
    path = write_source(tmp_path, "a,b", "y", "assign y=a&b;")
    with pytest.raises(RuntimeError):
        run_native(path, method, strategy=strategy, executable=native)


@pytest.mark.integration
@pytest.mark.parametrize("method", ["xag", "klut_bennett", "best_fit"])
@pytest.mark.parametrize("strategy", STRATEGIES)
def test_reject_method_strategy_combination(native, tmp_path, method, strategy):
    path = write_source(tmp_path, "a,b", "y", "assign y=a&b;")
    with pytest.raises(ValueError, match="only for"):
        synthesize(path, method, strategy=strategy, executable=native)
    with pytest.raises(RuntimeError, match="only for"):
        run_native(path, method, strategy=strategy, executable=native)


@pytest.mark.parametrize(
    "evidence",
    [
        None,
        {},
        {"name": "eager", "explicit": False},
        {"name": "bennett_inplace"},
        {"name": "eager", "explicit": True, "implementation": "bennett"},
        {
            "name": "eager",
            "explicit": True,
            "implementation": "caterpillar::eager_mapping_strategy",
        },
    ],
)
def test_old_bridge_cannot_ignore_strategy(monkeypatch, tmp_path, evidence):
    from logique.synthesis import native as boundary

    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        boundary.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"network": {}, "mapping_strategy": evidence}),
        ),
    )
    with pytest.raises(RuntimeError, match="did not confirm"):
        run_native("unused.v", "xag_bennett", strategy="eager", executable=executable)
