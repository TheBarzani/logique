# Restoring MCX representation ledger

This records decomposition and representation changes, not performance gains.
Correctness is integrated separately as `93bba09` and `b4ed5fa`. Only the owned
source/test portion of worker commit `0eacb13` supplies this metric change;
the worker checkpoint is preserved in the coordinator run, not cherry-picked.

Opt-in `clean_tree` / `fresh_zero` emits primary level `restoring_mcx`, marked
`restoring_mcx_resolved_standard_gates`; optional unrouted U/CX is explicitly
`restoring_mcx_common_basis_resolved_standard_gates`. CCX remains a primitive.
These counts cannot be merged with historical opaque/logical or FT counts.
Explicit decomposition/scratch fields and costs.py provenance are opt-in only.

The worker's immutable row ledger is
`dump/1025125442-qpy-coordinator-triage/worktrees/restoring-mcx/dump/1026021845-restoring-mcx/representation-ledger.json`,
SHA-256 `c84e28eb807247289bc5e447225360aaddd6c78012ef82d63c07782c07bd87c7`.
Four fixtures (edge k3/k5, isolated k5, unsatisfiable triangle k2), R1/R2/R3,
j0/1, seed7 and U/CX optimization0 yield 216 cases: 210 complete, six retained
sb_original exclusions, zero failed final cases and 2,100 saved rows.
The earlier 18 failed mixed-register exports retain their partial artifacts
and zero failed-case rows; those exports are not admitted.

Candidate and integrated coordinator independent replays each recount all 2,100
saved rows directly. An integrated additional replay freshly assembles all 210
complete cases and checks 1,050 primary components' ordered definitions, scalar
phases and workspace metadata against the saved QPY. All 480 omitted-option
artifacts are byte-identical to the a57e84f reference with identical metrics.
On those 480 matched rows opt-in changes 196 widths, 162 gate maps and 162
count/depth totals. These changes are independently confirmed by the reviewer;
reserved width and construction scratch capacity are distinct from live usage.
Measured native timing overlaps synthesis; unavailable mapping, optimization,
process-memory and general live-workspace fields remain null.

Exact source identity and bounded semantic admission are in
[the coordinator admission](restoring_mcx_admission.md) and the byte-preserved
[independent review](restoring_mcx_review.md). Commands and fresh replay evidence:
`dump/1026071418-restoring-mcx-coordinator-triage/`. Unsafe prior QPY/pilot
artifacts, historical tables and archived results remain unchanged and require
separate evidence review. This is no full study, superiority, freeze or paper
approval; wider original-to-transpiler equivalence remains excluded.
