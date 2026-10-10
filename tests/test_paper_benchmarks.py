"""Exercise the maintained paper pipeline on the unprecolored triangle."""

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
def test_paper_pipeline_uses_the_same_unprecolored_problem(tmp_path, monkeypatch):
    pd = pytest.importorskip("pandas")
    qiskit = pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    pytest.importorskip("saha_belletti")
    from logique.paths import native_executable

    try:
        executable = native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for paper benchmarks")
    if (
        "mcx_decomposition"
        not in inspect.signature(qiskit.QuantumCircuit.depth).parameters
    ):
        pytest.skip("Install the manuscript MCX depth patch")
    monkeypatch.setenv("LOGIQUE_NATIVE_EXECUTABLE", str(executable))
    spec = importlib.util.spec_from_file_location(
        "paper_benchmarks", ROOT / "tools/generate_paper_benchmarks.py"
    )
    paper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(paper)
    observed = []
    original_adapter = paper.comparison_circuit

    def comparison(problem, variant, *, iterations):
        assert not problem.precolored
        assert iterations == 1
        observed.append(variant)
        return original_adapter(problem, variant, iterations=iterations)

    monkeypatch.setattr(paper, "comparison_circuit", comparison)
    output = paper.generate(tmp_path / "run", ["K3"])
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["implementation"] == "src/logique"
    assert observed == ["original", "minimal", "simple", "balanced"]
    phase = manifest["cases"][0]
    assert phase["removed_precolors"] == {"1": 0}
    assert phase["status"] == "exhaustive"
    assert phase["assignments"] == 64 and phase["marked_assignments"] == 6
    assert phase["phase_exact"] and phase["workspace_restored"]
    assert len(list(output.glob("*.qasm"))) == 5
    assert (output / "K3.v").exists()
    current = pd.read_csv(output / "benchmark_results.csv").set_index("benchmark")
    reference = pd.read_csv(paper.REFERENCE).set_index("benchmark")
    comparison = pd.read_csv(output / "comparison.csv")
    assert len(comparison) == 15
    for row in comparison.itertuples():
        assert row.new == current.loc["K3", row.metric]
        assert row.old == reference.loc["K3", row.metric]
        assert row.delta == row.new - row.old
        assert row.exact == (row.delta == 0)
