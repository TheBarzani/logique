"""Validated graph-coloring inputs, independent of circuit and plotting libraries."""

from dataclasses import dataclass, field
from collections.abc import Mapping
from types import MappingProxyType


@dataclass(frozen=True)
class ColoringProblem:
    """Vertices have integer labels; colors are zero-based, including precolors."""

    vertices: tuple[int, ...]
    edges: tuple[tuple[int, int], ...]
    colors: int
    precolored: Mapping[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        vertices = tuple(sorted(self.vertices))
        if any(type(v) is not int for v in vertices) or len(set(vertices)) != len(
            vertices
        ):
            raise ValueError("Vertex labels must be distinct integers")
        if type(self.colors) is not int or self.colors < 1:
            raise ValueError("colors must be a positive integer")
        edges = tuple(sorted(set(tuple(sorted(e)) for e in self.edges)))
        if any(len(e) != 2 or any(v not in vertices for v in e) for e in edges):
            raise ValueError("Every edge must connect two declared vertices")
        precolored = dict(self.precolored)
        if any(
            v not in vertices or type(c) is not int or not 0 <= c < self.colors
            for v, c in precolored.items()
        ):
            raise ValueError(
                "Precolors must refer to declared vertices and valid colors"
            )
        object.__setattr__(self, "vertices", vertices)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "precolored", MappingProxyType(precolored))

    def is_valid(self, assignment: Mapping[int, int]) -> bool:
        """Check a complete coloring directly, without Boolean synthesis."""
        return (
            set(assignment) == set(self.vertices)
            and all(
                type(c) is int and 0 <= c < self.colors for c in assignment.values()
            )
            and all(assignment[v] == c for v, c in self.precolored.items())
            and all(assignment[u] != assignment[v] for u, v in self.edges)
        )

    def to_networkx(self):
        """Return a fresh graph with integer precolor attributes."""
        import networkx as nx

        graph = nx.Graph()
        graph.add_nodes_from(self.vertices)
        graph.add_edges_from(self.edges)
        nx.set_node_attributes(graph, dict(self.precolored), "color")
        return graph
