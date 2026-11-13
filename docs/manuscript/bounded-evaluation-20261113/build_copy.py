"""Assemble a new manuscript copy; preserve admitted background and old PDFs.

The caller runs the emitted command offline under its serial time/RSS supervisor.
No subprocess, environment installation, compilation, or network is invoked here.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manuscript = Path(__file__).resolve().parents[1]
    target = args.output.resolve()
    assert not target.exists(), "Use a new copy directory"
    source = manuscript / "conference.tex"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == (
        "7d0c06583a3ae0cf759ecf20e3114e28a9324c24c62fe482258576c8ba727969"
    )
    shutil.copytree(manuscript, target)
    original = source.read_text()
    start = original.index(r"\section{Evaluation Plan: Evidence Pending}")
    stop = original.index(r"\section{Conclusion: Revision Status}", start)
    text = (
        original[:start]
        + r"\input{bounded-evaluation-20261113/evaluation.tex}"
        + "\n\n"
        + original[stop:]
    )
    text = text.replace(
        r"\title{From Graph",
        r"\title[Provisional bounded evaluation]{Provisional draft (full evidence gate BLOCKED): From Graph",
        1,
    )
    a = text.index(r"\begin{abstract}") + len(r"\begin{abstract}")
    b = text.index(r"\end{abstract}", a)
    text = (
        text[:a]
        + "\n"
        + (
            "This provisional manuscript asks when logic-based graph-coloring compilation "
            "changes quantum resource costs under matched semantic and workspace contracts. "
            "A bounded evaluation draft presents previously admitted component, ideal-iteration, "
            "static fault-tolerant, dynamic preparation and conditional noisy evidence in "
            "separate contexts, retaining losses and exclusions. Its presentation requires "
            "independent review. The full manuscript evidence gate remains BLOCKED; "
            "the final title, abstract, contribution statement and comparative conclusions "
            "remain provisional. No novelty, broad superiority or noise-resilience claim "
            "is established by this draft.\n"
        )
        + text[b:]
    )
    text = text.replace(
        "This results-independent revision is not approval of the full manuscript.",
        "This bounded evaluation draft still requires independent presentation review "
        "and is not approval of the full manuscript.",
        1,
    )
    (target / "conference.tex").write_text(text)
    quantikz = (
        args.root
        / "dump/1024235721-coloring-paper-server-checkpoint/manuscript-build/tex-support/quantikz"
    )
    support = {}
    for path in sorted(quantikz.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
            support[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    executable = (
        args.root
        / "dump/1024235721-coloring-paper-server-checkpoint/latex-tools/bin/tectonic"
    )
    command = [
        str(executable),
        "--only-cached",
        "--keep-logs",
        "--keep-intermediates",
        "--outdir",
        str(target),
        str(target / "conference.tex"),
    ]
    (target.parent / (target.name + "-inputs.json")).write_text(
        json.dumps(
            dict(
                background_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                generated_tex_sha256=hashlib.sha256(text.encode()).hexdigest(),
                quantikz=support,
                tectonic_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
                command=command,
            ),
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(command))


if __name__ == "__main__":
    main()
