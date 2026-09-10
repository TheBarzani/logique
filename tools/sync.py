"""Run uv sync with the submodule's bundled C++ headers, without editing it."""

import os
from pathlib import Path
import shlex
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    external = root / "tweedledum/external"
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
