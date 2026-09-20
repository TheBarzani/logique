"""Execute the screenshot borrowing study without changing its source."""

import json
from pathlib import Path

import pytest


@pytest.mark.workflow
def test_guarded_phase_notebook(tmp_path):
    """Verify targets, phases, restoration, and deliberate failure cases offline."""
    pytest.importorskip("qiskit")
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    pytest.importorskip("pylatexenc")
    pytest.importorskip("nbformat")
    pytest.importorskip("nbclient")
    from logique.benchmarks.notebooks import execute_notebook

    root = Path(__file__).resolve().parents[1]
    source = root / "notebooks/studies/guarded_phase_oracle_two_ancillas.ipynb"
    original = source.read_bytes()
    for cell in json.loads(original)["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == []
            assert cell["execution_count"] is None
    executed = execute_notebook(
        source, output=tmp_path / "run", offline=True, workspace=root
    )
    assert source.read_bytes() == original
    summary = json.loads((executed.parent / "verification.json").read_text())
    assert len(summary["basis_verification"]) == 4
    assert all(
        row["phase_and_restoration"] == "PASS" for row in summary["basis_verification"]
    )
    assert len(summary["coherent_verification"]) == 8
    assert all(row["wrong_phase_inputs"] > 0 for row in summary["negative_checks"])
    figures = executed.parent / "annotated_circuits/screenshots"
    assert (figures / "reference_annotated.png").is_file()
    assert (figures / "reference_annotated.svg").is_file()
