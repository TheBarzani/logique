"""Independent check of executed ideal success-vs-iteration runs (Chia, task-13).

Own brute-force count of proper colourings M, closed-form P_j = sin^2((2j+1)theta),
theta = asin(sqrt(p)); compares every simulated row and the C2 iteration rule.
Petersen (infeasible to simulate) gets analytical rows only, labelled as such.
Usage: uv run --no-sync python tools/chia_success_check.py OUT.json RUN_DIR [RUN_DIR ...]
"""

import itertools
import json
import math
import sys
from pathlib import Path


def proper(vertices, edges, k):
    """Count proper k-colourings by brute force (own code, no logique import)."""
    pos = {v: i for i, v in enumerate(vertices)}
    return sum(
        all(a[pos[u]] != a[pos[v]] for u, v in edges)
        for a in itertools.product(range(k), repeat=len(vertices))
    )


def p_of(regime, m, n_bits, k, nv):
    # R1: Hadamard over all 2^n words; R2/R3: uniform over the k^|V| valid-code words.
    return m / (2**n_bits) if regime == "R1" else m / (k**nv)


def success(j, theta):
    return math.sin((2 * j + 1) * theta) ** 2


def rule(theta):
    x = math.pi / (4 * theta) - 0.5
    lo, hi = max(0, math.floor(x)), max(0, math.ceil(x))
    return lo if success(lo, theta) >= success(hi, theta) else hi


def first_max_in(rows_p):
    """First local maximum in a simulated list [(j, P)], or last row if none yet."""
    for i in range(1, len(rows_p) - 1):
        if rows_p[i][1] >= rows_p[i - 1][1] and rows_p[i][1] > rows_p[i + 1][1] + 1e-12:
            return rows_p[i][0]
    return None


def main() -> int:
    out_path, *runs = sys.argv[1:]
    report = {"cases": [], "petersen_analytical": []}
    for run in runs:
        for result in sorted(Path(run).glob("*/result.json")):
            r = json.loads(result.read_text())
            case, regime = r["case"], r["regime"]
            k, V = case["colors"], len(case["vertices"])
            c = max(1, (k - 1).bit_length())
            m = proper(case["vertices"], [tuple(e) for e in case["edges"]], k)
            p = p_of(regime, m, c * V, k, V)
            theta = math.asin(math.sqrt(p))
            rows = [(x["iterations"], x["simulated_valid_solution_probability"]) for x in r["rows"]]
            maxdiff = max(abs(pj - success(j, theta)) for j, pj in rows)
            fm = first_max_in(rows)
            rj = rule(theta)
            report["cases"].append(
                {
                    "case": case["name"], "regime": regime, "status": r["status"],
                    "M_own": m, "M_library": r["counts"]["marked"],
                    "support_library": r["counts"]["support"], "p": p,
                    "iterations_simulated": [j for j, _ in rows],
                    "max_abs_diff_vs_closed_form": maxdiff,
                    "rule_iterations_C2": rj,
                    "first_simulated_max": fm,
                    "P_at_rule": success(rj, theta),
                    "rule_equals_first_simulated_max": fm == rj if fm is not None else None,
                    "library_first_peak": r["analytical_ledger"]["first_peak_iteration"],
                    "max_leakage_valid_regimes": max(x["simulated_unused_code_leakage"] for x in r["rows"]),
                    "workspace_restored_min": min(x["simulated_restored_workspace_probability"] for x in r["rows"]),
                }
            )
    pet_edges = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + [
        (5 + i, 5 + (i + 2) % 5) for i in range(5)
    ]
    m = proper(list(range(10)), pet_edges, 3)
    for regime in ("R1", "R2", "R3"):
        p = p_of(regime, m, 20, 3, 10)
        theta = math.asin(math.sqrt(p))
        j = rule(theta)
        report["petersen_analytical"].append(
            {"regime": regime, "M": m, "p": p, "rule_iterations": j,
             "P_at_rule": success(j, theta),
             "kind": "analytical, NOT simulated: oracle width 47 (complete) / 37 (domain_free) > 22"}
        )
    Path(out_path).write_text(json.dumps(report, indent=1))
    for row in report["cases"]:
        print({k: row[k] for k in ("case", "regime", "status", "M_own", "M_library", "max_abs_diff_vs_closed_form",
                                    "rule_iterations_C2", "first_simulated_max", "rule_equals_first_simulated_max")})
    print(report["petersen_analytical"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
