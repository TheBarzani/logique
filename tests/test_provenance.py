"""Build metadata must describe the executable instead of a source constant."""

import json

from logique.benchmarks.provenance import environment


def test_environment_reads_selected_native_build(tmp_path):
    executable = tmp_path / "bridge"
    executable.write_text("a local executable")
    (tmp_path / "build_provenance.json").write_text(
        json.dumps(
            {"declared_reference_revision": "test-build-revision", "fixes": ["fix"]}
        )
    )
    versions = environment(executable=executable)
    assert versions["caterpillar"] == "test-build-revision"
    assert versions["bridge_fixes"] == ["fix"]


def test_environment_does_not_invent_missing_build_provenance(tmp_path):
    executable = tmp_path / "bridge"
    executable.write_text("a local executable")
    assert environment(executable=executable)["caterpillar"] == "not recorded"
    assert environment(executable=tmp_path / "missing")["caterpillar"] == "not recorded"
