"""Build scaling_data.json from private Chia work files (verified ledger rows only).
Run only in the private workspace:  python3 build_scaling_data.py <workspace-root>
Ledger ids: T8-3 fits (task-34 rows.json, 36 random graphs, k=3, n+m<=32), T8-7/8/9 widths and T depths and T
(task-35 rows.json: [T, T-depth, qubits] per method; k=3, R1, j=1, n_clean_m15), T5-1..3 (task-37 table.md).
Counts with n+m>=33 (T8-6, rotation-ladder artifact) are never read here.
"""
import json, sys, pathlib, re
import numpy as np
root = pathlib.Path(sys.argv[1])
rows = json.loads((root / "outputs/task-34/work/rows.json").read_text())
rand = [r for r in rows if r["name"].startswith("R")]
assert len(rand) == 216 and all(r["n"] + r["m"] <= 32 for r in rand)
out = {"fits": {}, "pc": {}, "profiles": {}}
methods = sorted({r["method"] for r in rand})
for m in methods:
    pts = sorted({(r["n"], r["m"], r["T"]) for r in rand if r["method"] == m})
    assert len(pts) == 12 or len(pts) > 6
    A = np.array([[1, n, e] for n, e, _ in pts], float); y = np.array([t for *_, t in pts], float)
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    ss = ((y - A @ c) ** 2).sum(); r2 = 1 - ss / ((y - y.mean()) ** 2).sum()
    out["fits"][m] = {"a": round(c[0], 2), "b": round(c[1], 2), "c": round(c[2], 2), "R2": round(float(r2), 4), "npts": len(pts)}
# graph independence: same (n,m), different seeds -> identical T
for m in methods:
    by = {}
    for r in rand:
        if r["method"] == m: by.setdefault((r["n"], r["m"]), set()).add(r["T"])
    assert all(len(v) == 1 for v in by.values()), m
d = json.loads((root / "outputs/task-35/work/rows.json").read_text())
for g in ("P3", "P6", "P9", "P12", "C6", "C12", "K4", "K6"):
    out["pc"][g] = d[g]
tm = (root / "outputs/task-37/work/table.md").read_text()
cur = None
for line in tm.splitlines():
    h = re.match(r"\*\*(\w+)\*\*", line)
    if h: cur = h.group(1); out["profiles"][cur] = {}; continue
    if cur and line.startswith("| ") and not line.startswith("| method") and "---" not in line:
        cells = [c.strip() for c in line.strip("|").split("|")]
        out["profiles"][cur][cells[0]] = [[int(x) for x in c.split("/")] for c in cells[1:]]
pathlib.Path(__file__).with_name("scaling_data.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(out["fits"])
