# K5 common lowering: retained failures and read-only recovery

Task `comparison-common-lowering-1101052342`; assigned worker branch
`codex/coloring-comparison-common-lowering-1101052342`, base `de230cc`.
**The bounded implementation/execution assignment is COMPLETE. New source and
measurements remain PENDING exact independent review. Full comparison scope
and manuscript admission remain open/blocked.**

Recovery checkpoint within this assigned worktree:
`dump/1108201139-common-lowering-k5-recovery/checkpoint.json` (RECOVERY).
Original interrupted continuation:
`dump/1103212134-comparison-common-lowering/checkpoint.json` (K5).
The [earlier K3/grid6 report](comparison_common_lowering_20261103.md), its900
circuits, histories and checkpoint are unchanged. No completed compiler group
was repeated. K5 compilation occurred on3November;8November recovery only ran
five boundary tests and read/hash/metric recount of saved circuits.

## What the wider attempt adds

K5/k5 has15 binary data wires. The frozen experiment requested all ten methods,
R1–R3,j1,seed7,profile none,unrouted U/CX,opt0,native floating rotations and
clean_tree/fresh_zero MCX. Original input precolors were removed. Every completed
source case is **sampled**, using32 seeded assignments plus four explicit inputs:
18056,0,5,32767. Word18056 encodes colors(0,1,2,3,4), independently verified as
proper; the others exercise violations/boundaries. The resulting36 checked
assignments do not prove all-input equivalence. No K5 result is headline-eligible.
Neither the earlier wide CEC corpus nor the previous K3/grid6 exhaustive checks
certifies these different artifacts.

The ten requested groups returned60 logical/restoring case records:50 complete,
six excluded and four failed. Complete cases supply365 recounted QPY circuits:
135 logical,115 restoring-MCX and115 common-basis. Width, instruction count,
depth and gate types match their saved hashes/manifests. All completed restoring
cases record clean_tree/fresh_zero; reusable lowering retains the reviewed `qubits_initially_zero=False` and
`num_processes=1` corrections.

Selected **complete j1 search** measurements in the common U/CX basis:

| Regime | Method | Allocated wires | U+CX instructions | Depth |
| --- | --- | ---: | ---: | ---: |
| R1 | xag | 76 | 2893 | 659 |
| R1 | structure_sequential | 58 | 2441 | 1045 |
| R1 | strongest available instruction/depth baseline, sb_balanced | — | 4715 | 2771 |
| R1 | strongest available width baseline, sb_minimal | 38 | — | — |
| R3 | best_fit | 32 | 56532 | 28858 |
| R3 | strongest instruction/depth baseline, sb_simple | — | 1451 | 588 |
| R3 | strongest width baseline, sb_minimal | 35 | — | — |

Dashes identify metrics not selected for that comparison, not absent circuits.
R3 best_fit has width ratio32/35=0.914285714, but instruction ratio
56532/1451=38.960716747 and depth ratio28858/588=49.078231293.
Thus its modest width saving accompanies much greater elementary cost in this
conditional observation. No routed runtime,FT cost or successful-solution cost
is implied by instruction/depth ratios. Deterministic compiler observations
have no shot confidence interval; the sample coverage is a separate limitation.

There are96 common-basis oracle/search metric/context comparisons:46 wins and
50 losses, no ties. Sixty use two available baselines;36 use three. These are
repeated metrics, not independent trials or an acceptance rate. **R1/R2 have
only sb_balanced/sb_minimal; sb_simple is unavailable at this MCX cap.** Favorable
R1/R2 ratios therefore cannot establish an advantage against all three corrected
baselines. R3 uses all three. Each metric selects its own minimum denominator.
Preparation/diffusion add96 ties. Raw primitives remain diagnostic.

## Failures and the corrected pre-constructor gate

The initial task harness incorrectly counted one invalid-code flag per vertex.
The baseline actually needs one per invalid code. K5/k5 has three invalid codes,
so its complete-predicate conservative bound is
$|E|+|V|(2^c-k)=10+5(8-5)=25$, rather than15. The new gate uses this expression
before quantum constructors and rejects the mixed K5 request against its
20-constraint cap. The test also checks the domain-free8-code effective problem,
whose bound is10. A future selective per-regime gate requires its own reviewed
implementation; the conservative gate does not authorize new wider runs.

The **library independently refused** sb_simple R1/R2 at25 controls: these two
restoring cases are failures, with no common cost. They were not silently
lowered with a different policy. K3/k3 has only one invalid code and grid6/k2
has none, so the corrected count leaves their frozen structural bounds unchanged.
The original faulty guard/source and its run remain preserved at d6268cf; the
new correction is f561883. This is a real harness limitation, not admission of
the original wider preallocation contract.

Other retained outcomes:

- aig_bennett: all three regimes in both logical/restoring runs excluded by the
  declared128-wire post-assembly limit; observed widths154/166 and134/146.
- best_fit R1/R2: restoring runs failed at the existing100000-operation QPY
  definition-resolution bound. Logical rows remain separate diagnostics.
- The original recount failed serializing a NumPy int64 context key. Its partial
  CSV,artifact recount,stderr and failed receipt remain untouched. JSON-native
  scalar normalization repairs reporting. Recovery writes a **new** directory
  through `--recount-source`; it does not compile or overwrite K5 artifacts.

The50000-instruction acceptance guard measures assembled pre-common-lowering
components, not final U/CX expansion. The56532-instruction common search is not
represented as satisfying a post-common instruction cap. Absolute process/time
supervision remained active. No limits were relaxed to turn a failure into a row.

## Provenance, bounds and exact continuation

The prerequisite13 files still exactly match admitted source253e850/cf678f7,
already deliberately imported as ef82766/c8aa562. The wide CEC decision0fc7d72
retains103 admitted saved oracle/search pairs and12 unresolved chains; report
SHA2567fba7222f010f6447106bc71c31181a24b37e07fc5f1e212c3182386ec62a0da
is rechecked. No retry or duplicate of the44 completed wide groups occurred.
The new task source chain is db389b2,d6268cf,f561883; the earlier measurement
report is ba8668a. Independent review must inspect the full chain, failures,
365-circuit inventory and earlier900-circuit evidence as distinct scopes.

The merged requested/open ledger contains14850 entries:253 completed cost
entries(each represents five components),nine exclusions,eight failures,
3780 unrun cost entries,6750 unrun routing entries and4050 unrun FT entries.
The original K5 ledger is preserved; RECOVERY adds per-case failure reasons.
No profiles,policies,FakeTorino seeds11/23/37/41/53 or FT1e-3/1e-2/1e-4 were
silently removed. No routed or FT numbers were derived from logical arithmetic.

Before K5 allocation, its frozen config declared60s/child,360s cumulative,
2GiB/process and all numerical/compiler/BLAS/OMP/Accelerate/Rayon/Qiskit
parallelism1. Scientific work used bounded classical verification, with no
statevector,dense Operator,density matrix or C5 work. Original staticFT dense4
remains unchanged. Original children including the failed recount totaled
48.249032s,maximum15.920461s/child; maximum Darwin wait4 high-water513015808bytes.
The new recovery predeclares60s/child,180s cumulative,2GiB/process and the same
serial settings. Five tests passed in0.444837s supervised; recount passed
in7.856024s,142917632bytes wait4. These are terminal observations, not simultaneous
group peaks or hard caps; ps sampling was denied. Black/Ruff and diff checks pass.
Only the existing absolute root venv interpreter and asserted assigned-worktree
imports were used. The prescribed native SHA2566aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a
is verified; it was not invoked during recovery. Binaries,pins,README,root,
archives,all failures and both previous runs remain unchanged. Current queue
calendar deadline is null; batch ceiling128 and review/resource limits remain.
No models/subagents,push,sync,API/paid fallback,purchase,hardware or excluded
research occurred. Interruption and inspection errors remain in the checkpoint.

Next: the assigned independent reviewer evaluates exact offered bytes and
restrictive data scope; coordinator alone integrates exact admitted paths.
Future wider execution must repair/review its per-regime pre-constructor policy
and establish sufficient all-input equivalence before headline use. Retain all
failures and losses,then complete missing profiles,MCX policies,routing seeds
and FT precision experiments with actual circuits. This worker does not wait or
poll for review and launches no successor model itself.
