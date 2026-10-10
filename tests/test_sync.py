"""Relocating dependencies preserves stale builds and allows a fresh sync."""

from pathlib import Path
import runpy

import pytest


@pytest.mark.parametrize("relocated", [False, True])
def test_sync_preserves_only_relocated_builds(tmp_path, relocated):
    source = tmp_path / "external/tweedledum"
    build = source / "_skbuild"
    cache = build / "platform/cmake-build/CMakeCache.txt"
    cache.parent.mkdir(parents=True)
    original_source = tmp_path / "tweedledum" if relocated else source
    cache.write_text(f"CMAKE_HOME_DIRECTORY:INTERNAL={original_source}\n")
    (build / "previous-result.txt").write_text("preserve")
    original = cache.read_bytes()
    sync = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/sync.py"))
    preserve = sync["preserve_relocated_build"]
    preserve(tmp_path)
    if relocated:
        assert not build.exists()
        backups = list((tmp_path / "dump/relocation").iterdir())
        assert len(backups) == 1
        assert (backups[0] / cache.relative_to(build)).read_bytes() == original
        assert (backups[0] / "previous-result.txt").read_text() == "preserve"
        # Repeating setup before the rebuild does not move or lose the backup.
        preserve(tmp_path)
        assert list((tmp_path / "dump/relocation").iterdir()) == backups
    else:
        assert cache.read_bytes() == original
        assert not (tmp_path / "dump").exists()
