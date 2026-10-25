"""Dependency and checkout provenance without mandatory optional imports."""

import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
from logique.paths import native_executable


def environment(*, executable: str | Path | None = None) -> dict:
    """Record versions and the bridge's build declaration when available.

    The reference revision describes the dependency declared by that build, not
    a verification of its checkout. Source hashes remain in native_provenance().
    Missing build records never imply that the reference sources were used.
    """
    try:
        build = native_provenance(executable)["build"] or {}
    except FileNotFoundError:
        build = {}
    versions = {
        "python": platform.python_version(),
        "caterpillar": build.get("declared_reference_revision", "not recorded"),
        "caterpillar_revision_kind": "declared build reference",
        "bridge_fixes": build.get("fixes", "not recorded"),
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


def native_provenance(executable: str | Path | None = None) -> dict:
    """Identify the native executable and the build record written beside it."""
    tool = native_executable(executable)
    build_info = tool.parent / "build_provenance.json"
    return {
        "executable": str(tool),
        "sha256": hashlib.sha256(tool.read_bytes()).hexdigest(),
        "build": json.loads(build_info.read_text()) if build_info.exists() else None,
    }


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
