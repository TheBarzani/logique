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
        {"optimization_profile": "balanced"},
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
