# Independent graph FT review

Task `graph-ft-review-1030020413`, 31 October 2026, America/Montreal.
Assigned review branch `codex/coloring-graph-ft-review-1030020413`, base
`e90adf3373236ef51a937480febd3cd7d669dce7`. **Review COMPLETE.**

**Correctness ADMIT**, restricted to the fixed edge harness and numerical
contract below, for exact candidate commits
`a7281df4021838688b4a071d549a30520f956ee4` and
`a65e6729abd6eee79940982e3e7d96fd1b6ca6ba`.
**Build: no changed build to admit**; the prescribed existing binary is verified.
**Evidence ADMIT**, as bounded numerical observations, for the 12 completed
study rows and identical-circuit final-source smoke in checkpoint commit
`b84b2df419e197b50cf836107443cfb1d7bac032`.
**Scientific BLOCK** remains for j=1 at 1e-4 with the fixed synthesis options,
general achieved preparation break-even, broader graph/iteration/precision
coverage, and full-paper conclusions. The three failures are admitted as
failure records, never as missing-cost estimates or completed search results.
No candidate changes or root integration were made by this reviewer.

## Exact inputs and scope

Candidate worktree is the sibling `graph-ft-execute`, HEAD
`b84b2df419e197b50cf836107443cfb1d7bac032`, clean at intake and final inspection.
Only three paths differ from the assigned base. The two correctness commits
add the harness/tests; the third separately records evidence.

| Candidate path | Final SHA256 |
| --- | --- |
| `src/logique/benchmarks/graph_ft.py` | `ae6c3f93c3ef2fb0abc279bafe300ef5c986f1e14700092a3dde903e08adb220` |
| `tests/test_graph_ft.py` | `4e8c1396a0da7e9b4c2cec19116d19422ef01214b8080ed1bd7bc390514dabc9` |
| `GRAPH_FT_CHECKPOINT.md` | `fda29a590de9146449751a6beb0a72d191e5650069c6a302231ff093e7910f4d` |

The original 15 study rows bind a7281df harness SHA256
`6b574551351df2ed5691ae83bedfba1c704b06ddb687bae3cf92ba306ba9810e`.
The final-source smoke binds a65e672. Its six emitted QPY artifacts are
byte-identical to the original R2/j=1/1e-3 artifacts. The final correction adds
only request rejection before allocations, leaving the successful path intact.

Candidate evidence root: `../graph-ft-execute/dump/1031151632-graph-ft-execution/`.
All **409** files in its final manifest independently match sizes and SHA256s.
Manifest SHA256 is
`6f20f0abb3870f251652f80a8b0ae860b67d02d5ff3719d4d83796ccb87132da`;
command ledger SHA256 is
`e1882a07601993560b0999f959cba881f66db761aab5e6e285133022f02a063d`.
Input Verilog hashes, before/after identities, 16 result records, all failures,
summary comparisons, source checkpoint and actual source/tests were inspected.
The earlier active-log manifest remains historical and is not the binding one.

The unchanged executable is
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`,
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No native rebuild or invocation was needed for the saved-circuit review.
The original static pilot source/tests, rotation source/tests, and lockfile
match base bytes. Original pilot source remains
`bc1ea4a1955d517f59c178d36d616ac67123e6e31093a8b81859534e01167c16`;
rotation source remains
`5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595`.

Read AGENTS.md, CLAUDE.md and the full revamp plan, the 29 October hard-bound
handoff, and the 30 October continuation from root because it is absent at this
base. Read rotation-norm admission/caller obligations, static-pilot admission,
original critical counterexamples, actual original pilot failure manifest,
architecture and relevant preparation, compiler, cost and threshold sources.
Read the active continuation queue without modifying it: its own max_batches
is 128 and deadline is Nov 2 00:00 local. Queue outcomes provide no admission.

## Compositional and semantic assessment

The actual problem has vertices 7 and 11, edge (7,11), k=3 and four LSB-first
data bits. Independent direct two-bit decoding gives six proper colorings
among 16 bitstrings, nine valid-code strings. The R1/R2 Verilog enforces both
domain checks and inequality; R3 removes only the domain checks. Native widths
are 13 and seven, respectively. These are meaningful edge constraints, unlike
the isolated-vertex original pilot.

For oracle V and clean embedding J, independently enumerating each column of
`V J - J D` establishes a numerical Frobenius upper bound on its spectral
norm. Here D is the independently decoded phase diagonal. Tensoring this
restricted operator with an identity reference does not increase that norm.
This supports coherent clean-input and external-reference action within the
numerical tolerance; it is not a dirty-scratch or exact floating-point theorem.
A and signed S0 operate only on the explicitly mapped data wires, so the
ideal clean oracle composition preserves the clean subspace. Actual residual
scratch and approximation gaps remain numerical observations.

Independent probes checked 192 clean columns across source/emitted oracles
for all six completed j=1 study rows, plus seeded complex superpositions.
They used direct color-bit arithmetic, not worker predicate/event helpers.
Maximum single-column discrepancy was about 1.244e-14 for R1/R2 and 1.359e-15
for R3. The seed is 1030020413. Local matrices checked signed
`S0 = diag(1,-1,...,-1)`, preparation against its intended initial vector,
and the adjoint of the actual emitted A, including scalar phase.

The independent evaluator fuses consecutive same-wire numeric gates without
normalization, then multiplies bounded four-wire matrices. Every saved full
j=1 search is authenticated against the ordered emitted component words,
mapped wires and scalar phases. The independently composed state is
`A S0 A† D A|0>`; six j=0 searches are independently checked as A alone.
This provides a different numerical implementation from the worker's full
statevector execution. Full states are not dense 13-wire Operators.

The unchanged compiler charges `(1+2j)n_A + j(n_O+n_S0)` rotations and scales
weighted component/preprocessing/assembly errors by its original norm product.
The reviewer recomputed these metadata relations and checked allocations for
every completed row. A is synthesized once and its emitted adjoint is reused.
Gray-code lowering precedes synthesis; S0's 21 residual rotations at j=1 are
included. Numerical recursive targets remain the reference: neither ideal
amplitudes nor exact unitary normalization replace them. R3 is compared with
its own edge-only target; approximate invalid-code leakage is retained.

This extension satisfies the original rotation caller obligations for the
fixed construction. The original pilot's four-qubit dense cap is unchanged:
the independent probe still gets ValidationLimitError on its 13-wire input.
The preserved old manifest is at
`/Users/mar/codex-work/logique/dump/1025034429-rotation-admission/worktrees/static-ft-pilot/dump/1025082919-static-ft-pilot/manifest.json`
and still records the 13-wire/dense4/statevector5 exclusion. New clean-column
validation does not retroactively widen that pilot or certify arbitrary graphs.

## Evidence, costs and counterexamples

All **60 emitted QPY circuits** from 13 completed executions independently
reproduce gate counts, widths, T-count and dependency T-depth. No worker cost
helper was used. T-count obeys actual concatenation; T-depth is independently
propagated through shared-wire dependencies, not added across components.

| Primary j=1 regime | Full T / dependency T-depth | Independent state error | Proper success | Invalid-code leakage |
| --- | --- | --- | --- | --- |
| R1 | 271982 / 194958 | 0.000193027004125 | 0.843773134666 | 0.109345018925 |
| R2 | 353792 / 222800 | 0.000167225122003 | 0.0740740781462 | 3.47999853e-9 |
| R3 | 353624 / 222764 | 0.000167225122003 | 0.0740740781462 | 3.47999853e-9 |

All nonzero approximation errors independently satisfy recorded compiler
bounds without extra slack. Only algebraically exact Clifford component
comparisons use a 1e-12 floating-comparison tolerance, because saved source
QPY expands H to U while emitted QPY retains H. This is not a general numerical
error theorem. Observed inverse discrepancies stay below 3e-14. The 1e-2 rows
and all six j=0 rows also agree with saved observations; the final-source smoke
has the same six emitted circuit bytes as the independently checked primary R2.

Independent exact-rational arithmetic verifies all 12 summary comparisons.
At primary matched j=1, R2/R3 lose 81810/81642 T. At selected first peaks,
R1 j=1 costs 271982 T while valid j=0 costs 5810 T and succeeds near 2/3.
The equality threshold 271982 is a supplied-cost algebraic threshold populated
with executed component costs; it does not optimize over schedules or include
verification, Clifford or runtime costs. A concrete counterexample to that
optimization inference is independently executed H at j=0: **zero T and 3/8
proper success**. Thus no general achieved break-even follows. The candidate
correctly leaves `achieved_break_even` null. Its comparison helper is arithmetic
over records, not an independent service/provenance certification mechanism;
this review authenticates the actual explicit records only.

The original nonunitary `(1+1e-6)I` counterexample rejects in all three component
roles at j=0,1,2: nine rejections, including unused components. Deliberate
phase, scratch and asymmetric-mapping faults reject independently. The three
saved SK failures reproduce from their original angle and allocated precision:
R1 needs 4.76190436e-6 at pi/8 but degree-five bound is 2.02770420e-5;
R2/R3 need approximately 3.703703e-6 at 1.9106332362490184 but achieve only
1.11656549e-5. Trials remain saved, with no full-search circuit/metrics or
analytic fallback. These are bounded synthesis failures, not quota pauses or
failed mathematical derivations.

## Reproducibility, limitations and next action

Fresh review evidence: `dump/1031195126-graph-ft-independent-review/`.
The two distinctive committed probe/supervisor files under `tools/` provide
reproduction; `commands.jsonl` records exact commands, exit codes, time and
wait4 high-water RSS. `budget.json` was written before numerical allocations.
Probe commit: `cba402a235d4502ada700078e5db9314f00a935b`.
Final identities, receipts, task/session, validation totals and commit linkage
are recorded in `review-checkpoint.json` and the final inventory.

Candidate regression: **246 passed, one deselected** in 18.03 pytest seconds
(18.395318 supervisor seconds). The sole deselection is the new local S0
five-wire dense case, to retain this review's declared dense-four limit;
it is not a failed case. All 24 original pilot and 187 rotation tests ran.
Selected reviewer Black/Ruff and whitespace checks pass. Supervised checks,
including all three failed probes and formatting/lint, total **132.195258s**;
maximum child wait4 RSS is **331,382,784 bytes**, longest child **25.265898s**.
The final scalar inventory has its separate self timing/RSS receipt. No full
repository suite, build, notebook, historical replay or broader scientific
coverage is claimed.

All numerical children use `/Users/mar/codex-work/logique/.venv/bin/python`,
explicit candidate PYTHONPATH and asserted imports; all listed numerical and
compiler thread settings are one. Independent budget is <=300 seconds total,
<=120 per child, declared process <=6 GiB and arrays <=64 MiB. Actual dense
matrices are <=4 qubits; actual oracle statevectors <=13, below authorized18.
RSS is per-child wait4 high-water, possibly including reaped descendants;
aggregate/group RSS and hard OS enforcement are unavailable and not claimed.

The three reviewer probe failures are retained: omitted SX/SXdg in the probe's
allowed Clifford set; wrong QuantumCircuit.unitary keyword; and comparison of
an algebraic zero-error Clifford with floating expanded-U arithmetic. These
were corrected only in reviewer code. Missing guessed historical paths and
truncated reads were followed by actual paths/focused reads. Candidate files,
README, pins, archives, failed/partial outputs, queue/history and other workers
were not changed. No model/subagent, paid/API, build/install/sync, hardware,
physical-QEC or excluded research ran. No worker push occurred.
Initial Git staging was sandbox-denied on the parent repository's worktree
index.lock; scoped automatic escalation succeeded. There was no automatic
approval-review rejection. Read-only inspection and Git command receipts are
in the tool transcript, with the Git failure also retained in the checkpoint;
these commands did not have independent RSS instrumentation.

Next: `graph-ft-integrate-1030020413` may integrate only the two exact admitted
correctness files after its own hash/overlap checks and validation, preserving
this independent decision and the separately recorded evidence scope. Keep
1e-4/j=1 unsupported under current options. A future stronger-SK attempt must
first preflight operation/state-work/time/memory bounds; otherwise retain the
failure. Broader graph/method/MCX coverage and an actual success-cost objective
including verification require new evidence and review. No prerequisite for
this bounded review remains open; the full paper remains unfinished.
