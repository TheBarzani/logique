# Selected scaling integration decision — 1 November 2026

Task `scaling-admit-selected-1101052342`, assigned root integration branch
`coloring-paper-revamp-codex`; assigned base `de230cce74089344343fcdf1c12d553cc4cf8607`,
actual intake `34f9e6372215648c26cff5dd7070caf368172a61`. This bounded integration triage is COMPLETE
with **scientific BLOCK**. Further source correction and exact independent
review are required; the full research/manuscript remains open.

Checkpoint: `dump/1101202146-scaling-selected-exact-block-integration/checkpoint.json`.
No candidate implementation, build, execution configuration or research metric
was integrated. No selected compiler ran. There is no new correctness commit
or metric commit: only this evidence decision and the exact review are tracked.

## Exact independent decision

Reviewer commit `d7b9496e59daee15733bb8402fb7875899c80e01` explicitly **BLOCKs the entire
composed source** at correctness `f444e428d4d3c19562e4b1a36815e2f427245848` and candidate HEAD
`59aa7c1053aeb491062bfe25f39fc4f1131c4027`. Its admitted implementation path list is empty.
The [verbatim review](scaling_current_composition_review_20261101.md) has SHA256
`523a3be9ff343721ce89d5a8d68b82f3b617dae2a75926490e4fe5906d08e767` and equals the reviewer Git blob and working file.
All twelve offered paths match their committed blobs and recorded SHA256s;
all remain withheld. This includes the seven process/runner/test/config files
carried identically from the older finalization ADMIT `0f8c9c7` of `a8b3606`.
That historical admission does not admit the current native composition.
No semantic merge or partial source extraction was attempted.

Fresh audit passes **96 source/context identities, 77 unchanged current-root
context paths, 589 candidate evidence entries and 1,116 reviewer evidence entries**.
Twelve actual module imports resolve to the explicit candidate `src`.
Current tracked root source matches its committed blobs; absent candidate-only
implementation paths remain absent. Candidate/reviewer branches are clean.
Both foundation and separately admitted SAT binaries retain their exact hashes.

## Reproduced accounting-transfer blocker

The current candidate restores the caller's SIGINT handler inside `run_bounded`
before `native.py` copies genuine receipt data into the caller dictionary.
A first SIGINT immediately before the success update (line88) or exception
update (line77) replaces that control flow with the original interruption.
The runner saves its positive elapsed fallback, but loses known status, return
code, RSS, cleanup and reaping fields. SAT timeout translation shares this path.

Fresh execution of the exact committed reviewer probe reproduces **both failures**
at the genuine receipt equality assertion (exit1 each). A two-input XOR shell
fixture and a sleeping child are process-control evidence, never compiler
performance or quantum evidence. Each probe includes an unchanged prior row
and one interrupted current row; two calls return and no further call is made.

| Fixture second call | Genuine boundary s | Saved/charged fallback s | Genuine RSS bytes | Return code | Genuine status |
| --- | ---: | ---: | ---: | ---: | --- |
| success | 0.114186792 | 0.115980041 | 1,982,464 | 0 | exited |
| timeout | 0.035135875 | 0.036491166 | 32,768 | -9 | timeout |

Both leaders were actually reaped; original exception identity is preserved,
current manifests are valid interrupted JSON, exact cumulative row-charge sums
remain positive, and no emergency cleanup occurs. Saved RSS is null and saved
return code/status/cleanup/reaping details are absent. This is receipt loss,
not a demonstrated live-child leak or a lost elapsed charge. Instrumentation
overhead and polling make these timings unsuitable as synthesis measurements.
The review's 99 passing transaction probes, 172 maintained passes and 24
preserved passes remain its restricted historical observations; they were not
rerun wholesale or treated as overriding the two whole-chain failures.

## Research evidence retained

The original selected ledger SHA256 is
`d650687aa6678189904c77929bab42f43332f218373eb8f641750805bc6650cc`; all ten prepared input hashes and canonical witness
hashes were freshly bound. `(10 + 12) × 2 × 5 = 220` original selected/controlled
slots remain pending, **zero selected runs**, not a five-repeat study.
Full DIMACS remains in scope. Eight supplied witnesses remain available;
DSJC125.1/le450_5a positive witnesses and every selected solution count M remain
unknown. Validation seeds11/23/37/53/71 and graph1729 are unchanged.
Unavailable stage splits stay null; bridge and boundary times overlap.
The candidate BLOCK gate was tested with sentinels and rejects before native
provenance, output creation or compiler launch. No pending manifest is a run.

## Precise next correction and admission gate

1. Start from the exact current composed candidate and deliberately preserve
   current-root SAT and other admitted dependencies. Protect the complete
   process return/exception-to-caller receipt transfer, including before and
   during both dictionary updates and SAT timeout translation.
2. Preserve the first interruption object, real process status, complete
   receipt and caller handler policy. Finishing transfer must not run another
   native call, repeat cleanup/wait, or signal a reaped/reusable PID. Keep
   existing failed-call charges and atomic runner persistence intact.
3. Obtain a new exact whole-chain independent decision covering both saved
   receipt failures and previously passing transaction/cleanup/SAT gates.
   A fragment review or old ADMIT does not release this composed source.
4. Only whole-source ADMIT permits candidate checks, exact root integration
   and fresh isolated integrated checks. Then create a dated selected execution
   configuration and run only missing queen-family-5, queen8_8 and planted32
   slots, five repeats, <=90s child/900s cumulative/<=6GiB declared budget.
   Preserve compiled positive/negative checks, networks, all failures/timeouts,
   null unavailable splits, overlapping time scopes and qualified RSS. Separate
   correctness from research metrics; require independent evidence review.

This report is a concrete correction handoff for the dispatcher/final coordinator,
not a new model launch or a queue admission. Existing selected-evidence and
full220 successors must honor this BLOCK; do not rerun this completed triage
or launch experiments merely because predecessor jobs finished. No queue,
state or history was edited and no new jobs were appended in this assignment.

## Resource and preservation scope

Declared before work:120s/child,180s cumulative,1GiB/process,serial children,
all compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. Audit plus both
probes: **5.379157s supervised boundary**, maximum wait4 high-water
**72,138,752 bytes**. No quantum arrays, native build or scientific compiler.
Darwin wait4 may include reaped descendants; simultaneous group peak and hard
allocation caps are unavailable and not claimed. Fixture child limits are2s
success/0.025s timeout, not selected-study limits.

The absolute existing root venv Python and explicit candidate PYTHONPATH were
used without sync. The unchanged foundation executable was explicitly selected
and hash-verified as `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the separate SAT build remains
`81bc6a786f29a5673881ef37c5fb0da02cec9d22a649b9d518d1b31db5d71571`.
Neither was invoked or rebuilt. Candidate/integrated acceptance suites are gated
by source admission; no root source changes warranted integrated acceptance here.
Commands/exits/time/RSS,task/session/commit identities, hashes and new failed
probe artifacts are retained in the checkpoint. Read-only initial inspections
have tool exit records but no separate measured RSS/time. Long combined reads
were followed by focused reads; two prospective new document paths were absent.

README hash `73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`, pins, histories, archives, old failures,
candidate/review evidence and restrictive scientific decisions are preserved.
No models/subagents/Codex subprocesses,API/paid fallback,purchases,hardware,
physicalQEC,precolored/conditional-workspace research,sync or push occurred.
Dispatcher alone launches successors and publishes committed integration HEAD.
No scalability, quantum phase/restoration, comparison, C5, FT/RUS, noise or
full-paper admission follows from this completed integration decision.
