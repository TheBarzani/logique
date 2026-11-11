"""Build results_data.json from the private Chia work files (verified ledger rows only).

Inputs live under outputs/ of the private research workspace, so this step only runs there:
  python3 build_results_data.py <workspace-root>
The public script make_results_tables.py reads the committed results_data.json.
Ledger ids (notes/claims.md, private): P6 K3 oracle T, P10 K4/C5 oracle T, P11 search T, P14 search offset D,
T4-2 K3 oracle q/g/d. K5/myciel3 (T4-3) and win/tie/loss (T4-5) are pending and deliberately NOT exported.
"""
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
def load(p): return json.loads((root / p).read_text())
out = {"oracle_T": {}, "search_T": {}, "offset_D": {"K3": 31, "K4": 47, "C5": 63},
       "k3_qgd": {}, "ledger": {"oracle_T": "P6,P10", "search_T": "P11", "offset_D": "P14", "k3_qgd": "T4-2"}}
def r1(rows):
    d = {}
    for x in rows:
        if "_R1_" in x["case"]:
            d[x["method"]] = x
    return d
k3 = r1(load("outputs/task-20/work/k3_ft_n_clean_m15.json"))
out["oracle_T"]["K3"] = {m: [x["t_count"], int(x["t_depth"])] for m, x in k3.items()
                         if x["rotations"] == 0 and m not in ("xag",)}
for g in ("K4", "C5"):
    o = r1(load(f"outputs/task-23/work/{g}_oracle_n_clean_m15.json"))
    s = r1(load(f"outputs/task-23/work/{g}_search_n_clean_m15.json"))
    for m, x in o.items():
        assert x["rotations"] == 0 and x["agree"], (g, m)
    out["oracle_T"][g] = {m: [x["t_count"], int(x["t_depth"])] for m, x in o.items()}
    out["search_T"][g] = {m: x["t_count"] for m, x in s.items()}
t = load("outputs/task-26/work/admitted_table.json")
for k, v in t.items():
    g, m = k.split(":")
    if g == "K3" and v:
        out["k3_qgd"][m] = v[:3]
pathlib.Path(__file__).with_name("results_data.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print({g: len(v) for g, v in out["oracle_T"].items()}, len(out["k3_qgd"]))
