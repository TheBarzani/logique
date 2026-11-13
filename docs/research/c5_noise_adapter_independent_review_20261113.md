# Independent C5 best-fit noise-adapter review

Task `c5-noise-adapter-review-1101052342`, 13 November 2026. Assigned base
`de230cce74089344343fcdf1c12d553cc4cf8607`; candidate correctness
`ad6c4630df0844615d62ef4742648cf466b88d2a`, final candidate
`55be27b9882c3d7754e0448217da12edf72ba987`.

**Bounded independent review COMPLETE. BLOCK the offered cumulative adapter
source chain: unchanged physical calibration is rejected across processes.
No new adapter source paths or noisy measurements are ADMITTED.**
The previously admitted component-lowering dependencies and ten ideal C5 rows
retain their restrictive admissions. No candidate repair, integration, scientific
sampling, native build or push occurred.

Fresh checkpoint: `dump/1113012557-c5-noise-adapter-independent-review/checkpoint.json`
in this review worktree. Unique probe:
`tools/probe_c5_noise_adapter_review_1101052342.py`.

## Blocking finding: physical channel identity depends on record-list order

`c5_noise_adapter.validate_calibration` removes top-level error UUIDs and
normalizes tuple/list JSON representation, then compares the complete `errors`
lists in their original order. Aer emits the local errors in dictionary iteration
order; this serialization does not give a stable cross-process record order.
The order of separate local error records is different from the ordered qargs,
instructions and probabilities **inside** each channel, which must be preserved.

The candidate's retained final real calibration smoke succeeds within its
creating process. A fresh reviewer process using the same installed backend
and the candidate's saved `calibration-smoke-final/noise.json` instead raises
`ValueError: C5 physical noise channels differ from backend calibration`.
The backend property/configuration bytes pass their preceding exact checks.
Two subsequent independently generated snapshots reproduce the mismatch.

Both regenerated snapshots and the saved snapshot contain **965 error records**.
Indexing them by `(type, operations, ordered gate_qubits)` gives 965 unique keys
and **exact equality of every remaining payload field**, after removing only
UUIDs. Raw key order differs in both comparisons. No tolerance, channel-matrix
approximation, qarg reversal or omitted probability is needed to demonstrate
the false rejection. The first diagnostic begins with saved `reset` versus fresh
`cz` records, rather than a changed calibration at a common physical key.
`calibration-keyed-audit.json` and both complete regenerated payloads preserve
this evidence. Installed Aer `noise_model.py::to_dict` was inspected directly:
it appends `_local_quantum_errors.items()` to an error list.

This is a **fail-closed execution blocker**, not evidence that incorrect noise
has been sampled. `_execute_seed` shares `output.parent/backend` across the
distinct request children and calls this guard before routing. Consequently a
later child can reject the identical backend snapshot for serialization order
alone. Passing component tests and the same-process smoke cannot admit this
whole execution chain. No shots are licensed by this review.

Required repair: canonicalize or index only independent top-level local error
records, with explicit unique operation/ordered-qarg identities and rejection
of duplicate or unsupported records. Preserve internal instruction order,
matrix shape/scalars, ordered qargs, probabilities, readout payload and raw
snapshot hashes. Add deterministic shuffled-record and separate-process snapshot
regressions, retaining rejection of changed probabilities, matrices, calibration
files and reversed qargs. Obtain a new exact cumulative-source independent review
before integration or the separately assigned execution. Do not weaken or remove
the calibration check, fix only a test, or rewrite this failed evidence.

## Exact source, build and metric decisions

The complete adapter, modified 1,216-line noisy caller, check tool, configuration,
new tests and imported component-lowering source were inspected, including
selectors, QPY signatures, compaction, restoration, durable pre-Aer metadata,
supervision, finalization and historical request reconciliation. Ten actual
module imports were asserted into the candidate checkout, never this older
review base. Five inherited whole files equal integration `cf678f72` and current
root; the five relevant QPY helper definitions also equal current root.
The newer unrelated root profile/native implementation is not transplanted or
admitted by this review.

| Decision | Exact paths / boundary |
| --- | --- |
| **BLOCK new cumulative source** | Five new/modified adapter paths below at `ad6c463`; whole noisy caller cannot enter C5 execution through this decision. Newly admitted path set is empty. |
| **Retain previous admission only** | Five unchanged inherited paths below, from review `a689221`, integration `cf678f72`. No new blanket MCX, FT, ideal-harness or supervisor admission. |
| Build/native | No new build offered or admitted. Prescribed unchanged binary SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a` verified and explicitly selected, never invoked. |
| Metrics/scientific evidence | Zero new noisy observations, shots, routed study costs or scientific sweep rows. The source checks below are finite diagnostics, not performance measurements or a formal error guarantee. |
| Worker handoff | `55be27b` is an implementation report, not source admission. Its cross-process calibration reuse claim is restricted by this failure. |

Exact offered source SHA256s, checked against working files and committed blobs:

| New/modified path — WITHHELD | SHA256 |
| --- | --- |
| `src/logique/benchmarks/c5_noise_adapter.py` | `51fae4ce56ced393ffe716c9d47cf8aed50d9822c5b49b21a45d851c5ace38d0` |
| `src/logique/benchmarks/noisy_iterations.py` | `b442146d972b22a4680e123f3247d21be1aa7d6f10a85aaa7118826792cf27df` |
| `tools/check_c5_noise_adapter.py` | `b6726a55993f4b8d98a8b1bf2141a81ae06c87991de2f70742bdaf21c397041c` |
| `tests/test_c5_noise_adapter.py` | `aa1e5966d7a10d744c6989abc55eaa910ae82a9a01fafa7a7221148c9e9454e1` |
| `configs/c5_best_fit_noise_adapter.json` | `2cea9cd979cd2e37824128e055a8df5ecc9643edd7df64a1f5df38d025a85d63` |

| Unchanged inherited path — prior admission retained | SHA256 |
| --- | --- |
| `src/logique/benchmarks/metrics.py` | `6ff3ef194a8cb3fec5e3adb2869daa939687d2c351780c14725fde5c029e84b9` |
| `src/logique/benchmarks/costs.py` | `8529ad29d6457ed784c700ae26a7579b72bc0221857eb575a884ee4dc6c7a7b0` |
| `src/logique/benchmarks/routing.py` | `b35f6eaaeba466f3393f0a42c39f15c74f26fb2539056eec68ea9add6730db8d` |
| `src/logique/benchmarks/iteration_study.py` | `c941aef068bb848174652644530d9f3fafc8e4e55c872f34b619753f76bd22c5` |
| `tests/test_component_lowering.py` | `9a37625010cb4c4df6d1cfb40efc0b54d728d34fa6826f135a292742843a898a` |

## What the bounded semantic checks establish

All **86** worker checkpoint inventory entries, **50** frozen best-fit evidence
entries and **15** structure-pilot entries match. The source manifest remains
`fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4`;
shared best-fit oracle hash remains
`8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268`.
The loader uses these saved components, with no structure reconstruction,
domain-check deletion or fresh lowering. Both regimes keep 10 data wires plus
one initially clean output; the oracle has 84,441 U/CX instructions.

Independent enumeration finds 30 proper words among 1,024 binary words,
243 valid-code words and 781 unused-code words. The new probe implements U
matrices and CX permutations directly, including global phase, on a seeded
complex clean-output vector with nonzero support across all input words.
It does not call the worker checker or Qiskit evolution for the oracle result.
Preparation/reflection checks use Qiskit evolution but independent analytic
expectations and distinct input buffers, including both output sectors.

| Check, complex128 seed20261113 | Measured residual / result |
| --- | --- |
| Saved oracle, no fitted phase | maximum signed amplitude error `8.960262534991317e-14` |
| Oracle dirty-output probability | `1.6977312417420117e-28` |
| Actual A followed by saved emitted inverse | R1 `2.3274e-17`, R2 `4.0461e-17` maximum signed error |
| Reflection versus `2*s*vdot(s,a)-a` | R1 `1.0729e-15`, R2 `8.8957e-16` |
| Complex-phase/unequal-damping two-wire channel | independent Kronecker-sum SuperOp residual `0`; physical `[7,2]` attaches to compact `[1,0]` |
| Asymmetric readout | exact matrix retained on mapped physical wire; omitted-wire correlated channel omitted whole |

These are finite numerical observations below the declared `1e-10` comparison
tolerance, not exhaustive floating operator proofs. The ten ideal sweep rows
were reused by hash; no scientific sweep was repeated.

A separate two-data-wire, one-output synthetic fixture exercises the real
selector, measured QPY readback, nontrivial five-wire layout and pre-sampling
persistence. Two noncommuting preceding steps are present for selected j2;
only one routing call occurs, and no j0/j1 output is created. Expected success
comes from independent 2x2 matrix multiplication. Full routed-state residual is
`3.3343e-16`, marginal residual `5.5512e-16`, restored workspace probability1.
The sampler is replaced by an explicit KeyboardInterrupt: validation remains
durable, the row becomes interrupted, and **no counts exist**. This fixture
deliberately isolates the loop from the independently observed calibration
failure; it cannot override that failure or establish actual C5 route feasibility.

Distinct identities encode source kind, frozen manifest hash, regime, seed and
iteration. The 50 unlaunched requests are `(6 R1 + 4 R2)*5 seeds`; all have null
counts and unique identities. Original 805-ledger identity and 50 structure
exclusions remain unchanged. The original runner rejects the best-fit config.
The preflight rejects widths19, timeouts121s and budgets above6GiB, and guards
routed active width before exponential state allocation/Aer. For 11/18 wires,
its eight-vector-plus128MiB estimate is 128.25/160MiB; that estimate does not
bound Python, calibration, circuit/transpiler or total process memory.
External supervision, cumulative budget and receipt reconciliation remain
mandatory. Direct child execution alone supplies no time enforcement.

## Structure pilot and manuscript scope

The current root pilot report and checkpoint were read and their saved bytes
reused. The 22-wire original j0,1 observations were not rerun. Its exact
977-instruction oracle `226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`
still needs the separately assigned absolute-phase/restoration lowering proof
on its reachable clean subspace. **PENDING** remains the decision here; no
general22-wire authorization, rejection or admission follows from best-fit tests.

The best-fit ideal domain advantage and overshoot losses retain their prior
admission. Neither ideal success nor11-wire width establishes noisy performance,
gate-cost advantage or resilience. The current 404 admitted family request
records remain separate from these 50 new requests; this review neither recounts
nor enlarges that scientific admission. No FT, full-family or manuscript result
is admitted, and there are no new confidence intervals.

## Resources, retained failures and handoff

Before arrays, budget declared120s per child,300s cumulative,2GiB/process,
serial children and all compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1.
Maximum new vectors11 wires, dense test Operators5, local channels2 wires;
original staticFT dense4 unchanged. Existing absolute root venv only, explicit
candidate PYTHONPATH and verified imports; no sync. Terminal Darwin wait4 RSS
is not an OS hard cap or simultaneous process-group peak; live/group RSS is null.

| Fresh child | Exit / outcome | Seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Identity/signed/channel probe |0, pass|4.568188|189415424|
| Real calibration guard |1, genuine source blocker|7.563520|466731008|
| Candidate selected regressions |0,70 passed/7 deselected|5.449140|152764416|
| Calibration diagnostic + initial toy |1, reviewer mock lacked backend.target|15.740650|614547456|
| Diagnostic + corrected toy |0, blocker retained and toy passes|15.555371|632176640|

Cumulative receipted children:48.876869s, maximum632,176,640bytes (~602.89MiB).
Two existing Aer warnings and one denied pytest-cache write are retained;
candidate tracked status remains clean. Seven supervisor/forced-kill tests are
deliberately excluded; no new supervisor certification is inferred. Probe
Black/Ruff pass. These checks are not a full-suite, notebook or historical replay.
The worker's original UUID failure, this cross-process failure, both complete
diagnostic snapshots and failed reviewer fixture remain preserved. Formatting
did not change numerical operations; pre-format probe copies are retained.
Read-only inspection commands/static checks have transcript exit/time records,
but no separately measured RSS. Absent guessed paths/truncated combined reads
were resolved by focused actual reads. No candidate source was modified.

**Next action:** coordinator records this exact BLOCK and assigns the narrow
calibration-record canonicalization plus independent review. After exact source
admission/integration, the existing distinct best-fit execution owner must use
fresh outputs, serial supervised children<=120s, cumulative<=900s, declared
memory<=6GiB, retained active-width exclusions and honest no-count timeouts.
Actual routing/sampling feasibility requires new bounded evidence and separate
review. No blind old-request replay or treating queue completion as admission.
Only this review and its unique probe are committed on the assigned branch;
README, pins, binaries, archives, histories and all old evidence remain intact.
Dispatcher alone launches successors and pushes integration HEAD.
