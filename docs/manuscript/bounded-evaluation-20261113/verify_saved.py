"""Recount saved scalar evidence without compiling or evolving quantum states.

Run with the existing root venv Python, explicit candidate PYTHONPATH, and
--root pointing to the authoritative integration checkout. Output is exclusive.
This authenticates presentation inputs; it does not independently admit science.
"""

import argparse
import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import logique


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = Path(__file__).resolve().parents[3]
    assert Path(logique.__file__).resolve() == candidate / "src/logique/__init__.py"
    root = args.root.resolve()
    sources = {}

    def read(path, expected=None):
        path = root / path
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        digest = h.hexdigest()
        if expected is not None:
            assert digest == expected, str(path)
        sources[str(path.relative_to(root))] = digest
        return path

    def load(path, expected=None):
        return json.loads(read(path, expected).read_text())

    successor = Path("dump/1101052342-full-research-successor")
    base = Path("dump/1030020413-full-scope-continuation-coordinator/worktrees")
    review = (
        base
        / "comparison-evidence-review/dump/1030165059-comparison-continuation-review"
    )
    read(
        "docs/research/comparison_continuation_admission_review_20261101.md",
        "c6e271f0e63e055280da0998f96415334be6ba3eb0799961d5f3dcecd98f8da2",
    )
    components = load(review / "admitted-component-intersection.json")
    assert len(components) == 230
    assert {row["component"] for row in components} == {"preparation", "diffusion"}
    # Bind every component to the execution's authenticated QPY inventory.
    execution = Path("dump/1030122806-wide-qpy-execution")
    inventory = load(execution / "checkpoint.json")["evidence_sha256"]
    for row in components:
        artifact = row["artifact"]
        read(execution / artifact, inventory[artifact])
    with read(review / "admitted-matched-service-details.csv").open() as stream:
        details = list(csv.DictReader(stream))
    assert len(details) == 492
    assert all(row["outcome"] == "tie" and float(row["ratio"]) == 1 for row in details)
    with read(review / "admitted-matched-service-summary.csv").open() as stream:
        summaries = list(csv.DictReader(stream))
    assert len(summaries) == 378
    assert sum(int(row["instances"]) for row in summaries) == 492

    c5 = base / "c5-complete-execute/dump/1101010944-c5-complete-best-fit"
    manifest = load(
        c5 / "manifest.json",
        "fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4",
    )
    for path, digest in manifest["evidence_hashes"].items():
        read(c5 / path, digest)
    with read(
        successor / "c5-admitted-plot-data.csv",
        "c788a1c7bafef6d54c1df7b2627b2957697045d5a6d2ce3e7adaa748bf230417",
    ).open() as stream:
        plotted = list(csv.DictReader(stream))
    c5_rows = []
    tex_rows = []
    for regime, support, count in [("R1", 1024, 6), ("R2", 243, 4)]:
        result = load(c5 / regime / "result.json")
        assert result["width"] == 11 and len(result["rows"]) == count
        assert result["artifacts"]["oracle"]["instructions"] == 84441
        assert result["artifacts"]["oracle"]["qubits"] == 11
        assert result["artifacts"]["oracle"]["sha256"] == (
            "8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268"
        )
        for row in result["rows"]:
            j = row["iterations"]
            prediction = math.sin((2 * j + 1) * math.asin(math.sqrt(30 / support))) ** 2
            saved = next(
                x
                for x in plotted
                if x["regime"] == regime and int(x["iterations"]) == j
            )
            assert float(saved["success"]) == row["success"]
            assert (
                float(saved["unused_code_probability"])
                == row["unused_code_probability"]
            )
            assert abs(row["success"] - prediction) < 1e-10
            assert abs(float(saved["analytical"]) - prediction) < 1e-15
            c5_rows.append(dict(regime=regime, j=j, **row))
            unused = row["unused_code_probability"]
            display = f"{unused:.9f}" if regime == "R1" else f"${unused:.2e}$"
            if regime == "R2":
                mantissa, exponent = f"{unused:.2e}".split("e")
                display = rf"${mantissa}\times10^{{{int(exponent)}}}$"
            tex_rows.append(
                f"{regime} & {j} & {row['success']:.12f} & {display}" + r"\\"
            )
    assert len(c5_rows) == len(plotted) == 10
    figure = load(successor / "figure-manifest.json")
    for name, digest in figure.items():
        read(successor / name, digest)
        copy = Path(__file__).parent / "assets" / name
        assert hashlib.sha256(copy.read_bytes()).hexdigest() == digest
    assert (Path(__file__).parent / "c5-rows.tex").read_text() == "\n".join(
        tex_rows
    ) + "\n"

    mcx = load(
        base
        / "mcx-whole-review/dump/1031145904-mcx-whole-independent-review/recount-results.json"
    )
    assert mcx["rows"] == {"complete": 1608, "excluded": 42}
    assert mcx["coherent"] == {"passed": 1335, "excluded_full_statevector": 84}
    assert sum(mcx["losses"].values()) == 5160

    ft_path = base / "graph-ft-execute/dump/1031151632-graph-ft-execution"
    ft_index = load(
        ft_path / "artifact-hashes-final.json",
        "6f20f0abb3870f251652f80a8b0ae860b67d02d5ff3719d4d83796ccb87132da",
    )
    summary = load(ft_path / "summary.json", ft_index["summary.json"]["sha256"])
    rows = summary["rows"]
    assert len(rows) == 15
    assert sum(r["status"] == "complete" for r in rows) == 12
    assert sum(r["status"] == "failed" for r in rows) == 3
    primary = [r for r in rows if r["j"] == 1 and r["budget"] == 0.001]
    assert [r["full_search_metrics"]["t_count"] for r in primary] == [
        271982,
        353792,
        353624,
    ]
    assert [r["full_search_metrics"]["t_depth"] for r in primary] == [
        194958,
        222800,
        222764,
    ]
    # Streaming hashes bind the table's full saved circuits, without QPY loading.
    for row in rows:
        relative = Path(row["directory"]).name
        for name in [
            "result.json",
            "search.qpy",
            "A.qpy",
            "A_inverse.qpy",
            "O.qpy",
            "S0.qpy",
        ]:
            key = str(Path(relative) / name)
            if key in ft_index:
                read(ft_path / key, ft_index[key]["sha256"])

    rus_path = base / "dynamic-rus-execute/dump/1031201007-dynamic-rus-execution"
    rus = load(rus_path / "summary.json")
    cases = load(rus_path / "cases.json")
    assert rus["cases"] == 20 and rus["terminal_branches"] == 220
    q = 1 - Fraction(1, 4) ** 4
    attempts = sum(Fraction(1, 4) ** n for n in range(4))
    costs = {"forward": 2 * attempts + 2 * q, "inverse": 2 * attempts + 2}
    for direction, cost in costs.items():
        case = next(c for c in cases if c["case"] == direction + "-cap4")
        assert Fraction(case["analytical_expected_resources"]["t"]) == cost
        assert abs(case["observed_expected_resources"]["t"] - float(cost)) < 1e-12
        assert abs(case["completion_probability_observed"] - float(q)) < 1e-12
    assert q == Fraction(255, 256)

    noisy = load("dump/1030015553-noisy-channel-integration-triage/audit.json")
    assert len(noisy["rows"]) == 28 and sum(r["shots"] for r in noisy["rows"]) == 1792
    triangle = [r for r in noisy["rows"] if r["child"].startswith("K3") and r["j"] == 1]
    assert [r["successes"] for r in triangle] == [3, 10, 10, 3, 7]
    assert [r["leakage"] for r in triangle] == [37, 28, 24, 34, 33]
    noisy_path = Path(
        "dump/1029204240-coloring-dispatch-continuation/worktrees/"
        "noisy-channel-repair/dump/1029210538-noisy-channel-repair"
    )
    noisy_index = load(
        noisy_path / "final-evidence-hashes.json",
        "db3ce032c7b9e284c22a57e1ff8627a4a9a4eb9388a19d4c5b61c2ecee0e4c77",
    )
    for path, digest in noisy_index.items():
        if path.startswith("runs/1029210741-noisy-iteration-study/"):
            read(noisy_path / path, digest)
    read(
        noisy_path / "runs/1029210741-noisy-iteration-study/manifest.json",
        "f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278",
    )
    read(
        "docs/research/noisy_family_independent_review_20261109.md",
        "a9681ad0aeca395b5183eb8daf01608827c0a60707dbeb7617eec335c5134b1d",
    )
    for path in [
        "docs/research/full_research_successor_20261101.md",
        "docs/research/noisy_family_integration_20261109.md",
        "docs/research/noisy_family_independent_review_20261109.md",
        "docs/research/c5_complete_independent_review_20261101.md",
        "docs/research/c5_complete_integration_20261101.md",
        "docs/research/mcx_whole_review_20261031.md",
        "docs/research/mcx_whole_integration_20261031.md",
        "docs/research/graph_ft_independent_review_20261031.md",
        "docs/research/graph_ft_integration_20261031.md",
        "docs/research/dynamic_rus_independent_review_20261101.md",
        "docs/research/dynamic_rus_integration_20261101.md",
        "docs/research/noisy_channel_integration_20261030.md",
        "dump/1031221547-c5-22-qubit-resource-pilot/checkpoint.json",
    ]:
        read(path)
    read(
        "dump/1025024643-coloring-integration-gate/worktrees/native-contract/"
        "dump/1025025511-native-contract/build/boolean_synthesis",
        "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a",
    )
    output = dict(
        scope="saved scalar checks and streaming hashes only; no quantum replay",
        component_rows=230,
        matched_details=492,
        summary_groups=378,
        c5_rows=10,
        mcx=mcx,
        graph_ft_primary=primary,
        rus_completion=str(q),
        rus_costs={k: str(v) for k, v in costs.items()},
        noisy_original_records=28,
        noisy_original_shots=1792,
        sha256=sources,
    )
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(
        f"Verified saved inputs: {len(sources)} hashes; ten C5 rows; 230 components; 492 ties"
    )


if __name__ == "__main__":
    main()
