"""Portable QPY circuits with lossless synthesis metadata."""

from pathlib import Path
import json


def export_result(result, directory, name):
    """Save QPY circuits and JSON metadata without flattening high-control gates."""
    from qiskit import qpy

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / f"{name}.qpy").open("wb") as stream:
        qpy.dump([result.circuit, result.oracle()], stream)
    (directory / f"{name}.json").write_text(
        json.dumps(result.metadata, indent=2) + "\n"
    )
