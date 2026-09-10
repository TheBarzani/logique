"""Independent domain regressions for parsing, mapping, and coloring semantics."""

import pytest
from vcgc import ColoringProblem, encode_coloring, read_dimacs


def test_dimacs_whitespace_isolates_precolors_and_repeated_reads(tmp_path):
    path = tmp_path / "graph.col"
    path.write_text("  c comment\n\n p edge 3 1\n e 1 2\n n 1 0\n x colors 3\n")
    first = read_dimacs(path)
    assert first.vertices == (1, 2, 3)
    assert dict(first.precolored) == {1: 0}
    path.write_text("p edge 1 0\nx colors 2\n")
    assert read_dimacs(path).vertices == (1,)
    assert first.vertices == (1, 2, 3)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "p edge 2 1\nx colors 2",
        "p edge 2 1\ne 1 3\nx colors 2",
        "p edge 1 0\nn 1 2\nx colors 2",
        "p edge 1 0\nbad record\nx colors 2",
        "p edge 1 0\nx colors 0",
        "p edge 1 0\np edge 1 0\nx colors 2",
    ],
)
def test_malformed_dimacs(content, tmp_path):
    path = tmp_path / "bad.col"
    path.write_text(content)
    with pytest.raises(ValueError):
        read_dimacs(path)


def test_color_override_and_missing_color(tmp_path):
    path = tmp_path / "graph.col"
    path.write_text("p edge 2 1\ne 1 2\n")
    with pytest.raises(ValueError, match="Specify colors"):
        read_dimacs(path)
    assert read_dimacs(path, colors=4).colors == 4


@pytest.mark.parametrize(
    "colors,width", [(1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (8, 3)]
)
def test_encoding_width_and_noncontiguous_labels(colors, width):
    encoding = encode_coloring(ColoringProblem((20, 3, 7), ((20, 3),), colors))
    assert encoding.bits_per_color == width
    assert list(encoding.input_mapping) == [3, 7, 20]
    assert encoding.input_count == 3 * width
    assert encoding.decode(1) == {3: 1, 7: 0, 20: 0}
    assert encoding.verilog() == encode_coloring(encoding.problem).verilog()


def test_classical_checker_checks_all_constraints():
    problem = ColoringProblem((1, 2, 9), ((1, 2),), 3, {1: 0})
    assert problem.is_valid({1: 0, 2: 1, 9: 2})
    for assignment in (
        {1: 0, 2: 0, 9: 1},
        {1: 0, 2: 3, 9: 1},
        {1: 1, 2: 2, 9: 0},
        {1: 0, 2: 1},
    ):
        assert not problem.is_valid(assignment)
    with pytest.raises(TypeError):
        problem.precolored[1] = 1
