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


def check_connected_wiring(graph):
    layout = bv.schematic_layout(graph)
    expected = Counter(
        (source, row["output"], port, inverted)
        for row in bv.gate_rows(graph)
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
    values = {f"x_{i}": bits for i, bits in enumerate(assignments)}
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
@pytest.mark.parametrize(
    "inversions", [(False, False), (True, False), (False, True), (True, True)]
)
def test_gate_notation_truth(kind, truth, inversions):
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
        bv.evaluate_gate_rows(graph, assignments), truth_outputs(graph, assignments)
    )
    assert "y_{0}" in bv.latex_blocks(graph)[0]
    assert bv.graph_stats(graph)["levels"] == 1
    assert bv.graph_stats(graph)["used_inputs"] == 2


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
