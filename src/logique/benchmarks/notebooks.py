"""Execute notebook sources with the invoking interpreter and isolated outputs."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from .runner import new_run_directory
from .provenance import environment, checkout_revision


def execute_notebook(
    source: str | Path,
    *,
    output: str | Path | None = None,
    offline: bool = False,
    workspace: str | Path | None = None,
) -> Path:
    """Execute a notebook in a temporary kernel; keep source outputs untouched."""
    import nbformat
    from nbclient import NotebookClient
    from jupyter_client.kernelspec import KernelSpecManager

    source = Path(source).resolve()
    root = Path(workspace).resolve() if workspace else Path.cwd().resolve()
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    directory = new_run_directory(output)
    manifest = {
        "run_id": directory.name,
        "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "offline": offline,
        "versions": environment(),
        "checkout": checkout_revision(root),
        "status": "running",
    }
    (directory / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if offline:
        notebook.cells.insert(
            0,
            nbformat.v4.new_code_cell(
                "import socket\ndef _block_network(*args, **kwargs):\n    raise RuntimeError('Network disabled for offline verification')\nsocket.create_connection = _block_network\nsocket.socket.connect = _block_network\n"
            ),
        )
    with tempfile.TemporaryDirectory(prefix="logique-kernel-") as temporary:
        spec = Path(temporary) / "logique-local"
        spec.mkdir()
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
                    "display_name": "LOGIQUE local",
                    "language": "python",
                }
            )
        )
        client = NotebookClient(
            notebook,
            timeout=300,
            kernel_name="logique-local",
            resources={"metadata": {"path": str(root)}},
        )
        client.create_kernel_manager().kernel_spec_manager = KernelSpecManager(
            kernel_dirs=[temporary]
        )
        try:
            client.execute(
                env={
                    **os.environ,
                    "LOGIQUE_WORKSPACE": str(root),
                    "LOGIQUE_OUTPUT": str(directory),
                    "LOGIQUE_OFFLINE": "1" if offline else "0",
                    "MPLBACKEND": "Agg",
                }
            )
            manifest["status"] = "complete"
        except Exception as error:
            manifest.update(status="failed", error=f"{type(error).__name__}: {error}")
            raise
        finally:
            (directory / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
            target = directory / f"{source.stem}_executed.ipynb"
            nbformat.write(notebook, target)
    return target
