# Exact bounded whole-circuit MCX integration — 31 October 2026

Task `mcx-whole-integrate-1030020413` is **COMPLETE** after exact integration
and validation. Scientific decision: **ADMIT only the independently reviewed
opt-in source and bounded resource observations; BLOCK broader MCX/FT/paper
claims.** Checkpoint: `dump/1031150845-mcx-whole-exact-integration/batch.json`.
Actual root intake was `0589310` (assigned historical base `e90adf3`), branch
`coloring-paper-revamp-codex`. Dispatcher alone publishes integration HEAD.

## Exact admission and preservation

Independent review `3f76e781f6c2b1134689e5aed6729b8961d7f08d` is copied
[verbatim here](mcx_whole_review_20261031.md), SHA256
`394ba15e01b4e3b43fcc3d45c5c3ae969e7bfb4871f5c24a8a23ed24a23c500e`.
Candidate HEAD remains `751a4eb70eb31d54005410a11153d7d97187a927`.
Only the three explicitly admitted owned source/test/tool paths were integrated:

| Candidate correctness commit | Root correctness commit |
| --- | --- |
| `dc304e9969856f4332fe7f0fba9c18f491c2ba2b` | `9670b88fc6607e8ae8946f7822eb55f20aa89678` |
| `865deab66564dfbe8807ca3e7c46d8ec0d13c222` | `fdefc1904066766a01fd2d1af35aa4e15059100f` |

| Exact integrated path | SHA256 |
| --- | --- |
| `src/logique/benchmarks/mcx_study.py` | `7518d7c164ebb8e307e08ed284bea79194286c70813a885dcb8afad2e9d2371e` |
| `tests/test_mcx_study.py` | `ca1009fada74377c961ee47e1311f2e0bc2b4c7836b6b35cfd5d5de47862a002` |
| `tools/run_mcx_study.py` | `322897eb72a1eb53804d7361831bd8753ff10c0c17c953b9a203bec6f655af4d` |

Both cherry-picks applied without conflict; no new semantic bytes were invented.
Root's already admitted QPY changes affect the wide-control branch; these tiny
whole fixtures and <=20-control templates do not enter that branch. SAT adapter
changes require explicit strategy/budgets; this study uses existing default
methods. Reused costs are identical. Integrated tests exercise current assembly,
QPY and native-default dependencies without replacing them with stale versions.
No new native build or dependency-pin admission is made.

The [original candidate checkpoint](mcx_whole_candidate_checkpoint_20261031.md)
is preserved byte-for-byte, SHA256
`46ab570febc88fb6acb03195a92f99c2ae4a221a0c4b7d8377b29e0c72db6143`.
**Binding erratum:** its sentence “Clean policies allocate zero scratch” is
rejected literally. Read “Clean policies allocate zero-initialized scratch.”
For example, clean_tree with four controls appends two wires. The historical
checkpoint is evidence with this erratum, not independently admitted prose in
its entirety. It was not cherry-picked into the root top level.
This documentation/evidence commit is separate from both correctness commits.

## Evidence actually admitted

Saved candidate evidence remains under the candidate worktree's
`dump/1031080140-mcx-whole-circuit/`; independent evidence remains under the
review worktree's `dump/1031145904-mcx-whole-independent-review/`.
The coordinator verified 47,552 unique evidence identities from saved inventories,
exact Git source/review identities, all 55 selected shards' source bindings and
all 1,452 whole-request input hashes. Forty-four shards bind to dc304e9 and
11 corrected triangle shards to 865deab. No experiment was replayed or relabeled.

Selected evidence has **1,608 completed rows / 42 exclusions**: 189 isolated,
1,419 whole; nine Gray exclusions at controls12..20 and 33 known sb_original
triangle exclusions. Gray11 executed; its 12,283 common gates and 6,140 CX are
observations within the frozen 50,000-operation constructor bound. Planning
coefficients are not hard allocation guarantees. Dutta remains theorem-only,
34 analytical rows / 20 range exclusions, with the published discrepancy retained.

Exactly 1,335 whole cases have bounded coherent evidence; **84 completed whole
cost rows exclude full statevector validation**. Review independently checked
4,005 oracle/diffusion/zero-reflection actions, 55 fresh j2 searches and 352
forward plus 352 marked-actual-inverse template actions through six controls.
Its 26,676-representation recount and 396 bounded representation action checks
remain qualified as in the exact report. Larger template/translation semantics
are not certified by a count recount. Dirty/conditional references and held
throwaway scratch use actual emitted inverses; unmirrored throwaway marking,
preparation and S0 explicitly substitute restoring clean_tree.

The 1,411 wins / 1,194 losses / 2,555 ties are 5,160 metric diagnostics against
matched clean_tree cases, not independent experiments or a superiority result.
Residual rotations are unpriced; total FT T-count/T-depth/precision remain null.
No routed target/calibration was selected. No nine-graph/strongest-baseline,
all-width, static-FT, RUS, physical-QEC or full-paper certificate follows.

## New validation and failures

Existing `/Users/mar/codex-work/logique/.venv/bin/python`, explicit candidate then
root PYTHONPATH with import-path assertions, prescribed unchanged private binary
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No sync/build or root-default binary. Commands/exits/time/RSS/environment live in
`commands.jsonl`; exact hashes and selected ledger checks in `validation.json`.

| New check | Result | Supervised seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Candidate MCX tests | 195 passed | 4.614945 | 160104448 |
| Integrated MCX plus bounded assembly/QPY/default-native checks | 243 passed, 284 deselected | 5.134460 | 170082304 |
| Selected Black | 3 files unchanged | 0.284226 | 36438016 |
| Selected Ruff | passed | 0.112601 | 19628032 |
| Evidence identity audit v2 | 47552 identities verified | 5.377175 | 103809024 |
| Integrated hashes/source bindings/input hashes | passed | 3.195862 | 129155072 |

The pre-array plan declares 2GiB process memory, <=120s children / 600s cumulative,
statevector<=18 and denseOperator<=5; original staticFT pilot dense4 unchanged.
Numerical children were serial; compiler/BLAS/OMP/Accelerate/Rayon/Qiskit
parallelism1. Terminal Darwin wait4 high-water may include reaped descendants;
no hard cap, live/group RSS or complete descendant visibility is claimed.
Regression seeds remain7/74/75; no new scientific seeds or metrics were generated.
This is not a full-suite/native-build/notebook/historical-replay validation.

Initial strict audit failed because the review inventory captured its finalizer
log while empty and command ledger before appending the final receipt. Preserved
finalizer source proves this order; fresh audit verifies final log JSON equals
the batch summary, old ledger hash equals all-but-final receipt bytes, and final
receipt exit0. Both old expected and current actual identities remain recorded.
No candidate/result/source mismatch was found; no history was repaired in place.
Initial cherry-pick failed128 at sandbox `.git/sequencer`; scoped automatic
escalation succeeded. No automatic approval-review rejection occurred.
All failed/partial logs and scripts remain. README, lockfile, queue, pins,
archives, old128 run/history and candidate/review worktrees remain untouched.

## Actionable remaining scope

`full-research-successor-1030020413` should consume this exact bounded admission
and its exclusions, not rerun this integration. Before broader MCX claims,
obtain independent wider-template and cross-representation semantic validation,
then execute matched nine-graph comparator/domain/conjunction/diffusion and
k-LUT/best-fit/structure comparisons under fresh preallocation/time budgets.
Routing needs common target/calibration/seeds; total FT needs actual rotation
synthesis and whole-search precision. Keep Dutta analytical unless a separately
validated circuit exists. Retain all losses and excluded cases. Existing graphFT,
RUS, comparison, scaling and noise chains retain ownership of their distinct
scope. No new queue entries/model launches/pushes were made here.
