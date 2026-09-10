"""Input-register decoding and hardware isolation without any network use."""

from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from vcgc import ColoringProblem, encode_coloring
from vcgc.execution.local import success_probability


def test_success_probability_counts_precolors_and_unused_codes():
    encoding = encode_coloring(ColoringProblem((1, 2), ((1, 2),), 3, {1: 0}))
    assert success_probability({"0100": 4, "1100": 2, "0000": 2}, encoding) == 0.5
    with pytest.raises(ValueError):
        success_probability({"0100": 0}, encoding)
    with pytest.raises(ValueError):
        success_probability({"0": 4}, encoding)


def test_ibm_submit_and_retrieve_use_explicit_backend_and_shots(monkeypatch):
    runtime = pytest.importorskip("qiskit_ibm_runtime")
    from vcgc.execution import ibm

    backend, prepared = object(), SimpleNamespace(num_qubits=6, depth=lambda: 9)
    service = Mock()
    service.backend.return_value = backend
    sampler = Mock()
    sampler.run.return_value.job_id.return_value = "test-job"
    factory = Mock(return_value=sampler)
    monkeypatch.setattr(runtime, "SamplerV2", factory)
    monkeypatch.setattr(ibm, "prepare", lambda circuit, wires, chosen, seed: prepared)
    record = ibm.submit(
        object(),
        [0, 1],
        backend_name="test_backend",
        shots=128,
        service=service,
        seed=3,
    )
    service.backend.assert_called_once_with("test_backend")
    factory.assert_called_once_with(mode=backend)
    sampler.run.assert_called_once_with([prepared], shots=128)
    assert record["job_id"] == "test-job"
    service.job.return_value.result.return_value = [
        SimpleNamespace(
            data=SimpleNamespace(data=SimpleNamespace(get_counts=lambda: {"01": 128}))
        )
    ]
    assert ibm.retrieve("test-job", service=service)["counts"] == {"01": 128}
    with pytest.raises(ValueError):
        ibm.submit(object(), [0], backend_name="", shots=128, service=service)
