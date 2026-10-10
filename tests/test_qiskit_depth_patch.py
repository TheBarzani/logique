"""Check weighted MCX costs, critical paths, and upstream depth compatibility."""

import ast
import importlib.util
import inspect
import json
from pathlib import Path
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "patch_depth", ROOT / "tools/patch_qiskit_depth.py"
)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


@pytest.fixture
def circuit_class(monkeypatch):
    qiskit = pytest.importorskip("qiskit")
    import qiskit.circuit.quantumcircuit as module

    source = Path(inspect.getfile(qiskit.QuantumCircuit)).read_text()
    model = json.loads((ROOT / "experiments/manuscript/depth-model.json").read_text())
    if patch.sha256(source) == patch.ORIGINAL_SHA256:
        source = patch.patched_source(source)
    assert patch.sha256(source) == model["patched_source_sha256"]
    tree = ast.parse(source)
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "QuantumCircuit"
    )
    method = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "depth"
    )
    code = textwrap.dedent(
        "\n".join(source.splitlines()[method.lineno - 1 : method.end_lineno])
    )
    namespace = dict(vars(module))
    exec(compile(code, "patched_depth", "exec"), namespace)
    monkeypatch.setattr(qiskit.QuantumCircuit, "depth", namespace["depth"])
    return qiskit.QuantumCircuit


@pytest.mark.parametrize(
    "controls, expected",
    [(1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (7, 3), (8, 3), (9, 4), (16, 4), (17, 5)],
)
def test_single_mcx_counts_controls(circuit_class, controls, expected):
    circuit = circuit_class(controls + 1)
    circuit.mcx(list(range(controls)), controls)
    assert circuit.depth() == circuit.depth(mcx_decomposition=False) == 1
    assert circuit.depth(mcx_decomposition=True) == expected


def test_parallel_and_sequential_critical_paths(circuit_class):
    circuit = circuit_class(11)
    circuit.mcx([0, 1, 2, 3, 4], 5)  # Three layers.
    circuit.mcx([6, 7, 8, 9], 10)  # Two layers in parallel.
    assert circuit.depth(mcx_decomposition=True) == 3
    circuit.cx(5, 10)  # Join the two paths.
    circuit.mcx([6, 7, 8, 9], 10)
    assert circuit.depth(mcx_decomposition=True) == 6
    assert circuit.depth() == 3


def test_filters_barriers_and_classical_dependencies(circuit_class):
    circuit = circuit_class(6, 1)
    circuit.mcx([0, 1, 2, 3], 4)
    circuit.barrier()
    circuit.x(5)
    circuit.measure(5, 0)
    circuit.measure(0, 0)
    assert circuit.depth(mcx_decomposition=True) == 5
    assert (
        circuit.depth(
            lambda instruction: instruction.operation.name == "mcx",
            mcx_decomposition=True,
        )
        == 2
    )
    assert circuit.depth(lambda instruction: False, mcx_decomposition=True) == 0
    # A caller may explicitly include directives; preserve that upstream choice.
    assert circuit.depth(lambda instruction: True, mcx_decomposition=True) == 6


def test_gate_semantics_not_names_or_total_wire_count(circuit_class):
    from qiskit.circuit import Gate
    from qiskit.circuit.library import MCXVChain, RXGate, XGate

    circuit = circuit_class(6)
    circuit.append(XGate().control(5, ctrl_state=0), list(range(6)))
    assert circuit.depth(mcx_decomposition=True) == 3
    circuit = circuit_class(6)
    circuit.append(RXGate(0.5).control(5), list(range(6)))
    circuit.append(Gate("mcx", 6, []), list(range(6)))
    assert circuit.depth(mcx_decomposition=True) == 2
    with pytest.warns(DeprecationWarning):
        gate = MCXVChain(5)
    circuit = circuit_class(gate.num_qubits)
    circuit.append(gate, list(range(gate.num_qubits)))
    assert circuit.depth(mcx_decomposition=True) == 3


def test_default_depth_matches_upstream_dag(circuit_class):
    from qiskit.converters import circuit_to_dag
    from qiskit.circuit.random import random_circuit

    assert circuit_class().depth(mcx_decomposition=True) == 0
    for seed in range(5):
        circuit = random_circuit(8, 12, max_operands=4, seed=seed)
        assert circuit.depth() == circuit.depth(mcx_decomposition=False)
        assert circuit.depth() == circuit_to_dag(circuit).depth()


def test_patcher_refuses_unrecognized_source():
    with pytest.raises(ValueError, match="original Qiskit"):
        patch.patched_source("class QuantumCircuit: pass\n")
