# Independent noisy ledger repair review — 30 October 2026

**Assigned review COMPLETE. ADMIT the exact corrected harness at f2bc546 within
its frozen-input and resource contracts. Separately ADMIT the exact 9bfa2cd
gate-total and de6ca3a layout patches. Historical defective harness revisions
remain BLOCKED as standalone implementations. ADMIT only the previously reviewed
28 completed rows/1792 shots as conditional observations. BLOCK full K3/five-seed,
new C5, full-family, superiority, FT/RUS and paper claims.** Queue completion is
not scientific admission.

Task `noisy-ledger-review-1030015553`, session
`01a18c7d-561b-7a62-a9a9-d039c1d5f5f0`, branch
`codex/coloring-noisy-ledger-review-1030015553`, intake
`97fde8a137fcc5807c84603963f7b179f81b04d3`.
Only this review is committed. New runnable probes and evidence are in
`dump/1030070752-noisy-ledger-independent-review/` (`R`) in this review worktree.
No candidate source, original evidence, queue, root integration source or prior
review was edited. No models, subagents, native builds, hardware or pushes ran.

Candidate `C`:
`/Users/mar/codex-work/logique/dump/1030015553-noisy-channel-integration-triage/worktrees/ledger-fix`.
Exact clean HEAD **92a6e03f018c67ab50af3d6499b2188470f87814**, containing correctness
**f2bc546c63e589cce71354e74d551fd5c2a81279**. Checkpoint SHA256:
`9db706dc05978087acf0b0f48e02c5e3907d975dded01f007847632804d29bf4`.
AGENTS.md, CLAUDE.md and the full revision plan were read, together with the
hard-bound handoff, original independent review, root integration triage,
candidate checkpoint, actual implementation/tests and relevant dependencies.
The renewed bounded authorization governs this task; the old run remains intact.

## Exact source decisions and integration boundary

| Object | Independent decision |
| --- | --- |
| f2bc546 correctness delta over the inherited chain | **ADMIT** both owned paths at the final hashes below. Analytical requests and atomic pre-sampling persistence meet the tested contracts. |
| Final cumulative harness containing 7d432ec43c841d453153a535074eef88af48a263, de6ca3a093a886ebb61dc4ff46cb050c97acdc7e, b62b77efe182e5de9aceccb0bc5aacf97cc4aa5b and f2bc546 | **ADMIT final noisy source/test bytes**, with the separately admitted routing dependency. This is an explicit review of the cumulative implementation, not inference from task completion. |
| Standalone 7d432ec, de6ca3a-era harness, b62b77e and 907a9369a82f4a2d588ff2b8a90db36d2b50a8fe | **BLOCK standalone harness use**: their decoder/ledger/persistence defects remain historical facts. The 907a936 checkpoint's timeout-validation overstatement is not admitted. |
| 9bfa2cddab07b6c2f72d991ebcfc5ad2e1785581 | **ADMIT separately as a metric correction**: omit measurements from gate totals; barrier/delay exclusion remains. It changes neither two-qubit counts nor ESP interpretation. Keep integration separate from correctness. |
| de6ca3a093a886ebb61dc4ff46cb050c97acdc7e layout delta | **ADMIT separately as correctness in the corrected harness**: index the unfiltered initial layout by input positions, then take original width. Dictionary insertion order cannot choose the data mapping. No historical full-harness admission follows. |
| Historical pilot configuration | **ADMIT as exact provenance/reproduction input**, not an instruction to rerun completed observations. Its saved 900s/6GiB settings were overridden to 600s/2GiB in review fixtures. |

| Final input path in C | SHA256 |
| --- | --- |
| `src/logique/benchmarks/noisy_iterations.py` | `4987edae90144c54fa75adb19de02eede03f63d30363bc90285b011c8b383dcd` |
| `tests/test_noisy_iterations.py` | `aa6f3f395722efc3a06de6dff28547af0191efddeb0ef46d87d211099bc47164` |
| `src/logique/benchmarks/routing.py` | `65c502f94955779db4976fa671d86a26387be31b74a48ade8963ddbe4a0a1ca4` |
| `tests/test_routing.py` | `fad76127abb72508e93b4efb379c3e479d2ea0878fd8d0e6843333d2e3beedaa` |
| `configs/noisy_iteration_pilot.json` | `30ed0758402d12ad588cb5464549dfc040b752309739322d1c981055630c4d49` |

Only those five source/test/config paths form this review's integration
intersection. Documentation commits 907a936/92a6e03 are attributed history, not
blanket admissions of claims. Verify identities again on integration.

Relevant dependencies were inspected and bound in `R/identities-history.json`:
iteration input/count/guard/classification helpers, analytical ledger,
preparation/reflection, structure oracle and actual compute inverse, noaux_v24
lowering, QPY resolver/catalogue, weighted depth, coloring model/encoding and
pins. Existing scientific gates remain unchanged; no other algorithms or metrics
from those modules are admitted here.

Candidate `coloring_study.py` SHA256 is
`e212d4984675f15125c4d460f15f1926c442e17eeea6e71c9d137820cd10f938`.
Integration intake additionally contains the separately admitted 4c5f3e4
`basis_identity` field in `run_coloring_study`. The two QPY helpers imported by
this harness are text-identical, verified in
`R/integration-dependency-check.json`. **Preserve the integration version;
do not overwrite that whole dependency with the older candidate file.**

Admission covers the exact hash-pinned ideal pilot, its complete ordered
iterations and clean-workspace static circuits. It is not a general arbitrary-
input, resume or iteration-selection API. Atomic replace protects against process
termination, not power loss/fsync failure. Parent SIGKILL/host loss can leave
running/launching status; this is never completed scientific evidence, and
surviving receipts require inspection. The supervisor owns one thread-only child,
not arbitrary process trees. The static manifest task label still names the
original noisy-channel-repair task; the actual session is dynamic. Future runs
must retain their external task/session receipt rather than treating that label
as a new task identity.

## Historical counterexamples and corrected ledger

Original review SHA256 remains
`1455d3bd2e246fc00ef92244091faa244fa90df48920051a266aa790e0fa8ce9`;
original worker checkpoint remains
`084992dfdfb1f731e18edb1b7b8612db94dcc821ac4408400012a2398058c414`.
The reviewer-written `R/independent_review.py` reproduces both defects from
preserved files:

* Old maintained requests total **755**, versus **805** analytical requests.
  C5 R1 j=0..5 and R2 j=0..3 each lost all five seeds: **50 omitted requests**.
  Exact ideal results still have width 22 and empty executed rows.
* Old K3 R2/seed37/j2 remains timeout, 18 active wires, no counts, and lacks
  allocation estimate, measurement order, routed validation and simulator seed.
  Result SHA256 remains
  `6164a429f93ce77c73969ca60c6a4a7e76e1343ea9b20ad8a4f2cdc2ced9fcd7`.
  New validation does not backfill the historical result.

Six candidate variants inspect the first manifest, prelaunch and within-launch
boundaries, with excluded C5 selected and unselected. All retain 805 requests,
seeds 11/23/37/41/53 and explicit statuses. Excluded C5 children never launch.
A separate reviewer-written first-write interruption proves the complete ledger
exists before child ownership.

Independent reconciliation exercises finished, failed, timeout, interrupted,
launch_failed, launching, budget_excluded, memory_limit,
memory_sampling_unavailable, cleanup_failed, supervision_failed and not_launched
receipts. Every requested index survives; valid completed rows are retained,
incorrect totals are downgraded, running/unstarted rows acquire explicit status,
and absent child rows cannot imply completion. Empty rows/counts, booleans,
negative/noninteger counts and wrong totals cannot certify completion. Candidate
regressions also cover empty results/receipts, absent/unlaunched children, failed
setup, prelaunch interruption, budget exhaustion, unavailable RSS, launch failure
and kill races. These contracts concern internally generated records; they do
not authenticate arbitrary externally supplied counts as scientific evidence.

## Forced termination and quantum contracts

Two complementary forced-kill checks pass. The candidate regression runs its
real QPY/compaction/validation/persistence path with documented mocked components,
routing and sampler. Its synthetic ps result synchronizes the test and is not
RSS evidence. Raw artifacts remain in
`R/pytest-tmp/test_forced_kill_preserves_val0/`.

Reviewer-written `R/forced_boundary.py` uses **real candidate component
construction and U/CX lowering** for an edge with labels 2/7, four logical wires
and two compact active wires. Reference QPY is independently constructed.
Routing/layout/metrics are fixtures; Aer.run writes a marker and sends SIGSTOP.
The parent sends actual SIGKILL and reaps the child, recording exit -9 and a 15s
boundary limit. No sampler output exists. Durable JSON before/after kill matches:

* `stage=validated_pre_sampling`, `status=running`, simulator seed 74728;
* initial/final input layout [3,1,0,2], compact measurement order [1,0];
* allocation estimate 134218240 bytes, norm 1 and restoration 1;
* marginal/full-state residuals 2.220446049250313e-16;
* no counts and no noisy-success estimate.

A synthetic timeout ownership receipt then exercises reconciliation: the row
becomes timeout, zero iterations complete, and validation survives. This is
explicit status injection; the actual child was manually killed at the boundary,
not allowed to time out. Request, QPY/channel fixtures, boundary marker,
before-kill JSON, kill receipt and reconciled manifest are retained under
`R/independent-forced-boundary/`.

Independent two-local-wire channels use explicit unequal damping Kraus products
and a complex diagonal unitary. Ordered qargs [5,1] map to [1,0]; a second unitary
maps [1,5] to [0,1]. Decoded SuperOp equals the independently formed Kronecker sum
exactly (maximum residual 0). Asymmetric readout matches exactly; source JSON is
unchanged. Two compact two-wire diagnostic runs at seed 90131, 32 shots each,
return identical `00:16,01:15,11:1` histograms. These are synthetic diagnostics,
not pilot observations. Candidate tests also reject malformed/wide payloads and
compare original/compacted five/seven-wire statevector trajectories. Only <=2-wire
local channel matrices are formed; no full-system density matrix is used.

Fresh coherent probes use one tiny two-vertex three-color edge under R1/R2/R3,
noncontiguous labels, unequal complex amplitudes over all 16 data words and clean
workspace. The independent reference computes signed coloring/edge-only phase,
`2|a><a|-I`, and emitted preparation followed by its actual inverse. Maximum signed
phase/full-workspace error is 1.6690311775283584e-15; diffusion error is at most
1.1673851243905792e-15. No fitted per-word phase or probability-only acceptance.
Widths are 9/9/7; only one/two-wire instructions are evolved. QPY readback preserves
these exact circuits. This is bounded construction evidence, not an arbitrary
approximate-amplitude or FT/RUS certificate.

Measured QPY tests detect changed qargs/cargs, phase, delay duration/unit, gate and
layout, and reject nonterminal measurement use. Eight three-wire Operator checks
cover both signs and all open/closed control states in CC-Rx prelowering. The
exact metric regression counts X+CX as two gates and one two-qubit gate despite
measurements/barriers/delays; measured wires remain active and readout still
contributes to diagnostic ESP.

## Exact scientific evidence decision

Original pilot:
`/Users/mar/codex-work/logique/dump/1029204240-coloring-dispatch-continuation/worktrees/noisy-channel-repair/dump/1029210538-noisy-channel-repair/runs/1029210741-noisy-iteration-study`.
Manifest SHA256:
`f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278`.
External 805-entry ledger:
`ebd5e4472a3cb43ae7b522cb706ca3f1f3b7fccbfb1f775c46bb1876379ea280`.
All 163 manifest evidence identities match, as do original review/source
identities. No pilot circuit was re-executed and no completed row retried.
Metadata checks confirm 28 completed rows/1792 shots: 15 path3 and 13 K3 rows,
preserving both failed/excluded j2 attempts.

**ADMIT exactly that previously independently reviewed intersection**, with its
original pointwise Wilson 95% intervals and qualifications. Original bitstring,
random-reference and calibration recounts remain attributed to the original
review, rather than repeated here. K3 seed23/j2 remains 21-wire infeasible;
seed37/j2 remains 18-wire timeout with no counts. The complete external ledger
remains 28 complete, one infeasible, one timeout, 775 unexecuted. **No full
30-row/five-seed K3 result exists.**

Random references retain 2048 batches, j+1 draws and seed 71028+100*seed+j;
leakage denominator is 2048*(j+1). Quantum native-two-qubit cost/p and random
sampling/classical-evaluation cost/p have different units. Zero observed
successes give null cost/p; ratios have no intervals. No pooling, simultaneous
coverage, speedup or resilience conclusion follows. Noise includes gate/readout
and gate-time thermal channels, excluding idle relaxation, crosstalk and drift.
Poor K3 outcomes and leakage remain visible.

**BLOCK new C5 execution admission.** Prior ideal manifest
`0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811`
and its 34-case/151-row admission, including 17-wire C5 R3, are unchanged.
C5 R1/R2 retain 22>18 exclusions. The 11-wire allocation candidate does not supply
phase/restoration/witness or execution evidence. Full families, superiority,
general ideal-amplitude claims, FT/RUS and the paper remain **BLOCKED**.

## Checks, resources, retained failures and next owner

Existing `/Users/mar/codex-work/logique/.venv/bin/python`, explicit
`PYTHONPATH=C/src`, no-bytecode writes and no sync. The prescribed private native
binary at
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`
was hash-verified before each check as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`, never invoked.
Versions: Qiskit 2.1.1, Aer 0.17.2, IBM Runtime 0.41.1, NumPy 2.2.6.
Compiler/BLAS/OpenMP/Accelerate/NumExpr/Rayon threads one, Qiskit parallelism off,
one numerical child at a time. Fixture memory/config limits were capped by the
reviewer runner without editing candidate files.

`R/run_check.py` enforces <=120s child and <=600s cumulative deadlines with
kill/reap. Declared 2GiB is checked through terminal wait4 RSS: **not a hard OS
cap or process-group RSS measurement**. The inner supervisor has sampled direct-
child RSS and fail-closed sampling. Arrays are prebounded: fresh statevectors<=9,
existing noisy regressions<=7, dense Operators<=3, channels<=2 local wires.
Original static-FT dense4 is untouched. No full density was formed.

| Fresh check | Result | Boundary seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Candidate noisy/routing regressions | 50 passed, 2 environmental failures | 15.365365 | 150503424 |
| Two supervisor reruns with scoped ps visibility | 2 passed | 0.635778 | 84541440 |
| Independent history/ledger/status/channel/coherent probes | passed | 1.304808 | 167313408 |
| Independent pre-Aer SIGKILL probe | passed | 0.561937 | 128335872 |

Total **17.867888 seconds**, maximum high-water **167313408 bytes**. The nested
kill receipt is inside its outer boundary and not double-charged. All 52 unique
candidate tests pass across two executions; no deselections. The first two
failures remain recorded: sandbox-denied ps triggered memory_sampling_unavailable
instead of expected success/timeout. Logs, receipts and tmp artifacts remain.
Scoped escalation enabled only those two process checks; no automatic approval
rejection occurred. An initial documentation patch was syntactically rejected
before writing any file; the corrected document creation succeeded. No source-
test or scientific failure was hidden. No full-suite/native/notebook/replay/
manuscript/paper validation is claimed.

`R/summary.json` and `R/evidence-hashes.json` are precommit snapshots. The interim
inventory captured the final-validation log before its last success line was
written; that one mismatch is retained in `R/inventory-snapshot-note.json`.
`R/final-evidence-hashes.json` is the authoritative completed evidence inventory.
Exact argv/environment/time/RSS receipts bind task/session, seeds and decisions.
Reproduction requires a fresh timestamped run folder; scripts create outputs
exclusively. `R/completion.json` records the final review commit after commit.

**Next owner: coordinator**, integrate only the admitted five-path intersection,
keeping correctness and 9bfa2cd metric changes separate, preserving newer 4c5f3e4
and running bounded integrated checks with explicit PYTHONPATH. Dispatcher alone
pushes integration HEAD. This reviewer has no remaining owned work.

After integration, separate implementation/review may add an iteration-only
request for **K3 R2/seed37/j2, 64 shots**, with fresh declared bounds. Do not execute
the old full pilot config or retry the 28 completed rows. Preserve the timeout;
seed23/j2 stays excluded until separately validated routing fits <=18. C5
lower-workspace validation/execution and full-paper work remain separate tasks.
