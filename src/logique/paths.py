"""Paths for timestamped dumps, native tools, and caches."""

from datetime import datetime
import os
from pathlib import Path
import re
import shutil


def dump_directory_name(description: str, *, when: datetime | None = None) -> str:
    """Name a dump using local MMDDHHMMSS time and a descriptive slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", description.lower()).strip("-")
    if not slug:
        raise ValueError("A dump requires a descriptive name")
    timestamp = (when or datetime.now()).astimezone()
    return f"{timestamp:%m%d%H%M%S}-{slug}"


def new_dump_directory(
    description: str, *, root: str | Path = "dump", when: datetime | None = None
) -> Path:
    """Create a timestamped dump, adding a numeric suffix for name collisions."""
    name = dump_directory_name(description, when=when)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        path = root / (name if index == 1 else f"{name}-{index}")
        try:
            path.mkdir()
        except FileExistsError:
            index += 1
        else:
            return path.resolve()


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
            "Native helper missing. Run logique native build --source external/native/boolean_synthesis; set LOGIQUE_NATIVE_EXECUTABLE to the resulting executable."
        )
    return Path(value).expanduser().resolve()
