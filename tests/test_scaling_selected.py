"""Selected source ledger integration; no compiler is invoked."""

from pathlib import Path
import json
import runpy

from logique.benchmarks.scaling_inputs import bounded_dimacs

ROOT = Path(__file__).parents[1]


def test_selected_preparation_retains_all_cases_and_zero_compiler_calls(tmp_path):
    prepare = runpy.run_path(str(ROOT / "tools/prepare_selected_scaling.py"))["prepare"]
    output = prepare(ROOT / "configs/coloring_scaling_selected.json", tmp_path)
    ledger = json.loads((output / "ledger.json").read_text())
    assert ledger["native_attempts"] == 0
    assert len(ledger["rows"]) == 10
    assert len(ledger["planned_attempts"]) == 220
    assert all(
        a["status"] == "blocked_admission_not_launched"
        for a in ledger["planned_attempts"]
    )
    for row in ledger["rows"]:
        assert row["input_status"] == "prepared_unprecolored"
        if row["witness"] is not None:
            witness = {int(v): c for v, c in row["witness"].items()}
            assert bounded_dimacs(row["prepared_path"], row["colors"]).is_valid(witness)
        else:
            assert row["name"] in ("DSJC125.1", "le450_5a")
            assert row["witness_status"] == "unknown"
