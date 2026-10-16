"""Replay the original paper pipeline without changing its reference artifacts."""

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
from pathlib import Path
import platform
import re
import shutil
import statistics
import struct
import sys
import zlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments/manuscript"
LEGACY = STUDY / "legacy"
METRICS = ("width", "depth", "gates")
METHODS = ("original", "minimal", "simple", "balanced")
HARDWARE_CSV = "data/execution/20250829_161926/execution_comparison.csv"


def digest(path: Path) -> str:
    """Return the SHA-256 of a file's original bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    """Read a results table without reordering benchmarks."""
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def compare_metrics(reference: list[dict], actual: list[dict]) -> dict:
    """Require identical benchmark coverage and exact positive metric values."""
    expected = {row["benchmark"]: row for row in reference}
    observed = {row["benchmark"]: row for row in actual}
    differences = []
    if len(observed) != len(actual):
        differences.append({"error": "Duplicate benchmark rows"})
    for name in sorted(expected.keys() | observed.keys()):
        if name not in expected or name not in observed:
            differences.append(
                {"benchmark": name, "error": "Benchmark coverage differs"}
            )
            continue
        for key, value in expected[name].items():
            if key == "benchmark":
                continue
            got = observed[name].get(key)
            if got is None or float(got) != float(value):
                differences.append(
                    {"benchmark": name, "metric": key, "expected": value, "actual": got}
                )
            elif key.endswith(METRICS) and float(got) <= 0:
                differences.append(
                    {"benchmark": name, "metric": key, "error": "Nonpositive result"}
                )
    return {"exact": not differences, "differences": differences}


def improvement_table(rows: list[dict]) -> dict:
    """Apply the historical mean of per-graph percentage reductions."""
    table = {
        method: {
            metric: statistics.mean(
                100
                * (float(row[f"sb_{method}_{metric}"]) - float(row[f"vcgc_{metric}"]))
                / float(row[f"sb_{method}_{metric}"])
                for row in rows
            )
            for metric in METRICS
        }
        for method in METHODS
    }
    return {
        "per_baseline_percent": table,
        "overall_percent": {
            metric: statistics.mean(table[method][metric] for method in METHODS)
            for metric in METRICS
        },
    }


def load_script(name: str):
    """Load an unchanged legacy script without executing its CLI entry point."""
    spec = importlib.util.spec_from_file_location(
        f"manuscript_{name}", LEGACY / "scripts" / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def compare_image(reference: Path, actual: Path, output: Path) -> dict:
    """Compare file bytes and RGBA pixels, saving an unaligned visual difference."""
    from PIL import Image, ImageChops, ImageDraw

    with Image.open(reference) as source, Image.open(actual) as generated:
        a, b = source.convert("RGBA"), generated.convert("RGBA")
        result = {
            "reference_sha256": digest(reference),
            "actual_sha256": digest(actual),
            "bytes_equal": reference.read_bytes() == actual.read_bytes(),
            "pixels_equal": a.size == b.size and a.tobytes() == b.tobytes(),
            "reference_size": list(a.size),
            "actual_size": list(b.size),
        }
        reference_chunks, actual_chunks = png_chunks(reference), png_chunks(actual)
        result["differing_png_chunks"] = sorted(
            key
            for key in reference_chunks.keys() | actual_chunks.keys()
            if reference_chunks.get(key) != actual_chunks.get(key)
        )
        result["decompressed_image_data_equal"] = zlib.decompress(
            reference_chunks["IDAT"]
        ) == zlib.decompress(actual_chunks["IDAT"])
        size = (max(a.width, b.width), max(a.height, b.height))
        padded = []
        for im in (a, b):
            canvas = Image.new("RGB", size, "white")
            canvas.paste(im, (0, 0))
            padded.append(canvas)
        diff = ImageChops.difference(*padded)
        diff.save(output.with_name(output.stem + "_difference.png"))
        panels = [*padded, diff]
        preview = Image.new("RGB", (1800, 680), "white")
        for i, (panel, label) in enumerate(
            zip(panels, ("Reference", "Regenerated", "Absolute pixel difference"))
        ):
            panel.thumbnail((600, 640))
            preview.paste(panel, (600 * i, 30))
            ImageDraw.Draw(preview).text((600 * i + 10, 5), label, fill="black")
        preview.save(output)
        return result


def png_chunks(path: Path) -> dict[str, bytes]:
    """Group PNG chunks to distinguish compression from metadata differences."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Expected PNG: {path}")
    chunks = {}
    offset = 8
    while offset < len(data):
        size = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8].decode("ascii")
        chunks[kind] = chunks.get(kind, b"") + data[offset + 8 : offset + 8 + size]
        offset += size + 12
    return chunks


def audit(manuscript: Path | None) -> dict:
    """Validate recovered sources and inspect the available runtime."""
    provenance = json.loads((STUDY / "provenance.json").read_text())
    for item in provenance["files"]:
        if digest(LEGACY / item["path"]) != item["sha256"]:
            raise ValueError(f"Historical snapshot changed: {item['path']}")
    packages = {}
    for distribution in importlib.metadata.distributions():
        packages[distribution.metadata["Name"]] = distribution.version
    result = {
        "source_commit": provenance["source_commit"],
        "snapshot_files_verified": len(provenance["files"]),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": dict(sorted(packages.items())),
        "historical_submodules": provenance["submodules"],
    }
    dependencies = {}
    for name, expected in provenance["dependencies"].items():
        spec = importlib.util.find_spec(name)
        if spec is None:
            dependencies[name] = {"error": "Package not installed"}
            continue
        package = Path(spec.origin).parent
        mismatches = [
            relative
            for relative, sha256 in expected["python_sources"].items()
            if not (package / relative).is_file()
            or digest(package / relative) != sha256
        ]
        dependencies[name] = {
            "reference_revision": expected["revision"],
            "python_sources_match": not mismatches,
            "mismatches": mismatches,
            "native_binary_hashes": {
                str(p.relative_to(package)): digest(p) for p in package.rglob("*.so")
            },
        }
    result["dependencies"] = dependencies
    try:
        from qiskit import QuantumCircuit

        source = Path(inspect.getfile(QuantumCircuit))
        model = json.loads((STUDY / "depth-model.json").read_text())
        result["qiskit_depth"] = {
            "parameters": list(inspect.signature(QuantumCircuit.depth).parameters),
            "source_sha256": digest(source),
            "mcx_option_available": "mcx_decomposition"
            in inspect.signature(QuantumCircuit.depth).parameters,
            "model": (
                model if digest(source) == model["patched_source_sha256"] else None
            ),
            "historical_patch_recovered": False,
        }
    except ImportError as error:
        result["qiskit_depth"] = {"error": str(error)}
    if manuscript:
        tex = (manuscript / "conference.tex").read_text()
        tex = re.sub(r"(?<!\\)%[^\n]*", "", tex)
        figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
        hashes = {digest(p): str(p.relative_to(LEGACY)) for p in LEGACY.rglob("*.png")}
        result["manuscript_figures"] = [
            {
                "figure": name,
                "reference": hashes.get(digest(manuscript / name)),
            }
            for name in figures
        ]
    return result


def plots(output: Path, *, figure_dpi: float, benchmark_csv: Path) -> dict:
    """Plot the supplied benchmark evaluation using the original drawing functions."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import ft2font, font_manager

    # Only suppress interactive windows; leave all original drawing calls intact.
    plt.show = lambda: None
    destination = output / "plots"
    destination.mkdir()
    comparisons = output / "comparisons"
    comparisons.mkdir()
    shutil.copyfile(benchmark_csv, destination / "benchmark_results.csv")
    visualizer = load_script("visualize_benchmarks").BenchmarkVisualizer(destination)
    visualizer.load_csv_data()
    titles = (
        "Circuit Width Comparison",
        "Circuit Depth Comparison",
        "Number of Gates Comparsion",
    )
    labels = ("Circuit Width", "Circuit Depth", "Number of Gates")
    result = {}
    with plt.rc_context({"figure.dpi": figure_dpi}):
        for metric, title, label in zip(METRICS, titles, labels):
            name = f"{metric}_comparison_log.png"
            visualizer.create_grouped_bar_chart(
                metric, title, label, filename=name, log_scale=True
            )
            plt.close("all")
            result[name] = compare_image(
                LEGACY / "data/output" / name, destination / name, comparisons / name
            )
        analyzer = load_script("analyze_results").ResultsAnalyzer(
            str(destination) + "/"
        )
        if not analyzer.load_results(str(LEGACY / HARDWARE_CSV)):
            raise ValueError("Could not read historical hardware measurements")
        analyzer.plot_success_probability_ieee()
        plt.close("all")
        name = "ieee_success_probability.png"
        result[name] = compare_image(
            LEGACY / "data/execution" / name, destination / name, comparisons / name
        )
    font = Path(font_manager.findfont("DejaVu Sans"))
    return {
        "images": result,
        "benchmark_input": str(benchmark_csv),
        "benchmark_input_sha256": digest(benchmark_csv),
        "hardware_input": HARDWARE_CSV,
        "hardware_input_sha256": digest(LEGACY / HARDWARE_CSV),
        "hardware_evidence": "Saved summary probabilities; no raw counts recovered",
        "rendering": {
            "matplotlib": matplotlib.__version__,
            "freetype": ft2font.__freetype_version__,
            "backend": matplotlib.get_backend(),
            "figure_dpi": figure_dpi,
            "font_sha256": digest(font),
        },
    }


def validate_evaluation(directory: Path, output: Path) -> dict:
    """Compare every rebuilt metric with the reference and write an audit table."""
    reference_path = LEGACY / "data/output/benchmark_results.csv"
    actual_path = directory / "benchmark_results.csv"
    reference, actual = read_rows(reference_path), read_rows(actual_path)
    comparison = compare_metrics(reference, actual)
    observed = {row["benchmark"]: row for row in actual}
    rows = []
    for reference_row in reference:
        name = reference_row["benchmark"]
        for method in ("vcgc", *(f"sb_{name}" for name in METHODS)):
            for metric in METRICS:
                key = f"{method}_{metric}"
                expected = int(reference_row[key])
                raw_value = observed.get(name, {}).get(key)
                value = float(raw_value) if raw_value is not None else None
                rows.append(
                    {
                        "benchmark": name,
                        "method": method,
                        "metric": metric,
                        "reference": expected,
                        "regenerated": value,
                        "delta": value - expected if value is not None else None,
                        "exact": value == expected and value > 0,
                    }
                )
    with (output / "metric-comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {
        "status": "exact" if comparison["exact"] else "different",
        **comparison,
        "metric_values_compared": len(rows),
        "metric_values_matching": sum(row["exact"] for row in rows),
        "reference_csv_sha256": digest(reference_path),
        "regenerated_csv_sha256": digest(actual_path),
        "regenerated_improvements": improvement_table(actual),
    }


def evaluate(output: Path, environment: dict) -> dict:
    """Run the original evaluation with an explicitly recorded depth model."""
    if any(
        not dependency.get("python_sources_match")
        for dependency in environment["dependencies"].values()
    ):
        return {
            "status": "blocked",
            "reason": "Installed synthesis Python sources differ from historical pins",
        }
    if not environment["qiskit_depth"].get("mcx_option_available"):
        return {
            "status": "blocked",
            "reason": "Apply the recorded patch with tools/patch_qiskit_depth.py",
        }
    if environment["qiskit_depth"].get("model") is None:
        return {
            "status": "blocked",
            "reason": "Unrecognized Qiskit depth implementation",
        }
    sys.path.insert(0, str(LEGACY))
    module = load_script("generate_benchmarks")
    destination = output / "evaluation"
    generator = module.BenchmarkGenerator(LEGACY / "data/benchmarks", destination)
    reference = read_rows(LEGACY / "data/output/benchmark_results.csv")
    results = []
    for row in reference:
        result = generator.process_benchmark(row["benchmark"])
        if result is None:
            raise RuntimeError(f"Original generator failed for {row['benchmark']}")
        metrics = [result.vcgc_metrics, *result.saha_belletti_metrics.values()]
        if any(min(m.width, m.depth, m.num_gates) <= 0 for m in metrics):
            raise RuntimeError(
                f"Original generator returned failure zeros: {row['benchmark']}"
            )
        results.append(result)
        generator.save_results_csv(results)
        generator.save_results_json(results)
    return {
        **validate_evaluation(destination, output),
        "depth_model": environment["qiskit_depth"]["model"]["id"],
        "historical_patch_recovered": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=("audit", "plots", "evaluate", "all"), default="all"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manuscript", type=Path)
    parser.add_argument("--figure-dpi", type=float, default=200)
    args = parser.parse_args()
    from logique.benchmarks.runner import new_run_directory

    output = new_run_directory(
        args.output, description=f"manuscript-{args.stage}", root=ROOT / "dump"
    )
    report = {
        "stage": args.stage,
        "runner_sha256": digest(Path(__file__)),
        "command": sys.argv,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    try:
        report["environment"] = audit(args.manuscript)
        report["reference_improvements"] = improvement_table(
            read_rows(LEGACY / "data/output/benchmark_results.csv")
        )
        if args.stage in ("evaluate", "all"):
            report["evaluation"] = evaluate(output, report["environment"])
        if args.stage == "plots":
            report["plots"] = plots(
                output,
                figure_dpi=args.figure_dpi,
                benchmark_csv=LEGACY / "data/output/benchmark_results.csv",
            )
        elif args.stage == "all" and report["evaluation"]["status"] != "blocked":
            report["plots"] = plots(
                output,
                figure_dpi=args.figure_dpi,
                benchmark_csv=output / "evaluation/benchmark_results.csv",
            )
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"Reproduction report: {output / 'report.json'}")
    failures = report.get("evaluation", {}).get("status") in ("blocked", "different")
    differences = any(
        not row["pixels_equal"]
        for row in report.get("plots", {}).get("images", {}).values()
    )
    return 2 if failures or differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
