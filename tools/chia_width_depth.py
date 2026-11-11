"""Chia T8 (task-35): logical width and independent T-depth of saved oracle circuits.

Usage: python chia_width_depth.py <probe_dir> <out_json> [mcx_method]
Per circuit: logical qubits and register sizes (before MCX expansion), qubits after expansion,
T-count and T-depth from the repo (ft_metrics), and T-depth recomputed by a hand-written
ASAP scheduler (a T/Tdg layer is counted when it is the next T on every qubit it touches;
non-T gates only propagate the layer index) -- independent of repo weighted_depth.
"""
import json, sys
from pathlib import Path
from qiskit import qpy
from logique.benchmarks.costs import clifford_t, decompose_mcx, ft_metrics
sys.path.insert(0, str(Path(__file__).parent))
from chia_ft_count import expand_cu


def own_t_depth(circ):
    lvl = {q: 0 for q in circ.qubits}  # T layers completed on each qubit's timeline
    for inst in circ.data:
        qs = inst.qubits
        if not qs:
            continue
        base = max(lvl[q] for q in qs)
        new = base + 1 if inst.operation.name in ("t", "tdg") else base
        for q in qs:
            lvl[q] = new
    return max(lvl.values())


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    mcx = sys.argv[3] if len(sys.argv) > 3 else "n_clean_m15"
    rows = []
    for f in sorted(root.glob("*/*_oracle_logical.qpy")):
        circ = qpy.load(open(f, "rb"))[0]
        exp, _ = decompose_mcx(circ, mcx)
        ct = clifford_t(expand_cu(exp))
        ft = ft_metrics(ct)
        rows.append({
            "method": f.parent.name.split("-", 1)[1],
            "logical_qubits": circ.num_qubits,
            "registers": {r.name: r.size for r in circ.qregs},
            "qubits_after_expansion": ct.num_qubits,
            "t_count": ft["t_count"], "t_depth_repo": ft["t_depth"], "t_depth_own": own_t_depth(ct),
        })
    out.write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
