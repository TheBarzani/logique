"""Conversions preserving gate polarity, bit order, and rotation phase."""

from functools import lru_cache
from qiskit import QuantumCircuit
from qiskit.circuit.library import RXGate, XGate


def _tweedledum_records(circuit):
    from tweedledum.ir import Qubit, rotation_angle

    records = []
    for inst in circuit:
        qs = list(inst.qubits())
        controls = [q.uid() for q in qs[:-1]]
        polarity = [q.polarity() == Qubit.Polarity.positive for q in qs[:-1]]
        kind = inst.kind()
        if kind == "ext.parity":
            for c, positive in zip(controls, polarity):
                records.append(
                    {
                        "kind": "x",
                        "controls": [c],
                        "polarity": [positive],
                        "target": qs[-1].uid(),
                    }
                )
        elif kind in ("std.x", "std.rx"):
            record = {
                "kind": "rx" if kind == "std.rx" else "x",
                "controls": controls,
                "polarity": polarity,
                "target": qs[-1].uid(),
            }
            if kind == "std.rx":
                record["angle"] = rotation_angle(inst)
            records.append(record)
        else:
            raise ValueError(f"Unsupported tweedledum operator: {kind}")
    return records


def _qiskit_records(circuit):
    from qiskit.circuit import ControlledGate

    records = []
    for item in circuit.data:
        op = item.operation
        qs = [circuit.find_bit(q).index for q in item.qubits]
        count = op.num_ctrl_qubits if isinstance(op, ControlledGate) else 0
        base = op.base_gate if count else op
        if base.name not in ("x", "rx"):
            raise ValueError(f"Cannot track phases for {op.name}")
        rec = {
            "kind": base.name,
            "controls": qs[:count],
            "target": qs[-1],
            "polarity": [bool((op.ctrl_state >> i) & 1) for i in range(count)],
        }
        if base.name == "rx":
            rec["angle"] = float(base.params[0])
        records.append(rec)
    return records


@lru_cache(maxsize=512)
def _lut_circuit(truth):
    from tweedledum.classical import TruthTable, create_from_binary_string
    from tweedledum.synthesis import pprm_synth

    n = (len(truth) - 1).bit_length()
    if len(truth) != 1 << n:
        raise ValueError("LUT truth table length must be a power of two")
    tt = TruthTable(n)
    create_from_binary_string(tt, truth)
    native = pprm_synth(tt)
    return records_to_qiskit(_tweedledum_records(native), n + 1)


def records_to_qiskit(records, width, *, expand_luts=True):
    """Preserve controlled rotations, control polarities, and LUT semantics."""
    qc = QuantumCircuit(width)
    for rec in records:
        cs, target = rec["controls"], rec["target"]
        polarity = rec["polarity"]
        if len(cs) != len(polarity) or target in cs or len(cs) != len(set(cs)):
            raise ValueError("Invalid gate wiring")
        if rec["kind"] == "lut":
            block = _lut_circuit(rec["truth"])
            for q, positive in zip(cs, polarity):
                if not positive:
                    qc.x(q)
            if expand_luts:
                qc.compose(block, qubits=[*cs, target], inplace=True)
            else:
                qc.append(block.to_gate(label=f"LUT{len(cs)}"), [*cs, target])
            for q, positive in zip(cs, polarity):
                if not positive:
                    qc.x(q)
        else:
            if rec["kind"] not in ("rx", "x"):
                raise ValueError(f"Unsupported gate {rec['kind']}")
            gate = RXGate(rec["angle"]) if rec["kind"] == "rx" else XGate()
            if cs:
                state = sum(int(p) << i for i, p in enumerate(polarity))
                gate = gate.control(len(cs), ctrl_state=state)
            qc.append(gate, [*cs, target])
    return qc
