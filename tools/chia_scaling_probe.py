"""Chia T8 pilot (task-33): build oracle circuits (R1, j=1, seed 7) for path/cycle/complete families.

Usage: python chia_scaling_probe.py <family> <k> <n_min> <n_max> <workdir>
Writes <workdir>/<fam><n>.col and probe dirs; validation exhaustive when data bits <= 12, else sampled (labelled).
Then run tools/chia_ft_count.py on each probe dir.
"""
import json, sys
from pathlib import Path
from logique.paths import dump_directory_name
from logique.benchmarks.coloring_study import run_coloring_study

METHODS = ["xag", "xag_bennett", "sb_simple", "sb_balanced", "sb_minimal", "structure_sequential"]
fam, k, lo, hi, work = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5])
work.mkdir(parents=True, exist_ok=True)
bits = (k - 1).bit_length()
for n in range(lo, hi + 1):
    if fam == "P": edges = [(i, i + 1) for i in range(1, n)]
    elif fam == "C": edges = [(i, i % n + 1) for i in range(1, n + 1)]
    else: edges = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    name = f"{fam}{n}_k{k}"
    col = work / f"{name}.col"
    col.write_text(f"c {name}, {k} colors\np edge {n} {len(edges)}\n" + "".join(f"e {a} {b}\n" for a, b in edges))
    val = "exhaustive" if n * bits <= 12 else "sampled"
    for m in METHODS:
        try:
            run_coloring_study({"kind": "coloring_study", "inputs": [str(col)], "methods": [m], "regimes": ["R1"],
                "iterations": [1], "seeds": [7], "colors": k, "validation": val, "remove_precolors": False,
                "output": str(work / "probe" / name / dump_directory_name(m.replace("_", "-")))})
            print(name, m, "ok", val, flush=True)
        except Exception as e:
            print(name, m, "FAIL", f"{type(e).__name__}: {str(e)[:200]}", flush=True)
