"""Known witnesses must exercise the marking branch of sampled checks."""

import json

import pytest

np = pytest.importorskip("numpy")

from logique.benchmarks.runner import load_config  # noqa: E402
from logique.verification.classical import verification_assignments  # noqa: E402


def integers(bits):
    return [sum(int(bit) << i for i, bit in enumerate(row)) for row in bits.T]


def test_explicit_witnesses_supplement_deterministic_samples():
    original, _ = verification_assignments(14, sampled=True, samples=2, seed=7)
    missing = next(value for value in range(1 << 14) if value not in integers(original))
    selected, report = verification_assignments(
        14, sampled=True, samples=2, seed=7, assignments=[missing, missing]
    )
    np.testing.assert_array_equal(selected[:, :2], original)
    assert integers(selected)[-1] == missing
    assert report == {
        "explicit_assignments": [missing],
        "explicit_assignments_added": 1,
    }


def test_explicit_inputs_preserve_exhaustive_and_zero_input_coverage():
    selected, report = verification_assignments(2, assignments=[3, 0])
    assert integers(selected) == [0, 1, 2, 3]
    assert report["explicit_assignments_added"] == 0
    selected, _ = verification_assignments(0, assignments=[0])
    assert selected.shape == (0, 1)


def test_large_input_register_does_not_truncate_witness_integers():
    witness = (1 << 69) | 1
    selected, _ = verification_assignments(
        70, sampled=True, samples=1, assignments=[witness]
    )
    assert witness in integers(selected)


@pytest.mark.parametrize("assignment", [-1, 8, 1.0, True, "001"])
def test_invalid_explicit_assignments_are_rejected(assignment):
    with pytest.raises(ValueError, match="assignment"):
        verification_assignments(3, assignments=[assignment])


def test_config_accepts_verification_assignments(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"inputs": ["path.col"], "verification_assignments": [5]})
    )
    assert load_config(path)["verification_assignments"] == [5]


@pytest.mark.integration
def test_positive_witness_exposes_unmarked_solution_in_large_sampled_oracle():
    pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    from qiskit import QuantumCircuit
    from logique import ColoringProblem, encode_coloring
    from logique.paths import native_executable
    from logique.synthesis import synthesize
    from logique.verification import validate, verify_phase_oracle

    try:
        native_executable()
    except FileNotFoundError:
        pytest.skip("Native executable not configured")
    problem = ColoringProblem(tuple(range(13)), tuple((i, i + 1) for i in range(12)), 2)
    encoding = encode_coloring(problem)
    witness = sum((i % 2) << i for i in range(13))
    assert problem.is_valid(encoding.decode(witness))
    result = synthesize(encoding)
    missing_mark = QuantumCircuit(result.circuit.num_qubits)
    # A single random negative input cannot distinguish identity from the oracle.
    report = verify_phase_oracle(
        result, encoding=encoding, circuit=missing_mark, sampled=True, samples=1
    )
    assert report["marked_assignments"] == 0
    with pytest.raises(AssertionError, match="phase marking"):
        verify_phase_oracle(
            result,
            encoding=encoding,
            circuit=missing_mark,
            sampled=True,
            samples=1,
            assignments=[witness],
        )
    report = verify_phase_oracle(
        result, encoding=encoding, sampled=True, samples=1, assignments=[witness]
    )
    assert report["status"] == "sampled"
    assert report["marked_assignments"] == 1
    assert report["explicit_assignments"] == [witness]
    assert validate(result, sampled=True, samples=1, assignments=[witness])[
        "wrapped_restoration"
    ]
