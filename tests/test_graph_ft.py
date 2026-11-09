"""Deterministic regression checks for the separate bounded graph FT harness."""

import json
import math
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import StatePreparation  # noqa: E402

from logique.benchmarks import graph_ft as ft, rotations, static_ft  # noqa: E402


@pytest.mark.parametrize("width", [1, 2, 3, 4, 5])
def test_separate_signed_s0_local_contract(width):
    limits = ft.GraphLimits()
    matrix = ft.local_matrix(ft.zero_reflection(width, limits), limits)
    expected = -np.eye(1 << width, dtype=complex)
    expected[0, 0] = 1
    assert np.linalg.norm(matrix - expected, 2) < 1e-12
    assert static_ft.MAX_OPERATOR_QUBITS == 4


def test_wide_clean_contract_never_allocates_operator():
    oracle = QuantumCircuit(13)
    oracle.x(1)
    oracle.cz(12, 1)
    oracle.x(1)
    with patch.object(ft, "Operator", side_effect=AssertionError("wide operator")):
        result = ft.clean_phase_check(
            oracle, [12, 1], lambda x: x == 1, ft.GraphLimits()
        )
    assert result["columns"] == 4
    assert result["phase_frobenius_error"] == 0


@pytest.mark.parametrize("fault", ["sign", "scratch", "mapping"])
def test_phase_cleanup_mapping_faults_rejected(fault):
    oracle = QuantumCircuit(6)
    oracle.x(1)
    oracle.cz(5, 1)
    oracle.x(1)
    mapping = [5, 1]
    if fault == "sign":
        oracle.global_phase += math.pi
    elif fault == "scratch":
        oracle.cx(5, 0)
    else:
        mapping.reverse()
    with pytest.raises(ValueError, match="contract failed"):
        ft.clean_phase_check(oracle, mapping, lambda x: x == 1, ft.GraphLimits())


@pytest.mark.parametrize(
    "width,data", [(19, 4), (13, 6), (1_000_000, 4), (True, 1), (2, 3)]
)
def test_preflight_rejects_before_arrays(width, data):
    with patch.object(ft.np, "zeros", side_effect=AssertionError("allocation")):
        with pytest.raises(ValueError, match="width"):
            ft.preflight(width, data, ft.GraphLimits())


@pytest.mark.parametrize(
    "kw",
    [
        {"seconds": 111},
        {"process_bytes": 7 * 1024**3},
        {"statevector_qubits": 19},
        {"clean_columns": True},
    ],
)
def test_invalid_budgets_reject(kw):
    with pytest.raises(ValueError):
        ft.GraphLimits(**kw)


def test_array_and_operation_budgets():
    with pytest.raises(ValueError, match="array budget"):
        ft.preflight(18, 4, replace(ft.GraphLimits(), array_bytes=1024))
    with pytest.raises(ValueError, match="column"):
        ft.preflight(13, 4, replace(ft.GraphLimits(), clean_columns=8))
    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.h(0)
    with pytest.raises(ValueError, match="operation budget"):
        ft.save_circuit(
            Path("unused"),
            "bad",
            circuit,
            emitted=True,
            limits=replace(ft.GraphLimits(), operations=1),
        )
    with patch.object(ft, "Operator", side_effect=AssertionError("allocation")):
        with pytest.raises(ValueError):
            ft.local_matrix(QuantumCircuit(6), ft.GraphLimits())


def test_qpy_phase_wires_counts_and_dependency_depth(tmp_path):
    circuit = QuantumCircuit(13, global_phase=0.27)
    circuit.t(12)
    circuit.tdg(1)
    circuit.cx(12, 1)
    circuit.t(1)
    with patch.object(ft, "Operator", side_effect=AssertionError("wide operator")):
        loaded, row = ft.save_circuit(
            tmp_path, "emitted", circuit, emitted=True, limits=ft.GraphLimits()
        )
    assert loaded == circuit
    assert row["metrics"]["t_count"] == 3
    assert row["metrics"]["t_depth"] == 2
    assert row["sha256"] == static_ft.sha256(tmp_path / "emitted.qpy")
    with pytest.raises(FileExistsError):
        ft.save_circuit(
            tmp_path, "emitted", circuit, emitted=True, limits=ft.GraphLimits()
        )


@pytest.mark.parametrize("fault", ["phase", "wire", "parameter"])
def test_qpy_corruption_rejects(tmp_path, fault):
    circuit = QuantumCircuit(2, global_phase=0.27)
    circuit.rz(0.31, 0)
    broken = QuantumCircuit(2, global_phase=0.27 + (0.1 if fault == "phase" else 0))
    broken.rz(0.32 if fault == "parameter" else 0.31, 1 if fault == "wire" else 0)
    with patch.object(ft.qpy, "load", return_value=[broken]):
        with pytest.raises(ValueError, match="readback failed"):
            ft.save_circuit(
                tmp_path, "bad", circuit, emitted=False, limits=ft.GraphLimits()
            )


def test_qpy_inverse_statepreparation_expands_definitions(tmp_path):
    circuit = QuantumCircuit(2, global_phase=0.37)
    circuit.append(StatePreparation([1 / math.sqrt(3)] * 3 + [0]), [0, 1])
    circuit = circuit.inverse()
    loaded, row = ft.save_circuit(
        tmp_path, "source", circuit, emitted=False, limits=ft.GraphLimits()
    )
    assert row["source_definitions_expanded"]
    assert (
        np.linalg.norm(
            ft.local_matrix(circuit, ft.GraphLimits())
            - ft.local_matrix(loaded, ft.GraphLimits()),
            2,
        )
        < 1e-13
    )


def test_sk_preflight_and_real_failure_keeps_original_contract():
    a = QuantumCircuit(4)
    a.rz(0.731, 0)
    o = QuantumCircuit(13)
    s = ft.zero_reflection(4, ft.GraphLimits())
    parts = dict(preparation=a, oracle=o, zero_reflection=s)
    pre = ft.sk_preflight(parts, 1, rotations.SynthesisOptions(), ft.GraphLimits())
    assert pre["weighted_rotation_occurrences"] == 24
    with pytest.raises(ValueError, match="estimated"):
        ft.sk_preflight(
            parts,
            1,
            rotations.SynthesisOptions(),
            replace(ft.GraphLimits(), operations=100),
        )
    with pytest.raises(rotations.PrecisionNotReachedError) as caught:
        rotations.compile_search(
            a,
            o,
            s,
            data_qubits=[12, 1, 7, 3],
            iterations=1,
            options=rotations.SynthesisOptions(
                max_recursion=0, basic_approximation_depth=1
            ),
        )
    assert caught.value.metadata["rotation_occurrences"] == 24
    assert caught.value.metadata["attempts"]


def test_failure_saved_without_fallback(tmp_path):
    failure = rotations.PrecisionNotReachedError("actual SK failed", {"attempts": [0]})
    with (
        patch.object(static_ft, "verify_admission", return_value={}),
        patch.object(ft, "build_components", side_effect=failure),
    ):
        directory = ft.run_case(
            Path(__file__).resolve().parents[1],
            Path("unused"),
            regime="R2",
            output_root=tmp_path,
        )
    row = json.loads((directory / "result.json").read_text())
    assert row["status"] == "failed"
    assert row["failure"]["trials"] == {"attempts": [0]}
    assert row["achieved_break_even"] is None
    assert row["input_graph"]["edges"] == [[7, 11]]
    assert not list(directory.glob("*.qpy"))


def test_no_break_even_from_missing_or_failed_rows():
    assert ft.compare_executed({}, {})["achieved_break_even"] is None


@pytest.mark.parametrize(
    "bad_request",
    [
        {"regime": "R4"},
        {"iterations": -1},
        {"iterations": 4},
        {"iterations": True},
        {"error_budget": True},
        {"error_budget": 0},
        {"error_budget": float("nan")},
        {"error_budget": 1e-13},
        {"options": None},
    ],
)
def test_invalid_request_rejects_before_native_or_arrays(tmp_path, bad_request):
    options = {"regime": "R2", "output_root": tmp_path, **bad_request}
    with (
        patch.object(
            ft, "build_components", side_effect=AssertionError("native/arrays")
        ),
        patch.object(
            static_ft,
            "verify_admission",
            side_effect=AssertionError("before preflight"),
        ),
    ):
        with pytest.raises(ValueError):
            ft.run_case(Path.cwd(), Path("unused"), **options)
    assert not list(tmp_path.iterdir())


def test_stronger_sk_rejects_before_synthesis_when_work_exceeds_cap(tmp_path):
    a = QuantumCircuit(4)
    o = QuantumCircuit(13)
    parts = dict(
        preparation=a,
        oracle=o,
        zero_reflection=ft.zero_reflection(4, ft.GraphLimits()),
        mapping=[0, 1, 2, 3],
    )
    with patch.object(
        rotations, "compile_search", side_effect=AssertionError("synthesis")
    ):
        with pytest.raises(ValueError, match="estimated operation/statevector"):
            ft.execute_case(
                tmp_path,
                parts,
                "R1",
                1,
                1e-4,
                ft.GraphLimits(),
                rotations.SynthesisOptions(max_recursion=6),
            )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("missing", ["preparation", "oracle", "zero_reflection"])
def test_active_search_components_cannot_be_unused(tmp_path, missing):
    circuit = QuantumCircuit(1)
    compiled = SimpleNamespace(
        preparation=rotations.CompiledComponent(circuit, {}),
        oracle=rotations.CompiledComponent(circuit, {}),
        zero_reflection=rotations.CompiledComponent(circuit, {}),
        preparation_inverse=circuit.inverse(),
        circuit=circuit,
        metadata={},
    )
    getattr(compiled, missing).circuit = None
    parts = dict(
        preparation=circuit,
        oracle=circuit,
        original_oracle=circuit,
        zero_reflection=circuit,
        mapping=[0],
    )
    with (
        patch.object(ft, "sk_preflight", return_value={}),
        patch.object(ft, "save_circuit", return_value=(circuit, {})),
        patch.object(rotations, "compile_search", return_value=compiled),
    ):
        with pytest.raises(ValueError, match="must emit|require emitted"):
            ft.execute_case(
                tmp_path,
                parts,
                "R1",
                1,
                1e-4,
                ft.GraphLimits(),
                rotations.SynthesisOptions(),
            )


@pytest.mark.parametrize("degree,depth", [(5, 12), (6, 11)])
def test_cli_passes_explicit_sk_options(tmp_path, degree, depth):
    (tmp_path / "result.json").write_text('{"status": "complete"}')
    with (
        patch(
            "sys.argv",
            [
                "graph_ft",
                "--executable",
                "unused",
                "--regime",
                "R2",
                "--error-budget",
                "0.0001",
                "--sk-max-recursion",
                str(degree),
                "--sk-basic-approximation-depth",
                str(depth),
            ],
        ),
        patch.object(ft, "run_case", return_value=tmp_path) as run,
    ):
        ft.main()
    assert run.call_args.kwargs["options"] == rotations.SynthesisOptions(
        max_recursion=degree, basic_approximation_depth=depth
    )
    assert run.call_args.kwargs["error_budget"] == 1e-4
