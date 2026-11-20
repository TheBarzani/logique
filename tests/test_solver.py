"""The witness search finds proper colorings and proves small infeasible cases."""

import itertools

import pytest

from logique.coloring.model import ColoringProblem
from logique.coloring.solver import find_coloring


def complete(n, colors):
    return ColoringProblem(
        tuple(range(1, n + 1)),
        tuple(itertools.combinations(range(1, n + 1), 2)),
        colors,
    )


def petersen(colors):
    outer = [(i, i % 5 + 1) for i in range(1, 6)]
    spokes = [(i, i + 5) for i in range(1, 6)]
    inner = [(6 + i, 6 + (i + 2) % 5) for i in range(5)]
    return ColoringProblem(tuple(range(1, 11)), tuple(outer + spokes + inner), colors)


@pytest.mark.parametrize(
    "problem, feasible",
    [
        (complete(3, 3), True),
        (complete(4, 3), False),
        (complete(5, 5), True),
        (petersen(3), True),
        (petersen(2), False),
    ],
)
def test_finds_a_proper_coloring_or_proves_there_is_none(problem, feasible):
    status, coloring = find_coloring(problem, budget_s=10)
    if feasible:
        assert status == "found" and problem.is_valid(coloring)
    else:
        assert status == "infeasible" and coloring is None


def test_precolors_are_kept():
    problem = ColoringProblem((1, 2, 3), ((1, 2), (2, 3)), 3, {1: 2, 3: 2})
    status, coloring = find_coloring(problem)
    assert status == "found" and coloring[1] == 2 == coloring[3]
    assert problem.is_valid(coloring)
    clash = ColoringProblem((1, 2), ((1, 2),), 2, {1: 0, 2: 0})
    assert find_coloring(clash) == ("infeasible", None)


def test_an_exhausted_budget_reports_a_timeout():
    assert find_coloring(petersen(3), budget_s=-1) == ("timeout", None)
