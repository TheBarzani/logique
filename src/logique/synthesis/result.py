"""Synthesis output and explicit oracle contracts."""

from dataclasses import dataclass
from collections import Counter
from qiskit import QuantumCircuit
from logique.circuits.records import _qiskit_records


def multiplicative_depth(graph: dict) -> int | None:
    """Largest number of AND nodes on any input-to-output path of an XAG or AIG.

    LUT networks have no multiplicative depth, so they return None.
    """
    nodes = {node["id"]: node for node in graph["nodes"]}
    if any(node["kind"] == "lut" for node in nodes.values()):
        return None
    depth: dict[int, int] = {}
    for node_id in sorted(nodes):  # fanins always precede their nodes
        node = nodes[node_id]
        reached = max((depth[f["node"]] for f in node["fanins"]), default=0)
        depth[node_id] = reached + (node["kind"] == "and")
    return max((depth[output["node"]] for output in graph["outputs"]), default=0)


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
            "multiplicative_depth": multiplicative_depth(graph),
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
