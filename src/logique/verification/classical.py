"""Independent truth evaluation and coherent monomial verification."""

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


def validate(result, *, sampled=False, samples=256, seed=7):
    """Check function values and the wrapped oracle, including coherent phases.

    Exact X/MCX/LUT/Rx(+/-pi) records are monomial: tracking their permutation
    and phase on every input also proves the action on input superpositions.
    Larger examples may explicitly request seeded sampling, which is not proof.
    """
    md = result.metadata
    n = len(md["input_qubits"])
    assignments = (
        np.random.default_rng(seed).integers(0, 2, (n, samples)).astype(bool)
        if sampled
        else input_assignments(n)
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
