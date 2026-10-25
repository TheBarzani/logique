"""Independent truth evaluation and coherent monomial verification."""

from collections.abc import Iterable
import operator

import numpy as np
from logique.circuits.records import _qiskit_records


def truth_outputs(graph, assignments):
    """Evaluate the exported logic network independently of its quantum mapping."""
    values = {node: assignments[i] for i, node in enumerate(graph["inputs"])}
    size = assignments.shape[1]
    for node in graph["nodes"]:
        if node["kind"] == "constant":
            values[node["id"]] = np.full(size, node["value"], dtype=bool)
        elif node["kind"] != "input":
            index = np.zeros(size, dtype=np.int64)
            for i, f in enumerate(node["fanins"]):
                index |= (values[f["node"]] ^ f["inverted"]).astype(np.int64) << i
            table = np.array([b == "1" for b in reversed(node["truth"])])
            values[node["id"]] = table[index]
    return np.array([values[o["node"]] ^ o["inverted"] for o in graph["outputs"]])


def input_assignments(n):
    if n > 12:
        raise ValueError(
            "Exhaustive analysis is limited to 12 inputs; use output cones or sampled validation"
        )
    return ((np.arange(1 << n)[None, :] >> np.arange(n)[:, None]) & 1).astype(bool)


def verification_assignments(
    n: int,
    *,
    sampled: bool = False,
    samples: int = 256,
    seed: int = 7,
    assignments: Iterable[int] | None = None,
) -> tuple[np.ndarray, dict]:
    """Augment deterministic coverage with explicit input-register integers.

    Bit i of each integer is input i, independent of the physical wire layout.
    Explicit inputs supplement sampling; they never turn sampled coverage into
    an exhaustive proof. Duplicate witnesses are checked once and recorded once.
    """
    if type(samples) is not int or samples < 1:
        raise ValueError("samples must be a positive integer")
    explicit = []
    for value in () if assignments is None else assignments:
        try:
            basis = operator.index(value)
        except TypeError as error:
            raise ValueError("verification assignments must be integers") from error
        if isinstance(value, (bool, np.bool_)) or not 0 <= basis < 1 << n:
            raise ValueError("verification assignment is outside the input register")
        if basis not in explicit:
            explicit.append(basis)
    selected = (
        np.random.default_rng(seed).integers(0, 2, (n, samples)).astype(bool)
        if sampled
        else input_assignments(n)
    )
    columns = {
        sum(int(bit) << i for i, bit in enumerate(bits)): j
        for j, bits in enumerate(selected.T)
    }
    added = [value for value in explicit if value not in columns]
    if added:
        extra = np.array(
            [[(value >> i) & 1 for value in added] for i in range(n)], dtype=bool
        ).reshape(n, len(added))
        selected = np.concatenate((selected, extra), axis=1)
    return selected, {
        "explicit_assignments": explicit,
        "explicit_assignments_added": len(added),
    }


def _apply_record(bits, phases, rec, *, inverse=False):
    cs = rec["controls"]
    values = [bits[q] ^ (not p) for q, p in zip(cs, rec["polarity"])]
    if rec["kind"] == "lut":
        index = sum(
            (v.astype(np.int64) << i for i, v in enumerate(values)),
            start=np.zeros(bits.shape[1], dtype=np.int64),
        )
        mask = np.array([b == "1" for b in reversed(rec["truth"])])[index]
    else:
        mask = (
            np.logical_and.reduce(values)
            if values
            else np.ones(bits.shape[1], dtype=bool)
        )
        if rec["kind"] == "z":
            phases[mask & bits[rec["target"]]] *= -1
            return
        if rec["kind"] not in ("x", "rx"):
            raise ValueError(f"Cannot track gate kind {rec['kind']}")
        if rec["kind"] == "rx":
            angle = rec["angle"] * (-1 if inverse else 1)
            if not np.isclose(abs(angle), np.pi):
                raise ValueError("Classical phase tracking only supports Rx(+/-pi)")
            phases[mask] *= -1j if angle > 0 else 1j
    bits[rec["target"]] ^= mask


def validate(result, *, sampled=False, samples=256, seed=7, assignments=None):
    """Check function values and the wrapped oracle, including coherent phases.

    Exact X/MCX/LUT/Rx(+/-pi) records are monomial: tracking their permutation
    and phase on every input also proves the action on input superpositions.
    Larger examples may explicitly request seeded sampling, which is not proof.
    Integer assignments supplement that coverage with known witnesses.
    """
    md = result.metadata
    n = len(md["input_qubits"])
    assignments, coverage = verification_assignments(
        n, sampled=sampled, samples=samples, seed=seed, assignments=assignments
    )
    expected = truth_outputs(md["source_network"], assignments)
    if not np.array_equal(expected, truth_outputs(md["network"], assignments)):
        raise AssertionError("Network transformation changed the Boolean function")
    bits = np.zeros((md["num_qubits"], assignments.shape[1]), dtype=bool)
    bits[md["input_qubits"]] = assignments
    initial = bits.copy()
    phases = np.ones(assignments.shape[1], dtype=complex)
    for rec in md["gates"]:
        _apply_record(bits, phases, rec)
    if not np.array_equal(bits[md["output_qubits"]], expected):
        raise AssertionError("Raw computation produces incorrect outputs")
    others = sorted(
        set(range(bits.shape[0])) - set(md["input_qubits"]) - set(md["output_qubits"])
    )
    raw_clean = not bits[others].any()
    raw_inputs = np.array_equal(bits[md["input_qubits"]], assignments)
    raw_phase = np.allclose(phases, 1)
    exported = initial.copy()
    exported_phases = np.ones(assignments.shape[1], dtype=complex)
    for rec in _qiskit_records(result.circuit):
        _apply_record(exported, exported_phases, rec)
    if not np.array_equal(exported, bits) or not np.allclose(exported_phases, phases):
        raise AssertionError("Qiskit export changed gate semantics or phases")
    # Copying into a separate target is XOR for either initial target value.
    for target_value in (False, True):
        copied = bits[md["output_qubits"]] ^ target_value
        assert np.array_equal(copied, expected ^ target_value)
    for rec in reversed(md["gates"]):
        _apply_record(bits, phases, rec, inverse=True)
    if not np.array_equal(bits, initial) or not np.allclose(phases, 1):
        raise AssertionError("Wrapped oracle does not restore workspace and phase")
    report = {
        **coverage,
        "status": "sampled" if sampled else "exhaustive",
        "assignments": assignments.shape[1],
        "seed": seed if sampled else None,
        "raw_workspace_zero": raw_clean,
        "raw_inputs_restored": raw_inputs,
        "raw_phase_exact": bool(raw_phase),
        "wrapped_restoration": True,
    }
    md["validation"] = report
    return report
