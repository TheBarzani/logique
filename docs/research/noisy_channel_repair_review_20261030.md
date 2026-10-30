# Independent noisy-channel repair review — 30 October 2026

**This bounded review is COMPLETE. BLOCK integration of the whole candidate
source chain pending the two concrete bookkeeping repairs below. ADMIT only the
exact 28 completed noisy rows as bounded, conditional observations. BLOCK a
complete 30-row/five-seed sweep, any new C5 R1/R2 execution claim, and broader
noisy-success conclusions.** Queue completion is not scientific admission.

Task `noisy-channel-review-1029204240`, session
`01a18b51-fe63-72e1-9748-44865ce19b0a`, branch
`codex/coloring-noisy-channel-review-1029204240`.
Only this review is committed. No candidate source, results or history was edited;
no integration, push, model/subagent launch, native build or hardware execution.
The required AGENTS.md, CLAUDE.md, full revision plan, hard-bound handoff,
candidate checkpoint/source/tests, relevant prior reviews and actual evidence
were read. The renewed authorization permits this batch; the old 128-batch
ceiling does not negate it. Earlier unfinished probes remain observations.

Candidate `C`:
`/Users/mar/codex-work/logique/dump/1029204240-coloring-dispatch-continuation/worktrees/noisy-channel-repair`.
Reviewed clean HEAD **`907a9369a82f4a2d588ff2b8a90db36d2b50a8fe`**, correctness
**`b62b77efe182e5de9aceccb0bc5aacf97cc4aa5b`**, inherited source/layout/metric
chain `7d432ec`, `9bfa2cd`, `de6ca3a`.
Worker evidence `E = C/dump/1029210538-noisy-channel-repair`;
pilot `P = E/runs/1029210741-noisy-iteration-study`.
Fresh review evidence `R`:
`dump/1030014028-noisy-channel-independent-review/` in this review worktree.

| Exact candidate input | SHA256 |
| --- | --- |
| `src/logique/benchmarks/noisy_iterations.py` | `c5ee2b6ef3d6e6175c4386f4e5a541609b5900b9529acb8eb1b2b1da88c89d3a` |
| `tests/test_noisy_iterations.py` | `7bb45bb46a0b274961a2591449bcd754e02213ec39179afa26801091288ac490` |
| `src/logique/benchmarks/routing.py` | `65c502f94955779db4976fa671d86a26387be31b74a48ade8963ddbe4a0a1ca4` |
| `tests/test_routing.py` | `fad76127abb72508e93b4efb379c3e479d2ea0878fd8d0e6843333d2e3beedaa` |
| `configs/noisy_iteration_pilot.json` | `30ed0758402d12ad588cb5464549dfc040b752309739322d1c981055630c4d49` |
| `NOISY_CHANNEL_REPAIR_CHECKPOINT.md` | `084992dfdfb1f731e18edb1b7b8612db94dcc821ac4408400012a2398058c414` |

`R/audit.json` binds the eight implementation dependencies, pilot manifest,
checkpoint and relevant old failure. All **163** pilot evidence hashes, **220**
worker inventory entries, and the exact ideal manifest's evidence hashes match.
This is a targeted evidence audit, not a scan of unrelated research artifacts.
`R/evidence-hashes.json` binds the fresh probes, logs, receipts and findings.
The candidate checkpoint and results remain authoritative historical bytes;
corrections stated here do not rewrite them.

| Exact evidence identity | SHA256 |
| --- | --- |
| `P/manifest.json` | `f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278` |
| `E/requested-ledger.json` | `ebd5e4472a3cb43ae7b522cb706ca3f1f3b7fccbfb1f775c46bb1876379ea280` |
| `E/summary.json` | `1a53796afacfd4df04db9a5e1c015a4dd1d7dea5025920c065d205dd99d5f010` |
| `E/final-evidence-hashes.json` | `db3ce032c7b9e284c22a57e1ff8627a4a9a4eb9388a19d4c5b61c2ecee0e4c77` |
| `R/evidence-hashes.json` | `46f194acf287a588591784e7021fcb4025a00287f7fe1bf1f60682b6ad06e246` |

## Blocking counterexamples and required repairs

1. **The maintained manifest loses 50 requested iterations.**
   `noisy_iterations.py:1017–1022` derives `requested_iterations` from the ideal
   result's executed `rows`. C5 R1/R2 are ideal-infeasible, so each of their five
   seeds records `[]`. The actual analytical requests are R1 j=0..5 and R2 j=0..3:
   `(6+4)*5 = 50` omitted requests. Thus summing the parent manifest's requests
   gives **755**, whereas its analytical scope and the worker's independently
   recounted `E/requested-ledger.json` give **805**. The external worker summary
   is truthful; it does not repair the maintained harness contract. Populate
   requested iterations from the analytical ledger before launching, and retain
   excluded/unlaunched entries explicitly. Add a regression using the existing
   excluded C5 records; it needs no quantum execution.

2. **A killed sampler loses completed validation metadata.**
   The actual `P/K3_k3_R2_seed37/result.json`, j=2, has `status="timeout"`,
   18 active wires, and no counts. It also lacks
   `working_set_estimate_bytes`, `measurement_compact_wires_lsb_first` and
   `routed_noiseless_validation`. The last progress write is at line 582;
   these fields are populated at lines 589–644 and are not flushed before the
   blocking Aer call at lines 665–667. The next write is after sampling at 697.
   Therefore the checkpoint's statement that j2 has saved validation is too
   strong. QPY and compact noise files do exist. This review independently
   reconstructs their coherent validation, but that new evidence must not be
   attributed to the worker's interrupted result. Atomically persist the
   validated pre-sampling stage and simulator seed before entering Aer; exercise
   forced termination at that boundary. Keep all old partial files unchanged.

These defects do not falsify the completed rows, which have the required saved
metadata. They block accepting the entire source/status repair as complete.
Passing decoder and routing checks below are narrowly positive findings, not
permission to cherry-pick the combined `b62b77e` as a wholly admitted harness.
The coordinator may separately review an isolated exact helper/metric patch or
a successor correcting both issues; no blanket ancestor admission is implied.

## Channel, QPY and coherent checks

The former smoke's unmodified serialized channel still reproduces
`ValueError: too many values to unpack (expected 2)` through bare
`NoiseModel.from_dict`. The candidate decoder reconstructs it and executes its
saved three-wire compact QPY successfully with **64 shots**, seed **72128**.
This is a new diagnostic smoke, not replacement pilot evidence.

A fresh complex-unitary/unequal-amplitude-damping example on ordered physical
qargs **[5,1]**, with asymmetric readout and reversed classical measurement
order, gives identical original/compact 256-shot histograms at seed **8321**:
`00:166, 01:22, 10:55, 11:13`. The decoder boundary receives square, two-dimensional
`complex128` arrays of the proper local size. Serialized inputs are unchanged.
Malformed dimensions, scalar pairs/types, nonfinite values, empty matrix lists
and three-local-wire matrices fail closed. Only local channels of at most two
wires were converted; no full noisy density operator was constructed.

All **306 local quantum channels and 51 readout channels** over the union of
pilot physical labels match a fresh model built from the installed FakeTorino
snapshot. Maximum quantum-channel residual is **1.1102230246251565e-16**;
readout matrices match exactly. Every saved compact noise file equals the
original physical snapshot with only ordered qargs relabeled. The 51-wire union
was never simulated. Calibration bytes match both the pilot and old smoke:

| Snapshot | SHA256 |
| --- | --- |
| Properties | `116c5692ad5669219571ce4c13132fdd68394aa543537b5ccf14a6bd2df10b11` |
| Configuration | `5ee2380a9ac055523b80cde987725216a1b63c1089b6e208bc08db5d2be626f8` |

All **30 logical/routed QPY pairs** were read and checked. Routed readback
preserves operation sequence, parameters, global phase, physical qargs,
measurement cargs, delay units and layout; the candidate's mutation regressions
also pass. Independent compaction reproduces the saved circuit exactly. Active
wires are the union of operated/measured wires, excluding barriers and
otherwise-idle delay-only wires; delays on retained wires remain. Measurement
order agrees with the final logical-to-physical layout. Gate totals exclude
measurements, barriers and delays; routed native two-qubit totals were recounted.
The 21-wire row was inspected as circuit data only and never simulated.

For **29 saved compact circuits**, an independently formed ideal amplitude
vector was mapped through the final layout and compared coherently, including
zero workspace and extra routing wires. Maximum full-state residual up to one
global phase is **3.854844335796954e-14**. Signed logical comparison gives
**8.156117808795256e-15** maximum error; maximum unused-code leakage in these
noiseless probes is **5.319985434177378e-27**. Workspace restores and norms agree
within 1e-10. The timed-out row passes this *fresh noiseless* check without
acquiring any noisy counts.

The independent reference applies marking then `2|a><a|-I` to amplitudes;
it does not read a candidate probability as the expected answer. Exact first
lobe values, with j=1 the first peak and j=2 one beyond, are:

| Case | j=0 | j=1 | j=2 |
| --- | --- | --- | --- |
| path3 k2 R1, M/N=1/4 | 1/4 | 1 | 1/4 |
| K3 k3 R2, M/N=2/9 | 2/9 | 722/729 | 23762/59049 |

Unequal complex amplitudes over all data words independently test signed oracle
phase and matching diffusion, and the actual emitted preparation followed by
its inverse. Largest respective residuals are 2.69e-15, 1.10e-15 and 1.25e-16.
The source uses the emitted compute inverse and preparation inverse; this is
bounded evidence for these constructions with clean workspace. Both replay and
candidate use Qiskit's statevector engine; this is an independent reference,
not two independent simulator engines. **None of these coherent noiseless
checks is a noisy-performance proof, general amplitude guarantee, or FT/RUS
admission.**

## Exact noisy observations and denominators

All seeds **11,23,37,41,53** actually launched, with three requested iterations
each. Ten receipts are terminal and reaped. Nine children finish; K3 seed37
is killed/reaped at its 120-second limit. Its completed j0/j1 rows survive.
The K3 seed23 j2 circuit has **21 active wires**, explicitly excluded; seed37
j2 has **18 wires**, timeout, no counts. No completed row was inferred from
ESP, a top-level schedule status, or coherent validation.

Independent classification of all bitstrings confirms **28 rows × 64 shots =
1792 measured shots**, with the following success counts. Parentheses give
invalid-code counts where nonzero; all path3 leakage counts are zero.

| Case | j | seed11 | seed23 | seed37 | seed41 | seed53 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| path3 k2 R1 | 0 | 15 | 18 | 16 | 11 | 14 |
| path3 k2 R1 | 1 | 50 | 52 | 57 | 51 | 54 |
| path3 k2 R1 | 2 | 14 | 21 | 21 | 20 | 19 |
| K3 k3 R2 | 0 | 9 (2) | 13 (2) | 13 (3) | 11 (4) | 10 (1) |
| K3 k3 R2 | 1 | 3 (37) | 10 (28) | 10 (24) | 3 (34) | 7 (33) |
| K3 k3 R2 | 2 | 9 (26) | excluded | timeout | 8 (40) | 9 (38) |

**ADMIT these exact 28 rows only**, including all 15 path3 rows and the 13-row
K3 partial result. No full five-seed K3 j2 result exists. The corrected external
scope ledger is **28 complete, one infeasible, one timeout, 775 unexecuted**.
The retained old runs still have zero noisy counts; their stale running
manifest and empty receipt remain historical evidence, not newly admitted runs.

Each noisy Wilson 95% interval was independently recomputed by inverting the
score-test quadratic. All 30 rows' random references were independently
regenerated with explicit color tuples, 2048 batches and seed
`71028 + 100*transpiler_seed + j`. A batch always executes j+1 draws; success
means any proper coloring in the batch. Leakage uses `2048*(j+1)` draws, not
2048 batches. Random cost is `(j+1)/p_batch`; quantum cost is native two-qubit
gates divided by measured proper-output probability. All values agree.
Unsatisfiable/all-success probes and the zero-cost/zero-success combination
confirm null cost/p on zero observed successes, never a claimed infinite or
zero true-success probability. The ratio has no confidence interval.

These are fixed-circuit, pointwise shot intervals, with no pooling of routing
seeds or simultaneous coverage. Gate/readout and gate-time thermal errors are
included; idle-delay relaxation, crosstalk and drift are excluded. Random and
quantum resource units differ, so their ratios do not establish speedup.
ESP remains an error-product diagnostic. The poor K3 observations and leakage
are retained; no noise-resilience or comparative-advantage claim is admitted.

## C5 decision

**No new C5 ideal or noisy execution is admitted by this repair.** The exact
prior ideal manifest `0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811`
and its evidence match the earlier independent ideal-only review. That prior
34-case/151-row admission, including C5 R3 at 17 wires, remains unchanged.
C5 R1/R2 in that run remain excluded at 22>18 wires, with no executed rows/QPY.
The best_fit 11-wire allocation candidate is not an independently verified
complete-predicate phase/restoration execution. A separate classical enumeration
here confirms 30 proper C5 three-colorings; it supplies no quantum evidence.
Do not substitute an analytical ledger or the allocated width for a C5 circuit
result. A new lower-workspace candidate needs its own exact independent review.

## Validation resources, retained failures and next action

Existing `/Users/mar/codex-work/logique/.venv/bin/python` was used with explicit
`PYTHONPATH=C/src`, no sync, Qiskit parallelism disabled and all BLAS/OpenMP/
Accelerate/NumExpr/Rayon threads one. The prescribed private native executable
was hash-verified as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
and never invoked. Installed versions match the saved pilot: Qiskit 2.1.1,
Aer 0.17.2, IBM Runtime 0.41.1 and NumPy 2.2.6. One numerical child ran at a time. Prebounded arrays use
at most 18 statevector wires, eight-vector estimate plus 128MiB; full dense
Operators and density matrices were not used. The original FT dense-four cap
was not enlarged. Review supervision has a 300-second cumulative ceiling and
2GiB sampled direct-child limit, not a hard OS or process-group memory cap.

| Fresh review child | Result | Boundary seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Candidate noisy/routing regressions | 43 passed | 3.066332 | 154435584 |
| Independent identities/counts/channels | Three checks pass; initial coherent probe fails | 8.944955 | 454311936 |
| Reflection diagnostic | passes | 0.704125 | 127942656 |
| Coherent v2 | exposes missing timeout fields | 8.918770 | 177127424 |
| Coherent v3 | all 29 compact circuits pass | 19.093798 | 193331200 |
| Decoder/lifecycle probe | passes | 0.576930 | 92766208 |

Total **41.304909 seconds**; maximum sampled/wait4 RSS **454311936 bytes**.
Receipts include exact argv, candidate cwd/PYTHONPATH, elapsed time, return codes,
reaping and thread controls. The initial coherent probe reused a NumPy array
that Qiskit's evolution changed through global-phase handling; deriving the
reference before evolution/copying inputs resolves that reviewer error. Its
source, failed log and receipt remain. V2's missing-key failure is the real
persistence finding above; v3 records the missing fields and independently
checks the saved circuit. No failed attempt was erased or relabeled as passing.
A deliberate interruption of the model turn occurred after the first audit
had exited; its terminal receipt survived. An expired interactive tool handle
was not a live numerical child.

Fresh deterministic supervisor probes verify expired setup and injected
interruption kill/reap ownership with terminal receipts. Candidate tests cover
launch failure, unavailable RSS sampling, kill races, empty results, unlaunched
seeds, budget exclusions and interruption. All 43 pass, but do not cover the two
real counterexamples found here. No full repository/native/notebook/paper
validation is claimed. Scoped automatic escalation supplied process visibility;
no approval-review rejection occurred.

Reproduction: copy the scripts to a **new timestamped run directory**, keeping
old evidence immutable. `run_check.py LABEL LIMIT PYTHON COMMAND...` supplies the
candidate environment and remaining 300-second budget; each receipt records the
exact command used here. `independent_audit.py`, `diagnose.py`, `coherent_v2.py`,
`coherent_v3.py` and `shape_status_probe.py` preserve the complete progression.
Use `coherent_v3.py` for the corrected coherent check, retaining the original
failures. `summary.json` and `evidence-hashes.json` provide task/session, source
identities, numerical budget, decisions and next action; `completion.json`
records the final review commit without a self-referential hash.

Next worker: repair requested-ledger construction and persist pre-sampling
validation, with nonnumerical/forced-termination regressions and exact review.
Keep the completed 28 rows and both failed/excluded attempts immutable. After
source admission, add a separately reviewed iteration-only request for **K3 R2,
seed37, j2**, fixed 64 shots and fresh declared bounds. Do not rerun completed
rows to hide the timeout. Seed23 j2 remains 21-wire infeasible unless a new,
independently validated routing fits <=18 wires. Coordinator alone integrates
exact admitted work; dispatcher alone pushes integration HEAD. The full study
and paper remain open; this review has no remaining owned work.
