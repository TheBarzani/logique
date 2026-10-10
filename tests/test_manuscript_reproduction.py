"""Prevent false success when historical evaluations or image comparisons differ."""

import importlib.util
import csv
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "reproduce_manuscript", ROOT / "tools/reproduce_manuscript.py"
)
reproduction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduction)


def test_metric_comparison_rejects_failures_and_missing_rows():
    reference = [{"benchmark": "K3", "vcgc_width": "11", "vcgc_depth": "30"}]
    assert reproduction.compare_metrics(reference, reference)["exact"]
    assert not reproduction.compare_metrics(reference, [])["exact"]
    assert not reproduction.compare_metrics(reference, reference * 2)["exact"]
    failed = [{"benchmark": "K3", "vcgc_width": "0", "vcgc_depth": "0"}]
    assert not reproduction.compare_metrics(reference, failed)["exact"]
    missing = [{"benchmark": "K3", "vcgc_width": "11"}]
    assert not reproduction.compare_metrics(reference, missing)["exact"]


def test_improvement_means_use_per_graph_relative_reduction():
    rows = []
    for baseline, proposed in ((10, 5), (100, 90)):
        row = {}
        for metric in reproduction.METRICS:
            row[f"vcgc_{metric}"] = proposed
            for method in reproduction.METHODS:
                row[f"sb_{method}_{metric}"] = baseline
        rows.append(row)
    result = reproduction.improvement_table(rows)
    assert result["overall_percent"] == {m: 30 for m in reproduction.METRICS}


def test_image_comparison_distinguishes_metadata_and_pixels(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image, PngImagePlugin

    reference = tmp_path / "reference.png"
    actual = tmp_path / "actual.png"
    preview = tmp_path / "comparison.png"
    image = Image.new("RGBA", (3, 3), "white")
    image.save(reference)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("test", "Different container, identical pixels")
    image.save(actual, pnginfo=metadata)
    result = reproduction.compare_image(reference, actual, preview)
    assert result["pixels_equal"] and not result["bytes_equal"]
    image.putpixel((1, 1), (255, 255, 255, 0))
    image.save(actual)
    assert not reproduction.compare_image(reference, actual, preview)["pixels_equal"]
    Image.new("RGBA", (4, 3), "white").save(actual)
    assert not reproduction.compare_image(reference, actual, preview)["pixels_equal"]


def test_validation_exports_each_metric_and_fresh_improvements(tmp_path, monkeypatch):
    reference_directory = tmp_path / "legacy/data/output"
    reference_directory.mkdir(parents=True)
    actual_directory = tmp_path / "generated"
    actual_directory.mkdir()
    row = {"benchmark": "test"}
    for metric in reproduction.METRICS:
        row[f"vcgc_{metric}"] = 50
        for method in reproduction.METHODS:
            row[f"sb_{method}_{metric}"] = 100
    for directory in (reference_directory, actual_directory):
        with (directory / "benchmark_results.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
    monkeypatch.setattr(reproduction, "LEGACY", tmp_path / "legacy")
    report = reproduction.validate_evaluation(actual_directory, tmp_path)
    assert report["metric_values_compared"] == report["metric_values_matching"] == 15
    assert report["exact"]
    assert report["regenerated_improvements"]["overall_percent"] == {
        metric: 50 for metric in reproduction.METRICS
    }
    comparison = reproduction.read_rows(tmp_path / "metric-comparison.csv")
    assert len(comparison) == 15
    assert all(float(row["delta"]) == 0 for row in comparison)


def test_all_stage_plots_regenerated_csv(tmp_path, monkeypatch):
    output = tmp_path / "run"
    monkeypatch.setattr(
        sys, "argv", ["reproduce_manuscript.py", "--output", str(output)]
    )
    monkeypatch.setattr(reproduction, "audit", lambda manuscript: {})

    def evaluate(directory, environment):
        generated = directory / "evaluation"
        generated.mkdir()
        (generated / "benchmark_results.csv").write_text("fresh evaluation")
        return {"status": "exact"}

    def plots(directory, *, figure_dpi, benchmark_csv):
        assert benchmark_csv == directory / "evaluation/benchmark_results.csv"
        assert benchmark_csv.read_text() == "fresh evaluation"
        return {"images": {}}

    monkeypatch.setattr(reproduction, "evaluate", evaluate)
    monkeypatch.setattr(reproduction, "plots", plots)
    assert reproduction.main() == 0
    assert "plots" in json.loads((output / "report.json").read_text())
