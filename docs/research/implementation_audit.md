# Coloring revision implementation audit

Audited on 25 October 2026 from transferred HEAD `3ec511d` on
`coloring-paper-revamp-codex`. The operating plan is
[the server execution plan](../coloring-paper-revamp-codex-plan.md), including its
26 October–1 November schedule. This audit does not add roadmap work.

## Existing implementation reused

| Task | Current implementation | Evidence and remaining work |
| --- | --- | --- |
| 1 | Notebook reference repairs (`e066c39`); native build provenance (`3a96dff`); existing claim audit | All maintained notebook sources currently have empty outputs and execution counts. Illustrative cells 0, 34, 36, 39–43 already distinguish matching and historical reflections and check zero leakage only for the former. Revision sources and nested histories were transferred. Source integration and build-derived environment reporting are being completed. |
| 2 | Config loader, synthesis/comparison/phase runners; normalized historical baseline adapter; coherent monomial verification | Loader has no regime/profile/workspace/target/precision/iteration-sweep/limit schema. Baseline API returns complete historical Grover circuits only. Verification accepts exhaustive or random inputs but no explicit witnesses. Stage timing and qubit roles are incomplete. These are open implementation tasks. |
| 3 | `costs.py` (`2ed650b`, `2848f21`), `routing.py` (`059e865`), `mcx_decompositions.ipynb` (`3ec511d`) | Explicit restoring and throwaway constructions, exact gadgets, dependency-graph T-depth, Dutta analytical reference, leading-order rotation estimate, success/iteration helpers, five-seed routing, and isolated 3–20-control study exist. Quantum smoke tests passed. Whole-algorithm approximate rotation synthesis and general paired-tree lowering are still open; a leading-order estimate is not an emitted approximation. |
| 4 | Existing all-bitstrings comparison and phase-oracle runner | R1–R3 controlled assembly, validated four-baseline comparison, complete qubit-role breakdown, strongest-baseline statistics, pilots and frozen protocol remain open. No corrected headline results exist yet. |
| 5 | Five maintained synthesis methods and native bridge | Low-T/depth/in-place/eager mappings, richer action serialization, balanced/MC profiles, standalone balancing tool, SAT integration and structure-aware scheduled oracle remain open. Preserve dependency revisions. |
| 6 | Per-circuit exact Clifford+T gadget counts and optional per-rotation estimate | Full-search accounting, compiled rotations under repeated-preparation budget, preparation break-even study and independent Astra derivation/RUS review remain open. |
| 7 | Correct matching-reflection Grover wrapper and small independent amplification regression | Complete ideal/noisy iteration sweeps, leakage, confidence intervals and random-sampling/cost-per-success study remain open. |
| 8 | General benchmark runner and fixed 180-second native timeout | Controlled scaling families, restored DIMACS inputs, five repetitions, stage memory/timeouts and larger-instance witnesses remain open. |

## Server evidence

The home server has 8 GiB RAM, eight logical CPUs and AC power. The initial
numerical policy is one memory-heavy job and one compiler process. Python 3.10.22,
Qiskit 2.1.1 and the locked research extras were installed through `tools/sync.py`.
CMake 3.31.6 and Ninja 1.11.1.4 are isolated build tools. The bridge built with
AppleClang 21.0.0; its build record includes the declared Caterpillar reference
and source hashes. No dependency revisions were changed.

The initial quantum smoke selection passed 109 tests (coloring, synthesis,
MCX/costs, routing, and notebook-source checks). Two notebook execution checks
initially failed because the sandbox blocked Jupyter socket binding; both passed
on their separate rerun with local socket access.

Execution logs, task/session IDs, tests and next actions are in
`dump/1024235721-coloring-paper-server-checkpoint/manifest.json`. No new comparison
or scalability result should be inferred from a passing toolkit test.

## Source-history preservation

Before source integration, complete nested `main` histories were bundled and
verified in `nested-histories/manuscript.bundle` and `research.bundle` under the
checkpoint. Their original Git metadata was moved alongside those bundles.
Original source files and generated PDFs remain on disk; generated LaTeX outputs
are excluded from parent tracking. Historical `experiments/manuscript/` artifacts
are unchanged.
