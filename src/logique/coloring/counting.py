"""Exact counts of proper colorings, used to choose Grover iteration counts."""

from math import perm
from typing import Any

from .model import ColoringProblem


def _eliminate(problem: ColoringProblem, budget: int) -> int | None:
    """Count by variable elimination, or None when a table would exceed ``budget``.

    Each edge contributes a k-by-k "different colors" table and each vertex a
    table of its allowed colors. Vertices are summed out in greedy min-fill
    order, so the largest table has k^(w + 1) entries for the induced width w
    of that order. Integer tables are evaluated alongside floating-point ones,
    which reveal any overflow; numpy is optional.
    """
    try:
        import numpy as np
    except ImportError:
        return None
    k = problem.colors
    adjacency: dict[int, set[int]] = {v: set() for v in problem.vertices}
    for u, v in problem.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    # Each table is kept as an (integer, floating-point) pair over its vertices.
    tables: list[tuple[tuple[int, ...], tuple[Any, Any]]] = []
    different = 1 - np.eye(k, dtype=np.int64)
    for u, v in problem.edges:
        tables.append(((u, v), (different, different.astype(float))))
    for v in problem.vertices:
        allowed = np.zeros(k, dtype=np.int64)
        if v in problem.precolored:
            allowed[problem.precolored[v]] = 1
        else:
            allowed[:] = 1
        tables.append(((v,), (allowed, allowed.astype(float))))

    def fill(v: int) -> int:
        near = sorted(adjacency[v])
        return sum(
            b not in adjacency[a] for i, a in enumerate(near) for b in near[i + 1 :]
        )

    exact, approximate = 1, 1.0
    while adjacency:
        vertex = min(adjacency, key=lambda v: (fill(v), len(adjacency[v]), v))
        scope = sorted(adjacency[vertex])
        if k ** (len(scope) + 1) > budget:
            return None
        involved = [pair for names, pair in tables if vertex in names]
        letters = {v: chr(97 + i) for i, v in enumerate([vertex, *scope])}
        spec = ",".join(
            "".join(letters[v] for v in names) for names, _ in tables if vertex in names
        )
        spec += "->" + "".join(letters[v] for v in scope)
        tables = [(names, pair) for names, pair in tables if vertex not in names]
        product = np.einsum(spec, *(pair[0] for pair in involved))
        estimate = np.einsum(spec, *(pair[1] for pair in involved))
        if scope:
            tables.append((tuple(scope), (product, estimate)))
        else:
            exact *= int(product)
            approximate *= float(estimate)
        for a in scope:
            adjacency[a] |= set(scope) - {a}
            adjacency[a].discard(vertex)
        del adjacency[vertex]
    if abs(exact - approximate) > 1e-6 * max(1.0, approximate):
        return None
    return exact


def count_colorings(
    problem: ColoringProblem, *, budget: int = 10_000_000
) -> int | None:
    """Count proper colorings with labelled colors, or None beyond ``budget``.

    Without precolors, colorings are counted up to a permutation of the color
    labels: each vertex receives either a color already in use or the next
    unused one, and every such partition into independent sets is weighted by
    the number of ways to label its m classes, k! / (k - m)!. Complete graphs
    use this formula directly. Variable elimination is tried before the search;
    ``budget`` bounds both its largest table and the number of search steps.
    """
    vertices = list(problem.vertices)
    k = problem.colors
    neighbours: dict[int, set[int]] = {v: set() for v in vertices}
    for u, v in problem.edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    n = len(vertices)
    if not problem.precolored and sum(map(len, neighbours.values())) == n * (n - 1):
        return perm(k, n) if n <= k else 0
    counted = _eliminate(problem, budget)
    if counted is not None:
        return counted
    order = sorted(vertices, key=lambda v: -len(neighbours[v]))
    position = {v: i for i, v in enumerate(order)}
    earlier = [
        [position[u] for u in neighbours[v] if position[u] < i]
        for i, v in enumerate(order)
    ]
    fixed = {position[v]: c for v, c in problem.precolored.items()}
    colors = [-1] * n
    steps = 0

    def extend(i: int, used: int) -> int:
        nonlocal steps
        steps += 1
        if steps > budget:
            raise TimeoutError
        if i == n:
            return 1 if fixed else perm(k, used)
        taken = {colors[j] for j in earlier[i]}
        if i in fixed:
            choices = [fixed[i]] if fixed[i] not in taken else []
        elif fixed:
            choices = [c for c in range(k) if c not in taken]
        else:
            choices = [c for c in range(min(used + 1, k)) if c not in taken]
        total = 0
        for color in choices:
            colors[i] = color
            total += extend(i + 1, max(used, color + 1))
        colors[i] = -1
        return total

    try:
        return extend(0, 0)
    except TimeoutError:
        return None
