"""Acquire and generate the graphs of the three tiers, and write their manifest.

Usage (from the checkout):

    uv run --no-sync python tools/build_graph_tiers.py [--fetch] [--witness-budget 120]

``--fetch`` downloads the DIMACS instances listed below into
``datasets/graphs/dimacs/``, checks them against the recorded SHA-256 of the
upstream file, and appends an ``x colors`` record with the known chromatic
number. Without it, the stored files are used. The small graphs and the planted
families are generated deterministically. Each graph is then classified by what
can be computed for it: *small* graphs are listed by name, *medium* graphs have
colorings that can be counted within the study's budget, and *large* graphs
cannot be counted. Graphs without a known coloring get one from the exact search
in ``logique.coloring.solver`` within the witness budget; planted families carry
their planted coloring. The manifest goes to ``datasets/graphs/tiers.json`` and
the witnesses to ``datasets/graphs/witnesses.json``.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from dataclasses import replace
import random
import subprocess
import time
import urllib.request

from logique.coloring import read_dimacs
from logique.coloring.counting import count_colorings
from logique.coloring.solver import find_coloring

ROOT = Path(__file__).resolve().parents[1]
GRAPHS = ROOT / "datasets" / "graphs"
COUNT_BUDGET = 300_000_000  # the study's ``count_budget``

COLOR = "https://mat.tepper.cmu.edu/COLOR/instances/"
COLOR04 = "https://mat.tepper.cmu.edu/COLOR04/INSTANCES/"
# name: (source, chromatic number, SHA-256 of the upstream file)
DIMACS = {
    "queen5_5": (
        COLOR,
        5,
        "d3b770332eb3897d35a7332baece51ea7bce99150bb900f49b27eff234d8cfac",
    ),
    "queen6_6": (
        COLOR,
        7,
        "ab44cb3ab4c30b3b9f4b8c8afbdb87947d287af8cdb7428e0f75d17199da512c",
    ),
    "queen8_8": (
        COLOR,
        9,
        "1579f7e1cf2d5ab7a0bdd1682a4dad3131084dca54c4690547383dbf44731948",
    ),
    "myciel6": (
        COLOR04,
        7,
        "5bb1be3fcb0da7bada24b90fa4e1ef67a02cdbcb1aa1e69587b2a75e287f61b1",
    ),
    "myciel7": (
        COLOR,
        8,
        "8037aaba268f3da68d8278c17694db04a18dacd9fbca669660f8edb1e6010602",
    ),
    "DSJC125.1": (
        COLOR04,
        5,
        "391a413b3eda8dc7efeedbcca75d4670c6d68e9846737941012abcb5f0782ba7",
    ),
    "le450_5a": (
        COLOR,
        5,
        "a39058fbffffa5220e7c70e64403196b0be19ec859d7d29a105738bf80785490",
    ),
    "4-Insertions_3": (
        COLOR04,
        4,
        "899f11fd1e31942d751ba169b2f58ed3c508d30077ec64dd8eb37df72107775a",
    ),
    "5-FullIns_3": (
        COLOR04,
        8,
        "7d296a049965a194175b4975105c4a34a89415d8e03b10e4878fdf4cbbb60cec",
    ),
}
# Three of these were used by the legacy code (commit 95f6167); their edge sets
# are checked against the legacy files when fetching.
LEGACY = {"queen8_8", "4-Insertions_3", "5-FullIns_3"}
# Instances whose witness search needs more than the default budget.
LONGER_WITNESS = {"queen8_8": 1800}
PAPER = ["K3", "K5", "K10", "K20", "myciel3", "myciel4", "myciel5"]
PAPER += ["2-Insertions_3", "zed-city_2019"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def edge_set(text: str) -> set:
    return {
        frozenset(map(int, line.split()[1:3]))
        for line in text.splitlines()
        if line.startswith("e ")
    }


def fetch(name: str) -> None:
    base, chromatic, expected = DIMACS[name]
    for attempt in range(5):  # the collection's server resets connections at times
        try:
            with urllib.request.urlopen(base + name + ".col", timeout=60) as response:
                data = response.read()
            break
        except OSError:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    if expected and sha256(data) != expected:
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
    text += f"c Logique: known chromatic number recorded as the color count.\nx colors {chromatic}\n"
    (GRAPHS / "dimacs" / f"{name}.col").write_text(text)


def write_col(path: Path, n: int, edges, colors: int, comment: str) -> None:
    lines = [f"c {comment}", f"p edge {n} {len(edges)}"]
    lines += [f"e {a} {b}" for a, b in edges]
    lines.append(f"x colors {colors}")
    path.write_text("\n".join(lines) + "\n")


def small_graphs() -> dict:
    """Paths, cycles, complete graphs and the Petersen graph (Section 3)."""
    graphs = {}
    for n in range(3, 9):
        graphs[f"P{n}"] = (n, [(i, i + 1) for i in range(1, n)], 2)
    graphs["P4_k3"] = (4, [(1, 2), (2, 3), (3, 4)], 3)
    for n in range(4, 8):
        cycle = [(i, i + 1) for i in range(1, n)] + [(1, n)]
        graphs[f"C{n}"] = (n, cycle, 2 if n % 2 == 0 else 3)
    for n in range(3, 6):
        graphs[f"K{n}"] = (n, list(itertools.combinations(range(1, n + 1), 2)), n)
    outer = [(i, i % 5 + 1) for i in range(1, 6)]
    spokes = [(i, i + 5) for i in range(1, 6)]
    inner = [(6 + i, 6 + (i + 2) % 5) for i in range(5)]
    graphs["petersen"] = (10, outer + spokes + inner, 3)
    return graphs


def planted(n: int, k: int, p: float, seed: int):
    """A graph with a planted k-coloring: balanced classes, cross pairs kept with p."""
    rng = random.Random(seed)
    coloring = {v: (v - 1) % k for v in range(1, n + 1)}
    edges = [
        (a, b)
        for a, b in itertools.combinations(range(1, n + 1), 2)
        if coloring[a] != coloring[b] and rng.random() < p
    ]
    return edges, coloring


def families() -> dict:
    """Controlled families: vary one of vertices, density and colors at a time."""
    specs = []
    for k in (3, 4):
        specs += [("vertices", n, k, 0.5) for n in (6, 8, 10, 12, 16, 20, 24, 32, 48)]
        specs += [("vertices", n, k, 0.5) for n in (64, 96, 128)]
    specs += [("density", 16, 3, p) for p in (0.1, 0.2, 0.3, 0.5, 0.7, 0.9)]
    specs += [("colors", 24, k, 0.5) for k in (2, 3, 4, 5, 6, 7, 8, 9, 12, 16)]
    graphs = {}
    for family, n, k, p in specs:
        seed = 1_000_000 * k + 1000 * n + round(100 * p)
        name = f"planted_n{n}_k{k}_p{round(100 * p):02d}"
        edges, coloring = planted(n, k, p, seed)
        graphs[name] = (family, n, k, p, seed, edges, coloring)
    return graphs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--witness-budget", type=float, default=120.0)
    args = parser.parse_args()
    for folder in ("dimacs", "small", "families"):
        (GRAPHS / folder).mkdir(exist_ok=True)
    if args.fetch:
        for name in DIMACS:
            fetch(name)

    entries, witnesses = [], {}

    def add(path: Path, source: dict, tier: str | None, coloring=None) -> None:
        problem = read_dimacs(path)
        if problem.precolored:
            # The protocol uses every graph without precolors, as the study does
            # (``drop_precolors``).
            source = {**source, "precolors_dropped": len(problem.precolored)}
            problem = replace(problem, precolored={})
        started = time.process_time()
        count = (
            None if tier == "small" else count_colorings(problem, budget=COUNT_BUDGET)
        )
        count_s = time.process_time() - started
        if tier is None:
            tier = "medium" if count is not None else "large"
        entry = {
            "name": path.stem,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path.read_bytes()),
            "tier": tier,
            "vertices": len(problem.vertices),
            "edges": len(problem.edges),
            "colors": problem.colors,
            **source,
            "colorings": count,
            "count_cpu_s": round(count_s, 3),
        }
        if coloring is not None:
            entry["witness"] = "planted"
        elif tier != "small":
            started = time.process_time()
            budget = max(args.witness_budget, LONGER_WITNESS.get(path.stem, 0))
            status, coloring = find_coloring(problem, budget_s=budget)
            entry["witness"] = status
            entry["witness_cpu_s"] = round(time.process_time() - started, 3)
        if coloring is not None:
            assert problem.is_valid(coloring), path
            witnesses[path.stem] = {str(v): c for v, c in sorted(coloring.items())}
        entries.append(entry)
        print(f"{path.stem:24} {tier:7} {entry.get('witness', '-')}", flush=True)

    for name, (n, edges, k) in small_graphs().items():
        path = GRAPHS / "small" / f"{name}.col"
        write_col(path, n, edges, k, f"{name}: small tier, generated")
        add(path, {"source": "generated"}, "small")
    for name in PAPER:
        add(
            GRAPHS / "benchmarks" / f"{name}.col",
            {"source": "manuscript benchmark"},
            None,
        )
    for name, (base, chromatic, _) in DIMACS.items():
        path = GRAPHS / "dimacs" / f"{name}.col"
        source = {"source": base + name + ".col", "chromatic_number": chromatic}
        if name in LEGACY:
            source["legacy"] = "same edges as legacy/vcgc commit 95f6167"
        add(path, source, None)
    for name, (family, n, k, p, seed, edges, coloring) in families().items():
        path = GRAPHS / "families" / f"{name}.col"
        comment = f"{name}: planted {k}-coloring, cross-class edge probability {p}, seed {seed}"
        write_col(path, n, edges, k, comment)
        source = {"source": "generated", "family": family, "density": p, "seed": seed}
        add(path, source, None, coloring)

    manifest = {
        "description": "Graphs of the three tiers (revision plan, Section 3 and Task 8).",
        "count_budget": COUNT_BUDGET,
        "witness_budget_s": args.witness_budget,
        "graphs": entries,
    }
    (GRAPHS / "tiers.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (GRAPHS / "witnesses.json").write_text(json.dumps(witnesses) + "\n")


if __name__ == "__main__":
    main()
