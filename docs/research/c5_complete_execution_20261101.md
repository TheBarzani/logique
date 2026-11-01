# Complete-predicate C5 best-fit execution — 1 November 2026

Assigned task `c5-complete-execute-1030020413` is **COMPLETE**.
Implementation and ten ideal iteration rows are ready for independent review;
**scientific admission remains pending**. This is no noise, baseline-superiority,
fault-tolerant, manuscript or full Task7 admission. The separate structure22
pilot still needs its own exact-source/evidence review. Original structure22
exclusions remain true for the exact old 18-wire run.

Branch: `codex/coloring-c5-complete-execute-1030020413`.
Base: `e90adf3373236ef51a937480febd3cd7d669dce7`.
Source correctness commits, in order: `dd6432d`, `df4a232`, `ab31ae7`.
Only `tools/check_c5_complete.py` and `tests/test_c5_complete.py` enter those
commits. This checkpoint is a separate research-evidence commit. No maintained
library, noise harness, README, dependency or historical source was changed.
Session: `01a1957c-cdd5-7f61-afc6-914968f9ac75`; commands and source inventories
are in the local provenance.

## Scientific result

The actual native allocation is **11 wires**: ordered data wires0–9, output10,
no other allocated workspace. Width was inspected from the native response
before LUT expansion, preparation, truth arrays or statevectors. It was not
assumed from the earlier allocation audit. Complete unused-code checks remain
present under both preparations. All quantum vectors use at most11 wires;
there are no dense Operators or density matrices.

C5 has $M=(3-1)^5-(3-1)=30$ proper three-colorings. Separate integer-word
enumeration finds243 valid codes,781 unused-code words and213 valid-code edge
violations among1024 binary words. R1 uses $N=1024$; R2 uses $N=243$.
The analytical exact-count first-lobe ledger selects peak4 for R1 and peak2
for R2. Every requested row through peak+1 was actually executed from saved,
read-back QPY components at complex128 precision with tolerance1e-10.

| Regime | j | Measured proper-coloring probability | Measured unused-code probability |
| --- | ---: | ---: | ---: |
| R1 | 0 | 0.029296875000000 | 0.762695312500000 |
| R1 | 1 | 0.243474841117736 | 0.594412624835681 |
| R1 | 2 | 0.574376138501423 | 0.334418748319526 |
| R1 | 3 | 0.871435021789861 | 0.101015340021105 |
| R1 | 4 | 0.999484622396888 | 0.000404939543798 |
| R1 | 5 | 0.900260183698787 | 0.078366998520575 |
| R2 | 0 | 0.123456790123457 | 7.29e-32 |
| R2 | 1 | 0.775420037219248 | 5.31e-28 |
| R2 | 2 | 0.950509084830911 | 7.47e-28 |
| R2 | 3 | 0.345567160992726 | 1.82e-27 |

The overshoot losses are retained. Fewer iterations in R2 do not imply a gate
cost advantage or a higher peak probability: its first peak is lower than R1's.
R1 unused-code population is expected on its binary support, rather than a
restoration failure; independent rational reflection predicts its value at
every row. R2 stays within valid codes to numerical precision. No shots were
taken, so binomial confidence intervals are inapplicable.

Exhaustive monomial tracking checks raw compiled outputs, exported gates,
source/mapped networks, phase and restoration on all1024 inputs, including all30
positive witnesses and both negative classes. Saved-QPY basis probes separately
check positive word70 (colors2,1,0,1,0), invalid word3 and edge-violation word0.
Seed37 generates a complex probe supported on all1024 input words. It checks
the absolute oracle phase, full clean workspace, matching signed reflection
and actual preparation/inverse without fitted phase alignment.

The emitted preparation A is constructed once; A dagger is the inverse of
those exact U/CX gates, and diffusion uses that emitted A. Both are saved.
Maximum coherent oracle residual is9.49e-14; reflection residual is1.14e-15;
actual-inverse residuals are3.88e-17 (R1) and5.97e-17 (R2).
Across all ten iteration rows the maximum signed residual is8.96e-13, total
norm/restoration error2.30e-12, and dirty-workspace probability2.88e-26.
These are bounded numerical observations, not formal floating-error bounds.

The final reconciliation independently updates each of1024 rational word
coefficients by marking and reflection about their support mean. It agrees
with all saved actual statevectors and their predictions, independently of
the experiment's two-class recurrence. This is worker validation, not an
independent scientific review or a second simulator engine.

## Exact evidence and resources

Validation/checkpoint directory: `dump/1101010451-c5-complete-checkpoint/`.
Final experiment: **`dump/1101010944-c5-complete-best-fit/`**.
Its `manifest.json` binds the exact native request/response/stderr/exit, Verilog,
profile, preflight, versions, source hashes, QPY, coherent probes, all ten
statevectors, row JSON and per-child receipts. `summary.json` in the checkpoint
binds the final manifest, source/test hashes, native source hashes and all
observed receipts. `final_validation.py` and its receipt document reconciliation.
Post-commit identities and final evidence hashes are in `final-receipt.json`.

Native binary is the explicitly prescribed private native-contract build,
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
The root default binary was not used. Native request is best_fit, cuts16/4,
unbalanced complete encoder and legacy default refactoring. Its emitted profile
confirmation and build declaration are preserved. CMakeCache points to the
private bridge source directory; its main, headers and CMake hashes are in
`summary.json`. These identify current source and the preserved build record;
no new build or stronger historical source/binary attestation is claimed.
Dependency gitlinks and every reused Python source hash are recorded.

Shared final oracle QPY SHA256:
`8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268`.
It has84,441 U/CX instructions; raw computation has42,220. R1 preparation and
inverse each have10 instructions, R2 each20; diffusion has1,175 and1,195,
respectively. This low-width candidate has substantial gate cost. There is no
matched baseline/routing/FT resource comparison in this task.

Final R1 child:32.755999s, wait4 high-water395,902,976bytes.
Final R2 child:27.242162s, high-water405,602,304bytes.
Compile is a separate serial child. Every child has<=120s; all attempts, failed
tests, diagnostics, static checks and reconciliation together use<160s recorded
child wall time, within the900s cumulative envelope. Declared memory budget is
6GiB/process; observed maximum is405,602,304bytes. Direct-child RSS is sampled
with termination on observed excess; it is not an OS hard cap or aggregate
process-group bound. wait4 high water may include reaped descendants. All
compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism is1; no build ran.
Seed37 is a probe/transpiler identity; statevectors involve no stochastic shots.

Existing research Python is used without sync/install, with explicit candidate
PYTHONPATH and asserted imports. Final focused suite: **205 passed**, no skips
or deselections; selected Ruff and Black checks pass. No broad suite, offline
notebook, historical replay, noise or hardware validation is claimed.

## Preserved failures and decisions

- `dump/1101010510-c5-complete-best-fit/`: initial candidate failed the coherent
  check after passing selected basis probes. Diagnostic receipts preserve the
  approximately0.07604 amplitude discrepancy and0.48484 dirty-workspace
  probability. Default zero-initialized transpilation was an invalid assumption
  for a reusable oracle called on superposed data. Source correctiondf4a232
  explicitly uses `qubits_initially_zero=False` and one transpiler process.
  This is a local harness correction, not a native bridge or predicate repair.
  A separately saved basis-word8 probe confirms the failed oracle puts nearly
  unit probability in dirty workspace; corrected lowering restores word8 with
  residual8.34e-13. `failure-isolation.json` preserves this counterexample.
- `dump/1101010727-c5-complete-best-fit/`: R1 completed; R2 stopped at the inverse
  probe. Its0.151858 residual came from an aliased NumPy input buffer used as a
  comparison reference. The tiny regression similarly failed at0.549856 before
  explicit copies. Final probes copy source buffers before evolution; emitted
  A/inverse round-trip and saved-state checks pass. No tolerance was relaxed.
  Rechecking the old saved R2 A/inverse with copied inputs gives1.60e-16,
  confirming that its failed diagnostic did not establish an inverse defect.
- Development `tests3.log`/receipt retain that failed buffer-alias regression
  (204 passed/1 failed). Earlier202/204 passing runs, all diagnostics and all
  partial QPY/artifacts remain immutable. Final205 tests include the corrected
  two-qubit QPY round-trip, spectator MCX, mapping and preallocation regressions.
- Initial Git stage/commit was sandbox-denied on the assigned worktree's shared
  index lock; scoped automatic escalation succeeded. There was no automatic
  approval-review rejection. Inspection failures included two absent guessed
  source/admission paths; actual maintained sources/reviews were then located.

The current integration report `docs/research/c5_22_qubit_pilot_20261031.md` and
its `dump/1031221547-c5-22-qubit-resource-pilot/checkpoint.json` were read.
All linked pilot evidence hashes match. Its ed781140 source/config and0da04596
handoff, four j=0,1 observations and remaining unexecuted rows are separate
evidence awaiting independent review; no structure numerical run was repeated.
The old34-case/151-row admission and the old structure22 exclusion are unchanged.

README, lockfile and submodule declarations match intake. No histories, archives,
failed/partial evidence, pins, binary, queue, root integration source or noise
harness was changed. No delegation, Codex subprocess, API, paid fallback,
purchase, hardware, physicalQEC, precolored or conditional-workspace work occurred.

## Next action

`c5-complete-review-1030020413` must inspect the exact final source/test bytes,
all three correctness commits, final native/profile provenance, QPY/scalar
phases, signed states, independent count/reflection and failed-attempt diagnosis.
Separately review the saved structure22 pilot's exact source/QPY/evidence or
record precise pending review. No queue outcome is scientific admission.
Only the root coordinator integrates exact independently admitted bytes on
`coloring-paper-revamp-codex`; the dispatcher alone pushes integration HEAD.
The full paper and remaining noisy/routed/matched-cost work remain open.
