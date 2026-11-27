"""The graph datasets agree with their manifest, folders and witnesses."""

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from logique.coloring import read_dimacs

ROOT = Path(__file__).resolve().parents[1]
GRAPHS = ROOT / "datasets" / "graphs"
TIERS = ("small", "medium", "large")


@pytest.fixture(scope="module")
def manifest():
    return json.loads((GRAPHS / "manifest.json").read_text())


@pytest.fixture(scope="module")
def problems(manifest):
    loaded = {}
    for entry in manifest["graphs"]:
        problem = read_dimacs(ROOT / entry["path"])
        loaded[entry["name"]] = replace(problem, precolored={})
    return loaded


def test_every_file_matches_its_entry(manifest, problems):
    names = Counter(entry["name"] for entry in manifest["graphs"])
    assert max(names.values()) == 1
    for entry in manifest["graphs"]:
        path = ROOT / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        problem = problems[entry["name"]]
        assert len(problem.vertices) == entry["vertices"]
        assert len(problem.edges) == entry["edges"]
        assert problem.colors == entry["colors"]


def test_folders_encode_split_tier_and_class(manifest):
    for entry in manifest["graphs"]:
        parts = Path(entry["path"]).relative_to("datasets/graphs").parts
        if entry["split"] == "discovery":
            assert parts[0] == "manuscript"
        else:
            assert entry["split"] == "confirmation"
            assert parts[:2] == (entry["tier"], entry["class"])
        assert entry["tier"] in TIERS


def test_tier_folders_hold_only_listed_graphs(manifest):
    listed = {entry["path"] for entry in manifest["graphs"]}
    for tier in (*TIERS, "manuscript"):
        for path in (GRAPHS / tier).rglob("*.col"):
            assert str(path.relative_to(ROOT)) in listed, path


def test_tiers_follow_their_rules(manifest):
    for entry in manifest["graphs"]:
        if entry["tier"] == "small":
            assert entry["data_qubits"] <= manifest["small_qubits"]
        elif entry["tier"] == "medium":
            assert entry["colorings"] is not None
        else:
            assert entry["colorings"] is None


def test_witnesses_are_proper_colorings(manifest, problems):
    witnesses = json.loads((GRAPHS / "witnesses.json").read_text())
    for entry in manifest["graphs"]:
        if entry["witness"] in ("found", "planted"):
            coloring = {int(v): c for v, c in witnesses[entry["name"]].items()}
            assert problems[entry["name"]].is_valid(coloring), entry["name"]


def test_no_two_problems_are_isomorphic(manifest, problems):
    """The same graph may appear with different color counts (P4 and P4_k3)."""

    def invariants(problem):
        degrees = Counter(v for edge in problem.edges for v in edge)
        return (
            problem.colors,
            len(problem.vertices),
            len(problem.edges),
            sorted(degrees.values()),
        )

    groups: dict = {}
    for name, problem in problems.items():
        groups.setdefault(str(invariants(problem)), []).append(name)
    rustworkx = pytest.importorskip("rustworkx")

    def graph(problem):
        g = rustworkx.PyGraph()
        index = {v: g.add_node(v) for v in problem.vertices}
        g.add_edges_from_no_data([(index[a], index[b]) for a, b in problem.edges])
        return g

    for names in groups.values():
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                assert not rustworkx.is_isomorphic(
                    graph(problems[a]), graph(problems[b])
                ), (a, b)
