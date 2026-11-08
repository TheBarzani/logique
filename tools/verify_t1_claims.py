"""Independent recomputation of manuscript claims C2-C6 (Chia, task-11).

Deliberately does not import logique.benchmarks: only the DIMACS loader and the
edge-only expression builder are used as inputs; every count is recomputed here.
Run: uv run --no-sync python tools/verify_t1_claims.py [OUT.json]
"""

import itertools
import json
import math
import sys
from pathlib import Path

from logique.coloring import read_dimacs
from logique.coloring.encoding import edge_coloring_expression

BENCH = Path("datasets/graphs/benchmarks")
GRAPHS = {"K3": "K3", "K5": "K5", "myciel3": "myciel3", "grid6": "grid6"}


def load(name):
    path = next(BENCH.glob(f"{name}.col"))
    p = read_dimacs(path)
    # precolors stripped (protocol decision 9)
    from logique.coloring import ColoringProblem

    return ColoringProblem(p.vertices, p.edges, p.colors)


def ceil_log2(k):
    return max(1, math.ceil(math.log2(k))) if k > 1 else 1


def count_ops(expr):
    return expr.count("&"), expr.count("|"), expr.count("^")


def proper_colorings(p):
    verts = p.vertices
    m = 0
    for a in itertools.product(range(p.colors), repeat=len(verts)):
        d = dict(zip(verts, a))
        if all(d[u] != d[v] for u, v in p.edges):
            m += 1
    return m


def success(j, theta):
    return math.sin((2 * j + 1) * theta) ** 2


def rule_iterations(theta):
    x = math.pi / (4 * theta) - 0.5
    lo, hi = max(0, math.floor(x)), max(0, math.ceil(x))
    # better of floor/ceil, ties to fewer iterations
    return lo if success(lo, theta) >= success(hi, theta) else hi


def first_peak(theta, limit=10000):
    best, bj = -1.0, 0
    for j in range(limit):
        s = success(j, theta)
        if s > best + 1e-12:
            best, bj = s, j
        elif s < best - 1e-12:
            return bj
    return bj


def main():
    out = {}
    for name in GRAPHS:
        p = load(name)
        V, E, k = len(p.vertices), len(p.edges), p.colors
        c = ceil_log2(k)
        row = {"V": V, "E": E, "k": k, "c": c, "n_data_qubits": c * V}
        # C5: c = max(1, ceil(log2 k)); n = c|V|
        row["C5_c_matches_bit_length"] = c == max(1, (k - 1).bit_length())
        # C3/C4: ANDs in the edge-only expression.
        expr, variables = edge_coloring_expression(p)
        ands, ors, xors = count_ops(expr)
        row["expr_variables"] = len(variables)
        row["expr_xor"] = xors
        row["expr_or"] = ors
        row["expr_and"] = ands
        # A 2-input realisation: each clause = c XORs and c-1 ORs; conjunction of E clauses = E-1 ANDs.
        row["C3_or_per_clause_is_c_minus_1"] = ors == E * (c - 1)
        row["C4_and_bound_E*c-1"] = E * c - 1
        row["C4_nonXOR_2input_gates"] = ands + ors
        row["C4_matches"] = ands + ors == E * c - 1
        out[name] = row

    # C2 / C6: brute force where N is small enough.
    for name in ("K3", "K5", "grid6"):
        p = load(name)
        V, k = len(p.vertices), p.colors
        c = ceil_log2(k)
        n = c * V
        N_valid = k**V
        M = proper_colorings(p)
        # C6: valid-code subspace has k^V assignments (count codes whose every vertex code < k).
        n_valid_codes = sum(
            1
            for code in range(2**n)
            if all(((code >> (c * i)) & (2**c - 1)) < k for i in range(V))
        )
        theta = math.asin(math.sqrt(M / N_valid))
        j_rule = rule_iterations(theta)
        j_peak = first_peak(theta)
        out[name].update(
            {
                "C6_valid_code_assignments": n_valid_codes,
                "C6_k_pow_V": N_valid,
                "C6_matches": n_valid_codes == N_valid,
                "proper_colorings_M": M,
                "theta": theta,
                "C2_rule_j": j_rule,
                "C2_first_peak_j": j_peak,
                "C2_success_at_rule": success(j_rule, theta),
                "C2_success_at_first_peak": success(j_peak, theta),
                "C2_rule_equals_first_peak": j_rule == j_peak,
            }
        )
    text = json.dumps(out, indent=1, sort_keys=True)
    print(text)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text + "\n")


if __name__ == "__main__":
    main()
