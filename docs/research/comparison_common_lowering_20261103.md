# Matched common lowering on K3 and grid6 — 3 November 2026

Task `comparison-common-lowering-1101052342`, session
`01a1a451-473c-7d93-8f2d-d03990421f6c`; assigned worker branch
`codex/coloring-comparison-common-lowering-1101052342`, base `de230cc`.
**Bounded execution finished; outcome CONTINUE for the remaining comparison
scope. New harness and measurements are PENDING exact independent review.**

Checkpoint within this assigned worktree:
`dump/1103211324-comparison-common-lowering/checkpoint.json` (RUN).
No result below is an independent scientific admission or a nine-graph claim.

## Scientific question and measured tradeoffs

Does a lower allocated width survive elementary compilation when candidates and
baselines use the same restoring MCX policy? On this two-graph subset, width,
U/CX instruction count and dependency depth give different answers. The
unprecolored K3/k3 and grid6/k2 each have six data wires. All R1/R2/R3 cases use
j=1, seed7, profile `none`, native floating rotations, unrouted U/CX basis and
optimization level0. R1 uses H/complete predicate, R2 valid-code preparation/
complete predicate, R3 valid-code preparation/domain-free predicate. Original
input precolors are explicitly removed; this is not precolored-instance research.

Selected **complete search** measurements, including preparation and one matching
oracle/reflection iteration:

| Graph/regime | Method | Allocated wires | U+CX instructions | CX instructions | U/CX depth |
| --- | --- | ---: | ---: | ---: | ---: |
| K3/R1 | best_fit | 12 | 897 | 312 | 521 |
| K3/R1 | sb_simple | 20 | 432 | 150 | 141 |
| K3/R1 | sb_minimal | 15 | 888 | 346 | 337 |
| K3/R3 | best_fit | 10 | 213 | 69 | 107 |
| K3/R3 | sb_simple | 14 | 300 | 105 | 137 |
| K3/R3 | sb_minimal | 13 | 402 | 151 | 201 |
| grid6/R1 | best_fit | 13 | 891 | 300 | 490 |
| grid6/R1 | xag | 15 | 376 | 136 | 214 |
| grid6/R1 | structure_sequential | 22 | 238 | 88 | 85 |
| grid6/R1 | structure_parallel | 22 | 238 | 88 | 90 |
| grid6/R1 | sb_simple | 22 | 294 | 102 | 91 |
| grid6/R1 | sb_minimal | 16 | 468 | 198 | 207 |

The denominator is selected independently per metric from all three available
corrected baselines: sb_simple, sb_balanced and sb_minimal. For example, K3/R1
best_fit has width ratio 12/15=0.8 against sb_minimal, but instruction ratio
897/432=2.076388889 and depth ratio 521/141=3.695035461 against sb_simple.
K3/R3 instead has ratios 10/13=0.769230769, 213/300=0.71 and
107/137=0.781021898. This comparison changes both predicate and preparation
between R1 and R3; the separately saved R2 rows retain the intervening control.
No mechanism is established from that contrast alone.

The grid6 sequential structure search uses 238/294=0.809523810 of the strongest
baseline's instruction count and 85/91=0.934065934 of its depth, but
22/16=1.375 times its strongest width. The parallel schedule has depth90 at the
same width and instruction count; a parallel source schedule gives no automatic
compiled-depth improvement here. These are deterministic compiler observations,
not shot estimates or confidence intervals. Different seeds/optimization or
rotation approximations could change the numbers.

## Complete denominator and evidence ledger

Twenty graph/method groups cover five native methods (xag, aig_bennett,
xag_bennett, klut_bennett, best_fit), two structure schedules and three baselines.
Every group returned all three regimes in both fresh logical and restoring/common
runs, with no failed or excluded selected cases. There are 900 saved QPY circuits:
300 logical,300 restoring-MCX,300 U/CX, including raw diagnostics and four services.
Every QPY hash and width/gate/depth/type metric was freshly read back and recounted.
All baseline denominators contain three methods. Exact context equality was
checked across 90 component/graph/regime/level contexts, retaining graph hashes,
iteration,seed,profile,MCX,basis,target,precision,representation and workspace.

| Metric level | Oracle/search details | Wins | Ties | Losses |
| --- | ---: | ---: | ---: | ---: |
| Logical, resolved mixed granularity | 252 | 102 | 2 | 148 |
| Restoring MCX, CCX retained | 252 | 78 | 0 | 174 |
| Common U/CX | 252 | 51 | 3 | 198 |

These are repeated metric/context comparisons, not independent trials or a
success percentage. Adding preparation/diffusion yields504 details per level;
common totals are51 wins,255 ties,198 losses. Raw rows are excluded from ratios.
No routed/FT values are inferred from these counts.

RUN contains `summary.csv`, `common-search-table.csv`, `artifact-recount.json`,
`strongest-details.json`, original per-group requests/configs/manifests/QPY,
command receipts and all logs. `requested-open-ledger.json` explicitly retains
14,850 graph/method/profile/regime/metric-axis entries:180 completed cost entries
(each represents five components),3,870 unrun cost entries,6,750 unrun routing
entries and4,050 unrun FT entries. Routing seeds11/23/37/41/53 and whole-algorithm
precisions1e-3/1e-2/1e-4 remain open. Profiles none/refactoring/balanced/
mc_reduction/cut_esop_balancing retain separate obligations; source integration
elsewhere does not complete this experiment. Additional policies, including
analytical Dutta and constrained throwaway use, are listed separately without
invented costs. sb_original stays excluded.

## Source, proof and resource boundaries

Reviewed profile source253e850 and component sourcecf678f7 were deliberately
cherry-picked as ef82766 and c8aa562 with no conflicts. All13 prerequisite files
match their admitted Git blobs exactly. Harness/config/tests are db389b2,
separate from this measurement report. The exact new source and evidence still
require the assigned independent reviewer; the worker cannot admit its own work.

The reused source applies clean_tree/fresh_zero to comparator/domain/final
conjunction, diffusion, native k-LUT/best-fit and structure blocks. Actual emitted
prefix inverses and dedicated disjoint scratch pools are retained. Reusable
lowering uses qubits_initially_zero=False and num_processes=1. Scratch is an
initially clean precondition, and allocated reserved width is not measured live
workspace. All new source checks are exhaustive over64 assignments, including
both marking and nonmarking branches; signed phase/XOR checking uses the existing
1e-9 numerical tolerance and standard-gate conventions. This is not a new
interval proof or full saved-U/CX coherent equivalence check. The previously
reviewed clean-tree construction and corrected component translation are reused;
independent review must assess their exact composition with these artifacts.

The exact CEC decision0fc7d72 admits103 saved wide oracle/search pairs, with12
remaining unresolved and excluded. Its report hash is
`7fba7222f010f6447106bc71c31181a24b37e07fc5f1e212c3182386ec62a0da`.
Those are different saved artifacts, not certificates for the new U/CX files.
General checker preallocation/full-input validation remains restricted. No CEC
retry or duplicate of the44 returned wide groups occurred. Classical structural
preflight inspected all nine inputs before quantum constructors; the frozen
slice admits<=12 data bits,k<=8,vertices<=8,edges<=16,constraints<=20. The seven
other graphs are outside this slice, not reported as compiler failures.

Before allocation the frozen config declares60s/child,600s cumulative,2GiB
process budget,serial execution and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit
parallelism1. Scientific children use classical verification, no statevectors,
dense operators or density matrices. Validation fixtures use<=7 vector wires
and<=5 operator wires; original staticFT dense4 remains unchanged. All21 execution/
recount children finished in30.939922s cumulatively (31.105418s outer boundary),
max2.027818s/child, maximum Darwin wait4 high-water173,326,336bytes. Nineteen
regressions passed in1.275662s supervised,148,602,880bytes. Black/Ruff pass.
ps sampling was denied; group RSS is null and no OS hard memory cap is claimed.
These are bounded checks, not full-suite/final-environment admission.

Only the existing absolute root venv Python and explicit asserted candidate
imports were used. Unchanged native executable hash6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a
was explicitly selected and verified; root default and binaries/pins were untouched.
Initial Git sandbox denial was resolved with scoped escalation; initial unused
import lint failure was corrected before execution. All failures/transcripts and
historical artifacts remain. No C5,models/subagents,push,sync,API/paid fallback,
purchase,hardware,physicalQEC or conditional-workspace research occurred.

## Exact continuation

First independently review db389b2 and the new900-circuit inventory, source
checks, strongest-baseline contexts and retained losses; integrate only exact
admitted paths/commits. Correct any finding in a new commit and review those
bytes. Then extend missing common-lowering groups after a reviewed wider
pre-constructor resource policy and relevant all-input equivalence; keep the12
wide UNKNOWN chains sample-qualified. Complete the explicit remaining profiles,
MCX policies, five routing seeds and three FT precisions with actual circuits,
not logical extrapolation. No further launch or waiting is performed here.
