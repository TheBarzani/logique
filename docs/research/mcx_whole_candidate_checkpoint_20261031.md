# Bounded whole-circuit MCX study

Task `mcx-whole-circuit-1030020413`, session
`01a191d5-5c47-7bb3-808a-553ec7d2a8b0`, branch
`codex/coloring-mcx-whole-circuit-1030020413`, base `e90adf3373236ef51a937480febd3cd7d669dce7`.
Assigned implementation/execution is **COMPLETE**. Scientific admission is
**BLOCKED pending exact independent review**. Full paper/MCX/FT scope is open.
No queue outcome constitutes admission.

Evidence: `dump/1031080140-mcx-whole-circuit/batch.json`.
The dispatcher resumed this session after an interruption (observed attempt2);
completed runs were retained rather than restarted.

## Ownership and commits

Only these tracked paths belong to this task:

- `src/logique/benchmarks/mcx_study.py`
- `tests/test_mcx_study.py`
- `tools/run_mcx_study.py`
- `MCX_WHOLE_CIRCUIT_CHECKPOINT.md` (this separate research-metric checkpoint)

Correctness/harness commit `dc304e9969856f4332fe7f0fba9c18f491c2ba2b` implements the study.
Correctness commit `865deab66564dfbe8807ca3e7c46d8ec0d13c222` translates known source exclusions and
adds zero/two-iteration regressions. It changes no successful circuit bytes:
7,920 completed QPY files from the corrected triangle shards match the original
saved SHA256s. This metric/evidence ledger is committed separately. No reused
cost helper, assembly, native bridge, dependency or historical metric changed.

| Final owned source | SHA256 |
| --- | --- |
| `src/logique/benchmarks/mcx_study.py` | `7518d7c164ebb8e307e08ed284bea79194286c70813a885dcb8afad2e9d2371e` |
| `tests/test_mcx_study.py` | `ca1009fada74377c961ee47e1311f2e0bc2b4c7836b6b35cfd5d5de47862a002` |
| `tools/run_mcx_study.py` | `322897eb72a1eb53804d7361831bd8753ff10c0c17c953b9a203bec6f655af4d` |

## Construction and scope

All eleven existing policies run with five native methods (including k-LUT and
best-fit), four normalized Saha-Belletti references and sequential/parallel
structure references under R1/R2/R3. Fixtures are noncontiguous-label edge k3,
edge k5, isolated k5 and unsatisfiable triangle k2. Evidence uses j1, seed7;
regressions independently check j0/j1/j2. This is a bounded fixture study, not
the nine-graph final comparison or a frozen full protocol.

Comparators and domain checks use the selected policy; final conjunction and
zero reflection restore scratch. Throwaway prefixes use the selected throwaway
construction, with **clean_tree explicitly substituted for unmirrored final
marking, A and S0**. Baseline/structure raw is lowered prefix, restoring mark,
actual expanded prefix inverse. Native raw uses compute-Z-actual-expanded-inverse
for every policy; raw itself retains its original backend contract and native
throwaway garbage. No direct-kickback advantage is inferred for native flows.
These wrappers implement the same phase service but retain their construction
identities, rather than treating raw and phase costs as interchangeable.

Throwaway substitution preserves original monomial instruction boundaries,
including controlled-Rx(plus/minus pi). Expanding such a gate first can expose
nonmonomial intermediates; inserting garbage there is outside the proof.
The original failed pilot is retained. Only X/Rx(plus/minus pi)/Z monomial source
records pass this throwaway boundary; opaque/interfering forms are rejected.
Actual emitted inverses cancel phases, restore held scratch and reuse the same
wires. No reconstructed forward mirror or free AND uncomputation is priced.

Clean policies allocate zero scratch; dirty policies borrow noninvolved wires
without assuming their state. Tests compare emitted action with an independent
integer MCX permutation on seeded superpositions entangled with an untouched
reference at three/four controls, including all four Khattar-Gidney policies.
Clean scratch alone starts zero. A retained control-changing monomial-prefix
regression checks actual inverse restoration. This bounded numerical evidence
is not an exhaustive all-width unitary or interval certificate.

Peak MCX scratch is construction capacity including borrowed wires, not backend
live workspace or process memory. Clean/dirty gate scratch is reusable after
restoration. Throwaway garbage is held once through its inverse: a baseline
prefix's held pool overlaps marking and therefore **adds to marking scratch**.
Sequential A/oracle/S0 peaks use their maximum, rather than summing capacities.
Reserved physical width still includes disjoint pools. At j0 only A contributes
to executed peak, although other pools remain reserved. Unknown backend liveness
and optimized/routed live workspace remain unavailable.

A is emitted once and actually inverted; diffusion has the positive sign
A(2|0><0|-I)A-dagger, and search embeds the saved components in explicit order.
Raw, A, S0, oracle, diffusion and full search are saved with explicit, U/CX
optimization0 and Clifford+T-plus-unsynthesized-Rz representations. Counts and
T-depth come from actual emitted operations/dependencies, never a sum of component
T-depths. Rotations are counted and **unpriced**: total FT T-count/T-depth and
precision remain null, even when known-T counts are small. No target/calibration
was selected, so routed costs are explicitly not executed. These are not static
FT, ideal-amplitude, RUS, physical QEC or measurement-assisted certificates.

Dutta is theorem-only: 54 (controls3..20,m1 in2/3/4) requests yield34 analytical
rows and20 out-of-theorem-range exclusions. Published modeled T quantities are
separated from null static-unitary costs. No Dutta circuit, measurement-free
T implementation or phase/restoration result is claimed. The preexisting
Theorem1/example depth discrepancy is retained, not resolved by this study.

## Gray preallocation and execution

The cap was frozen before numerical allocation at **50,000 phase/CX operations
per single forward construction/block**. The installed Gray chain visits2^n
n-character strings and emits at most n-1 CX plus one CU1 per nonzero string;
CU1 uses three phases/two CX. The bound is (n+4)2^n+2 operations. Planning memory
uses2048 bytes/operation and throughput10,000 operations/s; these are assumptions,
not hard allocator/time guarantees. Actual inverse copies and metric translations
are additional supervised work, not new uncapped Gray constructors.

Controls3..11 execute, including the formerly open n11 row: bound30,722 ops,
62,918,656 planning bytes,3.0722 planning seconds; actual forward common basis
has12,283 gates (6,140 CX). Controls12..20 have nine explicit **preconstructor**
exclusions: n12 bound65,538 exceeds cap; n20 bound25,165,826, planning51,539,611,648
bytes/2516.5826s. No excluded definition is requested. Aggregate Gray blocks also
check the sum before synthesis. All non-Gray policies execute controls3..20.
Above-four isolated rows are representation/cost observations; no independent
full-state restoration claim is inferred for those widths.

## Actual evidence and losses

The final selected ledger has **1,608 completed rows,42 explicit exclusions**:
189 isolated constructions and1,419 whole-circuit cases complete; nine Gray rows
and33 sb_original triangle/regime/policy rows exclude. Dutta's separate ledger
is additional. No failed row is silently admitted into the selected ledger.

Whole-circuit coherent checks pass on1,335 cases using independent binary-input
phase expectations and amplification recurrence, including full scratch-zero
output amplitudes. Largest error 1.0467090883352825e-14, tolerance3e-10,
without global-phase alignment. **84 completed cost rows exclude full statevector
validation** because their physical width exceeds18; they retain source-service
and small-template/compositional evidence only. The graph checks use a specified
uniform input and complete search initial state, not a full dense operator proof.
The maximum simulated width is18. Templates use arbitrary seeded complex inputs
with references. Dense operators are local, maximum3 qubits.

A separate direct QPY recount verifies **26,676 representations /8,892 components**:
file hashes, gate maps, widths, dependency depths, T-count/T-depth, residual
rotations and workspace maxima. Recount code does not call the cost metric
functions for expected values. It is a separately written local audit by this
worker, **not the queued independent model review**. Saved-circuit readback also
checks ordered standard gate semantics and scalar phases.

`losses-with-rotation-scope.json` records5,160 individual comparisons against the
same fixture/method/regime's clean_tree search across four metrics (width,
common CX, known-T contribution, known-T dependency depth):1,411 wins,1,194 losses,
2,555 ties. These are metric-level diagnostics, not independent benchmark counts
or a superiority aggregate. Each row includes full-statevector coverage and both
unsynthesized rotation counts. In particular a lower known-T contribution with
unpriced Rz is **not** a lower total FT cost.

For a concrete validated loss, edge-k3/xag/R1 noaux uses170 common CX versus168
for clean_tree; one-dirty KG uses174. Throwaway never lowers reserved width in
these129 matched cases:104 ties/25 losses; its common CX counts tie in129,
while known-T contributions improve in37/tie92. An edge-k5/k-LUT/R1 throwaway
width27 versus clean_tree15 example is explicitly outside full-statevector
coverage, so its cost difference is not advertised as a new semantic certificate.
No strongest-baseline headline or final manuscript table is admitted here.

## Validation, provenance and preservation

**195 regressions passed**, including every policy's entangled reference tests,
small complete graph phase/search, j0/j1/j2, held prefix/mark peaks, Gray guards,
exact local FT gadget and Dutta exclusions. Final Black/Ruff and Git whitespace
checks pass. No full suite, build, notebook, historical replay, routed/noisy or
rotation-synthesis execution is claimed. Original staticFT dense-four domain is
untouched.

Existing `/Users/mar/codex-work/logique/.venv/bin/python` only; every numerical
child uses explicit candidate PYTHONPATH and checks imports. The unchanged native
foundation is explicitly selected and SHA256 verified as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Its path is recorded in every plan and command receipt. Root's old default was
never selected. No sync, install, rebuild, pin change, hardware or model launch.

Commands/argv/exits/timing/RSS are in `commands.jsonl`. Final regression command
is existing Python plus `-m pytest tests/test_mcx_study.py -q -p no:cacheprovider`
under `supervisor.py correction-tests`;195 pass in4.835521 supervised seconds.
The direct recount passes in42.036138s. Each child is bounded120s; cumulative
recorded supervisor time is **341.503106s of900s**
(includes failed runs/checks), longest child42.036138s, maximum terminal child
high-water **203,816,960 bytes**. Declared process budget6GiB
on the8GiB host; no aggregate hard limit/live memory enforcement is claimed.
Darwin RUSAGE_CHILDREN may include reaped descendants; group RSS is unavailable.
Numerical children are serial. OMP/OpenBLAS/MKL/NumExpr/Accelerate/Rayon/Qiskit/
CMake parallelism is one (QISKIT_PARALLEL=FALSE); supervisor source preserves
the full environment contract even where receipt's filtered view omits a key.
Study seed7; entangled template RNG74/75 and auxiliary RNG7 are deterministic.

All failures remain: initial49-pass/one bookkeeping assertion; original xag
throwaway boundary failures;33 old exclusion-as-failure rows; first audit's
trailing-blank JSON parse error. New unique logs/scripts/run directories preserve
failed/partial predecessors. Exclusion repair changes reporting only (7,920 QPY
SHA256 matches), not historical failure records. Initial Git staging failed128
at the shared index.lock sandbox boundary; scoped automatic escalation succeeded.
No automatic approval-review rejection occurred.

Intake/preservation ledgers confirm README, lockfile, reused costs/assembly/
structure/baseline source and reviews unchanged. Source outputs, pins, histories,
archives and old128 queue/run are untouched. Active continuation128/deadline
were read, not altered. Dispatcher alone launches and pushes integration HEAD;
worker commits only its owned branch. No subagents, recursive Codex/model calls,
API/paid fallback/purchases or excluded research occurred.

## Exact handoff

Independent `mcx-whole-review-1030020413` should review the two correctness
commits, final hashes, actual selected ledger (including source-version binding),
monomial substitution boundaries, dirty/conditional entanglement, actual inverse
and held-peak accounting, QPY recount and qualified losses. The successful old
circuit evidence uses dc304e9; the final exception-only change is865deab, with
fresh triangle runs and unchanged successful QPY receipts. This is explicit
provenance, not an assertion that changed hashes were already admitted.

Only exact independent ADMIT permits coordinator integration of those bytes;
root coordinator alone integrates, dispatcher alone publishes. Full nine-graph,
large-template semantic coverage, target/calibration routing and rotation precision
remain separate work. This assigned bounded implementation/execution ends here;
review or publication is not performed by this worker.

Key evidence SHA256s (relative to the run above):

| Artifact | SHA256 |
| --- | --- |
| `intake.json` | `9b73d2a851cdeb561757bad40faf5460d9d77e30d7325db31b9d10a54ad14ebf` |
| `commands.jsonl` | `d06411f6a6c2677dd7805d3b5cec7a0ac1a9efe05fadcd97c4f30fe5dabcf13c` |
| `audit.py` | `b2b1834baeaf5928bc9f4541e1d867fddcf32a11edc5060c52008ad1522e2728` |
| `audit-v2.py` | `e5c2789bb4dacbec3877e14fe681a36ca70c2db737ae37f5ea26437e7bc26e0d` |
| `audit-results.json` | `1700fb8df4736282b4fc4d94ce96222d744a15d715baa8a217b753e7f397f2e8` |
| `driver-events.jsonl` | `3e412785836134c27e08c7940465b7e84eadec93d191e3dcde0f0ad6789a43cc` |
| `repair-events.jsonl` | `abcc6b6577bc6943afd3eb4a4ecfb47387958cdf6c9e490a81c34619d2ede26f` |
| `exclusion-repair-compatibility.json` | `74046f66d0353929119b623fb447c862ef593667e74d8cd08eeaf0c4ec09fcaa` |
| `losses-with-rotation-scope.json` | `d3053d03ac2f81d4bca23ee8956100af3eed76aec783fba991c47281da48d7d7` |
| `policy-loss-summary.json` | `2b9c5c0e51f655fcecfc3614a928a32eb314d2165b45514038afdf3d12d0508c` |
| `preservation-check.json` | `8df8b13ef81bf26091681395e577b4d00c7027f0db78a54af73885473b69306e` |
| `supervisor.py` | `2eb431cbb0ee535919c7fc2021a4da713b7195b881a51fb31e8baec6112a9aaf` |
| `study_driver.py` | `920256f93b2f4dd1907ee388f01046e9802f66e24c9e0cb714e6f7b6d4af9208` |
| `repair_driver.py` | `d70820bda6a531018ee3171adf71171861165792b0772da193978de6a33d5c3b` |
| `evidence-hashes.json` | `fc908f4c07b26f30b9bcbf14a5abc70ea41eaa611ee1ee95f5db8b17bf679d72` |
