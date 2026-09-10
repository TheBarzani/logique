"""Reproducible Boolean synthesis experiments, independent of graph coloring.

The native process uses pinned Caterpillar dependencies. Only JSON crosses its
boundary; the installed tweedledum extension supplies specialized XAG synthesis.
"""

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import time
import urllib.request

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RXGate, XGate

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "boolean_benchmarks"
NATIVE = ROOT / "native" / "boolean_synthesis"
METHODS = ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")
REFERENCE_REVISION = "4c6f766cd0ffc62d37ab45edfe80c9f1eae44764"


def environment():
    """Return the versions used by this run."""
    return {
        **{
            name: importlib.metadata.version(name)
            for name in ("qiskit", "tweedledum", "numpy")
        },
        "caterpillar": REFERENCE_REVISION,
        "bridge_fixes": "lhrs_uncompute_stack_pop, best_fit_cell_fanout",
    }


def build_native():
    """Configure and build the isolated C++17 helper; first use downloads sources."""
    for command in (
        [
            "cmake",
            "-S",
            str(NATIVE),
            "-B",
            str(NATIVE / "build"),
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        ["cmake", "--build", str(NATIVE / "build"), "-j", "2"],
    ):
        subprocess.run(command, check=True)
    return NATIVE / "build" / "boolean_synthesis"


def download_benchmarks(
    names=("ctrl", "int2float", "cavlc"), *, offline=False, cache=None
):
    """Fetch pinned AIGER/Verilog and license files, checking SHA-256 on every use."""
    manifest = json.loads((DATA / "manifest.json").read_text())
    cache = Path(cache) if cache is not None else DATA / "cache"
    names = tuple(names)
    if not set(names) <= {"ctrl", "int2float", "cavlc", "router"}:
        raise ValueError("Choose ctrl, int2float, cavlc, or router")
    paths = [f"random_control/{name}{ext}" for name in names for ext in (".aig", ".v")]
    for relative in ["LICENSE", *paths]:
        target = cache / relative
        if target.exists():
            payload = target.read_bytes()
        else:
            if offline:
                raise FileNotFoundError(
                    f"Offline cache missing {target}; run download_benchmarks() online once"
                )
            url = f"https://raw.githubusercontent.com/lsils/benchmarks/{manifest['revision']}/{relative}"
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read()
        if hashlib.sha256(payload).hexdigest() != manifest["sha256"][relative]:
            raise ValueError(f"Checksum mismatch: {target}")
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    return {name: cache / "random_control" / f"{name}.aig" for name in names}


def _native(path, method, **parameters):
    executable = NATIVE / "build" / "boolean_synthesis"
    if not executable.exists():
        raise FileNotFoundError(
            "Native helper missing. Run build_native() with CMake and a C++17 compiler installed."
        )
    request = {"path": str(Path(path).resolve()), "method": method, **parameters}
    proc = subprocess.run(
        [str(executable)],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode:
        raise RuntimeError(f"Native synthesis failed ({method}): {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def _tweedledum_records(circuit):
    from tweedledum.ir import Qubit, rotation_angle

    records = []
    for inst in circuit:
        qs = list(inst.qubits())
        controls = [q.uid() for q in qs[:-1]]
        polarity = [q.polarity() == Qubit.Polarity.positive for q in qs[:-1]]
        kind = inst.kind()
        if kind == "ext.parity":
            for c, positive in zip(controls, polarity):
                records.append(
                    {
                        "kind": "x",
                        "controls": [c],
                        "polarity": [positive],
                        "target": qs[-1].uid(),
                    }
                )
        elif kind in ("std.x", "std.rx"):
            record = {
                "kind": "rx" if kind == "std.rx" else "x",
                "controls": controls,
                "polarity": polarity,
                "target": qs[-1].uid(),
            }
            if kind == "std.rx":
                record["angle"] = rotation_angle(inst)
            records.append(record)
        else:
            raise ValueError(f"Unsupported tweedledum operator: {kind}")
    return records


def _qiskit_records(circuit):
    from qiskit.circuit import ControlledGate

    records = []
    for item in circuit.data:
        op = item.operation
        qs = [circuit.find_bit(q).index for q in item.qubits]
        count = op.num_ctrl_qubits if isinstance(op, ControlledGate) else 0
        base = op.base_gate if count else op
        if base.name not in ("x", "rx"):
            raise ValueError(f"Cannot track phases for {op.name}")
        rec = {
            "kind": base.name,
            "controls": qs[:count],
            "target": qs[-1],
            "polarity": [bool((op.ctrl_state >> i) & 1) for i in range(count)],
        }
        if base.name == "rx":
            rec["angle"] = float(base.params[0])
        records.append(rec)
    return records


@lru_cache(maxsize=512)
def _lut_circuit(truth):
    from tweedledum.classical import TruthTable, create_from_binary_string
    from tweedledum.synthesis import pprm_synth

    n = (len(truth) - 1).bit_length()
    if len(truth) != 1 << n:
        raise ValueError("LUT truth table length must be a power of two")
    tt = TruthTable(n)
    create_from_binary_string(tt, truth)
    native = pprm_synth(tt)
    return records_to_qiskit(_tweedledum_records(native), n + 1)


def records_to_qiskit(records, width, *, expand_luts=True):
    """Preserve controlled rotations, control polarities, and LUT semantics."""
    qc = QuantumCircuit(width)
    for rec in records:
        cs, target = rec["controls"], rec["target"]
        polarity = rec["polarity"]
        if len(cs) != len(polarity) or target in cs or len(cs) != len(set(cs)):
            raise ValueError("Invalid gate wiring")
        if rec["kind"] == "lut":
            block = _lut_circuit(rec["truth"])
            for q, positive in zip(cs, polarity):
                if not positive:
                    qc.x(q)
            if expand_luts:
                qc.compose(block, qubits=[*cs, target], inplace=True)
            else:
                qc.append(block.to_gate(label=f"LUT{len(cs)}"), [*cs, target])
            for q, positive in zip(cs, polarity):
                if not positive:
                    qc.x(q)
        else:
            if rec["kind"] not in ("rx", "x"):
                raise ValueError(f"Unsupported gate {rec['kind']}")
            gate = RXGate(rec["angle"]) if rec["kind"] == "rx" else XGate()
            if cs:
                state = sum(int(p) << i for i, p in enumerate(polarity))
                gate = gate.control(len(cs), ctrl_state=state)
            qc.append(gate, [*cs, target])
    return qc


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


@dataclass
class SynthesisResult:
    """Raw clean-output computation plus metadata; use oracle() for XOR targets."""

    circuit: QuantumCircuit
    metadata: dict

    def oracle(self):
        """Compute/copy/uncompute, retaining raw wire indices and appending targets."""
        raw_width = self.circuit.num_qubits
        outputs = self.metadata["output_qubits"]
        qc = QuantumCircuit(raw_width + len(outputs))
        qc.compose(self.circuit, range(raw_width), inplace=True)
        for i, q in enumerate(outputs):
            qc.cx(q, raw_width + i)
        qc.compose(self.circuit.inverse(), range(raw_width), inplace=True)
        return qc

    def phase_oracle(self, output=0):
        """Apply (-1)^f_output(x) with all computation workspace initially zero."""
        qc = self.circuit.copy()
        qc.z(self.metadata["output_qubits"][output])
        qc.compose(self.circuit.inverse(), inplace=True)
        return qc

    def summary(self):
        md = self.metadata
        graph = md["network"]
        kinds = Counter(n["kind"] for n in graph["nodes"])
        roles = set(md["input_qubits"]) | set(md["output_qubits"])
        gates = _qiskit_records(self.circuit)
        return {
            "method": md["method"],
            "k": md["parameters"].get("k"),
            "inputs": len(md["input_qubits"]),
            "outputs": len(md["output_qubits"]),
            "qubits": self.circuit.num_qubits,
            "workspace": self.circuit.num_qubits - len(roles),
            "AND": kinds["and"],
            "XOR": kinds["xor"],
            "LUT": kinds["lut"],
            "gates": self.circuit.size(),
            "depth": self.circuit.depth(),
            "seconds": md["seconds"],
            "gate_types": dict(self.circuit.count_ops()),
            "exact_ccx": sum(
                g["kind"] == "x" and len(g["controls"]) == 2 for g in gates
            ),
            "controlled_rx_pi": sum(g["kind"] == "rx" for g in gates),
            "mcx_3plus": sum(
                g["kind"] == "x" and len(g["controls"]) > 2 for g in gates
            ),
            "lut_blocks": sum(g["kind"] == "lut" for g in md["gates"]),
            "validation": md.get("validation", {}).get("status", "not run"),
        }


def synthesize(path, method="xag", *, k=4, outputs=None, outer_cut=16, inner_cut=4):
    """Import and synthesize one benchmark; output indices are zero-based."""
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    params = {"k": k} if method == "klut_bennett" else {}
    if method == "best_fit":
        params.update(outer_cut=outer_cut, inner_cut=inner_cut)
    if outputs is not None:
        params["outputs"] = list(outputs)
    start = time.perf_counter()
    md = _native(path, method, **params)
    if method == "xag":
        md["gates"], md["num_qubits"] = _xag_records(md["network"])
        n, m = len(md["network"]["inputs"]), len(md["network"]["outputs"])
        md.update(
            input_qubits=list(range(n)), output_qubits=list(range(n, n + m)), steps=[]
        )
    qc = records_to_qiskit(md["gates"], md["num_qubits"])
    md.update(
        parameters=params,
        seconds=time.perf_counter() - start,
        source=str(Path(path).resolve()),
        source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        versions=environment(),
    )
    return SynthesisResult(qc, md)


def truth_outputs(graph, assignments):
    """Evaluate the exported logic network independently of its quantum mapping."""
    values = {node: assignments[i] for i, node in enumerate(graph["inputs"])}
    size = assignments.shape[1]
    for node in graph["nodes"]:
        if node["kind"] == "constant":
            values[node["id"]] = np.full(size, node["value"], dtype=bool)
        elif node["kind"] != "input":
            index = np.zeros(size, dtype=np.int64)
            for i, f in enumerate(node["fanins"]):
                index |= (values[f["node"]] ^ f["inverted"]).astype(np.int64) << i
            table = np.array([b == "1" for b in reversed(node["truth"])])
            values[node["id"]] = table[index]
    return np.array([values[o["node"]] ^ o["inverted"] for o in graph["outputs"]])


def _assignments(n):
    if n > 12:
        raise ValueError(
            "Exhaustive analysis is limited to 12 inputs; use output cones or sampled validation"
        )
    return ((np.arange(1 << n)[None, :] >> np.arange(n)[:, None]) & 1).astype(bool)


def _apply_record(bits, phases, rec, *, inverse=False):
    cs = rec["controls"]
    values = [bits[q] ^ (not p) for q, p in zip(cs, rec["polarity"])]
    if rec["kind"] == "lut":
        index = sum(
            (v.astype(np.int64) << i for i, v in enumerate(values)),
            start=np.zeros(bits.shape[1], dtype=np.int64),
        )
        mask = np.array([b == "1" for b in reversed(rec["truth"])])[index]
    else:
        mask = (
            np.logical_and.reduce(values)
            if values
            else np.ones(bits.shape[1], dtype=bool)
        )
        if rec["kind"] == "rx":
            angle = rec["angle"] * (-1 if inverse else 1)
            if not np.isclose(abs(angle), np.pi):
                raise ValueError("Classical phase tracking only supports Rx(+/-pi)")
            phases[mask] *= -1j if angle > 0 else 1j
    bits[rec["target"]] ^= mask


def validate(result, *, sampled=False, samples=256):
    """Check function values and the wrapped oracle, including coherent phases.

    Exact X/MCX/LUT/Rx(+/-pi) records are monomial: tracking their permutation
    and phase on every input also proves the action on input superpositions.
    Larger examples may explicitly request seeded sampling, which is not proof.
    """
    md = result.metadata
    n = len(md["input_qubits"])
    assignments = (
        np.random.default_rng(7).integers(0, 2, (n, samples)).astype(bool)
        if sampled
        else _assignments(n)
    )
    expected = truth_outputs(md["source_network"], assignments)
    if not np.array_equal(expected, truth_outputs(md["network"], assignments)):
        raise AssertionError("Network transformation changed the Boolean function")
    bits = np.zeros((md["num_qubits"], assignments.shape[1]), dtype=bool)
    bits[md["input_qubits"]] = assignments
    initial = bits.copy()
    phases = np.ones(assignments.shape[1], dtype=complex)
    for rec in md["gates"]:
        _apply_record(bits, phases, rec)
    if not np.array_equal(bits[md["output_qubits"]], expected):
        raise AssertionError("Raw computation produces incorrect outputs")
    others = sorted(
        set(range(bits.shape[0])) - set(md["input_qubits"]) - set(md["output_qubits"])
    )
    raw_clean = not bits[others].any()
    raw_inputs = np.array_equal(bits[md["input_qubits"]], assignments)
    raw_phase = np.allclose(phases, 1)
    exported = initial.copy()
    exported_phases = np.ones(assignments.shape[1], dtype=complex)
    for rec in _qiskit_records(result.circuit):
        _apply_record(exported, exported_phases, rec)
    if not np.array_equal(exported, bits) or not np.allclose(exported_phases, phases):
        raise AssertionError("Qiskit export changed gate semantics or phases")
    # Copying into a separate target is XOR for either initial target value.
    for target_value in (False, True):
        copied = bits[md["output_qubits"]] ^ target_value
        assert np.array_equal(copied, expected ^ target_value)
    for rec in reversed(md["gates"]):
        _apply_record(bits, phases, rec, inverse=True)
    if not np.array_equal(bits, initial) or not np.allclose(phases, 1):
        raise AssertionError("Wrapped oracle does not restore workspace and phase")
    report = {
        "status": "sampled" if sampled else "exhaustive",
        "assignments": assignments.shape[1],
        "raw_workspace_zero": raw_clean,
        "raw_inputs_restored": raw_inputs,
        "raw_phase_exact": bool(raw_phase),
        "wrapped_restoration": True,
    }
    md["validation"] = report
    return report


def workspace_analysis(result, *, expanded=False):
    """Find conjunction-derived facts on reachable states, not automatic rewrites.

    Intervals end conservatively at the next write to either the protecting
    qubit or a proposed borrowed qubit. No permission to borrow is implied.
    """
    md = result.metadata
    assignments = _assignments(len(md["input_qubits"]))
    bits = np.zeros((md["num_qubits"], assignments.shape[1]), dtype=bool)
    bits[md["input_qubits"]] = assignments
    phases = np.ones(assignments.shape[1], dtype=complex)
    records = _qiskit_records(result.circuit) if expanded else md["gates"]
    workspace = sorted(
        set(range(bits.shape[0])) - set(md["input_qubits"]) - set(md["output_qubits"])
    )
    candidates, occupancy = [], []
    for index, rec in enumerate(records):
        clean_target = not bits[rec["target"]].any()
        _apply_record(bits, phases, rec)
        occupancy.append(int(np.any(bits[workspace], axis=1).sum()))
        if (
            rec["kind"] not in ("x", "rx")
            or len(rec["controls"]) < 2
            or not clean_target
        ):
            continue
        branch = bits[rec["target"]]
        if not branch.any():
            continue
        for q, known in zip(rec["controls"], rec["polarity"]):
            if not np.all(bits[q, branch] == known):
                continue
            end = next(
                (
                    j
                    for j in range(index + 1, len(records))
                    if records[j]["target"] in (q, rec["target"])
                ),
                len(records),
            )
            candidates.append(
                {
                    "after_gate": index,
                    "before_gate": end,
                    "condition": f"q{rec['target']} = 1",
                    "borrow_candidate": f"q{q}",
                    "known_value": int(known),
                    "proof": "exhaustive reachable states",
                }
            )
    return {
        "candidates": candidates,
        "occupancy": occupancy,
        "peak_nonzero_workspace": max(occupancy, default=0),
        "granularity": (
            "expanded Qiskit gates" if expanded else "native gate/LUT records"
        ),
        "scope": "Conjunction-derived facts only; consumption and restoration still require proof.",
    }


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


def borrowing_demo():
    """Exact four-control X with either two clean qubits or one plus borrowing.

    Qubits 0..3 are controls, 4 is the arbitrary target, 5.. are clean.
    The borrowed input b is known to be 1 only under the stored a AND b flag.
    """
    reference = QuantumCircuit(7, name="dedicated_workspace")
    reference.ccx(0, 1, 5)
    reference.ccx(5, 2, 6)
    reference.ccx(6, 3, 4)
    reference.ccx(5, 2, 6)
    reference.ccx(0, 1, 5)

    borrowed = QuantumCircuit(6, name="conditional_workspace")
    borrowed.ccx(0, 1, 5)
    borrowed.barrier(label="flag = a AND b")
    borrowed.x(1)
    borrowed.ccx(2, 3, 1)
    borrowed.barrier(label="borrow b")
    borrowed.ccx(5, 1, 4)
    borrowed.barrier(label="consume under flag")
    borrowed.ccx(2, 3, 1)
    borrowed.x(1)
    borrowed.ccx(0, 1, 5)
    return reference, borrowed


def verify_borrowing():
    """Check the entire valid subspace, plus an entangled-reference state."""
    from qiskit.quantum_info import Operator, Statevector

    checks = {}
    for qc in borrowing_demo():
        actual = Operator(qc).data[:, :32]
        expected = np.zeros_like(actual)
        for basis in range(32):
            output = basis ^ (16 if basis & 15 == 15 else 0)
            expected[output, basis] = 1
        if not np.allclose(actual, expected, atol=1e-10):
            raise AssertionError(
                "Borrowing demo failed subspace/phase/restoration check"
            )
        # A reference entangled with the inputs must retain its coherence.
        prep = QuantumCircuit(qc.num_qubits + 1)
        prep.h(0)
        prep.cx(0, qc.num_qubits)
        prep.h(1)
        prep.ry(0.71, 2)
        prep.h(3)
        prep.ry(0.39, 4)
        state = Statevector.from_instruction(prep)
        ideal = QuantumCircuit(qc.num_qubits + 1)
        ideal.mcx([0, 1, 2, 3], 4)
        if not np.allclose(
            state.evolve(qc, range(qc.num_qubits)).data,
            state.evolve(ideal).data,
            atol=1e-10,
        ):
            raise AssertionError("Entangled-reference check failed")
        checks[qc.name] = {
            "qubits": qc.num_qubits,
            "clean_workspace": qc.num_qubits - 5,
            "ccx": qc.count_ops().get("ccx", 0),
            "phase_and_restoration": "passed",
        }
    return checks


def verify_small_quantum(result):
    """Cross-check the actual Qiskit oracle and phase oracle on a superposition."""
    from qiskit.quantum_info import Statevector

    qc = result.oracle()
    if qc.num_qubits > 16:
        raise ValueError("Statevector check limited to 16 qubits")
    md = result.metadata
    n = len(md["input_qubits"])
    assignments = _assignments(n)
    values = truth_outputs(md["source_network"], assignments)
    prep = QuantumCircuit(qc.num_qubits)
    for q in md["input_qubits"]:
        prep.h(q)
    # Test a nonzero target, too; all other clean workspace stays zero.
    prep.x(result.circuit.num_qubits)
    state = Statevector.from_instruction(prep).evolve(qc)
    expected = np.zeros(1 << qc.num_qubits, dtype=complex)
    for x in range(1 << n):
        index = sum(
            int(assignments[i, x]) << q for i, q in enumerate(md["input_qubits"])
        )
        for i in range(values.shape[0]):
            index |= int(values[i, x] ^ (i == 0)) << (result.circuit.num_qubits + i)
        expected[index] = 1 / np.sqrt(1 << n)
    if not np.allclose(state.data, expected, atol=1e-9):
        raise AssertionError("Qiskit oracle differs in values, phases, or restoration")
    phase = result.phase_oracle()
    prep = QuantumCircuit(phase.num_qubits)
    for q in md["input_qubits"]:
        prep.h(q)
    expected = np.zeros(1 << phase.num_qubits, dtype=complex)
    for x in range(1 << n):
        index = sum(
            int(assignments[i, x]) << q for i, q in enumerate(md["input_qubits"])
        )
        expected[index] = (-1 if values[0, x] else 1) / np.sqrt(1 << n)
    if not np.allclose(
        Statevector.from_instruction(prep).evolve(phase).data, expected, atol=1e-9
    ):
        raise AssertionError("Phase oracle differs from (-1)^f(x)")
    return "Qiskit superposition, phase action, and restoration passed"


def export_result(result, directory, name):
    """Save QPY circuits and JSON metadata without flattening high-control gates."""
    from qiskit import qpy

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / f"{name}.qpy").open("wb") as stream:
        qpy.dump([result.circuit, result.oracle()], stream)
    (directory / f"{name}.json").write_text(
        json.dumps(result.metadata, indent=2) + "\n"
    )
