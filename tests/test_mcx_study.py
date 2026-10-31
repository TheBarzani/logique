"""Small coherent service and entangled-workspace MCX regressions."""

from pathlib import Path
import math
import os

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import MCXGate  # noqa: E402
from qiskit.quantum_info import Operator, Statevector  # noqa: E402

from logique.benchmarks import mcx_study as s  # noqa: E402
from logique.coloring import ColoringProblem  # noqa: E402

POLICIES = list(s.costs.MCX_DECOMPOSITIONS)


def state(circuit, vector):
    assert circuit.num_qubits <= 18
    assert len(vector) == 1 << circuit.num_qubits
    return Statevector(vector).evolve(circuit).data


def random_clean(original, total, seed=7):
    assert original <= total <= 18
    rng = np.random.default_rng(seed)
    v = np.zeros(1 << total, complex)
    x = rng.normal(size=1 << original) + 1j * rng.normal(size=1 << original)
    v[: 1 << original] = x / np.linalg.norm(x)
    return v


@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("controls", [3, 4])
def test_templates_with_entangled_dirty_and_reference(policy, controls):
    # Original spare wires are unknown/entangled for ALL policies; newly
    # appended clean/throwaway scratch alone starts at zero. Reference is added
    # AFTER lowering, so dirty borrowing cannot touch it.
    source = QuantumCircuit(2 * controls - 1)
    source.append(
        MCXGate(controls, ctrl_state=(1 << controls) - 2), range(controls + 1)
    )
    lowered, info = s.lower_block(source, policy, mirrored=True)
    if policy == "throwaway_tree":
        lowered.z(controls)
        lowered.compose(
            s._inverse(s.lower_block(source, policy, mirrored=True)[0]), inplace=True
        )
    total = lowered.num_qubits + 1
    assert total <= 18
    rng = np.random.default_rng(71 + controls)
    v = np.zeros(1 << total, complex)
    original = source.num_qubits
    coefficients = rng.normal(size=1 << (original + 1)) + 1j * rng.normal(
        size=1 << (original + 1)
    )
    coefficients /= np.linalg.norm(coefficients)
    indices = np.array(
        [
            x % (1 << original) + ((x >> original) << (total - 1))
            for x in range(len(coefficients))
        ]
    )
    v[indices] = coefficients
    # Independent MCX permutation; no Qiskit reference definition/operator.
    expected = np.zeros_like(v)
    for x in indices:
        fire = (int(x) & ((1 << controls) - 1)) == (1 << controls) - 2
        y = int(x) ^ ((1 << controls) if fire else 0)
        if policy == "throwaway_tree":
            expected[x] = v[x] * (-1 if (y >> controls) & 1 else 1)
        else:
            expected[y] = v[x]
    actual = QuantumCircuit(total).compose(lowered, range(lowered.num_qubits))
    np.testing.assert_allclose(state(actual, v), expected, atol=2e-10)
    if s.costs.MCX_DECOMPOSITIONS[policy].workspace == "dirty" and controls >= 4:
        assert info["borrowed_dirty_wires"] > 0


def test_gray_preflight_excludes_before_constructor(monkeypatch):
    assert s.construction_estimate("gray_code", 11)["status"] == "safe"
    for n in range(12, 21):
        assert s.construction_estimate("gray_code", n)["status"] == "excluded"
    monkeypatch.setattr(
        s.costs, "decompose_mcx", lambda *a, **kw: pytest.fail("allocated before guard")
    )
    q = QuantumCircuit(13)
    q.mcx(list(range(12)), 12)
    with pytest.raises(s.StudyExclusion, match="preallocation"):
        s.lower_block(q, "gray_code")
    q = QuantumCircuit(12)
    q.mcx(list(range(11)), 11)
    q.mcx(list(range(11)), 11)
    with pytest.raises(s.StudyExclusion, match="aggregate"):
        s.lower_block(q, "gray_code")


def test_throwaway_requires_mirror_and_monomial_prefix():
    q = QuantumCircuit(5)
    q.mcx([0, 1, 2], 3)
    with pytest.raises(s.StudyExclusion, match="mirror"):
        s.lower_block(q, "throwaway_tree")
    q.h(0)
    with pytest.raises(ValueError, match="Cannot track"):
        s.lower_block(q, "throwaway_tree", mirrored=True)


@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize(
    "method", ["sb_balanced", "structure_sequential", "xag", "klut_bennett", "best_fit"]
)
def test_complete_graph_phase_and_search(policy, method):
    if method in ("xag", "klut_bennett", "best_fit") and not os.environ.get(
        "LOGIQUE_NATIVE_EXECUTABLE"
    ):
        pytest.skip("native service tests require an explicit provenanced executable")
    p = ColoringProblem((-7, 20), ((-7, 20),), 3)
    case = s.assemble_mcx_case(p, method, "R2", policy)
    q = case.circuits["oracle"]
    data = case.metadata["data_qubits"]
    assert q.num_qubits <= 18
    v = np.zeros(1 << q.num_qubits, complex)
    expected = v.copy()
    for x in range(16):
        index = sum(((x >> b) & 1) << w for b, w in enumerate(data))
        v[index] = 0.25
        left, right = x & 3, x >> 2
        expected[index] = -0.25 if left < 3 and right < 3 and left != right else 0.25
    np.testing.assert_allclose(state(q, v), expected, atol=2e-10)
    search = case.circuits["search"]
    assert search.num_qubits <= 18
    predicted = np.zeros(16, complex)
    for x in range(16):
        if x & 3 < 3 and x >> 2 < 3:
            predicted[x] = 1 / 3
    marked = np.array(
        [(x & 3) < 3 and (x >> 2) < 3 and (x & 3) != x >> 2 for x in range(16)]
    )
    phased = predicted.copy()
    phased[marked] *= -1
    predicted = 2 * predicted * np.vdot(predicted, phased) - phased
    physical = np.zeros(1 << search.num_qubits, complex)
    for x, value in enumerate(predicted):
        physical[sum(((x >> b) & 1) << w for b, w in enumerate(data))] = value
    np.testing.assert_allclose(
        state(search, np.eye(1, 1 << search.num_qubits, dtype=complex)[0]),
        physical,
        atol=2e-10,
    )


def test_actual_held_peak_includes_mark_and_not_mirror_sum():
    # k=5 forces 3-bit invalid-code MCXs and seven retained constraints.
    p = ColoringProblem((1, 2), ((1, 2),), 5)
    c = s.assemble_mcx_case(p, "sb_balanced", "R1", "throwaway_tree")
    b = c.metadata["blocks"]
    held = b["prefix"]["held_scratch"]
    assert held > 0 and b["conjunction"]["scratch_capacity"] > 0
    assert (
        c.metadata["peak_mcx_scratch_capacity"]["oracle"]
        == held + b["conjunction"]["scratch_capacity"]
    )
    assert c.metadata["peak_mcx_scratch_capacity"]["search"] == max(
        c.metadata["peak_mcx_scratch_capacity"][x]
        for x in ("preparation", "oracle", "diffusion")
    )


def test_exact_local_ft_depth_and_unpriced_rotations():
    q = QuantumCircuit(3)
    q.ccx(0, 1, 2)
    rows, circuits = s.component_costs(q)
    assert circuits["partial_ft"].num_qubits <= 5
    np.testing.assert_allclose(
        Operator(circuits["partial_ft"]).data, Operator(q).data, atol=1e-12
    )
    assert rows["partial_ft"]["t_count"] == 7
    assert rows["partial_ft"]["t_depth"] == 3
    assert rows["partial_ft"]["total_t_count"] is None
    q.rz(math.pi / 7, 0)
    rows, _ = s.component_costs(q)
    assert rows["partial_ft"]["rotation_count"] == 1
    assert rows["routed"]["cost"] is None


def test_dutta_is_analytical_and_out_of_range_explicit():
    rows = s.analytical_dutta_rows()
    assert len(rows) == 54
    assert any(r["status"] == "excluded" for r in rows)
    assert all(
        r["static_unitary_t_count"] is None
        for r in rows
        if r["status"] == "analytical_only"
    )


def test_import_is_candidate():
    assert Path(s.__file__).resolve().is_relative_to(Path.cwd() / "src")


def test_throwaway_actual_inverse_after_control_changes():
    from qiskit.circuit.library import RXGate

    source = QuantumCircuit(6, global_phase=0.127)
    source.append(MCXGate(4, ctrl_state=13), [0, 1, 2, 3, 4])
    source.mcx([1, 3, 4], 5)
    source.append(RXGate(-math.pi).control(2), [0, 5, 2])
    forward, info = s.lower_block(source, "throwaway_tree", mirrored=True)
    actual = forward.copy()
    actual.z(5)
    actual.compose(s._inverse(forward), inplace=True)
    v = random_clean(6, actual.num_qubits)
    expected = v.copy()
    for x in range(64):
        y = x ^ (16 if x & 15 == 13 else 0)
        y ^= 32 if all((y >> b) & 1 for b in (1, 3, 4)) else 0
        expected[x] *= -1 if (y >> 5) & 1 else 1
    np.testing.assert_allclose(state(actual, v), expected, atol=2e-10)
    assert info["held_scratch"] == 3  # held once, never doubled for inverse
