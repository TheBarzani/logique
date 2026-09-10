"""Dependency and checkout provenance without mandatory optional imports."""

import importlib.metadata
import platform
from pathlib import Path
import subprocess
from logique.synthesis.native import REFERENCE_REVISION


def environment() -> dict:
    """Record installed versions; absent optional packages are explicit."""
    versions = {
        "python": platform.python_version(),
        "caterpillar": REFERENCE_REVISION,
        "bridge_fixes": "lhrs_uncompute_stack_pop, best_fit_cell_fanout",
    }
    for name in (
        "logique",
        "qiskit",
        "tweedledum",
        "numpy",
        "saha-belleti",
        "qiskit-ibm-runtime",
    ):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def checkout_revision(directory: str | Path) -> dict:
    """Identify a supplied checkout; installed wheels need no Git repository."""
    directory = Path(directory)
    try:
        revision = subprocess.check_output(
            ["git", "-C", str(directory), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        dirty = bool(
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(directory),
                    "status",
                    "--porcelain",
                    "--untracked-files=no",
                ],
                text=True,
            )
        )
        submodules = (
            subprocess.check_output(
                ["git", "-C", str(directory), "submodule", "status"], text=True
            )
            .strip()
            .splitlines()
        )
        return {"revision": revision, "dirty": dirty, "submodules": submodules}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"revision": None}
