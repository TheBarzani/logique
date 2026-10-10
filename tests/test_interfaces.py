"""Minimal imports, explicit paths, and CLI failure contracts."""

import json
import subprocess
import sys
import pytest
from logique.cli.main import main
from logique.paths import native_executable
from logique.benchmarks.runner import load_config, new_run_directory


def test_minimal_import_does_not_load_optional_stacks(tmp_path):
    code = "import sys, logique; from logique.cli.main import parser; parser(); assert not any(m in sys.modules for m in ['qiskit','tweedledum','matplotlib','pandas','qiskit_ibm_runtime'])"
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)
    subprocess.run(
        [sys.executable, "-m", "logique", "--help"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )


def test_native_resolution_is_explicit(tmp_path, monkeypatch):
    path = tmp_path / "bridge"
    path.write_text("test")
    monkeypatch.setenv("LOGIQUE_NATIVE_EXECUTABLE", str(path))
    assert native_executable() == path
    with pytest.raises(FileNotFoundError):
        native_executable(tmp_path / "missing")


def test_config_paths_and_overrides(tmp_path):
    config = tmp_path / "run.json"
    config.write_text(
        json.dumps({"inputs": ["input.v"], "methods": ["xag"], "output": "output"})
    )
    result = load_config(config, methods=["aig_bennett"], seed=11)
    assert result["inputs"] == [str(tmp_path / "input.v")]
    assert result["output"] == str(tmp_path / "output")
    assert result["methods"] == ["aig_bennett"]
    assert result["seed"] == 11
    config.write_text('{"inputs":["x.v"],"typo":1}')
    with pytest.raises(ValueError, match="Unknown"):
        load_config(config)


def test_run_directory_never_overwrites(tmp_path):
    output = new_run_directory(tmp_path / "run")
    (output / "important.txt").write_text("preserve")
    with pytest.raises(FileExistsError):
        new_run_directory(output)
    assert (output / "important.txt").read_text() == "preserve"


def test_default_runs_use_unique_dump_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = new_run_directory()
    (first / "important.txt").write_text("preserve")
    second = new_run_directory()
    assert first.parent == second.parent == tmp_path / "dump"
    assert first != second
    assert (first / "important.txt").read_text() == "preserve"
    assert not (tmp_path / "results").exists()


def test_missing_native_helper_points_to_relocated_source(monkeypatch):
    monkeypatch.delenv("LOGIQUE_NATIVE_EXECUTABLE", raising=False)
    monkeypatch.setattr("logique.paths.shutil.which", lambda name: None)
    with pytest.raises(FileNotFoundError, match="external/native/boolean_synthesis"):
        native_executable()


def test_cli_offline_failure_is_actionable(tmp_path, capsys):
    assert (
        main(["datasets", "fetch", "ctrl", "--offline", "--cache", str(tmp_path)]) == 1
    )
    assert "Offline cache missing" in capsys.readouterr().err
