"""Adversarial value/read/frame/release checks on saved actual level responses."""

from copy import deepcopy
import json
import os
from pathlib import Path

import pytest
from types import SimpleNamespace

import adapter

from level_value import LevelReplay, LevelValueError, validate_level_response


def test_candidate_import_identity() -> None:
    import logique.circuits.records as records
    import logique.synthesis.result as result_module

    source = Path(__file__).resolve().parents[5] / "src"
    for module in (records, result_module):
        assert Path(module.__file__).resolve().is_relative_to(source)
    assert Path(adapter.__file__).resolve().parent == Path(__file__).resolve().parent


@pytest.fixture
def response() -> dict:
    root = Path(os.environ["LOGIQUE_LEVEL_CORPUS"])
    return json.loads((root / "depth-03-shared.stdout").read_text())


@pytest.mark.parametrize("alias", [True, 1.0])
@pytest.mark.parametrize(
    "field", ["input_qubits", "output_qubits", "node", "leaves", "copies", "target"]
)
def test_typed_index_alias_rejects(response: dict, alias: object, field: str) -> None:
    if field in ("input_qubits", "output_qubits"):
        response[field][0] = alias
    else:
        entry = response["steps"][0]["level"][0]
        if field == "node":
            entry["node"] = alias
        else:
            entry["cones"][0][field] = [alias]
    with pytest.raises(LevelValueError):
        validate_level_response(response)


def test_wrong_value_live_operand_rejects(response: dict) -> None:
    machine = LevelReplay(response)
    machine.wires[machine.address(1)] ^= machine.mask
    with pytest.raises(LevelValueError, match="wrong-value operand"):
        machine.read(1)


def test_nonzero_release_rejects(response: dict) -> None:
    machine = LevelReplay(response)
    q = machine.allocate()
    machine.wires[q] = machine.mask
    with pytest.raises(LevelValueError, match="nonzero/double release"):
        machine.release(q)


def test_live_zero_release_rejects(response: dict) -> None:
    machine = LevelReplay(response)
    q = machine.allocate()
    machine.stacks[5].append(q)
    with pytest.raises(LevelValueError, match="release live address"):
        machine.release(q)


def test_nonzero_reuse_rejects(response: dict) -> None:
    machine = LevelReplay(response)
    q = machine.allocate()
    machine.release(q)
    machine.wires[q] = machine.mask
    with pytest.raises(LevelValueError, match="nonzero reuse"):
        machine.allocate()


def test_zero_release_and_reuse(response: dict) -> None:
    machine = LevelReplay(response)
    q = machine.allocate()
    machine.release(q)
    assert machine.allocate() == q
    assert machine.releases == machine.reuses == 1


def test_double_release_rejects(response: dict) -> None:
    machine = LevelReplay(response)
    q = machine.allocate()
    machine.release(q)
    with pytest.raises(LevelValueError, match="nonzero/double release"):
        machine.release(q)


def test_restoration_frame_catches_missing_inverse(response: dict) -> None:
    root = Path(os.environ["LOGIQUE_LEVEL_CORPUS"])
    equal = json.loads((root / "fast-01-equal.stdout").read_text())
    machine = LevelReplay(equal)
    parity = machine.parity
    calls = 0

    def missing_last_inverse(target: int, leaves: list[int]) -> None:
        nonlocal calls
        calls += 1
        if calls != 4:
            parity(target, leaves)

    machine.parity = missing_last_inverse
    with pytest.raises(LevelValueError, match="frame restoration"):
        machine.finish()


def test_legally_wired_wrong_gate_rejects(response: dict) -> None:
    response["gates"][0]["controls"][0] = 3
    with pytest.raises(LevelValueError, match="emitted gates differ"):
        validate_level_response(response)


@pytest.mark.parametrize(
    "field,alias",
    [("controls", True), ("controls", 1.0), ("target", True), ("target", 4.0)],
)
def test_typed_gate_payload_rejects(response: dict, field: str, alias: object) -> None:
    gate = response["gates"][0]
    if field == "controls":
        gate[field][0] = alias
    else:
        gate[field] = alias
    with pytest.raises(LevelValueError, match="emitted gates differ"):
        validate_level_response(response)


@pytest.mark.parametrize(
    "kind",
    [
        "input_cap",
        "node_cap",
        "action_cap",
        "gate_cap",
        "width_budget",
        "noncanonical_xor",
        "dirty_final",
    ],
)
def test_domain_and_budget_rejections(response: dict, kind: str) -> None:
    if kind == "input_cap":
        response["network"]["inputs"] = list(range(1, 8))
    elif kind == "node_cap":
        response["network"]["nodes"] *= 10
    elif kind == "action_cap":
        response["steps"] = response["steps"] * 33
    elif kind == "gate_cap":
        response["gates"] = response["gates"] * 1025
    elif kind == "width_budget":
        with pytest.raises(LevelValueError):
            validate_level_response(response, qubit_budget=4)
        return
    elif kind == "noncanonical_xor":
        response["network"]["nodes"][5]["kind"] = "xor"
    elif kind == "dirty_final":
        response["steps"] = response["steps"][:-1]
    with pytest.raises(LevelValueError):
        validate_level_response(response)


def test_actual_copy_release_and_unreleased_uncompute(response: dict) -> None:
    certificate = validate_level_response(deepcopy(response))
    assert certificate["zero_releases"] == 2
    assert certificate["zeroed_unreleased"] == 1
    assert certificate["frames"] == 4
    assert certificate["clean_workspace_required"] is True


@pytest.mark.parametrize(
    "mutation", ["valid", "boolean_leaf", "float_gate", "missing_steps"]
)
def test_private_boundary_precedes_construction(
    response: dict, tmp_path: Path, monkeypatch, mutation: str
) -> None:
    import logique.circuits.records as records

    source = tmp_path / "input.v"
    source.write_text("unused mocked subprocess input")
    response["private_request"] = dict(
        strategy="depth", qubit_budget=128, preprocessing="none"
    )
    if mutation == "boolean_leaf":
        response["steps"][0]["level"][0]["cones"][0]["leaves"][0] = True
    elif mutation == "float_gate":
        response["gates"][0]["controls"][0] = 0.0
    elif mutation == "missing_steps":
        del response["steps"]
    monkeypatch.setattr(
        adapter.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=json.dumps(response), stderr=""
        ),
    )
    calls = []

    def sentinel(*args):
        calls.append(args)
        raise RuntimeError("construction reached")

    monkeypatch.setattr(records, "records_to_qiskit", sentinel)
    with pytest.raises(RuntimeError if mutation == "valid" else LevelValueError):
        adapter.synthesize_level(source, executable="unused", strategy="depth")
    assert len(calls) == (mutation == "valid")


@pytest.mark.parametrize("strategy", ["fast", "depth"])
@pytest.mark.parametrize("policy", ["none", "refactoring"])
def test_actual_private_file_adapter(
    tmp_path: Path, strategy: str, policy: str
) -> None:
    source = tmp_path / "asymmetric.v"
    source.write_text(
        "module top(b, a, c, unused, y);\ninput b, a, c, unused;\noutput y;\nassign y = a & ~b;\nendmodule\n"
    )
    data = adapter.run_level(
        source,
        executable=os.environ["LOGIQUE_LEVEL_EXECUTABLE"],
        strategy=strategy,
        preprocessing=policy,
    )
    (tmp_path / "response.json").write_text(json.dumps(data, indent=2))
    assert data["level_value_validation"]["frames"] == 1


@pytest.mark.parametrize("strategy", ["fast", "depth"])
def test_actual_empty_output_selection(tmp_path: Path, strategy: str) -> None:
    source = tmp_path / "select-none.v"
    source.write_text(
        "module top(a, b, y);\ninput a, b;\noutput y;\nassign y = a & b;\nendmodule\n"
    )
    data = adapter.run_level(
        source,
        executable=os.environ["LOGIQUE_LEVEL_EXECUTABLE"],
        strategy=strategy,
        outputs=[],
    )
    (tmp_path / "response.json").write_text(json.dumps(data, indent=2))
    assert data["output_qubits"] == data["gates"] == data["steps"] == []
    assert data["num_qubits"] == 2


@pytest.mark.parametrize("alias", [True, 0.0])
def test_selected_output_types_reject_before_process(
    tmp_path: Path, alias: object, monkeypatch
) -> None:
    source = tmp_path / "not-read.v"
    source.write_text("placeholder")
    monkeypatch.setattr(
        adapter.subprocess, "run", lambda *a, **k: pytest.fail("process reached")
    )
    with pytest.raises(LevelValueError):
        adapter.run_level(source, executable="unused", strategy="fast", outputs=[alias])


@pytest.mark.parametrize("strategy", ["fast", "depth"])
def test_actual_six_input_boundary(tmp_path: Path, strategy: str) -> None:
    from check import apply_circuit

    source = tmp_path / "six-input.v"
    source.write_text(
        "module top(b, a, c, unused, d, e, y);\ninput b, a, c, unused, d, e;\noutput y;\nwire p, q, r;\nassign p = a & ~b;\nassign q = c & d;\nassign r = p ^ q;\nassign y = r ^ e;\nendmodule\n"
    )
    result = adapter.synthesize_level(
        source, executable=os.environ["LOGIQUE_LEVEL_EXECUTABLE"], strategy=strategy
    )
    data = result.metadata
    summary = result.summary()
    assert summary["method"] == "private_xag_level" and summary["inputs"] == 6
    (tmp_path / "response.json").write_text(json.dumps(data, indent=2))
    assert data["level_value_validation"]["assignments"] == 64
    oracle, phase = result.oracle(), result.phase_oracle()
    for assignment in range(64):
        inputs = [(assignment >> bit) & 1 for bit in range(6)]
        b, a, c, unused, d, e = inputs
        value = (a & (1 - b)) ^ (c & d) ^ e
        initial = inputs + [0] * (data["num_qubits"] - 6)
        for target in (0, 1):
            bits = initial + [target]
            assert apply_circuit(oracle, bits) == 1
            assert bits == initial + [target ^ value]
        bits = initial.copy()
        assert apply_circuit(phase, bits) == (-1 if value else 1)
        assert bits == initial
