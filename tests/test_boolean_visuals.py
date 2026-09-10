"""Check that visual notation faithfully represents the exported functions."""

import numpy as np
import pytest

from vcgc import benchmark_synthesis as bs
from vcgc import boolean_visuals as bv


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
    assignments = bs._assignments(2)
    np.testing.assert_array_equal(
        bv.evaluate_gate_rows(graph, assignments), bs.truth_outputs(graph, assignments)
    )
    assert "y_{0}" in bv.latex_blocks(graph)[0]
    assert bv.graph_stats(graph)["levels"] == 1
    assert bv.graph_stats(graph)["used_inputs"] == 2


@pytest.mark.parametrize("name,outputs", [("int2float", [3]), ("cavlc", [4, 5])])
def test_benchmark_visuals(name, outputs, tmp_path):
    if not (bs.NATIVE / "build/boolean_synthesis").exists():
        pytest.skip("Native bridge not built")
    path = bs.DATA / "cache/random_control" / f"{name}.aig"
    if not path.exists():
        pytest.skip("EPFL cache not downloaded")
    result = bs.synthesize(path, "xag", outputs=outputs)
    graph = result.metadata["network"]
    assignments = bs._assignments(len(graph["inputs"]))
    np.testing.assert_array_equal(
        bv.evaluate_gate_rows(graph, assignments), bs.truth_outputs(graph, assignments)
    )
    pytest.importorskip("graphviz")
    import shutil

    if shutil.which("dot"):
        assert b"<svg" in bv.graphviz_graph(graph, name).pipe(format="svg")
    pytest.importorskip("schemdraw")
    import matplotlib.pyplot as plt

    fig = bv.schematic_figure(graph)
    fig.savefig(tmp_path / "schematic.png")
    plt.close(fig)
    assert (tmp_path / "schematic.png").stat().st_size > 1000
    lut = bs.synthesize(path, "klut_bennett", outputs=outputs, k=4)
    ledger = bv.lut_table(lut.metadata["network"])
    assert len(ledger) == lut.summary()["LUT"]
    for row in ledger:
        assert int(row["truth (MSB first)"], 2) == int(row["hex"], 16)
        assert len(row["truth (MSB first)"]) == 2 ** len(
            row["ports (0 first)"].split(", ")
        )
