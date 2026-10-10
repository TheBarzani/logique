"""Install the manuscript's opt-in MCX tree-depth estimate in Qiskit 2.1.1."""

import ast
from datetime import datetime, timezone
import difflib
import hashlib
import inspect
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODEL = "logique.mcx_tree_bound.v1"
ORIGINAL_SHA256 = "c7737250ee5ade31ef4b264ec302c34831630a6082faf257a8913acf428ac3a0"


def sha256(source: str) -> str:
    """Hash the exact UTF-8 module source."""
    return hashlib.sha256(source.encode()).hexdigest()


def patched_source(source: str) -> str:
    """Add an optional weighting rule to the pinned upstream depth implementation."""
    if sha256(source) != ORIGINAL_SHA256:
        raise ValueError("Expected the original Qiskit 2.1.1 quantumcircuit.py")
    tree = ast.parse(source)
    circuit = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "QuantumCircuit"
    )
    method = next(
        n for n in circuit.body if isinstance(n, ast.FunctionDef) and n.name == "depth"
    )
    lines = source.splitlines(keepends=True)
    original = "".join(lines[method.lineno - 1 : method.end_lineno])
    replacement = original.replace(
        "        ),\n    ) -> int:",
        "        ),\n        *,\n        mcx_decomposition: bool = False,\n    ) -> int:",
        1,
    )
    replacement = replacement.replace(
        '        """Return circuit depth (i.e., length of critical path).',
        '        """Return circuit depth (i.e., length of critical path).\n\n'
        "        Opt-in analytical model: logique.mcx_tree_bound.v1.\n"
        "        See Phys. Rev. A 111, 052611 (2025), Section V. This weights\n"
        "        each n-controlled X by ceil(log2(n)) for n >= 2, and all\n"
        "        other included operations by one. It does not synthesize a\n"
        "        decomposition or account for ancilla allocation, restoration,\n"
        "        measurement/feed-forward, routing, or Clifford+T scheduling.\n"
        "        The mixed weighted depth is not the circuit's T-depth or\n"
        "        Toffoli-only depth, nor a proven global lower bound.\n",
        1,
    )
    replacement = replacement.replace(
        "        Returns:\n",
        "            mcx_decomposition: Use the MCX tree-depth bound as an\n"
        "                operation cost. False preserves upstream behavior.\n\n"
        "        Returns:\n",
        1,
    )
    replacement = replacement.replace(
        "        obj_depths = {",
        "        if mcx_decomposition:\n"
        "            from .controlledgate import ControlledGate\n"
        "            from .library.standard_gates.x import XGate\n\n"
        "        obj_depths = {",
        1,
    )
    replacement = replacement.replace(
        "                new_depth += 1",
        "                operation_depth = 1\n"
        "                if (\n"
        "                    mcx_decomposition\n"
        "                    and isinstance(instruction.operation, ControlledGate)\n"
        "                    and isinstance(instruction.operation.base_gate, XGate)\n"
        "                    and instruction.operation.num_ctrl_qubits >= 2\n"
        "                ):\n"
        "                    # Integer ceil(log2(n)); n counts controls, not wires.\n"
        "                    operation_depth = (instruction.operation.num_ctrl_qubits - 1).bit_length()\n"
        "                new_depth += operation_depth",
        1,
    )
    lines[method.lineno - 1 : method.end_lineno] = [replacement]
    result = "".join(lines)
    compile(result, "quantumcircuit.py", "exec")
    return result


def main() -> None:
    import qiskit
    from qiskit import QuantumCircuit

    target = Path(inspect.getfile(QuantumCircuit)).resolve()
    source = target.read_text()
    model = json.loads((ROOT / "experiments/manuscript/depth-model.json").read_text())
    if sha256(source) == model["patched_source_sha256"]:
        print(f"Already installed {MODEL}: {target}")
        return
    if qiskit.__version__ != "2.1.1":
        raise ValueError("This patch is pinned to Qiskit 2.1.1")
    replacement = patched_source(source)
    if sha256(replacement) != model["patched_source_sha256"]:
        raise ValueError("Patch and recorded model hash disagree")
    backup = (
        ROOT
        / "dump"
        / (
            "qiskit-depth-backup-"
            + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        )
    )
    backup.mkdir(parents=True)
    (backup / "quantumcircuit.py").write_text(source)
    (backup / "applied.patch").write_text(
        "".join(
            difflib.unified_diff(source.splitlines(True), replacement.splitlines(True))
        )
    )
    # Atomic replacement avoids modifying uv's cached wheel through a hard link.
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, suffix=".py")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(replacement)
        os.chmod(temporary, target.stat().st_mode)
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f"Installed {MODEL}: {target}\nOriginal source preserved: {backup}")
    print("Restart existing Python processes or notebook kernels to load the patch.")


if __name__ == "__main__":
    main()
