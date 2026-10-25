"""Check that visual notation faithfully represents the exported functions."""

from collections import Counter
import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("tweedledum")

from logique.verification.classical import input_assignments, truth_outputs
from logique.visualization import boolean as bv


def check_connected_wiring(graph, *, input_labels=None):
    layout = bv.schematic_layout(graph, input_labels=input_labels)
    expected = Counter(
        (source, row["output"], port, inverted)
        for row in bv.gate_rows(graph, input_labels=input_labels)
        for port, (source, inverted) in enumerate(row["args"])
    )
    actual = Counter(
        (w["source"], w["target"], w["port"], w["inverted"]) for w in layout["wires"]
    )
    assert actual == expected
    assert len(layout["rows"]) == len({r["output"] for r in layout["rows"]})
    for wire in layout["wires"]:
        points = wire["points"]
        np.testing.assert_array_equal(points[0], layout["outputs"][wire["source"]])
        np.testing.assert_array_equal(
            points[-1], layout["pins"][wire["target"]][wire["port"]]
        )
        assert np.isfinite(points).all()
        assert (len(points) - 1) % 3 == 0

    # Evaluate the routed connections, not just the pre-routing equations.
    assignments = input_assignments(len(graph["inputs"]))
    names = bv.signal_names(graph, input_labels=input_labels)
    values = {names[node]: bits for node, bits in zip(graph["inputs"], assignments)}
    values.update(
        {
            "0": np.zeros(assignments.shape[1], bool),
            "1": np.ones(assignments.shape[1], bool),
        }
    )
    for row in layout["rows"]:
        wires = sorted(
            (w for w in layout["wires"] if w["target"] == row["output"]),
            key=lambda w: w["port"],
        )
        args = [values[w["source"]] ^ w["inverted"] for w in wires]
        op = row["op"]
        value = {
            "AND": np.logical_and.reduce,
            "NOR": np.logical_or.reduce,
            "XOR": np.logical_xor.reduce,
            "XNOR": np.logical_xor.reduce,
            "BUF": lambda x: x[0],
            "NOT": lambda x: x[0],
        }[op](args)
        values[row["output"]] = value ^ (op in ("NOR", "XNOR", "NOT"))
    np.testing.assert_array_equal(
        np.array([values[f"y_{i}"] for i in range(len(graph["outputs"]))]),
        truth_outputs(graph, assignments),
    )


@pytest.mark.parametrize("kind,truth", [("and", "1000"), ("xor", "0110")])
@pytest.mark.parametrize("input_labels", [None, ["x_1,0", "x_1,1"]])
@pytest.mark.parametrize(
    "inversions", [(False, False), (True, False), (False, True), (True, True)]
)
def test_gate_notation_truth(kind, truth, inversions, input_labels):
    graph = {
        "inputs": [1, 2],
        "nodes": [{"id": i, "kind": "input", "fanins": []} for i in (1, 2)]
        + [
            {
                "id": 3,
                "kind": kind,
                "truth": truth,
                "fanins": [
                    {"node": i, "inverted": inv} for i, inv in zip((1, 2), inversions)
                ],
            }
        ],
        "outputs": [{"node": 3, "inverted": True}],
    }
    assignments = input_assignments(2)
    np.testing.assert_array_equal(
        bv.evaluate_gate_rows(graph, assignments, input_labels=input_labels),
        truth_outputs(graph, assignments),
    )
    assert "y_{0}" in bv.latex_blocks(graph)[0]
    assert bv.graph_stats(graph)["levels"] == 1
    assert bv.graph_stats(graph)["used_inputs"] == 2


def test_coloring_input_labels_preserve_network_and_connectivity():
    from copy import deepcopy

    pytest.importorskip("graphviz")
    pytest.importorskip("schemdraw")
    import shutil
    import matplotlib.pyplot as plt

    if not shutil.which("dot"):
        pytest.skip("System Graphviz is required")
    # Input order need not match node-number order or vertex-number order.
    graph = {
        "inputs": [8, 2],
        "nodes": [
            {"id": 8, "kind": "input", "fanins": []},
            {"id": 2, "kind": "input", "fanins": []},
            {
                "id": 12,
                "kind": "xor",
                "truth": "0110",
                "fanins": [
                    {"node": 8, "inverted": True},
                    {"node": 2, "inverted": False},
                ],
            },
        ],
        "outputs": [{"node": 12, "inverted": True}],
    }
    original = deepcopy(graph)
    labels = ["x_7,0", "x_3,1"]
    assert bv.signal_names(graph) == {8: "x_0", 2: "x_1", 12: "t_12"}
    assert bv.signal_names(graph, input_labels=labels) == {
        8: "x_7,0",
        2: "x_3,1",
        12: "t_12",
    }
    equations = "".join(bv.latex_blocks(graph, input_labels=labels))
    assert "x_{7,0}" in equations and "x_{3,1}" in equations
    generic = bv.graphviz_graph(graph, "Test")
    labeled = bv.graphviz_graph(graph, "Test", input_labels=labels)
    assert "x_7,0" in labeled.source and "x_3,1" in labeled.source
    assert [line for line in generic.body if " -> " in line] == [
        line for line in labeled.body if " -> " in line
    ]
    assert b"<svg" in labeled.pipe(format="svg")
    check_connected_wiring(graph, input_labels=labels)
    fig = bv.schematic_figure(graph, input_labels=labels)
    assert {"$x_{7,0}$", "$x_{3,1}$"} <= {
        text.get_text() for ax in fig.axes for text in ax.texts
    }
    plt.close(fig)
    lut = deepcopy(graph)
    lut["nodes"][-1]["kind"] = "lut"
    assert bv.lut_table(lut, input_labels=labels)[0]["ports (0 first)"] == (
        "~x_7,0, x_3,1"
    )
    assert graph == original


@pytest.mark.parametrize(
    "labels",
    [
        ["x_1,0"],
        ["x_1,0", "x_1,0"],
        ["", "x"],
        [None, "x"],
        ["t_3", "x"],
        ["y_0", "x"],
        ["0", "x"],
    ],
)
def test_invalid_input_labels(labels):
    graph = {
        "inputs": [1, 2],
        "nodes": [{"id": 3, "kind": "xor"}],
        "outputs": [{"node": 3}],
    }
    with pytest.raises(ValueError, match="label"):
        bv.signal_names(graph, input_labels=labels)


def test_walkthrough_dot_labels_preserve_xag_edges(tmp_path):
    graphviz = pytest.importorskip("graphviz")
    import shutil

    if not shutil.which("dot"):
        pytest.skip("System Graphviz is required")
    source = (
        Path(__file__).resolve().parents[1]
        / "experiments/tutorials/illustrative_example_v2.ipynb"
    )
    notebook = json.loads(source.read_text())
    cell = next(c for c in notebook["cells"] if c["id"] == "1d59e1bc")
    namespace = {
        "expression": "v7_0 ^ v3_1",
        "variables": ["v7_0", "v3_1"],
        "input_labels": ["x_7,0", "x_3,1"],
        "FIGURES": tmp_path,
        "SVG": lambda **kwargs: kwargs["data"],
        "display": lambda value: None,
    }
    exec(compile("".join(cell["source"]), str(source), "exec"), namespace)
    raw = json.loads(graphviz.Source(namespace["raw_dot"]).pipe(format="json"))
    labeled = json.loads(graphviz.Source(namespace["labeled_dot"]).pipe(format="json"))
    for drawing in (raw, labeled):
        nodes = {n["_gvid"]: n["name"] for n in drawing["objects"]}
        drawing["connections"] = [
            (nodes[e["tail"]], nodes[e["head"]], e.get("style"))
            for e in drawing["edges"]
        ]
    assert raw["connections"] == labeled["connections"]
    by_name = {node["name"]: node for node in labeled["objects"]}
    network = namespace["expression_xag"]
    for wire, subscript in enumerate(("7,0", "3,1")):
        assert by_name[str(network.pi_at(wire))]["label"] == (
            f"x<SUB>{subscript}</SUB>"
        )
    assert namespace["xag_dot_path"].read_text() == namespace["labeled_dot"]
    assert b"<svg" in namespace["xag_svg_path"].read_bytes()


@pytest.mark.parametrize("name,outputs", [("int2float", [3]), ("cavlc", [4, 5])])
def test_benchmark_visuals(name, outputs, tmp_path):
    path = Path(__file__).parent / "fixtures/boolean_visuals" / f"{name}.json"
    fixture = json.loads(path.read_text())
    assert fixture["outputs"] == outputs
    graph = fixture["networks"]["xag"]
    assignments = input_assignments(len(graph["inputs"]))
    for network in fixture["networks"].values():
        np.testing.assert_array_equal(
            truth_outputs(network, assignments), truth_outputs(graph, assignments)
        )
    np.testing.assert_array_equal(
        bv.evaluate_gate_rows(graph, assignments), truth_outputs(graph, assignments)
    )
    pytest.importorskip("graphviz")
    import shutil

    if shutil.which("dot"):
        assert b"<svg" in bv.graphviz_graph(graph, name).pipe(format="svg")
    pytest.importorskip("schemdraw")
    if not shutil.which("dot"):
        pytest.skip("System Graphviz is required for connected schematics")
    import matplotlib.pyplot as plt

    check_connected_wiring(graph)
    fig = bv.schematic_figure(graph)
    fig.savefig(tmp_path / "schematic.png")
    plt.close(fig)
    assert (tmp_path / "schematic.png").stat().st_size > 1000
    lut = fixture["networks"]["klut"]
    ledger = bv.lut_table(lut)
    assert len(ledger) == sum(n["kind"] == "lut" for n in lut["nodes"])
    for row in ledger:
        assert int(row["truth (MSB first)"], 2) == int(row["hex"], 16)
        assert len(row["truth (MSB first)"]) == 2 ** len(
            row["ports (0 first)"].split(", ")
        )


def test_connected_constants_aliases_and_repeated_fanins():
    pytest.importorskip("schemdraw")
    pytest.importorskip("graphviz")
    import shutil

    if not shutil.which("dot"):
        pytest.skip("System Graphviz is required")
    graph = {
        "inputs": [1, 2],
        "nodes": [
            {"id": 0, "kind": "constant", "value": False, "fanins": []},
            {"id": 1, "kind": "input", "fanins": []},
            {"id": 2, "kind": "input", "fanins": []},
            {
                "id": 3,
                "kind": "xor",
                "truth": "0110",
                "fanins": [
                    {"node": 1, "inverted": True},
                    {"node": 1, "inverted": False},
                ],
            },
        ],
        "outputs": [
            {"node": 3, "inverted": False},
            {"node": 0, "inverted": True},
            {"node": 1, "inverted": False},
            {"node": 1, "inverted": True},
        ],
    }
    check_connected_wiring(graph)
    assert "x_1" not in bv.schematic_layout(graph)["sources"]
