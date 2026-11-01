"""Prepare immutable remaining-request evidence; never launch an unreviewed retry.

After exact independent selector admission, the saved retry request can be used
with noisy_iterations --child under its admitted supervisor. This preparation
command performs scalar JSON/hash work only and never routes or samples.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess

from logique.benchmarks.noisy_iterations import (
    PILOT_HASH,
    selected_iterations,
    validate_config,
)
from logique.paths import new_dump_directory

NOISY_HASH = "f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278"
SEEDS = (11, 23, 37, 41, 53)
RETRY = ("K3_k3_R2", 37, 2)


def digest(path: Path) -> str:
    """Hash saved bytes without modifying them."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_manifest(root: Path, expected: str) -> dict:
    """Verify the frozen manifest and each explicitly bound evidence file."""
    if digest(root / "manifest.json") != expected:
        raise ValueError("Frozen manifest identity mismatch")
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected_digest in manifest["evidence_hashes"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or digest(path) != expected_digest:
            raise ValueError(f"Frozen evidence identity mismatch: {name}")
    return manifest


def remaining_ledger(ideal: dict, pilot: Path, noisy: Path) -> list[dict]:
    """Retain all analytical requests and subtract only admitted observations.

    Call only after verifying both frozen inventories. Old failures remain
    historical statuses; preparation never changes them to new measurements.
    """
    rows = []
    for case in ideal["cases"]:
        name = case["name"]
        reference = json.loads((pilot / name / "result.json").read_text())
        for seed in SEEDS:
            saved = noisy / f"{name}_seed{seed}" / "result.json"
            old = json.loads(saved.read_text()) if saved.exists() else {"rows": []}
            observed = {r["iterations"]: r for r in old["rows"]}
            for point in reference["analytical_ledger"]["rows"]:
                j = point["iterations"]
                previous = observed.get(j, {})
                status = previous.get("status", "not_executed")
                counts = previous.get("counts", {})
                complete = status == "complete" and sum(counts.values()) == 64
                key = (name, seed, j)
                if complete:
                    disposition = "admitted_observation_do_not_rerun"
                elif key == ("K3_k3_R2", 23, 2):
                    disposition = "excluded_21_active_wires"
                elif key == RETRY:
                    disposition = "blocked_pending_selector_review"
                elif reference["status"] == "infeasible":
                    disposition = "excluded_original_structure_width"
                else:
                    disposition = "unrun_requires_fresh_pre_aer_validation"
                rows.append(
                    {
                        "name": name,
                        "seed_transpiler": seed,
                        "iterations": j,
                        "analytical_prediction": point,
                        "historical_status": status,
                        "disposition": disposition,
                        "historical_result": str(saved) if saved.exists() else None,
                        "historical_result_sha256": (
                            digest(saved) if saved.exists() else None
                        ),
                    }
                )
    return rows


def prepare(config: dict, noisy: Path, root: Path = Path("dump")) -> Path:
    """Save the full805-minus28 ledger and exactly one unlaunched child request."""
    validate_config(config)
    if config["shots"] != 64 or config["execute"] != [RETRY[0]]:
        raise ValueError("Only the missing fixed64-shot K3 R2 retry is supported")
    pilot = Path(config["ideal_pilot"])
    ideal = verified_manifest(pilot, PILOT_HASH)
    verified_manifest(noisy, NOISY_HASH)
    rows = remaining_ledger(ideal, pilot, noisy)
    admitted = [
        r for r in rows if r["disposition"] == "admitted_observation_do_not_rerun"
    ]
    if len(rows) != 805 or len(admitted) != 28:
        raise ValueError("Expected frozen805 requests minus28 admitted observations")
    output = new_dump_directory("noisy-remaining-requests", root=root)
    request = {
        "config": config,
        "name": RETRY[0],
        "seed": RETRY[1],
        "iterations": [RETRY[2]],
        "output": str(output / "K3_k3_R2_seed37"),
    }
    reference = json.loads((pilot / RETRY[0] / "result.json").read_text())
    assert selected_iterations(request, reference) == [2]
    payloads = {
        "requested-ledger.json": rows,
        "remaining-ledger.json": [r for r in rows if r not in admitted],
        "retry-request.json": request,
        "checkpoint.json": {
            "task": "noisy-remaining-execute-1030020413",
            "session": os.environ.get("CODEX_THREAD_ID"),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "status": "BLOCK_sampling_pending_exact_selector_review",
            "scientific_admission": False,
            "requests": 805,
            "admitted_observations": 28,
            "remaining_requests": 777,
            "new_noisy_shots": 0,
            "dispositions": dict(Counter(r["disposition"] for r in rows)),
            "source_hashes": {
                str(p): digest(p)
                for p in (
                    Path(__file__).resolve(),
                    Path(__file__).resolve().parents[1]
                    / "src/logique/benchmarks/noisy_iterations.py",
                )
            },
            "input_manifests": {str(pilot): PILOT_HASH, str(noisy): NOISY_HASH},
            "next_action": "Independent exact selector review; then supervise only retry-request.json for120s,64shots. C5 requires a separately reviewed noisy adapter and fresh channel/layout/calibration validation.",
            "c5": "Ten best_fit ideal rows admitted by4fbf3d0; no downstream noise adapter admission. Historical structure22 exclusions retained; separate pilot lowering review pending.",
        },
    }
    for name, value in payloads.items():
        path = output / name
        with path.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
    return output


def main() -> None:
    """Prepare a new checkpoint without starting numerical children."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--admitted-noisy-run", type=Path, required=True)
    args = parser.parse_args()
    print(prepare(json.loads(args.config.read_text()), args.admitted_noisy_run))


if __name__ == "__main__":
    main()
