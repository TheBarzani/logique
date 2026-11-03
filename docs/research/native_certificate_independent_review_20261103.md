# Independent whole native certificate review — 3 November 2026

Task `native-certificate-review-1101052342`, session
`01a1a005-65d5-7de3-99b7-6bba0cf0f176`, assigned branch
`codex/coloring-native-certificate-review-1101052342`, base
`de230cce74089344343fcdf1c12d553cc4cf8607`.
Evidence RUN: `dump/1103010935-native-certificate-independent-review/`.

**Whole composed chain: BLOCK production integration. Review task COMPLETE.**
The exact offered HEAD is `b4bce3c2ee8ae45f2a4c7aaeb9946afdcff1841c`, comprising
correctness `d126bbd1d883cde2b332e64586aa8631287d1192` and separate build/report
commit `b4bce3c`. **Admitted paths/commits from this offer: none.** The coordinator
must not extract the C++ validator, protocol hunks or build changes as partially
admitted components. Prior admissions retain their original scope; they do not
admit this composition. No new performance, T-count, larger-domain or manuscript
claim is admitted. The full research evidence gate remains open/blocked.

## Reproducible remaining blocker

The old missing-certificate/seven-input failure is closed. However the promised
strict integer protocol still accepts malformed serialized leaf indices.
Starting from the exact saved valid six-input equal-cone response:

```python
response["steps"][0]["leaves"][0] = True  # repeat independently with 1.0
response["xag_schedule_audit"]["actions"][0]["leaves"][0] = True
```

The second experiment substitutes `1.0` in both locations. `explicit_leaves`
remains `[1, 2, 3]`; all physical gates, certificate tables and other fields are
unchanged. Actual candidate `api.synthesize(..., strategy="xag_low_t")` accepts
**both responses and calls `records_to_qiskit` once**, constructing a seven-wire
circuit. Only subprocess output is replaced; actual `run_native`, certificate
validation, construction and public return path execute. `nested-audit.json`
and both exact mutated JSON responses preserve the result. Response hashes:

| Mutation | SHA256 |
| --- | --- |
| Boolean serialized leaf | `efed83952e7451faeab093b6235ba6e2411d7c47d70e9a0ff255b5f8c245c662` |
| Floating serialized leaf | `7031108b63f6cd0212655e45c68b778144afbc54cdf8c58e7ddd3b4e4fca5db8` |

Cause: `native.py:314–315` validates `explicit_leaves` with strict `node_id`,
then compares the separate `step["leaves"]` using ordinary Python equality.
`True == 1 == 1.0`, so both malformed lists compare equal. The JSON comparison
between step and audit action at lines278–282 does not help when both contain
the same malformed type. The action payload is therefore not a valid typed
serialization of the native schedule despite passing this handshake.

**Severity and scientific distinction:** this is a narrow protocol acceptance
defect, not an accepted wrong Boolean output or a counterexample to theorem
92784ef. The modified field is redundant, and the emitted circuit remains the
same. It nevertheless violates this correction's explicit requirement and
public documentation that Boolean/float integer substitutes reject before
construction. The whole-chain gate concerns that promised boundary as well as
gate correctness. This finding supplies no evidence against existing SAT or
previously admitted ideal observations and does not change manuscript metrics.

## Entire source and mathematical chain inspected

I read the required repository instructions, full plan (including current-root
additions/deadline), full29October/30October handoffs, current1November successor,
actual worker checkpoints, old alias/blocker reviews, exact theorem92784ef,
capped-value review3383bea and integration BLOCK, and SAT review475eff6 and
integration5ec2127. The new queue's deadline is9November00:00EST and its128
additional-batch limit is unchanged. No old session or queue was restarted.

The review inspected complete current native/API, mapping, controls, capped
validator, action serializer, input selection/serialization/recording, ordinary
SAT emitter and CMake source, relevant tests and public protocol documentation.
It traced the pinned sequential strategy and effective LHRS visitor, allocator,
output preparation and XOR/AND gate emission, plus the pinned bsat solver.
The entire deliberately imported dependency from35618f4 was compared to exact
Git blobs; it was not treated as admitted merely because its headers matched.

The restricted correctness argument remains sound in the inspected code:

- `Domain` checks canonical consecutive PIs, cleaned reachable binary gates in
  stored topological order, nonconstant distinct earlier fanins, uncomplemented
  XOR edges and explicit AND/output polarities. It checks inputs<=6,
  nodes<=256 and outputs<=256 before validator graph containers. Predicted
  width<=256 and steps<=4096 are checked before Boolean tables. Parsing,
  selection, cleanup and optional refactoring happen earlier and have no
  general hard memory guarantee from these caps.
- The smaller-first inclusion rewrite, singleton case, equal-frontier buffer,
  incomparable-cone targets and reverse restoration match the pinned schedule.
  Boundary nodes carry values; internal aliases do not persist as Boolean
  operands. `Machine.read` checks actual values, while the skipped in-place
  target is resolved as an address. Frames verify saved target restoration;
  active boundary addresses/values and all other wires' zero values are checked.
  Ordinary uncompute verifies zero before release/reuse. A live stack generation
  alone never establishes value correctness.
- C++ compares independently reconstructed steps, actions, stacks, exact gates,
  width and I/O to actual audit and LHRS emission. The physical recorder rejects
  target aliases before normalizing equal literals or opposite polarities.
  The expected/audited/actual comparisons close the original duplicate-control
  issue without giving invalid gates a unitary meaning.
- Release/NDEBUG is essential for empty XOR frontiers. Their reverse compute
  can allocate another zero wire; it is not a free/uncompute operation. Debug
  explicitly rejects that unsupported case. No Debug admission is given.
- Before output preparation, active input/output-driver values and clean other
  workspace are checked. A first complemented PI output may flip the raw PI;
  later copies correct relative polarity. The actual emitted inverse in
  compute/copy/inverse and compute/Z/inverse restores every computation wire.
  Static X/CNOT/Toffoli permutations have phase+1; selected Z supplies the sign.
  Clean computation scratch is required; dirty initial scratch is excluded.

The theorem is byte-identical to
`92784ef5bb906aca0d7eda178ea1c15601298bee:NATIVE_VALUE_INVARIANT_REVIEW.md`.
Its original nodes7/9 stale-alias evidence remains untouched. The saved newer
equal-cone response independently retains nodes8/10 on restored PI wire0:
node truth mask `0x9696969696969696`, PI mask `0xaaaaaaaaaaaaaaaa`. At assignment2,
the node is1 and the physical PI is0. These aliases are stale but unread; imposing
an always-correct-stack invariant would reject a valid schedule.

SAT remains a distinct induction: ordinary compute obtains zero distinct storage,
checks current fanins and the result; ordinary uncompute checks its target/fanins,
then zero before release and marks the node absent. Final non-output cleanup is
checked. Unsupported leaves/cells/buffers/in-place/level actions reject. Its
inputs6/gates32/nodes64/outputs16/raw-width64/horizons128/conflicts100000/search30s
caps remain unchanged. Python's `sat_time_seconds+1` process timeout still wraps
the solver, whose native timeout parameter is ignored. Direct callers need an
external deadline; exhaustion is not global infeasibility or optimality proof.
The composed branch retains this actual current SAT source and dispatch; it
does not extend the two-cone theorem to SAT schedules.

## Build and evidence, separate from admission

The independent audit matches all17 offered path hashes to HEAD and the working
tree, re-resolves compiler depfiles and matches all **1,152 effective dependency
files**, hashes compiled executables/probes/cache/commands/provenance, verifies
the inherited exact imports and five unchanged dependency pins. `identities.json`
records the complete targeted inventory. The build is Release `-O3 -DNDEBUG`,
C++17, AppleClang21, using the pinned Caterpillar and existing overlays.
No new build is claimed by this reviewer and no existing binary was overwritten.

| Build artifact | SHA256 |
| --- | --- |
| Offered private executable | `d61e8f53b6e7fd9085bcc33fa5110184c41d3be7f6571a104d7b7b3ad9708278` |
| Effective LHRS overlay | `edd39ec5371dc33f985d6cf1ea0c3c0dd5c394da1cc69604afe92e23f3cbe7b9` |
| Pinned sequential XAG strategy | `6980dd085d51a2752a922914d5f7b9a07d0b8c9bff1e490f744d3e7852c89127` |
| Prescribed unchanged-experiment binary, hash-only | `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a` |
| Prior capped private binary, hash-only | `8941c1dcfbede0e570ac02d252f5d0de845e8068df65778c3e8d9b18327e0fc0` |

Fresh checks use only the offered composed private binary. The old default and
prior binaries remain untouched. Historical missing first-failed SAT/value build
bytes remain an acknowledged preservation limitation; this audit does not
reconstruct them or claim complete historical build preservation.

The unique reviewer probe independently evaluates returned graphs and generated
source programs, interprets physical gate records as integer permutations, and
interprets actual Qiskit wrapper instructions directly. It does not call worker
checkers, `_qiskit_records`, Boolean verification helpers or quantum simulators.
Exact scalar checks have no floating tolerance or sampling confidence interval.

| Fresh check | Observed result |
| --- | --- |
| Saved old/valid public boundary plus15 independent negative cases | All15 expected rejections occur before construction; valid response constructs7 wires |
| New nested typed-field adversaries | **2/2 malformed responses accepted; circuit construction reached** |
| Saved response reuse | 79 hash-matched responses; raw output/inverse/clean-other-wire scalar checks;24,640 actual wrapper columns for cases with<=4 outputs/width<=32 |
| Independent generated sources | Six seeded eight-operation programs, four declared inputs including unused, three outputs, two policies, sequential XAG and ordinary SAT XAG/AIG:36 responses,6,336 wrapper columns |
| Compiled probes | All3 exit0: action normalization/serialization, value/domain/emission, SAT guards; value probe retains1,024 frontier pairs/1,369 variants and nine state/cap, eight domain, six emission rejections |
| Focused candidate regressions | 718 passed, no skips/deselections; guarded tiny coherent test variants remain<=5 wires |
| Review tool Black/Ruff | Pass; formatted source AST matches the executed source snapshot |

The fresh source denominator is $6\times3\times2=36$ responses and
$36\times16\times(2^3+3)=6,336$ wrapper columns: every four-input assignment,
eight joint XOR targets, and three selected phase outputs. Seed1101052342 is
recorded with exact sources/requests/responses/hashes. These are bounded
correctness checks, not a graph-family performance experiment or general
preprocessing CEC. Width256 saved coverage is scalar, not a256-wire simulation.

## Limits, failures and next action

Before probes RUN/budget.json declared120s outer children,10s direct native
children,300s cumulative and2GiB process allocation, serial compiler/BLAS/OMP/
Accelerate/Rayon/Qiskit parallelism1. All execution used the existing absolute
root venv Python and asserted candidate native/API/path imports. The independent
probe allocates no simulator arrays; focused existing regressions use small
Boolean tables and guarded<=5-wire coherent checks. Original staticFT dense4
and all other limits are unchanged. Per-command wait4 high-water, time and
exit receipts are saved; this is not a simultaneous process-group peak or hard
memory cap. No compile, noisy sampling, C5, wider scientific replay or full-suite
claim is made.

Two initial fresh fixture encodings failed the pinned structural-Verilog parser:
first compact source, then multiline source still lacking token separators.
Both exact inputs, requests, stderr/stdout, exit1 receipts and probe versions
remain. A third new subdirectory with conventional separators passes all36.
These are reviewer fixture failures, not failed mathematical attempts or accepted
wrong-output native cases. Read-only missing-path/glob/outside-worktree Git
inspection errors and truncated reads were followed by actual/focused reads;
tool events retain their exits. No automatic approval rejection is inferred.

Required correction: strictly validate the duplicate `leaves` list as integer
node IDs (including types, length, uniqueness and equality to `explicit_leaves`),
then inspect equivalent redundant serialized index fields for the same equality
pitfall. Add both retained Boolean/float adversaries through `run_native` and
the real public boundary with a constructor sentinel. Keep the valid/stale-alias
responses and SAT tests, exact C++ source/build/pins, historical failures and
metrics unchanged. A narrow Python/test correction should not require rebuilding
unchanged C++ bytes. Obtain a new exact **whole-chain** independent review before
the coordinator integrates; do not cherry-pick this report as source admission.
The dispatcher/coordinator owns successor scheduling; this review launches none.

Only this uppercase report and the unique bounded probe are task-owned tracked
files. Candidate, root README, pins, histories, archives, prior checkpoints and
all failed/partial artifacts remain unchanged. No integration, push, sync,
models/subagents/Codex subprocesses, API/paid fallback, purchases, hardware,
physicalQEC, precolored or conditional-workspace work occurred. Required narrative
and important blocker sidecar are written atomically at the dispatcher destination.

## Exact reviewed identities — withheld, not admitted

The following complete offered-path inventory is bound to HEAD `b4bce3c`.
It records what was reviewed; **none of these paths is newly admitted**.

| Reviewed path | SHA256 |
| --- | --- |
| `external/native/boolean_synthesis/CMakeLists.txt` | `94ac0f0783cbb9fd86943240297b7f5cbd068393b71a598a1f40c26b370ab301` |
| `external/native/boolean_synthesis/README.md` | `c6a4a1d5dcf091fc329653ace8f32589e9c49d819d053c5f0c50b0e2b1a7f9dd` |
| `external/native/boolean_synthesis/include/mapping.hpp` | `35fc2610f327533824a82fedac84bb2e4990a6ef26ba86855d6550d077b0dd42` |
| `external/native/boolean_synthesis/include/types.hpp` | `8dee3c4a9ce2b230ec4425e0680fd58fd94f6817c087bf3e74aed8356d4f9ed3` |
| `external/native/boolean_synthesis/include/xag_controls.hpp` | `75c15af82adc2ec11e35af684e9e4e93ee6088199edb0498245e7d5c6e56365c` |
| `external/native/boolean_synthesis/include/xag_value_validator.hpp` | `9120bdec631307c5d09ee59770b6300f694eb185f343d1af758265292dd33d3d` |
| `external/native/boolean_synthesis/tests/action_serialization.cpp` | `beb651b1b35f0ee6faa2587068ed9eb9f8fa2f9b1c96d4d50c77fd22e9cfc057` |
| `external/native/boolean_synthesis/tests/value_validator.cpp` | `6ebf4a2250273f69bbbafc7cd404667df9db40f78f9edd52604df92caba3da51` |
| `src/logique/synthesis/native.py` | `3418b47b670e7f2e7a4bd2a4a96d4350a5af7ccec8cfbeb80035b180ba674e54` |
| `src/logique/synthesis/api.py` | `f2a8cbc8d6f2164c15cc90aa7854a2bb17361f304002500ac1284ce6722c9e46` |
| `tests/test_native_xag_lowt.py` | `c3ad41db6275e4812955a496523bef70899250dc3d876a5ebd360ec6854acd7f` |
| `tests/test_native_value_validator.py` | `30be70dab678fd2a7d2fc3908c0a2f41e214f983141fcd682ac4101f5b7f55ea` |
| `tests/test_native_value_certificate.py` | `99922e7c8937439c68610bf58b624ffabd711cfb3e8ab4c0b49fde1ae0d5b01e` |
| `tests/fixtures/native_value_certificate/old-seven-input.json` | `25b1968a5cf5043cff8a9fc9a827770402938cf25871068104f6bb5e69fbab48` |
| `tests/fixtures/native_value_certificate/valid-equal-cones.json` | `6f6ed77d607a6d9b084405bb9676134dede125cfe787d8ebb85ee6ecaa18861b` |
| `tests/fixtures/native_value_certificate/provenance.json` | `e525c231be9930d9e0ea4b12c1179ffaa940febd046ed6eb160dd399cab54e11` |
| `docs/research/native_certificate_composition_20261103.md` | `3c19d56b88494e80008a2d3dffd826dfb3b8c9c9cd0b5540e1564801e9422845` |

Total supervised child time (including both failed parser fixtures): **13.796986s**. Maximum observed child high-water: **93,126,656 bytes**. No hard memory cap is claimed.
