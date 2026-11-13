# C5 best-fit noise adapter: exact blocked integration — 13 November 2026

Task `c5-noise-adapter-integrate-1101052342`, session
`01a1d3a0-8834-7250-9550-7bf48eafeb6e`, integration branch
`coloring-paper-revamp-codex`. Historical assigned base `de230cc`; actual intake
`9385226242a52a0a87c646e754785a829f8b093c`.
Checkpoint: `dump/1113013934-c5-noise-adapter-integration-block/checkpoint.json`.
**This bounded integration decision is COMPLETE. Scientific/source gate: BLOCK.
No adapter source, configuration, tests, tools or measurements are integrated.**

## Exact independent decision

[Independent review](c5_noise_adapter_independent_review_20261113.md) is copied
verbatim from `10cecfe1e37b870c6a7cfecefc0fdaf3467f8be9:C5_NOISE_ADAPTER_REVIEW.md`.
SHA256: `718998c02dd82c6d75fb11b2a09c4c8c4cde11e3932be2be584ba0f4023dba9d`.
The committed blob, reviewer working copy and new copy match. The review
explicitly admits **zero new paths** from correctness candidate
`ad6c4630df0844615d62ef4742648cf466b88d2a`, final handoff
`55be27b9882c3d7754e0448217da12edf72ba987`. Queue completion is not admission.

The coordinator verified all ten offered whole-file hashes against both the
committed candidate and working files. Five unchanged inherited files still
equal integration `cf678f72`: metrics, costs, routing, iteration study and
component-lowering tests. Root's noisy caller remains the separately admitted
`0630dc70ecd0a8490acdff8dd661c2e939644be18bd500dd8be91dbae5e22385`,
not the withheld candidate
`b442146d972b22a4680e123f3247d21be1aa7d6f10a85aaa7118826792cf27df`.
Four new adapter paths are absent from root. No semantic merge was attempted.
The earlier [component admission](component_lowering_integration_20261103.md)
and every restrictive ideal/noisy decision remain unchanged.

## Why execution remains blocked

The candidate's `validate_calibration` removes ephemeral error UUIDs and
normalizes JSON containers, but compares independent top-level error records
in serialized list order. Aer can emit these records in different orders in
separate processes. The reviewer reproduced rejection of an unchanged backend
before routing; its same-process worker smoke cannot establish reuse between
request children.

Fresh scalar reconciliation of both saved regenerated snapshots confirms
**965 unique records per snapshot**, keyed by error type, operations and ordered
physical gate qubits. Every remaining payload field equals the worker's saved
snapshot exactly after UUID removal. Both raw key orders differ. No tolerance,
matrix approximation, reordered channel instructions or reversed qargs is needed
for this diagnosis. This fail-closed defect prevents execution; it is not evidence
of incorrectly sampled noise. All failed smokes and reviewer fixtures remain.

## Precise correction and downstream gate

The next implementation must start from these exact candidate bytes and
deliberately compose any required current-root dependencies. Canonicalize only
independent top-level local error records using explicit unique operation and
ordered-qarg identities; reject duplicate or unsupported records. Preserve
internal instruction order, channel matrix shapes/scalars, probabilities,
ordered qargs, asymmetric readout and raw snapshot hashes. Do not delete or
weaken physical calibration validation.

Add deterministic shuffled-record and independent-process snapshot regressions,
alongside rejection of changed probabilities/matrices/calibration files,
duplicates and reversed qargs. Obtain a **new exact cumulative-source independent
review**, covering the entire modified noisy caller and inherited dependencies,
then coordinator byte-exact integration. Only afterward may the already assigned
`c5-noise-missing-execute-1101151114` owner attempt fresh supervised routing and
sampling, followed by `c5-noise-missing-review-1101151114`. No automatic retry,
new model launch, queue mutation or source repair is performed by this decision.
The checkpoint contains a concrete correction specification for the dispatcher.

The separate request population remains $(6\text{ R1}+4\text{ R2})\times5=50$
unlaunched identities with null counts, seeds11/23/37/41/53. These do not replace
the original805 ledger or its50 structure exclusions. Current404 conditional
family request admissions remain separate. No new shots, confidence intervals,
route costs, noise-resilience or manuscript claims follow.

## Verification and scientific limits

Freshly rehashed inventories:86 worker,90 reviewer,50 frozen best-fit and15
original structure-pilot entries; zero mismatches. Candidate imports for ten
modules were asserted to the actual candidate. A fresh isolated tracked snapshot
of current HEAD then passed nine module import/hash checks, inherited-byte and
AST checks. These are scalar integration checks, not numerical regression tests.
With an empty admitted source set, no candidate test or scientific run was
replayed. Review's70 passed/7 deselected remains attributed review evidence.

| Fresh scalar check | Exit | Seconds | Self high-water bytes |
| --- | ---: | ---: | ---: |
| Candidate/evidence/calibration audit |0|1.385473|268681216|
| Current tracked snapshot creation |0|0.095218|22282240|
| Isolated current imports/identity/AST |0|0.282139|72220672|

Budget declared before checks:serial children,120s nominal child envelope,
300s cumulative,1GiB declared process memory,all compiler/BLAS/OMP/Accelerate/
Rayon/Qiskit parallelism1. No scientific arrays,statevectors,dense operators,
density matrices,compilation or sampling were allocated. Only bounded JSON,
source snapshots and imports were used. Receipts record elapsed time and Darwin
self/child high-water RSS separately; no simultaneous group peak or hard memory
cap is claimed. Scalar audit calls had no independent timeout-kill supervisor;
all completed below120s. Existing absolute root venv and explicit source paths
were used without sync. Prescribed native SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was selected and verified, never invoked; root default and all binaries unchanged.

The ten eleven-wire ideal rows and84,441-instruction oracle retain their prior
admission; finite reviewer residuals are not uniform proofs or noise results.
Original22-wire j0,1 evidence was reused by hash, not rerun. Its exact977-instruction
oracle remains PENDING separate clean-data absolute-phase/restoration lowering
proof. No generalized22-wire authorization follows.

Only this decision and the verbatim review are committed. README's existing edit,
dependency pins,histories,archives,prior reports and every failed/partial artifact
are preserved. No model/subagent/Codex subprocess,API/paid fallback,purchase,
hardware or excluded research occurred. Dispatcher alone pushes integration HEAD.
