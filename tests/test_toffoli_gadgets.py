"""Independent unitary check of the Toffoli gadgets behind ledger rows C8 and C9.

Qubit order (a, b, c), a = most significant bit; target is c. Pure numpy, no logique imports.
  * 7-T exact Toffoli (Amy et al. 2013, Fig. 13 style: 6 CNOT, 7 T/T^dagger, 2 H).
  * 4-T relative-phase Toffoli (Maslov 2016, Fig. 3 dashed gates 2-10: 4 T, 3 CNOT, 2 H).
"""

import numpy as np

I2 = np.eye(2)
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
T = np.diag([1, np.exp(1j * np.pi / 4)])
TD = T.conj().T


def one(g, q):
    ops = [I2, I2, I2]
    ops[q] = g
    return np.kron(np.kron(ops[0], ops[1]), ops[2])


def cnot(ctl, tgt):
    u = np.zeros((8, 8))
    for x in range(8):
        bits = [(x >> 2) & 1, (x >> 1) & 1, x & 1]
        if bits[ctl]:
            bits[tgt] ^= 1
        u[bits[0] * 4 + bits[1] * 2 + bits[2], x] = 1
    return u


def circuit(gates):
    """gates listed in time order; returns the product unitary and the T/T^dagger count."""
    u = np.eye(8, dtype=complex)
    t_count = 0
    for g in gates:
        kind = g[0]
        if kind == "cx":
            u = cnot(g[1], g[2]) @ u
        else:
            u = one({"H": H, "T": T, "Td": TD}[kind], g[1]) @ u
            t_count += kind in ("T", "Td")
    return u, t_count


A, B, C = 0, 1, 2
TOFFOLI = np.eye(8)
TOFFOLI[[6, 7]] = TOFFOLI[[7, 6]]

SEVEN_T = [
    ("H", C),
    ("cx", B, C),
    ("Td", C),
    ("cx", A, C),
    ("T", C),
    ("cx", B, C),
    ("Td", C),
    ("cx", A, C),
    ("T", B),
    ("T", C),
    ("H", C),
    ("cx", A, B),
    ("T", A),
    ("Td", B),
    ("cx", A, B),
]
FOUR_T = [
    ("H", C),
    ("T", C),
    ("cx", B, C),
    ("Td", C),
    ("cx", A, C),
    ("T", C),
    ("cx", B, C),
    ("Td", C),
    ("H", C),
]


def test_seven_t_toffoli_is_exact():
    u, t = circuit(SEVEN_T)
    assert t == 7
    assert np.allclose(u, TOFFOLI, atol=1e-12)


def test_four_t_gadget_is_toffoli_up_to_diagonal_phases():
    u, t = circuit(FOUR_T)
    assert t == 4
    d = u @ TOFFOLI.T  # Toffoli is self-inverse; u = d @ Toffoli
    assert np.allclose(
        d, np.diag(np.diag(d)), atol=1e-12
    ), "not diagonal: gadget is not phase-only"
    assert np.allclose(np.abs(np.diag(d)), 1, atol=1e-12)


def test_four_t_gadget_is_not_exact_toffoli():
    """It must differ from Toffoli by a non-global phase, otherwise the 'relative' label is wrong."""
    u, _ = circuit(FOUR_T)
    d = np.diag(u @ TOFFOLI.T)
    assert not np.allclose(d, d[0], atol=1e-6)
    # record which basis states carry the phase (documented in the report)
    print("phases (units of pi):", np.round(np.angle(d / d[0]) / np.pi, 4))


def test_four_t_gadget_compute_uncompute_cancels():
    """Using the gadget and its inverse (as in a compute/uncompute pair) gives identity: phases cancel."""
    u, _ = circuit(FOUR_T)
    assert np.allclose(u.conj().T @ u, np.eye(8), atol=1e-12)
