# Scaling harness integration triage — 28 October 2026

Decision: **WITHHOLD all scaling implementation commits**. This bounded triage
batch is COMPLETE; the candidate process/resource contract remains BLOCKED.
The [independent review](scaling_study_review.md) is preserved byte-for-byte from
review commit `4cb96fb681ca03887ce852edfb5ce84461115932` (SHA256
`7dbbbc8027cc27c3a4a4a66eaabf77c66a5211bf6f45af93a62a0a95c8bb1939`). No scaling source, config, tests or pilot metrics enter
integration. Implementation commits `5da2e1e`, `fd62200`, `36e730e` and checkpoint
`f095a5c` remain on the original worker branch. No partial admission is inferred
from their completed task status or the focused green suite.

## Reproduced blockers and correction acceptance

B1: a child sleeping 0.05 seconds with timeout 0.02 exits successfully because
wait4 completion precedes the deadline check after a 100 ms sleep. Define a
monotonic boundary deadline, cap waits/probes by remaining time, and reject
completion observed beyond it. Test the race, cumulative remaining-budget case,
ordinary success, and owned-group cleanup on timeout/interruption/success.

B2: wait4 RSS can include reaped descendants; it is neither isolated direct-child
RSS nor simultaneous aggregate process-group RSS. The new focused regression
reported 81,281,024 bytes versus the immediate child's self peak 16,039,936 bytes.
Correct scope labels/docstrings/guide and future manifests; retain unavailable
ps sampling as null and add a parent/reaped-descendant regression. Preserve all
old pilot values and the original misleading labels as historical evidence.

A correction worker should reuse the original task-owned commits on an isolated
candidate branch, put B1/B2 fixes in a separate correctness commit, and run the
review regressions plus relevant native/scaling tests with candidate PYTHONPATH.
Independently re-review exact changed source/test/guide hashes before any
integration. Future compiler timing must separate boundary observation overhead
from the existing combined bridge timer; disjoint stage timings remain absent.
Do not rebuild or change pins to hide existing mapping-suite incompatibility.

## Focused checks and evidence limits

Checkpoint: `dump/1028012936-scaling-integration-triage/batch.json`.
Fresh serial runs against scaling-harness/src used the existing Python, admitted
hash-verified binary, cache and thread limits 1, with 60-second job timeouts.
Review regressions: **2 failed** in 0.24 s (0.476103 s boundary wall), reproducing
B1/B2. Existing native-process/scaling/native-contract suite: **105 passed** in
15.56 s (15.779573 s boundary wall). Logs and exact commands are saved. Runner
RUSAGE_CHILDREN peaks were 81,281,024 then 84,525,056 bytes; these are cumulative
Darwin waited-child high-water marks including descendants, not isolated job
peaks or simultaneous group RSS. No quantum simulation, build or large study ran.
All enumerated candidate source/test/config/input/evidence and review protection
entries matched; no recursive artifact replay was repeated.

The saved tiny pilot has 110 real attempts: 11 inputs × 2 encoder profiles × 5
repetitions, all labelled ok. There are 90 exhaustive and 20 sampled rows;
100 rows include positive checks, ten K3/k2 rows exhaustively establish zero
solutions. Larger M is unknown. These Boolean network checks do not establish
quantum phases, arbitrary-target action, workspace cleanup or Grover correctness.
The old 12.4020618736 s boundary total includes polling overhead; the combined
bridge timer totals 0.9708516220 s. Stage times are not disjoint. Pilot RSS labels
are subject to B2, ps group sampling is unavailable, and the outer time wrapper
failed (kern.clockrate denied), leaving whole-harness RSS unavailable. Original
145 mapping-suite failures against this binary remain explicit and preserved.

Full DIMACS scope remains open: queen family unspecified; myciel6, myciel7,
DSJC125.1 and le450_5a missing; queen8_8 present/unexecuted; 5-FullIns_3 and
4-Insertions_3 unsupported raw precolored inputs. No precolored work is admitted.
Eligible source provenance, color choices, positive witnesses/unsat proofs,
protocol, broader families/profiles/methods, >=5 large-case repetitions and
explicit timeout/infeasibility ledgers remain required. No scalability, quantum,
FT/RUS, ideal-amplitude or manuscript approval follows from this triage.

## Ownership and release

`continue-full-revision-1028004102` already depends on this finished triage and
owns subsequent priorities. Its actionable correction/re-review/integration
request is saved once in this checkpoint; no duplicate queue chain or successor
coordinator is added here. Existing executed-iteration admissions/ownership are
unchanged. Dispatcher alone publishes committed integration HEAD. README edits,
source inputs, pins, binaries, archives, histories and old results are preserved.
Do not redispatch this completed triage merely because full Task8 remains open.
