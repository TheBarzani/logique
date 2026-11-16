"""Deterministic structural Boolean encoding of complete coloring predicates."""

from dataclasses import dataclass
import heapq
from pathlib import Path
from .model import ColoringProblem

# Shapes of the final conjunction over all constraints (balanced encodings only).
TREES = ("input", "rounds", "timed")


def edge_rounds(problem: ColoringProblem) -> dict[frozenset, int]:
    """Rounds of a proper edge colouring: the edges of one round share no vertex.

    The fewest-colour result of several greedy strategies on the line graph is
    kept, so the choice is deterministic for a given graph.
    """
    if not problem.edges:
        return {}
    import networkx as nx

    line = nx.line_graph(problem.to_networkx())
    best: dict | None = None
    for strategy in (
        "largest_first",
        "smallest_last",
        "DSATUR",
        "independent_set",
        "connected_sequential_bfs",
    ):
        colouring = nx.greedy_color(line, strategy=strategy)
        if best is None or max(colouring.values()) < max(best.values()):
            best = colouring
    assert best is not None
    return {frozenset(edge): round_ for edge, round_ in best.items()}


@dataclass(frozen=True)
class ColoringEncoding:
    """Consecutive vertex inputs, least-significant color bit first.

    Conjunctions and disjunctions are left-deep chains unless ``balanced``,
    which builds them as balanced trees of the same gates, so the predicate's
    multiplicative depth grows with the logarithm of the number of constraints.

    ``tree`` shapes the final conjunction of a balanced encoding; every shape
    uses the same gates. ``input`` pairs the constraints in input order.
    ``rounds`` orders the edges by an edge colouring (vertex checks first), so
    that constraints on disjoint vertices are paired. ``timed`` always joins
    the two constraints expected to be ready first: a vertex check when its
    own AND depth is reached, an edge at the end of its colouring round.
    """

    problem: ColoringProblem
    balanced: bool = False
    tree: str = "input"

    def __post_init__(self):
        if self.tree not in TREES:
            raise ValueError(f"tree must be one of {TREES}")
        if self.tree != "input" and not self.balanced:
            raise ValueError("Only a balanced encoding can choose its tree shape")

    @property
    def bits_per_color(self) -> int:
        """Use one bit for a one-color problem, constrained to zero."""
        return max(1, (self.problem.colors - 1).bit_length())

    @property
    def input_count(self) -> int:
        return len(self.problem.vertices) * self.bits_per_color

    @property
    def input_mapping(self) -> dict[int, tuple[int, ...]]:
        b = self.bits_per_color
        return {
            v: tuple(range(i * b, (i + 1) * b))
            for i, v in enumerate(self.problem.vertices)
        }

    def decode(self, basis: int) -> dict[int, int]:
        """Decode only the input register, whose bit zero is the first input."""
        return {
            v: sum(((basis >> q) & 1) << bit for bit, q in enumerate(qs))
            for v, qs in self.input_mapping.items()
        }

    def verilog(self) -> str:
        """Emit two-input structural gates accepted by the pinned native parser."""
        gates: list[str] = []
        wires: list[str] = []
        depth: dict[str, int] = {}  # AND depth of every wire; XOR gates are free

        def gate(a: str, op: str, b: str) -> str:
            name = f"t{len(wires)}"
            wires.append(name)
            gates.append(f"assign {name} = {a} {op} {b};")
            depth[name] = max(depth.get(a, 0), depth.get(b, 0)) + (op != "^")
            return name

        def combine(items: list[str], op: str, identity: str) -> str:
            if not items:
                return identity
            if self.balanced:
                while len(items) > 1:
                    paired = [gate(a, op, b) for a, b in zip(items[::2], items[1::2])]
                    items = paired + items[len(paired) * 2 :]
                return items[0]
            result = items[0]
            for item in items[1:]:
                result = gate(result, op, item)
            return result

        mapping = self.input_mapping
        constraints: list[str] = []
        for v, qs in mapping.items():
            # A compact comparator for x < k, built from most significant bits.
            if self.problem.colors != 1 << len(qs):
                less, equal = "1'b0", "1'b1"
                for bit in reversed(range(len(qs))):
                    x = f"x{qs[bit]}"
                    if (self.problem.colors >> bit) & 1:
                        less = gate(less, "|", gate(equal, "&", f"~{x}"))
                        equal = gate(equal, "&", x)
                    else:
                        equal = gate(equal, "&", f"~{x}")
                constraints.append(less)
            if v in self.problem.precolored:
                color = self.problem.precolored[v]
                constraints.append(
                    combine(
                        [
                            f"x{q}" if (color >> bit) & 1 else f"~x{q}"
                            for bit, q in enumerate(qs)
                        ],
                        "&",
                        "1'b1",
                    )
                )
        local = len(constraints)  # vertex checks come first
        rounds = edge_rounds(self.problem) if self.tree != "input" else {}
        edges = list(self.problem.edges)
        if rounds:
            edges.sort(key=lambda e: rounds[frozenset(e)])  # stable within a round
        for u, v in edges:
            constraints.append(
                combine(
                    [
                        gate(f"x{a}", "^", f"x{b}")
                        for a, b in zip(mapping[u], mapping[v])
                    ],
                    "|",
                    "1'b0",
                )
            )
        if self.tree == "timed" and len(constraints) > 1:
            # Vertex checks are ready at their own AND depth; edges finish one
            # colouring round after another, each round as deep as one edge.
            start = max((depth.get(c, 0) for c in constraints[:local]), default=0)
            level = max((depth.get(c, 0) for c in constraints[local:]), default=0)
            ready = [depth.get(c, 0) for c in constraints[:local]] + [
                start + (rounds[frozenset(e)] + 1) * max(1, level) for e in edges
            ]
            heap = [(t, i, c) for i, (t, c) in enumerate(zip(ready, constraints))]
            heapq.heapify(heap)
            count = len(heap)
            while len(heap) > 1:
                ta, _, a = heapq.heappop(heap)
                tb, _, b = heapq.heappop(heap)
                heapq.heappush(heap, (max(ta, tb) + 1, count, gate(a, "&", b)))
                count += 1
            output = heap[0][2]
        else:
            output = combine(constraints, "&", "1'b1")
        inputs = [f"x{i}" for i in range(self.input_count)]
        declarations = [f"module top({', '.join(inputs + ['y0'])});"]
        if inputs:
            declarations.append(f"input {', '.join(inputs)};")
        declarations.append("output y0;")
        if wires:
            declarations.append(f"wire {', '.join(wires)};")
        return "\n".join(
            declarations + gates + [f"assign y0 = {output};", "endmodule", ""]
        )

    def write_verilog(self, path: str | Path) -> Path:
        """Write the encoded predicate and return its path."""
        path = Path(path)
        path.write_text(self.verilog())
        return path


def encode_coloring(
    problem: ColoringProblem, *, balanced: bool = False, tree: str = "input"
) -> ColoringEncoding:
    """Encode all vertices, valid colors, precolors, and edge inequalities."""
    return ColoringEncoding(problem, balanced, tree)


def edge_coloring_expression(problem: ColoringProblem) -> tuple[str, list[str]]:
    """Build the paper's edge-only expression with its original tree/input order.

    Include only vertices incident on edges. Precolors and unused binary color
    codes are deliberately unconstrained, matching the historical encoding.
    """
    if problem.colors < 2 or not problem.edges:
        raise ValueError("Edge-only expression requires edges and at least two colors")
    bits = (problem.colors - 1).bit_length()
    vertices = sorted({v for edge in problem.edges for v in edge})
    variables = [f"v{v}_{bit}" for v in vertices for bit in range(bits)]
    expression = " & ".join(
        "(" + " | ".join(f"(v{u}_{bit} ^ v{v}_{bit})" for bit in range(bits)) + ")"
        for u, v in problem.to_networkx().edges()
    )
    return expression, variables
