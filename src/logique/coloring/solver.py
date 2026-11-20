"""Exact k-coloring search with a time budget, for positive verification witnesses.

Large instances cannot be verified exhaustively, so their oracles are checked on
known proper colorings. This module finds one by DSATUR backtracking: color the
uncolored vertex with the most distinct colors among its neighbours (ties broken
by the number of uncolored neighbours), try each admissible color, and undo on a
dead end. A new color is opened only after every lower one is in use, which
removes color permutations when nothing is precolored. The search is complete,
so without a time limit it either finds a coloring or proves there is none.
"""

import time

from .model import ColoringProblem


def find_coloring(
    problem: ColoringProblem, *, budget_s: float = 60.0
) -> tuple[str, dict[int, int] | None]:
    """Return ``("found", coloring)``, ``("infeasible", None)`` or ``("timeout", None)``.

    Colors are zero-based and respect the problem's precolors.
    """
    vertices = list(problem.vertices)
    index = {v: i for i, v in enumerate(vertices)}
    neighbours: list[list[int]] = [[] for _ in vertices]
    for a, b in problem.edges:
        neighbours[index[a]].append(index[b])
        neighbours[index[b]].append(index[a])
    k = problem.colors
    color = [-1] * len(vertices)
    # seen[v][c]: colored neighbours of v that have color c.
    seen = [[0] * k for _ in vertices]
    symmetric = not problem.precolored
    deadline = time.monotonic() + budget_s

    def assign(v: int, c: int) -> None:
        color[v] = c
        for u in neighbours[v]:
            seen[u][c] += 1

    def unassign(v: int) -> None:
        c = color[v]
        color[v] = -1
        for u in neighbours[v]:
            seen[u][c] -= 1

    for vertex, c in problem.precolored.items():
        v = index[vertex]
        if seen[v][c]:
            return "infeasible", None
        assign(v, c)

    def choose() -> int:
        best, key = -1, (-1, -1)
        for v in range(len(vertices)):
            if color[v] < 0:
                candidate = (
                    sum(1 for c in range(k) if seen[v][c]),
                    sum(1 for u in neighbours[v] if color[u] < 0),
                )
                if candidate > key:
                    best, key = v, candidate
        return best

    # Explicit stack of (vertex, colors still to try) keeps deep graphs safe.
    stack: list[tuple[int, list[int]]] = []
    while True:
        v = choose()
        if v < 0:
            return "found", {vertices[i]: c for i, c in enumerate(color)}
        used = max(color) + 1
        limit = min(k, used + 1) if symmetric else k
        stack.append((v, [c for c in range(limit) if not seen[v][c]]))
        while True:
            if time.monotonic() > deadline:
                return "timeout", None
            v, options = stack[-1]
            if color[v] >= 0:
                unassign(v)
            if options:
                assign(v, options.pop(0))
                break
            stack.pop()
            if not stack:
                return "infeasible", None
