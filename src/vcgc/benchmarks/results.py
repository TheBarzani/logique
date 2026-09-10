"""Shared readers for current runs and archived comparison tables."""

import json
from pathlib import Path


def load_results(path: str | Path):
    """Load a current CSV or normalize historical wide comparison metrics."""
    import pandas as pd

    path = Path(path)
    if path.is_dir():
        path = next(
            (
                path / name
                for name in (
                    "summary.csv",
                    "benchmark_results.csv",
                    "benchmark_results.json",
                )
                if (path / name).exists()
            ),
            path / "summary.csv",
        )
    if path.suffix == ".csv":
        frame = pd.read_csv(path)
    else:
        value = json.loads(path.read_text())
        if isinstance(value, dict):
            value = value.get("results", value)
        if isinstance(value, dict) and all(
            isinstance(row, dict) and "vcgc" in row for row in value.values()
        ):
            rows = []
            for name, row in value.items():
                methods = {
                    "vcgc": row["vcgc"],
                    **{
                        f"sb_{variant}": metrics
                        for variant, metrics in row.get("saha_belletti", {}).items()
                    },
                }
                rows.extend(
                    {
                        "benchmark": name,
                        "method": method,
                        "qubits": metrics["width"],
                        "depth": metrics["depth"],
                        "gates": metrics["gates"],
                        "metric_level": "historical",
                    }
                    for method, metrics in methods.items()
                )
            return pd.DataFrame(rows)
        if isinstance(value, dict):
            value = [{"benchmark": key, **row} for key, row in value.items()]
        frame = pd.json_normalize(value)
    if "method" in frame.columns:
        return frame
    prefixes = ["vcgc", "sb_original", "sb_simple", "sb_minimal", "sb_balanced"]
    rows = []
    for row in frame.to_dict("records"):
        for prefix in prefixes:
            width_key = (
                f"{prefix}_qubits" if f"{prefix}_qubits" in row else f"{prefix}_width"
            )
            if width_key in row:
                rows.append(
                    {
                        "benchmark": row.get(
                            "benchmark", row.get("filename", "unknown")
                        ),
                        "method": prefix,
                        "qubits": row[width_key],
                        "depth": row.get(f"{prefix}_depth"),
                        "gates": row.get(f"{prefix}_gates"),
                        "metric_level": "historical",
                    }
                )
    return pd.DataFrame(rows) if rows else frame
