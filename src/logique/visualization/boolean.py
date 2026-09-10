"""Readable equations, connected Schemdraw circuits, and Boolean DAGs."""

from collections import Counter
import json

import numpy as np


def signal_names(graph):
    names = {n: f"x_{i}" for i, n in enumerate(graph["inputs"])}
    for node in graph["nodes"]:
        if node["kind"] == "constant":
            names[node["id"]] = str(int(node["value"]))
        elif node["kind"] != "input":
            names[node["id"]] = f"t_{node['id']}"
    return names


def gate_rows(graph):
    """Factored equations; De Morgan changes notation, not the network function."""
    names = signal_names(graph)
    rows = []
    for node in graph["nodes"]:
        if node["kind"] in ("input", "constant"):
            continue
        args = [(names[f["node"]], f["inverted"]) for f in node["fanins"]]
        op = node["kind"].upper()
        if op == "AND" and all(inv for _, inv in args):
            op, args = "NOR", [(name, False) for name, _ in args]
        elif op == "XOR":
            op = "XNOR" if sum(inv for _, inv in args) % 2 else "XOR"
            args = [(name, False) for name, _ in args]
        if op not in ("AND", "NOR", "XOR", "XNOR"):
            raise ValueError("Gate equations require an AIG or XAG")
        rows.append({"output": names[node["id"]], "op": op, "args": args})
    rows.extend(
        {
            "output": f"y_{i}",
            "op": "NOT" if out["inverted"] else "BUF",
            "args": [(names[out["node"]], False)],
        }
        for i, out in enumerate(graph["outputs"])
    )
    return rows


def latex_name(name):
    if "_" in name:
        head, number = name.split("_", 1)
        return f"{head}_{{{number}}}"
    return name


def equation_latex(row):
    args = [
        rf"\overline{{{latex_name(name)}}}" if inv else latex_name(name)
        for name, inv in row["args"]
    ]
    operator = {"AND": r"\land", "NOR": r"\lor", "XOR": r"\oplus", "XNOR": r"\oplus"}
    expression = (
        f" {operator[row['op']]} ".join(args) if row["op"] in operator else args[0]
    )
    if row["op"] in ("NOR", "XNOR", "NOT"):
        expression = rf"\overline{{{expression}}}"
    return latex_name(row["output"]) + " &= " + expression


def latex_blocks(graph, rows_per_block=8):
    rows = gate_rows(graph)
    return [
        r"\begin{aligned}"
        + " \\\\ ".join(equation_latex(r) for r in rows[i : i + rows_per_block])
        + r"\end{aligned}"
        for i in range(0, len(rows), rows_per_block)
    ]


def evaluate_gate_rows(graph, assignments):
    """Independent check of the displayed factored equations and gate sheet."""
    values = {f"x_{i}": assignments[i] for i in range(len(graph["inputs"]))}
    values.update(
        {
            "0": np.zeros(assignments.shape[1], bool),
            "1": np.ones(assignments.shape[1], bool),
        }
    )
    for row in gate_rows(graph):
        args = [values[name] ^ inv for name, inv in row["args"]]
        if row["op"] == "AND":
            value = np.logical_and.reduce(args)
        elif row["op"] == "NOR":
            value = ~np.logical_or.reduce(args)
        elif row["op"] in ("XOR", "XNOR"):
            value = np.logical_xor.reduce(args) ^ (row["op"] == "XNOR")
        else:
            value = args[0] ^ (row["op"] == "NOT")
        values[row["output"]] = value
    return np.array([values[f"y_{i}"] for i in range(len(graph["outputs"]))])


def _schematic_gate(row):
    from schemdraw import logic

    classes = {
        "AND": logic.And,
        "NOR": logic.Nor,
        "XOR": logic.Xor,
        "XNOR": logic.Xnor,
        "NOT": logic.Not,
        "BUF": logic.Buf,
    }
    options = (
        {"inputnots": [i + 1 for i, (_, inv) in enumerate(row["args"]) if inv]}
        if len(row["args"]) > 1
        else {"l": 1.5}
    )
    return classes[row["op"]](**options).right()


def schematic_layout(graph: dict) -> dict:
    """Route each factored-netlist fanin to a measured Schemdraw gate pin.

    Graphviz supplies obstacle-aware cubic splines, not the visible symbols.
    The returned wiring is also used by regression tests to check connectivity.
    Coordinates use Schemdraw units; Graphviz points are divided by 72.
    """
    import schemdraw
    from graphviz import Digraph

    rows = gate_rows(graph)
    by_name = {row["output"]: row for row in rows}
    sources = sorted({name for row in rows for name, _ in row["args"]} - by_name.keys())
    dot = Digraph(
        graph_attr={
            "rankdir": "LR",
            "ranksep": "0.9",
            "nodesep": "0.7",
            "splines": "spline",
            "ordering": "in",
        },
        node_attr={"shape": "record", "margin": "0", "fontsize": "1"},
        edge_attr={"arrowhead": "none"},
    )
    for name in sources:
        dot.node(name, label="", shape="point", width="0.03", height="0.03")
    probe = schemdraw.Drawing(show=False)
    probe.config(unit=1)
    geometry = {}
    for row in rows:
        gate = probe.add(_schematic_gate(row).at((0, 0)))
        pins = [
            tuple(getattr(gate, f"in{i+1}") if len(row["args"]) > 1 else gate.start)
            for i in range(len(row["args"]))
        ]
        # Reserve an output stub, so a fanout dot cannot resemble a NOT bubble.
        width = float(gate.end.x) + 0.25
        geometry[row["output"]] = {"pins": pins, "end": tuple(gate.end), "width": width}
        label = "{{<p0> |<p1>}| }" if len(pins) == 2 else "<p0> "
        dot.node(row["output"], label=label, width=str(width), height="1")
    expected = []
    for row in rows:
        for port, (source, inverted) in enumerate(row["args"]):
            wire = {
                "source": source,
                "target": row["output"],
                "port": port,
                "inverted": inverted,
            }
            dot.edge(f"{source}:e", f"{row['output']}:p{port}:w", id=str(len(expected)))
            expected.append(wire)
    layout = json.loads(dot.pipe(format="json"))
    nodes = {node["name"]: node for node in layout["objects"]}
    positions = {
        name: np.array([float(v) / 72 for v in node["pos"].split(",")])
        for name, node in nodes.items()
    }
    origins, outputs, pins = {}, {}, {}
    for name, geom in geometry.items():
        origins[name] = positions[name] - (float(nodes[name]["width"]) / 2, 0)
        outputs[name] = origins[name] + (geom["width"], 0)
        pins[name] = [origins[name] + pin for pin in geom["pins"]]
    outputs.update({name: positions[name] for name in sources})
    wires = []
    for edge in layout.get("edges", []):
        wire = dict(expected[int(edge["id"])])
        curves = [op["points"] for op in edge["_draw_"] if op["op"] == "b"]
        if len(curves) != 1:
            raise ValueError("Expected one continuous Graphviz spline per connection")
        points = np.array(curves[0], dtype=float) / 72
        start, end = outputs[wire["source"]], pins[wire["target"]][wire["port"]]
        # Snap the spline and its tangent handles to exact symbol anchors.
        points[1] += start - points[0]
        points[-2] += end - points[-1]
        points[0], points[-1] = start, end
        if (len(points) - 1) % 3:
            raise ValueError("Invalid cubic spline returned by Graphviz")
        wires.append({**wire, "points": points})
    if len(wires) != len(expected):
        raise ValueError("Graphviz omitted a schematic connection")
    return {
        "rows": rows,
        "sources": sources,
        "origins": origins,
        "outputs": outputs,
        "pins": pins,
        "geometry": geometry,
        "wires": wires,
    }


def schematic_figure(graph: dict):
    """Draw a single fully connected circuit, retaining shared gates and nets."""
    import matplotlib.pyplot as plt
    import schemdraw
    import schemdraw.elements as elm
    from schemdraw.segments import SegmentBezier

    layout = schematic_layout(graph)
    coordinates = np.vstack(list(layout["outputs"].values()))
    span = np.ptp(coordinates, axis=0)
    fig, ax = plt.subplots(
        figsize=(max(10, span[0] * 0.65), max(4, (span[1] + 2) * 0.65))
    )
    drawing = schemdraw.Drawing(canvas=ax, show=False)
    drawing.config(fontsize=11, unit=1, lw=1.5)
    for wire in layout["wires"]:
        element = elm.Element().at((0, 0)).theta(0)
        points = wire["points"]
        # White under-strokes make unconnected crossings visibly pass over.
        for color, width in (("white", 4.5), ("#515c66", 1.2)):
            for i in range(0, len(points) - 1, 3):
                element.segments.append(
                    SegmentBezier(points[i : i + 4], color=color, lw=width)
                )
        drawing.add(element)
    fanouts = Counter(wire["source"] for wire in layout["wires"])
    for row in layout["rows"]:
        name = row["output"]
        gate = drawing.add(_schematic_gate(row).at(layout["origins"][name]))
        drawing.add(elm.Line().at(gate.end).to(layout["outputs"][name]))
        if name.startswith("y_"):
            drawing.add(
                elm.Label()
                .at(layout["outputs"][name] + (0.15, 0))
                .label(f"${latex_name(name)}$", loc="right")
            )
        else:
            center = layout["origins"][name] + (1.05, 0)
            drawing.add(elm.Label().at(center).label(f"${latex_name(name)}$"))
    for name in layout["sources"]:
        point = layout["outputs"][name]
        drawing.add(
            elm.Line().at(point).left(0.35).label(f"${latex_name(name)}$", loc="left")
        )
    for name, count in fanouts.items():
        if count > 1:
            drawing.add(elm.Dot(radius=0.045).at(layout["outputs"][name]))
    drawing.draw(show=False)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    return fig


def graph_stats(graph):
    depths, fanouts = {}, Counter()
    kinds = Counter(n["kind"] for n in graph["nodes"])
    used = set()
    for node in graph["nodes"]:
        depths[node["id"]] = max(
            (depths[f["node"]] + 1 for f in node["fanins"]), default=0
        )
        for f in node["fanins"]:
            fanouts[f["node"]] += 1
            used.add(f["node"])
    for out in graph["outputs"]:
        fanouts[out["node"]] += 1
        used.add(out["node"])
    return {
        "AND": kinds["and"],
        "XOR": kinds["xor"],
        "LUT": kinds["lut"],
        "levels": max(depths[o["node"]] for o in graph["outputs"]),
        "used_inputs": len(used & set(graph["inputs"])),
        "shared_internal_nodes": sum(
            fanouts[n["id"]] > 1
            for n in graph["nodes"]
            if n["kind"] not in ("input", "constant")
        ),
    }


def graphviz_graph(graph, title):
    """Layered vector DAG with explicit fanin ports and inversion markers."""
    from graphviz import Digraph

    dot = Digraph(
        graph_attr={
            "rankdir": "LR",
            "label": title,
            "labelloc": "t",
            "fontname": "Helvetica",
            "fontsize": "18",
            "ranksep": ".6",
            "nodesep": ".25",
            "pad": ".2",
            "bgcolor": "white",
        },
        node_attr={"fontname": "Helvetica", "fontsize": "10", "style": "filled"},
        edge_attr={"arrowsize": ".6", "color": "#69737d"},
    )
    names = signal_names(graph)
    used = {f["node"] for n in graph["nodes"] for f in n["fanins"]} | {
        o["node"] for o in graph["outputs"]
    }
    colors = {"and": "#dcece2", "xor": "#f5e6b8", "lut": "#dfe8f5"}
    for node in graph["nodes"]:
        if node["kind"] in ("input", "constant"):
            if node["id"] in used:
                dot.node(
                    str(node["id"]),
                    names[node["id"]],
                    shape="ellipse",
                    fillcolor="#f2f3f4",
                )
            continue
        label = f"{names[node['id']]} | {node['kind'].upper()}"
        if node["kind"] == "lut":
            label += f"{len(node['fanins'])} | 0x{int(node['truth'], 2):x}"
        ports = " | ".join(f"<p{i}> {i}" for i in range(len(node["fanins"])))
        dot.node(
            str(node["id"]),
            "{{" + ports + "}|" + label + "}",
            shape="record",
            fillcolor=colors[node["kind"]],
        )
        for i, f in enumerate(node["fanins"]):
            dot.edge(
                str(f["node"]),
                f"{node['id']}:p{i}",
                color="#b23c47" if f["inverted"] else "#69737d",
                style="dashed" if f["inverted"] else "solid",
                arrowhead="odot" if f["inverted"] else "normal",
            )
    for i, out in enumerate(graph["outputs"]):
        dot.node(f"out{i}", f"y_{i}", shape="doublecircle", fillcolor="#ffffff")
        dot.edge(
            str(out["node"]),
            f"out{i}",
            color="#b23c47" if out["inverted"] else "#69737d",
            style="dashed" if out["inverted"] else "solid",
            arrowhead="odot" if out["inverted"] else "normal",
        )
    return dot


def lut_table(graph):
    """Exact LUT definitions, with port 0 the least significant assignment bit."""
    names = signal_names(graph)
    return [
        {
            "node": names[n["id"]],
            "ports (0 first)": ", ".join(
                ("~" if f["inverted"] else "") + names[f["node"]] for f in n["fanins"]
            ),
            "truth (MSB first)": n["truth"],
            "hex": f"0x{int(n['truth'], 2):x}",
        }
        for n in graph["nodes"]
        if n["kind"] == "lut"
    ]
