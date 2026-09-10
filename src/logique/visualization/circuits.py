"""Circuit excerpts and small logic-network diagrams."""

from logique.circuits.records import records_to_qiskit


def circuit_window(result, start=0, count=25, *, expand_luts=False):
    """A labeled gate excerpt, not an independently executable sub-oracle."""
    records = result.metadata["gates"][start : start + count]
    qc = records_to_qiskit(records, result.circuit.num_qubits, expand_luts=expand_luts)
    figure = qc.draw("mpl", idle_wires=False, fold=90)
    # Place LUT names between wires so Qiskit's input indices remain legible.
    for label in figure.axes[0].texts:
        if label.get_text().startswith("LUT"):
            label.set_y(label.get_position()[1] + 0.28)
    return figure


def network_figure(result, *, source=False):
    """Draw a small Boolean network, labeling inversions on its edges."""
    import matplotlib.pyplot as plt
    import networkx as nx

    network = result.metadata["source_network" if source else "network"]
    if len(network["nodes"]) > 60:
        raise ValueError(
            "Select a smaller output cone for a readable network diagram (at most 60 nodes)"
        )
    graph = nx.DiGraph()
    labels, edge_labels = {}, {}
    for node in network["nodes"]:
        graph.add_node(node["id"])
        labels[node["id"]] = f"{node['id']}:{node['kind']}"
        for f in node["fanins"]:
            graph.add_edge(f["node"], node["id"])
            if f["inverted"]:
                edge_labels[f["node"], node["id"]] = "NOT"
    for i, out in enumerate(network["outputs"]):
        key = f"y{i}"
        graph.add_edge(out["node"], key)
        labels[key] = key
        if out["inverted"]:
            edge_labels[out["node"], key] = "NOT"
    graph.remove_nodes_from(list(nx.isolates(graph)))
    labels = {node: label for node, label in labels.items() if node in graph}
    positions = {}
    for level, nodes in enumerate(nx.topological_generations(graph)):
        for i, node in enumerate(nodes):
            positions[node] = (level, i - (len(nodes) - 1) / 2)
    fig, ax = plt.subplots(figsize=(10, 4))
    nx.draw_networkx(
        graph,
        positions,
        labels=labels,
        ax=ax,
        node_size=1100,
        node_color=["#d7eadf" if isinstance(n, str) else "#e0e8f2" for n in graph],
        font_size=8,
        arrowsize=15,
    )
    nx.draw_networkx_edge_labels(
        graph, positions, edge_labels=edge_labels, ax=ax, font_size=7
    )
    ax.set_axis_off()
    ax.margins(0.12)
    fig.tight_layout()
    return fig
