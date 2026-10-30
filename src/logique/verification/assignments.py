"""Explicit verification inputs: witnesses, boundary cases and random samples.

Random samples of a large coloring instance almost never contain a proper
coloring, so they cannot show that solutions are marked. These helpers add
proper colorings found by a classical search, assignments that violate exactly
one edge or use an unused color code, and seeded random inputs.
"""

import numpy as np

from .classical import input_assignments


def proper_colorings(problem, count: int, *, seed: int = 7, budget: int = 200_000):
    """Find up to ``count`` distinct proper colorings by randomized backtracking.

    Vertices are colored in decreasing order of degree with colors tried in a
    random order. Precolored vertices keep their color. The search stops after
    ``budget`` assignment steps per attempt, so a hard instance may return fewer
    colorings than requested.
    """
    rng = np.random.default_rng(seed)
    neighbours = {v: set() for v in problem.vertices}
    for u, v in problem.edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    order = sorted(problem.vertices, key=lambda v: -len(neighbours[v]))
    found: list[dict[int, int]] = []
    seen = set()
    for _ in range(4 * count):
        coloring = dict(problem.precolored)
        steps = [0]

        def extend(position: int) -> bool:
            if position == len(order):
                return True
            vertex = order[position]
            if vertex in problem.precolored:
                used = {coloring.get(u) for u in neighbours[vertex]}
                return coloring[vertex] not in used and extend(position + 1)
            for color in rng.permutation(problem.colors):
                steps[0] += 1
                if steps[0] > budget:
                    return False
                if all(coloring.get(u) != color for u in neighbours[vertex]):
                    coloring[vertex] = int(color)
                    if extend(position + 1):
                        return True
                    del coloring[vertex]
            return False

        if not extend(0):
            continue
        key = tuple(coloring[v] for v in problem.vertices)
        if key not in seen:
            seen.add(key)
            found.append(dict(coloring))
        if len(found) == count:
            break
    return found


def encode_assignment(encoding, coloring: dict[int, int]) -> np.ndarray:
    """Input bits of one coloring, in the encoding's least-significant-first order."""
    bits = np.zeros(encoding.input_count, dtype=bool)
    for vertex, wires in encoding.input_mapping.items():
        for bit, wire in enumerate(wires):
            bits[wire] = (coloring[vertex] >> bit) & 1
    return bits


def verification_assignments(
    encoding,
    *,
    samples: int = 256,
    witnesses: int = 16,
    exhaustive_inputs: int = 12,
    seed: int = 7,
):
    """Return an input matrix (inputs × assignments) and a coverage record.

    Up to ``exhaustive_inputs`` inputs every assignment is used. Beyond that the
    matrix holds proper colorings, for each one an assignment that copies a
    neighbor's color onto one endpoint of an edge and, when unused codes exist,
    one that gives a vertex an unused code, followed by ``samples`` random
    assignments. The coverage record states how many of each were included.
    """
    n = encoding.input_count
    if n <= exhaustive_inputs:
        return input_assignments(n), {"status": "exhaustive", "assignments": 1 << n}
    problem = encoding.problem
    rng = np.random.default_rng(seed)
    proper = proper_colorings(problem, witnesses, seed=seed)
    columns = [encode_assignment(encoding, c) for c in proper]
    edges = list(problem.edges)
    edge_cases = unused_cases = 0
    unused = range(problem.colors, 1 << encoding.bits_per_color)
    for coloring in proper:
        if edges:
            u, v = edges[rng.integers(len(edges))]
            if u not in problem.precolored:
                columns.append(
                    encode_assignment(encoding, {**coloring, u: coloring[v]})
                )
                edge_cases += 1
        if len(unused):
            vertex = problem.vertices[rng.integers(len(problem.vertices))]
            code = int(unused[rng.integers(len(unused))])
            columns.append(encode_assignment(encoding, {**coloring, vertex: code}))
            unused_cases += 1
    random = rng.integers(0, 2, (n, samples)).astype(bool)
    matrix = np.column_stack([*columns, random]) if columns else random
    coverage = {
        "status": "explicit",
        "assignments": matrix.shape[1],
        "witnesses": len(proper),
        "edge_violations": edge_cases,
        "unused_codes": unused_cases,
        "random": samples,
        "seed": seed,
    }
    return matrix, coverage
