"""Small phase-sensitive dynamic execution checks, independent target matrices."""

from fractions import Fraction

import pytest

from logique.benchmarks import dynamic_rus as rus
from logique.benchmarks.rus_accounting import retry_moments

np = pytest.importorskip("numpy")


def targets():
    identity = np.eye(2, dtype=complex)
    x = identity[::-1]
    h = (x + np.diag([1, -1])) / np.sqrt(2)
    u = (identity + 1j * np.sqrt(2) * x) / np.sqrt(3)
    ch = np.block([[identity, np.zeros((2, 2))], [np.zeros((2, 2)), h]])
    e = np.kron(x, identity) @ ch @ np.diag([1, 1, -1j, -1j])
    return u, e, e @ np.kron(u, identity)


ALPHA = (1 - 1j) * np.sqrt(3 / 8)
BETA = (1 + 1j) / np.sqrt(8)


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, atol=3e-13, rtol=0)


@pytest.mark.parametrize("direction", ["forward", "inverse"])
@pytest.mark.parametrize("cap", range(5))
def test_actual_branches_phases_cptp_and_resources(direction, cap):
    _, e, v = targets()
    target = v if direction == "forward" else v.conj().T
    paths = rus.enumerate_instrument((direction,), cap=cap, max_branches=5)
    assert len(paths) == cap + 1
    sums = {True: np.zeros((4, 4), complex), False: np.zeros((4, 4), complex)}
    observed = dict.fromkeys(paths[0].resources, 0.0)
    for path in paths:
        word = path.records[0]
        attempts = len(word)
        extension = path.completed or direction == "inverse"
        if path.completed:
            close(path.state, ALPHA * BETA ** (attempts - 1) * target)
            assert word == (1,) * (attempts - 1) + (0,)
        else:
            close(
                path.state,
                BETA**cap * (np.eye(4) if direction == "forward" else e.conj().T),
            )
            assert word == (1,) * cap
        effect = path.state.conj().T @ path.state
        sums[path.completed] += effect
        probability = np.trace(effect).real / 4
        expected = {
            "t": 2 * attempts + 2 * extension,
            "clifford": (5 if direction == "forward" else 7) * attempts
            + 15 * extension,
            "measurement": attempts,
            "reset": attempts,
            "feedforward": attempts,
            "retry": max(0, attempts - 1),
        }
        assert path.resources == expected
        assert path.costs == {"t": expected["t"], **dict.fromkeys(rus.UNPRICED)}
        for key in observed:
            observed[key] += probability * path.resources[key]
        measured = [g.outcome for g in path.events if g.name == "measure"]
        assert tuple(measured) == word
        for i, event in enumerate(path.events):
            if event.name == "measure":
                assert path.events[i + 1].name == "reset"
                assert path.events[i + 2].name == "feedforward"
    s = float(1 - Fraction(1, 4) ** cap)
    close(sums[True], s * np.eye(4))
    close(sums[False], (1 - s) * np.eye(4))
    close(sums[True] + sums[False], np.eye(4))
    analytical = rus.analytical_expectations(direction, cap)
    assert (
        analytical["completion_probability"] == retry_moments(cap).success_probability
    )
    for key in observed:
        assert observed[key] == pytest.approx(float(analytical[key]), abs=3e-13)


@pytest.mark.parametrize("refs", [0, 1, 3])
@pytest.mark.parametrize("direction", ["forward", "inverse"])
def test_arbitrary_entangled_state_execution(refs, direction):
    rng = np.random.default_rng(20261031 + refs)
    state = rng.normal(size=2 ** (2 + refs)) + 1j * rng.normal(size=2 ** (2 + refs))
    state /= np.linalg.norm(state)
    # refs=1 is generally entangled; explicitly check Schmidt rank.
    if refs:
        assert np.linalg.matrix_rank(state.reshape(4, -1)) > 1
    _, _, v = targets()
    target = v if direction == "forward" else v.conj().T
    # Apply to color axes without allocating a five-wire dense operator at refs=3.
    expected = (target @ state.reshape(4, -1)).reshape(-1)
    paths = rus.execute(
        state, (direction,), cap=3, max_branches=4, reference_wires=refs
    )
    assert sum(np.vdot(p.state, p.state).real for p in paths) == pytest.approx(1)
    for path in paths:
        if path.completed:
            close(path.state, ALPHA * BETA ** (len(path.records[0]) - 1) * expected)


def test_full_rank_mixed_entangled_channel_and_abort_distinction():
    rng = np.random.default_rng(20261030)
    m = rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8))
    rho = m @ m.conj().T
    rho /= np.trace(rho)
    _, _, v = targets()
    for direction, target in (("forward", v), ("inverse", v.conj().T)):
        paths = rus.enumerate_instrument((direction,), cap=2, max_branches=3)
        channels = {True: np.zeros((8, 8), complex), False: np.zeros((8, 8), complex)}
        for path in paths:
            op = np.kron(path.state, np.eye(2))
            channels[path.completed] += op @ rho @ op.conj().T
        ideal = np.kron(target, np.eye(2)) @ rho @ np.kron(target.conj().T, np.eye(2))
        close(channels[True], 15 / 16 * ideal)
        assert np.linalg.norm(channels[True] + channels[False] - ideal) > 1e-3


@pytest.mark.parametrize("cap", range(5))
def test_serial_compositions_stop_at_first_abort_and_keep_scalar_phases(cap):
    directions = ("forward", "inverse", "forward")
    paths = rus.enumerate_instrument(directions, cap=cap, max_branches=85)
    assert len(paths) == rus.preflight(directions, cap, 85)
    _, _, v = targets()
    complete = np.zeros((4, 4), complex)
    total = np.zeros((4, 4), complex)
    for path in paths:
        effect = path.state.conj().T @ path.state
        total += effect
        if path.completed:
            complete += effect
            scalar = ALPHA**3 * BETA ** (sum(map(len, path.records)) - 3)
            close(path.state, scalar * v)
        else:
            assert path.records[-1] == (1,) * cap
            assert len(path.records) <= 3
    close(total, np.eye(4))
    close(complete, float((1 - Fraction(1, 4) ** cap) ** 3) * np.eye(4))


def test_inverse_failure_prefix_once_and_wrong_order_counterexamples():
    u, e, v = targets()
    paths = rus.enumerate_instrument(("inverse",), cap=2, max_branches=3)
    retried = paths[1]
    assert retried.records == ((1, 0),)
    prefix = rus.extension_gates("inverse")
    assert retried.events[: len(prefix)] == prefix
    assert sum(g.name in ("t", "tdg") and g.wires == (2,) for g in retried.events) == 2
    close(retried.state, ALPHA * BETA * v.conj().T)
    wrong_repeated = (
        ALPHA * BETA * np.kron(u.conj().T, np.eye(2)) @ e.conj().T @ e.conj().T
    )
    wrong_order = e.conj().T @ np.kron(u.conj().T, np.eye(2))
    assert np.linalg.norm(retried.state - wrong_repeated) > 0.1
    assert np.linalg.norm(wrong_order - v.conj().T) > 0.1
    # A fresh inverse path is not the adjoint of a sampled forward path.
    # Use r=1: at r=2 alpha*beta happens to be real, so those maps coincide.
    forward = rus.enumerate_instrument(("forward",), cap=2, max_branches=3)[0]
    assert np.linalg.norm(paths[0].state - forward.state.conj().T) > 0.1


def test_real_qiskit_primitive_matrix_and_control_counterexample():
    qiskit = pytest.importorskip("qiskit")
    from qiskit.quantum_info import Operator

    # Independent Qiskit execution of the primitive, in MSB order |a,h>.
    primitive = qiskit.QuantumCircuit(2)
    primitive.h(1)
    primitive.t(1)
    primitive.cx(1, 0)
    primitive.h(1)
    primitive.cx(1, 0)
    primitive.t(1)
    primitive.h(1)
    matrix = Operator(primitive).data
    u, e, _ = targets()
    close(matrix[:2, :2], ALPHA * u)
    close(matrix[2:, :2], BETA * np.eye(2))
    paths = rus.enumerate_instrument(("forward",), cap=1, max_branches=2)
    close(e.conj().T @ paths[0].state, np.kron(matrix[:2, :2], np.eye(2)))
    close(paths[1].state, np.kron(matrix[2:, :2], np.eye(2)))
    # Naively control the whole unitary trial. Control-zero always measures 0;
    # control-one has success 3/4. The record leaks the control, causing mixing.
    controlled = qiskit.QuantumCircuit(3)  # MSB |control,a,h>
    controlled.append(primitive.to_gate().control(), [2, 0, 1])
    actual = Operator(controlled).data
    initial = np.zeros(8, complex)
    initial[[0, 4]] = 1 / np.sqrt(2)
    evolved = actual @ initial
    k0 = evolved[[0, 1, 4, 5]]
    k1 = evolved[[2, 3, 6, 7]]
    rho = np.outer(k0, k0.conj()) + np.outer(k1, k1.conj())
    assert np.trace(rho).real == pytest.approx(1)
    assert np.trace(rho @ rho).real < 0.99


def test_saved_dynamic_circuit_roundtrip(tmp_path):
    pytest.importorskip("qiskit")
    from qiskit import qpy

    for direction in ("forward", "inverse"):
        for cap in range(5):
            circuit = rus.build_circuit(direction, cap=cap)
            path = tmp_path / f"{direction}-{cap}.qpy"
            with path.open("wb") as stream:
                qpy.dump(circuit, stream)
            with path.open("rb") as stream:
                loaded = qpy.load(stream)[0]
            assert loaded == circuit
            assert loaded.num_qubits == 3
            assert loaded.metadata["static_substitution_supported"] is False
            if cap:
                assert "if_else" in loaded.count_ops()
                assert "measure" in loaded.count_ops()
                assert "reset" in loaded.count_ops()
            # Independently interpret actual loaded QPY instructions/conditions,
            # using Qiskit gate evolution, rather than the candidate event list.
            qpy_paths = execute_qiskit_columns(loaded)
            actual = rus.enumerate_instrument((direction,), cap=cap, max_branches=5)
            assert set(qpy_paths) == {p.records[0] for p in actual}
            for branch in actual:
                close(qpy_paths[branch.records[0]], branch.state)


def execute_qiskit_columns(circuit):
    """Test-side branch interpreter of real QPY: <=3-wire, four columns."""
    from qiskit.circuit import IfElseOp
    from qiskit.circuit.library import XGate
    from qiskit.quantum_info import Statevector

    data_rows = [0, 4, 2, 6]  # Qiskit basis for |a=0,h,l>, module column order.
    initial = np.zeros((8, 4), complex)
    initial[data_rows, np.arange(4)] = 1

    def evolve(state, operation, qargs):
        return np.column_stack(
            [
                Statevector(state[:, col]).evolve(operation, qargs).data
                for col in range(4)
            ]
        )

    def walk(block, paths, qmap, cmap):
        for instruction in block.data:
            operation = instruction.operation
            qs = [qmap[q] for q in instruction.qubits]
            cs = [cmap[c] for c in instruction.clbits]
            result = []
            for state, classical, word in paths:
                if isinstance(operation, IfElseOp):
                    bit, value = operation.condition
                    selected = 0 if classical[cmap[bit]] == value else 1
                    body = operation.blocks[selected]
                    result.extend(
                        walk(
                            body,
                            [(state, classical, word)],
                            dict(zip(body.qubits, qs)),
                            dict(zip(body.clbits, cs)),
                        )
                    )
                elif operation.name == "measure":
                    for outcome in (0, 1):
                        projected = state.copy()
                        projected[((np.arange(8) >> qs[0]) & 1) != outcome] = 0
                        result.append(
                            (
                                projected,
                                {**classical, cs[0]: outcome},
                                word + (outcome,),
                            )
                        )
                elif operation.name == "reset":
                    # Every reset follows a known Z measurement. No normalization
                    # or phase choice is made, even on zero-norm columns.
                    reset = evolve(state, XGate(), qs) if word[-1] else state
                    result.append((reset, classical, word))
                else:
                    result.append((evolve(state, operation, qs), classical, word))
            paths = result
        return paths

    paths = walk(
        circuit,
        [(initial, {}, ())],
        {q: i for i, q in enumerate(circuit.qubits)},
        {c: i for i, c in enumerate(circuit.clbits)},
    )
    for state, _, _ in paths:
        close(state[[1, 3, 5, 7]], np.zeros((4, 4)))
    return {word: state[data_rows] for state, _, word in paths}


@pytest.mark.parametrize("bad", [-1, True, 1.0, None, 5, 10**50])
def test_preflight_rejects_before_arrays(monkeypatch, bad):
    monkeypatch.setattr(
        np, "eye", lambda *a, **kw: pytest.fail("allocated before cap check")
    )
    with pytest.raises(ValueError):
        rus.enumerate_instrument(("forward",), cap=bad, max_branches=85)


def test_other_preallocation_guards(monkeypatch):
    state = np.zeros(4)
    monkeypatch.setattr(
        np, "eye", lambda *a, **kw: pytest.fail("allocated before guard")
    )
    for directions, cap, maximum in [
        (("forward",) * 4, 1, 85),
        (("forward",) * 3, 4, 84),
        (("controlled",), 1, 85),
        (["forward"], 1, 85),
        (("forward",), 1, True),
        (("forward",), 1, 86),
    ]:
        with pytest.raises(ValueError):
            rus.enumerate_instrument(directions, cap=cap, max_branches=maximum)
    with pytest.raises(ValueError):
        rus.execute(state, (), cap=0, max_branches=1, reference_wires=4)


@pytest.mark.parametrize(
    "state",
    [
        np.zeros(8),
        np.zeros((4, 5)),
        np.ones((4, 1, 1)),
        np.full(4, np.nan),
        np.array(["a"] * 4),
    ],
)
def test_invalid_state_rejects(state):
    with pytest.raises(ValueError):
        rus.execute(state, ("forward",), cap=1, max_branches=2)


def test_empty_program_and_zero_state_keep_every_record():
    state = np.zeros(4, complex)
    paths = rus.execute(state, (), cap=0, max_branches=1)
    assert len(paths) == 1 and paths[0].completed and not paths[0].events
    paths = rus.execute(state, ("forward",), cap=4, max_branches=5)
    assert len(paths) == 5
    assert all(np.linalg.norm(path.state) == 0 for path in paths)
