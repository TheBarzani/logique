"""Regression checks for selecting a missing iteration before routing/sampling."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from logique.benchmarks import noisy_iterations as subject


def reference():
    """Return complete ordered ideal metadata without quantum allocations."""
    return {
        "analytical_ledger": {"rows": [{"iterations": j} for j in range(3)]},
        "rows": [{"iterations": j} for j in range(3)],
    }


@pytest.mark.parametrize("chosen", [[], [True], [2, 2], [2, 1], [-1], [3], "2", None])
def test_invalid_selector_fails_before_output_creation(tmp_path, chosen):
    config = json.loads(Path("configs/noisy_iteration_pilot.json").read_text())
    config["ideal_pilot"] = str(tmp_path / "ideal")
    saved = tmp_path / "ideal" / "tiny"
    saved.mkdir(parents=True)
    (saved / "result.json").write_text(json.dumps(reference()))
    output = tmp_path / "child"
    with pytest.raises(ValueError, match="iteration subset"):
        subject.execute_seed(
            dict(
                config=config,
                name="tiny",
                seed=37,
                iterations=chosen,
                output=str(output),
            )
        )
    assert not output.exists()


def test_selector_requires_all_preceding_ideal_rows():
    ref = reference()
    assert subject.selected_iterations({"iterations": [2]}, ref) == [2]
    assert subject.selected_iterations({}, ref) == [0, 1, 2]
    ref["rows"].pop(0)
    with pytest.raises(ValueError, match="complete ordered"):
        subject.selected_iterations({"iterations": [2]}, ref)


def test_only_j2_routes_with_both_preceding_steps(tmp_path, monkeypatch):
    """Exercise the real execution loop; stop at first route, before Aer."""
    from qiskit import QuantumCircuit, qpy
    from qiskit.quantum_info import Statevector
    import numpy as np
    import qiskit
    from logique.benchmarks import routing

    config = json.loads(Path("configs/noisy_iteration_pilot.json").read_text())
    config.update(
        ideal_pilot=str(tmp_path / "ideal"), max_qubits=3, memory_bytes=2 * 1024**3
    )
    saved = tmp_path / "ideal" / "tiny"
    saved.mkdir(parents=True)
    prep = QuantumCircuit(2)
    prep.ry(0.31, 0)
    prep.h(1)
    oracle = QuantumCircuit(3)
    oracle.cx(0, 1)
    diffusion = QuantumCircuit(2)
    diffusion.ry(0.47, 0)
    parts = [prep, oracle, diffusion]
    ref = reference()
    ref.update(
        case={"name": "edge", "vertices": [0, 1], "edges": [[0, 1]], "colors": 2},
        regime="R1",
        construction={"width": 3},
        counts={"data_bits": 2},
    )
    (saved / "result.json").write_text(json.dumps(ref))
    for name, part in zip(("preparation", "oracle", "diffusion"), parts):
        with (saved / f"{name}.qpy").open("xb") as stream:
            qpy.dump(part, stream)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "noise.json").write_text('{"errors": []}')
    monkeypatch.setattr(subject, "_components", lambda *a: (parts, []))
    monkeypatch.setattr(routing, "default_backend", lambda: SimpleNamespace())
    expected = QuantumCircuit(3)
    expected.compose(prep, [0, 1], inplace=True)
    for _ in range(2):
        expected.compose(oracle, inplace=True)
        expected.compose(diffusion, [0, 1], inplace=True)
    calls = []

    def route(circuit, **kwargs):
        calls.append(circuit)
        assert kwargs["seed_transpiler"] == 37
        observed = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        )
        np.testing.assert_allclose(
            observed.data, Statevector.from_instruction(expected).data, atol=1e-14
        )
        raise RuntimeError("stop_before_any_sampling")

    monkeypatch.setattr(qiskit, "transpile", route)
    output = tmp_path / "child"
    with pytest.raises(RuntimeError, match="stop_before_any_sampling"):
        subject.execute_seed(
            dict(
                config=config, name="tiny", seed=37, iterations=[2], output=str(output)
            )
        )
    assert len(calls) == 1
    assert not (output / "j0").exists()
    assert not (output / "j1").exists()
    result = json.loads((output / "result.json").read_text())
    assert result["requested_iterations"] == [2]
    assert result["rows"] == [{"iterations": 2, "status": "failed"}]


def test_preparer_refuses_wrong_frozen_identity(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "remaining", Path("tools/run_noisy_remaining.py").resolve()
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "manifest.json").write_text("{}")
    with pytest.raises(ValueError, match="identity mismatch"):
        module.verified_manifest(tmp_path, "0" * 64)
