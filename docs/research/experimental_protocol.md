# Post-pilot comparison protocol — 28 October 2026

Status: **partial protocol fixed for this bounded batch, not a full-study freeze**.
Task `controlled-comparison-study-1028023823` implements Tasks 2/4. Independent
review must decide on exact source and evidence hashes before scientific use.
No superiority, complete-paper, FT/RUS or ideal-amplitude approval follows.

The saved K3/K5/myciel3 pilot at
`/Users/mar/codex-work/logique/dump/1025012448-coloring-study/` was inspected:
its config requests five methods/four baselines, R1/R2/R3, j=0/1, seed7,
32 samples and positive/negative witnesses. Its 144 complete cases and 720
logical rows are historical. The inverse-StatePreparation QPY defect found in
`stage_controls_qpy_review.md` prevents retroactive semantic admission.
`qpy_semantic_admission.md`, `qpy_representation_changes.md`,
`restoring_mcx_admission.md`, `restoring_mcx_representation_changes.md`, and
component width/instruction/depth admissions were inspected before fixing these
parameters. Those corrections change representation and accounting; they are
not measured synthesis improvements. New evidence never overwrites the pilot.

## Fixed comparison contract

All nine original inputs, in order: K3, K5, myciel3, grid6, K10, K20, myciel4,
myciel5, 2-Insertions_3. The unrelated zed-city input is not one of the nine.
Use each file's `x colors` value; remove all saved precolors explicitly and
record them. Sort original integer labels and allocate contiguous LSB-first
words, including isolated vertices. The baseline adapter normalizes labels to
0..n-1 and translates its MSB-first words. All methods mark **proper colorings**.

R1: H preparation, complete predicate. R2: actual valid-color unitary
preparation at original k, complete predicate. R3: same preparation at original
k, edge-only predicate obtained by compiling at 2^ceil(log2(k)) colors.
The R3 predicate is equivalent on preparation support, not all binary codes.
Use actual emitted A inverse and positive signed A(2|0><0|-I)A†. Fix j=1,
seed7 for finite validation and common lowering, samples32 above12 data bits;
exhaustive monomial validation through12. This comparison is resource counting,
not an executed amplitude/noise study. No statevector or full Operator is
allocated by the harness. Quantum regressions retain <=5-wire dense operators
and <=18-wire statevectors; wider dense historical tests are excluded explicitly.

For every graph, deterministic DSATUR (sorted tie breaks, color symmetry,
10000 search-node cap) supplies a positive witness checked by `is_valid`.
No found solution means unknown, never unsatisfiable. Supplement with all-zero
edge violation, a first-vertex invalid code when available, and maximum binary
boundary. Log exact assignments and the actual exhaustive/sampled phase/XOR
coverage. Sampled checks do not prove unrestricted Boolean equivalence.

The five synthesis methods are xag, aig_bennett, xag_bennett, klut_bennett,
best_fit. Keep existing mapping defaults, k-LUT4, best-fit cuts16/4. Explicit
profiles shared across those representations are:

- `none`: original left-fold encoder, explicit common cleanup without refactoring.
- `refactoring`: same encoder, common native bidecomposition refactoring before
  representation conversion. Both exported preprocessing boundaries are checked
  against the independent graph predicate with the selected finite coverage.
- `balanced`: balanced AND/OR encoder and common native `none`. Associativity,
  identical leaves and primary-input order justify the encoder transformation;
  both exported boundaries are independently checked with recorded coverage.

The four hand-built baselines (original/simple/minimal/balanced) and the two
separately named structure references (sequential/parallel) do not consume a
Boolean preprocessing profile. Their metadata says not applicable. Repeating
these fixed references in profile strata supplies matched comparisons, not a
claim that a Boolean optimizer transformed a baseline. Structure parallel retains
private per-layer comparator scratch; sequential retains shared comparator
scratch. Never report parallel depth at sequential width. The sb_original
multiple-higher-neighbor defect remains an explicit exclusion, never repaired
by relabeling it as another method.

MC reduction and standalone cut/ESOP balancing remain **open**: `balancing.py`
checks per-pass SAT equivalence, but no admitted end-to-end synthesis profile
connects that tool or tweedledum MC optimization here. They are not aliases for
`balanced` or `refactoring`. Low-T mapping, SAT mapping and conditional-workspace
synthesis are outside this runnable comparison. Native functionality is reused
from the private admitted executable, SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No bridge rebuild or pin change is needed. Root's old executable is not used.

## Accounting and execution budgets

Save raw, preparation, oracle, diffusion and complete j1 search independently.
Primary logical QPY recursively resolves emitted definitions, retaining closed
MCX and numeric scalar phase. This is mixed granularity; it differs from old
opaque counts. Readback signatures check classes, ordered wires, parameters,
control states and phase. Recount every accepted cost directly from saved QPY.
Measurements and barriers are excluded from gate counts; barriers still fence
logical depth and parallel scratch reuse. QPY now preserves these barriers.

Separately attempt `clean_tree`/`fresh_zero` and its unrouted U/CX common basis,
optimization0, seed7. Existing admitted subset: original k<=8, data<=21,
j<=2, MCX<=20 controls, recursive depth32/100000 visits. Scratch is fresh,
zero and disjoint between raw/preparation/S0; no cross-role borrowing. Actual
lowered prefixes are inverted, including their phases. Over-limit conjunctions
and unsupported gates fail explicitly. Common results do not silently use a
no-ancilla Qiskit default for a failed clean-tree request. Logical rows retain
`qiskit_default_uncontrolled` to describe their unresolved MCX policy, not a
restoration/decomposition guarantee. Common-basis wider transpiler equivalence
is not generally certified by existing admissions and requires review.

Report allocated data, output/kickback, constraints, explicit MCX scratch and
unknown residual backend workspace. Unknown is not AND-only. Reserved register
size is not measured live peak. Timings retain overlapping native-combined and
Python synthesis scopes; optimization/mapping split times and true live peaks
remain unavailable, not zero.

One ordinary numerical child at a time. Child budget30s, total900s including
recount, with120s reserved for a separate bounded recount child. All compiler,
BLAS/OpenMP/Accelerate threads1. Preallocation structural caps: data256,
vertices64, edges256. Native graph allocation is polynomial for these fixed
inputs; no dense arrays are requested. Post-assembly acceptance caps:4096
allocated wires,50000 top-level instructions,50000 mixed-granularity depth.
These latter caps do not prevent internal native/Qiskit allocations.
Process-group RSS is sampled and the group killed at6GiB; wait4 high-water
is recorded with its descendant-inclusive OS scope. This is an observation and
termination budget, not a hard instantaneous allocation bound. A denied RSS
probe is unavailable evidence, not a zero measurement. The 8GiB host requires
measured successful RSS below7GiB. Timeout/memory/failed children retain logs
and partial artifacts but contribute no accepted summary rows. Missing work
at the cumulative deadline remains not-run-budget. Every structurally eligible
case is attempted in the fixed order; no manual selection by performance.

## Aggregation and remaining freeze requirements

Select the cheapest **available validated baseline** independently per graph,
metric and exact regime/component/profile/MCX/workspace/level/j/seed/target/
precision context, recording available baseline names/count. Report cost ratios,
geometric means and wins/ties/losses. Never average over weaker baselines.
Groups without any valid baseline remain unmatched, with no invented ratio.
Losses, exclusions and denominators remain visible beside any summary.

FakeTorino routing at seeds11,23,37,41,53, target snapshots/duration; static
whole-search rotation budgets1e-3 (sensitivity1e-2/1e-4); broader MCX/dirty/
conditionally clean policies; connected CEC-checked MC/cut/ESOP profiles; full
compiler-stage and live-workspace instrumentation remain full-study open rows.
Routing helpers and cost models exist but do not establish these measurements.
Independent exact-hash review, completion of these controls and predefined
remaining experiments are necessary before a full protocol freeze. This document
records post-pilot decisions before this batch's numerical study; later findings
must be appended with dates and hashes, never silently edited into a prior freeze.
