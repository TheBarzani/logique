"""Prevent false success when historical evaluations or image comparisons differ."""

import importlib.util
from pathlib import Path

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
