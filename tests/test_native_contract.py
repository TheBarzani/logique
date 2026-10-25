"""Common native preprocessing preserves independent Boolean and phase contracts."""

from pathlib import Path
import json
from types import SimpleNamespace

import pytest

from logique.synthesis.native import METHODS, run_native


@pytest.fixture
def native():
    from logique.paths import native_executable

    try:
        return native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the compiled native bridge")


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "factoring.v"
    path.write_text(
        """module top(b, a, c, unused, y);
input b, a, c, unused;
output y;
wire p, q, r;
assign p = a & b;
assign q = a & c;
assign r = p | q;
assign y = r & a;
endmodule
"""
    )
    return path


@pytest.mark.integration
@pytest.mark.parametrize("policy", ["none", "refactoring"])
def test_common_preprocessing_before_every_representation(native, source, policy):
    np = pytest.importorskip("numpy")
    from logique.synthesis import synthesize
    from logique.verification import validate, truth_outputs, verify_phase_oracle
    from logique.verification.classical import input_assignments

    inputs = input_assignments(4)
    b, a, c, _unused = inputs
    expected = [a & (b | c)]
    shared = None
    for method in METHODS:
        result = synthesize(source, method, preprocessing=policy, executable=native)
        md = result.metadata
        evidence = md["preprocessing"]
        assert evidence["common"] and evidence["policy"] == policy
        assert md["parameters"]["preprocessing"] == policy
        assert evidence["before_network"] == md["source_network"]
        if shared is None:
            shared = evidence
        assert shared == evidence
        for graph in (md["source_network"], evidence["after_network"], md["network"]):
            assert len(graph["inputs"]) == 4  # Includes the unused input.
            np.testing.assert_array_equal(truth_outputs(graph, inputs), expected)
        if policy == "none":
            assert evidence["after_network"] == evidence["before_network"]
        else:
            # This fixture makes an ignored policy observable.
            assert evidence["after_network"] != evidence["before_network"]
        assert validate(result)["wrapped_restoration"]
        assert verify_phase_oracle(result)["phase_exact"]


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("policy", ["none", "refactoring"])
def test_common_preprocessing_constants_aliases_and_projection(
    native, tmp_path, method, policy
):
    np = pytest.importorskip("numpy")
    from logique.synthesis import synthesize
    from logique.verification import validate, truth_outputs
    from logique.verification.classical import input_assignments, _apply_record
    from logique.circuits.records import _qiskit_records

    path = tmp_path / "aliases.v"
    path.write_text(
        """module top(b, a, unused, u, v, w, x, z);
input b, a, unused;
output u, v, w, x, z;
wire p;
assign p = a & b;
assign u = ~b;
assign v = p;
assign w = ~p;
assign x = 1'b0;
assign z = 1'b1;
endmodule
"""
    )
    # Order, repeated aliases, complemented logic and both constants survive.
    projection = [4, 1, 0, 1, 3, 2]
    result = synthesize(
        path, method, outputs=projection, preprocessing=policy, executable=native
    )
    md = result.metadata
    inputs = input_assignments(3)
    b, a, _unused = inputs
    p = a & b
    expected = np.array([np.ones(8, dtype=bool), p, ~b, p, np.zeros(8), ~p])
    for graph in (
        md["source_network"],
        md["preprocessing"]["after_network"],
        md["network"],
    ):
        np.testing.assert_array_equal(truth_outputs(graph, inputs), expected)
    assert validate(result)["wrapped_restoration"]
    # Independently track each actual phase wrapper, including both constants.
    for output in range(len(projection)):
        bits = np.zeros((md["num_qubits"], 8), dtype=bool)
        bits[md["input_qubits"]] = inputs
        initial = bits.copy()
        phases = np.ones(8, dtype=complex)
        for record in _qiskit_records(result.phase_oracle(output=output)):
            _apply_record(bits, phases, record)
        np.testing.assert_array_equal(bits, initial)
        np.testing.assert_allclose(phases, np.where(expected[output], -1, 1))


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS)
def test_omitted_policy_retains_legacy_mapping(native, source, method):
    policy = "none" if method == "aig_bennett" else "refactoring"
    legacy = run_native(source, method, executable=native)
    explicit = run_native(source, method, executable=native, preprocessing=policy)
    assert not legacy["preprocessing"]["common"]
    assert legacy["preprocessing"]["policy"] == policy
    for key in (
        "network",
        "source_network",
        "gates",
        "num_qubits",
        "input_qubits",
        "output_qubits",
        "steps",
    ):
        assert legacy.get(key) == explicit.get(key)


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("policy", ["none", "refactoring"])
def test_common_preprocessing_tiny_superposition(native, tmp_path, method, policy):
    pytest.importorskip("qiskit")
    from logique.synthesis import synthesize
    from logique.verification import verify_small_quantum

    path = tmp_path / "small.v"
    path.write_text(
        """module top(b, a, y);
input b, a;
output y;
assign y = a & ~b;
endmodule
"""
    )
    result = synthesize(path, method, preprocessing=policy, executable=native)
    assert result.oracle().num_qubits <= 5
    verify_small_quantum(result)


@pytest.mark.parametrize("policy", ["balanced", "legacy", "", False, {}, []])
def test_python_rejects_unsupported_policy_before_launch(monkeypatch, policy):
    from logique.synthesis import api

    monkeypatch.setattr(api, "run_native", lambda *a, **kw: pytest.fail("launched"))
    with pytest.raises(ValueError, match="preprocessing"):
        api.synthesize(Path("unused.v"), preprocessing=policy)


@pytest.mark.integration
@pytest.mark.parametrize(
    "controls",
    [
        {"preprocessing": "balanced"},
        {"preprocessing": "legacy"},
        {"preprocessing": None},
        {"preprocessing": {}},
        {"preprocessing": False},
        {"preprocessing": []},
        {"preprocess": "refactoring"},
        {"sat": True},
        {"k": 4},
    ],
)
def test_native_rejects_unsupported_controls(native, source, controls):
    with pytest.raises(RuntimeError):
        run_native(source, "xag", executable=native, **controls)


@pytest.mark.integration
def test_no_new_methods_exposed(native, source):
    assert METHODS == ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")
    with pytest.raises(RuntimeError, match="Unknown synthesis method"):
        run_native(source, "xag_mapping", executable=native)


@pytest.mark.parametrize(
    "evidence",
    [
        None,
        {},
        {"common": False, "policy": "none"},
        {"common": True, "policy": "refactoring"},
        {
            "common": True,
            "policy": "none",
            "before_network": None,
            "after_network": None,
        },
    ],
)
def test_old_or_nonconfirming_bridge_cannot_ignore_opt_in(
    monkeypatch, tmp_path, evidence
):
    from logique.synthesis import native as boundary

    executable = tmp_path / "old-bridge"
    executable.touch()
    monkeypatch.setattr(
        boundary.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"network": {}, "preprocessing": evidence}),
        ),
    )
    with pytest.raises(RuntimeError, match="did not confirm"):
        run_native("unused.v", "xag", executable=executable, preprocessing="none")


@pytest.mark.integration
@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("policy", ["none", "refactoring"])
@pytest.mark.parametrize("case", ["edge", "isolated", "unsatisfiable", "empty"])
def test_common_preprocessing_independent_coloring(native, method, policy, case):
    from logique import ColoringProblem, encode_coloring
    from logique.synthesis import synthesize
    from logique.verification import validate, verify_phase_oracle

    problems = {
        "edge": ColoringProblem((1, 7), ((1, 7),), 2),
        "isolated": ColoringProblem((9,), (), 3),
        "unsatisfiable": ColoringProblem((9,), ((9, 9),), 2),
        "empty": ColoringProblem((), (), 2),
    }
    encoding = encode_coloring(problems[case])
    result = synthesize(encoding, method, preprocessing=policy, executable=native)
    assert result.metadata["parameters"]["preprocessing"] == policy
    assert validate(result)["wrapped_restoration"]
    assert verify_phase_oracle(result, encoding=encoding)["phase_exact"]
