"""Authenticate the separately admitted C5 best-fit source for noisy routing.

This source has ten ideal rows, not observations in the original 805-request
structure ledger. Loading and preparing requests never routes or samples.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from logique.benchmarks import noisy_iterations as noisy
from logique.paths import new_dump_directory

SOURCE_KIND = "c5-best-fit-complete-qpy-v1"
MANIFEST_SHA256 = "fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4"
ORACLE_SHA256 = "8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268"
SEEDS = (11, 23, 37, 41, 53)
CASE = {
    "name": "C5_k3_best_fit_complete",
    "vertices": list(range(5)),
    "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
    "colors": 3,
}


def digest(path: Path) -> str:
    """Hash exact saved bytes before parsing or executing them."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inventory(root: Path) -> dict:
    """Authenticate every frozen evidence entry, rejecting path traversal."""
    root = root.resolve()
    if digest(root / "manifest.json") != MANIFEST_SHA256:
        raise ValueError("C5 best-fit manifest identity mismatch")
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["evidence_hashes"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or digest(path) != expected:
            raise ValueError(f"C5 best-fit evidence identity mismatch: {name}")
    return manifest


def request_identity(regime: str, seed: int, iteration: int) -> str:
    """Name a new request without changing the historical structure ledger."""
    if regime not in ("R1", "R2") or type(seed) is not int or seed not in SEEDS:
        raise ValueError("Unsupported C5 best-fit regime/seed")
    limit = 5 if regime == "R1" else 3
    if type(iteration) is not int or not 0 <= iteration <= limit:
        raise ValueError("Outside admitted C5 first-peak-plus-one scope")
    return f"{SOURCE_KIND}:{MANIFEST_SHA256}:{regime}:seed{seed}:j{iteration}"


def validate_layout(
    physical: list[int], final: list[int], measured: dict, width: int, data: int
) -> None:
    """Reject inconsistent physical calibration/data maps before any Aer call."""
    if (
        physical != sorted(set(physical))
        or any(type(q) is not int or q < 0 for q in physical)
        or len(physical) > 18
        or len(final) != width
        or len(set(final)) != width
        or any(type(q) is not int or q < 0 for q in final)
        or sorted(measured) != list(range(data))
        or any(final[i] not in physical for i in range(data))
        or any(measured[i] != physical.index(final[i]) for i in range(data))
    ):
        raise ValueError("C5 physical calibration/measurement layout mismatch")


def _json_identity(value) -> str:
    """Normalize JSON containers while retaining scalar types and array order."""
    return json.dumps(value, sort_keys=True, allow_nan=False)


def _unique_object(pairs: list[tuple]) -> dict:
    """Reject repeated JSON object keys before they can hide changed payloads."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate C5 noise JSON object key")
        result[key] = value
    return result


def calibration_records(snapshot: dict) -> dict[tuple, str]:
    """Index independent local records, preserving each channel's exact payload.

    Only the installed FakeTorino operation/type/ordered-physical-qargs schema
    is supported. A record contains one operation at one ordered physical
    location. UUIDs are ephemeral; no other field or internal array is removed,
    sorted, flattened, rounded or decoded. Duplicate identities fail closed.
    """
    normalized = json.loads(_json_identity(snapshot))
    if (
        not isinstance(normalized, dict)
        or set(normalized) != {"errors"}
        or not isinstance(normalized["errors"], list)
    ):
        raise ValueError("Unsupported C5 noise snapshot keys")
    records = {}
    for error in normalized["errors"]:
        if not isinstance(error, dict):
            raise ValueError("Unsupported C5 noise record")
        kind = error.get("type")
        fields = {"type", "operations", "gate_qubits", "probabilities"}
        if kind == "qerror":
            fields.add("instructions")
        elif kind != "roerror":
            raise ValueError("Unsupported C5 noise record type")
        if set(error) - {"id"} != fields:
            raise ValueError("Unsupported C5 noise record keys")
        operations, locations = error["operations"], error["gate_qubits"]
        allowed = {"id", "reset", "sx", "x", "cz"} if kind == "qerror" else {"measure"}
        if (
            not isinstance(operations, list)
            or len(operations) != 1
            or not isinstance(operations[0], str)
            or operations[0] not in allowed
            or not isinstance(locations, list)
            or len(locations) != 1
            or not isinstance(locations[0], list)
        ):
            raise ValueError("Unsupported C5 noise operation/physical key")
        qargs = locations[0]
        arity = 2 if operations[0] == "cz" else 1
        if (
            len(qargs) != arity
            or any(type(q) is not int or q < 0 for q in qargs)
            or len(set(qargs)) != len(qargs)
        ):
            raise ValueError("Unsupported C5 ordered physical qargs")
        identity = (kind, operations[0], tuple(qargs))
        if identity in records:
            raise ValueError("Duplicate C5 noise record identity")
        error.pop("id", None)
        records[identity] = _json_identity(error)
    return records


def validate_calibration(backend, directory: Path, snapshot: dict) -> dict:
    """Bind reused gate/readout noise to this actual FakeTorino calibration.

    Compare the complete serialized local-channel model, including ordered
    physical qargs, before compaction. An unrelated preexisting backend folder
    must never silently supply the calibration for a new best-fit request.
    """
    from qiskit_aer.noise import NoiseModel

    hashes = {}
    for kind, filename in (
        ("properties", backend.props_filename),
        ("configuration", backend.conf_filename),
    ):
        saved = directory / f"{kind}.json"
        if saved.read_bytes() != (Path(backend.dirname) / filename).read_bytes():
            raise ValueError("C5 backend calibration identity mismatch")
        hashes[kind] = digest(saved)
    raw = (directory / "noise.json").read_bytes()
    saved = json.loads(raw, object_pairs_hook=_unique_object)
    if _json_identity(snapshot) != _json_identity(saved):
        raise ValueError("C5 noise snapshot/file identity mismatch")
    expected = NoiseModel.from_backend(backend).to_dict(serializable=True)
    if calibration_records(saved) != calibration_records(expected):
        raise ValueError("C5 physical noise channels differ from backend calibration")
    hashes["noise"] = hashlib.sha256(raw).hexdigest()
    return hashes


def load_source(config: dict, regime: str) -> dict:
    """Load exact restoring U/CX components and normalize ideal row metadata.

    No synthesis, optimization or domain-check removal is performed. Width is
    guarded before QPY loading, and only local one/two-wire gates are accepted.
    The original emitted A inverse is retained alongside A and reflection.
    """
    noisy.validate_config(config, pilot_hash=MANIFEST_SHA256)
    if regime not in ("R1", "R2") or config["execute"] != ["R1", "R2"]:
        raise ValueError("Only complete-predicate C5 R1/R2 source is supported")
    root = Path(config["ideal_pilot"])
    verify_inventory(root)
    source = json.loads((root / regime / "result.json").read_text())
    if source["width"] != 11 or source["data_qubits"] != list(range(10)):
        raise ValueError("Unexpected admitted C5 wire map")
    noisy.allocation_guard(11, config)
    from qiskit import qpy

    components = {}
    for name in ("preparation", "preparation_inverse", "oracle", "diffusion"):
        path = root / regime / f"{name}.qpy"
        metadata = source["artifacts"][name]
        if digest(path) != metadata["sha256"]:
            raise ValueError("C5 component identity mismatch")
        with path.open("rb") as stream:
            loaded = qpy.load(stream)
        if len(loaded) != 1:
            raise ValueError("Expected one admitted component")
        circuit = loaded[0]
        expected_width = 11 if name == "oracle" else 10
        if circuit.num_qubits != expected_width or circuit.num_clbits:
            raise ValueError("Unexpected C5 component allocation")
        if len(circuit.data) != metadata["instructions"]:
            raise ValueError("C5 instruction accounting changed")
        if circuit.parameters or any(
            item.operation.name not in ("u", "cx") or item.operation.num_qubits > 2
            for item in circuit.data
        ):
            raise ValueError("Only admitted flat U/CX components are supported")
        components[name] = circuit
    if source["artifacts"]["oracle"]["sha256"] != ORACLE_SHA256:
        raise ValueError("Unexpected C5 oracle identity")
    if len(components["oracle"].data) != 84441:
        raise ValueError("Expected the full 84,441-instruction oracle")
    support, peak = (1024, 4) if regime == "R1" else (243, 2)
    rows = []
    if [row["iterations"] for row in source["rows"]] != list(range(peak + 2)):
        raise ValueError("Incomplete C5 ideal first-peak-plus-one evidence")
    for row in source["rows"]:
        prediction = (
            math.sin((2 * row["iterations"] + 1) * math.asin(math.sqrt(30 / support)))
            ** 2
        )
        if not row["passed"] or abs(row["success"] - prediction) > 1e-10:
            raise ValueError("C5 ideal row fails analytical reconciliation")
        rows.append(
            {
                **row,
                "analytical_ledger_prediction": prediction,
                "simulated_valid_solution_probability": row["success"],
            }
        )
    reference = {
        **source,
        "case": CASE,
        "construction": {"width": 11},
        "counts": {**source["counts"], "data_bits": 10},
        "rows": rows,
    }
    return {
        "reference": reference,
        "parts": [components[n] for n in ("preparation", "oracle", "diffusion")],
        "preparation_inverse": components["preparation_inverse"],
        "policies": [{"source": SOURCE_KIND, "re_lowered": False}],
        "identity": {
            "source_kind": SOURCE_KIND,
            "source_manifest_sha256": MANIFEST_SHA256,
            "oracle_sha256": ORACLE_SHA256,
            "oracle_instructions": 84441,
            "historical_805_ledger_membership": False,
        },
    }


def prepare(config: dict, *, root: Path = Path("dump")) -> Path:
    """Write fifty distinct, unlaunched requests for later admitted execution."""
    sources = {regime: load_source(config, regime) for regime in ("R1", "R2")}
    output = new_dump_directory("c5-best-fit-noise-requests", root=root)
    ledger = []
    for regime, source in sources.items():
        for seed in SEEDS:
            for row in source["reference"]["rows"]:
                j = row["iterations"]
                identity = request_identity(regime, seed, j)
                request = {
                    "source_kind": SOURCE_KIND,
                    "request_identity": identity,
                    "config": config,
                    "name": regime,
                    "seed": seed,
                    "iterations": [j],
                    "output": str(output / f"{regime}_seed{seed}_j{j}"),
                }
                filename = f"{regime}_seed{seed}_j{j}-request.json"
                noisy._write(output / filename, request)
                ledger.append(
                    {
                        "request_identity": identity,
                        "request": filename,
                        "status": "unlaunched_pending_adapter_source_review",
                        "admitted_ideal_success": row["success"],
                        "counts": None,
                    }
                )
    noisy._write(output / "requested-ledger.json", {"rows": ledger})
    return output
