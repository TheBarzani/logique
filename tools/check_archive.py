"""Verify that every indexed historical artifact still has its original bytes."""

import hashlib
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root / "archive/index.json").read_text())["files"]
    failures = []
    for record in records:
        path = root / record["path"]
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]
        ):
            failures.append(record["path"])
    if failures:
        raise SystemExit("Archive integrity failure: " + ", ".join(failures))
    print(f"Verified {len(records)} historical artifacts")


if __name__ == "__main__":
    main()
