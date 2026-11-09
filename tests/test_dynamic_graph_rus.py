"""Independent small-matrix and actual QPY checks of the edge instrument."""

from pathlib import Path

import pytest

from logique.benchmarks import dynamic_graph_rus as graph

np = pytest.importorskip("numpy")
ALPHA = (1 - 1j) * np.sqrt(3 / 8)
BETA = (1 + 1j) / np.sqrt(8)


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, atol=3e-13, rtol=0)


def targets():
    """Independent admitted V columns; no candidate gates or target helpers."""
    v = np.array(
        [
            [1, 1, -1j / np.sqrt(2), -1j / np.sqrt(2)],
            [1, -1, -1j / np.sqrt(2), 1j / np.sqrt(2)],
            [1, 0, 1j * np.sqrt(2), 0],
            [0, 1, 0, 1j * np.sqrt(2)],
        ],
        complex,
    ) / np.sqrt(3)
    u = np.eye(2) + 1j * np.sqrt(2) * np.array([[0, 1], [1, 0]])
    u /= np.sqrt(3)
    e = v @ np.kron(u.conj().T, np.eye(2))
    a = np.kron(v, v)
    m = np.diag(
        [-1 if i // 4 < 3 and i % 4 < 3 and i // 4 != i % 4 else 1 for i in range(16)]
    )
    s0 = -np.eye(16)
    s0[0, 0] = 1
    d = a @ s0 @ a.conj().T
    return v, e, a, m, s0, d


def expected_branch(branch, program, cap):
    """Derive the exact stopped prefix from analytical maps, with scalar phases."""
    v, e, _, m, s0, _ = targets()
    result = np.eye(16, dtype=complex)
    records = iter(branch.records)
    for index, stage in enumerate(graph.stages(program)):
        if stage.kind == "mark":
            result = m @ result
        elif stage.kind == "zero_reflection":
            result = s0 @ result
        else:
            record = next(records)
            assert (record.stage, record.vertex, record.direction) == (
                index,
                stage.vertex,
                stage.kind,
            )
            success = bool(record.outcomes) and record.outcomes[-1] == 0
            if success:
                assert record.outcomes == (1,) * (len(record.outcomes) - 1) + (0,)
                local = (
                    ALPHA
                    * BETA ** (len(record.outcomes) - 1)
                    * (v if stage.kind == "forward" else v.conj().T)
                )
            else:
                assert record.outcomes == (1,) * cap
                assert not branch.completed and branch.stopped_at == index
                local = BETA**cap * (
                    np.eye(4) if stage.kind == "forward" else e.conj().T
                )
            lifted = (
                np.kron(local, np.eye(4))
                if stage.vertex == 0
                else np.kron(np.eye(4), local)
            )
            result = lifted @ result
            if not success:
                break
    assert next(records, None) is None
    return result


@pytest.mark.parametrize(
    "program,cap",
    [
        (p, c)
        for p in ("prepare", "mark", "reflect", "iterate", "search")
        for c in range(5)
        if p != "search" or c <= 2
    ],
)
def test_all_input_columns_exact_prefixes_completeness_and_stop_resources(program, cap):
    paths_by_columns = []
    for start in range(0, 16, 4):
        paths_by_columns.append(
            graph.execute(
                np.eye(16, dtype=complex)[:, start : start + 4],
                program,
                cap=cap,
                max_branches=341,
            )
        )
    paths = paths_by_columns[0]
    assert len(paths) == graph.preflight(program, cap, 341)
    effect = np.zeros((16, 16), complex)
    complete = np.zeros_like(effect)
    observed = dict.fromkeys(paths[0].resources, 0.0)
    for number, branch in enumerate(paths):
        actual = np.concatenate([p[number].state for p in paths_by_columns], axis=1)
        close(actual, expected_branch(branch, program, cap))
        local_effect = actual.conj().T @ actual
        effect += local_effect
        if branch.completed:
            complete += local_effect
            assert branch.stopped_at is None
        probability = np.trace(local_effect).real / 16
        for key in observed:
            observed[key] += probability * branch.resources[key]
        assert branch.costs == {
            "t": branch.resources["t"],
            **dict.fromkeys(graph.primitive.UNPRICED),
        }
        assert branch.resources["measurement"] == sum(
            len(r.outcomes) for r in branch.records
        )
        assert branch.resources["reset"] == branch.resources["measurement"]
        # Prefix costs count each reached inverse E-dagger once, even cap0.
        extensions = sum(
            r.direction == "inverse" or bool(r.outcomes and r.outcomes[-1] == 0)
            for r in branch.records
        )
        phase_t = sum(
            126 if s.kind == "mark" else 21 if s.kind == "zero_reflection" else 0
            for i, s in enumerate(graph.stages(program))
            if branch.completed or i < branch.stopped_at
        )
        assert (
            branch.resources["t"]
            == 2 * branch.resources["measurement"] + 2 * extensions + phase_t
        )
    close(effect, np.eye(16))
    analytical = graph.analytical_expectations(program, cap)
    close(complete, float(analytical["completion_probability"]) * np.eye(16))
    for key, value in observed.items():
        assert value == pytest.approx(float(analytical[key]), abs=3e-13, rel=3e-13)


@pytest.mark.parametrize("program", ["prepare", "reflect", "iterate"])
def test_cap4_arbitrary_entangled_reference_and_no_deterministic_substitution(program):
    rng = np.random.default_rng(20261109)
    state = rng.normal(size=128) + 1j * rng.normal(size=128)
    state /= np.linalg.norm(state)
    assert np.linalg.matrix_rank(state.reshape(16, 8)) == 8
    paths = graph.execute(state, program, cap=4, max_branches=341, reference_wires=3)
    completed_probability = 0.0
    discarded_fidelity = 0.0
    _, _, a, m, _, d = targets()
    target = {"prepare": a, "reflect": d, "iterate": d @ m}[program]
    ideal = (target @ state.reshape(16, 8)).reshape(-1)
    for branch in paths:
        expected = (expected_branch(branch, program, 4) @ state.reshape(16, 8)).reshape(
            -1
        )
        close(branch.state, expected)
        p = np.vdot(branch.state, branch.state).real
        completed_probability += p if branch.completed else 0
        discarded_fidelity += abs(np.vdot(ideal, branch.state)) ** 2
    assert sum(np.vdot(b.state, b.state).real for b in paths) == pytest.approx(1)
    assert completed_probability == pytest.approx(
        float(graph.analytical_expectations(program, 4)["completion_probability"])
    )
    assert discarded_fidelity < 0.9999


def test_single_edge_overshoot_is_a_loss_and_aborts_remain_flagged():
    initial = np.zeros(16, complex)
    initial[0] = 1
    paths = graph.execute(initial, "search", cap=2, max_branches=127)
    valid = [4 * a + b for a in range(3) for b in range(3) if a != b]
    completed = sum(np.vdot(b.state, b.state).real for b in paths if b.completed)
    proper = sum(
        np.vdot(b.state[valid], b.state[valid]).real for b in paths if b.completed
    )
    assert completed == pytest.approx((15 / 16) ** 6)
    assert proper / completed == pytest.approx(2 / 27)
    assert 2 / 27 < 2 / 3


def qpy_execute(circuit, data):
    """Execute actual QPY via Qiskit Statevector; <=6 wires, no dense operator."""
    from qiskit.circuit import IfElseOp
    from qiskit.circuit.library import XGate
    from qiskit.quantum_info import Statevector

    rows = np.array(
        [
            sum(((i >> (3 - bit)) & 1) << (2 + bit) for bit in range(4))
            for i in range(16)
        ]
    )
    initial = np.zeros(64, complex)
    initial[rows] = data

    def walk(block, paths, qmap, cmap):
        for instruction in block.data:
            op = instruction.operation
            qs = [qmap[q] for q in instruction.qubits]
            cs = [cmap[c] for c in instruction.clbits]
            out = []
            for state, bits, word in paths:
                if isinstance(op, IfElseOp):
                    bit, value = op.condition
                    body = op.blocks[0 if bits[cmap[bit]] == value else 1]
                    out.extend(
                        walk(
                            body,
                            [(state, bits, word)],
                            dict(zip(body.qubits, qs)),
                            dict(zip(body.clbits, cs)),
                        )
                    )
                elif op.name == "measure":
                    for outcome in (0, 1):
                        projected = state.copy()
                        projected[((np.arange(64) >> qs[0]) & 1) != outcome] = 0
                        out.append(
                            (projected, {**bits, cs[0]: outcome}, word + (outcome,))
                        )
                elif op.name == "reset":
                    reset = (
                        Statevector(state).evolve(XGate(), qs).data
                        if word[-1]
                        else state
                    )
                    out.append((reset, bits, word))
                else:
                    out.append((Statevector(state).evolve(op, qs).data, bits, word))
            paths = out
        return paths

    paths = walk(
        circuit,
        [(initial, {}, ())],
        {q: i for i, q in enumerate(circuit.qubits)},
        {c: i for i, c in enumerate(circuit.clbits)},
    )
    for state, _, _ in paths:
        close(state[(np.arange(64) & 3) != 0], 0)
    return {word: state[rows] for state, _, word in paths}


@pytest.mark.parametrize(
    "program,cap",
    [
        ("mark", 4),
        ("prepare", 0),
        ("reflect", 0),
        ("search", 0),
        ("search", 1),
        ("iterate", 2),
    ],
)
def test_loaded_qpy_classical_control_matches_executed_instrument(
    tmp_path, program, cap
):
    pytest.importorskip("qiskit")
    from qiskit import qpy

    circuit = graph.build_circuit(program, cap=cap, max_branches=341)
    path = tmp_path / f"{program}-{cap}.qpy"
    with path.open("wb") as stream:
        qpy.dump(circuit, stream)
    with path.open("rb") as stream:
        loaded = qpy.load(stream)[0]
    rng = np.random.default_rng(20261110)
    state = rng.normal(size=16) + 1j * rng.normal(size=16)
    state /= np.linalg.norm(state)
    qpy_paths = qpy_execute(loaded, state)
    actual = graph.execute(state, program, cap=cap, max_branches=341)
    assert len(qpy_paths) == len(actual)
    for branch in actual:
        word = tuple(o for r in branch.records for o in r.outcomes)
        close(qpy_paths[word], branch.state)


@pytest.mark.parametrize("bad", [-1, True, 1.0, 5, 10**50])
def test_cap_preallocation_guard(monkeypatch, bad):
    monkeypatch.setattr(np, "concatenate", lambda *a, **k: pytest.fail("allocated"))
    with pytest.raises(ValueError):
        graph.execute(np.zeros(16), "prepare", cap=bad, max_branches=341)


def test_strict_bounds_invalid_inputs_and_zero_records(monkeypatch):
    for program, cap, maximum in [
        ("search", 3, 341),
        ("search", 4, 341),
        ("reflect", 4, 340),
        ("mark", 0, True),
        ("prepare", 0, 342),
        ("unknown", 0, 1),
    ]:
        with pytest.raises(ValueError):
            graph.preflight(program, cap, maximum)
    with pytest.raises(ValueError):
        graph.execute(np.zeros(16), "mark", cap=0, max_branches=1, reference_wires=4)
    for state in (np.zeros(15), np.zeros((16, 5)), np.full(16, np.nan)):
        with pytest.raises(ValueError):
            graph.execute(state, "prepare", cap=0, max_branches=1)
    paths = graph.execute(np.zeros(16), "reflect", cap=4, max_branches=341)
    assert len(paths) == 341 and all(np.linalg.norm(p.state) == 0 for p in paths)


def test_exact_admitted_dependency_is_imported():
    expected = Path(__file__).resolve().parents[1] / "src/logique/benchmarks"
    assert Path(graph.__file__).resolve().parent == expected
    assert Path(graph.primitive.__file__).resolve().parent == expected
