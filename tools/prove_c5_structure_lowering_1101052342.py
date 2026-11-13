"""Independent bounded exact certificate for the saved C5 structure lowering.

No transpilation, native call, Statevector, Operator, or production verifier.
Qiskit is used only to deserialize QPY. Local H/X/T/Z/CX identities compose
over sparse reachable states in Z[zeta_8, 1/2], with a fixed support guard.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time


EXPECTED = "226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b"
ONE = (1, 0, 0, 0, 0)
ZERO = (0, 0, 0, 0, 0)
SUPPORT_CAP = 64


def normal(a: tuple[int, ...]) -> tuple[int, ...]:
    """Canonical (a+b*z+c*z²+d*z³)/2**k, where z**4=-1."""
    *v, k = a
    if not any(v):
        return ZERO
    while k and all(x % 2 == 0 for x in v):
        v = [x // 2 for x in v]
        k -= 1
    return (*v, k)


def add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    k = max(a[4], b[4])
    return normal(
        (*(a[i] * 2 ** (k - a[4]) + b[i] * 2 ** (k - b[4]) for i in range(4)), k)
    )


def neg(a: tuple[int, ...]) -> tuple[int, ...]:
    return (*(-x for x in a[:4]), a[4])


def shift(a: tuple[int, ...], power: int) -> tuple[int, ...]:
    """Multiply by z**power using integer arithmetic only."""
    v = [0] * 4
    for i, x in enumerate(a[:4]):
        j = (i + power) % 8
        v[j % 4] += x if j < 4 else -x
    return (*v, a[4])


def half_sqrt(a: tuple[int, ...]) -> tuple[int, ...]:
    """Multiply by 1/sqrt(2) = (z-z³)/2, exactly."""
    v = add(shift(a, 1), neg(shift(a, 3)))
    return normal((*v[:4], v[4] + 1))


def step(state: dict, name: str, wires: list[int]) -> dict:
    """Apply one independently specified local block, pruning exact zeros only."""
    q = 1 << wires[-1]
    if name == "cx":
        c = 1 << wires[0]
        return {s ^ q if s & c else s: a for s, a in state.items()}
    if name == "x":
        return {s ^ q: a for s, a in state.items()}
    if name in ("t", "tdg", "z"):
        power = {"t": 1, "tdg": -1, "z": 4}[name]
        return {s: shift(a, power) if s & q else a for s, a in state.items()}
    assert name == "h"
    # Enforce the declared memory/support bound BEFORE expanding the map.
    if len(state) * 2 > SUPPORT_CAP:
        raise ValueError("Sparse preallocation support cap exceeded")
    out = {}
    for s, a in state.items():
        b = half_sqrt(a)
        low = s & ~q
        out[low] = add(out.get(low, ZERO), b)
        out[low | q] = add(out.get(low | q, ZERO), neg(b) if s & q else b)
    return {s: a for s, a in out.items() if a != ZERO}


def pi_interval() -> tuple[Fraction, Fraction]:
    """Prove a rational enclosure using Machin's identity and alternating series."""

    def atan_bounds(inverse: int) -> tuple[Fraction, Fraction]:
        # atan(1/m), 80 terms. Alternating-series next term bounds remainder.
        s = sum(
            (
                Fraction((-1) ** k, (2 * k + 1) * inverse ** (2 * k + 1))
                for k in range(80)
            ),
            Fraction(0),
        )
        return s, s + Fraction(1, 161 * inverse**161)

    a, b = atan_bounds(5)
    c, d = atan_bounds(239)
    return 16 * a - 4 * d, 16 * b - 4 * c


def load_blocks(path: Path) -> tuple[list, dict]:
    """Bind every actual instruction to a local identity and bound angle error."""
    from qiskit import qpy

    assert Path(qpy.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise ValueError("This certificate is scoped to the exact saved oracle")
    with path.open("rb") as stream:
        circuits = qpy.load(stream)
    assert len(circuits) == 1
    circuit = circuits[0]
    assert circuit.num_qubits == 22 and len(circuit.data) == 977
    assert circuit.num_clbits == 0 and float(circuit.global_phase) == 0
    lo, hi = pi_interval()
    patterns = {
        (Fraction(1, 2), 0, 1): "h",
        (1, 0, 1): "x",
        (0, 0, Fraction(1, 4)): "t",
        (0, 0, Fraction(-1, 4)): "tdg",
        (0, 0, 1): "z",
    }
    blocks = []
    bound = Fraction(0)
    bindings = []
    for index, item in enumerate(circuit.data):
        op = item.operation
        wires = [circuit.find_bit(q).index for q in item.qubits]
        assert not item.clbits and len(set(wires)) == len(wires)
        if op.name == "cx":
            assert len(wires) == 2 and op.ctrl_state == 1
            name = "cx"
        else:
            assert op.name == "u" and len(wires) == 1
            params = [Fraction(float(p)) for p in op.params]
            matches = []
            for ratios, label in patterns.items():
                errors = [
                    max(abs(p - r * lo), abs(p - r * hi))
                    for p, r in zip(params, ratios)
                ]
                if max(errors) < Fraction(1, 10**15):
                    matches.append((label, errors))
            assert len(matches) == 1
            name, errors = matches[0]
            # U = diag(1,e^i phi) Ry(theta) diag(1,e^i lambda).
            bound += errors[0] / 2 + errors[1] + errors[2]
        blocks.append((name, wires))
        bindings.append(
            dict(
                index=index,
                name=name,
                wires=wires,
                params_hex=[float(p).hex() for p in op.params],
            )
        )
    return blocks, dict(
        qpy_sha256=digest,
        global_phase=0,
        counts=dict(Counter(name for name, _ in blocks)),
        bindings=bindings,
        angle_operator_norm_bound=float(bound),
        rigorous_bound_less_than_1e_12=bound < Fraction(1, 10**12),
        rigorous_bound_less_than_5e_14=bound < Fraction(5, 10**14),
        bound_rational=[str(bound.numerator), str(bound.denominator)],
    )


def predicate(word: int) -> bool:
    """Independent C5 complete predicate, LSB-first two-bit color words."""
    colors = [(word >> (2 * v)) & 3 for v in range(5)]
    return all(c < 3 for c in colors) and all(
        colors[v] != colors[(v + 1) % 5] for v in range(5)
    )


def multiply(a: tuple, b: tuple) -> tuple:
    v = [0] * 4
    for i in range(4):
        for j in range(4):
            v[(i + j) % 4] += a[i] * b[j] * (1 if i + j < 4 else -1)
    return normal((*v, a[4] + b[4]))


def certify(gates: list) -> dict:
    """Prove reachable product states using exact one/two-wire local identities.

    On each basis input every CX control is required to be a definite bit.
    Thus CX acts as I or X on the target without entangling the factors.
    This invariant is CHECKED, never inferred from the transpiler's assumptions.
    Only 22 pairs of ring coefficients are retained per input (linear support).
    """
    trace = hashlib.sha256()
    cx_reads = Counter()
    peak_live_superpositions = 0
    for word in range(1024):
        factors = [(ZERO, ONE) if (word >> q) & 1 else (ONE, ZERO) for q in range(22)]
        for index, (name, wires) in enumerate(gates):
            q = wires[-1]
            if name == "cx":
                control = factors[wires[0]]
                if control[0] == ZERO and control[1] != ZERO:
                    bit = 1
                elif control[1] == ZERO and control[0] != ZERO:
                    bit = 0
                else:
                    raise ValueError(
                        f"Nonclassical CX control at word={word}, gate={index}"
                    )
                cx_reads[bit] += 1
                if bit:
                    factors[q] = tuple(reversed(factors[q]))
            elif name == "x":
                factors[q] = tuple(reversed(factors[q]))
            elif name in ("t", "tdg", "z"):
                a, b = factors[q]
                factors[q] = (a, shift(b, {"t": 1, "tdg": -1, "z": 4}[name]))
            else:
                assert name == "h"
                a, b = factors[q]
                factors[q] = (half_sqrt(add(a, b)), half_sqrt(add(a, neg(b))))
            peak_live_superpositions = max(
                peak_live_superpositions,
                sum(a != ZERO and b != ZERO for a, b in factors),
            )
            trace.update(
                json.dumps([word, index, factors], separators=(",", ":")).encode()
            )
        phase = ONE
        for q, pair in enumerate(factors):
            bit = (word >> q) & 1
            if pair[1 - bit] != ZERO:
                raise AssertionError(f"Restoration failure word={word}, wire={q}")
            phase = multiply(phase, pair[bit])
        if phase != (neg(ONE) if predicate(word) else ONE):
            raise AssertionError(f"Absolute phase failure word={word}, phase={phase}")
    return dict(
        checked_columns=1024,
        marked_columns=sum(predicate(w) for w in range(1024)),
        exact_final_residual=0,
        restored_scratch_wires=list(range(10, 22)),
        local_factor_support=2,
        local_factor_wires=1,
        coefficient_slots_per_input=44,
        cx_classical_control_checks=dict(cx_reads),
        peak_live_superpositions=peak_live_superpositions,
        method="exact product-factor induction; every CX control checked classical on every reachable basis trace",
        reachable_trace_sha256=trace.hexdigest(),
    )


def self_check() -> None:
    """Exact local identity checks, including relative phases and inverse pairs."""
    assert half_sqrt(half_sqrt(ONE)) == (1, 0, 0, 0, 1)
    assert multiply(half_sqrt(ONE), half_sqrt(ONE)) == (1, 0, 0, 0, 1)
    assert shift(ONE, 8) == ONE
    assert shift(ONE, 4) == neg(ONE)
    for s in range(4):
        state = {s: ONE}
        for name, wires in [("h", [0]), ("h", [0])]:
            state = step(state, name, wires)
        assert state == {s: ONE}
        assert step(step(state, "t", [0]), "tdg", [0]) == state
        assert step(step(state, "cx", [0, 1]), "cx", [0, 1]) == state
    # H Z H = X, preserving absolute rather than projective phase.
    for s in range(2):
        state = {s: ONE}
        for gate in ("h", "z", "h"):
            state = step(state, gate, [0])
        assert state == {s ^ 1: ONE}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("oracle", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    self_check()
    blocks, identities = load_blocks(args.oracle)
    result = certify(blocks)
    result.update(identities)
    result["elapsed_seconds"] = time.monotonic() - start
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k
                not in (
                    "bindings",
                    "block_certificates",
                    "bound_rational",
                    "max_support_at_each_cut",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
