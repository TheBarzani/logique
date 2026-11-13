"""Run serial, bounded checks against an explicitly supplied isolated checkout.

This task-specific harness records commands and terminal wait4 RSS. It does not
claim a hard process-group memory limit or scientific evidence admission.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def digest(path: Path) -> str:
    """Return the exact file digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: Path, output: Path, name: str) -> dict:
    """Supervise one serial child for at most 120 seconds and save its receipt."""
    receipt_path = output / f"{name}.receipt.json"
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    env = dict(os.environ)
    for key in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "RAYON_NUM_THREADS",
        "QISKIT_NUM_PROCS",
        "CMAKE_BUILD_PARALLEL_LEVEL",
    ):
        env[key] = "1"
    env.update(
        PYTHONPATH=str(cwd / "src"),
        QISKIT_PARALLEL="FALSE",
        MPLBACKEND="Agg",
        PYTHONDONTWRITEBYTECODE="1",
    )
    started = time.monotonic()
    status = "finished"
    with (output / f"{name}.log").open("x") as log:
        child = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        while True:
            pid, code, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - started >= 120:
                status = "timeout"
                os.killpg(child.pid, signal.SIGKILL)
                _, code, usage = os.wait4(child.pid, 0)
                break
            time.sleep(0.05)
    result = dict(
        command=command,
        cwd=str(cwd),
        status=status,
        exit=os.waitstatus_to_exitcode(code),
        seconds=time.monotonic() - started,
        wait4_high_water_bytes=usage.ru_maxrss,
        rss_scope="Darwin terminal child high-water; may include reaped descendants; no live group peak/hard cap",
        declared_process_bytes=6 * 1024**3,
    )
    receipt_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    """Run a saved command under the validation budget."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("name")
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()
    receipts = list(args.output.glob("*.receipt.json"))
    consumed = sum(json.loads(p.read_text())["seconds"] for p in receipts)
    if consumed + 120 > 900:
        raise RuntimeError("Insufficient remaining cumulative 900-second allowance")
    print(json.dumps(run(args.command, args.checkout, args.output, args.name)))


if __name__ == "__main__":
    main()
