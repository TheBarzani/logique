"""Deterministic structural Boolean encoding of complete coloring predicates."""

from dataclasses import dataclass
from pathlib import Path
from .model import ColoringProblem


@dataclass(frozen=True)
class ColoringEncoding:
    """Consecutive vertex inputs, least-significant color bit first."""

    problem: ColoringProblem
    balanced: bool = False

    def __post_init__(self) -> None:
        if type(self.balanced) is not bool:
            raise ValueError("balanced must be a Boolean")

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

        def gate(a: str, op: str, b: str) -> str:
            name = f"t{len(wires)}"
            wires.append(name)
            gates.append(f"assign {name} = {a} {op} {b};")
            return name

        def combine(items: list[str], op: str, identity: str) -> str:
            if not items:
                return identity
            if self.balanced:
                while len(items) > 1:
                    items = [
                        (
                            gate(items[i], op, items[i + 1])
                            if i + 1 < len(items)
                            else items[i]
                        )
                        for i in range(0, len(items), 2)
                    ]
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
        for u, v in self.problem.edges:
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
    problem: ColoringProblem, *, balanced: bool = False
) -> ColoringEncoding:
    """Encode the complete predicate with optional balanced AND and OR trees.

    The default retains the existing gate order. Balancing changes only the
    association of conjunctions and disjunctions, preserving all constraints
    and input ordering; it does not select a native optimization strategy.
    """
    return ColoringEncoding(problem, balanced=balanced)


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
