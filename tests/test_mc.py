"""Bounded private MC recipe, positional CEC and failure-persistence regressions."""

from copy import deepcopy
import json
import os
from pathlib import Path
import random
import sys

import pytest

from logique.synthesis.mc import (
    MC_PASSES,
    MCOptimizationError,
    _truth,
    _validate,
    reduce_mc_verilog,
)


def _source(path, inputs, outputs, wires=()):
    names = [*inputs, *(name for name, _ in outputs)]
    lines = [f"module top({', '.join(names)});"]
    lines += [f"input {name};" for name in inputs]
    lines += [f"output {name};" for name, _ in outputs]
    lines += [f"wire {name};" for name, _ in wires]
    lines += [f"assign {name} = {expr};" for name, expr in [*wires, *outputs]]
    path.write_text("\n".join([*lines, "endmodule", ""]))
    return path


@pytest.fixture(scope="module")
def native_case(tmp_path_factory):
    selected = os.environ.get("LOGIQUE_MC_EXECUTABLE")
    if not selected:
        pytest.skip("Set LOGIQUE_MC_EXECUTABLE to a provenanced private build")
    tool = Path(selected).resolve()
    directory = tmp_path_factory.mktemp("mc-fixture")
    source = _source(
        directory / "source.v",
        ["z", "a", "unused", "b"],
        [("y", "t ^ u"), ("inv", "~a"), ("zero", "1'b0"), ("one", "1'b1")],
        [("t", "z & a"), ("u", "z & b")],
    )
    evidence = reduce_mc_verilog(
        source, executable=tool, artifacts=directory / "retained"
    )
    return tool, source, evidence


def test_real_recipe_locates_minmc_change(native_case):
    _, _, evidence = native_case
    checked = [e for e in evidence["events"] if e["kind"] == "checked"]
    assert [e["boundary"] for e in checked] == ["original", *MC_PASSES]
    expected = ["", "", "", ""]
    for assignment in range(16):
        z, a, _, b = [bool(assignment & (1 << i)) for i in range(4)]
        for i, value in enumerate([z and (a ^ b), not a, False, True]):
            expected[i] += str(int(value))
    assert all(e["truth"] == expected for e in checked)
    statistics = {e["boundary"]: e["statistics"] for e in checked}
    assert statistics["refactoring"]["and_count"] == 2
    assert statistics["xag_minmc_cut_rewriting"]["and_count"] == 1
    assert statistics["cleanup_6"]["inputs"] == 4
    assert (
        json.loads((Path(evidence["artifacts"]) / "evidence.json").read_text())
        == evidence
    )


@pytest.mark.parametrize("inputs", [[], ["z", "unused", "a"]])
def test_constants_duplicates_and_asymmetric_projection(native_case, tmp_path, inputs):
    tool, _, _ = native_case
    outputs = [("one", "1'b1"), ("zero", "1'b0"), ("dup", "1'b1")]
    if inputs:
        outputs += [("inverse", "~a"), ("projection", "z")]
    source = _source(tmp_path / "source.v", inputs, outputs)
    result = reduce_mc_verilog(
        source, executable=tool, artifacts=tmp_path / "artifacts"
    )
    checked = [e for e in result["events"] if e["kind"] == "checked"]
    for record in checked:
        assert record["truth"][:3] == [
            "1" * (1 << len(inputs)),
            "0" * (1 << len(inputs)),
            "1" * (1 << len(inputs)),
        ]
        if inputs:
            assert record["truth"][3:] == ["11110000", "01010101"]


@pytest.mark.parametrize("input_count,output_count", [(11, 1), (0, 17), (0, 0)])
def test_native_caps_precede_truth_tables(
    native_case, tmp_path, input_count, output_count
):
    tool, _, _ = native_case
    source = _source(
        tmp_path / "source.v",
        [f"x{i}" for i in range(input_count)],
        [(f"y{i}", "1'b0") for i in range(output_count)],
    )
    with pytest.raises(MCOptimizationError) as caught:
        reduce_mc_verilog(source, executable=tool, artifacts=tmp_path / "failed")
    events = caught.value.mc_evidence["events"]
    assert events[-1]["kind"] == "failure"
    assert not any(e["kind"] in {"checked", "started"} for e in events)
    assert (tmp_path / "failed/source.v").read_bytes() == source.read_bytes()


def test_exact_input_and_output_caps_preserve_unused_inputs(native_case, tmp_path):
    tool, _, _ = native_case
    source = _source(
        tmp_path / "source.v",
        [f"x{i}" for i in range(10)],
        [(f"y{i}", "x7" if i % 2 else "1'b1") for i in range(16)],
    )
    evidence = reduce_mc_verilog(
        source, executable=tool, artifacts=tmp_path / "exact-cap"
    )
    for event in evidence["events"]:
        if event["kind"] == "checked":
            assert event["assignments"] == 1024
            assert len(event["truth"]) == 16
            assert event["statistics"]["inputs"] == 10
            assert event["truth"][1] == ("0" * 128 + "1" * 128) * 4


def test_real_native_node_cap_precedes_truth_tables(native_case, tmp_path):
    tool, _, _ = native_case
    rng = random.Random(7)
    names = [f"x{i}" for i in range(10)]
    wires = []
    for i in range(5000):
        a, b = rng.sample(names, 2)
        name = f"w{i}"
        wires.append((name, f"{a} {'&' if i % 2 else '^'} {b}"))
        names.append(name)
    source = _source(
        tmp_path / "source.v",
        names[:10],
        [("y", names[-1])],
        wires,
    )
    with pytest.raises(MCOptimizationError) as caught:
        reduce_mc_verilog(source, executable=tool, artifacts=tmp_path / "node-cap")
    events = caught.value.mc_evidence["events"]
    assert events[0]["kind"] == "snapshot"
    assert events[0]["graph"]["size"] > 4096
    assert not any(e["kind"] == "checked" for e in events)


@pytest.mark.parametrize(
    "corruption", ["missing", "false", "table", "graph", "readback"]
)
def test_rejects_incomplete_or_changed_evidence(native_case, corruption):
    events = deepcopy(native_case[2]["events"])
    if corruption == "missing":
        events.pop(-2)
    else:
        record = next(
            e
            for e in events
            if e["kind"] == "checked" and e["boundary"] == "refactoring"
        )
        if corruption == "false":
            record["serialization_equivalent"] = 1
        elif corruption == "table":
            record["truth"][0] = "0" * 16
        elif corruption == "graph":
            snapshot = next(
                e
                for e in events
                if e["kind"] == "snapshot" and e["boundary"] == "refactoring"
            )
            snapshot["graph"]["outputs"][0]["complement"] ^= True
        else:
            record["readback_graph"]["outputs"][0]["complement"] ^= True
    with pytest.raises(ValueError):
        _validate(events)


def _stub_tool(tmp_path, native_case, body):
    tool = tmp_path / "tool"
    # Test subprocess uses this environment's interpreter, never a model launcher.
    tool.write_text(f"#!{sys.executable}\n" + body)
    tool.chmod(0o755)
    provenance = native_case[0].parent / "build_provenance.json"
    (tmp_path / "build_provenance.json").write_bytes(provenance.read_bytes())
    return tool


def test_timeout_retains_complete_and_partial_protocol(native_case, tmp_path):
    tool = _stub_tool(
        tmp_path,
        native_case,
        'import sys,time\nprint(\'{"kind":"started","boundary":"refactoring"}\',flush=True)\nsys.stdout.write("{partial")\nsys.stdout.flush()\ntime.sleep(10)\n',
    )
    with pytest.raises(MCOptimizationError) as caught:
        reduce_mc_verilog(
            native_case[1], executable=tool, artifacts=tmp_path / "timeout", timeout=2
        )
    evidence = caught.value.mc_evidence
    assert evidence["error"]["type"] == "TimeoutExpired"
    assert evidence["events"] == [{"kind": "started", "boundary": "refactoring"}]
    assert (tmp_path / "timeout/stdout.jsonl").read_text().endswith("{partial")
    assert evidence["exit_code"] is not None
    assert (tmp_path / "timeout/evidence.json").is_file()


def test_false_native_success_preserves_all_returned_events(native_case, tmp_path):
    events = deepcopy(native_case[2]["events"])
    next(e for e in events if e["kind"] == "checked")["equivalent_original"] = False
    body = (
        "import sys\nsys.stdout.write("
        + repr("\n".join(map(json.dumps, events)) + "\n")
        + ")\n"
    )
    tool = _stub_tool(tmp_path, native_case, body)
    with pytest.raises(MCOptimizationError) as caught:
        reduce_mc_verilog(
            native_case[1], executable=tool, artifacts=tmp_path / "failed"
        )
    assert caught.value.mc_evidence["events"] == events
    assert caught.value.mc_evidence["exit_code"] == 0
    assert caught.value.mc_evidence["status"] == "failed"


@pytest.mark.parametrize("timeout", [0, -1, True, float("nan"), float("inf"), 121])
def test_invalid_timeout_rejected_before_io(timeout):
    with pytest.raises(ValueError, match="timeout"):
        reduce_mc_verilog("absent.v", executable="absent", timeout=timeout)


def test_python_node_cap_precedes_truth_allocation():
    with pytest.raises(ValueError, match="caps"):
        _truth({"size": 4097, "nodes": [], "inputs": [], "outputs": [{}]})


def test_long_graph_and_cycle_are_handled_without_recursion():
    nodes = [{"id": 0, "kind": "constant", "fanins": []}]
    nodes += [{"id": i, "kind": "input", "fanins": []} for i in [1, 2]]
    for node_id in range(3, 1503):
        nodes.append(
            {
                "id": node_id,
                "kind": "xor",
                "fanins": [
                    {"node": node_id - 1, "complement": False},
                    {"node": 1, "complement": False},
                ],
            }
        )
    graph = {
        "size": len(nodes),
        "nodes": nodes,
        "inputs": [1, 2],
        "outputs": [{"node": 1502, "complement": False}],
    }
    assert _truth(graph) == ["0011"]
    nodes[3]["fanins"][0]["node"] = 1502
    with pytest.raises(ValueError, match="Cyclic"):
        _truth(graph)


def test_source_cap_precedes_tool_io(tmp_path):
    source = tmp_path / "source.v"
    source.write_bytes(b" " * (1048576 + 1))
    with pytest.raises(ValueError, match="MiB"):
        reduce_mc_verilog(source, executable="absent")
