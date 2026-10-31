# Graph FT execution checkpoint

2026-10-31, America/Montreal. Task `graph-ft-execute-1030020413`; session
`01a19360-efc9-7280-a7c8-63dc8d4120f0`. Worker branch
`codex/coloring-graph-ft-execute-1030020413`, base `e90adf3`.
Bounded implementation and execution are COMPLETE. Independent exact-source/evidence review is still required. Full paper
remains open. No scientific admission follows from this worker outcome.

Correctness commits: `a7281df4021838688b4a071d549a30520f956ee4` adds the
harness/tests; `a65e6729abd6eee79940982e3e7d96fd1b6ca6ba` adds fail-fast
request validation before any native call or preparation allocation. These nine
additional source lines preserve the successful numerical path. The original
15-row evidence binds a7281df; a separate final-source R2/j=1/1e-3 run binds
a65e672. This document is the separate evidence/checkpoint commit.

Evidence root (relative to this worktree):
`dump/1031151632-graph-ft-execution/`. See `batch.json`, `summary.json`,
`commands.jsonl`, `protected-identities.json`, `artifact-hashes-final.json`,
`first-peak-selection.json`, `readback-audit.json`, exclusive per-row QPY/JSON,
and the separate `final-source-smoke/` receipt/readback. All original failed
and partial artifacts remain in their original directories.

## Construction and proof boundary

The graph has vertices 7 and 11, one edge (7,11), k=3, LSB-first data order.
Actual native `xag_bennett`, common preprocessing `none`, uses 13 wires for
R1/R2 and seven for R3. The explicit private binary is unchanged SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Its full path and build metadata are in every row. No native build was run.
R1 uses H and the complete k=3 predicate. R2 uses ordinary StatePreparation
with the same predicate. R3 changes only encoder colors to four to remove
unused-code checks; proper-color decoding/reference remains k=3.

Each original and explicitly Gray-code-lowered oracle is checked on all 16
clean data columns against the independent `problem.is_valid` reference
(edge inequality only for R3). Summed squared column errors give a Frobenius
bound on the clean-subspace spectral error. Linearity extends this action to
coherent data and an external reference. No dirty initial scratch is admitted.
A and S0 act only on the mapped data register, so their composition with the
clean oracle preserves zero scratch. A is checked locally for unitarity and
its initial column is compared with an independent valid-code vector. Signed
`S0=-X^n MCZ X^n` is checked locally against diag(1,-1,...,-1).

No wide dense Operator is constructed. Full searches use sequential clean
statevectors; dense operators are local only. For every completed row, the
unchanged admitted rotation compiler emits A once, reuses its actual inverse
including scalar phase, and allocates all `(1+2j)n_A+j(n_O+n_S0)` rotations.
The four-data-wire Gray-code S0 contributes 21 residual rotations at j=1.
It is neither free nor replaced by an analytical estimate. Original recursive
numeric targets and floating-point/norm allowances remain unchanged.

QPY source definitions are expanded before writing to avoid the known inverse
StatePreparation serialization defect. Every reload must retain the ordered
standard leaves, wire indices, numeric parameters and scalar phase. Saved
emitted components reconstruct the complete saved search. Local adjoint
checks are phase sensitive. Full-state target/approximation error, proper
success, invalid-code leakage, scratch cleanup and measured ideal gaps are
recorded separately. These are numerical observations, not interval or general
ideal-amplitude certificates. R3 is compared with its own edge-only target;
approximate leakage is measured rather than assuming exact valid support.

## Executed schedules and costs

Independent enumeration of all 16 assignments gives M=6 proper colorings.
N=16 for R1 and N=9 on ideal R2/R3 support. The first-peak floor/ceiling
calculation selects j=1 for R1 and j=0 for R2/R3, with fewer-j tie preference.
All three regimes also execute the same j=1 schedule to expose overshoot.
Each precision is a whole-search budget, not a per-preparation allowance.

| Regime | j | Budget | Status | Full T | Full dependency T-depth | Clean-state error | Compiler bound |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| R1 | 1 | 0.001 | complete | 271982 | 194958.0 | 0.00019302700412851848 | 0.0003799104036421433 |
| R2 | 1 | 0.001 | complete | 353792 | 222800.0 | 0.0001672251220385147 | 0.00044690433508541046 |
| R3 | 1 | 0.001 | complete | 353624 | 222764.0 | 0.00016722512204194368 | 0.0004469043282535396 |
| R1 | 1 | 0.01 | complete | 170962 | 154550.0 | 0.002092959012930841 | 0.00420735554729429 |
| R2 | 1 | 0.01 | complete | 289412 | 200768.0 | 0.0005221702467496984 | 0.0018115786422660551 |
| R3 | 1 | 0.01 | complete | 289244 | 200732.0 | 0.0005221702467399687 | 0.0018115786354341843 |
| R1 | 1 | 0.0001 | failed | null | null | null | null |
| R2 | 1 | 0.0001 | failed | null | null | null | null |
| R3 | 1 | 0.0001 | failed | null | null | null | null |
| R2 | 0 | 0.001 | complete | 5810 | 2904.0 | 0.00043942642070120887 | 0.0004772227462363283 |
| R3 | 0 | 0.001 | complete | 5810 | 2904.0 | 0.00043942642070120887 | 0.0004772227462363283 |
| R2 | 0 | 0.01 | complete | 1126 | 562.0 | 0.0034511053517167064 | 0.004807801025585805 |
| R3 | 0 | 0.01 | complete | 1126 | 562.0 | 0.0034511053517167064 | 0.004807801025585805 |
| R2 | 0 | 0.0001 | complete | 27270 | 13634.0 | 1.6399887353054933e-05 | 2.2331310509490363e-05 |
| R3 | 0 | 0.0001 | complete | 27270 | 13634.0 | 1.6399887353054933e-05 | 2.2331310509490363e-05 |

Primary j=1 component costs (T / dependency T-depth):

| Regime | A | A inverse | O | S0 | Diffusion | Full search |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 0 / 0.0 | 0 / 0.0 | 182 / 42.0 | 271800 / 194916.0 | 271800 / 194916.0 | 271982 / 194958.0 |
| R2 | 27270 / 13634.0 | 27270 / 13634.0 | 182 / 42.0 | 271800 / 194916.0 | 326340 / 209124.0 | 353792 / 222800.0 |
| R3 | 27270 / 13634.0 | 27270 / 13634.0 | 14 / 6.0 | 271800 / 194916.0 | 326340 / 209124.0 | 353624 / 222764.0 |

T-count follows `T_A+j(2T_A+T_O+T_S0)` from actual emitted gates. T-depth is
computed from the full dependency graph, never by an additive component formula.
Unused j=0 O/S0 have no emitted circuit or assigned zero cost. Source caller
semantics are nevertheless verified and source circuits retained.

At primary j=1, measured proper success is approximately 0.843773 for R1 and
0.0740741 for R2/R3. R1 leakage is approximately 0.109345; valid-preparation
leakage is approximately 3.48e-9. Nonzero scratch stays below 3.85e-31 in the
15-row study. At j=0, R2/R3 give approximately 2/3 proper success.

The first-peak primary schedules have raw T charges 271982 (R1) versus 5810
(R2/R3), with the supplied-cost equality threshold A_V=271982. By contrast,
matched j=1 gives raw losses of 81810 and 81642 T. These are comparable executed
circuits with known M, not supplied hypothetical circuit costs. The j=0 valid
schedule has no oracle invocation; verification and Clifford costs remain
unpriced. This first-peak comparison does not optimize T charge per verified
solution over all j: H at j=0 itself has zero T. Therefore the general
`achieved_break_even` field remains null. Raw relations, exact thresholds and
T per measured proper success are retained in `summary.json`; no unqualified
preparation advantage, strongest-baseline or paper claim is made.

## Precision failures and follow-up

All three j=1 rows at 1e-4 fail bounded SK through degree five. R1 S0 needs
4.761904e-6 for Rz(pi/8), versus best bounded error 2.0277e-5. R2/R3 A needs
3.703704e-6 for Rz(1.9106332362490184), versus best 1.11657e-5.
Full trial metadata, exact requested allocations, source QPY and failures are
preserved; no full-search metric or analytic replacement is supplied. These
are numerical synthesis limits, not failed mathematical derivations or quota
pauses. The j=0 valid preparations at 1e-4 do complete; the R1 first-peak
comparator remains absent, so that break-even comparison stays null.

Next: queued `graph-ft-review-1030020413` independently reviews both exact
correctness commits and all evidence, including failure/status/readback and
first-peak scope. `graph-ft-integrate-1030020413` alone decides exact admission
and root integration. Tight j=1 sensitivity is scientifically BLOCKED for the
fixed options. Any successor should inspect the saved failing angles/trials
and preflight any allowed stronger SK settings against time/operation/memory
limits before execution; otherwise retain explicit unsupported precision.
Do not widen the original pilot, alter rotation contracts or invent costs.

## Validation, resource scope and preservation

Final regression: 247 passed (36 new graph, 24 original static, 187 unchanged
rotation tests), no skips/deselections. Selected Black/Ruff and focused
one-file mypy pass. This is not a full-suite/build/notebook/replay validation.
Independent accounting code in `readback.py` reloads 54 emitted QPY circuits
from 12 completed study rows and reconstructs T depth without the cost helper.
The module itself also readbacks every source and emitted QPY.

Limits were declared before numerical allocations in `budget.json`: one
numerical/native child serially; BLAS/OpenMP/Accelerate/Rayon/Qiskit/compiler
parallelism one; <=120s supervisor child, 110s graph deadline and <=900s
cumulative supervised work. Declared process budget is 6 GiB, reserved array
budget 64 MiB, statevector <=18, dense local <=5. Actual graph statevectors
are 13 or seven wires and local graph matrices four wires; a five-wire local
S0 regression is also tested. State-gate-work and emitted-operation caps are
preflighted separately. SK length estimates do not claim a hard Python RSS
bound. Wait4 measures per-child high-water (Darwin bytes, possible reaped
descendants), with no group RSS measurement or hard OS memory cap claimed.
Final measured totals and exact timeout/RSS scopes are in `batch.json`.

All scientific children use the existing root .venv Python with explicit
candidate PYTHONPATH and asserted import paths. No sync/install/build, paid
fallback, model subprocess, subagent, API, hardware, physical QEC, precolored
or conditional-workspace research was run. No push was run.

The original static_ft source/tests, rotation source/tests/review, native binary,
lockfile and all protected tracked inputs equal their intake/base bytes.
Original pilot manifest still records the 13-wire versus dense4 failure;
it was read without replay or modification. Root README SHA256 remains
`73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`.
Only the two new owned code/test paths and this checkpoint are committed.
Queues, histories, archives, pins, other workers and root integration remain
untouched. Dispatcher alone launches models and pushes integration HEAD.

Operational failures retained: initial absent worktree-local continuation/queue
paths (root copies then read), truncated combined reads (focused full chunks
followed), guessed old checkpoint paths (actual git blob and manifest then read),
initial SK work-estimate regression, a test expecting three rather than 24
weighted rotations, initial mixed-dictionary mypy inference, and a reserved
pytest parameter name during the final preflight tests. Corrected final checks
are separate logs. The initial Git index-lock write was sandbox-denied;
scoped automatic Git escalation succeeded without an approval-review rejection.
Initial uninstrumented formatting and read-only inspection commands remain
in the dispatcher event transcript; numerical/static supervised commands,
exits, logs, time/RSS and failures are in commands.jsonl. No scientific failure
or partial artifact was deleted or relabeled.

Final-source R2/j=1/1e-3 execution completed in 82.842682s and its six emitted
QPY circuits passed the separate readback audit. There are therefore 13 completed
executions plus three retained precision failures (15 study rows plus this final
source smoke), and 60 emitted circuits checked by the separate accounting code.
Supervised numerical/static/readback wall before the final scalar inventory,
conservatively including failed tests, is **608.946744s**. Maximum wait4 child high-water is
**622,411,776 bytes**; longest child is **82.952326s**.
No timeout or declared process-budget exceedance was observed. This is not a
hard group memory-cap assertion.

| Owned source | Study a7281df SHA256 | Final a65e672 SHA256 |
| --- | --- | --- |
| src/logique/benchmarks/graph_ft.py | 6b574551351df2ed5691ae83bedfba1c704b06ddb687bae3cf92ba306ba9810e | ae6c3f93c3ef2fb0abc279bafe300ef5c986f1e14700092a3dde903e08adb220 |
| tests/test_graph_ft.py | 224b8d7637108a557b2f672a1bfef619d6cda04f9f4a42923ad5992cb0bbbfbd | 4e8c1396a0da7e9b4c2cec19116d19422ef01214b8080ed1bd7bc390514dabc9 |

The initial artifact inventory included its own still-open stdout log and thus
hashed that log before the final print. It is retained as `artifact-hashes.json`
for failure provenance and is superseded by the fresh `artifact-hashes-final.json`.
The final inventory runs after every supervised log closes; it records its own
scalar timing/RSS and exit status before binding the command ledger in batch.json.
This bookkeeping correction does not change circuits, metrics or source bytes.
