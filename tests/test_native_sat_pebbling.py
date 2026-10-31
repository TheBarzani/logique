"""Bounded SAT mapping with independent scalar coherent-action checks."""

import itertools
import json
import os
import subprocess
from unittest.mock import patch

import pytest

from logique.synthesis import synthesize
from logique.synthesis.native import SAT_LIMITS, run_native
from logique.circuits.records import _qiskit_records

BUDGET = dict(
    qubit_budget=16, sat_max_steps=64, sat_conflict_limit=10000, sat_time_seconds=3
)


def source(tmp_path, body, inputs="b, a, c, unused", outputs="y"):
    path = tmp_path / "tiny.v"
    path.write_text(
        f"module top({inputs}, {outputs});\ninput {inputs};\noutput {outputs};\n"
        + body
        + "\nendmodule\n"
    )
    return path


def apply(records, bits):
    phase = 1
    for row in records:
        assert row["kind"] in ("x", "z")
        controls = row.get("controls", [])
        assert len(set(controls)) == len(controls)
        assert row["target"] not in controls
        if all(
            bits[q] == p
            for q, p in zip(controls, row.get("polarity", [True] * len(controls)))
        ):
            if row["kind"] == "x":
                bits[row["target"]] ^= 1
            elif bits[row["target"]]:
                phase *= -1
    return phase


def coherent(result, expected):
    """Every basis column including arbitrary joint targets; no quantum arrays."""
    md = result.metadata
    n, m = len(md["input_qubits"]), len(md["output_qubits"])
    assert n <= 6 and m <= 6 and md["num_qubits"] <= 64
    oracle = list(_qiskit_records(result.oracle()))
    phases = [list(_qiskit_records(result.phase_oracle(output=j))) for j in range(m)]
    for x in itertools.product((0, 1), repeat=n):
        values = expected(*x)
        for targets in itertools.product((0, 1), repeat=m):
            bits = [0] * (md["num_qubits"] + m)
            for q, bit in zip(md["input_qubits"], x):
                bits[q] = bit
            bits[md["num_qubits"] :] = targets
            want = bits.copy()
            want[md["num_qubits"] :] = [t ^ y for t, y in zip(targets, values)]
            assert apply(oracle, bits) == 1
            assert bits == want
        for j, records in enumerate(phases):
            bits = [0] * md["num_qubits"]
            for q, bit in zip(md["input_qubits"], x):
                bits[q] = bit
            want = bits.copy()
            assert apply(records, bits) == (-1 if values[j] else 1)
            assert bits == want


@pytest.mark.integration
@pytest.mark.parametrize("method", ["aig_bennett", "xag_bennett"])
@pytest.mark.parametrize("policy", ["none", "refactoring"])
@pytest.mark.parametrize("case", ["shared", "parity", "alias", "zero_gate"])
def test_actual_sat_coherent_action(tmp_path, method, policy, case):
    fixtures = {
        "shared": (
            "wire p, q, r;\nassign p = a & ~b;\nassign q = p ^ c;\n"
            "assign r = p & c;\nassign y = q | r;\n",
            "y",
            lambda b, a, c, u: [((a & (1 - b)) ^ c) | (a & (1 - b) & c)],
        ),
        "parity": (
            "wire p, q, l, r;\nassign p = a ^ b;\nassign q = b ^ c;\n"
            "assign l = p ^ c;\nassign r = a ^ q;\nassign y = l & ~r;\n",
            "y",
            lambda b, a, c, u: [0],
        ),
        "alias": (
            "wire p;\nassign p = a & b;\nassign y = ~b;\nassign z = p;\n"
            "assign w = ~p;\nassign v = 1'b0;\nassign u = 1'b1;\n",
            "y, z, w, v, u",
            lambda b, a, c, unused: [1 - b, a & b, 1 - (a & b), 0, 1],
        ),
        "zero_gate": (
            "assign y = ~b;\nassign z = 1'b0;\nassign w = 1'b1;\n",
            "y, z, w",
            lambda b, a, c, unused: [1 - b, 0, 1],
        ),
    }
    text, outputs, reference = fixtures[case]
    result = synthesize(
        source(tmp_path, text, outputs=outputs),
        method,
        strategy="sat_pebbling",
        preprocessing=policy,
        **BUDGET,
    )
    assert result.metadata["sat_validation"]["cec"] == "not_performed"
    assert (
        result.metadata["mapping_strategy"]["implementation"]
        == "logique::bounded_sat_pebbling"
    )
    assert result.metadata["num_qubits"] <= BUDGET["qubit_budget"]
    assert {s["action"] for s in result.metadata["steps"]} <= {"compute", "uncompute"}
    coherent(result, reference)


@pytest.mark.integration
@pytest.mark.parametrize("method", ["aig_bennett", "xag_bennett"])
def test_recomputation_with_actual_qubit_budget(tmp_path, method):
    # Four serial ANDs can clean with three gate pebbles, requiring recomputation.
    text = (
        "wire p, q, r;\nassign p = a & b;\nassign q = p & c;\n"
        "assign r = q & d;\nassign y = r & e;\n"
    )
    path = source(tmp_path, text, inputs="a, b, c, d, e")
    result = synthesize(
        path,
        method,
        strategy="sat_pebbling",
        preprocessing="none",
        **{**BUDGET, "qubit_budget": 8},
    )
    assert result.metadata["num_qubits"] == 8
    nodes = [s["node"] for s in result.metadata["steps"] if s["action"] == "compute"]
    assert len(nodes) > len(set(nodes))
    assert result.metadata["sat_validation"]["zero_releases"] >= 4
    coherent(result, lambda a, b, c, d, e: [a & b & c & d & e])


@pytest.mark.integration
@pytest.mark.parametrize(
    "controls, match",
    [
        ({"qubit_budget": 2}, "qubit_budget"),
        ({"qubit_budget": 5, "sat_max_steps": 1}, "horizon budget"),
    ],
)
def test_real_negative_budgets(tmp_path, controls, match):
    path = source(tmp_path, "wire p;\nassign p = a & b;\nassign y = p & c;\n")
    with pytest.raises(RuntimeError, match=match):
        synthesize(
            path,
            "xag_bennett",
            strategy="sat_pebbling",
            preprocessing="none",
            **{**BUDGET, **controls},
        )


@pytest.mark.integration
def test_input_cap_before_tables_and_zero_gate_solver(tmp_path):
    path = source(tmp_path, "assign y = a;\n", inputs="a, b, c, d, e, f, g")
    with pytest.raises(RuntimeError, match="unsupported domain"):
        synthesize(path, "xag_bennett", strategy="sat_pebbling", **BUDGET)


@pytest.mark.parametrize("name", SAT_LIMITS)
@pytest.mark.parametrize("value", [None, 0, -1, True, 1.5, "2", 100001])
def test_python_rejects_invalid_controls_before_launch(name, value):
    with patch("logique.synthesis.native.subprocess.run") as launch:
        with pytest.raises(ValueError, match=name):
            synthesize(
                "absent.v",
                "xag_bennett",
                strategy="sat_pebbling",
                **{**BUDGET, name: value},
            )
        launch.assert_not_called()


@pytest.mark.parametrize("method", ["xag", "klut_bennett", "best_fit"])
def test_unsupported_method(method):
    with pytest.raises(ValueError, match="only for AIG/XAG"):
        synthesize("absent.v", method, strategy="sat_pebbling", **BUDGET)


def test_budgets_require_sat():
    with pytest.raises(ValueError, match="budgets require"):
        synthesize("absent.v", "xag_bennett", qubit_budget=5)


@pytest.mark.integration
@pytest.mark.parametrize(
    "extra",
    [
        {"qubit_budget": 0},
        {"qubit_budget": True},
        {"sat_time_seconds": 31},
        {"strategy": "fast_lowt"},
    ],
)
def test_native_controls_cannot_bypass_python(tmp_path, extra):
    path = source(tmp_path, "assign y = a & b;\n")
    request = dict(
        path=str(path), method="xag_bennett", strategy="sat_pebbling", **BUDGET
    )
    request.update(extra)
    proc = subprocess.run(
        [os.environ["LOGIQUE_NATIVE_EXECUTABLE"]],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert proc.returncode == 1
    assert not proc.stdout


def test_native_process_wall_timeout_is_enforced(tmp_path):
    script = tmp_path / "blocked"
    script.write_text("#!/bin/sh\nexec /bin/sleep 4\n")
    script.chmod(0o755)
    with pytest.raises(subprocess.TimeoutExpired):
        run_native(
            "absent.v",
            "xag_bennett",
            executable=script,
            strategy="sat_pebbling",
            **{**BUDGET, "sat_time_seconds": 1},
        )


@pytest.mark.integration
@pytest.mark.parametrize("method", ["aig_bennett", "xag_bennett"])
@pytest.mark.parametrize("case", ["edge", "isolated", "empty", "unsatisfiable"])
def test_coloring_reference_and_restoration(method, case):
    from logique import ColoringProblem, encode_coloring

    problems = {
        "edge": ColoringProblem((2, 9), ((2, 9),), 3),
        "isolated": ColoringProblem((9,), (), 3),
        "empty": ColoringProblem((), (), 2),
        "unsatisfiable": ColoringProblem((9,), ((9, 9),), 2),
    }
    problem = problems[case]
    encoding = encode_coloring(problem)
    result = synthesize(
        encoding, method, strategy="sat_pebbling", preprocessing="none", **BUDGET
    )

    def expected(*x):
        c = encoding.bits_per_color
        assignment = {
            v: sum(x[i * c + j] << j for j in range(c))
            for i, v in enumerate(problem.vertices)
        }
        return [int(problem.is_valid(assignment))]

    coherent(result, expected)


@pytest.mark.integration
def test_six_inputs_mask_and_output_reordering(tmp_path):
    path = source(
        tmp_path,
        "assign y = a & b;\nassign z = ~a;\n",
        inputs="f, e, d, c, b, a",
        outputs="y, z",
    )
    result = synthesize(
        path, "xag_bennett", outputs=[1, 0, 0], strategy="sat_pebbling", **BUDGET
    )
    coherent(result, lambda f, e, d, c, b, a: [1 - a, a & b, a & b])


@pytest.mark.integration
def test_output_copy_width_budget(tmp_path):
    path = source(tmp_path, "assign y = a;\n", inputs="a")
    with pytest.raises(RuntimeError, match="width exceeds"):
        synthesize(
            path,
            "xag_bennett",
            outputs=[0, 0],
            strategy="sat_pebbling",
            **{**BUDGET, "qubit_budget": 1},
        )


@pytest.mark.integration
def test_output_count_cap(tmp_path):
    path = source(tmp_path, "assign y = a;\n", inputs="a")
    with pytest.raises(RuntimeError, match="unsupported domain"):
        synthesize(
            path, "xag_bennett", outputs=[0] * 17, strategy="sat_pebbling", **BUDGET
        )


def test_bridge_must_confirm_sat_budgets(tmp_path):
    from types import SimpleNamespace

    exe = tmp_path / "bridge"
    exe.touch()
    payload = dict(
        network={},
        steps=[],
        num_qubits=3,
        mapping_strategy=dict(
            name="sat_pebbling",
            explicit=True,
            implementation="logique::bounded_sat_pebbling",
        ),
    )
    with patch(
        "logique.synthesis.native.subprocess.run",
        return_value=SimpleNamespace(returncode=0, stdout=json.dumps(payload)),
    ):
        with pytest.raises(RuntimeError, match="SAT budgets"):
            run_native(
                "absent.v",
                "xag_bennett",
                executable=exe,
                strategy="sat_pebbling",
                **BUDGET,
            )
