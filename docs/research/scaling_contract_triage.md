# Scaling contract integration triage — 28 October 2026

Decision: **WITHHOLD integration; BLOCK scaling execution** under the
[exact-hash gate](scaling_study_admission.md). This bounded batch is COMPLETE.
The original [triage](scaling_study_triage.md) remains historical; the correction
and independent re-review are a new completed batch, not a relaunch of it.

Task `integrate-scaling-contract-1028023823`, session
`01a18153-ffcb-7953-87ed-fd290bbc2680`, integration intake
`fc734b386449e69716d0ac3018b878a23e05ba95`.
Checkpoint: `dump/1028030635-scaling-contract-integration-triage/batch.json`.
All required plan documents were read; renewed full-plan authorization applies.
The review report is preserved byte-for-byte with its source identity checked
against review commit `5411998`. Candidate HEAD, original/correction ancestry,
18 relevant candidate identities, five review evidence identities and the native
binary hash were verified. No recursive old-pilot artifact scan was repeated.

## Fresh reproduction

Two serial jobs used the existing research Python, actual scaling-fix/src
PYTHONPATH, cache `/Users/mar/codex-work/logique/.cache/epfl`, and the required
private native binary SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
All numerical thread limits were 1. Each job had 30-second wall/CPU limits,
a 2 GiB terminal wait4 memory check and a cumulative 60-second wall budget.
This was not hard aggregate memory enforcement; simultaneous group RSS was
unavailable. Small fixture allocation bounds were retained. Only existing tiny
quantum fixtures (at most five qubits) ran; no larger simulation, dense Operator study, native build or larger compiler
study was launched.

| Job | Result | Boundary wall seconds | Darwin wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Three real cleanup races + cumulative-ledger regression | 4 failed, pytest exit 1 | 1.9631352080 | 44,154,880 |
| Candidate process/scaling/native-contract + original B1/B2 tests | 114 passed, pytest exit 0 | 17.4799298332 | 84,721,664 |

Wait4 is per invocation, may include reaped descendants, and is neither isolated
process RSS nor simultaneous group RSS. Both jobs stayed within the declared
bounds. The validation wrapper's exit 0 means the expected BLOCK evidence and
compatibility results were verified; it does not mean the four regressions pass.
Full logs, commands, receipts, copied replay scripts and identities are saved in
the checkpoint directory. Candidate source, review evidence, binary, queue and
root README hashes remained unchanged after tests.

The three direct cases again raised real PermissionError after an observer delay
following the final WNOHANG return. The study fixture again launched all five
calls, labelled each failed and left native process time null instead of one
timeout followed by four budget-exhausted rows. These synthetic boundary tests
are not compiler performance measurements. The focused green suite does not
resolve this counterexample or the historical 145 mapping-suite failures.

## Preserved scope and next ownership

Original 110-attempt tiny pilot, B1/B2 evidence, labels, values and failed outputs
remain untouched. Its boundary wall 12.4020618736 s and combined bridge timer
0.9708516220 s are distinct scopes, not disjoint stages. It remains historical
B1/B2-scoped evidence, with no retrospective admission. Correction attempt 1's
previously overwritten full log and reconstructed-receipt limitation remain
explicit in the copied report. Missing/unsupported selected-DIMACS ledger,
unknown counts, five larger repeats and truthful stage/resource scopes stay open.

At intake queue/state had 76 definitions and 106/128 batches; re-review was
complete and this integration task running. The existing selected-scaling job
requires this gate and explicitly permits independent input/witness/protocol
preparation when blocked. It must preserve that actionable status without
executing the unadmitted harness. No queue or state was edited. Other subsequent
scientific jobs retain their existing ownership and may inspect this gate.

Already queued `continue-full-research-1028023823` owns arranging the next bounded
cleanup/accounting correction, independent review and integration, as specified
in the admission gate. It also owns full-plan continuation after existing reviews.
No duplicate final coordinator, model, subagent or Codex subprocess was launched.
Actual commit inspection found `36e730e` contains only a scaling regression test,
not documentation portions; it too stays withheld. No code, research metrics,
dependency pins, archives, histories, old outputs or
README edits were integrated or altered. Only task-owned review/admission/triage
copies and status additions enter integration. Dispatcher alone publishes HEAD;
this batch performs no push, hardware, API/paid fallback or environment sync.
