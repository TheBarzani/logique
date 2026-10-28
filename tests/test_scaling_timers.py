import hashlib
import json

import pytest

from logique.benchmarks.scaling_timers import export_saved_timers, timer_fields


def test_timer_scopes_and_missing_values():
    fields = timer_fields({"native_seconds": 0.125}, {"wall_seconds": 0.2})
    assert fields["native_combined_seconds"] == 0.125
    assert fields["boundary_minus_bridge_seconds"] == pytest.approx(0.075)
    assert fields["optimization_seconds"] is fields["mapping_seconds"] is None
    assert fields["cleanup_seconds"] is fields["polling_seconds"] is None
    assert timer_fields(None, {})["native_combined_seconds"] is None
    assert (
        timer_fields({"native_seconds": 2}, {"wall_seconds": 1})[
            "boundary_minus_bridge_seconds"
        ]
        is None
    )


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, "1"])
def test_invalid_timer_is_never_coerced(value):
    with pytest.raises(ValueError):
        timer_fields({"native_seconds": value}, {})


def test_saved_response_hash_checked_and_failure_rows_retained(tmp_path):
    response = tmp_path / "response.json"
    response.write_text('{"native_seconds": 0.125}')
    manifest = tmp_path / "run.json"
    manifest.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "case": "large",
                        "status": "ok",
                        "process": {"wall_seconds": 0.3},
                        "response": {
                            "path": response.name,
                            "sha256": hashlib.sha256(response.read_bytes()).hexdigest(),
                        },
                    },
                    {"case": "missing", "status": "missing_input"},
                ]
            }
        )
    )
    original = manifest.read_bytes()
    output = tmp_path / "timers.json"
    exported = export_saved_timers(manifest, output)
    assert len(exported["rows"]) == 2
    assert exported["rows"][1]["times"]["native_combined_seconds"] is None
    assert manifest.read_bytes() == original
    with pytest.raises(FileExistsError):
        export_saved_timers(manifest, output)
    response.write_text('{"native_seconds": 999}')
    with pytest.raises(ValueError, match="SHA256"):
        export_saved_timers(manifest, tmp_path / "bad.json")
