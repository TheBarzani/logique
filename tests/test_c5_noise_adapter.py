"""Focused identity, selector, physical-layout and no-rebuild regressions."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from logique.benchmarks import c5_noise_adapter as adapter
from logique.benchmarks import noisy_iterations as noisy


def config():
    return json.loads(Path("configs/c5_best_fit_noise_adapter.json").read_text())


def test_legacy_runner_rejects_distinct_best_fit_manifest():
    with pytest.raises(ValueError, match="exact admitted ideal pilot"):
        noisy.validate_config(config())


def test_bad_inventory_rejected_before_qpy(tmp_path):
    (tmp_path / "manifest.json").write_text("{}")
    settings = config()
    settings["ideal_pilot"] = str(tmp_path)
    with pytest.raises(ValueError, match="manifest identity"):
        adapter.load_source(settings, "R1")


@pytest.mark.parametrize(
    "regime,seed,j", [("R3", 11, 0), ("R1", True, 0), ("R2", 11, 4)]
)
def test_identity_rejects_unadmitted_scope(regime, seed, j):
    with pytest.raises(ValueError):
        adapter.request_identity(regime, seed, j)


def test_fifty_new_identities_are_unique():
    identities = {
        adapter.request_identity(regime, seed, j)
        for regime, rows in (("R1", 6), ("R2", 4))
        for seed in adapter.SEEDS
        for j in range(rows)
    }
    assert len(identities) == 50
    assert all(adapter.SOURCE_KIND in identity for identity in identities)


def channel_snapshot():
    """Use ordered, noncommuting branches, complex matrices and asymmetric readout."""
    return {
        "errors": [
            {
                "type": "qerror",
                "id": "saved-uuid",
                "operations": ["cz"],
                "gate_qubits": [[3, 1]],
                "probabilities": [0.25, 0.75],
                "instructions": [
                    [{"name": "x", "qubits": [1]}, {"name": "z", "qubits": [1]}],
                    [
                        {
                            "name": "unitary",
                            "qubits": [0],
                            "params": [
                                [[[0.0, 1.0], [0.0, 0.0]], [[0.0, 0.0], [1.0, 0.0]]]
                            ],
                        }
                    ],
                ],
            },
            {
                "type": "qerror",
                "id": "another-uuid",
                "operations": ["x"],
                "gate_qubits": [[1]],
                "probabilities": [1.0],
                "instructions": [[{"name": "id", "qubits": [0]}]],
            },
            {
                "type": "roerror",
                "operations": ["measure"],
                "gate_qubits": [[3]],
                "probabilities": [[0.81, 0.19], [0.07, 0.93]],
            },
        ]
    }


@pytest.fixture
def calibration(tmp_path, monkeypatch):
    from copy import deepcopy
    from qiskit_aer.noise import NoiseModel

    installed, saved = tmp_path / "installed", tmp_path / "saved"
    installed.mkdir()
    saved.mkdir()
    for kind in ("properties", "configuration"):
        (installed / f"{kind}.json").write_text("{}")
        (saved / f"{kind}.json").write_text("{}")
    snapshot = channel_snapshot()
    (saved / "noise.json").write_text(json.dumps(snapshot))
    backend = SimpleNamespace(
        dirname=str(installed),
        props_filename="properties.json",
        conf_filename="configuration.json",
    )
    expected = deepcopy(snapshot)
    expected["errors"][0]["id"] = "fresh-uuid"
    monkeypatch.setattr(
        NoiseModel,
        "from_backend",
        lambda b: SimpleNamespace(to_dict=lambda **kw: deepcopy(expected)),
    )
    return backend, saved, snapshot


def test_calibration_accepts_only_independent_record_reordering(calibration):
    from copy import deepcopy
    from itertools import permutations

    backend, saved, snapshot = calibration
    before = (saved / "noise.json").read_bytes()
    expected = adapter.calibration_records(snapshot)
    for order in permutations(snapshot["errors"]):
        shuffled = {"errors": deepcopy(order)}
        (saved / "noise.json").write_text(json.dumps(shuffled))
        assert adapter.calibration_records(shuffled) == expected
        assert adapter.validate_calibration(backend, saved, shuffled)[
            "noise"
        ] == adapter.digest(saved / "noise.json")
    assert before != (saved / "noise.json").read_bytes()
    assert snapshot == channel_snapshot()


@pytest.mark.parametrize(
    "mutation",
    [
        "probability",
        "matrix",
        "shape",
        "scalar_type",
        "instruction_order",
        "branch_order",
        "internal_qargs",
        "physical_qargs",
        "readout",
        "duplicate",
        "unsupported_field",
        "unsupported_operation",
        "unsupported_type",
        "multi_operation",
        "multi_location",
        "bool_qarg",
        "duplicate_qarg",
        "default",
        "top_level",
        "nonfinite",
    ],
)
def test_calibration_rejects_changed_or_unsupported_channels(calibration, mutation):
    from copy import deepcopy

    backend, saved, original = calibration
    snapshot = deepcopy(original)
    error = snapshot["errors"][0]
    if mutation == "probability":
        error["probabilities"][0] += 0.01
    elif mutation == "matrix":
        error["instructions"][1][0]["params"][0][0][0][1] = -1.0
    elif mutation == "shape":
        error["instructions"][1][0]["params"][0].pop()
    elif mutation == "scalar_type":
        error["probabilities"][0] = True
    elif mutation == "instruction_order":
        error["instructions"][0].reverse()
    elif mutation == "branch_order":
        error["instructions"].reverse()
    elif mutation == "internal_qargs":
        error["instructions"][0][0]["qubits"] = [0]
    elif mutation == "physical_qargs":
        error["gate_qubits"][0].reverse()
    elif mutation == "readout":
        snapshot["errors"][2]["probabilities"].reverse()
    elif mutation == "duplicate":
        snapshot["errors"].append(deepcopy(error))
    elif mutation == "unsupported_field":
        error["noise_qubits"] = [[3, 1]]
    elif mutation == "unsupported_operation":
        error["operations"] = ["cx"]
    elif mutation == "unsupported_type":
        error["type"] = "default"
    elif mutation == "multi_operation":
        error["operations"].append("cz")
    elif mutation == "multi_location":
        error["gate_qubits"].append([1, 3])
    elif mutation == "bool_qarg":
        error["gate_qubits"][0][1] = True
    elif mutation == "duplicate_qarg":
        error["gate_qubits"] = [[3, 3]]
    elif mutation == "default":
        del error["gate_qubits"]
    elif mutation == "top_level":
        snapshot["extra"] = []
    elif mutation == "nonfinite":
        error["probabilities"][0] = float("nan")
    (saved / "noise.json").write_text(json.dumps(snapshot))
    with pytest.raises(ValueError):
        adapter.validate_calibration(backend, saved, snapshot)


@pytest.mark.parametrize("kind", ["properties", "configuration", "noise"])
def test_calibration_rejects_changed_files(calibration, kind):
    backend, saved, snapshot = calibration
    (saved / f"{kind}.json").write_text('{"changed": true}')
    with pytest.raises(ValueError, match="identity mismatch"):
        adapter.validate_calibration(backend, saved, snapshot)


def test_duplicate_identity_rejected_even_when_expected_matches(
    calibration, monkeypatch
):
    from copy import deepcopy
    from qiskit_aer.noise import NoiseModel

    backend, saved, snapshot = calibration
    snapshot["errors"].append(deepcopy(snapshot["errors"][0]))
    (saved / "noise.json").write_text(json.dumps(snapshot))
    monkeypatch.setattr(
        NoiseModel,
        "from_backend",
        lambda b: SimpleNamespace(to_dict=lambda **kw: snapshot),
    )
    with pytest.raises(ValueError, match="Duplicate"):
        adapter.validate_calibration(backend, saved, snapshot)


def test_duplicate_json_key_rejected(calibration):
    backend, saved, snapshot = calibration
    (saved / "noise.json").write_text('{"errors": [], "errors": []}')
    with pytest.raises(ValueError, match="Duplicate"):
        adapter.validate_calibration(backend, saved, snapshot)


def test_independent_process_calibration_snapshots(tmp_path):
    """Two real offline FakeTorino processes must accept the same calibration."""
    import os
    import subprocess
    import sys
    import time

    checkout = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(checkout / "src"))
    first = tmp_path / "first"
    for name, reference in (("first", None), ("second", first)):
        output = tmp_path / name
        command = [
            sys.executable,
            str(checkout / "tools/check_c5_noise_adapter.py"),
            "--calibration-output",
            str(output),
        ]
        if reference is not None:
            command += ["--calibration-reference", str(reference)]
        started = time.monotonic()
        with (tmp_path / f"{name}.log").open("x") as log:
            child = subprocess.run(
                command,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=45,
                check=False,
            )
        (tmp_path / f"{name}.receipt.json").write_text(
            json.dumps(
                {
                    "command": command,
                    "exit": child.returncode,
                    "seconds": time.monotonic() - started,
                    "timeout_seconds": 45,
                    "rss_scope": "outer supervised pytest wait4 includes descendants; no per-child hard cap",
                }
            )
        )
        assert child.returncode == 0, (tmp_path / f"{name}.log").read_text()
        result = json.loads((output / "calibration-check.json").read_text())
        assert result["records"] == 965 and result["scientific_shots"] == 0

    # Independently compare payloads after the only authorized UUID removal.
    def keyed(path):
        records = {}
        for item in json.loads(path.read_text())["errors"]:
            item.pop("id", None)
            key = (
                item["type"],
                tuple(item["operations"]),
                tuple(map(tuple, item["gate_qubits"])),
            )
            assert key not in records
            records[key] = item
        return records

    assert keyed(first / "noise.json") == keyed(tmp_path / "second/noise.json")
    import random

    snapshot = json.loads((first / "noise.json").read_text())
    original = adapter.calibration_records(snapshot)
    random.Random(20261120).shuffle(snapshot["errors"])
    assert adapter.calibration_records(snapshot) == original
    # The validator also accepts this permutation against the other process's
    # independently reconstructed model, while hashing the new raw file bytes.
    from logique.benchmarks.routing import default_backend

    backend = default_backend()
    (first / "noise.json").rename(first / "noise-original.json")
    (first / "noise.json").write_text(json.dumps(snapshot))
    raw = adapter.digest(first / "noise.json")
    assert adapter.validate_calibration(backend, first, snapshot)["noise"] == raw


def test_layout_preserves_ordered_physical_measurements():
    adapter.validate_layout([2, 7, 9], [9, 2, 7], {0: 2, 1: 0}, 3, 2)
    with pytest.raises(ValueError, match="layout mismatch"):
        adapter.validate_layout([2, 7, 9], [9, 2, 7], {0: 0, 1: 2}, 3, 2)
    with pytest.raises(ValueError, match="layout mismatch"):
        adapter.validate_layout(
            list(range(19)), list(range(11)), dict(enumerate(range(10))), 11, 10
        )
    with pytest.raises(ValueError, match="layout mismatch"):
        adapter.validate_layout([2, 7, 9], [9, 2, 2], {0: 2, 1: 0}, 3, 2)


def test_saved_adapter_builds_preceding_steps_without_structure(tmp_path, monkeypatch):
    """Run the real selector/assembly loop and stop exactly at first routing."""
    import numpy as np
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    from logique.benchmarks import routing

    prep, oracle, reflection = [QuantumCircuit(2) for _ in range(3)]
    prep.h(0)
    oracle.cx(0, 1)
    reflection.ry(0.31, 1)
    parts = [prep, oracle, reflection]
    reference = {
        "case": {"vertices": [0, 1], "edges": [[0, 1]], "colors": 2},
        "regime": "R1",
        "construction": {"width": 2},
        "counts": {"data_bits": 2},
        "analytical_ledger": {"rows": [{"iterations": j} for j in range(3)]},
        "rows": [{"iterations": j} for j in range(3)],
    }
    source = {
        "reference": reference,
        "parts": parts,
        "policies": [],
        "identity": {"source_kind": adapter.SOURCE_KIND},
    }
    monkeypatch.setattr(adapter, "load_source", lambda *a: source)
    monkeypatch.setattr(adapter, "validate_calibration", lambda *a: {})
    monkeypatch.setattr(
        noisy, "_components", lambda *a: pytest.fail("rebuilt structure")
    )
    monkeypatch.setattr(routing, "default_backend", lambda: SimpleNamespace())
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "noise.json").write_text('{"errors": []}')
    expected = prep.copy()
    for _ in range(2):
        expected.compose(oracle, inplace=True)
        expected.compose(reflection, inplace=True)
    calls = []

    def route(circuit, **kwargs):
        calls.append(circuit)
        assert kwargs["qubits_initially_zero"] is False
        assert kwargs["num_processes"] == 1
        actual = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        )
        np.testing.assert_allclose(
            actual.data, Statevector.from_instruction(expected).data, atol=1e-14
        )
        raise RuntimeError("routing_timeout_surrogate_no_sampling")

    monkeypatch.setattr(qiskit, "transpile", route)
    output = tmp_path / "child"
    request = {
        "source_kind": adapter.SOURCE_KIND,
        "request_identity": adapter.request_identity("R1", 37, 2),
        "config": config(),
        "name": "R1",
        "seed": 37,
        "iterations": [2],
        "output": str(output),
    }
    wrong = {**request, "request_identity": "original-structure"}
    with pytest.raises(ValueError, match="request identity"):
        noisy.execute_seed(wrong)
    assert not output.exists()
    with pytest.raises(RuntimeError, match="routing_timeout_surrogate"):
        noisy.execute_seed(request)
    assert len(calls) == 1
    record = json.loads((output / "result.json").read_text())
    assert record["rows"] == [{"iterations": 2, "status": "failed"}]
    assert record["request_identity"] == request["request_identity"]
    assert not (output / "j0").exists() and not (output / "j1").exists()
