"""Chia T6 pilot: Clifford+T cost of saved oracle circuits, with an independent recount.

Usage: python chia_ft_count.py <probe_dir> <out_json> [mcx_method] [component]
Method 1: decompose_mcx('gray_code') -> clifford_t -> ft_metrics (repo FT code).
Method 2 (independent): count gates of the pre-lowering circuit and apply the per-gate
T costs stated in the code docstring (ccx 7, rccx 4, ch 2, ccrx 4) by hand.
Oracle only; controlled rotations other than ccrx(+-pi) stay as rz and are reported separately.
"""

import json
import math
import sys
from pathlib import Path

from qiskit import QuantumCircuit, qpy

from logique.benchmarks.costs import (
    clifford_t,
    decompose_mcx,
    ft_metrics,
    is_mcx,
    _gadget_name,
)

HAND_T = {"cu": 4, "ccx": 7, "rccx": 4, "rccx_dg": 4, "ccrx+": 4, "ccrx-": 4, "ch": 2}


def expand_cu(circuit):
    """Replace cu(+-pi/2,-pi/2,pi/2,0) (= controlled-Rx(+-pi/2)) by H CS H + phase T on the control.

    Exact (checked against the gate unitary in outputs/task-23/work/cu_decomp_check.py): 4 T each.
    """
    out = QuantumCircuit(*circuit.qregs, *circuit.cregs, name=circuit.name)
    out.global_phase = circuit.global_phase
    for inst in circuit.data:
        op = inst.operation
        if op.name != "cu":
            out.append(op, inst.qubits, inst.clbits)
            continue
        th = float(op.params[0])
        assert abs(abs(th) - math.pi / 2) < 1e-9 and abs(float(op.params[1]) + math.pi / 2) < 1e-9
        assert abs(float(op.params[2]) - math.pi / 2) < 1e-9 and abs(float(op.params[3])) < 1e-9
        assert op.ctrl_state == 1
        c, t = inst.qubits
        pos = th > 0
        a, b = (out.t, out.tdg) if pos else (out.tdg, out.t)
        out.h(t)
        a(c); a(t); out.cx(c, t); b(t); out.cx(c, t)
        out.h(t)
        b(c)
    return out


def hand_count(circuit):
    total = 0
    for inst in circuit.data:
        g = "cu" if inst.operation.name == "cu" else _gadget_name(inst.operation)
        if g in HAND_T:
            total += HAND_T[g]
        elif inst.operation.name in ("t", "tdg"):
            total += 1
    return total


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    mcx = sys.argv[3] if len(sys.argv) > 3 else "gray_code"
    component = sys.argv[4] if len(sys.argv) > 4 else "oracle"  # oracle|search|diffusion|preparation
    rows = []
    for f in sorted(root.glob(f"*/*_{component}_logical.qpy")):
        with open(f, "rb") as fh:
            circ = qpy.load(fh)[0]
        method_dir = f.parent.name.split("-", 1)[1]
        tag = f.name.replace(f"_{component}_logical.qpy", "")
        try:
            expanded, info = decompose_mcx(circ, mcx)
            hand = hand_count(expanded)
            ft = ft_metrics(clifford_t(expand_cu(expanded)))
            rows.append(
                {
                    "method": method_dir,
                    "mcx": mcx,
                    "component": component,
                    "case": tag,
                    "t_count": ft["t_count"],
                    "t_depth": ft["t_depth"],
                    "rotations": ft["rotation_count"],
                    "qubits": ft["qubits"],
                    "hand_t_count": hand,
                    "agree": hand == ft["t_count"],
                }
            )
        except Exception as e:  # keep going, record failure
            rows.append({"method": method_dir, "case": tag, "error": repr(e)[:200]})
    out.write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
