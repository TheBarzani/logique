"""Relative-phase Toffoli substitution inside compute / diagonal / uncompute compositions (ledger C9 follow-up).

Exhaustive: full unitary on every input (dirty ancillas included) for small oracles; for the K3 k=3 oracle
(16 qubits) all clean-input basis states plus seeded random dirty inputs. No private build is used.
"""

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Operator, Statevector  # noqa: E402

from logique.benchmarks import costs  # noqa: E402


def _oracle(compute, phase):
    qc = compute.copy()
    phase(qc)
    qc.compose(compute.inverse(), inplace=True)
    return qc


def _edge_compute(qc, a, b, d, f):
    """f = 1 iff the two-bit colours a, b are equal; d are scratch bits."""
    for i in range(2):
        qc.cx(a[i], d[i])
        qc.cx(b[i], d[i])
    qc.ccx(d[0], d[1], f, ctrl_state=0)


def test_edge_oracle_full_unitary_k3colors():
    compute = QuantumCircuit(7)  # a0 a1 b0 b1 d0 d1 f
    _edge_compute(compute, (0, 1), (2, 3), (4, 5), 6)
    rel = costs.relative_phase_toffolis(compute)
    assert "rccx" in rel.count_ops() and "ccx" not in rel.count_ops()
    assert not np.allclose(Operator(rel).data, Operator(compute).data)  # gadget really differs alone
    phase = lambda qc: qc.z(6)
    np.testing.assert_allclose(
        Operator(_oracle(rel, phase)).data, Operator(_oracle(compute, phase)).data, atol=1e-9
    )


def test_k3_two_colour_oracle_full_unitary():
    # vertices 0,1,2 (1 bit each); d_e = x_u xor x_v on edges (0,1),(0,2),(1,2); good = all d_e = 1.
    compute = QuantumCircuit(7)  # v0 v1 v2 d01 d02 d12 g
    for (u, v), d in zip([(0, 1), (0, 2), (1, 2)], (3, 4, 5)):
        compute.cx(u, d)
        compute.cx(v, d)
    compute.ccx(3, 4, 6)
    rel = costs.relative_phase_toffolis(compute)
    phase = lambda qc: qc.cz(6, 5)
    np.testing.assert_allclose(
        Operator(_oracle(rel, phase)).data, Operator(_oracle(compute, phase)).data, atol=1e-9
    )


def test_k3_three_colour_oracle_basis_and_dirty_inputs():
    n = 6 + 6 + 3 + 1  # colours, d, flags, g
    compute = QuantumCircuit(n)
    col = lambda v: (2 * v, 2 * v + 1)
    for e, (u, v) in enumerate([(0, 1), (0, 2), (1, 2)]):
        d = (6 + 2 * e, 7 + 2 * e)
        for i in range(2):
            compute.cx(col(u)[i], d[i])
            compute.cx(col(v)[i], d[i])
        compute.ccx(d[0], d[1], 12 + e, ctrl_state=0)
    for e in range(3):  # bad_e flags -> good = none bad
        compute.x(12 + e)
    compute.ccx(12, 13, 15)
    rel = costs.relative_phase_toffolis(compute)
    phase = lambda qc: qc.cz(15, 14)
    a, b = _oracle(rel, phase), _oracle(compute, phase)
    rng = np.random.default_rng(20261111)
    inputs = [x for x in range(64)] + [int(v) for v in rng.integers(0, 2**n, 64)]
    for x in inputs:
        sa = Statevector.from_int(x, 2**n).evolve(a)
        sb = Statevector.from_int(x, 2**n).evolve(b)
        assert np.allclose(sa.data, sb.data, atol=1e-9), x


@pytest.mark.parametrize("controls", [3, 4, 5, 6])
def test_clean_tree_equals_mcx_on_clean_ancillas_only(controls):
    tree = costs._tree(controls, uncompute=True)
    n = tree.num_qubits
    ref = QuantumCircuit(n)
    ref.mcx(list(range(controls)), controls)
    ut, ur = Operator(tree).data, Operator(ref).data
    anc = list(range(controls + 1, n))
    clean = [x for x in range(2**n) if all(not (x >> q) & 1 for q in anc)]
    np.testing.assert_allclose(ut[np.ix_(clean, clean)], ur[np.ix_(clean, clean)], atol=1e-9)
    # no leakage out of the clean subspace
    dirty_rows = [x for x in range(2**n) if x not in set(clean)]
    assert np.allclose(ut[np.ix_(dirty_rows, clean)], 0, atol=1e-9)
    # on dirty ancillas the substitution is NOT valid (documented restriction)
    if controls >= 4:
        assert not np.allclose(ut, ur, atol=1e-9)
