# Heralded two-vertex dynamic k=3 RUS marking and reflection

Task `dynamic-rus-graph-1101052342`, 9 November 2026, America/Montreal.
**Bounded implementation/execution COMPLETE. Independent scientific review PENDING.**
The full research/manuscript evidence gate remains open. This worker neither
integrates root nor pushes; the dispatcher owns publication.

Branch `codex/coloring-dynamic-rus-graph-1101052342`, assigned base
`de230cce74089344343fcdf1c12d553cc4cf8607`.
Correctness-only commit **`48b820388712a247f91aab8e8459543bb036bd1d`** owns exactly
`src/logique/benchmarks/dynamic_graph_rus.py` and `tests/test_dynamic_graph_rus.py`.
This separate checkpoint/report changes no library code or historical metric.

Evidence run, created with `logique.paths.new_dump_directory` using local time:
`dump/1109163219-dynamic-graph-rus-execution/` in this assigned worktree.
Its `checkpoint.json`, `summary.json`, `cases.json`, `branches.json`,
`inputs.npz`, `provenance.json`, six QPY circuits and per-case arrays retain the
actual executed maps, reference states, flags, resources and instructions.
`study.py` is the executed worker study. It is not an independent review.

## Scientific result and scope

The ideal, uncontrolled one-vertex instruments **can compose into a heralded
coherent graph reflection**. No obstruction to this particular classically
sequenced composition was found. This is not deterministic finite-cap Grover,
quantum control of RUS, an unlimited execution, static A/A-dagger substitution,
a noise result or a resource advantage. Independent admission of the new exact
source/evidence is still required.

The graph has two independent two-bit vertex registers and one edge, k=3,
colors 00,01,10. The complete predicate marks the six unequal valid pairs and
rejects every pair containing 11. Data order is MSB `(v0.h,v0.l,v1.h,v1.l)`;
references follow. Event/Qiskit wire labels are `(retry,scratch,data...,refs...)`.
The executor propagates primitive gate amplitudes, Z projections and reset;
it never evolves inputs with supplied Kraus matrices. It retains zero-norm
records and stops on the first exhausted invocation, before every later stage.
Each record specifies invocation index, vertex, direction, reached outcomes,
completed/abort flag and exact terminal prefix state.

Admitted primitive dependency `78c98a1` is already an ancestor of the assigned
base. Its source/tests match the integrated admission hashes and current root;
they were deliberately read, hash-checked and imported from candidate `src`.
No stale dependency, original dynamic source change or cherry-pick is hidden.
The generic elementary tensor/index action from that dependency is reused on
the new graph axes; this wider composition requires the new independent review.

## Exact channel derivation

Use the admitted one-vertex quantities

$$\alpha=(1-i)\sqrt{3/8},\quad\beta=(1+i)/\sqrt8,\quad
K^{f}_r=\alpha\beta^{r-1}V,\quad
K^{i}_r=\alpha\beta^{r-1}V^\dagger.$$

At cap c, forward exhaustion is `beta**c I`, inverse exhaustion is
`beta**c E-dagger`. E-dagger is the actual expanded inverse, paid **once before
trials**, including c=0. It is never repeated on failure. Fresh inverse path
phases are retained, not conjugated sampled-forward phases. Outcome/reset and
classical control are ideal, and fresh zero helper inputs are assumptions.

Let `A=V tensor V`, `S0=2|0000><0000|-I`, `D=A S0 A-dagger`. Reflection executes
inverse vertex1, inverse vertex0, S0, forward vertex0, forward vertex1, in that
time order. Completed record r has map
`alpha**4 beta**(sum(reached_attempts)-4) D`. Its probability is data-independent.
For `s=1-4**(-c)`, the sum of completed branches, also on arbitrary references,
is exactly `s**4 (D tensor I) rho (D-dagger tensor I)` in ideal gate algebra.
This is a trace-decreasing channel, not a deterministic unitary certificate.

Every earlier abort retains its actual prefix: completed local maps and any
already reached mark/S0, followed by beta**c I or beta**c E-dagger on the
exhausted vertex. No later inverse, S0, extension, marking or measurement runs.
The full flagged instrument is
`sum_record |record,flag><record,flag| tensor K_record rho K_record-dagger`.
All branch effects sum to identity. Discarding flags/records generally produces
a random-unitary mixture instead of the desired reflection. At cap4, the saved
Schmidt-rank-eight entangled input has discard-flag fidelity **0.9854492967096983**
to its ideal reflected output. The completed subchannel preserves its intended
coherent action; quantum-controlled RUS remains outside scope.

Marking uses six explicit point phases, each implemented by a clean-scratch
compute, CCZ and uncompute, with exact seven-T Toffoli expansions into H/T/Tdg/CX.
No arbitrary-angle rotation or hidden multi-control gate is used. Each point
costs21 T; the six-point marker costs126 T. S0 costs21 T and includes explicit
XZXZ=-I so its absolute sign matches `2|0000><0000|-I`. Scratch is restored;
phase-sensitive all-input and actual QPY checks corroborate the gate algebra.
This is deliberately unoptimized and establishes no optimality or comparison.

## Executed evidence, including losses

**23 cases / 1,183 terminal records**, maximum341 per case. prepare, mark,
reflect and mark-then-reflect each cover caps0..4; full prepare-mark-reflect
covers caps0..2. Full-search caps3/4 are preallocation exclusions:1,093/5,461
records exceed341. No pruning or omitted abort is used to fit the limit.

All16 data columns are executed in four-column batches. The independent
column formula in the saved study checks every completed and aborted prefix,
without phase fitting. An untouched three-wire pure reference has Schmidt
rank8, seed20261109. Four mixed-purification columns and a full-rank16x16 graph
density matrix test mixed/reference channel action without wide reference
operators, Choi matrices or density matrices. Six saved QPYs are reloaded and
replayed using Qiskit Statevector primitive evolution, explicit projections and
classical conditions. These cross-checks belong to this worker, not independent
scientific review.

| Numerical check | Maximum absolute residual |
| --- | ---: |
| Phase-sensitive branch map entries | 1.0103182026100664e-14 |
| Completed/abort effects versus scalar identities | 2.842170943040401e-14 |
| Pure/mixed-purification reference amplitudes | 3.251669631848525e-16 |
| Completed full-rank graph-density channel entries | 3.094747024500797e-15 |
| Loaded-QPY primitive replay entries | 6.138078244619834e-17 |

Matrix/state tolerance is3e-13, complex128. Probability-weighted resource totals
use relative3e-13 with absolute3e-13 near zero; largest relative residual is
3.3756713448514735e-14. These are floating-point corroborations, not certified
operator-norm bounds or uncertainty intervals. No stochastic shots, sampling
confidence intervals or hardware measurements exist.

| Executed case | Terminal records | Completion | Observed unconditional stop T |
| --- | ---: | ---: | ---: |
| Preparation cap4, two invocations | 21 | 0.9922027587890625 | 9.278717041015584 |
| Reflection cap0 | 1 | 0 | 1.9999999999999967 |
| Reflection cap1 | 5 | 0.31640625 | 22.257812499999773 |
| Reflection cap2 | 31 | 0.7724761962890625 | 34.62588500976521 |
| Reflection cap3 | 121 | 0.9389496445655823 | 38.35969316959336 |
| Reflection cap4 | 341 | 0.9844663145486265 | 39.33693810412615 |
| Mark then reflection cap4 | 341 | 0.9844663145486265 | 165.33693810412186 |
| Full preparation plus one iteration cap2 | 127 | 0.6789341568946838 | 149.65165674685932 |

Counts are event-derived and probability-weighted using the maximally mixed
graph input (denominator16); input independence follows from the exact scalar
branch effects. With `F=(14/3)s` and `I=(8/3)s+2`, predicted reflection stop T is
`R=I(1+s)+21s**2+F(s**2+s**3)`. Mark-then-reflect is126+R. Full search is
`F(1+s)+126s**2+I(s**2+s**3)+21s**4+F(s**4+s**5)`.
Every reached inverse prefix is charged even when it aborts. Measurement, reset,
feedforward, retry, Clifford and runtime costs remain **null**, not zero;
the observed operation counts are separately saved. No T-depth, latency,
noise/physical-QEC or achieved preparation break-even is claimed.

The edge is an unfavorable amplification example: M/N=6/9, initial proper
probability2/3. Conditional on completion, one iteration gives
`sin**2(3 asin(sqrt(2/3)))=2/27=0.07407407407407407`. The executed full-search
cap2 joint probability of completion and proper coloring is
**0.05029141902923401**, with completion0.6789341568946592. This overshoot loss
is preserved. Aborted states are not relabeled as completed proper solutions.

## Validation, budget and preserved failures

Final exact source passes **326 tests**, no skips/deselections:40 new graph,
38 prior dynamic,100 accounting and148 preparation break-even tests.
Selected Black/Ruff, one-file mypy, stdlib-only lazy import/preflight and source/
README/lockfile/native/admitted-dependency preservation audits pass. This is a
bounded relevant check, not the full repository/paper validation.

Before arrays, budget.json declared120s per child,300s cumulative numerical,
1GiB/process, cap4/341 records, dense matrices<=16x16,<=4 columns,<=3 references,
<=9 explicit dynamic wires and one numerical/compiler child at a time. Actual
engine columns have at most8 explicit wires; the largest live amplitude block
is256x4 (purification columns), and QPY replay uses6 wires. No dense operator
exceeds4 wires. The original staticFT dense4 domain is unchanged.

All numerical children, including the first failing test run, used
**20.613195582758635 seconds** boundary wall time. Saved study:10.095382417s,
terminal wait4 high-water658,243,584 bytes (~627.75MiB). Final tests:5.109069958s,
98,959,360 bytes. Fixed preallocation bounds and process-group timeouts are
actual safeguards; terminal direct-child wait4 may include reaped descendants
and is neither live/group RSS monitoring nor hard memory enforcement. No
hard memory cap is claimed. Compiler/BLAS/OMP/Accelerate/Rayon/Qiskit settings
are serial. Only the existing absolute root venv Python and explicit candidate
PYTHONPATH are used. Native hash6aa7357d...be14a9a was explicitly selected and
verified, never invoked or rebuilt; no sync/install/pin change occurred.

Command3 retained10 failing assertions/160 passes: cap0 test counting used an
empty tuple instead of bool, and absolute3e-12 was too strict for weighted
integer totals (~188 operations differed by3.3e-12). The corrected scalar
comparison uses the stated relative tolerance; matrix tolerance is unchanged.
Command5 retained four typing failures, corrected without changing instrument
semantics. These are test/type issues, not failed mathematical constructions.
Command14 retained sandbox index.lock denial; scoped escalation succeeded.
The first escalated commit lacked Git identity; its failed command is retained,
and command-local prior HEAD identity allowed the owned-path commit without
persistent Git configuration. No automatic approval-review rejection occurred.
Initial source snapshots were taken after command8, not before the initial
failed test; the original failure logs remain. Long initial reads truncated
and were followed by focused complete chunks. No failure artifact was removed.

## Identities and next action

| Item | SHA256 |
| --- | --- |
| New graph source | 934022995306673975bded34f8aec94704200c29e95ab2fede142cb56c8063b0 |
| New graph tests | 6859f95e38cdeec4606e0fd7729444a217d898bd4bd02db66068e0c71cf75bb5 |
| Immutable evidence index,72 entries | 7cfa0c1be0f86aacf608c6fd719a1f810a5eeb25517c34dfe777438c4491983d |
| Summary | 672201a4f32bbc52daed185e2bf6e1fa95eed2748eaf8f015a6c93d4f25d0648 |
| Full branch/event ledger | 43c3e1ea81486d4a2d3bdb5c76c06c44a9c02076ab9610a6e582b126b4f79cfa |
| Saved inputs | 9cda440dee0a3a575784dd6ce48097c751a9711563cbd744e6a2282885e28587 |

The index binds scripts, source snapshots, inputs, arrays, QPYs, budgets,
provenance, failed/pass logs and frozen receipts. Final Git/checkpoint files
remain separate to avoid a self-referential index. The required researcher brief
was atomically written to LOGIQUE_RESEARCH_BRIEF; its SHA is in brief-receipt.json.
No important sidecar was requested: this is a constructive candidate, with no
new material scientific BLOCK or manuscript advantage claim.

Next: queued `dynamic-rus-graph-review-1101052342` independently reviews exact
48b8203 and the saved instrument/QPY/reference/abort/cost evidence, explicitly
including complete-predicate marking and the wider use of primitive tensor
action. It must issue scoped path/hash/commit admission or concrete rejection.
Only `dynamic-rus-graph-integrate-1101052342` may integrate admitted bytes.
No model/subagent/Codex/API launch, paid fallback/purchase, hardware, precolored,
physical-QEC or conditional-workspace research occurred. Queue/history/archive,
README, dependencies, old candidate/review/evidence and root are unchanged;
calendar deadline removal was respected. No prerequisite polling is needed.
