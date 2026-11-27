"""Build the graphs of the three tiers, with their manifest, witnesses and index.

Usage (from the checkout, research environment):

    uv run --no-sync python tools/build_graph_tiers.py [--fetch] [--jobs 4] [--recompute]

Layout of ``datasets/graphs/``:

- ``discovery/`` holds the nine graphs of the rejected manuscript. They are the
  *discovery* set: every finding up to 26 November 2026 comes from them. This
  tool reads them and never rewrites them.
- ``small/``, ``medium/`` and ``large/`` hold every other graph of the study (the
  *confirmation* set), as ``<tier>/<class>/<name>.col``.
- ``teaching/`` and ``legacy/`` hold inputs outside the tiers; this tool ignores
  them.

Tiers. A generated structured graph (paths, cycles, wheels, Latin squares and the
other classes of ``structured()``) is *small* when its data register, |V| times
⌈log₂ k⌉ qubits, has at most ``SMALL_QUBITS`` qubits, so that the search can be
simulated exactly. Every other graph is *medium* when its proper colorings can be
counted within ``COUNT_BUDGET`` (so that the complete search can be priced
exactly), and *large* otherwise.

DIMACS instances are downloaded once from the graph-coloring collection, checked
against the recorded SHA-256 of the upstream file, given an ``x colors`` record
with their known chromatic number, and stored in their tier folder; ``--fetch``
downloads them again. Generated graphs are rebuilt from fixed seeds on every run.

An entry is reused from the previous manifest when its file has the same SHA-256,
so only new or changed graphs are counted and searched again (``--recompute``
forces everything). Every graph gets a verification witness: the planted coloring
of a planted family, or one found by ``logique.coloring.solver`` within the
witness budget. Structural columns (clique number, triangles, bipartiteness,
girth, density) describe each graph, and its ``origin`` says who made it and how:
the author named in the header of a downloaded file, or the construction and seed
of a generated one. The tool stops if two graphs are isomorphic.
It writes ``manifest.json``, ``witnesses.json`` and the index ``README.md``.
"""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, replace
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import time
import urllib.request

from logique.coloring import read_dimacs
from logique.coloring.counting import count_colorings
from logique.coloring.solver import find_coloring

ROOT = Path(__file__).resolve().parents[1]
GRAPHS = ROOT / "datasets" / "graphs"
TIERS = ("small", "medium", "large")
COUNT_BUDGET = 300_000_000  # the study's ``count_budget``
SMALL_QUBITS = 24
# Each evaluation is appended here as it finishes, so that an interrupted run
# loses no counting or search (ignored by Git).
CACHE = ROOT / ".cache" / "graph-tiers" / "evaluations.jsonl"

COLLECTION = " (DIMACS graph-coloring collection)"
MANUSCRIPT = "; a benchmark of the original manuscript"
TRICK = "Michael Trick: graph from the Mycielski transformation"
# The nine graphs of the original manuscript (the discovery set): (class, origin).
DISCOVERY = {
    "K3": ("complete", "Complete graph written for the original manuscript"),
    "K5": ("complete", "Complete graph written for the original manuscript"),
    "K10": ("complete", "Complete graph written for the original manuscript"),
    "K20": ("complete", "Complete graph written for the original manuscript"),
    "myciel3": ("mycielski", TRICK + COLLECTION + MANUSCRIPT),
    "myciel4": ("mycielski", TRICK + COLLECTION + MANUSCRIPT),
    "myciel5": ("mycielski", TRICK + COLLECTION + MANUSCRIPT),
    "2-Insertions_3": (
        "insertions",
        "M. Caramia and P. Dell'Olmo: 2-Insertions graph of order 3"
        + COLLECTION
        + MANUSCRIPT,
    ),
    "zed-city_2019": (
        "zed-city",
        "IBM Quantum Hackathon 2019: the Zed city problem of placing convenience "
        "stores in city districts, posed as vertex coloring" + MANUSCRIPT,
    ),
}

COLOR = "https://mat.tepper.cmu.edu/COLOR/instances/"
COLOR04 = "https://mat.tepper.cmu.edu/COLOR04/INSTANCES/"
# name: (class, source, chromatic number, SHA-256 of the upstream file)
DIMACS = {
    "queen5_5": (
        "queens",
        COLOR,
        5,
        "d3b770332eb3897d35a7332baece51ea7bce99150bb900f49b27eff234d8cfac",
    ),
    "queen6_6": (
        "queens",
        COLOR,
        7,
        "ab44cb3ab4c30b3b9f4b8c8afbdb87947d287af8cdb7428e0f75d17199da512c",
    ),
    "queen8_8": (
        "queens",
        COLOR,
        9,
        "1579f7e1cf2d5ab7a0bdd1682a4dad3131084dca54c4690547383dbf44731948",
    ),
    "myciel6": (
        "mycielski",
        COLOR04,
        7,
        "5bb1be3fcb0da7bada24b90fa4e1ef67a02cdbcb1aa1e69587b2a75e287f61b1",
    ),
    "myciel7": (
        "mycielski",
        COLOR,
        8,
        "8037aaba268f3da68d8278c17694db04a18dacd9fbca669660f8edb1e6010602",
    ),
    "DSJC125.1": (
        "random",
        COLOR04,
        5,
        "391a413b3eda8dc7efeedbcca75d4670c6d68e9846737941012abcb5f0782ba7",
    ),
    "le450_5a": (
        "leighton",
        COLOR,
        5,
        "a39058fbffffa5220e7c70e64403196b0be19ec859d7d29a105738bf80785490",
    ),
    "4-Insertions_3": (
        "insertions",
        COLOR04,
        4,
        "899f11fd1e31942d751ba169b2f58ed3c508d30077ec64dd8eb37df72107775a",
    ),
    "5-FullIns_3": (
        "insertions",
        COLOR04,
        8,
        "7d296a049965a194175b4975105c4a34a89415d8e03b10e4878fdf4cbbb60cec",
    ),
    "anna": (
        "book-characters",
        COLOR,
        11,
        "94907497db819e1375db6f20273cc582f2b6601bfa21e9bdf72b47d3533cf22a",
    ),
    "david": (
        "book-characters",
        COLOR,
        11,
        "8a75efd18606b87cc2f9a4e0ec87f8b8ca3e237b7ecc710a1ef2f069fe212192",
    ),
    "huck": (
        "book-characters",
        COLOR,
        11,
        "b635483fe5da294e3f35d890969d8f8b31c818e11e2b18521c2e5546fe2eb3ba",
    ),
    "jean": (
        "book-characters",
        COLOR,
        10,
        "ad92a264160d87a2a55a9e1f0f41a9f584ca11c3f3ea1f6f1a7630d495e81790",
    ),
    "games120": (
        "football-games",
        COLOR,
        9,
        "30bcc1004a11b6cbed6e96727d48e1927e74a36383d966ec04eead8b68cb38f9",
    ),
    "miles250": (
        "city-distances",
        COLOR,
        8,
        "7fea68199802d69dd76930b74bf13cdc4da48d1a0c781c8da06688ad6d639206",
    ),
}
# Three of these were used by the legacy code (commit 95f6167); their edge sets
# are checked against the legacy files when fetching.
LEGACY = {"queen8_8", "4-Insertions_3", "5-FullIns_3"}
SGB = "Stanford GraphBase (D. E. Knuth): "
JOHNSON = (
    "David Johnson: random graph with edge probability 0.1 from Johnson, Aragon, "
    "McGeoch and Schevon, Operations Research 39 (1991)"
)
LEIGHTON = (
    "Craig Morgenstern: Leighton graph (F. T. Leighton, J. Res. Natl. Bur. Stand. "
    "84, 1979) with 450 vertices and 5 colors"
)
# Who made each DIMACS instance, as its file header states.
ORIGIN = {
    "queen5_5": SGB + "5 by 5 queen graph",
    "queen6_6": SGB + "6 by 6 queen graph",
    "queen8_8": SGB + "8 by 8 queen graph",
    "myciel6": TRICK,
    "myciel7": TRICK,
    "DSJC125.1": JOHNSON,
    "le450_5a": LEIGHTON,
    "4-Insertions_3": "M. Caramia and P. Dell'Olmo: 4-Insertions graph of order 3",
    "5-FullIns_3": "M. Caramia and P. Dell'Olmo: 5-FullIns graph of order 3",
    "anna": SGB + "characters of Anna Karenina (Tolstoy)",
    "david": SGB + "characters of David Copperfield (Dickens)",
    "huck": SGB + "characters of Huckleberry Finn (Twain)",
    "jean": SGB + "characters of Les Misérables (Hugo)",
    "games120": SGB + "college football teams joined when they played",
    "miles250": SGB + "North American cities less than 250 miles apart",
}
# Instances whose witness search needs more than the default budget.
LONGER_WITNESS = {"queen8_8": 1800}

CLASSES = {
    "paths": "Paths; trees, so the edge-wise oracle has no slack.",
    "cycles": "Single cycles, even (two colors) and odd (three colors).",
    "complete": "Complete graphs.",
    "petersen": "The Petersen graph: triangle-free, three colors.",
    "wheels": "A hub joined to every vertex of a cycle; every triangle uses the hub.",
    "complete-multipartite": "Every vertex joined to every vertex of the other "
    "parts: the most triangles without larger cliques.",
    "latin-squares": "Rook's graphs: one clique per row and per column of an n by n "
    "grid; their n-colorings are the Latin squares of order n.",
    "sudoku": "Sudoku graphs: cliques for rows, columns and boxes.",
    "grids": "Square grids: bipartite with many cycles.",
    "hypercubes": "Hypercubes: bipartite and triangle-free.",
    "planar-triangulations": "Maximal planar graphs (map coloring): random vertex "
    "insertions followed by random edge flips; three colors exactly when every "
    "degree is even, four otherwise.",
    "interval-graphs": "Overlaps of random intervals (scheduling and register "
    "allocation): the chromatic number equals the clique number.",
    "planted-vertices": "Planted k-colorings with balanced classes and cross-class "
    "edges kept with probability 0.5, varying the number of vertices.",
    "planted-density": "Planted 3-colorings of 16 vertices, varying the cross-class "
    "edge probability (0.5 is planted_n16_k3_p50 in planted-vertices).",
    "planted-colors": "Planted k-colorings of 24 vertices with a planted k-clique, "
    "so that the chromatic number is exactly k, for every k from 2 to 20.",
    "queens": "Queen graphs (DIMACS): cliques along rows, columns and diagonals.",
    "mycielski": "Mycielski graphs (DIMACS): triangle-free with growing chromatic "
    "number.",
    "random": "Random graph DSJC125.1 (DIMACS): edge probability 0.1.",
    "leighton": "Leighton graph le450_5a (DIMACS): planted cliques, known "
    "chromatic number.",
    "insertions": "Insertion graphs (DIMACS): Mycielski-like constructions.",
    "book-characters": "Characters of a novel joined when they appear together "
    "(Stanford GraphBase, DIMACS).",
    "football-games": "College football teams joined when they played "
    "(Stanford GraphBase, DIMACS).",
    "city-distances": "North American cities joined when closer than 250 miles "
    "(Stanford GraphBase, DIMACS).",
    "zed-city": "The Zed city problem of the IBM Quantum Hackathon 2019, posed as "
    "vertex coloring.",
}


@dataclass
class Spec:
    """One graph of the catalog, before its tier is known."""

    name: str
    cls: str
    text: str
    source: dict
    structured: bool = False
    coloring: dict | None = None
    stored: Path | None = None  # existing file (the discovery graphs)
    also_in: list = field(default_factory=list)
    origin: str = ""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def col_text(n: int, edges, colors: int, comment: str) -> str:
    lines = [f"c {comment}", f"p edge {n} {len(edges)}"]
    lines += [f"e {a} {b}" for a, b in edges]
    lines.append(f"x colors {colors}")
    return "\n".join(lines) + "\n"


def bits(colors: int) -> int:
    return max(1, (colors - 1).bit_length())


# Structured classes -------------------------------------------------------


def latin_square(n: int):
    cell = {(i, j): i * n + j + 1 for i in range(n) for j in range(n)}
    edges = [
        (cell[a], cell[b])
        for a, b in itertools.combinations(sorted(cell), 2)
        if a[0] == b[0] or a[1] == b[1]
    ]
    return n * n, edges


def sudoku(box: int):
    side = box * box
    cell = {(r, c): r * side + c + 1 for r in range(side) for c in range(side)}

    def joined(a, b):
        same_box = (a[0] // box, a[1] // box) == (b[0] // box, b[1] // box)
        return a[0] == b[0] or a[1] == b[1] or same_box

    edges = [
        (cell[a], cell[b])
        for a, b in itertools.combinations(sorted(cell), 2)
        if joined(a, b)
    ]
    return side * side, edges


def multipartite(parts):
    part = [i for i, size in enumerate(parts) for _ in range(size)]
    edges = [
        (a + 1, b + 1)
        for a, b in itertools.combinations(range(len(part)), 2)
        if part[a] != part[b]
    ]
    return len(part), edges


def wheel(rim: int):
    edges = [(i, i % rim + 1) for i in range(1, rim + 1)]
    edges += [(i, rim + 1) for i in range(1, rim + 1)]
    return rim + 1, [tuple(sorted(e)) for e in edges]


def grid(side: int):
    cell = {(r, c): r * side + c + 1 for r in range(side) for c in range(side)}
    edges = [(cell[r, c], cell[r, c + 1]) for r in range(side) for c in range(side - 1)]
    edges += [
        (cell[r, c], cell[r + 1, c]) for r in range(side - 1) for c in range(side)
    ]
    return side * side, sorted(edges)


def hypercube(dimension: int):
    n = 2**dimension
    edges = [
        (a + 1, b + 1)
        for a, b in itertools.combinations(range(n), 2)
        if bin(a ^ b).count("1") == 1
    ]
    return n, edges


def planar_triangulation(n: int, seed: int):
    """Random vertex insertions into faces, then random edge flips (a sphere)."""
    rng = random.Random(seed)
    faces = [(1, 2, 3), (1, 2, 3)]  # the two sides of the first triangle
    for v in range(4, n + 1):
        a, b, c = faces.pop(rng.randrange(len(faces)))
        faces += [(a, b, v), (b, c, v), (c, a, v)]
    edges = {frozenset(e) for f in faces for e in itertools.combinations(f, 2)}

    def degree(v):
        return sum(1 for e in edges if v in e)

    for _ in range(4 * n):
        f = rng.randrange(len(faces))
        u, w = rng.sample(faces[f], 2)
        (x,) = set(faces[f]) - {u, w}
        others = [g for g, face in enumerate(faces) if g != f and {u, w} <= set(face)]
        (g,) = others
        (y,) = set(faces[g]) - {u, w}
        if x == y or frozenset((x, y)) in edges or min(degree(u), degree(w)) <= 3:
            continue
        edges.remove(frozenset((u, w)))
        edges.add(frozenset((x, y)))
        faces[f], faces[g] = (x, y, u), (x, y, w)
    result = sorted(tuple(sorted(e)) for e in edges)
    assert len(result) == 3 * n - 6
    degrees = Counter(v for e in result for v in e)
    colors = 3 if all(d % 2 == 0 for d in degrees.values()) else 4
    return n, result, colors


def interval_graph(n: int, seed: int):
    rng = random.Random(seed)
    spans = []
    for _ in range(n):
        start = rng.random()
        spans.append((start, start + rng.uniform(0.05, 0.25)))
    edges = [
        (i + 1, j + 1)
        for i, j in itertools.combinations(range(n), 2)
        if spans[i][0] < spans[j][1] and spans[j][0] < spans[i][1]
    ]
    clique = max(sum(1 for a, b in spans if a <= s < b) for s, _ in spans)
    return n, edges, max(2, clique)


def structured() -> list[Spec]:
    """Small structured graphs and their larger relatives (fixed constructions)."""
    graphs: list[tuple[str, str, int, list, int, str]] = []

    def add(name, cls, n, edges, colors, description):
        graphs.append((name, cls, n, sorted(edges), colors, description))

    for n in range(3, 9):
        add(f"P{n}", "paths", n, [(i, i + 1) for i in range(1, n)], 2, "path")
    add("P4_k3", "paths", 4, [(1, 2), (2, 3), (3, 4)], 3, "path with three colors")
    for n in range(4, 8):
        cycle = [(i, i + 1) for i in range(1, n)] + [(1, n)]
        add(f"C{n}", "cycles", n, cycle, 2 if n % 2 == 0 else 3, "cycle")
    add("K4", "complete", 4, list(itertools.combinations(range(1, 5), 2)), 4, "K4")
    outer = [(i, i % 5 + 1) for i in range(1, 6)]
    spokes = [(i, i + 5) for i in range(1, 6)]
    inner = [(6 + i, 6 + (i + 2) % 5) for i in range(5)]
    add("petersen", "petersen", 10, outer + spokes + inner, 3, "Petersen graph")
    for rim in range(5, 9):
        n, edges = wheel(rim)
        add(f"wheel_{rim}", "wheels", n, edges, 4 if rim % 2 else 3, "wheel")
    for parts in ((2, 2, 2), (3, 3, 3), (2, 2, 2, 2), (2, 2, 2, 2, 2)):
        n, edges = multipartite(parts)
        name = "multipartite_" + "_".join(map(str, parts))
        add(
            name, "complete-multipartite", n, edges, len(parts), "complete multipartite"
        )
    for order in range(3, 7):
        n, edges = latin_square(order)
        add(f"latin_square_{order}", "latin-squares", n, edges, order, "rook's graph")
    for box in (2, 3):
        n, edges = sudoku(box)
        side = box * box
        add(f"sudoku_{side}x{side}", "sudoku", n, edges, side, "Sudoku graph")
    for side in (3, 4, 5):
        n, edges = grid(side)
        add(f"grid_{side}x{side}", "grids", n, edges, 2, "square grid")
    for dimension in (3, 4):
        n, edges = hypercube(dimension)
        add(f"hypercube_{dimension}", "hypercubes", n, edges, 2, "hypercube")
    for size in (10, 16, 24, 32):
        seed = 5_000_000 + size
        n, edges, colors = planar_triangulation(size, seed)
        add(
            f"planar_n{size}",
            "planar-triangulations",
            n,
            edges,
            colors,
            f"planar triangulation, seed {seed}",
        )
    for size in (12, 20, 32, 48):
        seed = 6_000_000 + size
        n, edges, colors = interval_graph(size, seed)
        add(
            f"interval_n{size}",
            "interval-graphs",
            n,
            edges,
            colors,
            f"interval graph, seed {seed}",
        )
    return [
        Spec(
            name,
            cls,
            col_text(n, edges, colors, f"{name}: {description}, generated"),
            {"source": "generated"},
            structured=True,
            origin="Generated by tools/build_graph_tiers.py: "
            + construction(name, cls, n, colors, description),
        )
        for name, cls, n, edges, colors, description in graphs
    ]


def construction(name: str, cls: str, n: int, colors: int, description: str) -> str:
    """A precise phrase for the origin of a structured graph."""
    seed = description.split(", ")[-1]  # "seed N" for the random constructions
    phrases = {
        "paths": f"path on {n} vertices with {colors} colors",
        "cycles": f"cycle on {n} vertices with {colors} colors",
        "complete": f"complete graph on {n} vertices",
        "petersen": "the Petersen graph, 10 vertices with 3 colors",
        "wheels": f"wheel: a hub joined to a cycle of {n - 1} vertices, "
        f"{colors} colors",
        "complete-multipartite": "complete multipartite graph with parts of sizes "
        + ", ".join(name.split("_")[1:]),
        "latin-squares": f"rook's graph of a {colors} by {colors} board, whose "
        f"{colors}-colorings are the Latin squares of order {colors}",
        "sudoku": f"{colors} by {colors} Sudoku graph",
        "grids": f"{round(n ** 0.5)} by {round(n ** 0.5)} square grid with 2 colors",
        "hypercubes": f"{n.bit_length() - 1}-dimensional hypercube with 2 colors",
        "planar-triangulations": f"random planar triangulation on {n} vertices "
        f"(vertex insertions, then edge flips), {seed}",
        "interval-graphs": f"random interval graph on {n} vertices, {seed}",
    }
    return phrases[cls]


# Planted families ---------------------------------------------------------


def planted(n: int, k: int, p: float, seed: int, clique: bool = False):
    """Balanced planted k-coloring; cross-class pairs kept with probability p."""
    rng = random.Random(seed)
    coloring = {v: (v - 1) % k for v in range(1, n + 1)}
    edges = [
        (a, b)
        for a, b in itertools.combinations(range(1, n + 1), 2)
        if coloring[a] != coloring[b] and rng.random() < p
    ]
    if clique:  # vertices 1..k carry the k different colors
        edges = sorted(set(edges) | set(itertools.combinations(range(1, k + 1), 2)))
    return edges, coloring


def families() -> list[Spec]:
    specs = []
    for k in (3, 4):
        for n in (6, 8, 10, 12, 16, 20, 24, 32, 48, 64, 96, 128):
            specs.append(("planted-vertices", n, k, 0.5, False))
    for p in (0.1, 0.2, 0.3, 0.7, 0.9):
        specs.append(("planted-density", 16, 3, p, False))
    for k in range(2, 21):
        specs.append(("planted-colors", 24, k, 0.5, True))
    graphs = []
    for cls, n, k, p, clique in specs:
        if clique:
            seed = 7_000_000 + 1000 * k + n
            name = f"planted_n{n}_k{k}_p{round(100 * p):02d}_clique"
            comment = (
                f"{name}: planted {k}-coloring with a planted {k}-clique, "
                f"cross-class edge probability {p}, seed {seed}"
            )
        else:
            seed = 1_000_000 * k + 1000 * n + round(100 * p)
            name = f"planted_n{n}_k{k}_p{round(100 * p):02d}"
            comment = (
                f"{name}: planted {k}-coloring, cross-class edge probability {p}, "
                f"seed {seed}"
            )
        edges, coloring = planted(n, k, p, seed, clique)
        source = {"source": "generated", "family": cls, "density": p, "seed": seed}
        graphs.append(
            Spec(
                name,
                cls,
                col_text(n, edges, k, comment),
                source,
                coloring=coloring,
                origin="Generated by tools/build_graph_tiers.py: planted "
                f"{k}-coloring of {n} vertices"
                + (f" with a planted {k}-clique" if clique else "")
                + f", cross-class edge probability {p}, seed {seed}",
            )
        )
    for spec in graphs:
        if spec.name == "planted_n16_k3_p50":
            spec.also_in = ["planted-density"]
    return graphs


# Manuscript and DIMACS ----------------------------------------------------


def discovery() -> list[Spec]:
    specs = []
    for name, (cls, origin) in DISCOVERY.items():
        path = GRAPHS / "discovery" / f"{name}.col"
        specs.append(
            Spec(
                name,
                cls,
                path.read_bytes().decode(),
                {"source": "original manuscript"},
                stored=path,
                origin=origin,
            )
        )
    return specs


def edge_set(text: str) -> set:
    return {
        frozenset(map(int, line.split()[1:3]))
        for line in text.splitlines()
        if line.startswith("e ")
    }


def fetch(name: str) -> str:
    _, base, chromatic, expected = DIMACS[name]
    for attempt in range(5):  # the collection's server resets connections at times
        try:
            with urllib.request.urlopen(base + name + ".col", timeout=60) as response:
                data = response.read()
            break
        except OSError:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    if sha256(data) != expected:
        raise RuntimeError(f"{name}: upstream file changed")
    text = data.decode()
    if name in LEGACY:
        legacy = subprocess.check_output(
            ["git", "show", f"95f6167:data/big_benchmarks/{name}.col"],
            cwd=ROOT,
            text=True,
        )
        if edge_set(legacy) != edge_set(text):
            raise RuntimeError(f"{name}: differs from the legacy instance")
    if not text.endswith("\n"):
        text += "\n"
    return (
        text + "c Logique: known chromatic number recorded as the color count.\n"
        f"x colors {chromatic}\n"
    )


def stored_files() -> dict[str, Path]:
    found = {}
    for tier in TIERS:
        for path in (GRAPHS / tier).glob("*/*.col"):
            found[path.stem] = path
    for old in ("dimacs", "small", "families"):  # layout before 26 November 2026
        for path in (GRAPHS / old).glob("*.col"):
            found.setdefault(path.stem, path)
    return found


def dimacs(refetch: bool) -> list[Spec]:
    stored = stored_files()
    specs = []
    for name, (cls, base, chromatic, _) in DIMACS.items():
        text = None
        if name in stored and not refetch:
            text = stored[name].read_bytes().decode()
        if text is None:
            print(f"fetching {name}", flush=True)
            text = fetch(name)
        source = {"source": base + name + ".col", "chromatic_number": chromatic}
        if name in LEGACY:
            source["legacy"] = "same edges as legacy/vcgc commit 95f6167"
        origin = ORIGIN[name] + COLLECTION
        specs.append(Spec(name, cls, text, source, origin=origin))
    return specs


# Evaluation ---------------------------------------------------------------


def parse(text: str):
    with tempfile.NamedTemporaryFile("w", suffix=".col", delete=False) as handle:
        handle.write(text)
    try:
        return read_dimacs(handle.name)
    finally:
        Path(handle.name).unlink()


def structure(problem) -> dict:
    adj = defaultdict(set)
    for a, b in problem.edges:
        adj[a].add(b)
        adj[b].add(a)
    n, m = len(problem.vertices), len(problem.edges)
    triangles = sum(
        1 for a in adj for b in adj[a] if b > a for c in adj[a] & adj[b] if c > b
    )
    best = 1 if n else 0

    def expand(size, candidates, excluded):
        nonlocal best
        if not candidates and not excluded:
            best = max(best, size)
            return
        if size + len(candidates) <= best:
            return
        pivot = max(candidates | excluded, key=lambda v: len(adj[v] & candidates))
        for v in list(candidates - adj[pivot]):
            expand(size + 1, candidates & adj[v], excluded & adj[v])
            candidates = candidates - {v}
            excluded = excluded | {v}

    if m:
        expand(0, set(adj), set())
    side: dict[int, int] = {}
    bipartite = True
    for start in adj:
        if start in side:
            continue
        side[start], stack = 0, [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in side:
                    side[w] = 1 - side[u]
                    stack.append(w)
                elif side[w] == side[u]:
                    bipartite = False
    girth = None
    for start in adj:  # shortest cycle through BFS from every vertex
        distance, parent, queue = {start: 0}, {start: None}, [start]
        for u in queue:
            for w in adj[u]:
                if w not in distance:
                    distance[w], parent[w] = distance[u] + 1, u
                    queue.append(w)
                elif parent[u] != w:
                    cycle = distance[u] + distance[w] + 1
                    girth = cycle if girth is None else min(girth, cycle)
    return {
        "density": round(2 * m / (n * (n - 1)), 4) if n > 1 else 0.0,
        "max_degree": max((len(s) for s in adj.values()), default=0),
        "clique_number": best,
        "triangles": triangles,
        "bipartite": bipartite,
        "girth": girth,
    }


def evaluate(spec: Spec, previous: dict | None, witness: dict | None, budget: float):
    """The manifest entry and witness of one graph (runs in a worker process)."""
    problem = parse(spec.text)
    entry = {"name": spec.name, "class": spec.cls, **spec.source}
    if problem.precolored:
        # Every graph is used without precolors, as the study does (``drop_precolors``).
        entry["precolors_dropped"] = len(problem.precolored)
        problem = replace(problem, precolored={})
    k = problem.colors
    entry.update(
        {
            "vertices": len(problem.vertices),
            "edges": len(problem.edges),
            "colors": k,
            "data_qubits": len(problem.vertices) * bits(k),
            **structure(problem),
        }
    )
    reuse = previous is not None and previous.get("colorings") is not None
    reuse = reuse or (previous is not None and previous.get("tier") == "large")
    if reuse:
        count, count_s = previous["colorings"], previous.get("count_cpu_s", 0.0)
    else:
        started = time.process_time()
        count = count_colorings(problem, budget=COUNT_BUDGET)
        count_s = round(time.process_time() - started, 3)
    if spec.structured and entry["data_qubits"] <= SMALL_QUBITS:
        tier = "small"
    else:
        tier = "medium" if count is not None else "large"
    entry.update({"tier": tier, "colorings": count, "count_cpu_s": count_s})
    if spec.coloring is not None:
        coloring, entry["witness"] = spec.coloring, "planted"
    elif witness is not None:
        coloring = {int(v): c for v, c in witness.items()}
        entry["witness"] = previous.get("witness", "found") if previous else "found"
        entry["witness_cpu_s"] = previous.get("witness_cpu_s") if previous else None
    else:
        started = time.process_time()
        status, coloring = find_coloring(
            problem, budget_s=max(budget, LONGER_WITNESS.get(spec.name, 0))
        )
        entry["witness"] = status
        entry["witness_cpu_s"] = round(time.process_time() - started, 3)
    if coloring is not None:
        assert problem.is_valid(coloring), spec.name
    return entry, coloring


def check_duplicates(specs: list[Spec]) -> None:
    """Stop before any counting if two graphs with the same color count are isomorphic.

    The same graph with different color counts is a different coloring problem (for
    example P4 with two and with three colors), so only equal color counts compare.
    """
    problems = {spec.name: parse(spec.text) for spec in specs}
    groups = defaultdict(list)
    for name, problem in problems.items():
        degrees = Counter(v for e in problem.edges for v in e)
        key = (
            problem.colors,
            len(problem.vertices),
            len(problem.edges),
            tuple(sorted(degrees.values())),
        )
        groups[key].append(name)
    try:
        import rustworkx
    except ImportError:  # invariants only
        rustworkx = None

    def graph(problem):
        g = rustworkx.PyGraph()
        index = {v: g.add_node(v) for v in problem.vertices}
        g.add_edges_from_no_data([(index[x], index[y]) for x, y in problem.edges])
        return g

    duplicates = []
    for group in groups.values():
        for a, b in itertools.combinations(group, 2):
            if rustworkx is None or rustworkx.is_isomorphic(
                graph(problems[a]), graph(problems[b])
            ):
                duplicates.append((a, b))
    if duplicates:
        raise SystemExit(f"isomorphic graphs in the catalog: {duplicates}")


# Output -------------------------------------------------------------------


def index(entries: list[dict]) -> str:
    """The README of datasets/graphs, generated from the manifest."""
    lines = [
        "# Graphs",
        "",
        "Generated by `tools/build_graph_tiers.py`; do not edit by hand. The manifest",
        "(`manifest.json`) holds every column below and more for each graph, and",
        "`witnesses.json` holds one proper coloring per graph.",
        "",
        "## Layout",
        "",
        "| Folder | What it holds |",
        "| --- | --- |",
        "| `discovery/` | The nine graphs of the rejected manuscript: the **discovery "
        "set**, on which every finding up to 26 November 2026 was made. Their tiers "
        "are listed below. |",
        "| `small/<class>/` | **Small tier**: structured graphs whose data register "
        f"has at most {SMALL_QUBITS} qubits, simulated exactly. |",
        "| `medium/<class>/` | **Medium tier**: graphs whose colorings can be counted "
        "within the study's budget, so the complete search is priced exactly. |",
        "| `large/<class>/` | **Large tier**: graphs whose colorings cannot be "
        "counted; compared per Grover iteration. |",
        "| `teaching/` | Tutorial inputs and the format template (`template.col`). |",
        "| `legacy/` | Historical and development inputs outside the study. |",
        "",
        "Every graph outside `discovery/` belongs to the **confirmation set**. Each "
        "file records its color count k in an `x colors` line. ω is the clique "
        "number: when ω = k, k colors are necessary, so k is the chromatic number.",
        "",
        "## Classes",
        "",
        "| Class | Description |",
        "| --- | --- |",
    ]
    used = sorted({e["class"] for e in entries}, key=list(CLASSES).index)
    lines += [f"| {cls} | {CLASSES[cls]} |" for cls in used]
    header = [
        "| Graph | Class | Vertices | Edges | k | ω | Triangles | Colorings | "
        "Witness | Origin |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def row(e):
        count = "—" if e["colorings"] is None else f"{e['colorings']:,}"
        origin = e["origin"]
        if str(e.get("source", "")).startswith("https://"):
            origin += f" ([file]({e['source']}))"
        return (
            f"| {e['name']} | {e['class']} | {e['vertices']} | {e['edges']} | "
            f"{e['colors']} | {e['clique_number']} | {e['triangles']:,} | {count} | "
            f"{e['witness']} | {origin} |"
        )

    groups = [("Discovery set (`discovery/`)", "discovery", None)]
    groups += [
        (f"{tier.capitalize()} tier (`{tier}/`)", "confirmation", tier)
        for tier in TIERS
    ]
    for title, split, tier in groups:
        chosen = [
            e
            for e in entries
            if e["split"] == split and (tier is None or e["tier"] == tier)
        ]
        lines += ["", f"## {title}", ""]
        counts = Counter(e["tier"] if tier is None else e["class"] for e in chosen)
        summary = ", ".join(f"{n} {label}" for label, n in counts.items())
        lines += [f"{len(chosen)} graphs: {summary}.", ""] + header
        lines += [row(e) for e in chosen]
    lines += [
        "",
        "## Sources",
        "",
        "- **Generated graphs** (structured classes and planted families) are built by "
        "`tools/build_graph_tiers.py` from the construction and seed given in their "
        "origin and in the first line of each file.",
        "- **DIMACS graph-coloring collection** (maintained by Michael Trick): "
        "[COLOR](https://mat.tepper.cmu.edu/COLOR/instances.html) and "
        "[COLOR02/03/04](https://mat.tepper.cmu.edu/COLOR04/). Each downloaded file "
        "keeps its original header, which names its author, and is checked against the "
        "SHA-256 recorded in the tool.",
        "- **Stanford GraphBase**: D. E. Knuth, *The Stanford GraphBase: A Platform for "
        "Combinatorial Computing*, Addison-Wesley, 1993. The queen, book, football and "
        "city-distance graphs come from it through the DIMACS collection.",
        "- **Original manuscript**: the complete graphs were written for it; the other "
        "discovery graphs come from the sources named in their origin.",
    ]
    return "\n".join(lines) + "\n"


def order(entry: dict) -> tuple:
    return (
        entry["split"] != "discovery",
        TIERS.index(entry["tier"]),
        list(CLASSES).index(entry["class"]),
        entry["vertices"],
        entry["name"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--recompute", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--witness-budget", type=float, default=120.0)
    args = parser.parse_args()

    specs = discovery() + dimacs(args.fetch) + structured() + families()
    names = Counter(spec.name for spec in specs)
    assert max(names.values()) == 1, [n for n, c in names.items() if c > 1]
    check_duplicates(specs)

    previous: dict[str, dict] = {}
    witnesses: dict[str, dict] = {}
    for manifest in (GRAPHS / "manifest.json", GRAPHS / "tiers.json"):
        if manifest.exists() and not args.recompute:
            for e in json.loads(manifest.read_text())["graphs"]:
                previous.setdefault(e["name"], e)
    if (GRAPHS / "witnesses.json").exists() and not args.recompute:
        witnesses = json.loads((GRAPHS / "witnesses.json").read_text())

    def prior(spec):
        e = previous.get(spec.name)
        if e is None or e.get("sha256") != sha256(spec.text.encode()):
            return None, None
        return e, witnesses.get(spec.name)

    cached: dict[tuple, tuple] = {}
    if CACHE.exists() and not args.recompute:
        for line in CACHE.read_text().splitlines():
            record = json.loads(line)
            key = (record["name"], record["sha256"], record["count_budget"])
            coloring = record["coloring"]
            if coloring is not None:
                coloring = {int(v): c for v, c in coloring.items()}
            cached[key] = (record["entry"], coloring)
    CACHE.parent.mkdir(parents=True, exist_ok=True)

    entries: dict[str, dict] = {}
    found: dict[str, dict] = {}
    pending = []
    for spec in specs:
        key = (spec.name, sha256(spec.text.encode()), COUNT_BUDGET)
        if key in cached:
            entries[spec.name], found[spec.name] = cached[key]
        else:
            pending.append(spec)
    print(f"{len(specs) - len(pending)} graphs cached, {len(pending)} to evaluate")
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = {
            pool.submit(evaluate, spec, *prior(spec), args.witness_budget): spec
            for spec in pending
        }
        for future in as_completed(futures):
            spec = futures[future]
            entry, coloring = future.result()
            entries[spec.name], found[spec.name] = entry, coloring
            record = {
                "name": spec.name,
                "sha256": sha256(spec.text.encode()),
                "count_budget": COUNT_BUDGET,
                "entry": entry,
                "coloring": coloring,
            }
            with CACHE.open("a") as handle:
                handle.write(json.dumps(record) + "\n")
            print(f"{spec.name:30} {entry['tier']:7} {entry['witness']}", flush=True)

    written = set()
    for spec in specs:
        entry = entries[spec.name]
        entry.pop("source", None)
        entry.update({"class": spec.cls, **spec.source, "origin": spec.origin})
        if spec.stored is not None:
            path = spec.stored
            entry["split"] = "discovery"
        else:
            path = GRAPHS / entry["tier"] / spec.cls / f"{spec.name}.col"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(spec.text.encode())
            entry["split"] = "confirmation"
        written.add(path.resolve())
        entry["path"] = str(path.relative_to(ROOT))
        entry["sha256"] = sha256(path.read_bytes())
        if spec.also_in:
            entry["also_in"] = spec.also_in
    for folder in [*TIERS, "dimacs", "small", "families"]:
        for path in (GRAPHS / folder).rglob("*.col"):
            if path.resolve() not in written:
                path.unlink()
        for directory in sorted((GRAPHS / folder).rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        if (GRAPHS / folder).is_dir() and not any((GRAPHS / folder).iterdir()):
            (GRAPHS / folder).rmdir()

    keys = ["name", "path", "sha256", "split", "tier", "class", "origin"]
    ordered = []
    for e in sorted(entries.values(), key=order):
        ordered.append({**{k: e[k] for k in keys}, **e})
    manifest = {
        "description": "Graphs of the study: the discovery set (manuscript/) and the "
        "confirmation set by tier and class. Written by tools/build_graph_tiers.py.",
        "count_budget": COUNT_BUDGET,
        "small_qubits": SMALL_QUBITS,
        "witness_budget_s": args.witness_budget,
        "graphs": ordered,
    }
    (GRAPHS / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (GRAPHS / "tiers.json").unlink(missing_ok=True)
    coloring_of = {
        e["name"]: {str(v): c for v, c in sorted(found[e["name"]].items())}
        for e in ordered
        if found[e["name"]] is not None
    }
    (GRAPHS / "witnesses.json").write_text(json.dumps(coloring_of) + "\n")
    (GRAPHS / "README.md").write_text(index(ordered))
    print(Counter((e["split"], e["tier"]) for e in ordered))


if __name__ == "__main__":
    main()
