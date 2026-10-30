"""Controlled-study inputs, baseline oracles, search instances and the runner."""

import itertools
import json
from dataclasses import replace
from pathlib import Path

import pytest

from logique import read_dimacs
from logique.coloring.counting import count_colorings
from logique.coloring.model import ColoringProblem

ROOT = Path(__file__).resolve().parents[1]
GRAPHS = ROOT / "datasets/graphs/benchmarks"


def unprecolored(name):
    return replace(read_dimacs(GRAPHS / f"{name}.col"), precolored={})


def brute_force(problem):
    return sum(
        problem.is_valid(dict(zip(problem.vertices, colors)))
        for colors in itertools.product(
            range(problem.colors), repeat=len(problem.vertices)
        )
    )


@pytest.mark.parametrize("colors", [2, 3, 4])
def test_count_colorings_matches_enumeration(colors):
    source = unprecolored("myciel3")
    kept = source.vertices[:7]
    problem = ColoringProblem(
        vertices=kept,
        edges=tuple(e for e in source.edges if e[0] in kept and e[1] in kept),
        colors=colors,
    )
    assert count_colorings(problem) == brute_force(problem)
    fixed = replace(problem, precolored={kept[0]: colors - 1})
    assert count_colorings(fixed) == brute_force(fixed)


def test_count_colorings_uses_the_complete_graph_formula_and_budget():
    assert count_colorings(unprecolored("K10")) == 3628800
    assert count_colorings(unprecolored("K5")) == 120
    assert count_colorings(unprecolored("myciel4"), budget=1000) is None


def test_verification_assignments_include_witnesses_and_violations():
    np = pytest.importorskip("numpy")
    from logique import encode_coloring
    from logique.verification import verification_assignments

    problem = unprecolored("myciel4")  # 5 colors, 3 bits: unused codes exist
    encoding = encode_coloring(problem)
    matrix, coverage = verification_assignments(encoding, samples=32, witnesses=4)
    assert coverage["status"] == "explicit" and coverage["witnesses"] == 4
    assert coverage["edge_violations"] == 4 and coverage["unused_codes"] == 4
    assert matrix.shape == (encoding.input_count, 4 + 4 + 4 + 32)

    def decoded(column):
        basis = sum(int(bit) << i for i, bit in enumerate(column))
        return problem.is_valid(encoding.decode(basis))

    valid = [decoded(matrix[:, i]) for i in range(12)]
    assert valid[:4] == [True] * 4 and not any(valid[4:])
    exhaustive, small = verification_assignments(encode_coloring(unprecolored("K3")))
    assert small["status"] == "exhaustive" and exhaustive.shape[1] == 64
    assert np.issubdtype(matrix.dtype, np.bool_)


@pytest.mark.parametrize("variant", ["original", "simple", "minimal", "balanced"])
@pytest.mark.parametrize("domain_checks", [True, False])
def test_baseline_oracles_mark_exactly_the_predicate(variant, domain_checks):
    pytest.importorskip("qiskit")
    pytest.importorskip("saha_belletti")
    from logique import encode_coloring
    from logique.synthesis.saha_belletti import baseline_oracle
    from logique.verification import verify_xor_oracle

    problem = unprecolored("K3")
    oracle = baseline_oracle(problem, variant, domain_checks=domain_checks)
    encoding = encode_coloring(problem if domain_checks else replace(problem, colors=4))
    report = verify_xor_oracle(
        oracle.circuit, data=oracle.data, target=oracle.target, encoding=encoding
    )
    assert report["status"] == "exhaustive"
    assert report["marked_assignments"] == (6 if domain_checks else 24)
    assert oracle.colors == (3 if domain_checks else 4)


@pytest.fixture
def native():
    pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    from logique.paths import native_executable

    try:
        return native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for study tests")


@pytest.mark.integration
@pytest.mark.parametrize("regime,domain", [("R1", 64), ("R2", 27), ("R3", 27)])
@pytest.mark.parametrize("method", ["xag", "best_fit", "sb_original", "sb_balanced"])
def test_one_iteration_matches_amplitude_amplification(native, method, regime, domain):
    from qiskit.quantum_info import Statevector

    from logique.benchmarks.costs import grover_success
    from logique.circuits.search import baseline_instance, logique_instance

    problem = unprecolored("K3")
    if method.startswith("sb_"):
        instance = baseline_instance(problem, method[3:], regime)
    else:
        instance = logique_instance(problem, method, regime, executable=native)
    assert instance.domain == domain and instance.validation["status"] == "exhaustive"
    probabilities = Statevector(instance.grover(1)).probabilities(instance.data)
    success = sum(
        p
        for basis, p in enumerate(probabilities)
        if problem.is_valid(instance.encoding.decode(basis))
    )
    assert success == pytest.approx(grover_success(6 / domain, 1), abs=1e-9)


@pytest.mark.parametrize("policy", ["throwaway_tree", "clean_tree", "2_dirty_kg24"])
def test_expanded_mirrored_oracle_is_exact(policy):
    np = pytest.importorskip("numpy")
    pytest.importorskip("saha_belletti")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    from logique.benchmarks.study import expand_oracle
    from logique.circuits.search import baseline_instance

    # Five colors need three bits, so the comparator uses a three-control gate;
    # R3 omits the invalid-color checks and keeps the register small.
    problem = ColoringProblem(vertices=(1, 2), edges=((1, 2),), colors=5)
    instance = baseline_instance(problem, "original", "R3")
    expanded, _ = expand_oracle(instance, policy)
    assert expanded.num_qubits <= 12
    width = instance.oracle.num_qubits
    rng = np.random.default_rng(3)
    start = QuantumCircuit(expanded.num_qubits)
    for q in [*instance.data, *instance.roles["output"]]:
        start.ry(rng.uniform(0.3, 2.8), q)
        start.rz(rng.uniform(0, 6.2), q)
    reference = start.copy()
    reference.compose(instance.oracle, range(width), inplace=True)
    actual = start.copy()
    actual.compose(expanded, inplace=True)
    overlap = np.vdot(Statevector(reference).data, Statevector(actual).data)
    assert abs(overlap) == pytest.approx(1, abs=1e-9)


def test_throwaway_ancillas_are_held_until_their_mirror():
    pytest.importorskip("saha_belletti")
    from logique.benchmarks.costs import is_mcx
    from logique.benchmarks.study import expand_oracle
    from logique.circuits.search import baseline_instance

    problem = ColoringProblem(vertices=(1, 2), edges=((1, 2),), colors=5)
    instance = baseline_instance(problem, "original", "R1")
    start, stop = instance.mirrored
    held = sum(
        inst.operation.num_ctrl_qubits - 2
        for inst in instance.oracle.data[start:stop]
        if is_mcx(inst.operation, 3)
    )
    expanded, (compute, kick) = expand_oracle(instance, "throwaway_tree")
    assert compute["garbage_ancillas"] == held > 0
    # The kick-back gate cannot use held ancillas, so its own are added on top.
    width = instance.oracle.num_qubits
    assert expanded.num_qubits == width + held + kick["appended_ancillas"]


@pytest.mark.integration
def test_study_runner_exports_every_level(native, tmp_path):
    import pandas as pd

    from logique.benchmarks.runner import load_config, run_benchmarks

    config = tmp_path / "study.json"
    config.write_text(
        json.dumps(
            {
                "kind": "study",
                "inputs": [str(GRAPHS / "K3.col")],
                "methods": ["xag", "sb_balanced"],
                "regimes": ["R1", "R3"],
                "mcx_policies": ["clean_tree"],
                "pricing": ["static", "measurement"],
                "targets": ["logical", "toffoli", "fault-tolerant"],
                "output": str(tmp_path / "1030000000-study"),
            }
        )
    )
    run = run_benchmarks(load_config(config), executable=native)
    manifest = json.loads((run / "run.json").read_text())
    assert manifest["status"] == "complete" and len(manifest["cases"]) == 4
    assert all(
        case["validation"]["status"] == "exhaustive" for case in manifest["cases"]
    )
    rows = pd.read_csv(run / "summary.csv")
    search = rows[rows.component == "search"].set_index(
        ["method", "regime", "metric_level"]
    )
    # Valid-color preparation needs one iteration, the Hadamard state two.
    assert search.loc[("xag", "R3", "fault-tolerant"), "iterations"] == 1
    assert search.loc[("xag", "R1", "fault-tolerant"), "iterations"] == 2
    # Preparation (6) + oracle (39) + diffusion (43) exact T gates for K3.
    assert search.loc[("xag", "R3", "fault-tolerant"), "t_exact"] == 88
    assisted = search.loc[
        ("xag", "R3", "fault-tolerant, measurement-assisted"), "t_exact"
    ]
    assert assisted < 88
    assert set(rows.component) >= {"preparation", "oracle", "diffusion", "search"}


def test_study_settings_reject_unknown_values():
    pytest.importorskip("qiskit")
    from logique.benchmarks.study import study_settings

    base = {"inputs": ["x.col"], "methods": ["xag"]}
    with pytest.raises(ValueError, match="regimes"):
        study_settings({**base, "regimes": ["R4"]})
    with pytest.raises(ValueError, match="mcx_policies"):
        study_settings({**base, "mcx_policies": ["unknown"]})
    with pytest.raises(ValueError, match="not available yet"):
        study_settings({**base, "optimization_profile": "esop_balancing"})
    with pytest.raises(ValueError, match="iterations"):
        study_settings({**base, "iterations": "many"})
    with pytest.raises(ValueError, match="limits"):
        study_settings({**base, "limits": {"unknown": 1}})
    assert study_settings(base)["regimes"] == ["R1", "R2", "R3"]
