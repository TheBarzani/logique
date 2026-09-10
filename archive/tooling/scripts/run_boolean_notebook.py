"""Execute the Boolean synthesis tutorial with the current Python interpreter."""

import argparse
import os
from pathlib import Path
import sys
import tempfile

from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient
import nbformat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--notebook",
        type=Path,
        help="Notebook to execute (defaults to workspace tutorial)",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = args.notebook or root / "examples/boolean_synthesis_workspace.ipynb"
    default_name = (
        f"{source.stem}_executed.ipynb" if args.notebook else "executed.ipynb"
    )
    output = args.output or root / "data/boolean_benchmarks/results" / default_name
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    if args.offline:
        notebook.cells.insert(
            0,
            nbformat.v4.new_code_cell(
                "import socket\n"
                "def _block_network(*args, **kwargs):\n"
                "    raise RuntimeError('Network disabled for offline verification')\n"
                "socket.create_connection = _block_network\n"
                "socket.socket.connect = _block_network\n"
            ),
        )
    # A temporary kernel spec avoids depending on the user's selected Jupyter kernel.
    with tempfile.TemporaryDirectory(prefix="vcgc-kernel-") as directory:
        spec = Path(directory) / "vcgc-local"
        spec.mkdir()
        import json

        (spec / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        sys.executable,
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                    ],
                    "display_name": "VCGC local",
                    "language": "python",
                }
            )
        )
        manager = KernelSpecManager(kernel_dirs=[directory])
        client = NotebookClient(
            notebook,
            timeout=240,
            kernel_name="vcgc-local",
            resources={"metadata": {"path": str(root)}},
        )
        client.create_kernel_manager().kernel_spec_manager = manager
        client.execute(
            env={
                **os.environ,
                "VCGC_OFFLINE": "1" if args.offline else "0",
                "MPLBACKEND": "Agg",
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, output)
    print(f"Executed {len(notebook.cells)} cells: {output}")


if __name__ == "__main__":
    main()
