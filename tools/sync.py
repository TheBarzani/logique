"""Run uv sync with the submodule's bundled C++ headers, without editing it."""

import os
from pathlib import Path
import shlex
import subprocess
import sys
from uuid import uuid4


def preserve_relocated_build(root: Path) -> None:
    """Move tweedledum's stale absolute-path build cache into ignored dump/."""
    source = root / "external/tweedledum"
    build = source / "_skbuild"
    for cache in build.glob("*/cmake-build/CMakeCache.txt"):
        home = next(
            (
                line.removeprefix("CMAKE_HOME_DIRECTORY:INTERNAL=")
                for line in cache.read_text().splitlines()
                if line.startswith("CMAKE_HOME_DIRECTORY:INTERNAL=")
            ),
            None,
        )
        if home and Path(home).resolve() != source.resolve():
            destination = root / "dump/relocation" / f"tweedledum-build-{uuid4().hex}"
            destination.parent.mkdir(parents=True, exist_ok=True)
            build.rename(destination)
            print(f"Preserved relocated tweedledum build at {destination}", flush=True)
            return


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    external = root / "external/tweedledum/external"
    headers = {
        "fmt_INCLUDE_DIR": external / "fmt/include",
        "Eigen3_INCLUDE_DIR": external / "eigen",
        "nlohmann_json_INCLUDE_DIR": external / "nlohmann",
        "PHMAP_INCLUDE_DIR": external / "parallel_hashmap",
    }
    if any(not path.is_dir() for path in headers.values()):
        raise SystemExit(
            "Initialize dependencies first: git submodule update --init --recursive"
        )
    preserve_relocated_build(root)
    arguments = shlex.split(os.environ.get("CMAKE_ARGS", ""))
    arguments.extend(f"-D{name}={path}" for name, path in headers.items())
    environment = {
        **os.environ,
        "CMAKE_ARGS": shlex.join(arguments),
        "CMAKE_BUILD_PARALLEL_LEVEL": os.environ.get("CMAKE_BUILD_PARALLEL_LEVEL", "2"),
    }
    return subprocess.call(
        ["uv", "sync", "--locked", *sys.argv[1:]], cwd=root, env=environment
    )


if __name__ == "__main__":
    raise SystemExit(main())
