"""Regression checks for the guarded int2float target relocations."""

import json
from pathlib import Path

import pytest


@pytest.mark.workflow
def test_int2float_conditional_workspace(tmp_path):
    """Execute exhaustive and coherent checks against the saved source network."""
    for dependency in (
        "qiskit",
        "numpy",
        "pandas",
        "matplotlib",
        "pylatexenc",
        "nbformat",
        "nbclient",
    ):
        pytest.importorskip(dependency)
    from logique.benchmarks.notebooks import execute_notebook

    root = Path(__file__).resolve().parents[1]
    source = root / "experiments/studies/int2float_conditional_workspace.ipynb"
    original = source.read_bytes()
    for cell in json.loads(original)["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == []
            assert cell["execution_count"] is None
    executed = execute_notebook(
        source, output=tmp_path / "run", offline=True, workspace=root
    )
    assert source.read_bytes() == original
    report = json.loads((executed.parent / "verification.json").read_text())
    assert report["selected_output"] == 3
    assert len(report["verification"]) == 7
    assert all(
        row["wrong_outputs"] == 0
        and row["input_and_scratch_restored"]
        and row["exact_phase"]
        for row in report["verification"]
    )
    assert len(report["statevector_checks"]) == 14
    resources = {row["circuit"]: row for row in report["resources"]}
    assert resources["ccx_reference"]["allocated_qubits"] == 19
    assert resources["borrow_q9"]["allocated_qubits"] == 18
    assert resources["borrow_q4_q9"]["allocated_qubits"] == 17
    assert resources["borrow_q12"]["allocated_qubits"] == 18
    assert resources["borrow_q12_q4_q9"]["allocated_qubits"] == 16
    assert resources["clean_reuse_q12"]["C3X"] == 0
    assert all(row["wrong_inputs"] > 0 for row in report["rejected_attempts"])
    assert (executed.parent / "borrow_q4_q9_circuit.svg").is_file()
    assert (executed.parent / "borrow_q4_q9.qpy").is_file()
    annotations = json.loads((executed.parent / "circuit_annotations.json").read_text())
    figure_cell = next(
        cell
        for cell in json.loads(executed.read_text())["cells"]
        if "def draw_annotated_circuit" in "".join(cell["source"])
    )
    assert sum(
        "image/png" in output.get("data", {}) for output in figure_cell["outputs"]
    ) == len(annotations)
    assert {row["circuit"] for row in annotations} == set(resources) - {
        "original_rotations"
    }
    for row in annotations:
        assert row["basis_columns_checked"] == 4096
        assert row["rendered_operations"] == resources[row["circuit"]]["operations"]
        assert row["allocated_qubits"] == resources[row["circuit"]]["allocated_qubits"]
        assert row["hidden_idle_wires"] == [0, 1]
        assert {0, 1}.isdisjoint(row["displayed_wires"])
        assert len(row["displayed_wires"]) == row["allocated_qubits"] - 2
        stages = row["stages"]
        assert stages[0]["start"] == 0
        assert stages[-1]["stop"] == row["rendered_operations"]
        for before, after in zip(stages, stages[1:]):
            assert before["stop"] == after["start"]
            assert before["out"] == after["in"]
        assert stages[0]["in"]["11"] == "y"
        assert stages[-1]["out"]["11"] == r"y\oplus f"
        assert stages[-2]["stage"] == "Uncompute"
        for wire, value in stages[-1]["out"].items():
            if int(wire) < 11:
                assert value == f"x_{{{wire}}}"
            elif int(wire) > 11:
                assert value == "0"
        for export in row["exports"]:
            assert (executed.parent / export).stat().st_size > 0
