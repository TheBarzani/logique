"""Exact counts of proper colorings, used to choose Grover iteration counts."""

from math import perm

from .model import ColoringProblem


def count_colorings(
    problem: ColoringProblem, *, budget: int = 10_000_000
) -> int | None:
    """Count proper colorings with labelled colors, or None beyond ``budget``.

    Without precolors, colorings are counted up to a permutation of the color
    labels: each vertex receives either a color already in use or the next
    unused one, and every such partition into independent sets is weighted by
    the number of ways to label its m classes, k! / (k - m)!. Complete graphs
    use this formula directly. ``budget`` bounds the number of search steps.
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
