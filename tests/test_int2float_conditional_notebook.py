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
