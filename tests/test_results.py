"""Historical data remains readable without changing its original bytes."""

from pathlib import Path
import json
import hashlib
import pytest


def test_archive_hashes():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "archive/index.json").read_text())
    for record in manifest["files"]:
        assert (
            hashlib.sha256((root / record["path"]).read_bytes()).hexdigest()
            == record["sha256"]
        ), record["path"]


def test_historical_csv_and_json_agree():
    pytest.importorskip("pandas")
    from vcgc.benchmarks.results import load_results

    root = Path(__file__).resolve().parents[1] / "archive/research/data/output"
    csv = load_results(root / "benchmark_results.csv")
    structured = load_results(root / "benchmark_results.json")
    columns = ["benchmark", "method", "qubits", "depth", "gates"]

    def canonical(frame):
        return (
            frame[columns].sort_values(["benchmark", "method"]).reset_index(drop=True)
        )

    # The historical JSON includes grid6, which is absent from the CSV.
    assert set(structured.benchmark) - set(csv.benchmark) == {"grid6"}
    shared = structured[structured.benchmark.isin(csv.benchmark)]
    assert canonical(csv).equals(canonical(shared))
