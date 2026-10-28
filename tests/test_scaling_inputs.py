"""Independent graph preparation never invokes the blocked compiler boundary."""

from pathlib import Path

import pytest

from logique.benchmarks.scaling_inputs import (
    bounded_dimacs,
    decode_dimacs_binary,
    greedy_witness,
    normalize_legacy,
    queen_problem,
)
from logique.coloring import ColoringProblem


ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("size,colors", [(5, 5), (7, 7), (8, 11), (9, 11)])
def test_queen_witness_checks_every_attack(size, colors):
    problem, witness = queen_problem(size, colors)
    assert problem.is_valid(witness)
    assert len(problem.vertices) == size * size
    # Independent attack enumeration, including both diagonal slopes.
    for u in problem.vertices:
        r, c = divmod(u - 1, size)
        for v in problem.vertices:
            s, t = divmod(v - 1, size)
            if u != v and (r == s or c == t or abs(r - s) == abs(c - t)):
                assert witness[u] != witness[v]
                assert tuple(sorted((u, v))) in problem.edges


def test_queen_rejects_invalid_formula_and_allocation():
    with pytest.raises(ValueError):
        queen_problem(8, 8)
    with pytest.raises(ValueError):
        queen_problem(1000000, 5)


@pytest.mark.parametrize(
    "name,colors", [("5-FullIns_3.col", 8), ("4-Insertions_3.col", 4)]
)
def test_exact_legacy_normalization_preserves_edges_and_source(tmp_path, name, colors):
    source = ROOT / "datasets/graphs/scaling" / name
    before = source.read_bytes()
    output = tmp_path / name
    report = normalize_legacy(source, output, colors=colors)
    normalized = bounded_dimacs(output, colors)
    assert not normalized.precolored
    assert report["removed_records"] == ["n 1 0"]
    assert normalized.edges == bounded_dimacs(source, colors).edges
    assert source.read_bytes() == before
    with pytest.raises(FileExistsError):
        normalize_legacy(source, output, colors=colors)


def test_normalization_refuses_nonallowlisted_or_changed_input(tmp_path):
    source = tmp_path / "4-Insertions_3.col"
    source.write_text("p edge 2 1\nn 1 0\ne 1 2\n")
    with pytest.raises(ValueError, match="exact legacy"):
        normalize_legacy(source, tmp_path / "new.col", colors=4)


def test_huge_header_rejected_before_parser(tmp_path):
    source = tmp_path / "huge.col"
    source.write_text("p edge 99999999999 0\n")
    with pytest.raises(ValueError, match="budget"):
        bounded_dimacs(source, 3)


def test_binary_decode_bit_order_and_doubled_header(tmp_path):
    # 1--2, 1--3; rows padded independently; MSB denotes column zero.
    header = b"c fixture\np edge 3 4\n"
    source = tmp_path / "graph.b"
    source.write_bytes(str(len(header)).encode() + b"\n" + header + b"\x00\x80\x80")
    output = tmp_path / "graph.col"
    report = decode_dimacs_binary(source, output)
    assert report["declared_edges"] == 4
    assert report["undirected_edges"] == 2
    assert bounded_dimacs(output, 2).edges == ((1, 2), (1, 3))
    with pytest.raises(FileExistsError):
        decode_dimacs_binary(source, output)
    source.write_bytes(source.read_bytes()[:-1])
    with pytest.raises(ValueError, match="length mismatch"):
        decode_dimacs_binary(source, tmp_path / "bad.col")


def test_binary_refuses_self_loop_and_wrong_count(tmp_path):
    for payload, count in [(b"\x80\x00", 1), (b"\x00\x80", 3)]:
        header = f"p edge 2 {count}\n".encode()
        source = tmp_path / "bad.b"
        source.write_bytes(str(len(header)).encode() + b"\n" + header + payload)
        with pytest.raises(ValueError):
            decode_dimacs_binary(source, tmp_path / "bad.col")


def test_greedy_failure_is_unknown_not_unsat():
    graph = ColoringProblem((1, 2, 3), ((1, 2), (2, 3), (1, 3)), 2)
    assert greedy_witness(graph) is None
    assert greedy_witness(ColoringProblem((1, 9), ((1, 9),), 2)) == {1: 0, 9: 1}
    with pytest.raises(ValueError, match="precolors"):
        greedy_witness(ColoringProblem((1,), (), 2, {1: 0}))
