"""Fail closed on the reviewed two-dirty20 defect without a wide statevector."""

import cmath
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

import pytest

pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import (  # noqa: E402
    CCXGate,
    CXGate,
    HGate,
    MCXGate,
    RCCXGate,
    TGate,
    TdgGate,
    XGate,
    ZGate,
)

from logique.benchmarks import costs, mcx_study  # noqa: E402

POLICY = "2_dirty_kg24"
REJECTION = "2_dirty_kg24 with 20 controls is unsupported"


def test_actual_import_paths():
    root = Path(__file__).resolve().parents[1]
    for module in (costs, mcx_study):
        assert Path(module.__file__).resolve() == (
            root / "src/logique/benchmarks" / (module.__name__.split(".")[-1] + ".py")
        )


def test_registry_and_cached_construction_reject_before_upstream(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("rejected constructor was invoked")

    monkeypatch.setattr(costs._mcx, "synth_mcx_2_dirty_kg24", forbidden)
    for build in (
        costs.MCX_DECOMPOSITIONS[POLICY].build,
        lambda n: costs._construction(POLICY, n),
    ):
        with pytest.raises(ValueError, match=REJECTION):
            build(20)


@pytest.mark.parametrize("controls", range(3, 20))
def test_smaller_two_dirty_counts_still_delegate(monkeypatch, controls):
    sentinel = object()
    calls = []

    def build(n):
        calls.append(n)
        return sentinel

    monkeypatch.setattr(costs._mcx, "synth_mcx_2_dirty_kg24", build)
    assert costs.MCX_DECOMPOSITIONS[POLICY].build(controls) is sentinel
    assert calls == [controls]


@pytest.mark.parametrize("method", sorted(set(costs.MCX_DECOMPOSITIONS) - {POLICY}))
def test_other_twenty_control_policies_are_not_excluded(monkeypatch, method):
    sentinel = object()
    item = costs.MCX_DECOMPOSITIONS[method]
    monkeypatch.setitem(
        costs.MCX_DECOMPOSITIONS, method, replace(item, build=lambda n: sentinel)
    )
    costs._construction.cache_clear()
    try:
        assert costs._construction(method, 20) is sentinel
    finally:
        costs._construction.cache_clear()


@pytest.mark.parametrize("ctrl_state", [0, (1 << 20) - 1])
@pytest.mark.parametrize("entry", ["decompose", "phase", "study"])
def test_entire_block_rejects_before_any_template_or_result(
    monkeypatch, ctrl_state, entry
):
    source = QuantumCircuit(39)
    # A valid gate first must not trigger even a smaller template allocation.
    source.append(MCXGate(3), range(4))
    source.append(MCXGate(20, ctrl_state=ctrl_state), range(21))

    def forbidden(*args, **kwargs):
        pytest.fail("template or lowered result allocated before rejection")

    monkeypatch.setattr(costs, "_construction", forbidden)
    if entry != "study":  # study resolves source records before cost lowering
        monkeypatch.setattr(QuantumCircuit, "copy_empty_like", forbidden)
    with pytest.raises(ValueError, match=REJECTION):
        if entry == "decompose":
            costs.decompose_mcx(source, POLICY)
        elif entry == "phase":
            costs.decompose_phase_oracle(source, 20, POLICY)
        else:
            mcx_study.lower_block(source, POLICY)


def test_isolated_cost_rejects_before_circuit_allocation(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("isolated circuit allocated before rejection")

    monkeypatch.setattr(costs, "QuantumCircuit", forbidden)
    with pytest.raises(ValueError, match=REJECTION):
        costs.isolated_mcx_costs(POLICY, 20)


@lru_cache(maxsize=8)
def _primitive_matrix(name):
    gates = dict(
        x=XGate,
        h=HGate,
        t=TGate,
        tdg=TdgGate,
        z=ZGate,
        cx=CXGate,
        ccx=CCXGate,
        rccx=RCCXGate,
    )
    gate = gates[name]()
    assert gate.num_qubits <= 3
    return gate.to_matrix()


def _sparse_action(record, initial):
    """Apply frozen primitives to <=8 entries, with charged discarded L2 norm."""
    phase = cmath.exp(1j * record["global_phase"])
    state = {word: amplitude * phase for word, amplitude in initial.items()}
    discarded = 0.0
    for name, wires, params in record["gates"]:
        assert not params and len(wires) <= 3
        assert len(set(wires)) == len(wires) and all(0 <= w < 39 for w in wires)
        matrix = _primitive_matrix(name)
        assert matrix.shape == (1 << len(wires), 1 << len(wires))
        mask = sum(1 << w for w in wires)
        result = {}
        for word, amplitude in state.items():
            col = sum(((word >> w) & 1) << j for j, w in enumerate(wires))
            for row in range(len(matrix)):
                value = amplitude * matrix[row, col]
                if value != 0:
                    out = (word & ~mask) | sum(
                        ((row >> j) & 1) << w for j, w in enumerate(wires)
                    )
                    result[out] = result.get(out, 0j) + value
        assert len(result) <= 8
        discarded += math.sqrt(
            sum(abs(a) ** 2 for a in result.values() if abs(a) < 1e-13)
        )
        state = {word: a for word, a in result.items() if abs(a) >= 1e-13}
    assert discarded < 1e-11
    return state


def test_retained_wrong_target_and_coherent_marking_witness():
    frozen = (Path(__file__).parent / "fixtures/mcx_dirty20_rejected.json").read_bytes()
    assert hashlib.sha256(frozen).hexdigest() == (
        "625c4c8600ba779ca464da316ce7ccd92d6b0ae14759dcc9bc17103710466f65"
    )
    fixture = json.loads(frozen)
    assert fixture["width"] == 39
    word = fixture["input"]
    assert word == (1 << 22) + 3 == 4194307
    assert word & ((1 << 20) - 1) == 3  # conjunction false; target20 zero
    assert _sparse_action(fixture["forward"], {word: 1}) == pytest.approx(
        {5242883: 1}, abs=1e-11
    )
    assert _sparse_action(fixture["paired_phase"], {word: 1}) == pytest.approx(
        {word: -1}, abs=1e-11
    )
    # Reference bit39 is never an operand. A second unaffected component makes
    # the erroneous sign relative, so it cannot be removed as a global phase.
    initial = {0: 1 / math.sqrt(2), word | (1 << 39): 1 / math.sqrt(2)}
    expected_wrong = {0: initial[0], word | (1 << 39): -initial[word | (1 << 39)]}
    actual = _sparse_action(fixture["paired_phase"], initial)
    assert actual == pytest.approx(expected_wrong, abs=1e-11)
    error = math.sqrt(sum(abs(actual.get(w, 0) - a) ** 2 for w, a in initial.items()))
    assert error == pytest.approx(math.sqrt(2), abs=1e-11)
