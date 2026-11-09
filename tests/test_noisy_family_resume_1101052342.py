"""Resume guards prevent scientific histograms and failed attempts from replay."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "family_runner", Path(__file__).parents[1] / "tools/run_noisy_family_1101052342.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def row(status, **extra):
    return dict(
        name="path7_k2_R1", seed_transpiler=11, iterations=2, status=status, **extra
    )


@pytest.mark.parametrize(
    "status",
    [
        "complete",
        "timeout",
        "failed",
        "interrupted_scope_stop",
        "compact_noise_infeasible",
    ],
)
def test_attempted_requests_never_reopen(status):
    current = [row("unrun_requires_fresh_pre_aer_validation")]
    saved = row(status, result="preserved/result.json")
    runner.resume_ledger(current, [saved])
    assert current == [saved]


def test_only_unattempted_budget_rows_reopen():
    current = [row("unrun_requires_fresh_pre_aer_validation")]
    runner.resume_ledger(current, [row("not_launched_budget")])
    assert current[0]["status"] == "unrun_requires_fresh_pre_aer_validation"
    assert current[0]["previous_status"] == "not_launched_budget"
    with pytest.raises(ValueError, match="attempted result"):
        runner.resume_ledger(current, [row("not_launched_budget", result="saved.json")])


def test_duplicate_or_changed_request_set_rejected():
    current = [row("unrun_requires_fresh_pre_aer_validation")]
    with pytest.raises(ValueError, match="unique request"):
        runner.resume_ledger(current, [row("complete"), row("complete")])
    with pytest.raises(ValueError, match="unique request"):
        runner.resume_ledger(current, [dict(row("complete"), iterations=3)])
