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
| 5 | Five maintained synthesis methods, native bridge and standalone balancing tool | Balanced AND/OR encoder association is opt-in and validated against independent predicates (`e6f3b45`). The standalone tool supports XAG, algebraic and ESOP passes with per-pass and serialization equivalence checks (`90df410`). Native strategy/action serialization integration, common preprocessing, MC reduction, SAT pebbling and structure-aware scheduled oracles remain open. Dependency pins remain fixed. |
| 6 | Per-circuit Clifford+T gadgets; unintegrated static rotation prototype; independent derivation/RUS review | The independent reviews establish the unitary composition and separate RUS derivation, with explicit limitations. Rotation repair is not approved: the latest reviewed bytes admit a near-unitary numeric matrix that violates the requested whole-search error budget. FT comparisons remain blocked. Correct matrix admission/accounting and obtain a fresh hash-bound review before integration; complete-search experiments and preparation break-even results remain open. |
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

## Rotation integration gate: 25 October bounded batch

Integration HEAD at intake was `1e1f525`. The two repair files exactly match
the SHA-256 identities in the [independent re-review](task6_rotation_rereview.md):
`rotations.py` = `5a811a35f2f3d6203d68bb441213d521883b8b56235054df7384fd00db679457`,
`test_rotations.py` = `5513b65b67831e9100e76db00fadbbe22890da125f1abe8492d65c026cd924a1`.
The review task completed, but its scientific decision is **blocked**. Neither
repair file was integrated. The different untracked root prototype and the
user's README changes were preserved byte-for-byte.

The independently rerun 37-test review suite reproduces the accepted numeric
matrix counterexample: A = (1 + 1e-6) I, O = S0 = Z, j = 2. Actual error is
`5.000009999589494e-6`, reported bound `5.000000212751493e-6`, and a requested
budget of `5.000005e-6` is exceeded. Two passing review tests deliberately
confirm blockers, so this green suite does not admit the rotation contract.
Unitary-only telescoping does not bound products of admitted nonunitary numeric
targets. The next correction must reject such inputs or account for their norms;
increasing a fixed floating-point margin is not an acceptable resolution.

The manuscript findings in that re-review concern the older repair worktree
(HEAD `90df410`). Integration already contains `eef059d`: zero reflection is
`-X^n MCZ X^n`, A is initialized once with O,D repeated, full data preparation
is specified, p=0 means no prepared marked amplitude, and the first-peak
floor/ceiling candidates and tie convention are explicit. This context difference
was checked directly; a new independent review must inspect the current text.
It does not remove the matrix blocker or grant manuscript approval.

Unblocked balancing exchange, independent graph predicates and dispatcher
regressions passed **100 tests**, with both native tools configured and no skips.
One numerical process ran at a time using the existing research interpreter;
the independent review used the repair source via explicit PYTHONPATH. No new
comparison metrics, historical outputs or dependency pins were changed.

Identity records, the preserved review suite and both test logs are in
`dump/1025024643-coloring-integration-gate/`. The server checkpoint manifest
records the append-only dispatcher handoff. Shared preprocessing/mappings,
MC reduction/balancing integration, SAT/structure scheduling, decomposition,
workspace/routing/precision controls, post-pilot protocol freeze, complete-search
FT and separate RUS accounting, iteration/noise and scaling studies, full
comparisons and evidence-gated manuscript/final reviews all remain in scope.
