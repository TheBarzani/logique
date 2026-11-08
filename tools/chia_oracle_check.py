"""Independent functional check of saved oracle circuits (Chia, task-15).

For every case JSON in the given run dirs: load the saved oracle .qpy, apply it to |x>|0..0> for every
input word x (data qubits from metadata), and require the output to be (-1)^f(x)|x>|0..0> where f is an own
brute-force proper-colouring predicate on the coloured graph (no logique predicate used). Circuits wider than
MAXQ qubits are skipped and labelled.
Usage: uv run --no-sync python tools/chia_oracle_check.py OUT.json MAXQ RUN_DIR [RUN_DIR ...]
"""
import json, sys
from pathlib import Path
import numpy as np
from qiskit import qpy
from qiskit.quantum_info import Statevector


def predicate(case, x):
    k, verts, edges = case["colors"], case["vertices"], case["edges"]
    bpc = max(1, (k - 1).bit_length())
    col = {}
    for v in verts:
        lo = case["input_mapping"][str(v)]
        word = sum(((x >> q) & 1) << i for i, q in enumerate(lo))
        col[v] = word
    # R1/R2: complete predicate (codes >= k invalid); R3: edge-only (no domain check)
    if case["regime"] != "R3" and any(c >= k for c in col.values()):
        return 0
    return int(all(col[a] != col[b] for a, b in edges))


def main():
    out, maxq, *runs = sys.argv[1:]
    maxq = int(maxq)
    res = []
    for run in runs:
        for f in sorted(Path(run).glob("0*_j1_s7.json")):
            r = json.loads(f.read_text())
            if r["status"] != "complete":
                res.append({"case": r["name"], "method": r["method"], "regime": r["regime"], "result": "excluded"})
                continue
            name = r["artifacts"]["oracle_logical"]
            with open(f.parent / name, "rb") as fh:
                qc = qpy.load(fh)[0]
            row = {"case": r["name"], "method": r["method"], "regime": r["regime"], "qubits": qc.num_qubits}
            if qc.num_qubits > maxq:
                row["result"] = "skipped_too_wide"; res.append(row); continue
            data = r["data_qubits"]; nd = len(data)
            bad = 0; marked = 0
            for x in range(2 ** nd):
                idx = sum(((x >> i) & 1) << q for i, q in enumerate(data))
                sv = Statevector.from_int(idx, 2 ** qc.num_qubits).evolve(qc)
                amp = sv.data[idx]
                f_x = predicate(r, x); marked += f_x
                want = -1 if f_x else 1
                if abs(amp - want) > 1e-9:
                    bad += 1
            row.update(result="ok" if bad == 0 else "FAIL", inputs=2 ** nd, mismatches=bad, marked=marked)
            res.append(row)
            print(row, flush=True)
    Path(out).write_text(json.dumps(res, indent=1))
    print("fail" if any(x.get("result") == "FAIL" for x in res) else "no failures")

main()
