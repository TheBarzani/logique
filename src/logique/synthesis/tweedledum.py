"""Adapter for specialized tweedledum XAG synthesis."""

from pathlib import Path

from logique.circuits.records import _tweedledum_records


def _network_records(network):
    from tweedledum.synthesis import xag_synth

    circuit = xag_synth(network)
    return _tweedledum_records(circuit), circuit.num_qubits()


def _reduce_multiplicative_complexity(source, target):
    """Rewrite a structural Verilog XAG with tweedledum's MC-reduction flow.

    The flow refactors with free XOR gates and rewrites 5-input cuts from a
    database of networks with minimum multiplicative complexity; input and
    output order are preserved. A network without inputs is copied unchanged,
    because tweedledum would declare an empty input list.
    """
    from tweedledum.classical import optimize, read_verilog, write_verilog

    network = read_verilog(str(source))
    if network.num_pis() == 0:
        Path(target).write_bytes(Path(source).read_bytes())
        return target
    optimize(network)
    write_verilog(network, str(target))
    return target


def _xag_records(graph):
    from tweedledum.classical import LogicNetwork

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
    return _network_records(network)
