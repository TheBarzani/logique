"""Independent domain regressions for parsing, mapping, and coloring semantics."""

import pytest
from logique import ColoringProblem, encode_coloring, read_dimacs


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


def _evaluate(verilog: str, bits: list[int]) -> tuple[int, int]:
    """Value and AND/OR depth of y0 for one input assignment."""
    values = {f"x{i}": (b, 0) for i, b in enumerate(bits)}
    values.update({"1'b0": (0, 0), "1'b1": (1, 0)})

    def term(t):
        value, depth = values[t.lstrip("~")]
        return (1 - value if t.startswith("~") else value), depth

    for line in verilog.splitlines():
        if not line.startswith("assign "):
            continue
        name, expression = line[len("assign ") : -1].split(" = ")
        parts = expression.split()
        if len(parts) == 1:
            values[name] = term(parts[0])
            continue
        (a, da), op, (b, db) = term(parts[0]), parts[1], term(parts[2])
        value = {"&": a & b, "|": a | b, "^": a ^ b}[op]
        values[name] = value, max(da, db) + (op != "^")
    return values["y0"]


@pytest.mark.parametrize(
    "problem",
    [
        ColoringProblem((1, 2, 3), ((1, 2), (2, 3), (1, 3)), 3),
        ColoringProblem((1, 2, 3, 4), ((1, 2), (2, 3), (3, 4), (4, 1)), 5, {2: 4}),
        ColoringProblem((1, 2, 3, 4, 5), ((1, 2), (2, 3), (3, 4), (4, 5)), 2),
        ColoringProblem((), (), 2),
    ],
)
def test_balanced_encoding_keeps_the_predicate_and_its_gates(problem):
    chain = encode_coloring(problem)
    balanced = encode_coloring(problem, balanced=True)
    assert balanced.verilog().count("assign") == chain.verilog().count("assign")
    depths = {}
    for basis in range(1 << chain.input_count):
        bits = [(basis >> i) & 1 for i in range(chain.input_count)]
        expected = problem.is_valid(chain.decode(basis))
        for encoding in (chain, balanced):
            value, depth = _evaluate(encoding.verilog(), bits)
            assert value == expected
            depths[encoding.balanced] = depth
    assert depths[True] <= depths[False]
    if len(problem.edges) >= 4:
        assert depths[True] < depths[False]
