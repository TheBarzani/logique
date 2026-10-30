# Noisy-channel integration triage — 30 October 2026

Task `integrate-noisy-channel-1029204240`, session
`01a18b60-59a1-7682-bb77-729997542422`, is **COMPLETE**.
**BLOCK the whole candidate source chain; ADMIT the exact 28 independently
reviewed measured rows only as bounded conditional observations.** Full research,
Task 7 and the manuscript evidence gate remain OPEN. This is a fresh decision
on completed review672dc5f, superseding only the earlier missing-review status.
Intake: `97fde8a137fcc5807c84603963f7b179f81b04d3`, integration branch
`coloring-paper-revamp-codex`. Checkpoint:
`dump/1030015553-noisy-channel-integration-triage/`.

## Exact admission and withheld implementation

The [verbatim independent review](noisy_channel_repair_review_20261030.md) is
byte-identical to `672dc5f:NOISY_CHANNEL_REPAIR_REVIEW.md`, SHA256
`1455d3bd2e246fc00ef92244091faa244fa90df48920051a266aa790e0fa8ce9`. The checkpoint's `audit.json` records the actual SHA256 and
all source/evidence identities. Original candidate/review files, failures and
partial probes remain in their original worktrees unchanged.

Reviewed candidate907a936 contains correctnessb62b77e and inherited7d432ec,
metric9bfa2cd and layoutde6ca3a. **None is integrated here.** The review's
positive decoder/routing findings do not constitute an isolated exact patch
admission; cherry-picking their combined source would bypass its explicit BLOCK.
No correctness, configuration or metric source changes are made by this triage.

The fresh read-only audit imports the actual candidate module through its
absolute `src`, matches six checkpoint/source/test/config files to candidate
HEAD, checks the review's bounded source/input identities, all163 pilot evidence
hashes and the review evidence inventory, and independently reclassifies every
saved measured bitstring. It confirms:

* The maintained manifest has755 requested iterations versus805 in the external
  analytical scope ledger. Excluded C5 R1/R2 each retain empty per-seed requests,
  losing50 requested entries across five seeds. The source derives requests
  from executed ideal rows after launch instead of the analytical ledger before
  launch.
* K3 R2 seed37 j2 has18 active wires, timeout and no counts. Its saved result
  lacks allocation estimate, measurement order, routed validation and simulator
  seed. Those fields are computed after the last progress write, then Aer blocks.
  The original checkpoint's claim of saved validation is too strong. The
  independent review's fresh coherent check is new reviewer evidence, not
  metadata persisted by the worker. QPY/channel artifacts survive unchanged.

## Exact bounded observations

Pilot manifest SHA256:
`f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278`.
Evidence remains under
`dump/1029204240-coloring-dispatch-continuation/worktrees/noisy-channel-repair/dump/1029210538-noisy-channel-repair/`;
its pilot subdirectory is `runs/1029210741-noisy-iteration-study`.
The exact external ledger hash is
`ebd5e4472a3cb43ae7b522cb706ca3f1f3b7fccbfb1f775c46bb1876379ea280`.

The reviewed intersection is **28 completed rows ×64 shots =1792 measured
shots**, all15 path3 k2 R1 rows and13 K3 k3 R2 rows. Seeds11/23/37/41/53 each
request j=0,1,2. Success counts are copied from, and freshly recounted against,
the saved bitstrings; parentheses show nonzero invalid-code counts.

| Case | j | seed11 | seed23 | seed37 | seed41 | seed53 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| path3 k2 R1 | 0 | 15 | 18 | 16 | 11 | 14 |
| path3 k2 R1 | 1 | 50 | 52 | 57 | 51 | 54 |
| path3 k2 R1 | 2 | 14 | 21 | 21 | 20 | 19 |
| K3 k3 R2 | 0 | 9 (2) | 13 (2) | 13 (3) | 11 (4) | 10 (1) |
| K3 k3 R2 | 1 | 3 (37) | 10 (28) | 10 (24) | 3 (34) | 7 (33) |
| K3 k3 R2 | 2 | 9 (26) | excluded | timeout | 8 (40) | 9 (38) |

The complete805-entry external ledger remains28 complete, one21-wire
infeasible, one timeout,775 unexecuted. Ten seeds launched; nine children finish
and one is killed/reaped at120s, retaining its two completed rows. There is no
complete30-row/five-seed K3 sweep. The old two runs still have zero noisy counts.

Use only the saved pointwise Wilson95% intervals for each fixed64-shot circuit;
no routing-seed pooling or simultaneous coverage. Random references use2048
batches, j+1 draws per batch, seed71028+100*transpiler_seed+j; their leakage
denominator is2048*(j+1). Quantum cost uses native two-qubit gates per measured
proper output; random cost uses draws plus classical predicate evaluation.
The different units and ratios without confidence intervals establish no
speedup. Zero successes produce null cost/p; ESP is a diagnostic.
Noise includes gate/readout and gate-time thermal channels; idle-delay
relaxation, drift and crosstalk are excluded. The poor K3 observations and
leakage are retained. No resilience, superiority, general ideal-amplitude,
FT/RUS, full-family or paper approval follows.

No new C5 execution is admitted. Prior ideal-only34-case/151-row admission,
including C5 R3 at17 wires, remains unchanged. C5 R1/R2 remain excluded at22>18
wires in that exact run. The best_fit11-wire allocation candidate still needs
complete-predicate phase/restoration/witness review and actual execution.

## Focused successor chain

Exactly three jobs were appended atomically to the authorized continuation
queue, from11 to14 definitions, with existing headers/definitions unchanged:

1. `noisy-ledger-fix-1030015553`: correctness/high, own separate branch/worktree
   initialized at907a936. Repair the prelaunch805-entry analytical ledger and
   atomic pre-Aer validation/seed persistence, with excluded-C5 and forced-kill
   regressions. Own only the noisy harness, its tests and a new checkpoint.
2. `noisy-ledger-review-1030015553`: critical_review/high, separate branch and
   worktree at97fde8a. Review exact new hashes plus inherited dependencies,
   original counterexamples and termination/status/channel contracts; give
   correctness and metric/evidence decisions separately.
3. `noisy-ledger-integrate-1030015553`: coordinator; candidate checks, exact
   independently admitted integration and integrated checks, or complete with
   explicit scientific BLOCK/actionable follow-up. Preserve metric separation.

Each has1800s and12 attempts for transient pauses, within the new run's128
additional-batch ceiling and unchanged2November00:00 local deadline. The old
128-batch run, all histories and current state are untouched. `queue-before.json`,
`queue-proposed.json`, prompts and `queue-append-receipt.json` preserve the exact
change. Worktrees were created without launching models. Dispatcher alone
launches and publishes integration HEAD; no push occurred here.

This chain performs source repairs/integration only, without rerunning the28
completed rows. After exact admission, a separate reviewed iteration-only child
request may retry K3 R2 seed37 j2,64 shots,120s child/900s fresh cumulative.
Seed23 j2 stays21-wire excluded unless separately validated new routing fits18.
The existing `continue-full-paper-1029204240` owns broader scheduling and should
reuse this chain rather than duplicate it.

## Full tasks1–8 and evidence gate

The complete [hard-bound scope matrix](full_research_bound_handoff_20261029.md)
remains applicable. Later decisions supersede only their specific missing-review
entries; no scope is dropped by this bounded triage.

| Task | Current admitted/reused state | Concrete open work / gate |
| --- | --- | --- |
| 1 — audit/manuscript | Preserved histories/replay and exact results-independent9a980ec→eee7baa; this review and bounded observation ledger | Evidence-dependent evaluation, figures/tables, responses, contribution/title/abstract/conclusion; final research checks, native provenance, offline notebook copies, isolated135 replay, TeX/PDF verification and independent final Astra correctness/claim review. Full paper OPEN. |
| 2 — controls | Existing R1–R3, normalized labels/bit order, witnesses/QPY/restoration and service/context4c5f3e4 gates | Full target/routing/calibration/precision/process controls, workspace policies/live peak and protocol freeze. Missing identities cannot certify comparability; compiler stage splits unavailable. |
| 3 — costs/MCX | Existing restricted exact gadget, T-count/dependency-depth, expanded-inverse, clean_tree/fresh_zero and numerical rotation admissions | Matched whole-circuit policies across comparators/domain checks/conjunction/diffusion/k-LUT/best-fit; clean/dirty/throwaway mirrors/conditionally clean and analytical Dutta; bounded Gray3..20 including open>10; full/component logical/common/routed/FT costs and held scratch/restoration. No blanket FT/MCX admission. |
| 4 — comparisons | Existing partial9240b80/a31bb24, service/context4c5f3e4; all losses retained | Wide-QPY closed-control31/32/33 phase/inverse/scratch repair/review;43 unrun groups and clipped myciel5 group after budgets/admission; nine graphs/R1–R3, larger CEC/witness proof, strongest baseline/exact intersection, common lowering, routed seeds11/23/37/41/53 and precision1e-3 plus1e-2/1e-4. sb_original excluded. |
| 5 — mechanisms/native | Existing serialized/shared/in-place/eager/balanced/structure bounded admissions; sequential transition proof92784ef only | Capped production Boolean-value/two-cone validator with canonical cleaned topological domain, f_n/W[q]/frame/control reads, release/restore/output checks and private provenanced build/review; e2d054b withheld. Other native mappings, MC reduction, cut/ESOP balancing, SAT budgets, preprocessing CEC, structure common lowering/tradeoffs remain open. |
| 6 — graph FT/RUS | Restricted numerical rotation compiler and isolated static pilot; supplied-cost/analytical RUS ledgers | Meaningful graph FT using emitted A/inverse and whole-algorithm repeated error budgets, phase/restoration/error and preparation break-even; preserve original dense4 pilot cap. Separately execute/review dynamic RUS channels, branches/abort/retry/resources/coherent restrictions; never substitute into static A/A†. |
| 7 — success/noise | Prior exact34-case/151-row ideal-only admission; newly admitted28 bounded noisy observations | Whole noisy source chain BLOCK on two real bookkeeping defects; focused chain above. Full paths3..8/K3/C5/P4 non-power-of-two first-peak+one-beyond, full five-seed/routed/noisy/random/leakage/confidence/cost evidence remain incomplete. C5 R1/R2 best_fit11 allocation is unadmitted. |
| 8 — scaling | Admitted input/helper/witness/pending ledger and historical timer only; zero selected compiler invocations | Completed cleanup review44ad4ba BLOCKs single-SIGINT cleanup/reaping/receipt ownership. Existing cancellation correction→review→integration/execution→evidence chain remains queued. All220 selected attempts/two profiles/five slots plus full DIMACS/controlled study, witness unknowns and M unknowns remain open; actual queen-family-5/queen8_8/planted32 five repeats only after source admission under90s child/900s cumulative/<=6GiB. |

The evidence gate stays **BLOCKED**: no complete matched strongest-baseline
comparison, full ablations/resource study, selected scaling evidence or complete
iteration/noise family coverage. This pilot cannot determine a full-paper
improvement/tradeoff/resubmission conclusion. Hardware, physical QEC, precolored
research and conditional-workspace synthesis stay excluded.

## Validation, failures and preservation

Existing root `.venv/bin/python` and explicit candidate/root PYTHONPATH were
used; native SHA256 verified as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`,
never invoked. No sync, build or dependency change occurred. BLAS/OpenMP/
Accelerate/NumExpr/Rayon threads1, Qiskit parallelism disabled. No scientific
sampling, full noisy density matrix, >18-wire statevector or >5-wire Operator
was run; tests use tiny fixtures (routing Operators3 wires), retaining staticFT4.

The final metadata audit took0.314734s and31,129,600 bytes self high-water RSS, under
60s/256MiB terminal-self bounds, streaming hashes with10s Git child timeouts.
Its initial coordinator-only probe misread `case.vertices` as an integer;
exit1/TypeError and original script are saved, then corrected to list length.
No candidate failure was hidden by that correction.

The first candidate37-pass/6-deselected check and root routing11-pass check
briefly overlapped because the coordinator launched root checks before receiving
candidate completion. Both logs/receipts remain; those timings are diagnostic.
The checks were repeated serially to comply with the resource contract.
Serial candidate results:37 passed/6 deselected,13.960127s,
154,451,968 bytes wait4 high-water. Serial unchanged-root
routing results:11 passed,9.805286s,
145,883,136 bytes. Exact command/time/RSS receipts are in the checkpoint.
Candidate supervisor tests were deliberately deselected; the prior independent
43-pass review remains attributed to that reviewer. These checks do not admit
the two uncorrected source defects. Root routing checks exercise unchanged root
behavior, not an integrated noisy repair. No full-suite/native/notebook/paper
validation is claimed. Each check has60s child limit and2GiB terminal wait4 RSS
check, without a hard OS memory cap or process-group memory measurement.

Worktree creation initially hit a sandbox ref-lock denial; scoped escalation
succeeded without approval-review rejection. Only selected planning/research documents
are committed. README's original modification/hash is preserved, as are pins,
archives, nested histories and all earlier failed/partial evidence. This task
has no remaining owned implementation work; dispatcher successors own repair.
