"""Maintained notebook sources and isolated execution contracts."""

import ast
import json
from pathlib import Path
import pytest


def test_maintained_sources_are_unexecuted_and_parse():
    root = Path(__file__).resolve().parents[1]
    notebooks = list((root / "notebooks").rglob("*.ipynb"))
    required = {
        "tutorials/graph_coloring.ipynb",
        "tutorials/boolean_workspace.ipynb",
        "studies/boolean_visual_study.ipynb",
        "studies/coloring_comparison.ipynb",
        "studies/guarded_phase_oracle_two_ancillas.ipynb",
        "studies/int2float_conditional_workspace.ipynb",
    }
    assert required <= {
        path.relative_to(root / "notebooks").as_posix() for path in notebooks
    }
    for path in notebooks:
        for cell in json.loads(path.read_text())["cells"]:
            if cell["cell_type"] == "code":
                assert cell["outputs"] == []
                assert cell["execution_count"] is None
                source = "".join(cell["source"])
                ast.parse(source)
                assert "sys.path.insert" not in source
                assert "build_native(" not in source


def test_notebook_runner_keeps_source_and_records_failure(tmp_path):
    nbformat = pytest.importorskip("nbformat")
    pytest.importorskip("nbclient")
    from nbclient.exceptions import CellExecutionError
    from logique.benchmarks.notebooks import execute_notebook

    source = tmp_path / "example.ipynb"
    nbformat.write(
        nbformat.v4.new_notebook(
            cells=[nbformat.v4.new_code_cell("raise ValueError('expected failure')")]
        ),
        source,
    )
    original = source.read_bytes()
    output = tmp_path / "run"
    with pytest.raises(CellExecutionError):
        execute_notebook(source, output=output, offline=True, workspace=tmp_path)
    assert source.read_bytes() == original
    assert json.loads((output / "run.json").read_text())["status"] == "failed"
    assert (output / "example_executed.ipynb").is_file()
