"""Independent small checks of physical noise mapping and study boundaries."""

import json
import math
import os
from pathlib import Path
import sys

import pytest

pytest.importorskip("qiskit_aer")
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error

from logique.benchmarks.noisy_iterations import (
    MEMORY_BYTES,
    allocation_guard,
    compact_circuit,
    compact_noise_dict,
    cost_per_success,
    random_trials,
    save_qpy,
    supervise,
    validate_config,
    wilson,
)
from logique.coloring import ColoringProblem


@pytest.fixture
def config():
    return json.loads(Path("configs/noisy_iteration_pilot.json").read_text())


@pytest.mark.parametrize(
    "key,value",
    [
        ("max_qubits", 19),
        ("timeout_seconds", 121),
        ("budget_seconds", 901),
        ("shots", 0),
        ("memory_bytes", 7 * 1024**3),
        ("seed", True),
        ("pilot_manifest_sha256", "bad"),
        ("execute", []),
    ],
)
def test_config_rejects_unsafe_controls(config, key, value):
    config[key] = value
    with pytest.raises(ValueError):
        validate_config(config)


def test_preallocation_guard(config):
    validate_config(config)
    assert allocation_guard(18, config) < MEMORY_BYTES
    with pytest.raises(ValueError):
        allocation_guard(19, config)
    config["memory_bytes"] = 128 * 1024**2
    with pytest.raises(ValueError):
        allocation_guard(18, config)


def test_wilson_endpoints_and_scope():
    zero, all_hits = wilson(0, 64), wilson(64, 64)
    assert zero["interval_95"][0] == 0
    assert 0.05 < zero["interval_95"][1] < 0.06
    assert all_hits["interval_95"][1] == 1
    assert math.isclose(zero["interval_95"][1], 1 - all_hits["interval_95"][0])
    assert wilson(32, 64)["interval_95"][0] < 0.5 < wilson(32, 64)["interval_95"][1]
    with pytest.raises(ValueError):
        wilson(1, 0)
    assert cost_per_success(12, 0, 64, "gates")["cost_over_measured_p"] is None
    assert cost_per_success(12, 16, 64, "gates")["cost_over_measured_p"] == 48


def test_compaction_retains_physical_qarg_order_phase_and_measurements(tmp_path):
    circuit = QuantumCircuit(7, 2)
    circuit.global_phase = 0.37
    circuit.h(4)
    circuit.cx(4, 1)
    circuit.delay(20, 4, unit="dt")
    circuit.delay(20, 6, unit="dt")
    circuit.measure(4, 0)
    circuit.measure(1, 1)
    compact, physical = compact_circuit(circuit)
    assert physical == [1, 4]
    assert compact.num_qubits == 2
    assert compact.count_ops()["delay"] == 1
    cx = next(i for i in compact.data if i.operation.name == "cx")
    assert [compact.find_bit(q).index for q in cx.qubits] == [1, 0]
    loaded = save_qpy(tmp_path / "circuit.qpy", compact)
    assert float(loaded.global_phase) == 0.37
    # Delay is identity; asymmetric qarg order is checked above.
    assert Statevector.from_instruction(
        loaded.remove_final_measurements(inplace=False)
    ).probabilities() == pytest.approx([0.5, 0, 0, 0.5])


def test_physical_noise_compaction_matches_independent_channels():
    # Ordered physical CZ(4,1), error on SECOND qarg; distinct readout on4.
    # An incorrect sorted-qarg mapping gives a different deterministic output.
    source = NoiseModel()
    source.add_quantum_error(pauli_error([("XI", 1)]), "cz", [4, 1])
    source.add_quantum_error(pauli_error([("X", 1)]), "x", [0])  # omitted idle
    source.add_readout_error(ReadoutError([[0, 1], [1, 0]]), [4])
    source.add_readout_error(ReadoutError([[1, 0], [0, 1]]), [1])
    circuit = QuantumCircuit(5, 2)
    circuit.cz(4, 1)
    circuit.measure(4, 0)
    circuit.measure(1, 1)
    compact, physical = compact_circuit(circuit)
    snapshot = compact_noise_dict(source.to_dict(serializable=True), physical)
    mapped = NoiseModel.from_dict(snapshot)
    independent = NoiseModel()
    independent.add_quantum_error(pauli_error([("XI", 1)]), "cz", [1, 0])
    independent.add_readout_error(ReadoutError([[0, 1], [1, 0]]), [1])
    for model, subject in (
        (source, circuit),
        (mapped, compact),
        (independent, compact),
    ):
        counts = (
            AerSimulator(
                method="statevector", noise_model=model, max_parallel_threads=1
            )
            .run(subject, shots=16, seed_simulator=9)
            .result()
            .get_counts()
        )
        assert counts == {"11": 16}
    # Every retained serialized channel remains byte-for-byte identical except qargs.
    original = source.to_dict(serializable=True)["errors"]
    for error in snapshot["errors"]:
        physical_qargs = [[physical[q] for q in error["gate_qubits"][0]]]
        recovered = dict(error, gate_qubits=physical_qargs)
        assert recovered in original


def test_reject_default_or_nonlocal_noise():
    with pytest.raises(ValueError):
        compact_noise_dict({"errors": [{"type": "qerror"}]}, [3])
    with pytest.raises(ValueError):
        compact_noise_dict(
            {
                "errors": [
                    {"type": "qerror", "gate_qubits": [[3]], "noise_qubits": [[2]]}
                ]
            },
            [3],
        )
    with pytest.raises(ValueError):
        compact_noise_dict({"errors": []}, [3, 3])


def test_random_trials_declared_domain_and_seed():
    triangle = ColoringProblem((0, 1, 2), ((0, 1), (0, 2), (1, 2)), 3)
    result = random_trials(triangle, "R2", 1, 1000, 11)
    assert result == random_trials(triangle, "R2", 1, 1000, 11)
    assert result["unused_code_per_draw"]["successes"] == 0
    assert result["analytical_batch_success"] == pytest.approx(1 - (21 / 27) ** 2)
    assert (
        result["batch_success"]["interval_95"][0]
        < result["analytical_batch_success"]
        < result["batch_success"]["interval_95"][1]
    )
    binary = random_trials(triangle, "R1", 0, 1000, 11)
    assert binary["unused_code_per_draw"]["successes"] > 0


def test_supervisor_records_success_failure_and_timeout(tmp_path):
    for label, code, seconds, expected in (
        ("ok", "print('saved')", 5, "finished"),
        ("fail", "raise RuntimeError('retained failure')", 5, "failed"),
        ("timeout", "import time; time.sleep(2)", 0.1, "timeout"),
    ):
        result = supervise(
            [sys.executable, "-c", code],
            tmp_path / f"{label}.log",
            dict(os.environ),
            seconds,
            MEMORY_BYTES,
        )
        assert result["status"] == expected
        assert result["wait4_invocation_high_water_bytes"] > 0
    assert "retained failure" in (tmp_path / "fail.log").read_text()
    with pytest.raises(FileExistsError):
        supervise(
            [sys.executable, "-c", "pass"],
            tmp_path / "ok.log",
            dict(os.environ),
            5,
            MEMORY_BYTES,
        )


def test_measured_signature_detects_order_phase_delay_and_gate_changes(tmp_path):
    from logique.benchmarks.noisy_iterations import measured_qpy_signature

    original = QuantumCircuit(3, 2)
    original.global_phase = 0.19
    original.cx(2, 0)
    original.delay(13, 2, unit="dt")
    original.measure(2, 1)
    original.measure(0, 0)
    signature = measured_qpy_signature(original)
    assert (
        measured_qpy_signature(save_qpy(tmp_path / "measured.qpy", original))
        == signature
    )
    for change in ("qargs", "cargs", "phase", "duration", "unit", "gate"):
        changed = QuantumCircuit(3, 2)
        changed.global_phase = 0.29 if change == "phase" else 0.19
        if change == "gate":
            changed.cz(2, 0)
        else:
            changed.cx(0, 2) if change == "qargs" else changed.cx(2, 0)
        changed.delay(
            17 if change == "duration" else 13,
            2,
            unit="ns" if change == "unit" else "dt",
        )
        changed.measure(2, 0 if change == "cargs" else 1)
        changed.measure(0, 1 if change == "cargs" else 0)
        assert measured_qpy_signature(changed) != signature
    with pytest.raises(FileExistsError):
        save_qpy(tmp_path / "measured.qpy", original)
    original.x(2)
    with pytest.raises(ValueError, match="terminal"):
        measured_qpy_signature(original)


def test_supervisor_expired_setup_reaps_and_receipts(tmp_path, monkeypatch):
    import logique.benchmarks.noisy_iterations as subject

    ticks = iter([0.0, 2.0, 2.1])
    monkeypatch.setattr(subject.time, "monotonic", lambda: next(ticks))
    log = tmp_path / "setup.log"
    receipt = supervise(
        [sys.executable, "-c", "import time; time.sleep(3)"],
        log,
        dict(os.environ),
        1,
        MEMORY_BYTES,
    )
    assert receipt["status"] == "timeout"
    assert receipt["reaped"]
    assert json.loads(log.with_suffix(".log.receipt.json").read_text()) == receipt
    with pytest.raises(ChildProcessError):
        os.waitpid(receipt["child_pid"], os.WNOHANG)


def test_supervisor_unavailable_ps_stops_safely(tmp_path, monkeypatch):
    import logique.benchmarks.noisy_iterations as subject

    def unavailable(*args, **kwargs):
        raise PermissionError("ps unavailable")

    monkeypatch.setattr(subject.subprocess, "run", unavailable)
    receipt = supervise(
        [sys.executable, "-c", "import time; time.sleep(3)"],
        tmp_path / "ps.log",
        dict(os.environ),
        5,
        MEMORY_BYTES,
    )
    assert receipt["status"] == "memory_sampling_unavailable"
    assert receipt["reaped"] and receipt["rss_sampling"] == "unavailable"
    assert receipt["sampled_direct_child_peak_rss_bytes"] is None


def test_supervisor_launch_failure_receipt(tmp_path):
    receipt = supervise(
        ["/no-such-logique-executable"],
        tmp_path / "launch.log",
        dict(os.environ),
        5,
        MEMORY_BYTES,
    )
    assert receipt["status"] == "launch_failed"
    assert not receipt["reaped"] and receipt["child_pid"] is None


def test_scheduled_qpy_preserves_layout_and_rejects_mutation(tmp_path, monkeypatch):
    from qiskit import qpy, transpile
    from logique.benchmarks.noisy_iterations import measured_qpy_signature
    from logique.benchmarks.routing import default_backend

    circuit = QuantumCircuit(3, 2)
    circuit.ry(0.73, 0)
    circuit.cx(0, 2)
    circuit.rz(0.47, 2)
    circuit.cx(0, 2)
    circuit.measure(0, 1)
    circuit.measure(1, 0)
    routed = transpile(
        circuit,
        backend=default_backend(),
        seed_transpiler=11,
        optimization_level=3,
        scheduling_method="alap",
    )
    loaded = save_qpy(tmp_path / "scheduled.qpy", routed)
    assert measured_qpy_signature(loaded) == measured_qpy_signature(routed)
    assert loaded.layout.final_index_layout() == routed.layout.final_index_layout()
    changed = routed.copy()
    changed.global_phase += 0.3
    monkeypatch.setattr(qpy, "load", lambda stream: [changed])
    with pytest.raises(AssertionError, match="semantics changed"):
        save_qpy(tmp_path / "corrupt.qpy", routed)


def test_supervisor_cleanup_kill_race_keeps_receipt(tmp_path, monkeypatch):
    import logique.benchmarks.noisy_iterations as subject

    def denied_group(pid, sig):
        raise PermissionError("synthetic group-signal race")

    monkeypatch.setattr(subject.os, "killpg", denied_group)
    receipt = supervise(
        [sys.executable, "-c", "import time; time.sleep(3)"],
        tmp_path / "killrace.log",
        dict(os.environ),
        0.02,
        MEMORY_BYTES,
    )
    assert receipt["reaped"]
    assert receipt["status"] == "timeout"
    assert receipt["errors"]


def test_layout_filter_does_not_depend_on_virtual_dictionary_order():
    from qiskit.transpiler import Layout, TranspileLayout

    original = QuantumCircuit(2)
    physical = QuantumCircuit(3)
    # Ancilla inserted before data: Qiskit 2.1.1 filtered helper raises here.
    ancilla = physical.qubits[2]
    layout = TranspileLayout(
        initial_layout=Layout(
            {ancilla: 0, original.qubits[0]: 2, original.qubits[1]: 1}
        ),
        input_qubit_mapping={original.qubits[0]: 0, original.qubits[1]: 1, ancilla: 2},
        _input_qubit_count=2,
        _output_qubit_list=physical.qubits,
    )
    assert layout.initial_index_layout(filter_ancillas=False)[:2] == [2, 1]
    assert layout.final_index_layout(filter_ancillas=True) == [2, 1]


def test_json_kraus_and_complex_unitary_channels_preserve_order_and_shape():
    import numpy as np
    from qiskit_aer.noise import amplitude_damping_error, coherent_unitary_error
    from logique.benchmarks.noisy_iterations import noise_from_snapshot

    source = NoiseModel()
    phase = np.diag([1, 1j, -1j, -1]).astype(complex)
    channel = amplitude_damping_error(0.31).tensor(amplitude_damping_error(0.07))
    channel = channel.compose(coherent_unitary_error(phase))
    source.add_quantum_error(channel, "cz", [6, 2])
    source.add_readout_error(ReadoutError([[0.93, 0.07], [0.19, 0.81]]), [2])
    serialized = json.loads(json.dumps(source.to_dict(serializable=True)))
    before = json.dumps(serialized, sort_keys=True)
    compact = compact_noise_dict(serialized, [2, 6])
    mapped = noise_from_snapshot(compact)
    # Independent channel matrices: two local wires only, ordered [6,2]->[1,0].
    actual = mapped._local_quantum_errors["cz"][(1, 0)].to_quantumchannel().data
    assert actual.shape == (16, 16)
    np.testing.assert_allclose(actual, channel.to_quantumchannel().data, atol=1e-14)
    np.testing.assert_allclose(
        mapped._local_readout_errors[(0,)].probabilities,
        source._local_readout_errors[(2,)].probabilities,
    )
    assert json.dumps(serialized, sort_keys=True) == before
    circuit = QuantumCircuit(7, 2)
    circuit.h(6)
    circuit.x(2)
    circuit.cz(6, 2)
    circuit.measure(6, 0)
    circuit.measure(2, 1)
    small, physical = compact_circuit(circuit)
    assert physical == [2, 6]
    counts = []
    for model, subject in ((source, circuit), (mapped, small)):
        counts.append(
            AerSimulator(
                method="statevector",
                noise_model=model,
                max_parallel_threads=1,
                max_parallel_shots=1,
                max_parallel_experiments=1,
            )
            .run(subject, shots=128, seed_simulator=19)
            .result()
            .get_counts()
        )
    assert counts[0] == counts[1]


def test_json_channel_rejects_malformed_or_wide_matrices():
    from logique.benchmarks.noisy_iterations import noise_from_snapshot

    def snapshot(qubits, matrix):
        return {
            "errors": [
                {
                    "type": "qerror",
                    "instructions": [
                        [
                            {
                                "name": "kraus",
                                "qubits": qubits,
                                "params": [matrix],
                            }
                        ]
                    ],
                }
            ]
        }

    with pytest.raises(ValueError, match="two-wire"):
        noise_from_snapshot(snapshot([0, 1, 2], []))
    with pytest.raises(ValueError, match="dimensions"):
        noise_from_snapshot(snapshot([0], [[[1, 0]]]))
    with pytest.raises(ValueError, match="scalar pair"):
        noise_from_snapshot(snapshot([0], [[1, 0], [0, 1]]))


def test_completion_requires_every_requested_row_and_counts():
    from logique.benchmarks.noisy_iterations import finalize_result

    record = {
        "status": "complete",
        "rows": [
            {"iterations": 0, "status": "complete"},
            {"iterations": 1, "status": "running"},
            {"iterations": 2, "status": "not_started"},
        ],
    }
    finalize_result(record, "timeout", 64)
    assert record["status"] == "partial_with_explicit_statuses"
    assert [r["status"] for r in record["rows"]] == [
        "partial_without_noisy_counts",
        "timeout",
        "timeout",
    ]
    finalize_result({"rows": []}, "failed", 64)
    complete = {"rows": [{"status": "complete", "counts": {"0": 64}}]}
    finalize_result(complete, "finished", 64)
    assert complete["status"] == "complete"


def test_failed_setup_retains_all_requested_iterations(config, tmp_path, monkeypatch):
    import logique.benchmarks.noisy_iterations as subject

    def failed(request, record):
        record["rows"][0]["status"] = "running"
        raise RuntimeError("synthetic setup failure")

    monkeypatch.setattr(subject, "_execute_seed", failed)
    output = tmp_path / "child"
    with pytest.raises(RuntimeError, match="setup failure"):
        subject.execute_seed(
            {"config": config, "name": "path3_k2_R1", "seed": 11, "output": str(output)}
        )
    result = json.loads((output / "result.json").read_text())
    assert len(result["rows"]) == 3
    assert all(r["status"] == "failed" for r in result["rows"])
    assert result["status"] == "partial_with_explicit_statuses"


def test_supervisor_interruption_reaps_owned_child(tmp_path, monkeypatch):
    import logique.benchmarks.noisy_iterations as subject

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt("synthetic interruption")

    monkeypatch.setattr(subject.subprocess, "run", interrupted)
    receipt = supervise(
        [sys.executable, "-c", "import time; time.sleep(3)"],
        tmp_path / "interrupt.log",
        dict(os.environ),
        5,
        MEMORY_BYTES,
    )
    assert receipt["status"] == "interrupted"
    assert receipt["reaped"]


@pytest.mark.parametrize(
    "mode", ["empty", "interrupted", "launch_failed", "budget", "before_launch"]
)
def test_schedule_finalizes_empty_interrupted_unlaunched_and_budget(
    config, tmp_path, monkeypatch, mode
):
    import logique.benchmarks.noisy_iterations as subject
    import logique.benchmarks.routing as routing

    config["execute"] = ["path3_k2_R1"]
    monkeypatch.setattr(routing, "SEEDS", (11, 23))

    def supervisor(command, log, env, seconds, memory):
        if mode == "interrupted":
            request = json.loads(Path(command[-1]).read_text())
            child = Path(request["output"])
            child.mkdir()
            subject._write(
                child / "result.json",
                {
                    "status": "running",
                    "rows": [
                        {"iterations": 0, "status": "complete"},
                        {"iterations": 1, "status": "running"},
                        {"iterations": 2, "status": "not_started"},
                    ],
                },
            )
            # A killed supervisor can leave an empty reserved receipt.
            log.with_suffix(".log.receipt.json").touch()
            raise KeyboardInterrupt("synthetic coordinator interruption")
        return {"status": "launch_failed" if mode == "launch_failed" else "finished"}

    monkeypatch.setattr(subject, "supervise", supervisor)
    if mode == "before_launch":

        def interrupted(*args, **kwargs):
            raise KeyboardInterrupt("synthetic prelaunch interruption")

        monkeypatch.setattr(subject.subprocess, "check_output", interrupted)
    if mode == "budget":
        ticks = iter([0, 1000, 1001, 1002])
        monkeypatch.setattr(subject.time, "monotonic", lambda: next(ticks))
    output = subject.run_study(config, root=tmp_path)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["status"] != "running"
    statuses = [c["status"] for c in manifest["children"]]
    assert (
        statuses
        == {
            "empty": ["empty_child_result"] * 2,
            "interrupted": ["interrupted_without_receipt", "not_launched"],
            "launch_failed": ["launch_failed"] * 2,
            "budget": ["budget_excluded"] * 2,
            "before_launch": ["not_launched"] * 2,
        }[mode]
    )
    entry = next(e for e in manifest["scope_ledger"] if e["name"] == "path3_k2_R1")
    assert entry["noise_status"] == "partial_or_failed"
    assert all(s["requested_iterations"] == [0, 1, 2] for s in entry["seeds"])
    for seed in entry["seeds"]:
        assert [r["iterations"] for r in seed["iteration_statuses"]] == [0, 1, 2]
        assert seed["completed_iterations"] == []
    if mode == "interrupted":
        result = json.loads((output / "path3_k2_R1_seed11/result.json").read_text())
        assert result["rows"][0]["status"] == "partial_without_noisy_counts"
        assert result["rows"][1]["status"] == "interrupted_without_receipt"


def _assert_full_ideal_scope(manifest, pilot):
    """Check the exact admitted input, including the formerly absent 50 requests."""
    total = executed = 0
    for entry in manifest["scope_ledger"]:
        reference = json.loads((pilot / entry["name"] / "result.json").read_text())
        iterations = [r["iterations"] for r in reference["analytical_ledger"]["rows"]]
        assert [s["seed"] for s in entry["seeds"]] == [11, 23, 37, 41, 53]
        for seed in entry["seeds"]:
            assert seed["requested_iterations"] == iterations
            assert [r["iterations"] for r in seed["iteration_statuses"]] == iterations
            total += len(seed["requested_iterations"])
        executed += len(reference["rows"]) * 5
    assert total == 805
    assert executed == 755  # Executed ideal rows omit the excluded C5 requests.
    excluded = [
        e for e in manifest["scope_ledger"] if e["name"] in ("C5_k3_R1", "C5_k3_R2")
    ]
    assert len(excluded) == 2
    for entry in excluded:
        reference = json.loads((pilot / entry["name"] / "result.json").read_text())
        assert reference["rows"] == []
        assert entry["ideal_status"] == "infeasible"
        assert entry["width"] == 22
        expected = list(range(6 if entry["name"] == "C5_k3_R1" else 4))
        for seed in entry["seeds"]:
            assert seed["requested_iterations"] == expected
            assert seed["completed_iterations"] == []
            assert seed["result_status"] is None
            assert all(
                r["status"] == "ideal_infeasible" for r in seed["iteration_statuses"]
            )
    assert (
        sum(len(s["requested_iterations"]) for e in excluded for s in e["seeds"]) == 50
    )


@pytest.mark.parametrize("selected_excluded", [False, True])
@pytest.mark.parametrize(
    "boundary_stage", ["initial_write", "before_launch", "within_launch"]
)
def test_exact_805_requests_persist_before_and_after_launch(
    config, tmp_path, monkeypatch, selected_excluded, boundary_stage
):
    import logique.benchmarks.noisy_iterations as subject

    pilot = Path(config["ideal_pilot"])
    if selected_excluded:
        config["execute"] = ["C5_k3_R1", "C5_k3_R2", "path3_k2_R1"]

    def boundary(command, log, env, seconds, memory):
        manifest = json.loads((log.parent / "manifest.json").read_text())
        _assert_full_ideal_scope(manifest, pilot)
        # No excluded ideal QPY exists: such children must never be launched.
        assert "C5" not in log.name
        assert not list(log.parent.glob("*/result.json"))
        raise KeyboardInterrupt("injected first-launch boundary")

    if boundary_stage == "before_launch":

        def before_launch(*args, **kwargs):
            (manifest_path,) = tmp_path.glob("*/manifest.json")
            _assert_full_ideal_scope(json.loads(manifest_path.read_text()), pilot)
            raise KeyboardInterrupt("injected prelaunch boundary")

        monkeypatch.setattr(subject.subprocess, "check_output", before_launch)
    elif boundary_stage == "initial_write":
        write = subject._write
        interrupted = False

        def first_write(path, value):
            nonlocal interrupted
            write(path, value)
            if path.name == "manifest.json" and not interrupted:
                interrupted = True
                _assert_full_ideal_scope(json.loads(path.read_text()), pilot)
                raise KeyboardInterrupt("injected first-write boundary")

        monkeypatch.setattr(subject, "_write", first_write)
    monkeypatch.setattr(subject, "supervise", boundary)
    output = subject.run_study(config, root=tmp_path)
    manifest = json.loads((output / "manifest.json").read_text())
    _assert_full_ideal_scope(manifest, pilot)
    assert manifest["status"] == "interrupted_schedule_not_scientific_admission"
    assert "boundary" in manifest["interruption"]
    assert all(
        s["completed_iterations"] == []
        for e in manifest["scope_ledger"]
        for s in e["seeds"]
    )
    selected = next(e for e in manifest["scope_ledger"] if e["name"] == "path3_k2_R1")
    assert [s["process_status"] for s in selected["seeds"]] == [
        (
            "interrupted_without_receipt"
            if boundary_stage == "within_launch"
            else "not_launched"
        ),
        "not_launched",
        "not_launched",
        "not_launched",
        "not_launched",
    ]


def _forced_sampling_child(request_path):
    """Run the real persistence/validation path with <=3 wires and a blocked mock."""
    import signal
    from types import SimpleNamespace
    from unittest.mock import patch
    from qiskit import qpy
    from qiskit.transpiler import Layout, TranspileLayout
    import qiskit
    import qiskit_aer
    import logique.benchmarks.noisy_iterations as subject
    import logique.benchmarks.routing as routing

    request = json.loads(Path(request_path).read_text())
    pilot = Path(request["config"]["ideal_pilot"])
    case_dir = pilot / request["name"]
    case_dir.mkdir(parents=True)
    preparation = QuantumCircuit(2)
    preparation.h([0, 1])
    parts = [preparation, QuantumCircuit(3), QuantumCircuit(2)]
    for name, part in zip(("preparation", "oracle", "diffusion"), parts):
        with (case_dir / f"{name}.qpy").open("xb") as stream:
            qpy.dump(part, stream)
    reference = {
        "status": "complete",
        "case": {"name": "edge", "vertices": [0, 1], "edges": [[0, 1]], "colors": 2},
        "regime": "R1",
        "construction": {"width": 3},
        "counts": {"data_bits": 2},
        "analytical_ledger": {"rows": [{"iterations": 0}]},
        "rows": [
            {
                "iterations": 0,
                "analytical_ledger_prediction": 0.5,
                "simulated_valid_solution_probability": 0.5,
            }
        ],
    }
    subject._write(case_dir / "result.json", reference)
    backend_dir = Path(request["output"]).parent / "backend"
    backend_dir.mkdir()
    noise = NoiseModel()
    noise.add_quantum_error(pauli_error([("X", 0.1), ("I", 0.9)]), "h", [2])
    subject._write(backend_dir / "noise.json", noise.to_dict(serializable=True))

    def route(circuit, **kwargs):
        mapped = [2, 0, 1]
        routed = QuantumCircuit(3, 2)
        for item in circuit.data:
            routed.append(
                item.operation,
                [mapped[circuit.find_bit(q).index] for q in item.qubits],
                [circuit.find_bit(c).index for c in item.clbits],
            )
        routed._layout = TranspileLayout(
            initial_layout=Layout({q: mapped[i] for i, q in enumerate(circuit.qubits)}),
            input_qubit_mapping={q: i for i, q in enumerate(circuit.qubits)},
            _input_qubit_count=3,
            _output_qubit_list=routed.qubits,
        )
        return routed

    class BlockedSampler:
        def __init__(self, noise_model, **options):
            assert noise_model._local_quantum_errors

        def run(self, circuit, **options):
            # This is the exact boundary BEFORE any sampler work, rather than
            # a fake saved row. SIGKILL cannot execute child finally handlers.
            subject._write(
                Path(request["output"]).parent / "sampling-boundary.json", options
            )
            os.kill(os.getpid(), signal.SIGSTOP)
            raise AssertionError("blocked sampler unexpectedly resumed")

    with (
        patch.object(subject, "_components", return_value=(parts, [])),
        patch.object(
            routing, "default_backend", return_value=SimpleNamespace(target=None)
        ),
        patch.object(
            routing,
            "_seed_metrics",
            return_value={"two_qubit_count": 0, "duration_s": 0},
        ),
        patch.object(qiskit, "transpile", route),
        patch.object(qiskit_aer, "AerSimulator", BlockedSampler),
    ):
        subject.execute_seed(request)


def test_forced_kill_preserves_validated_pre_sampling_metadata(
    config, tmp_path, monkeypatch
):
    import signal
    import subprocess
    import logique.benchmarks.noisy_iterations as subject

    config.update(
        ideal_pilot=str(tmp_path / "ideal"),
        max_qubits=3,
        memory_bytes=2 * 1024**3,
        random_batches=1,
    )
    request = {
        "config": config,
        "name": "tiny",
        "seed": 11,
        "output": str(tmp_path / "tiny_seed11"),
    }
    request_path = tmp_path / "request.json"
    subject._write(request_path, request)
    boundary = tmp_path / "sampling-boundary.json"

    def observe(command, **kwargs):
        if boundary.exists():
            raise KeyboardInterrupt("force SIGKILL at pre-sampling boundary")
        # The outer test runner measures RSS. Avoid relying on ps permissions
        # to synchronize this deterministic three-wire persistence regression.
        return subprocess.CompletedProcess(command, 0, stdout="1\n", stderr="")

    monkeypatch.setattr(subject.subprocess, "run", observe)
    receipt = subject.supervise(
        [
            sys.executable,
            "-c",
            "import runpy,sys; runpy.run_path(sys.argv[1])['_forced_sampling_child'](sys.argv[2])",
            str(Path(__file__).resolve()),
            str(request_path),
        ],
        tmp_path / "forced-kill.log",
        dict(os.environ),
        15,
        2 * 1024**3,
    )
    assert receipt["status"] == "interrupted", (
        receipt,
        (tmp_path / "forced-kill.log").read_text(),
    )
    assert receipt["returncode"] == -signal.SIGKILL
    assert receipt["reaped"]
    with pytest.raises(ChildProcessError):
        os.waitpid(receipt["child_pid"], os.WNOHANG)
    result_path = Path(request["output"]) / "result.json"
    before = json.loads(result_path.read_text())
    subject._write(tmp_path / "pre-reconciliation.json", before)
    row = before["rows"][0]
    assert row["status"] == "running"
    assert row["stage"] == "validated_pre_sampling"
    assert row["seed_simulator"] == 72128
    assert row["working_set_estimate_bytes"] == 8 * 16 * 4 + 128 * 1024**2
    assert row["measurement_compact_wires_lsb_first"] == [1, 0]
    validation = row["routed_noiseless_validation"]
    assert validation["state_norm_squared"] == pytest.approx(1)
    assert validation["restored_workspace_probability"] == pytest.approx(1)
    assert validation["max_data_marginal_error"] < config["tolerance"]
    assert validation["full_state_error_up_to_global_phase"] < config["tolerance"]
    assert "counts" not in row and "noisy_success" not in row
    scope = subject._requested_scope(
        {"cases": [{"name": "tiny"}]}, Path(config["ideal_pilot"]), ["tiny"], (11,)
    )
    manifest = {
        "config": config | {"execute": ["tiny"]},
        "scope_ledger": scope,
        "children": [receipt | {"name": "tiny_seed11"}],
    }
    subject._reconcile_scope(manifest, tmp_path, config["shots"])
    subject._write(tmp_path / "terminal-ownership.json", manifest)
    after = json.loads(result_path.read_text())
    assert after["status"] == "partial_with_explicit_statuses"
    assert after["rows"][0] == row | {"status": "interrupted"}
    seed = scope[0]["seeds"][0]
    assert seed["iteration_statuses"] == [{"iterations": 0, "status": "interrupted"}]
    assert seed["completed_iterations"] == []
    assert seed["process_status"] == "interrupted"


def test_parent_keeps_missing_rows_and_rejects_uncounted_completion(tmp_path):
    import logique.benchmarks.noisy_iterations as subject

    result_dir = tmp_path / "tiny_seed11"
    result_dir.mkdir()
    subject._write(
        result_dir / "result.json",
        {
            "status": "complete",
            "rows": [
                {"iterations": 0, "status": "complete", "counts": {"0": 64}},
                {"iterations": 1, "status": "complete"},
            ],
        },
    )
    seed = {"seed": 11, "requested_iterations": [0, 1, 2]}
    entry = {"name": "tiny", "seeds": [seed]}
    manifest = {
        "config": {"execute": ["tiny"]},
        "scope_ledger": [entry],
        "children": [{"name": "tiny_seed11", "status": "finished"}],
    }
    subject._reconcile_scope(manifest, tmp_path, 64)
    assert seed["iteration_statuses"] == [
        {"iterations": 0, "status": "complete"},
        {"iterations": 1, "status": "partial_without_noisy_counts"},
        {"iterations": 2, "status": "missing_child_row"},
    ]
    assert seed["completed_iterations"] == [0]
    assert entry["noise_status"] == "partial_or_failed"
