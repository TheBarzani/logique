"""Explicit, working-directory-independent paths for native tools and caches."""

import os
import shutil
from pathlib import Path


def cache_directory(cache: str | Path | None = None) -> Path:
    """Return the chosen cache without creating it or downloading anything."""
    value = cache if cache is not None else os.environ.get("LOGIQUE_CACHE")
    return (
        Path(value if value is not None else Path.home() / ".cache/logique/epfl")
        .expanduser()
        .resolve()
    )


def native_executable(executable: str | Path | None = None) -> Path:
    """Resolve an explicit executable, environment setting, or PATH entry."""
    value = (
        executable
        or os.environ.get("LOGIQUE_NATIVE_EXECUTABLE")
        or shutil.which("boolean_synthesis")
    )
    if value is None or not Path(value).expanduser().is_file():
        raise FileNotFoundError(
            "Native helper missing. Run logique native build --source native/boolean_synthesis; set LOGIQUE_NATIVE_EXECUTABLE to the resulting executable."
        )
    return Path(value).expanduser().resolve()
