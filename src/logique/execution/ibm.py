"""Optional IBM execution: preparation, explicit submission, and retrieval."""

import os
from pathlib import Path
from .local import measured_circuit


def create_service():
    """Use an explicit local .env or an account already saved by the IBM SDK."""
    from dotenv import load_dotenv
    from qiskit_ibm_runtime import QiskitRuntimeService

    load_dotenv(Path.cwd() / ".env", override=False)
    token = os.environ.get("IBM_QUANTUM_API_TOKEN")
    if token:
        return QiskitRuntimeService(
            channel="ibm_quantum_platform",
            token=token,
            instance=os.environ.get("INSTANCE_NAME"),
        )
    return QiskitRuntimeService()


def prepare(circuit, input_qubits: list[int], backend, *, seed: int = 7):
    """Transpile against a supplied backend without submitting any job."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    manager = generate_preset_pass_manager(
        backend=backend, optimization_level=1, seed_transpiler=seed
    )
    return manager.run(measured_circuit(circuit, input_qubits))


def submit(
    circuit,
    input_qubits: list[int],
    *,
    backend_name: str,
    shots: int,
    service=None,
    seed: int = 7,
) -> dict:
    """Submit one explicitly configured job and immediately return its identifier."""
    if not backend_name or type(shots) is not int or shots < 1:
        raise ValueError("An explicit backend and positive shots are required")
    from qiskit_ibm_runtime import SamplerV2

    service = service if service is not None else create_service()
    backend = service.backend(backend_name)
    prepared = prepare(circuit, input_qubits, backend, seed=seed)
    job = SamplerV2(mode=backend).run([prepared], shots=shots)
    return {
        "job_id": job.job_id(),
        "backend": backend_name,
        "shots": shots,
        "seed": seed,
        "input_qubits": list(input_qubits),
        "transpiled_qubits": prepared.num_qubits,
        "transpiled_depth": prepared.depth(),
    }


def retrieve(job_id: str, *, service=None) -> dict:
    """Retrieve the single named input register; does not submit a new job."""
    service = service if service is not None else create_service()
    job = service.job(job_id)
    return {"job_id": job_id, "counts": job.result()[0].data.data.get_counts()}
