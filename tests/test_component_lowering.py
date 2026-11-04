"""Signed component contracts; bounded matrices and independent XOR references."""

import ast
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
from qiskit import QuantumCircuit, qpy, transpile  # noqa: E402
from qiskit.quantum_info import Operator, Statevector  # noqa: E402
from logique.benchmarks import costs, metrics, routing  # noqa: E402

SEED = 1101052342


def component(controls=3):
    """Nontrivial scalar, open controls, nonadjacent target and idle spectator."""
    circuit = QuantumCircuit(controls + 2)
    # Target is wire 0, spectator is the high wire; controls use reversed order.
    circuit.mcx(list(range(controls, 0, -1)), 0, ctrl_state=1)
    circuit.global_phase = 0.23
    return circuit


def xor_reference(width, controls):
    """Construct basis permutation and scalar independently of Qiskit gates."""
    assert width <= 18  # Before exponentially sized arrays.
    indices = np.arange(1 << width)
    packed = sum(((indices >> q) & 1) << i for i, q in enumerate(controls))
    outputs = indices.copy()
    outputs[packed == 1] ^= 1
    return outputs, np.exp(0.23j)


def dense(circuit):
    assert circuit.num_qubits <= 5  # Before Operator's exponential allocation.
    return Operator(circuit).data


def coherent(width):
    assert width <= 18  # Before random vectors and Statevector allocation.
    rng = np.random.default_rng(SEED)
    data = rng.normal(size=1 << width) + 1j * rng.normal(size=1 << width)
    return data / np.linalg.norm(data)


@pytest.mark.parametrize("level", [0, 1, 3])
def test_common_lowering_all_columns_nonzero_target_and_spectator(level):
    circuit = component()
    lowered = metrics.lower_circuit(
        circuit, basis_gates=["u", "cx"], optimization_level=level, seed=7
    )
    outputs, phase = xor_reference(5, [3, 2, 1])
    expected = np.zeros((32, 32), dtype=complex)
    expected[outputs, np.arange(32)] = phase
    # All 32 columns, including both target/spectator sectors; no phase fit.
    np.testing.assert_allclose(dense(lowered), expected, atol=1e-12, rtol=0)


@pytest.mark.parametrize("controls", [3, 4, 5])
def test_coherent_component_and_actual_emitted_inverse(controls):
    circuit = component(controls)
    lowered = metrics.lower_circuit(circuit, basis_gates=["u", "cx"])
    width = lowered.num_qubits
    assert width == controls + 2 <= 18
    assert all(inst.operation.num_qubits <= 2 for inst in lowered.data)
    data = coherent(width)
    outputs, phase = xor_reference(width, list(range(controls, 0, -1)))
    expected = np.empty_like(data)
    expected[outputs] = data * phase
    actual = Statevector(data.copy()).evolve(lowered)
    np.testing.assert_allclose(actual.data, expected, atol=1e-12, rtol=0)
    # Invert the emitted instructions, including their scalar, on distinct buffers.
    restored = actual.evolve(lowered.inverse())
    np.testing.assert_allclose(restored.data, data, atol=1e-12, rtol=0)


def test_mcx_clifford_lowering_preserves_unknown_spectator_and_actual_inverse():
    circuit = component()
    expanded, info = costs.decompose_mcx(circuit, "noaux_v24")
    assert expanded.num_qubits == 5 and info["appended_ancillas"] == 0
    lowered = costs.clifford_t(expanded)
    outputs, phase = xor_reference(5, [3, 2, 1])
    expected = np.zeros((32, 32), dtype=complex)
    expected[outputs, np.arange(32)] = phase
    np.testing.assert_allclose(dense(lowered), expected, atol=1e-12, rtol=0)
    data = coherent(5)
    restored = Statevector(data.copy()).evolve(lowered).evolve(lowered.inverse())
    np.testing.assert_allclose(restored.data, data, atol=1e-12, rtol=0)


def test_throwaway_marking_uses_actual_inverse_and_restores_held_scratch():
    compute = component()
    oracle, info = costs.decompose_phase_oracle(compute, 0, "throwaway_tree")
    assert info["held_throwaway_ancillas"] == 1
    assert oracle.num_qubits == 6 <= 18
    lowered = metrics.lower_circuit(oracle, basis_gates=["u", "cx"])
    # Scratch alone starts clean; data, output and spectator are coherent.
    data = coherent(5)
    state = np.zeros(1 << 6, dtype=complex)
    state[:32] = data
    outputs, _ = xor_reference(5, [3, 2, 1])
    expected = state.copy()
    expected[:32] *= 1 - 2 * (outputs & 1)
    actual = Statevector(state.copy()).evolve(lowered).data
    np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
    assert np.sum(np.abs(actual[32:]) ** 2) < 1e-24


def test_routing_preserves_component_entry_contract(monkeypatch):
    calls = []

    def route(circuit, **kwargs):
        assert kwargs["qubits_initially_zero"] is False
        assert kwargs["num_processes"] == 1
        calls.append(kwargs["seed_transpiler"])
        return transpile(
            circuit,
            basis_gates=["u", "cx"],
            optimization_level=kwargs["optimization_level"],
            seed_transpiler=kwargs["seed_transpiler"],
            qubits_initially_zero=kwargs["qubits_initially_zero"],
            num_processes=kwargs["num_processes"],
        )

    circuit = component()
    # routed_metrics requires explicitly expanded MCX, retaining spectator action.
    expanded, _ = costs.decompose_mcx(circuit, "noaux_v24")

    def measured(routed, target):
        np.testing.assert_allclose(dense(routed), dense(circuit), atol=1e-12, rtol=0)
        return {"two_qubit_count": 0, "depth": 0}

    monkeypatch.setattr(routing, "transpile", route)
    monkeypatch.setattr(routing, "_seed_metrics", measured)
    backend = SimpleNamespace(name="bounded-probe", num_qubits=5, target=None)
    routing.routed_metrics(expanded, backend=backend, seeds=(11, 23))
    assert calls == [11, 23]


def test_noisy_component_lowering_on_coherent_nonzero_entry(monkeypatch):
    import logique.benchmarks.noisy_iterations as noisy
    import logique.circuits.structure as structure
    from logique.coloring import ColoringProblem

    circuit = component()
    monkeypatch.setattr(
        structure,
        "structure_oracle",
        lambda *a, **kw: SimpleNamespace(phase_oracle=lambda: circuit),
    )
    problem = ColoringProblem((0, 1), ((0, 1),), 2)
    parts, _ = noisy._components(problem, "R1")
    assert [p.num_qubits for p in parts] == [2, 5, 2]
    np.testing.assert_allclose(dense(parts[1]), dense(circuit), atol=1e-12, rtol=0)


def test_ideal_saved_components_preserve_absolute_operators(tmp_path):
    import json
    from logique.benchmarks.iteration_study import simulate_case
    from logique.circuits.structure import structure_oracle
    from logique.coloring import ColoringProblem

    config = json.loads(Path("configs/iteration_pilot.json").read_text())
    config["iteration_limit"] = 1
    case = {"name": "edge", "vertices": [0, 1], "edges": [[0, 1]], "colors": 2}
    output = tmp_path / "case"
    result = simulate_case(case, "R1", config, output)
    assert all(row["comparison_passed"] for row in result["rows"])
    with (output / "oracle.qpy").open("rb") as stream:
        saved = qpy.load(stream)[0]
    logical = structure_oracle(ColoringProblem((0, 1), ((0, 1),), 2)).phase_oracle()
    np.testing.assert_allclose(dense(saved), dense(logical), atol=1e-12, rtol=0)


@pytest.mark.parametrize(
    "module_name",
    ["metrics", "costs", "routing", "iteration_study", "noisy_iterations"],
)
def test_every_assigned_transpiler_has_explicit_reuse_and_serial_contract(module_name):
    module = importlib.import_module(f"logique.benchmarks.{module_name}")
    tree = ast.parse(Path(module.__file__).read_text())
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "transpile"
    ]
    assert calls
    for call in calls:
        kwargs = {kw.arg: kw.value for kw in call.keywords}
        assert ast.literal_eval(kwargs["qubits_initially_zero"]) is False
        assert ast.literal_eval(kwargs["num_processes"]) == 1


def test_regression_allocation_guards_reject_before_arrays():
    with pytest.raises(AssertionError):
        coherent(19)
    with pytest.raises(AssertionError):
        xor_reference(19, [1, 2, 3])
    with pytest.raises(AssertionError):
        dense(QuantumCircuit(6))
