# Graph FT precision checkpoint — 9 November 2026

Task `graph-ft-precision-1101052342`; branch
`codex/coloring-graph-ft-precision-1101052342`; assigned base `de230cc`.
**Bounded implementation/preflight/one-case execution complete. Independent
exact-source and evidence review is pending. Scientific BLOCK remains for
j=1, whole-search precision 1e-4. No new full-search cost is available.**

Fresh evidence: `dump/1109113519-graph-ft-precision/` (RUN).
The local `task-ledger.json`, `checkpoint.json`, `commands.jsonl`,
`artifact-hashes.json`, and `result.json` identify session, commits, exact
commands/exits, timing/RSS scope, source/input/evidence hashes and next action.
Old checkpoints, all three original failures and all primary costs are unchanged.

## What changed scientifically

The fixed graph remains vertices (7,11), edge (7,11), k=3, four LSB-first data
bits, xag_bennett/none, restoring Gray-code MCX, clean computation workspace.
Fresh native constructions use the prescribed unchanged private executable,
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
R1/R2 widths are 13, R3 width seven. All 96 source/lowered clean columns pass
absolute phase/restoration checks; recorded Frobenius residuals are zero in
this evaluation. A unitarity defects are <=2.166e-15 and initial-state gaps
<=6.434e-16. These are finite numerical observations, not formal error bounds.

The new local degree-six/depth-twelve probes overcome the two distinct saved
failing rotations. The emitted one-qubit QPY words and all degrees 0..6 trials
are saved. They do not establish a completed preparation, reflection or search.

| Saved failed rotation | Allocated precision | Old degree-five bound | New degree-six bound | Local gates / T |
| --- | ---: | ---: | ---: | ---: |
| R1 S0: pi/8 | 4.761904357254428e-6 | 2.0277042049248834e-5 | 6.209522513131447e-8 | 119726 / 65722 |
| R2/R3 A: 1.9106332362490184 | 3.703703320770689e-6 (R2) | 1.1165654933613787e-5 | 9.538178417834687e-8 | 117694 / 64713 |

The R2 precision is slightly stricter than R3's 3.7037035738029423e-6.
`current-allocations.json` recomputes the original norm-aware compiler allocation
from the current lowered components, preserving the original numeric targets.
For j=1, weights are (3,1,1); residual rotation counts are (0,0,21) in R1 and
(2,0,21) in R2/R3, hence 21 or 27 total occurrences. Norm product is 1 for R1
and 1.000000000000144 for valid preparation. Preprocessing is charged before
allocating precision; all three allocations exactly equal the saved values.
A must still be emitted once, with its actual scalar-preserving inverse reused.
No new full emitted A/inverse was available for this failed search trial.

## Resource preflight and actual failed search request

At depth12/degree6 the existing conservative bound is
`sum(weights*(lowered_length + rotations*2*12*5**6))`. This is an upper bound
used by the harness guard, **not a measured cost or proof of infeasibility**.

| Regime | Estimated operation ceiling | State-gate-work estimate | Existing guard |
| --- | ---: | ---: | --- |
| R1 | 7875644 | 64517275648 | BLOCK: operations>3000000 and work>20000000000 |
| R2 | 10125710 | 82949816320 | BLOCK: both caps |
| R3 | 10125196 | 1296025088 | BLOCK: operation cap |

All degree-six basis depths1..12 were preflighted without synthesis. Largest
accepted depths are3/2/3 for R1/R2/R3. These smaller nets are not uniformly more
accurate than the original net. One actual R3/j1/1e-4 request uses degree6/depth3,
the largest depth admitted for R3. Its preflight allows 2531446 operations;
preparation fails at the same angle with best bound **0.001392940029734499**,
versus **3.7037035738029423e-6** required. This is a retained precision failure,
not a timeout; supervisor exit1 in 1.496130s. Target QPY, input Verilog, native
metadata and all seven trials remain in `1109113956-graph-ft-edge/`.
No emitted complete search, success observation, cost or analytical replacement
is recorded. Other accepted depths were not executed; no exhaustive parameter
impossibility claim follows. All three original degree-five failures remain.

## Exact source, inheritance and validation

Own correctness commit **61184f7** changes only graph_ft.py/test_graph_ft.py:
explicit bounded SK CLI options, runtime narrowing of mandatory emitted A/O/S0,
and six focused regressions. Defaults and every numerical tolerance/cap remain
unchanged. Original rotations/static_ft source and tests remain base-identical;
original staticFT dense-four pilot is untouched.

| Own path | SHA256 |
| --- | --- |
| src/logique/benchmarks/graph_ft.py | 7ef2844defe79d1e60e5e7d274dd4ca8ab87bf59c22df33fb9ef7b6a887449f4 |
| tests/test_graph_ft.py | c7dc9c688154c660eda1397791b18fa505ff6439de18e390ce5284a4f21a95c8 |

Current root dependency changes were deliberately incorporated before any new
scientific construction: reviewed `253e850` as **c8fea5a**, reviewed `cf678f7`
as **325ea11**, without conflicts. All13 inherited paths match both admitted
committed blobs and current root; exact hashes are in `inherited-exact-paths.json`.
The first preserves profile evidence through failures; the graph uses its ordinary
Bennett/no-profile path. The second disables Qiskit's program-entry zero
assumption and forces serial component transpilation. Neither changes the
rotation compiler or authorizes broader FT claims. Consult the current root
`profiles_failure_integration_20261103.md` and
`component_lowering_integration_20261103.md` plus their restrictive independent
reviews. The next reviewer must inspect the inherited bytes with this change.
The coordinator should retain current root dependencies and integrate only exact
newly admitted own paths, avoiding duplicate dependency cherry-picks.

Focused regression: **253 passed**, no skips/deselections, 18.74 pytest seconds,
19.155012s boundary. Selected Black/Ruff and one-file mypy with
`--follow-imports=silent --ignore-missing-imports` pass; this closes the prior
optional-circuit annotation issue within that scope. Not full-repository or
final environment/native/notebook/replay validation. Explicit candidate import
assertions cover graph/rotation/static/costs/API/native/Grover modules.
57 relevant historical inventory entries match the prior hash-bound manifest;
13 inherited dependency files and protected source/tests/lockfile/README match.
No old experiment, large search or C5 simulation was replayed.

## Success-cost objective and retained losses

Primary j1 historical R1/R2/R3 costs remain **271982/353792/353624 T**.
Valid preparation's matched-j losses remain 81810/81642 T. The historical
proper-success denominators give approximately 322340.20, 4776191.74 and
4773923.74 T per proper outcome. These are descriptive arithmetic over the
admitted old rows, not fresh graph costs. H/j0 already has T=0 and p=3/8,
expected attempts8/3. Valid/j0 costs5810T at primary precision and p near2/3,
approximately8715 T per proper outcome.

For independent restarts a priced objective would be
`(w_T*T + w_C*Cliffords + w_time*runtime + verification_cost)/p_proper`.
Clifford/runtime/verification prices are absent, so achieved break-even stays
null. Nothing here overturns prior losses or supports an optimized-search,
strongest-baseline, ideal-amplitude, RUS or full-paper advantage.

## Limits, preservation and next action

Before arrays RUN/budget.json declares <=120s/child, <=600s cumulative,
<=6GiB/process, <=64MiB reserved arrays, statevector<=18, dense<=5, original
pilot dense4, serial children and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit
parallelism1. Actual source statevectors<=13 and local dense operators<=4;
regressions include the existing five-wire local S0 check. Two local rotation
probes each take about4.31s boundary. Final timing/RSS totals are in checkpoint.
Wait4 high-water may include reaped descendants; no live aggregate RSS or hard
memory cap is claimed. Outer process-group timeout and preallocation guards
are present. Existing absolute root venv Python only; no sync/build/install.

Preserved failures include the first focused test's incomplete fixture
(missing mapping;252pass/1fail), initial sandbox Git-sequencer denial, then
missing command-local committer identity. Explicit scoped retry succeeded;
no automatic approval-review rejection. Read-only inspection and Git commands
have transcript receipts but no separate timing/RSS; no fabricated measurements.
All numerical/static receipts include failures in cumulative charges.

Next: assigned independent review of exact61184f7 and these artifacts, then
coordinator exact admission. A further implementation should first inventory all
required unique rotations under the unchanged whole-search allocation and
review a tighter source-specific operation/memory/time bound under existing
caps. Local success for two angles cannot supply that inventory. Only then
attempt missing R1/R2/R3 full searches with actual emitted A/inverse and norm,
phase and scratch checks. If that cannot be bounded, retain scientific BLOCK.
Do not widen caps, relax tolerances or invent costs. This is a compiler/resource
follow-up, not two failed mathematical derivations requiring recursive escalation.
No models/subagents/Codex/API/paid fallback, purchases, hardware, physicalQEC,
precolored/conditional-workspace work or push occurred. Dispatcher owns launches
and publication; root/source/queue/history/archive/binary/pins remain unchanged.
