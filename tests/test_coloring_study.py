"""Bounded controls, independent semantics, and reproducible saved pilot metrics."""

# ruff: noqa: E402

import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("saha_belletti")
from qiskit import qpy
from qiskit.quantum_info import Statevector

from logique.benchmarks import coloring_study as study
from logique.benchmarks.metrics import circuit_metrics
from logique.benchmarks.runner import load_config, run_benchmarks
from logique.coloring import ColoringProblem, encode_coloring

from logique.paths import native_executable

try:
    BRIDGE = native_executable()
except FileNotFoundError:
    BRIDGE = None


def evolve(circuit):
    assert circuit.num_qubits <= 12
    return Statevector.from_instruction(circuit).data


@pytest.mark.parametrize("regime", study.REGIMES)
@pytest.mark.parametrize("iterations", (0, 1, 2))
@pytest.mark.parametrize(
    "problem",
    (
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        ColoringProblem((2, 8, 90), ((2, 8), (8, 90)), 2),
        ColoringProblem((42,), (), 5),
    ),
)
def test_matching_preparation_diffusion_and_search(problem, regime, iterations):
    case = study.assemble_case(problem, "sb_balanced", regime, iterations=iterations)
    encoding = encode_coloring(problem)
    initial = evolve(case.preparation)
    if regime == "R1":
        np.testing.assert_allclose(initial, 1 / np.sqrt(len(initial)), atol=1e-9)
    else:
        expected_initial = np.array(
            [
                (
                    1 / np.sqrt(problem.colors ** len(problem.vertices))
                    if all(c < problem.colors for c in encoding.decode(x).values())
                    else 0
                )
                for x in range(len(initial))
            ]
        )
        np.testing.assert_allclose(initial, expected_initial, atol=1e-9)
    marked = np.array(
        [problem.is_valid(encoding.decode(x)) for x in range(len(initial))]
    )
    expected = initial.copy()
    for _ in range(iterations):
        expected[marked] *= -1
        expected = 2 * initial * np.vdot(initial, expected) - expected
    actual = evolve(case.search)
    np.testing.assert_allclose(actual[: len(initial)], expected, atol=1e-8)
    np.testing.assert_allclose(actual[len(initial) :], 0, atol=1e-8)
    np.testing.assert_allclose(
        evolve(case.preparation.compose(case.diffusion)), initial, atol=1e-8
    )
    md = case.metadata
    assert md["input_mapping"] == {
        v: list(q) for v, q in encoding.input_mapping.items()
    }
    assert sum(md["role_counts"].values()) == case.oracle.num_qubits
    assert md["validation"]["status"] == "exhaustive"
    assert md["validation"]["target_initializations"] == [0, 1]
    assert "linearity" in md["validation"]["phase_evidence"]


@pytest.mark.parametrize("method", study.METHODS)
@pytest.mark.parametrize("regime", study.REGIMES)
@pytest.mark.integration
def test_native_semantics_and_effective_r3_palette(method, regime):
    if BRIDGE is None:
        pytest.skip("shared native bridge unavailable")
    problem = ColoringProblem((9, 100), ((9, 100),), 3)
    case = study.assemble_case(problem, method, regime, executable=BRIDGE)
    md = case.metadata
    assert md["colors"] == 3
    assert md["effective_predicate_colors"] == (4 if regime == "R3" else 3)
    assert md["backend_metadata"]["coloring"]["vertices"] == [9, 100]
    assert md["input_mapping"] == {9: [0, 1], 100: [2, 3]}
    assert md["validation"]["marked_assignments"] == (12 if regime == "R3" else 6)
    # Phase validation above checks actual monomial gates against the graph,
    # including cleanup, even when synthesis has too many wires for statevectors.
    assert md["validation"]["workspace_restored"]


def test_r3_keeps_asymmetric_k5_preparation():
    p = ColoringProblem((6, 19), ((6, 19),), 5)
    case = study.assemble_case(p, "sb_original", "R3")
    assert case.metadata["effective_predicate_colors"] == 8
    assert case.metadata["validation"]["marked_assignments"] == 56
    initial = evolve(case.preparation)
    encoding = encode_coloring(p)
    for x, amplitude in enumerate(initial):
        assert abs(amplitude) == pytest.approx(
            0.2 if max(encoding.decode(x).values()) < 5 else 0, abs=1e-9
        )


def test_large_baseline_validation_uses_no_statevector(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("dense statevector allocation forbidden")

    monkeypatch.setattr(Statevector, "from_instruction", forbidden)
    p = ColoringProblem(tuple(range(13)), tuple((i, i + 1) for i in range(12)), 2)
    witness = sum((i % 2) << i for i in range(13))
    case = study.assemble_case(
        p, "sb_minimal", "R3", samples=1, verification_assignments=[witness]
    )
    report = case.metadata["validation"]
    assert report["status"] == "sampled"
    assert report["explicit_assignments"] == [witness]
    assert report["marked_assignments"] >= 1
    assert report["assignments"] <= 2


def test_precolors_require_explicit_removal():
    problem = ColoringProblem((2, 9), ((2, 9),), 3, {2: 1})
    with pytest.raises(ValueError, match="explicit remove_precolors"):
        study.assemble_case(problem, "sb_minimal", "R2")
    case = study.assemble_case(problem, "sb_minimal", "R2", remove_precolors=True)
    assert case.metadata["transformations"] == [
        {"operation": "remove_precolors", "removed": {2: 1}}
    ]
    assert case.metadata["validation"]["marked_assignments"] == 6


@pytest.mark.parametrize(
    "controls",
    [
        {"methods": ["unknown"]},
        {"regimes": ["R4"]},
        {"iterations": 1},
        {"iterations": [True]},
        {"iterations": [-1]},
        {"seeds": [1.5]},
        {"seeds": [7, 7]},
        {"samples": 0},
        {"validation": "none"},
        {"remove_precolors": "true"},
        {"common_basis": 1},
        {"common_basis": True, "optimization_level": True},
        {"common_basis": True, "basis_gates": ["cx", "rz"]},
        {"optimization_level": 2},
        {"colors": 1},
        {"target": "FakeTorino"},
        {"precision": 0.001},
        {"memory_limit": 1024},
        {"parameters": {"k": 5}},
        {"optimization_profile": "esop"},
        {"workspace_policy": "dirty"},
        {"routing": True},
        {"timeout": 180},
        {"decomposition_policy": "clean"},
        {"ft_synthesis": True},
        {"output": "dump/incorrect"},
        {"verification_assignments": [0]},
    ],
)
def test_reject_controls_before_work(monkeypatch, controls):
    def forbidden(*args, **kwargs):
        pytest.fail("input parsing or numerical work started before validation")

    monkeypatch.setattr(study, "read_dimacs", forbidden)
    with pytest.raises(ValueError):
        study.run_coloring_study({"inputs": ["missing.col"], **controls})


def write_config(tmp_path, **controls):
    source = tmp_path / "edge.col"
    source.write_text("p edge 2 1\ne 1 2\nx colors 3\n")
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "kind": "coloring_study",
                "inputs": ["edge.col"],
                "methods": ["sb_balanced"],
                "regimes": ["R2"],
                "iterations": [0, 1],
                "seeds": [7, 9],
                "output": "1025123456-test",
                **controls,
            }
        )
    )
    return path


def test_loader_resolves_per_input_assignments(tmp_path):
    config = load_config(
        write_config(tmp_path, verification_assignments={"edge.col": [4]})
    )
    assert config["verification_assignments"] == {str(tmp_path / "edge.col"): [4]}
    assert config["inputs"] == [str(tmp_path / "edge.col")]


@pytest.mark.parametrize(
    "assignments",
    ({"other.col": [0]}, {"edge.col": [True]}, {"edge.col": [-1]}, {"edge.col": [16]}),
)
def test_invalid_per_input_assignments(tmp_path, monkeypatch, assignments):
    def forbidden(*args, **kwargs):
        pytest.fail("assembly started before input-specific validation")

    monkeypatch.setattr(study, "assemble_case", forbidden)
    with pytest.raises(ValueError, match="assignment"):
        study.run_coloring_study(
            load_config(write_config(tmp_path, verification_assignments=assignments))
        )


def test_saved_qpy_reproduces_every_metric_and_dispatch(tmp_path):
    import pandas as pd

    config = load_config(
        write_config(tmp_path, common_basis=True, optimization_level=0)
    )
    output = run_benchmarks(config)
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete"
    assert len(manifest["cases"]) == 4
    rows = pd.read_csv(output / "summary.csv")
    assert len(rows) == 40
    for row in rows.to_dict("records"):
        with (output / row["artifact"]).open("rb") as stream:
            circuit = qpy.load(stream)[0]
        metrics = circuit_metrics(circuit)
        assert row["qubits"] == metrics["qubits"]
        assert row["gates"] == metrics["gates"]
        assert row["depth"] == metrics["depth"]
        assert row["regime"] == "R2"
        assert row["method"] == "sb_balanced"
        assert row["iteration"] in (0, 1)
        assert row["seed"] in (7, 9)
        if row["metric_level"] == "common_basis":
            assert set(circuit.count_ops()) <= {"u", "cx"}
    for case in manifest["cases"]:
        saved = json.loads((output / f'{case["name"]}.json').read_text())
        assert saved == case
        assert len(case["sha256"]) == 64
        assert len(case["artifacts"]) == 10
        assert case["timings"]["validation_seconds"] >= 0
    assert json.loads((output / "config.json").read_text()) == config


def test_exclusions_and_failures_have_no_comparison_costs(tmp_path, monkeypatch):
    import pandas as pd

    config_path = write_config(
        tmp_path,
        methods=["sb_original", "sb_simple", "sb_balanced"],
        iterations=[1],
        seeds=[7],
    )
    (tmp_path / "edge.col").write_text("p edge 3 2\ne 1 2\ne 1 3\nx colors 2\n")
    original = study.assemble_case

    def assemble(problem, method, *args, **kwargs):
        if method == "sb_simple":
            raise RuntimeError("injected construction failure")
        return original(problem, method, *args, **kwargs)

    monkeypatch.setattr(study, "assemble_case", assemble)
    output = study.run_coloring_study(load_config(config_path))
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    assert [c["status"] for c in manifest["cases"]] == [
        "excluded",
        "failed",
        "complete",
    ]
    assert "multi-edge" in manifest["cases"][0]["reason"]
    rows = pd.read_csv(output / "summary.csv")
    assert set(rows.method) == {"sb_balanced"}


def test_pilot_config_is_valid_and_has_positive_witnesses():
    from logique.coloring import read_dimacs

    config = load_config(
        Path(__file__).resolve().parents[1] / "configs/coloring_pilot.json"
    )
    assert len(config["methods"]) == 9
    assert config["remove_precolors"]
    for path in config["inputs"]:
        p = read_dimacs(path)
        p = ColoringProblem(p.vertices, p.edges, p.colors)
        encoding = encode_coloring(p)
        assert any(
            p.is_valid(encoding.decode(x))
            for x in config["verification_assignments"][path]
        )


@pytest.mark.integration
@pytest.mark.parametrize("regime", study.REGIMES)
def test_native_asymmetric_constant_r3_and_complete_search(regime):
    if BRIDGE is None:
        pytest.skip("shared native bridge unavailable")
    problem = ColoringProblem((42,), (), 5)
    native = study.assemble_case(
        problem, "xag", regime, iterations=2, executable=BRIDGE
    )
    baseline = study.assemble_case(problem, "sb_balanced", regime, iterations=2)
    actual, expected = evolve(native.search), evolve(baseline.search)
    np.testing.assert_allclose(actual[:8], expected[:8], atol=1e-8)
    np.testing.assert_allclose(actual[8:], 0, atol=1e-8)
    assert native.metadata["input_mapping"] == {42: [0, 1, 2]}
    assert native.metadata["validation"]["marked_assignments"] == (
        8 if regime == "R3" else 5
    )


@pytest.mark.integration
def test_native_sampled_explicit_assignments():
    if BRIDGE is None:
        pytest.skip("shared native bridge unavailable")
    case = study.assemble_case(
        ColoringProblem((2, 9), ((2, 9),), 3),
        "xag",
        "R3",
        validation="sampled",
        samples=1,
        verification_assignments=[4, 12],
        executable=BRIDGE,
    )
    report = case.metadata["validation"]
    assert report["status"] == "sampled"
    assert report["explicit_assignments"] == [4, 12]
    assert report["marked_assignments"] >= 2
    assert report["raw_validation"]["explicit_assignments"] == [4, 12]


def test_baseline_validation_rejects_wrong_target_phase(monkeypatch):
    import logique.synthesis as synthesis

    original = synthesis.baseline_components

    def corrupt(*args, **kwargs):
        result = original(*args, **kwargs)
        result.circuit.z(result.metadata["kickback_qubit"])
        return result

    monkeypatch.setattr(synthesis, "baseline_components", corrupt)
    with pytest.raises(AssertionError, match="clean XOR"):
        study.assemble_case(ColoringProblem((1, 2), ((1, 2),), 2), "sb_balanced", "R1")


def test_stage_timing_contract_keeps_native_combined_and_unknown_splits():
    stages = study._stage_timings({"synthesis_seconds": 2.0}, {"native_seconds": 0.5})
    assert stages["synthesis"]["seconds"] == 2.0
    assert stages["synthesis"]["clock"] == "time.perf_counter"
    assert stages["native_combined"]["seconds"] == 0.5
    assert stages["native_combined"]["included_in"] == "synthesis"
    assert stages["native_combined"]["clock"] == "std::chrono::steady_clock"
    for key in ("optimization", "mapping"):
        assert stages[key]["status"] == "unavailable"
        assert stages[key]["seconds"] is None
    assert stages["routing"]["status"] == "not_enabled"
    absent = study._stage_timings({}, {})["native_combined"]
    assert absent["status"] == "unavailable"
    assert absent["seconds"] is None


def test_network_statistics_are_structural_and_do_not_guess_lut_depth():
    graph = {
        "nodes": [
            {"id": 0, "kind": "constant", "fanins": []},
            {"id": 1, "kind": "input", "fanins": []},
            {"id": 2, "kind": "input", "fanins": []},
            {"id": 3, "kind": "xor", "fanins": [{"node": 1}, {"node": 2}]},
            {"id": 4, "kind": "and", "fanins": [{"node": 1}, {"node": 3}]},
            {"id": 5, "kind": "and", "fanins": [{"node": 4}, {"node": 2}]},
        ],
        "inputs": [1, 2],
        "outputs": [{"node": 5}],
    }
    stats = study._network_statistics(graph, "fixture")
    assert (stats["AND"], stats["XOR"], stats["LUT"]) == (2, 1, 0)
    assert stats["logic_depth"] == 3
    assert stats["multiplicative_depth"] == 2
    assert stats["source"] == "fixture"
    graph["nodes"][-1]["kind"] = "lut"
    stats = study._network_statistics(graph, "fixture")
    assert stats["LUT"] == 1
    assert stats["multiplicative_depth"] is None
    assert study._network_statistics(None, "missing")["status"] == "unavailable"


@pytest.mark.parametrize("iterations", [0, 1])
def test_workspace_provenance_partitions_reserved_component_wires(iterations):
    case = study.assemble_case(
        ColoringProblem((2, 8, 90), ((2, 8), (8, 90)), 2),
        "sb_balanced",
        "R2",
        iterations=iterations,
    )
    md = case.metadata
    assert md["metadata_version"] == 2
    assert md["peak_memory"] == {"status": "unavailable", "bytes": None}
    assert md["structural_statistics"]["network"]["status"] == "unavailable"
    for component, circuit in case.circuits.items():
        workspace = md["component_workspace"][component]
        wires = [q for group in workspace["roles"].values() for q in group]
        assert sorted(wires) == list(range(circuit.num_qubits))
        assert workspace["peak_reserved_qubits"] == circuit.num_qubits
        assert workspace["peak_live_workspace_qubits"] is None
        assert workspace["role_counts"]["mcx_ancilla"] == 0
    raw = md["component_workspace"]["raw"]["roles"]
    oracle = md["component_workspace"]["oracle"]["roles"]
    assert raw["output"] == oracle["kickback"]
    assert not raw["kickback"] and not oracle["output"]
    assert oracle["constraint"] == md["backend_metadata"]["constraint_qubits"]
    assert oracle["unknown"] == md["backend_metadata"]["workspace_qubits"]


@pytest.mark.integration
def test_native_workspace_remains_unknown_with_network_evidence():
    if BRIDGE is None:
        pytest.skip("shared native bridge unavailable")
    case = study.assemble_case(
        ColoringProblem((2, 9), ((2, 9),), 3),
        "xag_bennett",
        "R2",
        executable=BRIDGE,
    )
    md = case.metadata
    roles = md["component_workspace"]["oracle"]["roles"]
    assert roles["unknown"] == md["qubit_roles"]["synthesis_workspace"]
    assert roles["unknown"]
    assert "AND" not in roles
    assert (
        md["stage_timings"]["native_combined"]["seconds"]
        == md["backend_metadata"]["native_seconds"]
    )
    for name in ("source_network", "network"):
        stats = md["structural_statistics"][name]
        assert stats["AND"] == sum(
            n["kind"] == "and" for n in md["backend_metadata"][name]["nodes"]
        )


def test_saved_metadata_uses_monotonic_clock_and_reads_old_tables(
    tmp_path, monkeypatch
):
    from itertools import count
    from types import SimpleNamespace
    from logique.benchmarks.results import load_results

    def forbidden():
        raise AssertionError("wall clock must not measure elapsed durations")

    # Restrict the runner's clock without altering Qiskit/logging wall timestamps.
    ticks = count(100, 0.25)
    monkeypatch.setattr(
        study, "time", SimpleNamespace(perf_counter=lambda: next(ticks), time=forbidden)
    )
    output = study.run_coloring_study(
        load_config(
            write_config(
                tmp_path,
                seeds=[7],
                iterations=[0],
                common_basis=True,
                optimization_level=0,
            )
        )
    )
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["schema_version"] == 1
    assert manifest["metadata_version"] == 2
    case = manifest["cases"][0]
    assert case["status"] == "complete"
    assert case["stage_timings"]["case_total"]["seconds"] == case["total_seconds"]
    for key, elapsed in case["timings"].items():
        assert elapsed == 0.25
        assert case["stage_timings"][key.removesuffix("_seconds")]["seconds"] == elapsed
    for artifact, record in case["artifact_statistics"].items():
        import hashlib

        assert (
            record["sha256"]
            == hashlib.sha256((output / artifact).read_bytes()).hexdigest()
        )
        with (output / artifact).open("rb") as stream:
            metrics = circuit_metrics(qpy.load(stream)[0])
        assert record["metrics"] == {**metrics, "metric_level": record["metric_level"]}
        lowering = record["stage_timings"]["lowering"]
        if record["metric_level"] == "logical":
            assert lowering == {"status": "not_requested", "seconds": None}
        else:
            assert lowering["status"] == "measured"
            assert lowering["seconds"] >= 0
    current = load_results(output)
    legacy_columns = [
        "benchmark",
        "method",
        "regime",
        "component",
        "iteration",
        "seed",
        "metric_level",
        "qubits",
        "depth",
        "gates",
        "artifact",
    ]
    legacy = tmp_path / "legacy.csv"
    current[legacy_columns].to_csv(legacy, index=False)
    assert load_results(legacy).equals(current[legacy_columns])


def test_failed_lowering_retains_partial_evidence_without_cost_rows(
    tmp_path, monkeypatch
):
    import logique.benchmarks.metrics as metrics

    def fail(*args, **kwargs):
        raise RuntimeError("injected common-basis failure")

    monkeypatch.setattr(metrics, "lower_circuit", fail)
    output = study.run_coloring_study(
        load_config(
            write_config(
                tmp_path,
                methods=["sb_balanced"],
                seeds=[7],
                iterations=[0],
                common_basis=True,
            )
        )
    )
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    case = manifest["cases"][0]
    assert case["status"] == "failed"
    assert case["reason"] == "RuntimeError: injected common-basis failure"
    assert len(case["artifact_statistics"]) == 1
    assert next(iter(case["artifact_statistics"].values()))["metric_level"] == "logical"
    assert case["stage_timings"]["case_total"]["seconds"] >= 0
    assert not (output / "summary.csv").exists()


def qpy_roundtrip(circuit):
    import io

    stream = io.BytesIO()
    qpy.dump(circuit, stream)
    stream.seek(0)
    return qpy.load(stream)[0]


def assert_resolved_semantics(original, saved):
    """Prove composition via <=4-wire blocks; never simulate wider scratch."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    expected = original.copy_empty_like()
    # Each replacement is proved as an operator, including all input columns
    # and scalar phases. Unchanged wider standard gates use exact signatures.
    for item in original.data:
        block = QuantumCircuit(len(item.qubits))
        block.append(item.operation, range(len(item.qubits)))
        resolved, metadata = study._resolved_qpy_circuit(block)
        if metadata["expanded_definitions"]:
            if block.num_qubits <= 4:
                np.testing.assert_allclose(
                    Operator(resolved).data, Operator(block).data, atol=1e-12, rtol=0
                )
            else:
                # Five-wire open MCX: exhaustive monomial proof, no operator
                # or statevector allocation. This helper admits no wider block.
                from logique.circuits.records import _qiskit_records
                from logique.verification.classical import _apply_record

                assert block.num_qubits == 5
                outcomes = []
                for candidate in (block, resolved):
                    bits = (
                        (np.arange(32)[None, :] >> np.arange(5)[:, None]) & 1
                    ).astype(bool)
                    phases = np.full(32, np.exp(1j * float(candidate.global_phase)))
                    for record in _qiskit_records(candidate):
                        _apply_record(bits, phases, record)
                    outcomes.append((bits, phases))
                np.testing.assert_array_equal(outcomes[0][0], outcomes[1][0])
                np.testing.assert_allclose(
                    outcomes[0][1], outcomes[1][1], atol=1e-12, rtol=0
                )
        expected.compose(
            resolved,
            [original.find_bit(q).index for q in item.qubits],
            inplace=True,
        )
    before = study._qpy_semantic_signature(expected)
    after = study._qpy_semantic_signature(saved)
    # Independent blockwise composition associates phase additions differently.
    # QPY itself must retain the exact signature of its resolved input.
    before.pop("global_phase")
    after.pop("global_phase")
    assert before == after
    assert (
        abs(
            np.exp(1j * float(expected.global_phase))
            - np.exp(1j * float(saved.global_phase))
        )
        < 1e-12
    )
    if original.num_qubits <= 4:
        np.testing.assert_allclose(
            Operator(saved).data, Operator(original).data, atol=1e-11, rtol=0
        )


@pytest.mark.parametrize("colors", [3, 5])
@pytest.mark.parametrize("inverse", [False, True])
@pytest.mark.parametrize("nested", [False, True])
def test_qpy_actual_preparation_inverse_nested_and_scalar_phase(
    colors, inverse, nested
):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import StatePreparation
    from qiskit.quantum_info import Operator

    width = (colors - 1).bit_length()
    # Asymmetric complex entries expose reversed wires, conjugation and phase.
    amplitudes = np.zeros(1 << width, dtype=complex)
    amplitudes[:colors] = np.arange(1, colors + 1) * np.exp(
        1j * np.arange(colors) * 0.37
    )
    amplitudes /= np.linalg.norm(amplitudes)
    circuit = QuantumCircuit(width, global_phase=0.231)
    prep = StatePreparation(amplitudes)
    circuit.append(prep.inverse() if inverse else prep, list(reversed(range(width))))
    if nested:
        for phase in (0.17, -0.29):
            outer = QuantumCircuit(width, global_phase=phase)
            outer.append(circuit.to_gate().inverse(), range(width))
            circuit = outer
    resolved, provenance = study._resolved_qpy_circuit(circuit)
    saved = qpy_roundtrip(resolved)
    assert "state_preparation" not in saved.count_ops()
    assert "state_preparation_dg" not in saved.count_ops()
    assert provenance["representation"] == "resolved_standard_gates"
    assert_resolved_semantics(circuit, saved)
    np.testing.assert_allclose(
        Operator(saved).data, Operator(circuit).data, atol=1e-12, rtol=0
    )
    # The original object was not renamed or mutated to influence QPY.
    if not nested:
        assert circuit.data[0].operation._inverse is inverse


def assert_clean_xor_columns(case, problem, regime):
    """Exhaustive monomial proof of raw XOR and scratch restoration."""
    from logique.circuits.records import _qiskit_records
    from logique.verification.classical import _apply_record

    encoding = encode_coloring(problem)
    reference = (
        ColoringProblem(problem.vertices, problem.edges, 1 << encoding.bits_per_color)
        if regime == "R3"
        else problem
    )
    effective = encode_coloring(reference)
    inputs = case.metadata["data_qubits"]
    target = case.metadata["backend_metadata"]["output_qubits"][0]
    assignments = np.arange(1 << len(inputs))
    truth = np.array(
        [reference.is_valid(effective.decode(int(x))) for x in assignments]
    )
    for initial_target in (0, 1):
        bits = np.zeros((case.raw.num_qubits, len(assignments)), dtype=bool)
        for i, wire in enumerate(inputs):
            bits[wire] = ((assignments >> i) & 1).astype(bool)
        bits[target] = initial_target
        expected = bits.copy()
        expected[target] ^= truth
        phases = np.full(len(assignments), np.exp(1j * float(case.raw.global_phase)))
        for record in _qiskit_records(case.raw):
            _apply_record(bits, phases, record)
        np.testing.assert_array_equal(bits, expected)
        np.testing.assert_allclose(phases, 1, atol=1e-12, rtol=0)
    # Actual oracle is exactly X H; raw; H X on the same target. This proves
    # phase marking and clean scratch by linearity without a wide statevector.
    from qiskit import QuantumCircuit

    oracle = QuantumCircuit(case.raw.num_qubits)
    oracle.x(target)
    oracle.h(target)
    oracle.compose(case.raw, inplace=True)
    oracle.h(target)
    oracle.x(target)
    resolved, _ = study._resolved_qpy_circuit(oracle)
    actual, _ = study._resolved_qpy_circuit(case.oracle)
    assert study._qpy_semantic_signature(resolved) == study._qpy_semantic_signature(
        actual
    )


@pytest.mark.parametrize(
    "problem,method",
    [
        (ColoringProblem((-7, 20), ((-7, 20),), 3), "sb_balanced"),
        (ColoringProblem((42,), (), 5), "sb_balanced"),
        (ColoringProblem((2, 8, 90), ((2, 8), (8, 90), (2, 90)), 2), "xag"),
        (ColoringProblem((42,), (), 3), "xag"),
    ],
)
@pytest.mark.parametrize("regime", ["R2", "R3"])
@pytest.mark.parametrize("iterations", [0, 1])
def test_qpy_saved_study_semantics_counts_and_roles(
    tmp_path, monkeypatch, problem, method, regime, iterations
):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    import pandas as pd

    if method in study.METHODS and BRIDGE is None:
        pytest.skip("shared native bridge unavailable")
    original = study.assemble_case(
        problem, method, regime, iterations=iterations, executable=BRIDGE
    )
    # The mocked parser permits noncontiguous labels in a runner regression;
    # no fabricated external experiment is inferred from this test fixture.
    monkeypatch.setattr(study, "read_dimacs", lambda *args, **kwargs: problem)
    config = load_config(
        write_config(
            tmp_path,
            methods=[method],
            regimes=[regime],
            seeds=[7],
            iterations=[iterations],
            common_basis=True,
            optimization_level=0,
        )
    )
    output = study.run_coloring_study(config, executable=BRIDGE)
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete"
    case = manifest["cases"][0]
    assert case["input_mapping"] == {
        str(v): wires for v, wires in original.metadata["input_mapping"].items()
    }
    rows = pd.read_csv(output / "summary.csv")
    assert len(rows) == 10
    saved = {}
    for component, circuit in original.circuits.items():
        for level in ("logical", "common_basis"):
            artifact = case["artifacts"][f"{component}_{level}"]
            with (output / artifact).open("rb") as stream:
                restored = qpy.load(stream)[0]
            record = case["artifact_statistics"][artifact]
            assert record["status"] == "verified"
            assert record["metrics"] == {
                **circuit_metrics(restored),
                "metric_level": level,
            }
            row = rows[rows.artifact == artifact].iloc[0]
            for key in ("qubits", "gates", "depth"):
                assert row[key] == record["metrics"][key]
            assert record["workspace"] == case["component_workspace"][component]
            assert record["workspace"]["peak_live_workspace_qubits"] is None
            assert record["serialization"]["readback_check"]["status"] == (
                "exact_standard_gate_signature_match"
            )
            if level == "logical":
                assert_resolved_semantics(circuit, restored)
                saved[component] = restored
            else:
                assert set(restored.count_ops()) <= {"u", "cx"}
                # Check lowering on bounded components as an operator. Wider
                # common-basis circuit lowering is not numerically certified.
                if circuit.num_qubits <= 4:
                    np.testing.assert_allclose(
                        Operator(restored).data,
                        Operator(circuit).data,
                        atol=1e-11,
                        rtol=0,
                    )
    assert_clean_xor_columns(original, problem, regime)
    assert original.preparation.num_qubits <= 4
    a = Operator(saved["preparation"]).data
    s0 = -np.eye(len(a))
    s0[0, 0] = 1
    np.testing.assert_allclose(
        Operator(saved["diffusion"]).data,
        a @ s0 @ a.conj().T,
        atol=1e-11,
        rtol=0,
    )
    # Independent data-space amplification, with full search simulation only
    # when its entire scratch register fits the explicit five-wire bound.
    initial = a[:, 0]
    encoding = encode_coloring(problem)
    valid = np.array(
        [
            all(color < problem.colors for color in encoding.decode(x).values())
            for x in range(len(initial))
        ]
    )
    np.testing.assert_allclose(
        initial,
        np.where(valid, 1 / np.sqrt(problem.colors ** len(problem.vertices)), 0),
        atol=1e-12,
        rtol=0,
    )
    marked = np.array(
        [problem.is_valid(encoding.decode(x)) for x in range(len(initial))]
    )
    expected = initial.copy()
    for _ in range(iterations):
        expected[marked] *= -1
        expected = 2 * initial * np.vdot(initial, expected) - expected
    composed = QuantumCircuit(original.search.num_qubits)
    composed.compose(original.preparation, case["data_qubits"], inplace=True)
    for _ in range(iterations):
        composed.compose(original.oracle, inplace=True)
        composed.compose(original.diffusion, case["data_qubits"], inplace=True)
    assert_resolved_semantics(composed, saved["search"])
    if saved["search"].num_qubits <= 5:
        actual = Statevector.from_instruction(saved["search"]).data
        np.testing.assert_allclose(
            actual[: len(expected)], expected, atol=1e-11, rtol=0
        )
        np.testing.assert_allclose(actual[len(expected) :], 0, atol=1e-11, rtol=0)


@pytest.mark.parametrize("failure", ["opaque", "readback_phase"])
def test_qpy_unsupported_or_changed_readback_retains_evidence_without_rows(
    tmp_path, monkeypatch, failure
):
    from qiskit.circuit import Gate

    if failure == "opaque":
        assemble = study.assemble_case

        def unsupported(*args, **kwargs):
            case = assemble(*args, **kwargs)
            # Even a familiar gate name cannot make an opaque Gate supported.
            case.preparation.append(Gate("state_preparation_dg", 2, []), [0, 1])
            return case

        monkeypatch.setattr(study, "assemble_case", unsupported)
    else:
        load = qpy.load
        calls = 0

        def corrupt(*args, **kwargs):
            nonlocal calls
            circuits = load(*args, **kwargs)
            calls += 1
            if calls == 2:
                circuits[0].global_phase += 0.125
            return circuits

        monkeypatch.setattr(qpy, "load", corrupt)
    config = load_config(
        write_config(tmp_path, seeds=[7], iterations=[0], common_basis=False)
    )
    output = study.run_coloring_study(config)
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    case = manifest["cases"][0]
    assert case["status"] == "failed"
    assert ("opaque QPY" if failure == "opaque" else "signature changed") in case[
        "reason"
    ]
    assert not (output / "summary.csv").exists()
    records = list(case["artifact_statistics"].values())
    assert [r["status"] for r in records] == [
        "verified",
        "resolving" if failure == "opaque" else "written_unverified",
    ]
    assert "metrics" not in records[-1]
    for artifact in case["artifacts"].values():
        assert (output / artifact).exists()
    if failure == "readback_phase":
        signatures = records[-1]["readback_signatures"]
        assert signatures["actual"] != signatures["expected"]


def test_qpy_resolution_bounds_and_unsupported_circuits():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter

    circuit = QuantumCircuit(1)
    circuit.h(0)
    for _ in range(34):
        outer = QuantumCircuit(1)
        outer.append(circuit.to_gate(), [0])
        circuit = outer
    with pytest.raises(ValueError, match="depth limit 32"):
        study._resolved_qpy_circuit(circuit)
    circuit = QuantumCircuit(1)
    circuit.rx(Parameter("theta"), 0)
    with pytest.raises(ValueError, match="bound, quantum-only"):
        study._resolved_qpy_circuit(circuit)
    circuit = QuantumCircuit(1, 1)
    circuit.measure(0, 0)
    with pytest.raises(ValueError, match="bound, quantum-only"):
        study._resolved_qpy_circuit(circuit)
    circuit = QuantumCircuit(1)
    circuit.rx(float("inf"), 0)
    with pytest.raises(ValueError, match="finite parameters"):
        study._resolved_qpy_circuit(circuit)
    circuit = QuantumCircuit(1)
    circuit.x([0] * 100_001)
    with pytest.raises(ValueError, match="100000 operations"):
        study._resolved_qpy_circuit(circuit)


@pytest.mark.parametrize("colors", [3, 5])
def test_qpy_controlled_nested_preparation_retains_conditional_scalar_phase(colors):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import StatePreparation

    width = (colors - 1).bit_length()
    amplitudes = np.zeros(1 << width)
    amplitudes[:colors] = 1 / np.sqrt(colors)
    body = QuantumCircuit(width, global_phase=0.417)
    body.append(StatePreparation(amplitudes).inverse(), range(width))
    circuit = QuantumCircuit(width + 1, global_phase=-0.19)
    circuit.append(body.to_gate().control(1, ctrl_state=0), range(width + 1))
    resolved, _ = study._resolved_qpy_circuit(circuit)
    assert_resolved_semantics(circuit, qpy_roundtrip(resolved))


@pytest.mark.parametrize("controls", [3, 4])
def test_qpy_retains_logical_mcx_and_open_control_state(controls):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCXGate

    circuit = QuantumCircuit(controls + 1, global_phase=0.17)
    state = sum(1 << i for i in range(controls) if i % 2 == 0)
    circuit.append(MCXGate(controls, ctrl_state=state), range(controls + 1))
    resolved, provenance = study._resolved_qpy_circuit(circuit)
    assert provenance["expanded_definitions"]
    assert sum(isinstance(item.operation, MCXGate) for item in resolved.data) == 1
    assert len(resolved.data) == 1 + 2 * (controls - state.bit_count())
    saved = qpy_roundtrip(resolved)
    assert_resolved_semantics(circuit, saved)


# Restoring MCX evidence uses only <=3-wire local matrices and integer/scalar
# columns for wider monomial blocks. No wide dense vector/operator is allocated.
def _restoring_scalar_column(circuit, bits):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCXGate
    from qiskit.quantum_info import Operator

    phase = np.exp(1j * float(circuit.global_phase))
    cursor = 0
    while cursor < len(circuit.data):
        item = circuit.data[cursor]
        op = item.operation
        wires = [circuit.find_bit(q).index for q in item.qubits]
        if isinstance(op, MCXGate):
            value = sum(((bits >> q) & 1) << j for j, q in enumerate(wires))
            mask = (1 << op.num_ctrl_qubits) - 1
            output = (
                value ^ (1 << op.num_ctrl_qubits)
                if value & mask == op.ctrl_state
                else value
            )
            cursor += 1
        else:
            # An emitted inverse-RCCX definition contains H/T/CX leaves.
            # Contract contiguous local leaves to a <=3-wire monomial matrix;
            # this proves their joint action without a wide quantum state.
            group = []
            for end in range(cursor, min(cursor + 32, len(circuit.data))):
                leaf = circuit.data[end]
                leaf_wires = [circuit.find_bit(q).index for q in leaf.qubits]
                wires = list(dict.fromkeys([*wires, *leaf_wires]))
                assert len(wires) <= 3, (op.name, wires)
                group.append((leaf.operation, leaf_wires))
                local = QuantumCircuit(len(wires))
                for operation, mapping in group:
                    local.append(operation, [wires.index(q) for q in mapping])
                matrix = Operator(local).data
                if np.all(np.sum(abs(matrix) > 1e-12, axis=0) == 1):
                    break
            else:
                raise AssertionError("No bounded local monomial contraction")
            value = sum(((bits >> q) & 1) << j for j, q in enumerate(wires))
            column = matrix[:, value]
            output = int(np.flatnonzero(abs(column) > 1e-12)[0])
            phase *= column[output]
            cursor = end + 1
        for j, q in enumerate(wires):
            bits = (bits & ~(1 << q)) | (((output >> j) & 1) << q)
    return bits, phase


@pytest.mark.parametrize("controls", (3, 4, 5, 20))
def test_restoring_mcx_scalar_template_and_fresh_reuse(controls):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCXGate

    source = QuantumCircuit(controls + 3, global_phase=0.317)
    # Existing spare wires deliberately start nonzero and must never be borrowed.
    source.append(MCXGate(controls), range(controls + 1))
    source.append(MCXGate(controls, ctrl_state=1), list(reversed(range(controls + 1))))
    lowered, info = study._restoring_mcx_block(source)
    assert info["appended_ancillas"] == controls - 2
    assert info["clean_wires_used"] == info["borrowed_dirty_wires"] == 0
    assert info["emitted_max_controls"] <= 2
    columns = (
        range(1 << (controls + 1))
        if controls <= 5
        else (0, 1, (1 << controls) - 1, (1 << (controls + 1)) - 1)
    )
    for x in columns:
        initial = x | (3 << (controls + 1))
        actual, phase = _restoring_scalar_column(lowered, initial)
        expected, reference = _restoring_scalar_column(source, initial)
        assert actual == expected  # all fresh high scratch bits are zero
        assert abs(phase - reference) < 2e-12


@pytest.mark.parametrize("state", range(8))
def test_restoring_open_mcx_superposition_and_actual_inverse(state):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCXGate

    nested = QuantumCircuit(4, global_phase=0.237)
    nested.append(MCXGate(3, ctrl_state=state), [2, 0, 3, 1])
    source = QuantumCircuit(4, global_phase=0.411)
    source.append(nested.to_gate().inverse(), [3, 1, 0, 2])
    lowered, _ = study._restoring_mcx_block(source)
    assert lowered.num_qubits == 5
    rng = np.random.default_rng(814)
    data = rng.normal(size=16) + 1j * rng.normal(size=16)
    data /= np.linalg.norm(data)
    before = np.r_[data, np.zeros(16)]
    actual = Statevector(before.copy()).evolve(lowered).data
    expected = Statevector(data.copy()).evolve(source).data
    np.testing.assert_allclose(actual, np.r_[expected, np.zeros(16)], atol=2e-12)
    np.testing.assert_allclose(
        Statevector(actual.copy()).evolve(lowered.inverse()).data, before, atol=2e-12
    )


@pytest.mark.parametrize(
    "controls",
    (
        {"mcx_decomposition": "gray_code", "mcx_workspace": "fresh_zero"},
        {"mcx_decomposition": "throwaway_tree", "mcx_workspace": "fresh_zero"},
        {"mcx_decomposition": "n_dirty_i15", "mcx_workspace": "fresh_zero"},
        {"mcx_decomposition": "clean_tree"},
        {"mcx_workspace": "fresh_zero"},
        {"mcx_decomposition": "clean_tree", "mcx_workspace": "borrow_clean"},
        {"mcx_decomposition": None, "mcx_workspace": None},
    ),
)
def test_restoring_controls_reject_before_artifacts(tmp_path, monkeypatch, controls):
    def forbidden(*args, **kwargs):
        pytest.fail("numerical/artifact work before preflight")

    monkeypatch.setattr(study, "assemble_case", forbidden)
    output = tmp_path / "1026000000-invalid-policy"
    with pytest.raises(ValueError, match="mcx_"):
        study.run_coloring_study(
            dict(inputs=["missing.col"], output=str(output), **controls)
        )
    assert not output.exists()


def test_restoring_fixed_bounds_preflight_and_unhandled_gate():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Gate

    for problem in (
        ColoringProblem((1,), (), 9),
        ColoringProblem(tuple(range(22)), (), 2),
    ):
        with pytest.raises(ValueError, match="k<=8"):
            study.assemble_case(
                problem,
                "sb_balanced",
                "R2",
                mcx_decomposition="clean_tree",
                mcx_workspace="fresh_zero",
            )
    with pytest.raises(ValueError, match="iterations 0..2"):
        study.validate_study_config(
            dict(
                inputs=["missing.col"],
                iterations=[3],
                mcx_decomposition="clean_tree",
                mcx_workspace="fresh_zero",
            )
        )
    wide = QuantumCircuit(22)
    wide.mcx(list(range(21)), 21)
    with pytest.raises(ValueError, match="20 controls"):
        study._restoring_mcx_block(wide)
    opaque = QuantumCircuit(4)
    opaque.append(Gate("hidden_mcx", 4, []), range(4))
    with pytest.raises(ValueError, match="opaque"):
        study._restoring_mcx_block(opaque)


@pytest.mark.parametrize("regime", study.REGIMES)
@pytest.mark.parametrize("iterations", (0, 1))
@pytest.mark.parametrize(
    "problem",
    (
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        ColoringProblem((42,), (), 5),
        ColoringProblem((2, 8, 90), ((2, 8), (8, 90), (2, 90)), 2),
    ),
)
def test_restoring_independent_predicate_and_disjoint_search(
    problem, regime, iterations
):
    from qiskit import QuantumCircuit

    original = study.assemble_case(
        problem, "sb_balanced", regime, iterations=iterations
    )
    case = study.assemble_case(
        problem,
        "sb_balanced",
        regime,
        iterations=iterations,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    md = case.metadata
    data = md["data_qubits"]
    n = len(data)
    bits = (problem.colors - 1).bit_length()
    target = md["backend_metadata"]["output_qubits"][0]
    for x in range(1 << n):
        colors = {
            v: (x >> (i * bits)) & ((1 << bits) - 1)
            for i, v in enumerate(problem.vertices)
        }
        predicate = all(colors[a] != colors[b] for a, b in problem.edges) and (
            regime == "R3" or all(c < problem.colors for c in colors.values())
        )
        for t in (0, 1):
            initial = sum(((x >> i) & 1) << q for i, q in enumerate(data)) | (
                t << target
            )
            out, phase = _restoring_scalar_column(case.raw, initial)
            assert out == initial ^ (int(predicate) << target)
            assert abs(phase - 1) < 2e-12
            old, old_phase = _restoring_scalar_column(original.raw, initial)
            assert old == out and abs(old_phase - phase) < 2e-12
    owners = md["mcx_lowering"]["search_scratch_ownership"]
    all_scratch = [q for group in owners.values() for q in group]
    assert len(set(all_scratch)) == len(all_scratch)
    assert not set(all_scratch) & set(range(original.raw.num_qubits))
    expected = QuantumCircuit(case.search.num_qubits)
    maps = md["mcx_lowering"]["search_embeddings"]
    expected.compose(case.preparation, maps["preparation"], inplace=True)
    for _ in range(iterations):
        expected.compose(case.oracle, maps["oracle"], inplace=True)
        expected.compose(case.diffusion, maps["diffusion"], inplace=True)
    assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
        case.search
    )
    for name, q in case.circuits.items():
        assert md["mcx_lowering"]["emitted_max_controls"][name] <= 2
        workspace = md["component_workspace"][name]
        assert sorted(
            q for group in workspace["roles"].values() for q in group
        ) == list(range(q.num_qubits))
        assert workspace["peak_live_workspace_qubits"] is None
    # A small complete physical register permits an independent amplification
    # reference and tests all scratch amplitudes, without dropping idle wires.
    if case.search.num_qubits <= 5:
        assert case.preparation.num_qubits <= 5
        initial = Statevector.from_instruction(case.preparation).data[: 1 << n]
        ideal = initial.copy()
        for _ in range(iterations):
            for x in range(1 << n):
                colors = [
                    (x >> (i * bits)) & ((1 << bits) - 1)
                    for i in range(len(problem.vertices))
                ]
                good = (
                    regime == "R3" or all(c < problem.colors for c in colors)
                ) and all(
                    colors[problem.vertices.index(a)]
                    != colors[problem.vertices.index(b)]
                    for a, b in problem.edges
                )
                if good:
                    ideal[x] *= -1
            ideal = 2 * initial * np.vdot(initial, ideal) - ideal
        expected_vector = np.zeros(1 << case.search.num_qubits, dtype=complex)
        for x, amplitude in enumerate(ideal):
            expected_vector[sum(((x >> i) & 1) << q for i, q in enumerate(data))] = (
                amplitude
            )
        np.testing.assert_allclose(
            Statevector.from_instruction(case.search).data, expected_vector, atol=2e-11
        )


@pytest.mark.parametrize("method", study.METHODS)
@pytest.mark.parametrize("regime", study.REGIMES)
def test_restoring_native_emitted_blocks_and_fallback(method, regime, monkeypatch):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    import logique.verification as verification

    if BRIDGE is None:
        pytest.skip("admitted private native bridge unavailable")
    problem = ColoringProblem((-7, 20), ((-7, 20),), 3)
    original = study.assemble_case(problem, method, regime, executable=BRIDGE)
    lowered = study.assemble_case(
        problem,
        method,
        regime,
        executable=BRIDGE,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    assert max(lowered.metadata["mcx_lowering"]["emitted_max_controls"].values()) <= 2
    if lowered.raw.num_qubits == original.raw.num_qubits:
        expected = study._resolved_qpy_circuit(original.raw, expand_wide=True)[0]
        assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
            lowered.raw
        )

    # Explicit branch coverage, not a naturally failing backend fixture.
    def conservative(*args, **kwargs):
        raise AssertionError("forced conservative branch")

    monkeypatch.setattr(verification, "verify_kickback_oracle", conservative)
    fallback = study.assemble_case(
        ColoringProblem((42,), (), 3),
        method,
        regime,
        executable=BRIDGE,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    assert fallback.metadata["oracle_construction"] == "compute_Z_inverse_compute"
    expected = fallback.raw.copy()
    expected.z(fallback.metadata["backend_metadata"]["output_qubits"][0])
    expected.compose(
        study._resolved_qpy_circuit(fallback.raw.inverse())[0], inplace=True
    )
    assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
        fallback.oracle
    )
    if fallback.oracle.num_qubits <= 4:
        matrix = Operator(fallback.oracle).data
        raw = Operator(fallback.raw).data
        mark = QuantumCircuit(fallback.oracle.num_qubits)
        mark.z(fallback.metadata["backend_metadata"]["output_qubits"][0])
        np.testing.assert_allclose(
            matrix, raw.conj().T @ Operator(mark).data @ raw, atol=2e-11
        )


def test_restoring_preparation_contained_mcx_and_disjoint_inverse(monkeypatch):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCXGate
    import logique.circuits.grover as grover

    original_preparation = grover.coloring_preparation

    def preparation(encoding):
        block = original_preparation(encoding)
        nested = QuantumCircuit(4, global_phase=0.319)
        nested.append(MCXGate(3, ctrl_state=2), [2, 0, 3, 1])
        block.append(nested.to_gate(), [3, 1, 0, 2])
        return block

    monkeypatch.setattr(grover, "coloring_preparation", preparation)
    case = study.assemble_case(
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        "sb_balanced",
        "R2",
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    md = case.metadata["mcx_lowering"]
    assert len(md["search_scratch_ownership"]["preparation"]) == 1
    assert len(md["search_scratch_ownership"]["zero_reflection"]) == 1
    assert len(md["search_scratch_ownership"]["raw"]) > 0
    inverse = study._resolved_qpy_circuit(case.preparation.inverse())[0]
    assert (
        study._qpy_semantic_signature(inverse)["operations"]
        == study._qpy_semantic_signature(case.diffusion)["operations"][
            : len(inverse.data)
        ]
    )
    assert abs(np.exp(1j * float(case.diffusion.global_phase)) + 1) < 2e-12
    assert md["blocks"]["preparation"]["mcx_gates"] == 1


@pytest.mark.parametrize("fault", ("none", "opaque", "readback_phase"))
def test_restoring_saved_qpy_and_partial_failure(tmp_path, monkeypatch, fault):
    from qiskit.circuit import Gate
    import pandas as pd

    fixture = tmp_path / "edge.col"
    fixture.write_text("p edge 2 1\nx colors 3\ne 1 2\n")
    output = tmp_path / ("1026000000-" + fault)
    original_assemble = study.assemble_case
    original_load = qpy.load
    calls = [0]

    def assemble(*args, **kwargs):
        case = original_assemble(*args, **kwargs)
        if fault == "opaque" and kwargs["iterations"] == 1:
            case.preparation.append(Gate("unknown_inverse", 1, []), [0])
        return case

    def load(*args, **kwargs):
        circuits = original_load(*args, **kwargs)
        calls[0] += 1
        if fault == "readback_phase" and calls[0] == 12:
            circuits[0].global_phase += 0.125
        return circuits

    monkeypatch.setattr(study, "assemble_case", assemble)
    monkeypatch.setattr(qpy, "load", load)
    study.run_coloring_study(
        dict(
            inputs=[str(fixture)],
            methods=["sb_balanced"],
            regimes=["R2"],
            iterations=[0, 1],
            common_basis=True,
            optimization_level=0,
            output=str(output),
            mcx_decomposition="clean_tree",
            mcx_workspace="fresh_zero",
        )
    )
    manifest = json.loads((output / "run.json").read_text())
    rows = pd.read_csv(output / "summary.csv")
    assert manifest["implemented_metric_levels"] == ["restoring_mcx", "common_basis"]
    assert set(rows.metric_level) == {"restoring_mcx", "common_basis"}
    assert set(rows.mcx_decomposition) == {"clean_tree"}
    assert set(rows.mcx_workspace) == {"fresh_zero"}
    assert "costs.py" in manifest["source_hashes"]
    assert [c["status"] for c in manifest["cases"]] == [
        "complete",
        "complete" if fault == "none" else "failed",
    ]
    assert len(rows) == (20 if fault == "none" else 10)
    for case in manifest["cases"]:
        if case["status"] == "failed":
            assert case["artifacts"]
            assert set(rows.iteration) == {0}
            continue
        reference = original_assemble(
            ColoringProblem((1, 2), ((1, 2),), 3),
            "sb_balanced",
            "R2",
            iterations=case["iteration"],
            mcx_decomposition="clean_tree",
            mcx_workspace="fresh_zero",
        )
        for key, filename in case["artifacts"].items():
            with (output / filename).open("rb") as stream:
                saved = original_load(stream)[0]
            record = case["artifact_statistics"][filename]
            assert record["status"] == "verified"
            assert (
                record["readback_signatures"]["expected"]
                == record["readback_signatures"]["actual"]
            )
            assert {
                k: v for k, v in circuit_metrics(saved).items() if k != "metric_level"
            } == {k: v for k, v in record["metrics"].items() if k != "metric_level"}
            if key.endswith("_logical") or key.endswith("_restoring_mcx"):
                component = key.removesuffix("_logical").removesuffix("_restoring_mcx")
                assert study._qpy_semantic_signature(
                    saved
                ) == study._qpy_semantic_signature(reference.circuits[component])


@pytest.mark.parametrize("method", ("sb_original", "sb_simple", "sb_minimal"))
@pytest.mark.parametrize("regime", study.REGIMES)
def test_restoring_other_baseline_prefix_inverses(method, regime):
    problem = ColoringProblem((-7, 20), ((-7, 20),), 3)
    source = study.assemble_case(problem, method, regime)
    lowered = study.assemble_case(
        problem,
        method,
        regime,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    target = source.metadata["backend_metadata"]["output_qubits"][0]
    for x in range(16):
        for t in (0, 1):
            bits = x | (t << target)
            expected, phase = _restoring_scalar_column(source.raw, bits)
            actual, lowered_phase = _restoring_scalar_column(lowered.raw, bits)
            assert actual == expected and abs(phase - lowered_phase) < 2e-12


@pytest.mark.parametrize("method", ("klut_bennett", "best_fit"))
@pytest.mark.parametrize("regime", study.REGIMES)
def test_restoring_native_k5_scratch_qpy_readback(method, regime):
    import io

    if BRIDGE is None:
        pytest.skip("admitted private native bridge unavailable")
    case = study.assemble_case(
        ColoringProblem((42,), (), 5),
        method,
        regime,
        executable=BRIDGE,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    for original in case.circuits.values():
        stream = io.BytesIO()
        qpy.dump(original, stream)
        stream.seek(0)
        saved = qpy.load(stream)[0]
        assert study._qpy_semantic_signature(saved) == study._qpy_semantic_signature(
            original
        )


@pytest.mark.parametrize(
    "cap", [None, True, False, 0, -1, 1.0, 2.5, "4", "bad", [], {}, float("inf")]
)
def test_component_width_rejects_before_input_or_artifact_work(monkeypatch, cap):
    def forbidden(*args, **kwargs):
        raise AssertionError("work before configuration rejection")

    monkeypatch.setattr(study, "read_dimacs", forbidden)
    monkeypatch.setattr(study, "assemble_case", forbidden)
    from logique.benchmarks import runner

    monkeypatch.setattr(runner, "new_run_directory", forbidden)
    with pytest.raises(ValueError, match="max_component_qubits.*positive integer"):
        study.run_coloring_study(
            {"inputs": ["missing.col"], "max_component_qubits": cap}
        )


def _width_config(tmp_path, **controls):
    from datetime import datetime

    source = tmp_path / "tiny.col"
    source.write_text("p edge 1 0\nx colors 2\n")
    return {
        "inputs": [str(source)],
        "methods": ["sb_balanced"],
        "regimes": ["R2"],
        "iterations": [0],
        "seeds": [7],
        "output": str(tmp_path / f"{datetime.now():%m%d%H%M%S}-width"),
        **controls,
    }


@pytest.mark.parametrize(
    "over", ["raw", "preparation", "oracle", "diffusion", "search", "all"]
)
def test_component_width_gates_all_artifact_work(tmp_path, monkeypatch, over):
    from types import SimpleNamespace
    from logique.benchmarks import metrics

    # Width-only stand-ins: no oversized quantum object is allocated. Metadata
    # deliberately understates width to require checking actual components.
    names = ("raw", "preparation", "oracle", "diffusion", "search")
    widths = {name: 8 if over in (name, "all") else 4 for name in names}
    assembled = study.ColoringStudyCase(
        *(SimpleNamespace(num_qubits=widths[name]) for name in names),
        metadata={"component_workspace": {"stale": {"peak_reserved_qubits": 1}}},
    )
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: assembled)

    def forbidden(*args, **kwargs):
        raise AssertionError("over-budget case entered artifact/metric work")

    monkeypatch.setattr(study, "_resolved_qpy_circuit", forbidden)
    monkeypatch.setattr(metrics, "lower_circuit", forbidden)
    monkeypatch.setattr(metrics, "circuit_metrics", forbidden)
    monkeypatch.setattr(qpy, "dump", forbidden)
    output = study.run_coloring_study(
        _width_config(tmp_path, max_component_qubits=4, common_basis=True)
    )
    manifest = json.loads((output / "run.json").read_text())
    case = manifest["cases"][0]
    assert case["status"] == "excluded"
    check = case["component_width_check"]
    assert check["allocated_qubits"] == widths
    assert check["max_component_qubits"] == 4
    assert check["over_budget_components"] == [n for n in names if widths[n] > 4]
    assert check["status"] == "excluded"
    assert "max_component_qubits=4" in case["reason"]
    for name in check["over_budget_components"]:
        assert f"{name}=8" in case["reason"]
    assert json.loads((output / f'{case["name"]}.json').read_text()) == case
    assert not list(output.glob("*.qpy"))
    assert not (output / "summary.csv").exists()
    assert not case.get("artifacts")


@pytest.mark.parametrize("restoring", [False, True])
def test_component_width_equality_mixed_success_and_omission(
    tmp_path, monkeypatch, restoring
):
    import copy
    import pandas as pd
    from types import SimpleNamespace

    controls = (
        {"mcx_decomposition": "clean_tree", "mcx_workspace": "fresh_zero"}
        if restoring
        else {}
    )
    original = study.assemble_case
    tiny = ColoringProblem((1,), (), 2)
    assembled = original(tiny, "sb_balanced", "R2", iterations=0, **controls)
    cap = max(q.num_qubits for q in assembled.circuits.values())
    assert cap <= 5
    # Scalar raw predicate and ordered search composition; no dense simulation.
    target = assembled.metadata["backend_metadata"]["output_qubits"][0]
    for x in (0, 1):
        for t in (0, 1):
            out, phase = _restoring_scalar_column(assembled.raw, x | (t << target))
            assert out == (x | (t << target)) ^ (1 << target)
            assert abs(phase - 1) < 2e-12
    expected = assembled.search.copy_empty_like()
    expected.compose(
        assembled.preparation, assembled.metadata["data_qubits"], inplace=True
    )
    assert study._qpy_semantic_signature(
        study._resolved_qpy_circuit(expected)[0]
    ) == study._qpy_semantic_signature(study._resolved_qpy_circuit(assembled.search)[0])

    def fake(problem, *args, seed, **kwargs):
        case = copy.deepcopy(assembled)
        if seed == 7:
            case.search = SimpleNamespace(num_qubits=cap + 1)
        return case

    monkeypatch.setattr(study, "assemble_case", fake)
    config = _width_config(tmp_path, seeds=[7, 9], max_component_qubits=cap, **controls)
    output = study.run_coloring_study(config)
    manifest = json.loads((output / "run.json").read_text())
    assert [c["status"] for c in manifest["cases"]] == ["excluded", "complete"]
    rejected, accepted = manifest["cases"]
    assert accepted["component_width_check"]["status"] == "accepted"
    assert max(accepted["component_width_check"]["allocated_qubits"].values()) == cap
    rows = pd.read_csv(output / "summary.csv")
    assert len(rows) == 5
    assert set(rows.seed) == {9}
    assert not list(output.glob(f'{rejected["name"]}*.qpy'))

    # Omission adds neither a config default nor case field and preserves saved
    # QPY bytes and metric values (timing/provenance fields naturally differ).
    monkeypatch.setattr(
        study, "assemble_case", lambda *a, **kw: copy.deepcopy(assembled)
    )
    omitted = dict(config, seeds=[9], output=str(tmp_path / "1026123456-omitted"))
    del omitted["max_component_qubits"]
    before = study.run_coloring_study(omitted)
    old = json.loads((before / "run.json").read_text())
    assert "max_component_qubits" not in old["config"]
    assert "component_width_check" not in old["cases"][0]
    old_rows = pd.read_csv(before / "summary.csv")
    for key in ("qubits", "gates", "depth", "gate_types", "metric_level", "component"):
        assert list(rows[key]) == list(old_rows[key])
    for name in accepted["artifacts"].values():
        assert (output / name).read_bytes() == (before / name).read_bytes()


def test_component_width_counts_real_j0_reserved_mcx_pools(tmp_path, monkeypatch):
    from qiskit import QuantumCircuit
    from logique.benchmarks import metrics

    # Four data wires need one S0 scratch wire. It remains reserved at j0,
    # although search executes only A and its MCX live-capacity field is zero.
    case = study.assemble_case(
        ColoringProblem((1, 2), ((1, 2),), 3),
        "sb_balanced",
        "R2",
        iterations=0,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    owners = case.metadata["mcx_lowering"]["search_scratch_ownership"]
    assert owners["zero_reflection"]
    assert (
        case.metadata["component_workspace"]["search"]["mcx_live_peak_upper_bound"] == 0
    )
    expected = QuantumCircuit(case.search.num_qubits)
    expected.compose(
        case.preparation,
        case.metadata["mcx_lowering"]["search_embeddings"]["preparation"],
        inplace=True,
    )
    assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
        case.search
    )
    cap = case.search.num_qubits - 1
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)

    def forbidden(*args, **kwargs):
        raise AssertionError("reserved j0 width escaped artifact gate")

    monkeypatch.setattr(qpy, "dump", forbidden)
    monkeypatch.setattr(metrics, "circuit_metrics", forbidden)
    output = study.run_coloring_study(_width_config(tmp_path, max_component_qubits=cap))
    saved = json.loads((output / "run.json").read_text())["cases"][0]
    assert saved["status"] == "excluded"
    assert saved["component_width_check"]["allocated_qubits"] == {
        name: q.num_qubits for name, q in case.circuits.items()
    }
    assert "search" in saved["component_width_check"]["over_budget_components"]
    assert not list(output.glob("*.qpy"))
    assert not (output / "summary.csv").exists()


class _InstructionIntSubclass(int):
    pass


@pytest.mark.parametrize(
    "cap",
    [
        None,
        True,
        False,
        0,
        -1,
        -(10**100),
        1.0,
        2.5,
        float("nan"),
        float("inf"),
        "4",
        "",
        [],
        {},
        (),
        {1},
        complex(1),
        _InstructionIntSubclass(4),
        np.int64(4),
    ],
)
def test_component_instructions_reject_before_input_or_run(monkeypatch, cap):
    from logique.benchmarks import runner

    def forbidden(*args, **kwargs):
        raise AssertionError("work before instruction config rejection")

    monkeypatch.setattr(study, "read_dimacs", forbidden)
    monkeypatch.setattr(study, "assemble_case", forbidden)
    monkeypatch.setattr(runner, "new_run_directory", forbidden)
    with pytest.raises(
        ValueError, match="max_component_instructions.*positive integer"
    ):
        study.run_coloring_study(
            {"inputs": ["missing.col"], "max_component_instructions": cap}
        )


@pytest.mark.parametrize("cap", [1, 4, 10**100])
def test_component_instructions_positive_builtin_config(cap):
    config = study.validate_study_config(
        {"inputs": ["missing.col"], "max_component_instructions": cap}
    )
    assert config["max_component_instructions"] == cap
    assert "max_component_instructions" not in study.validate_study_config(
        {"inputs": ["missing.col"]}
    )


@pytest.mark.parametrize(
    "over", ["raw", "preparation", "oracle", "diffusion", "search", "all"]
)
@pytest.mark.parametrize("width_cap", [None, 4])
def test_component_instructions_gate_all_before_artifacts(
    tmp_path, monkeypatch, over, width_cap
):
    from types import SimpleNamespace
    from logique.benchmarks import metrics

    names = ("raw", "preparation", "oracle", "diffusion", "search")
    counts = {n: 10**9 if over in (n, "all") else 4 for n in names}
    reads = []

    class Instructions:
        def __init__(self, name):
            self.name = name

        def __len__(self):
            reads.append(self.name)
            return counts[self.name]

        def __iter__(self):
            raise AssertionError("acceptance traversed instructions")

    # Count/width stand-ins avoid allocating large synthetic quantum objects.
    assembled = study.ColoringStudyCase(
        *(SimpleNamespace(data=Instructions(n), num_qubits=4) for n in names),
        metadata={},
    )
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: assembled)

    def forbidden(*args, **kwargs):
        raise AssertionError("count exclusion entered downstream work")

    monkeypatch.setattr(study, "_resolved_qpy_circuit", forbidden)
    monkeypatch.setattr(metrics, "lower_circuit", forbidden)
    monkeypatch.setattr(metrics, "circuit_metrics", forbidden)
    monkeypatch.setattr(qpy, "dump", forbidden)
    controls = {} if width_cap is None else {"max_component_qubits": width_cap}
    output = study.run_coloring_study(
        _width_config(
            tmp_path, max_component_instructions=4, common_basis=True, **controls
        )
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    check = rec["component_instruction_check"]
    assert reads == list(names)
    assert check["top_level_instructions"] == counts
    assert check["max_component_instructions"] == 4
    assert check["over_budget_components"] == [n for n in names if counts[n] > 4]
    assert rec["status"] == check["status"] == "excluded"
    assert "mixed granularity" in check["scope"]
    for n in check["over_budget_components"]:
        assert f"{n}=1000000000" in rec["reason"]
    if width_cap is not None:
        assert rec["component_width_check"]["status"] == "accepted"
    assert json.loads((output / f'{rec["name"]}.json').read_text()) == rec
    assert not rec.get("artifacts")
    assert not list(output.glob("*.qpy"))
    assert not (output / "summary.csv").exists()


def test_component_instructions_width_rejection_short_circuits(tmp_path, monkeypatch):
    class WidthOnly:
        num_qubits = 5

        @property
        def data(self):
            raise AssertionError("instruction gate ran after width exclusion")

    case = study.ColoringStudyCase(*(WidthOnly() for _ in range(5)), metadata={})
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)
    output = study.run_coloring_study(
        _width_config(tmp_path, max_component_qubits=4, max_component_instructions=1)
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    assert rec["status"] == "excluded"
    assert "component_instruction_check" not in rec
    assert rec["component_width_check"]["status"] == "excluded"
    assert not list(output.glob("*.qpy"))


@pytest.mark.parametrize("restoring", [False, True])
@pytest.mark.parametrize("iterations", [0, 1])
def test_component_instructions_genuine_equality_omission_and_continuation(
    tmp_path, monkeypatch, restoring, iterations
):
    import copy
    import csv
    from types import SimpleNamespace

    controls = (
        {"mcx_decomposition": "clean_tree", "mcx_workspace": "fresh_zero"}
        if restoring
        else {}
    )
    assembled = study.assemble_case(
        ColoringProblem((42,), (), 3),
        "sb_balanced",
        "R2",
        iterations=iterations,
        **controls,
    )
    counts = {n: len(q.data) for n, q in assembled.circuits.items()}
    cap = max(counts.values())
    width = max(q.num_qubits for q in assembled.circuits.values())
    assert width <= 5

    def outcomes(*a, seed, **kw):
        if seed == 1:
            raise RuntimeError("intentional assembly failure")
        case = copy.deepcopy(assembled)
        if seed == 2:
            case.search = SimpleNamespace(data=range(cap + 1), num_qubits=width)
        return case

    monkeypatch.setattr(study, "assemble_case", outcomes)
    output = study.run_coloring_study(
        _width_config(
            tmp_path,
            max_component_instructions=cap,
            max_component_qubits=width,
            seeds=[1, 2, 3],
            iterations=[iterations],
            common_basis=True,
            optimization_level=0,
            **controls,
        )
    )
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    assert [c["status"] for c in manifest["cases"]] == [
        "failed",
        "excluded",
        "complete",
    ]
    failed, excluded, accepted = manifest["cases"]
    assert "component_instruction_check" not in failed
    assert "intentional assembly failure" in failed["reason"]
    check = accepted["component_instruction_check"]
    assert check["top_level_instructions"] == counts
    assert check["status"] == "accepted" and not check["over_budget_components"]
    assert accepted["component_width_check"]["status"] == "accepted"
    for rec in (failed, excluded):
        assert not list(output.glob(rec["name"] + "*.qpy"))
    rows = list(csv.DictReader((output / "summary.csv").open()))
    assert len(rows) == 10 and {r["seed"] for r in rows} == {"3"}
    for name, original in assembled.circuits.items():
        level = "restoring_mcx" if restoring else "logical"
        with (output / accepted["artifacts"][name + "_" + level]).open("rb") as f:
            assert_resolved_semantics(original, qpy.load(f)[0])

    monkeypatch.setattr(
        study, "assemble_case", lambda *a, **kw: copy.deepcopy(assembled)
    )
    omitted = study.run_coloring_study(
        _width_config(
            tmp_path,
            seeds=[3],
            iterations=[iterations],
            common_basis=True,
            optimization_level=0,
            output=str(tmp_path / "1027030000-omitted"),
            **controls,
        )
    )
    old = json.loads((omitted / "run.json").read_text())
    assert "max_component_instructions" not in old["config"]
    assert "component_instruction_check" not in old["cases"][0]
    old_rows = list(csv.DictReader((omitted / "summary.csv").open()))

    def normalize(rs):
        return [{k: v for k, v in r.items() if k != "lowering_seconds"} for r in rs]

    assert normalize(rows) == normalize(old_rows)
    for artifact in accepted["artifacts"].values():
        assert (output / artifact).read_bytes() == (omitted / artifact).read_bytes()


@pytest.mark.parametrize("failure", ["barrier", "opaque"])
def test_component_instructions_empty_barrier_nested_and_opaque(
    tmp_path, monkeypatch, failure
):
    from qiskit import QuantumCircuit
    from qiskit.circuit import Gate

    tiny = study.assemble_case(
        ColoringProblem((1,), (), 2), "sb_balanced", "R2", iterations=0
    )
    tiny.raw = QuantumCircuit(tiny.raw.num_qubits)  # empty -> zero
    tiny.preparation = QuantumCircuit(1)
    body = QuantumCircuit(1)
    for _ in range(20):
        body.x(0)
    tiny.oracle = QuantumCircuit(tiny.oracle.num_qubits)
    tiny.oracle.append(body.to_gate().inverse(), [0])  # nested -> one
    tiny.diffusion = QuantumCircuit(1)
    tiny.search = QuantumCircuit(tiny.search.num_qubits)
    if failure == "barrier":
        tiny.search.barrier()  # included -> one
    else:
        tiny.search.append(Gate("unsupported_opaque", 1, []), [0])  # opaque -> one
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: tiny)
    output = study.run_coloring_study(
        _width_config(tmp_path, max_component_instructions=1)
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    check = rec["component_instruction_check"]
    assert check["top_level_instructions"] == dict(
        raw=0, preparation=0, oracle=1, diffusion=0, search=1
    )
    assert check["status"] == "accepted"
    # Later QPY resolution still rejects unsupported opaque definitions and
    # retains previous partial artifacts; acceptance is not export admission.
    if failure == "barrier":
        assert rec["status"] == "complete"
        with (output / rec["artifacts"]["search_logical"]).open("rb") as stream:
            assert study._qpy_semantic_signature(
                qpy.load(stream)[0]
            ) == study._qpy_semantic_signature(tiny.search)
    else:
        assert rec["status"] == "failed" and failure in rec["reason"]
        assert rec["artifacts"] and list(output.glob("*.qpy"))
        assert not (output / "summary.csv").exists()


def test_component_instructions_real_reserved_j0(tmp_path, monkeypatch):
    from qiskit import QuantumCircuit

    case = study.assemble_case(
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        "sb_balanced",
        "R2",
        iterations=0,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    owners = case.metadata["mcx_lowering"]["search_scratch_ownership"]
    assert owners["zero_reflection"]
    assert (
        case.metadata["component_workspace"]["search"]["mcx_live_peak_upper_bound"] == 0
    )
    expected = QuantumCircuit(case.search.num_qubits)
    expected.compose(
        case.preparation,
        case.metadata["mcx_lowering"]["search_embeddings"]["preparation"],
        inplace=True,
    )
    # Ordered exact emitted composition also retains scalar phase and idle pools.
    assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
        case.search
    )
    counts = {n: len(q.data) for n, q in case.circuits.items()}
    assert counts["search"] < max(counts.values())
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)
    output = study.run_coloring_study(
        _width_config(
            tmp_path,
            max_component_instructions=counts["search"],
            mcx_decomposition="clean_tree",
            mcx_workspace="fresh_zero",
        )
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    assert rec["status"] == "excluded"
    assert rec["component_instruction_check"]["top_level_instructions"] == counts
    assert "oracle" in rec["component_instruction_check"]["over_budget_components"]
    assert not list(output.glob("*.qpy"))


@pytest.mark.parametrize(
    "cap",
    [
        None,
        True,
        False,
        0,
        -1,
        -(10**100),
        1.0,
        2.5,
        float("nan"),
        float("inf"),
        "4",
        "",
        [],
        {},
        (),
        {1},
        complex(1),
        _InstructionIntSubclass(4),
        np.int64(4),
    ],
)
def test_component_depth_rejects_before_input_or_run(monkeypatch, cap):
    from logique.benchmarks import runner

    def forbidden(*args, **kwargs):
        raise AssertionError("work before depth config rejection")

    monkeypatch.setattr(study, "read_dimacs", forbidden)
    monkeypatch.setattr(study, "assemble_case", forbidden)
    monkeypatch.setattr(runner, "new_run_directory", forbidden)
    with pytest.raises(ValueError, match="max_component_depth.*positive integer"):
        study.run_coloring_study(
            {"inputs": ["missing.col"], "max_component_depth": cap}
        )


@pytest.mark.parametrize("cap", [1, 4, 10**100])
def test_component_depth_positive_builtin_config(cap):
    config = study.validate_study_config(
        {"inputs": ["missing.col"], "max_component_depth": cap}
    )
    assert config["max_component_depth"] == cap
    assert "max_component_depth" not in study.validate_study_config(
        {"inputs": ["missing.col"]}
    )


@pytest.mark.parametrize(
    "over", ["raw", "preparation", "oracle", "diffusion", "search", "all"]
)
@pytest.mark.parametrize("existing_caps", [False, True])
def test_component_depth_all_offenders_once_before_artifacts(
    tmp_path, monkeypatch, over, existing_caps
):
    from logique.benchmarks import metrics

    names = ("raw", "preparation", "oracle", "diffusion", "search")
    depths = {n: 10**100 if over in (n, "all") else 4 for n in names}
    reads = []

    class DepthOnly:
        # Only existing caps may read width/count; depth never reads definitions.
        def __init__(self, name):
            self.name = name

        @property
        def num_qubits(self):
            assert existing_caps
            return 4

        @property
        def data(self):
            assert existing_caps
            return range(4)

        @property
        def definition(self):
            raise AssertionError("depth gate traversed definitions")

        def depth(self, *args, **kwargs):
            assert not args and not kwargs
            reads.append(self.name)
            assert reads.count(self.name) == 1
            return depths[self.name]

    assembled = study.ColoringStudyCase(*(DepthOnly(n) for n in names), metadata={})
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: assembled)

    def forbidden(*args, **kwargs):
        raise AssertionError("depth exclusion entered downstream work")

    monkeypatch.setattr(study, "_resolved_qpy_circuit", forbidden)
    monkeypatch.setattr(metrics, "lower_circuit", forbidden)
    monkeypatch.setattr(metrics, "circuit_metrics", forbidden)
    monkeypatch.setattr(qpy, "dump", forbidden)
    controls = (
        {"max_component_qubits": 4, "max_component_instructions": 4}
        if existing_caps
        else {}
    )
    output = study.run_coloring_study(
        _width_config(tmp_path, max_component_depth=4, common_basis=True, **controls)
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    check = rec["component_depth_check"]
    assert reads == list(names)
    assert check["depths"] == depths
    assert check["max_component_depth"] == 4
    assert check["over_budget_components"] == [n for n in names if depths[n] > 4]
    assert rec["status"] == check["status"] == "excluded"
    assert "mixed granularity" in check["scope"]
    for n in check["over_budget_components"]:
        assert f"{n}={10**100}" in rec["reason"]
    if existing_caps:
        assert rec["component_width_check"]["status"] == "accepted"
        assert rec["component_instruction_check"]["status"] == "accepted"
    assert json.loads((output / f'{rec["name"]}.json').read_text()) == rec
    assert "artifacts" not in rec and "artifact_statistics" not in rec
    assert not list(output.glob("*.qpy"))
    assert not (output / "summary.csv").exists()


@pytest.mark.parametrize("first", ["width", "count"])
def test_component_depth_existing_rejections_short_circuit(
    tmp_path, monkeypatch, first
):
    class EarlierOnly:
        num_qubits = 10**100 if first == "width" else 4

        @property
        def data(self):
            assert first == "count"
            return range(10**9)

        def depth(self):
            raise AssertionError("depth accessed after earlier rejection")

    case = study.ColoringStudyCase(*(EarlierOnly() for _ in range(5)), metadata={})
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)
    output = study.run_coloring_study(
        _width_config(
            tmp_path,
            max_component_qubits=4,
            max_component_instructions=4,
            max_component_depth=1,
        )
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    assert rec["status"] == "excluded"
    assert "component_depth_check" not in rec
    if first == "width":
        assert "component_instruction_check" not in rec
    else:
        assert rec["component_instruction_check"]["status"] == "excluded"
    assert "artifacts" not in rec
    assert not list(output.glob("*.qpy"))


@pytest.mark.parametrize("restoring", [False, True])
@pytest.mark.parametrize("iterations", [0, 1])
def test_component_depth_genuine_equality_omission_and_continuation(
    tmp_path, monkeypatch, restoring, iterations
):
    import copy
    import csv
    from types import SimpleNamespace

    controls = (
        {"mcx_decomposition": "clean_tree", "mcx_workspace": "fresh_zero"}
        if restoring
        else {}
    )
    assembled = study.assemble_case(
        ColoringProblem((42,), (), 3),
        "sb_balanced",
        "R2",
        iterations=iterations,
        **controls,
    )
    depths = {n: q.depth() for n, q in assembled.circuits.items()}
    cap = max(depths.values())
    width = max(q.num_qubits for q in assembled.circuits.values())
    count = max(len(q.data) for q in assembled.circuits.values())
    assert width <= 5

    def outcomes(*a, seed, **kw):
        assert "max_component_depth" not in kw
        if seed == 1:
            raise RuntimeError("intentional assembly failure")
        case = copy.deepcopy(assembled)
        if seed == 2:
            case.search = SimpleNamespace(
                depth=lambda: cap + 1, num_qubits=width, data=range(count)
            )
        return case

    monkeypatch.setattr(study, "assemble_case", outcomes)
    config = _width_config(
        tmp_path,
        max_component_depth=cap,
        max_component_qubits=width,
        max_component_instructions=count,
        seeds=[1, 2, 3],
        iterations=[iterations],
        common_basis=True,
        optimization_level=0,
        **controls,
    )
    output = study.run_coloring_study(config)
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete_with_failures"
    assert [c["status"] for c in manifest["cases"]] == [
        "failed",
        "excluded",
        "complete",
    ]
    failed, excluded, accepted = manifest["cases"]
    assert "component_depth_check" not in failed
    check = accepted["component_depth_check"]
    assert check["depths"] == depths and max(depths.values()) == cap
    assert check["status"] == "accepted" and not check["over_budget_components"]
    for rec in (excluded, accepted):
        assert rec["component_width_check"]["status"] == "accepted"
        assert rec["component_instruction_check"]["status"] == "accepted"
    for rec in (failed, excluded):
        assert not list(output.glob(rec["name"] + "*.qpy"))
    rows = list(csv.DictReader((output / "summary.csv").open()))
    assert len(rows) == 10 and {r["seed"] for r in rows} == {"3"}
    for name, original in assembled.circuits.items():
        level = "restoring_mcx" if restoring else "logical"
        with (output / accepted["artifacts"][name + "_" + level]).open("rb") as f:
            assert_resolved_semantics(original, qpy.load(f)[0])

    # Identical assembled objects avoid fresh autogenerated instruction-name noise.
    def fixed(*a, **kw):
        assert "max_component_depth" not in kw
        return copy.deepcopy(assembled)

    monkeypatch.setattr(study, "assemble_case", fixed)
    omitted_config = dict(
        config, seeds=[3], output=str(tmp_path / "1027090000-omitted")
    )
    del omitted_config["max_component_depth"]
    omitted = study.run_coloring_study(omitted_config)
    old = json.loads((omitted / "run.json").read_text())
    assert "max_component_depth" not in old["config"]
    assert "component_depth_check" not in old["cases"][0]
    old_rows = list(csv.DictReader((omitted / "summary.csv").open()))
    assert [{k: v for k, v in r.items() if k != "lowering_seconds"} for r in rows] == [
        {k: v for k, v in r.items() if k != "lowering_seconds"} for r in old_rows
    ]
    for artifact in accepted["artifacts"].values():
        assert (output / artifact).read_bytes() == (omitted / artifact).read_bytes()


@pytest.mark.parametrize(
    "witness",
    ["empty", "parallel", "serial", "barrier_only", "barrier", "nested", "opaque"],
)
def test_component_depth_real_default_granularity_and_partial_exports(
    tmp_path, monkeypatch, witness
):
    from qiskit import QuantumCircuit
    from qiskit.circuit import Gate

    case = study.assemble_case(
        ColoringProblem((1,), (), 2), "sb_balanced", "R2", iterations=0
    )
    case.raw = QuantumCircuit(case.raw.num_qubits)
    case.preparation = QuantumCircuit(1)
    case.oracle = QuantumCircuit(case.oracle.num_qubits)
    case.diffusion = QuantumCircuit(1)
    case.search = QuantumCircuit(2)
    expected_depth = 1
    cap = 1
    if witness == "empty":
        expected_depth = 0
    elif witness == "barrier_only":
        case.search.barrier(0, 1)
        expected_depth = 0
    elif witness == "parallel":
        case.search.x(0)
        case.search.x(1)
    elif witness == "serial":
        case.search.x(0)
        case.search.cx(0, 1)
        expected_depth = 2
    elif witness == "barrier":
        case.search.x(0)
        case.search.x(0)
        case.search.barrier(0, 1)
        case.search.x(1)
        # Ignoring the barrier completely would give 2, counting it would give 4.
        expected_depth = 3
        cap = 3
    elif witness == "nested":
        body = QuantumCircuit(2, global_phase=0.417)
        for _ in range(8):
            body.x(0)
            body.cx(0, 1)
        case.search.global_phase = -0.19
        case.search.append(body.to_gate().inverse(), [1, 0])
    else:

        class NoDefinition(Gate):
            @property
            def definition(self):
                raise AssertionError("opaque definition was traversed")

            @definition.setter
            def definition(self, value):
                pass

        case.search.append(NoDefinition("opaque_depth_witness", 2, []), [1, 0])
    assert case.search.depth() == expected_depth
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)
    output = study.run_coloring_study(_width_config(tmp_path, max_component_depth=cap))
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    check = rec["component_depth_check"]
    assert check["depths"] == dict(
        raw=0, preparation=0, oracle=0, diffusion=0, search=expected_depth
    )
    if witness == "serial":
        assert rec["status"] == check["status"] == "excluded"
        assert not list(output.glob("*.qpy"))
    elif witness == "opaque":
        assert check["status"] == "accepted" and rec["status"] == "failed"
        assert rec["artifacts"] and len(list(output.glob("*.qpy"))) == 4
        assert not (output / "summary.csv").exists()
    else:
        assert rec["status"] == "complete" and check["status"] == "accepted"
        with (output / rec["artifacts"]["search_logical"]).open("rb") as f:
            assert_resolved_semantics(case.search, qpy.load(f)[0])


def test_component_depth_real_reserved_j0(tmp_path, monkeypatch):
    from qiskit import QuantumCircuit

    case = study.assemble_case(
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        "sb_balanced",
        "R2",
        iterations=0,
        mcx_decomposition="clean_tree",
        mcx_workspace="fresh_zero",
    )
    owners = case.metadata["mcx_lowering"]["search_scratch_ownership"]
    assert owners["zero_reflection"]
    assert (
        case.metadata["component_workspace"]["search"]["mcx_live_peak_upper_bound"] == 0
    )
    expected = QuantumCircuit(case.search.num_qubits)
    expected.compose(
        case.preparation,
        case.metadata["mcx_lowering"]["search_embeddings"]["preparation"],
        inplace=True,
    )
    # Exact ordered standard-gate composition, phase and idle pools; no wide array.
    assert study._qpy_semantic_signature(expected) == study._qpy_semantic_signature(
        case.search
    )
    depths = {n: q.depth() for n, q in case.circuits.items()}
    assert depths["search"] < max(depths.values())
    monkeypatch.setattr(study, "assemble_case", lambda *a, **kw: case)
    output = study.run_coloring_study(
        _width_config(
            tmp_path,
            max_component_depth=depths["search"],
            mcx_decomposition="clean_tree",
            mcx_workspace="fresh_zero",
        )
    )
    rec = json.loads((output / "run.json").read_text())["cases"][0]
    assert rec["status"] == "excluded"
    assert rec["component_depth_check"]["depths"] == depths
    assert "oracle" in rec["component_depth_check"]["over_budget_components"]
    assert not list(output.glob("*.qpy"))
