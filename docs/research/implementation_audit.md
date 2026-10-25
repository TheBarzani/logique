# Coloring revision implementation audit

Audited on 25 October 2026 from transferred HEAD `3ec511d` on
`coloring-paper-revamp-codex`. The operating plan is
[the server execution plan](../coloring-paper-revamp-codex-plan.md), including its
26 October–1 November schedule. This audit does not add roadmap work.

## Existing implementation reused

| Task | Current implementation | Evidence and remaining work |
| --- | --- | --- |
| 1 | Notebook reference repairs (`e066c39`); native build provenance (`3a96dff`); existing claim audit | All maintained notebook sources currently have empty outputs and execution counts. Illustrative cells 0, 34, 36, 39–43 already distinguish matching and historical reflections and check zero leakage only for the former. Revision sources and nested histories were transferred. Sources are now tracked after verified history preservation; environment reporting reads the selected bridge build record (`7daf835`, `b34a22b`). |
| 2 | Config loader, synthesis/comparison/phase runners; normalized historical baseline adapter; coherent monomial verification | Controlled R1–R3 assembly, per-input witnesses, iterations/seeds, explicit precolor removal, QPY export and validated baseline components are implemented (`94665c0`, `4fa714c`, `8058826`). Unsupported precision/routing/profile/limit controls are rejected, not silently ignored. Stage timing and qubit-role classification still need extension. |
| 3 | `costs.py` (`2ed650b`, `2848f21`), `routing.py` (`059e865`), `mcx_decompositions.ipynb` (`3ec511d`) | Explicit restoring and throwaway constructions, exact gadgets, dependency-graph T-depth, Dutta analytical reference, leading-order rotation estimate, success/iteration helpers, five-seed routing, and isolated 3–20-control study exist. Quantum smoke tests passed. Paired monomial compute-Z-uncompute lowering now holds scratch and uses the actual expanded inverse (`8f3a08d`). Whole-algorithm emitted rotation synthesis is under implementation/review. Gray-code rows above ten controls still need bounded execution or explicit infeasibility records; the existing notebook caps them at ten. |
| 4 | Existing all-bitstrings comparison and phase-oracle runner | The K3/K5/myciel3 logical pilot completed 144 validated cases with 18 explicit original-baseline exclusions and no failures. Every completed case exercised a marked input. All 720 metric rows were reproduced from saved QPY; per-instance strongest-baseline summaries are saved separately (`ba6b5b8`). Full nine-graph/multilevel evaluation, complete workspace classification and protocol freeze remain open; these pilot results are not headline evidence. |
| 5 | Five maintained synthesis methods and native bridge | Balanced AND/OR encoder association is opt-in and validated against independent predicates (`e6f3b45`). Bundled SAT, standalone XAG balancing/algebraic rewriting and ESOP balancing compiled and ran in feasibility probes. A reusable balancing tool, native strategy/serialization integration, common preprocessing, MC reduction and structure-aware scheduled oracle remain open. Dependency pins remain fixed. |
| 6 | Per-circuit exact Clifford+T gadget counts and optional per-rotation estimate | Full-search accounting, compiled rotations under repeated-preparation budget, preparation break-even study and independent Astra derivation/RUS review remain open. |
| 7 | Correct matching-reflection Grover wrapper and small independent amplification regression | Complete ideal/noisy iteration sweeps, leakage, confidence intervals and random-sampling/cost-per-success study remain open. |
| 8 | General benchmark runner and fixed 180-second native timeout | The three requested legacy inputs were restored byte-for-byte from `95f6167`, with hashes (`040d420`). Remaining source inputs, controlled families, five repetitions, stage memory/timeouts and larger-instance witnesses remain open. The restored color parameters are historical inputs, not verified chromatic-number claims. |

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

## Additional execution evidence

- `dump/1024235721-coloring-paper-server-checkpoint/historical-replay/`
  reproduced all 135 archived metrics inside an isolated Qiskit environment.
  The corrected research environment was checked to remain unpatched.
- The full pre-pilot suite passed 333 tests with six explicit skips; Black, Ruff,
  mypy and package build passed. Fetching the pinned EPFL inputs subsequently
  enabled and passed their skipped regressions. The historical patch remains
  intentionally absent from the corrected environment.
- `dump/1025012448-coloring-study/` contains the logical pilot and all 720 saved
  circuit metric rows; `comparison/` has 1,350 per-instance metric comparisons
  and 450 separately matched summaries. Seeds, iteration counts, components and
  metric levels are never combined implicitly.
- Graph and Boolean tutorial notebooks and the existing bounded MCX study ran
  offline with unchanged sources. The illustrative notebook's historical-cost
  section requires the isolated historical interpreter, which was used for its
  successful rerun. Logs retain the initial expected failure in the unpatched
  environment. No hardware or remote circuit jobs were run.
- Results-independent manuscript corrections cover matching diffusion, solution
  fraction, valid codes versus proper colorings, restoration contracts, logical
  Clifford+T accounting and full-search gate-count composition (`62fb1af`).
  The old abstract/evaluation/contribution claims still await the evidence gate;
  no final revised manuscript or superiority claim is asserted.
