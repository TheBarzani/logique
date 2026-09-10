"""DIMACS edge format with VCGC's x colors and n precolor extensions."""

from pathlib import Path
from .model import ColoringProblem


def read_dimacs(path: str | Path, *, colors: int | None = None) -> ColoringProblem:
    """Read a fresh problem; reject malformed records with line-numbered errors."""
    size = None
    count = None
    edges: list[tuple[int, int]] = []
    precolored: dict[int, int] = {}
    file_colors = None
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        parts = line.split()
        if not parts or parts[0] == "c":
            continue
        try:
            if parts[:2] == ["p", "edge"] and len(parts) == 4 and size is None:
                size, count = map(int, parts[2:])
                if size < 0 or count < 0:
                    raise ValueError("Negative graph size")
            elif parts[0] == "e" and len(parts) == 3:
                edges.append((int(parts[1]), int(parts[2])))
            elif (
                parts[:2] == ["x", "colors"] and len(parts) == 3 and file_colors is None
            ):
                file_colors = int(parts[2])
            elif parts[0] == "n" and len(parts) == 3:
                vertex, color = map(int, parts[1:])
                if vertex in precolored:
                    raise ValueError("Duplicate precolor")
                precolored[vertex] = color
            else:
                raise ValueError("Unknown, duplicate, or malformed record")
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: {error}") from error
    if size is None or count != len(edges):
        raise ValueError("Missing problem record or edge count mismatch")
    selected = colors if colors is not None else file_colors
    if selected is None:
        raise ValueError("Specify colors or provide an x colors record")
    return ColoringProblem(
        tuple(range(1, size + 1)), tuple(edges), selected, precolored
    )
