"""Chia T6 pilot: Clifford+T cost of saved oracle circuits, with an independent recount.

Usage: python chia_ft_count.py <probe_dir> <out_json>
Method 1: decompose_mcx('gray_code') -> clifford_t -> ft_metrics (repo FT code).
Method 2 (independent): count gates of the pre-lowering circuit and apply the per-gate
T costs stated in the code docstring (ccx 7, rccx 4, ch 2, ccrx 4) by hand.
Oracle only; controlled rotations other than ccrx(+-pi) stay as rz and are reported separately.
"""

import json
import sys
from pathlib import Path

from qiskit import qpy

from logique.benchmarks.costs import (
    clifford_t,
    decompose_mcx,
    ft_metrics,
    is_mcx,
    _gadget_name,
)

HAND_T = {"ccx": 7, "rccx": 4, "rccx_dg": 4, "ccrx+": 4, "ccrx-": 4, "ch": 2}


def hand_count(circuit):
    total = 0
    for inst in circuit.data:
        g = _gadget_name(inst.operation)
        if g in HAND_T:
            total += HAND_T[g]
        elif inst.operation.name in ("t", "tdg"):
            total += 1
    return total


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    mcx = sys.argv[3] if len(sys.argv) > 3 else "gray_code"
    rows = []
    for f in sorted(root.glob("*/*_oracle_logical.qpy")):
        with open(f, "rb") as fh:
            circ = qpy.load(fh)[0]
        method_dir = f.parent.name.split("-", 1)[1]
        tag = f.name.replace("_oracle_logical.qpy", "")
        try:
            expanded, info = decompose_mcx(circ, mcx)
            hand = hand_count(expanded)
            ft = ft_metrics(clifford_t(expanded))
            rows.append(
                {
                    "method": method_dir,
                    "mcx": mcx,
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
