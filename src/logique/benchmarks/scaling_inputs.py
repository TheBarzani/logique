"""Bounded input preparation for the selected, unprecolored compiler study.

This module launches no compiler, solver, or quantum simulation. Witnesses are
checked directly on graph edges, independently of the Boolean encoder.
"""

import hashlib
from pathlib import Path

from logique.coloring import ColoringProblem, read_dimacs


LEGACY_NORMALIZATION = {
    "5-FullIns_3.col": "b7b92bc6efadefef0a398c37171d755eacd73d7d4b56bb955ac830414cf72b64",
    "4-Insertions_3.col": "efb99099fbe360deb28e0bb8907e0ddbcc38eb009eaa75df46e6c3c2bc891125",
}
MAX_BYTES = 2 * 1024**2
MAX_VERTICES = 1000
MAX_EDGES = 100000


def bounded_bytes(path: str | Path) -> bytes:
    """Reject oversized input before reading it into memory."""
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("input exceeds 2 MiB preparation budget")
    return data


def bounded_dimacs(path: str | Path, colors: int) -> ColoringProblem:
    """Check declared sizes before the maintained parser allocates vertices."""
    if type(colors) is not int or not 2 <= colors <= 256:
        raise ValueError("colors must be in [2, 256]")
    data = bounded_bytes(path)
    for line in data.decode().splitlines():
        fields = line.split()
        if fields[:2] == ["p", "edge"] and len(fields) == 4:
            n, m = map(int, fields[2:])
            if not 0 <= n <= MAX_VERTICES or not 0 <= m <= MAX_EDGES:
                raise ValueError("declared graph exceeds preparation budget")
    return read_dimacs(path, colors=colors)


def normalize_legacy(path: str | Path, output: str | Path, *, colors: int) -> dict:
    """Remove precolors only from two exact legacy inputs under full-plan policy.

    Preserve comments and edge records; replace the historical color parameter
    explicitly. The new file is an unprecolored graph experiment, not an
    equivalent fixed-precolor problem. Never modify the original bytes.
    """
    path, output = Path(path), Path(output)
    data = bounded_bytes(path)
    digest = hashlib.sha256(data).hexdigest()
    if LEGACY_NORMALIZATION.get(path.name) != digest:
        raise ValueError("normalization requires an allowlisted exact legacy input")
    problem = bounded_dimacs(path, colors)
    lines, removed = [], []
    for line in data.decode().splitlines():
        fields = line.split()
        if fields and fields[0] == "n":
            removed.append(line)
        elif fields[:2] != ["x", "colors"]:
            lines.append(line)
    lines += [f"x colors {colors}"]
    with output.open("x") as stream:
        stream.write("\n".join(lines) + "\n")
    normalized = bounded_dimacs(output, colors)
    if normalized.precolored or normalized.edges != problem.edges:
        raise AssertionError("normalization changed graph edges or retained precolors")
    return {
        "source_sha256": digest,
        "normalized_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "removed_records": removed,
        "colors": colors,
        "policy": "full-plan unprecolored graph normalization; fixed-precolor semantics discarded",
    }


def decode_dimacs_binary(path: str | Path, output: str | Path) -> dict:
    """Decode bounded DIMACS lower-triangle bytes using primary bin2asc bit order.

    Some original headers count both orientations. Accept exactly m or 2m;
    record this discrepancy and write the number of undirected edge records.
    Reject self loops, truncated/extra data, and nonzero padding bits.
    """
    data = bounded_bytes(path)
    first, rest = data.split(b"\n", 1)
    length = int(first)
    if not 0 < length <= min(len(rest), 65536):
        raise ValueError("invalid binary preamble length")
    preamble = rest[:length].decode("ascii")
    headers = [s.split() for s in preamble.splitlines() if s.startswith("p ")]
    if len(headers) != 1 or headers[0][:2] != ["p", "edge"]:
        raise ValueError("one p edge header required")
    n, declared = map(int, headers[0][2:])
    if not 0 < n <= MAX_VERTICES or not 0 <= declared <= MAX_EDGES:
        raise ValueError("binary graph exceeds preparation budget")
    payload = rest[length:]
    if len(payload) != sum((i + 8) // 8 for i in range(n)):
        raise ValueError("binary payload length mismatch")
    edges, offset = [], 0
    for i in range(n):
        row = payload[offset : offset + (i + 8) // 8]
        offset += len(row)
        for j in range(len(row) * 8):
            if row[j // 8] & (1 << (7 - j % 8)):
                if j >= i:
                    raise ValueError("self loop or nonzero padding")
                edges.append((j + 1, i + 1))
    if declared not in (len(edges), 2 * len(edges)):
        raise ValueError("binary header edge count disagrees with adjacency")
    comments = [s for s in preamble.splitlines() if s.startswith("c")]
    text = "\n".join(comments + [f"p edge {n} {len(edges)}"])
    text += "\n" + "".join(f"e {u} {v}\n" for u, v in edges)
    with Path(output).open("x") as stream:
        stream.write(text)
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "decoded_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "declared_edges": declared,
        "undirected_edges": len(edges),
        "format": "primary bin2asc.c: row (i+8)//8 bytes, MSB-first columns <=i",
    }


def queen_problem(size: int, colors: int) -> tuple[ColoringProblem, dict[int, int]]:
    """Construct row-major queen squares and verify (row+2*column) mod colors.

    Sizes/colors are explicit study parameters. No chromatic number is inferred.
    """
    if type(size) is not int or not 2 <= size <= 16:
        raise ValueError("queen size must be in [2, 16]")
    if type(colors) is not int or not 2 <= colors <= 256:
        raise ValueError("colors must be in [2, 256]")
    positions = [divmod(i, size) for i in range(size * size)]
    edges = []
    for i, (r, c) in enumerate(positions):
        for j in range(i):
            s, t = positions[j]
            if r == s or c == t or abs(r - s) == abs(c - t):
                edges.append((j + 1, i + 1))
    problem = ColoringProblem(tuple(range(1, size * size + 1)), tuple(edges), colors)
    witness = {i + 1: (r + 2 * c) % colors for i, (r, c) in enumerate(positions)}
    if not problem.is_valid(witness):
        raise ValueError("chosen queen color formula is invalid at these parameters")
    return problem, witness


def greedy_witness(problem: ColoringProblem) -> dict[int, int] | None:
    """Try one deterministic saturation-degree greedy coloring; no UNSAT inference.

    Quadratic selection is bounded to the preparation vertex/edge limits.
    Failure means unknown, and never changes the requested color count.
    """
    if problem.precolored:
        raise ValueError("fixed precolors are excluded")
    if len(problem.vertices) > MAX_VERTICES or len(problem.edges) > MAX_EDGES:
        raise ValueError("graph exceeds witness preparation budget")
    adjacent = {v: set() for v in problem.vertices}
    for u, v in problem.edges:
        adjacent[u].add(v)
        adjacent[v].add(u)
    witness: dict[int, int] = {}
    while len(witness) < len(adjacent):
        vertex = max(
            (v for v in adjacent if v not in witness),
            key=lambda v: (
                len({witness[u] for u in adjacent[v] if u in witness}),
                len(adjacent[v]),
                -v,
            ),
        )
        used = {witness[u] for u in adjacent[vertex] if u in witness}
        color = next((c for c in range(problem.colors) if c not in used), None)
        if color is None:
            return None
        witness[vertex] = color
    return witness if problem.is_valid(witness) else None
