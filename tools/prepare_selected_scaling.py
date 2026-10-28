"""Prepare complete Task8 input/witness ledger without launching synthesis."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from logique.benchmarks.scaling_inputs import (
    bounded_dimacs,
    decode_dimacs_binary,
    greedy_witness,
    normalize_legacy,
    queen_problem,
)
from logique.paths import new_dump_directory


def prepare(config_path: Path, root: Path) -> Path:
    """Write fresh graphs, provenance and independently checked witnesses."""
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text())
    if config["kind"] != "selected_scaling_preparation":
        raise ValueError("preparation-only config required")
    output = new_dump_directory("selected-scaling-inputs", root=root)
    rows = []
    for item in config["selected_inputs"]:
        row = dict(item, execution_status="blocked_admission", compiler_repeats=0)
        source = (
            (config_path.parent / item["path"]).resolve() if item.get("path") else None
        )
        if item.get("queen_size"):
            problem, witness = queen_problem(item["queen_size"], item["colors"])
            target = output / (item["name"] + ".col")
            target.write_text(
                f"c generated row-major queen graph size={item['queen_size']}\n"
                f"p edge {len(problem.vertices)} {len(problem.edges)}\n"
                + "".join(f"e {u} {v}\n" for u, v in problem.edges)
                + f"x colors {problem.colors}\n"
            )
            row["origin"] = "generated explicitly; no primary DIMACS identity claim"
        elif source is None or not source.is_file():
            row.update(input_status="missing_input", witness_status="unknown")
            rows.append(row)
            continue
        else:
            row["source_path"] = str(source)
            row["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            target = source
            if item.get("transform") == "remove_legacy_precolors":
                target = output / (item["name"] + "-unprecolored.col")
                row["normalization"] = normalize_legacy(
                    source, target, colors=item["colors"]
                )
            elif item.get("transform") == "decode_binary":
                target = output / (item["name"] + ".col")
                row["decoding"] = decode_dimacs_binary(source, target)
            problem = bounded_dimacs(target, item["colors"])
            if problem.precolored:
                row.update(
                    input_status="unsupported_precolored", witness_status="unsupported"
                )
                rows.append(row)
                continue
            witness = greedy_witness(problem)
            if item.get("queen_formula_size"):
                generated, formula = queen_problem(
                    item["queen_formula_size"], item["colors"]
                )
                if (
                    problem.edges != generated.edges
                    or problem.vertices != generated.vertices
                ):
                    raise ValueError(
                        "legacy queen labeling/edges differ from row-major definition"
                    )
                witness = formula
        if problem.precolored:
            raise AssertionError("precolored study prohibited")
        row.update(
            input_status="prepared_unprecolored",
            prepared_path=str(target),
            prepared_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            vertices=len(problem.vertices),
            undirected_edges=len(problem.edges),
            witness_status=(
                "verified_graph_predicate" if witness is not None else "unknown"
            ),
            witness=witness,
            solution_count=None,
            count_scope="unknown M; witness gives existence only",
            check_scope="independent graph predicate only; no Boolean network, phase or restoration evidence",
        )
        if witness is not None and not problem.is_valid(witness):
            raise AssertionError("invalid positive witness")
        rows.append(row)
    ledger = {
        "schema_version": 1,
        "config": str(config_path),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "execution_gate": config["execution_gate"],
        "budget": config["budget"],
        "controlled_families": config["controlled_families"],
        "rows": rows,
        "native_attempts": 0,
        "status": "preparation_complete_execution_blocked",
    }
    case_names = [row["name"] for row in rows]
    for family in config["controlled_families"]:
        for n, density, colors in itertools.product(
            family["vertices"], family["densities"], family["colors"]
        ):
            case_names.append(f"planted-n{n}-d{density}-k{colors}")
    budget = config["budget"]
    ledger["planned_attempts"] = [
        {
            "case": name,
            "method": method,
            "encoder_profile": profile,
            "repetition": rep,
            "validation_seed": seed,
            "status": "blocked_admission_not_launched",
            "per_child_wall_seconds": budget["per_child_wall_seconds"],
            "cumulative_boundary_wall_seconds": budget[
                "cumulative_boundary_wall_seconds"
            ],
            "memory_budget_bytes": budget["memory_bytes"],
            "times": {
                "encoding_seconds": None,
                "native_combined_seconds": None,
                "optimization_seconds": None,
                "mapping_seconds": None,
                "lowering_seconds": None,
                "boundary_wall_seconds": None,
            },
            "peak_memory_bytes": None,
            "response": None,
            "circuit": None,
        }
        for name, method, profile, (rep, seed) in itertools.product(
            case_names,
            budget["methods"],
            budget["encoder_profiles"],
            enumerate(budget["validation_seeds"]),
        )
    ]
    (output / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("dump"))
    args = parser.parse_args()
    print(prepare(args.config, args.root))
