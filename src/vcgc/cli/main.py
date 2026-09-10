"""Small command handlers delegating all research behavior to library modules."""

import argparse
import json
from pathlib import Path
import sys


def parser() -> argparse.ArgumentParser:
    """Describe explicit commands; constructing help imports no optional backend."""
    root = argparse.ArgumentParser(
        prog="vcgc", description="Graph-coloring and Boolean-oracle research"
    )
    root.add_argument("--version", action="version", version="vcgc 0.2.0")
    commands = root.add_subparsers(dest="command", required=True)
    datasets = commands.add_parser(
        "datasets", help="Acquire pinned Boolean inputs"
    ).add_subparsers(dest="action", required=True)
    fetch = datasets.add_parser("fetch")
    fetch.add_argument("names", nargs="*", default=["ctrl", "int2float", "cavlc"])
    fetch.add_argument("--cache", type=Path)
    fetch.add_argument("--offline", action="store_true")
    native = commands.add_parser(
        "native", help="Build the native synthesis helper"
    ).add_subparsers(dest="action", required=True)
    build = native.add_parser("build")
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--build", type=Path)
    build.add_argument("--jobs", type=int, default=2)
    synth = commands.add_parser(
        "synthesize", help="Compile a .col, .v, .aig, or .aag input"
    )
    synth.add_argument("input", type=Path)
    synth.add_argument("--colors", type=int)
    synth.add_argument("--method", default="xag")
    synth.add_argument("--k", type=int, default=4)
    synth.add_argument("--outputs", type=int, nargs="+")
    synth.add_argument("--outer-cut", type=int, default=16)
    synth.add_argument("--inner-cut", type=int, default=4)
    synth.add_argument("--native-executable", type=Path)
    synth.add_argument("--output", type=Path)
    synth.add_argument(
        "--validation", choices=["exhaustive", "sampled", "none"], default="exhaustive"
    )
    synth.add_argument("--seed", type=int, default=7)
    synth.add_argument(
        "--view", choices=["raw", "xor", "phase", "grover"], default="raw"
    )
    synth.add_argument("--iterations", type=int, default=1)
    benchmark = commands.add_parser(
        "benchmark", help="Run a reproducible experiment"
    ).add_subparsers(dest="action", required=True)
    run = benchmark.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--output", type=Path)
    run.add_argument("--methods", nargs="+")
    run.add_argument("--seed", type=int)
    run.add_argument("--native-executable", type=Path)
    plot = commands.add_parser("plot", help="Plot current or historical result tables")
    plot.add_argument("input", type=Path)
    plot.add_argument(
        "--metric", default="qubits", choices=["qubits", "gates", "depth", "seconds"]
    )
    plot.add_argument("--output", type=Path, required=True)
    plot.add_argument("--normalize", action="store_true")
    plot.add_argument("--log", action="store_true")
    notebook = commands.add_parser(
        "notebook", help="Execute a maintained notebook"
    ).add_subparsers(dest="action", required=True)
    execute = notebook.add_parser("run")
    execute.add_argument("input", type=Path)
    execute.add_argument("--output", type=Path)
    execute.add_argument("--workspace", type=Path)
    execute.add_argument("--offline", action="store_true")
    hardware = commands.add_parser(
        "hardware", help="Explicit IBM submission or local analysis"
    ).add_subparsers(dest="action", required=True)
    submit = hardware.add_parser("submit")
    submit.add_argument("input", type=Path, help="QPY file; exactly one circuit")
    submit.add_argument("--input-qubits", type=int, nargs="+", required=True)
    submit.add_argument("--backend", required=True)
    submit.add_argument("--shots", type=int, required=True)
    submit.add_argument("--seed", type=int, default=7)
    submit.add_argument("--output", type=Path)
    retrieve = hardware.add_parser("retrieve")
    retrieve.add_argument("job_id")
    retrieve.add_argument("--output", type=Path, required=True)
    analyze = hardware.add_parser("analyze")
    analyze.add_argument("input", type=Path, help="Retrieved counts JSON")
    analyze.add_argument("--graph", type=Path, required=True)
    analyze.add_argument("--colors", type=int)
    return root


def dispatch(args) -> None:
    """Invoke only the dependencies needed by the selected command."""
    if args.command == "datasets":
        from vcgc.benchmarks.datasets import download_benchmarks

        print(
            json.dumps(
                {
                    k: str(v)
                    for k, v in download_benchmarks(
                        args.names, cache=args.cache, offline=args.offline
                    ).items()
                },
                indent=2,
            )
        )
    elif args.command == "native":
        from vcgc.synthesis.native import build_native

        print(build_native(args.source, build=args.build, jobs=args.jobs))
    elif args.command == "synthesize":
        from qiskit import qpy
        from vcgc import read_dimacs, encode_coloring
        from vcgc.synthesis import synthesize
        from vcgc.verification import validate
        from vcgc.benchmarks.export import export_result
        from vcgc.benchmarks.runner import new_run_directory
        from vcgc.benchmarks.provenance import checkout_revision

        encoding = (
            encode_coloring(read_dimacs(args.input, colors=args.colors))
            if args.input.suffix == ".col"
            else None
        )
        result = synthesize(
            encoding if encoding is not None else args.input,
            args.method,
            k=args.k,
            outputs=args.outputs,
            outer_cut=args.outer_cut,
            inner_cut=args.inner_cut,
            executable=args.native_executable,
        )
        if args.validation != "none":
            validate(result, sampled=args.validation == "sampled", seed=args.seed)
        circuit = result.circuit
        if args.view == "xor":
            circuit = result.oracle()
        elif args.view == "phase":
            circuit = result.phase_oracle()
        elif args.view == "grover":
            from vcgc.circuits.grover import coloring_preparation, grover_circuit

            circuit = grover_circuit(
                result,
                preparation=(
                    coloring_preparation(encoding) if encoding is not None else None
                ),
                iterations=args.iterations,
            )
        output = new_run_directory(args.output)
        result.metadata["run"] = {
            "id": output.name,
            "view": args.view,
            "iterations": args.iterations,
            "checkout": checkout_revision(Path.cwd()),
        }
        export_result(result, output, args.input.stem)
        with (output / "circuit.qpy").open("wb") as stream:
            qpy.dump(circuit, stream)
        print(json.dumps({"output": str(output), **result.summary()}, indent=2))
    elif args.command == "benchmark":
        from vcgc.benchmarks.runner import load_config, run_benchmarks

        config = load_config(
            args.config,
            output=str(args.output) if args.output else None,
            methods=args.methods,
            seed=args.seed,
        )
        print(run_benchmarks(config, executable=args.native_executable))
    elif args.command == "plot":
        from vcgc.visualization.results import plot_results
        import matplotlib.pyplot as plt

        figure = plot_results(
            args.input,
            metric=args.metric,
            output=args.output,
            normalize=args.normalize,
            log=args.log,
        )
        plt.close(figure)
        print(args.output)
    elif args.command == "notebook":
        from vcgc.benchmarks.notebooks import execute_notebook

        print(
            execute_notebook(
                args.input,
                output=args.output,
                offline=args.offline,
                workspace=args.workspace,
            )
        )
    elif args.command == "hardware":
        if args.action == "submit":
            from qiskit import qpy
            from vcgc.execution.ibm import submit
            from vcgc.benchmarks.runner import new_run_directory

            with args.input.open("rb") as stream:
                circuits = qpy.load(stream)
            if len(circuits) != 1:
                raise ValueError("Submit a QPY containing exactly one selected circuit")
            output = new_run_directory(args.output)
            record = submit(
                circuits[0],
                args.input_qubits,
                backend_name=args.backend,
                shots=args.shots,
                seed=args.seed,
            )
            (output / "job.json").write_text(json.dumps(record, indent=2) + "\n")
            print(json.dumps(record, indent=2))
        elif args.action == "retrieve":
            from vcgc.execution.ibm import retrieve

            # Reserve the output before requesting job results.
            with args.output.open("x") as stream:
                json.dump(retrieve(args.job_id), stream, indent=2)
            print(args.output)
        else:
            from vcgc import read_dimacs, encode_coloring
            from vcgc.execution.local import success_probability

            record = json.loads(args.input.read_text())
            probability = success_probability(
                record["counts"],
                encode_coloring(read_dimacs(args.graph, colors=args.colors)),
            )
            print(json.dumps({"success_probability": probability}))


def main(argv=None) -> int:
    """Return a process exit status, with actionable optional-dependency errors."""
    command_parser = parser()
    args = command_parser.parse_args(argv)
    try:
        dispatch(args)
    except ImportError as error:
        print(
            f"vcgc: missing optional dependency: {error}. Install the corresponding extra with uv sync --extra <feature>.",
            file=sys.stderr,
        )
        return 2
    except (ValueError, OSError, RuntimeError) as error:
        print(f"vcgc: {error}", file=sys.stderr)
        return 1
    return 0
