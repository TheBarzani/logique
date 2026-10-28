"""Export existing bridge timers without running or admitting synthesis evidence."""

import argparse
import hashlib
import json
import math
from pathlib import Path


BRIDGE_SCOPE = (
    "main.cpp native_seconds: after stdin JSON decoding; source read/parse, output "
    "selection, preprocessing, representation conversion, mapping, graph/gate/action "
    "JSON construction; stops before final result.dump() and stdout write"
)


def _seconds(value: float | int | None) -> float | int | None:
    if value is None:
        return None
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ValueError("timer must be finite nonnegative seconds or null")
    return value


def timer_fields(response: dict | None, process: dict) -> dict:
    """Keep combined bridge time separate from enclosing boundary observation.

    Their difference is an aggregate residual, not a measured polling or cleanup
    stage. No disjoint optimization/mapping timers exist in this bridge.
    """
    combined = _seconds(response.get("native_seconds")) if response else None
    boundary = _seconds(process.get("wall_seconds"))
    return {
        "native_combined_seconds": combined,
        "native_combined_scope": BRIDGE_SCOPE,
        "boundary_wall_seconds": boundary,
        "boundary_scope": "process setup through observation and cleanup; overlaps bridge",
        "boundary_minus_bridge_seconds": (
            boundary - combined
            if boundary is not None and combined is not None and boundary >= combined
            else None
        ),
        "residual_scope": (
            "aggregate difference only: setup, stdin JSON decode, final dump/write, "
            "transport, polling/observation and cleanup; no disjoint measurement"
        ),
        "optimization_seconds": None,
        "mapping_seconds": None,
        "lowering_seconds": None,
        "polling_seconds": None,
        "cleanup_seconds": None,
    }


def export_saved_timers(manifest: str | Path, output: str | Path) -> dict:
    """Verify referenced response hashes and export all rows to a fresh file.

    Historical statuses and resource labels are retained verbatim, with an
    explicit warning that this export cannot repair their admission blockers.
    """
    manifest = Path(manifest).resolve()
    if manifest.stat().st_size > 16 * 1024**2:
        raise ValueError("manifest exceeds 16 MiB")
    data = manifest.read_bytes()
    run = json.loads(data)
    rows = []
    for row in run["rows"]:
        artifact = row.get("response")
        response = None
        if artifact:
            path = (manifest.parent / artifact["path"]).resolve()
            if path.parent != manifest.parent or path.stat().st_size > 64 * 1024**2:
                raise ValueError("response outside run directory or exceeds 64 MiB")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != artifact["sha256"]:
                raise ValueError("saved response SHA256 mismatch")
            response = json.loads(raw)
        rows.append(
            {
                **{
                    k: row.get(k)
                    for k in ("case", "method", "profile", "repetition", "status")
                },
                "response": artifact,
                "historical_process": row.get("process", {}),
                "times": timer_fields(response, row.get("process", {})),
            }
        )
    result = {
        "schema_version": 1,
        "source_manifest": str(manifest),
        "source_manifest_sha256": hashlib.sha256(data).hexdigest(),
        "scope": "read-only metadata export; historical process/resource blockers remain; no admission",
        "rows": rows,
    }
    with Path(output).open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return result


def main() -> None:
    """Export a supplied saved manifest; never launch the native executable."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    export_saved_timers(args.manifest, args.output)


if __name__ == "__main__":
    main()
