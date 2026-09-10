"""Regression checks for phase-preserving benchmark synthesis and borrowing."""

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("tweedledum")
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from pathlib import Path
from logique.synthesis import METHODS, synthesize
from logique.paths import native_executable, cache_directory
from logique.circuits.records import records_to_qiskit
from logique.verification import validate, truth_outputs, verify_small_quantum
from logique.verification.classical import input_assignments
from logique.workspace import workspace_analysis, verify_borrowing
from logique.benchmarks.datasets import download_benchmarks

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def native():
    try:
        native_executable()
    except FileNotFoundError:
        pytest.skip("Build native/boolean_synthesis before integration tests")


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("name", ["xor_and", "and4", "shared"])
def test_teaching_functions(native, method, name):
    result = synthesize(
        ROOT / "datasets" / "boolean" / "teaching" / f"{name}.v", method
    )
    assert validate(result)["wrapped_restoration"]
    verify_small_quantum(result)


@pytest.mark.parametrize("method", METHODS)
def test_constants_aliases_and_output_order(native, tmp_path, method):
    path = tmp_path / "edge.v"
    path.write_text(
        """module top(a, b, u, v, w, x, y, z);
input a, b;
output u, v, w, x, y, z;
wire p;
assign p = a & b;
assign u = ~a;
assign v = a;
assign w = p;
assign x = ~p;
assign y = 1'b0;
assign z = 1'b1;
endmodule
"""
    )
    result = synthesize(path, method)
    validate(result)
    projected = synthesize(path, method, outputs=[5, 2, 0, 2])
    validate(projected)
    verify_small_quantum(projected)


def test_rotation_export_preserves_phase():
    records = [
        {
            "kind": "rx",
            "angle": np.pi,
            "controls": [0, 1],
            "polarity": [False, True],
            "target": 2,
        }
    ]
    actual = records_to_qiskit(records, 3)
    ideal = QuantumCircuit(3)
    ideal.x(0)
    ideal.mcrx(np.pi, [0, 1], 2)
    ideal.x(0)
    assert np.allclose(Operator(actual).data, Operator(ideal).data)
    wrong = QuantumCircuit(3)
    wrong.x(0)
    wrong.ccx(0, 1, 2)
    wrong.x(0)
    assert not np.allclose(Operator(actual).data, Operator(wrong).data)


@pytest.mark.parametrize("truth", ["0110", "0010101000001000", "10110100", "0", "1"])
def test_lut_lowering_bit_order_and_negative_controls(truth):
    n = (len(truth) - 1).bit_length()
    record = {
        "kind": "lut",
        "truth": truth,
        "controls": list(range(n)),
        "polarity": [i % 2 == 0 for i in range(n)],
        "target": n,
    }
    matrix = Operator(records_to_qiskit([record], n + 1)).data
    for basis in range(1 << (n + 1)):
        index = sum(
            (((basis >> i) & 1) ^ (not record["polarity"][i])) << i for i in range(n)
        )
        target = basis ^ ((int(truth[-index - 1])) << n)
        assert np.isclose(matrix[target, basis], 1)


def test_borrowing_restores_entanglement_and_phase():
    checks = verify_borrowing()
    assert checks["conditional_workspace"]["clean_workspace"] == 1


def test_workspace_facts(native):
    result = synthesize(ROOT / "datasets/boolean/teaching/and4.v", "aig_bennett")
    report = workspace_analysis(result)
    assert report["candidates"]
    assert all(row["before_gate"] > row["after_gate"] for row in report["candidates"])
    assert report["peak_nonzero_workspace"] == 2


def test_offline_missing_and_corrupt_cache(tmp_path):
    with pytest.raises(FileNotFoundError, match="Offline cache"):
        download_benchmarks(offline=True, cache=tmp_path)
    (tmp_path / "LICENSE").write_text("not the license")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        download_benchmarks(offline=True, cache=tmp_path)


@pytest.mark.parametrize("name", ["ctrl", "int2float", "cavlc"])
def test_epfl_methods_and_formats(native, name):
    path = cache_directory() / "random_control" / f"{name}.aig"
    if not path.exists():
        pytest.skip("Download the pinned EPFL benchmarks before integration tests")
    reference = None
    for method, k in [(m, 4) for m in METHODS] + [
        ("klut_bennett", 3),
        ("klut_bennett", 6),
    ]:
        result = synthesize(path, method, k=k)
        assert validate(result)["status"] == "exhaustive"
        if reference is None:
            reference = result.metadata["source_network"]
    verilog = synthesize(path.with_suffix(".v"))
    assignments = input_assignments(len(reference["inputs"]))
    assert np.array_equal(
        truth_outputs(reference, assignments),
        truth_outputs(verilog.metadata["source_network"], assignments),
    )


def test_invalid_inputs(native, tmp_path):
    with pytest.raises(ValueError):
        synthesize("unused", "not_a_method")
    source = ROOT / "datasets/boolean/teaching/and4.v"
    with pytest.raises(RuntimeError, match="Output index"):
        synthesize(source, outputs=[99])
    with pytest.raises(RuntimeError, match="k must"):
        synthesize(source, "klut_bennett", k=17)
    path = tmp_path / "bad.v"
    path.write_text("invalid verilog")
    with pytest.raises(RuntimeError, match="parse failed"):
        synthesize(path)


def test_best_fit_nested_cleanup(native):
    path = cache_directory() / "random_control/ctrl.aig"
    if not path.exists():
        pytest.skip("Download ctrl for nested best-fit regression")
    result = synthesize(path, "best_fit", outer_cut=6, inner_cut=2)
    assert validate(result)["wrapped_restoration"]


def test_best_fit_router_stack_regression(native):
    path = cache_directory() / "random_control/router.aig"
    if not path.exists():
        pytest.skip("Download optional router for reference stack regression")
    result = synthesize(path, "best_fit")
    assert all(g["target"] not in g["controls"] for g in result.metadata["gates"])
    assert validate(result, sampled=True, samples=1024)["wrapped_restoration"]
