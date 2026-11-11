"""Chia T8 sweeps (task-34): build oracle circuits (R1, j=1, seed 7) for the protocol section 10 families.

Usage: python chia_scaling_probe2.py <sweep: Sk|SE|SV> <workdir> [name-filter]
Writes <workdir>/<name>.col and <workdir>/probe/<name>/...; then run tools/chia_ft_count.py per probe dir.
"""
import random, sys
from pathlib import Path
from logique.paths import dump_directory_name
from logique.benchmarks.coloring_study import run_coloring_study

METHODS = ["xag", "xag_bennett", "sb_simple", "sb_balanced", "sb_minimal", "structure_sequential"]


def rand_edges(n, m, seed):
    allp = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    m = min(m, len(allp))
    return sorted(random.Random(seed).sample(allp, m))


def instances(sweep):
    if sweep == "Sk":
        for fam in "PC":
            n = 6
            e = [(i, i + 1) for i in range(1, n)] + ([(n, 1)] if fam == "C" else [])
            for k in range(2, 9):
                yield f"{fam}{n}_k{k}", n, e, k
    elif sweep == "SE":
        for s in (101, 102, 103):
            for m in (4, 8, 12, 16, 20, 24):
                yield f"R8m{m}s{s}_k3", 8, rand_edges(8, m, s), 3
    elif sweep == "SV":
        for s in (101, 102, 103):
            for n in range(4, 11):
                yield f"R{n}m{2*n}s{s}_k3", n, rand_edges(n, 2 * n, s), 3
    elif sweep == "SH":  # held-out check of the fitted formulas (predictions written down before the run, task-34)
        for n, m, s in [(12, 30, 104), (11, 15, 105), (9, 35, 106)]:
            yield f"H{n}m{m}s{s}_k3", n, rand_edges(n, m, s), 3
    elif sweep == "ST":  # diagnostic: where does the large-MCX regime start (n=9, m=24..30, seed 107)
        for m in range(18, 24):
            yield f"T9m{m}s107_k3", 9, rand_edges(9, m, 107), 3
    elif sweep == "SH2":  # in-range held-out (n+m <= 32); predictions: struct -9+22n+36m, xag_bennett -21+28(n+m), sb_simple -9+22(n+m)
        for n, m, s in [(12, 18, 104), (7, 25, 106), (10, 22, 105)]:
            yield f"H{n}m{m}s{s}_k3", n, rand_edges(n, m, s), 3


sweep, work = sys.argv[1], Path(sys.argv[2])
filt = sys.argv[3] if len(sys.argv) > 3 else ""
work.mkdir(parents=True, exist_ok=True)
for name, n, edges, k in instances(sweep):
    if filt not in name:
        continue
    bits = (k - 1).bit_length()
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
