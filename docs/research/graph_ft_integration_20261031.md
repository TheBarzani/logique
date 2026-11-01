# Exact graph FT integration — 31 October 2026

Task `graph-ft-integrate-1030020413` is **COMPLETE** on
`coloring-paper-revamp-codex`. Assigned base `e90adf3`; actual intake
`8557b5551b37f382f3837e0d3d9f60606ff9a56c`.
Checkpoint: `dump/1031200049-graph-ft-exact-integration/checkpoint.json`.

Independent review `78107e17564fc70c50f21235c549d057b73c4260` **ADMITs** exact
correctness commits `a7281df4021838688b4a071d549a30520f956ee4` and
`a65e6729abd6eee79940982e3e7d96fd1b6ca6ba`, and separately bounded evidence
checkpoint `b84b2df419e197b50cf836107443cfb1d7bac032`.
The [verbatim independent review](graph_ft_independent_review_20261031.md)
SHA256 is `476cb937e3ce5c38a48f56c9c1d5488f0124a67c4ba1257b26fa786fd503d137`.
It matches the review worktree and committed Git blob. Worker checkpoint
[GRAPH_FT_CHECKPOINT.md](../../GRAPH_FT_CHECKPOINT.md)
is preserved byte-for-byte; its pending-review text is historical, superseded
by this exact decision and independent review.

## Integrated source and evidence

Correctness commits integrated without conflicts as `4c58971` and `6d590a8`.
Separate evidence checkpoint integrated as `80dcf85`. No semantic edits were
made to the reviewed bytes. Only the two new correctness paths and separate
worker checkpoint entered these commits.

| Path | Final SHA256 |
| --- | --- |
| `src/logique/benchmarks/graph_ft.py` | `ae6c3f93c3ef2fb0abc279bafe300ef5c986f1e14700092a3dde903e08adb220` |
| `tests/test_graph_ft.py` | `4e8c1396a0da7e9b4c2cec19116d19422ef01214b8080ed1bd7bc390514dabc9` |
| `GRAPH_FT_CHECKPOINT.md` | `fda29a590de9146449751a6beb0a72d191e5650069c6a302231ff093e7910f4d` |

All 409 entries in candidate final evidence inventory match sizes and hashes;
manifest SHA256 `6f20f0abb3870f251652f80a8b0ae860b67d02d5ff3719d4d83796ccb87132da`.
Command ledger SHA256
`e1882a07601993560b0999f959cba881f66db761aab5e6e285133022f02a063d`.
All 35 independent-review inventory entries and its checkpoint-bound command
ledger match. The independent review covers 60 emitted QPY circuits, 192 clean
columns, actual emitted adjoints, component/full-search costs and three reproduced
precision failures. This coordinator hashes those artifacts without replaying the
large emitted searches or presenting new full-search measurements.

Admission is restricted to vertices 7 and 11, edge (7,11), k=3, LSB-first,
`xag_bennett`, preprocessing `none`, explicit restoring Gray-code MCX, and clean
computation workspace. R1/R2 use the complete predicate; R3 removes domain checks
and retains its own edge-only numeric target. Original recursive numeric targets,
rotation allocations, norm allowances, scalar phases and inverse reuse remain
binding. Original staticFT pilot and its dense-four limit are unchanged.
No dirty-workspace, dynamic/RUS or general ideal-amplitude certificate follows.

Exactly 12 completed study rows plus one identical-circuit final-source smoke
are admitted numerical observations. Three j=1/1e-4 failures remain failures,
with no search costs or analytical replacements. Matched primary j=1 costs are
271982 T for R1, 353792 for R2 and 353624 for R3. These preserve the valid-preparation
losses. First-peak raw charges compare R1/j=1 with valid/j=0; this does not
optimize cost per verified solution. H/j=0 already has zero T and proper success
3/8. General `achieved_break_even` remains null. No strongest-baseline or
full-paper claim is admitted.

## Candidate and integrated validation

Candidate imports explicitly resolve to its assigned `src`: **247 passed**,
including all graph, original staticFT and rotation regressions. Integrated
imports resolve to root `src`: **280 passed, 37 deselected**, the same 247 plus
33 non-integration SAT adapter tests. The 37 deselections are SAT integration
cases requiring the distinct SAT executable; graph tests have no deselections.
Selected Black/Ruff pass. Focused mypy uses the worker's reviewed
`--follow-imports=skip` scope. A stronger `--follow-imports=silent` probe
reports one optional-circuit annotation error at graph_ft.py:422; its failed
receipt remains and no clean transitive type-check claim is made. Preparation
is always emitted by compile_search, including j=0, as the executed regressions
check; the shared component annotation also permits unused O/S0 to be null.
Any optional-circuit type narrowing needs a separate exact-source review. No full-suite,
notebook, build, historical replay or full-study admission is claimed.

The dependency audit found separately admitted SAT adapter changes in root
`api.py` and `native.py`, matching `622b950` and its
[independent review](native_mapping_independent_review_20261031.md).
Their diff retains the non-SAT Bennett path used here; no changed dependency
bytes were merged or invented. Fresh root R1/R2/R3 constructions with the
prescribed executable recheck 96 clean columns across original/lowered oracles.
All three A/O/S0 source words match saved reviewed QPY exactly, including ordered
standard leaves, wires, parameters and scalar phase. Native widths remain
13/13/7. This exercises the actual integrated dependency boundary.

Executable SHA256 remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
at the explicit native-contract private-build path. Its build provenance is
hashed in `preservation.json`; saved native metadata remains in each original
row and the fresh construction directories. No rebuild or binary replacement
occurred; the root default old binary was not selected.

## Resources, failures and next action

Budget declared before allocations: serial child<=120s,cumulative<=600s,
process<=6GiB,arrays<=64MiB,statevectors<=18,local dense<=5,all compiler/BLAS/
OMP/Accelerate/Rayon/Qiskit parallelism1. Actual new construction statevectors
are <=13 and dense operators four wires; the regression includes a five-wire
local S0 check. The original pilot remains dense4. Existing root venv Python
only, explicit PYTHONPATH and asserted imports; no sync/install.
Supervised checks, including failures, total 67.678159s; maximum child
high-water is 222,789,632 bytes. Receipts record commands, exits, elapsed time
and wait4 child high-water,
possibly including reaped descendants; no aggregate RSS or hard OS memory cap
is claimed. Deterministic construction has no sampling seed; original reviewer
seed1030020413 remains attributed to its saved independent probes.

Failed receipts remain: the first dependency audit detected the admitted SAT
adapter drift; the second guessed the wrong review inventory filename, then the
actual inventory passed. Both script revisions/logs remain. The first root
regression mistakenly included SAT execution using the prescribed older graph
binary: 31 failures/286 passes, predominantly unsupported SAT controls. This
was a test-selection error, not graph evidence or a SAT regression diagnosis;
the fresh correctly scoped check above passes. Its entire log/artifacts remain.
Initial cherry-pick failed on sandbox `.git/sequencer` creation; scoped automatic
escalation succeeded. No automatic approval-review rejection occurred. Git/read
inspection events have tool command/exits, without independently measured RSS;
that limitation is recorded separately from supervised receipts.

README remains SHA256
`73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`.
No histories, archives, pins, original failed/partial artifacts, candidate/review
sources or queue definitions were changed. No models/subagents/Codex launch,
API/paid fallback,purchase,hardware,physicalQEC,precolored or conditional-workspace
research occurred. No push; dispatcher alone publishes integration HEAD.

**Scientific BLOCK:** fixed-options j=1/1e-4, broader graph/method/precision
coverage, achieved preparation break-even, and full-paper conclusions.
The existing full-research successor owns further evidence work. Inspect the
saved failing angles/trials and preflight stronger SK operation/state-work,
time/memory budgets before any new tight-precision run; otherwise retain
unsupported status. A meaningful success-cost objective must price verification,
Clifford/runtime terms and compare schedules including H/j=0, followed by exact
independent evidence review. Keep the separate dynamic-RUS chain and original
pilot scope unchanged. This assigned integration has no unfinished prerequisite
and needs no polling continuation.
