"""Saved real protocol boundaries: no native process or quantum arrays needed."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from logique.synthesis import native

FIXTURES = Path(__file__).parent / "fixtures/native_value_certificate"


def saved(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def valid():
    return saved("valid-equal-cones.json")


def boundary(monkeypatch, tmp_path, response, *, public=False, strategy="xag_low_t"):
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(response)),
    )
    if public:
        from logique.synthesis import api

        monkeypatch.setattr(
            api, "records_to_qiskit", lambda *a: pytest.fail("constructed circuit")
        )
        return api.synthesize(
            tmp_path / "unused.v",
            "xag_bennett",
            strategy=strategy,
            executable=executable,
        )
    return native.run_native(
        tmp_path / "unused.v", "xag_bennett", strategy=strategy, executable=executable
    )


@pytest.mark.parametrize("public", [False, True])
def test_exact_saved_old_response_rejected(monkeypatch, tmp_path, public):
    response = saved("old-seven-input.json")
    assert len(response["network"]["inputs"]) == 7
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, response, public=public)


def test_exact_saved_valid_response_and_stale_alias(monkeypatch, tmp_path, valid):
    accepted = boundary(monkeypatch, tmp_path, valid)
    assert accepted == valid
    cert = valid["xag_value_validation"]
    assert cert["assignments"] == 64
    # Nodes8/10 alias PI wire0 after restoration; they are not Boolean values.
    assert valid["xag_schedule_audit"]["node_stacks"][10] == [0, 0, 0]
    assert cert["node_values"][10] != cert["node_values"][1]


CERT_FIELDS = [
    "policy",
    "caps",
    "inputs",
    "assignments",
    "nodes",
    "width",
    "steps",
    "blocks",
    "operand_reads",
    "zero_releases",
    "node_values",
    "block_checks",
]


@pytest.mark.parametrize("field", CERT_FIELDS)
@pytest.mark.parametrize("replacement", [None, True, "1", 1.0, [], {}])
@pytest.mark.parametrize("public", [False, True])
def test_malformed_certificate_fields(
    monkeypatch, tmp_path, valid, field, replacement, public
):
    valid["xag_value_validation"][field] = replacement
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=public)


@pytest.mark.parametrize("field", CERT_FIELDS)
def test_missing_certificate_fields(monkeypatch, tmp_path, valid, field):
    del valid["xag_value_validation"][field]
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


@pytest.mark.parametrize("certificate", [None, False, [], {}, "old-v0"])
def test_missing_or_malformed_certificate(monkeypatch, tmp_path, valid, certificate):
    valid["xag_value_validation"] = certificate
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


@pytest.mark.parametrize("field", native.XAG_VALUE_CAPS)
@pytest.mark.parametrize("delta", [-1, 1])
def test_exact_caps_required(monkeypatch, tmp_path, valid, field, delta):
    valid["xag_value_validation"]["caps"][field] += delta
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


def replace(path, value):
    def mutate(response):
        target = response
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


MUTATIONS = [
    replace(["xag_value_validation", "policy"], "stack_only"),
    replace(["xag_value_validation", "assignments"], 32),
    replace(["xag_value_validation", "inputs"], 5),
    replace(["xag_value_validation", "nodes"], 11),
    replace(["xag_value_validation", "width"], 8),
    replace(["xag_value_validation", "steps"], 4),
    replace(["xag_value_validation", "blocks"], 0),
    replace(["xag_value_validation", "operand_reads"], 30),
    replace(["xag_value_validation", "zero_releases"], 1),
    replace(["num_qubits"], 257),
    replace(["network", "inputs"], list(range(1, 8))),
    replace(["network", "nodes"], [{}] * 257),
    replace(["network", "outputs"], [{}] * 257),
    replace(["steps"], [{}] * 4097),
    replace(["input_qubits", 0], True),
    replace(["input_qubits", 0], 7),
    replace(["output_qubits", 0], 7),
    replace(["output_qubits"], []),
    replace(["network", "inputs", 0], True),
    replace(["network", "nodes", 0, "id"], False),
    replace(["network", "outputs", 0, "node"], 12),
    replace(["network", "outputs", 0, "inverted"], 0),
    replace(["gates", 0, "controls", 0], 7),
    replace(["gates", 0, "controls", 0], True),
    replace(["gates", 0, "polarity", 0], 1),
    replace(["gates", 0, "target"], 1),
    replace(["gates", 2, "controls", 0], 1),
    replace(["xag_value_validation", "node_values", 10], 0),
    replace(["xag_value_validation", "block_checks", 0, "undo"], 0),
    replace(["xag_value_validation", "block_checks", 0, "entry", 0, "wire"], 7),
    replace(["xag_value_validation", "block_checks", 0, "entry", 0, "value"], 0),
    replace(["xag_value_validation", "block_checks", 0, "frames", 0, "prepared"], 0),
    replace(
        ["xag_value_validation", "block_checks", 0, "frames", 0, "restored_value"], 0
    ),
    replace(["xag_schedule_audit", "node_stacks", 10], [7]),
    replace(["xag_schedule_audit", "actions"], []),
]


@pytest.mark.parametrize(
    "mutate", MUTATIONS, ids=lambda m: f"mutation-{MUTATIONS.index(m)}"
)
@pytest.mark.parametrize("public", [False, True])
def test_inconsistent_response_rejected(monkeypatch, tmp_path, valid, mutate, public):
    mutate(valid)
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=public)


@pytest.mark.parametrize("strategy", ["bennett", "bennett_inplace", "eager"])
def test_other_strategies_do_not_require_certificate(
    monkeypatch, tmp_path, valid, strategy
):
    del valid["xag_value_validation"]
    valid["mapping_strategy"].update(
        name=strategy, implementation=f"caterpillar::{strategy}_mapping_strategy"
    )
    assert boundary(monkeypatch, tmp_path, valid, strategy=strategy) == valid


def test_saved_fixture_manifest():
    manifest = json.loads((FIXTURES / "provenance.json").read_text())
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest


def test_absent_certificate_rejected_before_construction(monkeypatch, tmp_path, valid):
    del valid["xag_value_validation"]
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


def test_exact_saved_valid_response_constructs_public_circuit(
    monkeypatch, tmp_path, valid
):
    from logique.synthesis import api

    source = tmp_path / "source.v"
    source.write_text("saved response protocol fixture")
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(valid)),
    )
    result = api.synthesize(
        source, "xag_bennett", strategy="xag_low_t", executable=executable
    )
    assert result.circuit.num_qubits == 7
    assert len(result.circuit.data) == len(valid["gates"])
    assert result.metadata["xag_value_validation"] == valid["xag_value_validation"]


@pytest.mark.parametrize(
    "path,value",
    [
        (["physical_control_normalization", 0, "emitted_gate_count"], True),
        (["physical_control_normalization", 0, "polarity", 0], 1),
        (["physical_control_normalization", 0, "target"], 7),
        (["physical_control_normalization", 0, "rule"], "unverified"),
        (["xag_schedule_audit", "actions", 0, "target_index"], True),
        (["xag_schedule_audit", "actions", 0, "explicit_leaves", 0], True),
        (["xag_value_validation", "caps", "inputs"], 6.0),
        (["xag_value_validation", "caps", "width"], True),
        (
            ["xag_value_validation", "block_checks", 0, "frames", 0, "restored_wire"],
            None,
        ),
    ],
)
def test_nested_protocol_types(monkeypatch, tmp_path, valid, path, value):
    replace(path, value)(valid)
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


@pytest.mark.parametrize("public", [False, True])
@pytest.mark.parametrize(
    "leaves",
    [
        None,
        True,
        1.0,
        "1,2,3",
        {},
        [True, 2, 3],
        [1.0, 2, 3],
        [],
        [1, 2],
        [1, 2, 3, 4],
        [1, 1, 3],
        [1, 2, 12],
        [1, 3, 2],
    ],
)
def test_redundant_leaf_list_is_strict(monkeypatch, tmp_path, valid, leaves, public):
    # Mirror the malformed payload in both records so their JSON equality
    # cannot hide a missing independent validation of the redundant list.
    valid["steps"][0]["leaves"] = leaves
    valid["xag_schedule_audit"]["actions"][0]["leaves"] = leaves
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=public)


def serialized_indices():
    """Enumerate every node/wire index in the retained valid certificate."""
    response = saved("valid-equal-cones.json")
    paths = []

    def visit(value, path=()):
        if isinstance(value, dict):
            for key, item in value.items():
                # The source graph is separate preprocessing evidence; the
                # certificate covers the actual mapped graph and its indices.
                if key not in ("source_network", "preprocessing"):
                    visit(item, (*path, key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, (*path, index))
        elif type(value) is int and path[-1] in (
            "id",
            "node",
            "target",
            "target_index",
            "leaf",
            "root",
            "wire",
            "restored_wire",
            "physical_target",
        ):
            paths.append((path, value))
        elif type(value) is int and any(
            key in path
            for key in (
                "inputs",
                "input_qubits",
                "output_qubits",
                "explicit_leaves",
                "leaves",
                "physical_leaves",
                "physical_controls",
                "controls",
                "emitted_controls",
                "node_stacks",
            )
        ):
            paths.append((path, value))

    visit(response)
    return paths


@pytest.mark.parametrize("path,value", serialized_indices())
@pytest.mark.parametrize("alias", ["bool", "float"])
def test_all_serialized_indices_reject_numeric_aliases(
    monkeypatch, tmp_path, valid, path, value, alias
):
    # Float aliases preserve every saved index; Boolean aliases preserve 0/1.
    replacement = bool(value) if alias == "bool" else float(value)
    replace(path, replacement)(valid)
    # Keep redundant step/audit payloads identical to exercise their types,
    # rather than just the type-sensitive JSON comparison between them.
    if path[0] == "steps":
        replace(("xag_schedule_audit", "actions", *path[1:]), replacement)(valid)
    elif path[:2] == ("xag_schedule_audit", "actions"):
        if path[3] in valid["steps"][path[2]]:
            replace(("steps", *path[2:]), replacement)(valid)
    with pytest.raises(RuntimeError, match="value certificate"):
        boundary(monkeypatch, tmp_path, valid, public=True)


@pytest.mark.parametrize("alias", [None, True, 1.0])
def test_public_constructor_sentinel_for_saved_leaf_adversaries(
    monkeypatch, tmp_path, valid, alias
):
    from logique.synthesis import api

    if alias is not None:
        valid["steps"][0]["leaves"][0] = alias
        valid["xag_schedule_audit"]["actions"][0]["leaves"][0] = alias
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(valid)),
    )
    calls = []

    class ConstructionReached(Exception):
        pass

    def constructor(*args):
        calls.append(args)
        raise ConstructionReached

    monkeypatch.setattr(api, "records_to_qiskit", constructor)
    expected = ConstructionReached if alias is None else RuntimeError
    with pytest.raises(expected):
        api.synthesize(
            tmp_path / "unused.v",
            "xag_bennett",
            strategy="xag_low_t",
            executable=executable,
        )
    assert len(calls) == (1 if alias is None else 0)


@pytest.mark.parametrize("alias", [True, 1.0])
def test_profile_composition_keeps_rejected_certificate_evidence(
    monkeypatch, tmp_path, valid, alias
):
    from logique.synthesis import api, research_profiles

    graph = valid["source_network"]
    profile = {
        "before_network": graph,
        "after_network": graph,
        "verilog": "unused",
        "source_sha256": "fixture",
        "caps": {"inputs": 10, "nodes": 4096},
        "seconds": 0,
    }
    monkeypatch.setattr(
        research_profiles, "preprocess_verilog", lambda *a, **kw: profile
    )
    valid["steps"][0]["leaves"][0] = alias
    valid["xag_schedule_audit"]["actions"][0]["leaves"][0] = alias
    executable = tmp_path / "bridge"
    executable.touch()
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(valid)),
    )
    monkeypatch.setattr(
        api, "records_to_qiskit", lambda *a: pytest.fail("constructed circuit")
    )
    with pytest.raises(RuntimeError, match="value certificate") as caught:
        api.synthesize(
            tmp_path / "unused.v",
            "xag_bennett",
            strategy="xag_low_t",
            optimization_profile="cut_esop_balancing",
            executable=executable,
        )
    evidence = caught.value.profile_evidence
    assert evidence["status"] == "failed"
    assert evidence["failed_boundary"] == "mapping_native"
    assert evidence["mapping_request"]["strategy"] == "xag_low_t"
