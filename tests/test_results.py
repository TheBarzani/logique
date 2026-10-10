"""Historical comparison formats remain readable using small local fixtures."""

import json
import pytest


def test_historical_csv_and_json_agree(tmp_path):
    pytest.importorskip("pandas")
    from logique.benchmarks.results import load_results

    csv_path = tmp_path / "benchmark_results.csv"
    csv_path.write_text(
        "benchmark,vcgc_width,vcgc_depth,vcgc_gates,"
        "sb_original_qubits,sb_original_depth,sb_original_gates\n"
        "edge,3,5,7,4,6,8\n"
    )
    json_path = tmp_path / "benchmark_results.json"
    json_path.write_text(
        json.dumps(
            {
                "results": {
                    "edge": {
                        "vcgc": {"width": 3, "depth": 5, "gates": 7},
                        "saha_belletti": {
                            "original": {"width": 4, "depth": 6, "gates": 8}
                        },
                    },
                    "grid6": {"vcgc": {"width": 9, "depth": 10, "gates": 11}},
                }
            }
        )
    )
    csv = load_results(csv_path)
    structured = load_results(json_path)
    columns = ["benchmark", "method", "qubits", "depth", "gates"]

    def canonical(frame):
        return (
            frame[columns].sort_values(["benchmark", "method"]).reset_index(drop=True)
        )

    assert set(csv.method) == {"logique", "sb_original"}
    assert set(csv.metric_level) == {"historical"}
    assert set(structured.metric_level) == {"historical"}
    assert set(structured.benchmark) - set(csv.benchmark) == {"grid6"}
    shared = structured[structured.benchmark.isin(csv.benchmark)]
    assert canonical(csv).equals(canonical(shared))
    # Directory loading still discovers a historical table without an archive.
    assert canonical(load_results(tmp_path)).equals(canonical(csv))
