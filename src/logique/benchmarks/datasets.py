"""Pinned EPFL benchmark acquisition and integrity-checked offline use."""

import hashlib
from importlib.resources import files
import json
from pathlib import Path
import urllib.request
from logique.paths import cache_directory


def benchmark_manifest() -> dict:
    """Read the manifest bundled in the installed package."""
    return json.loads(files("logique.benchmarks").joinpath("epfl.json").read_text())


def download_benchmarks(
    names=("ctrl", "int2float", "cavlc"), *, offline=False, cache=None
) -> dict[str, Path]:
    """Fetch pinned inputs and license, verifying hashes on every use."""
    manifest = benchmark_manifest()
    cache = cache_directory(cache)
    names = tuple(names)
    if not names or not set(names) <= {"ctrl", "int2float", "cavlc", "router"}:
        raise ValueError("Choose ctrl, int2float, cavlc, or router")
    paths = [f"random_control/{name}{ext}" for name in names for ext in (".aig", ".v")]
    for relative in ["LICENSE", *paths]:
        target = cache / relative
        if target.exists():
            payload = target.read_bytes()
        else:
            if offline:
                raise FileNotFoundError(
                    f"Offline cache missing {target}; run logique datasets fetch online once"
                )
            url = f"https://raw.githubusercontent.com/lsils/benchmarks/{manifest['revision']}/{relative}"
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read()
        if hashlib.sha256(payload).hexdigest() != manifest["sha256"][relative]:
            raise ValueError(f"Checksum mismatch: {target}")
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    return {name: cache / "random_control" / f"{name}.aig" for name in names}
