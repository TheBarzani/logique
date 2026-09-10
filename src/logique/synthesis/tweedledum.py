"""Adapter for specialized tweedledum XAG synthesis."""

from logique.circuits.records import _tweedledum_records


def _xag_records(graph):
    from tweedledum.classical import LogicNetwork
    from tweedledum.synthesis import xag_synth

    network = LogicNetwork()
    signals = {}
    for node in graph["nodes"]:
        kind = node["kind"]
        if kind == "input":
            signals[node["id"]] = network.create_pi()
        elif kind == "constant":
            signals[node["id"]] = network.get_constant(node["value"])
        else:
            cs = [
                ~signals[f["node"]] if f["inverted"] else signals[f["node"]]
                for f in node["fanins"]
            ]
            signals[node["id"]] = getattr(network, f"create_{kind}")(*cs)
    for out in graph["outputs"]:
        network.create_po(
            ~signals[out["node"]] if out["inverted"] else signals[out["node"]]
        )
    circuit = xag_synth(network)
    return _tweedledum_records(circuit), circuit.num_qubits()
