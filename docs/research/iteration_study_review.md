# Independent executed-iteration review — 28 October 2026

**ADMIT the exact bounded ideal-only implementation and final pilot identified
below.** This assigned review is COMPLETE. This is a scientific decision for
34 completed graph/regime cases and 151 executed rows, not completion of Task7
or the paper. C5 k3 R1/R2 remain explicitly infeasible under the present cap.
No counterexample was found within this contract; no candidate repair is needed
before integration of this bounded slice.

Task: `iteration-review-1028004102`; session ID not supplied. Reviewer worktree:
`/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/iteration-review`,
branch `codex/coloring-iteration-review-1028004102`. No model delegation occurred.
I read AGENTS.md, CLAUDE.md and the full revision plan, inspected the current
implementation/claim audits, the renewed resumption audit/intake, and the actual
candidate source, tests, guide, results and ITERATION_CHECKPOINT.md. Earlier
narrow handoff restrictions do not replace the renewed full-plan authorization;
earlier scientific exclusions and exact-hash admissions remain in force.

## Exact object of admission

Candidate root (abbreviated `C` below):
`/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/executed-iterations`.
The predecessor finished before this review. Its worktree was clean at intake
and after validation. Implementation commit:
`ca4315b15583823c44e5a2b9d6059212511853f0`. Separate evidence/checkpoint commit and
reviewed HEAD: `3d5aa19c7231768e1547b00ad0fd1f75c32b804c`.

| Candidate file relative to C | SHA-256 |
| --- | --- |
| `src/logique/benchmarks/iteration_study.py` | `ae8ab77da89716381c3ec86b1d044e6800f8fbf748251543ac2d7a2161354539` |
| `tests/test_iteration_study.py` | `0bb47bb75ded322ea09fab2f97084e6828624317469bc0a3ea8e1b45aedec3cf` |
| `configs/iteration_pilot.json` | `523c3439cb576fd0a9d2c3cd5d99a73a825ac0ef87e804447d3153818a6adb40` |
| `docs/research/iteration_study_guide.md` | `5c9885322d95d41bb2ec1387faaf2dd34bd4d5b5ee194c2f0a0460b281927f11` |
| `docs/research/iteration_pilot_results.md` | `1fc5cab42f566da7e5d6e21696ee3fbe26e578fe66aa956a007e450720f00cbf` |
| `ITERATION_CHECKPOINT.md` | `e62254d291f715c9d018213344dad5e38a2f3e109f4e53ae814e2f6cb353c9c2` |
| `dump/1028005202-executed-ideal-iterations/manifest.json` | `0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811` |

The exact manifest binds **211 saved evidence files**, including config,
requests, logs, per-case results and QPY components; every entry was hash-checked.
All 11 entries in the worker's final validation receipt also matched. The final
receipt SHA-256 is
`2101be1c60a7241860a3e72113be5eb5a612a33f3cf5eccad744c751b8c00380`.
The older development pilot is preserved and is not substituted for this run.

Reused source identities are also part of the reviewed construction:

| Source relative to C | SHA-256 |
| --- | --- |
| `src/logique/benchmarks/ideal_iterations.py` | `7724b76624bc07cf3164abf2c76ddb677c21ccc6cdc86991f8cc09b659b53e40` |
| `src/logique/benchmarks/coloring_study.py` | `3df109e3d8a368ad552ca8f628a6ee96736e306af488c9e1481493845399ce62` |
| `src/logique/circuits/structure.py` | `8c7a999384f61a6dcd69372472030c8b8de36c04b2beb8909213140a0eaf2073` |
| `src/logique/circuits/grover.py` | `be7c0ed0f4b322b18c19d35cb4ea74f7f2bb38fd4d191a61131373bf984b9598` |
| `src/logique/coloring/encoding.py` | `000bb92b33757dbb576199f44c82003da4e12c40185ad2d99813b54427f6b837` |
| `src/logique/coloring/model.py` | `b99c29bf82e6767974d411dd2dd3b9d8bd7a71816253de9d707d9d3e682248fb` |

Admission is for these bytes and this evidence, not arbitrary future variants of
the files. The coordinator must verify the identities on integration.

## Contract and independent derivation

The construction is the sequential structure oracle with clean flags,
comparator scratch and output, sorted vertex labels and LSB-first color words.
R1 prepares all binary words and marks the complete coloring predicate. R2
prepares valid codes and marks the complete predicate. R3 uses the same valid-code
preparation and the edge-only oracle; equivalence to complete coloring is confined
to that support. All non-data wires must start zero. No arbitrary-dirty-workspace
contract is inferred.

For every case, the reviewer enumerated integer color tuples and packed their
indices independently of all candidate count/encoding/predicate helpers. Marking
requires each color < k and unequal endpoints; the R3 oracle's out-of-support
phase was checked against inequalities alone. The independently counted M and N
matched all 36 records, including the two unexecuted cases.

The reviewer applied exact `Fraction` arithmetic to **each individual data
amplitude**: start with coefficient 1 on the declared support and 0 elsewhere;
negate marked coefficients, then apply `2*support_mean - coefficient` on support
and negate the complement. Divide coefficients by sqrt(N) only when comparing
to the numerical state. This derives the actual action of
`D = 2|s><s| - I`, where `|s> = A|0>`, independently of the candidate's good/bad
recurrence. Exact rational probabilities determine the first local peak for
0 < M/N < 1/2; ties choose fewer iterations. For M/N >= 1/2 the first-lobe
integer optimum is j=0; M=0 or M=N uses the explicit constant-probability
convention. Every saved extent agrees with j=0 through this peak+1.

An additional calculation compared each row to
`sin²((2j+1)*asin(sqrt(M/N)))`, treating M=0,N separately. The full signed
statevector, leakage, norm and clean-workspace probability were checked, with
no fitted scalar or relative-phase alignment. R1 leakage was compared to the
independent probability on invalid integer codes, rather than incorrectly
requiring zero. R2/R3 leakage must vanish within the declared numerical tolerance.

The reviewer loaded and evolved the saved QPY components directly; the candidate
simulation helper did not supply replay probabilities. Both runs use the same
installed Qiskit Statevector engine, so this is independently constructed
reference/replay evidence, not a claim of two independent simulator engines.
The saved operations are all U/CX on at most two wires. Preparation and diffusion
were applied even for the zero-data case to verify their scalar convention:
D=+1 and the true empty oracle supplies -1 on each iteration.

## Observed validation

All **34 completed cases / 151 rows** reproduced. The retained scope is paths3–8
k2, K3/C5/P4 k3, unsatisfiable K3 k2, the empty k3 graph, and a noncontiguous
edge/isolate k3 fixture, each requested in R1/R2/R3. The maximum independent
signed amplitude residual and maximum combined numerical comparison error were
both **6.512331117749953e-14**, below 1e-10. The saved maximum probability error
is 4.440892098500626e-14, restoration/norm error 4.4853010194856324e-14, and
restricted-support leakage 1.121429153693601e-29; replay agrees with these rows.

In particular, K3 k3 R2 at j=1 gives **0.9903978052126163** with M=6,N=27;
path8 k2 R1 at j=1 gives **0.06885528564453086** with M=2,N=256. These are actual
saved-circuit reproductions of the analytical checks, not inserted predictions.

Five further coherent probes used deterministic complex coefficients on **all**
binary inputs, entangled with a reference qubit, with the oracle shifted onto
physical wires 1..width and the reference on wire 0. They covered K3 k3 R3,
unsatisfiable K3 k2 R1, empty k3 R1, and the noncontiguous edge/isolate k3 R1/R3.
Absolute oracle phase, oracle squared, and matching diffusion on the arbitrary
complex state all agreed. Maximum error across these probes was
**2.2275578683769102e-15**. They used at most 13 total wires. Clean non-data
restoration was included in the full-vector comparisons; the reference was
entangled with data, not substituted for dirty scratch.

Tiny dense-operator checks on one-vertex k=1,3,5 preparations and diffusions used
at most **3 qubits**, testing asymmetric valid-code support and the complement
with absolute scalar phase. Maximum error was **1.2165651714327434e-15**.
These are bounded diagnostic checks, not general ideal-amplitude certification.

The focused candidate-source regression suite passed **379 tests**, with no
skips/deselections. It includes the deliberately opposite-sign diffuser whose
probabilities agree while signed amplitudes fail, all-binary exact phase and
restoration, empty/unsatisfiable/isolate cases, and timeout/budget bookkeeping.
The worker's saved Black/Ruff logs and receipt were verified; no full-suite,
build, notebook, historical replay or noisy/routed experiment was rerun here.

## Resource and reproducibility assessment

The source caps exact enumeration at 12 data bits before enumeration, checks the
actual complete register against max_qubits<=18 before quantum preparation or
statevector arrays, resolves definitions and scalar phases, then lowers to U/CX
before evolution. It never asks the statevector engine to materialize a wide
gate matrix. The inspected structure builder constructs circuits, not dense
operators, before the width gate. The reviewer independently patched preparation
and Statevector allocation to fail, and observed C5 R1/R2 return infeasible
without reaching either; a 13-data-bit config was rejected at enumeration guard.

C5 k3 R1/R2 require **22 wires**, exceed 18 and have **no executed rows or QPY**.
Their exact M,N, full requested analytical sweep and next action are retained.
C5 R3 executes at 17 wires. The result `probability_kind` field alone must never
be used to count executions: only actual rows in completed cases are admitted.
The unsupported cases are not evidence of circuit failure or successful execution.

The supervisor is serial, records wait4 peak RSS and exit status, kills the child
process group on its timeout, and preserves explicit failed/timeout/budget
statuses. It uses <=180 seconds per child and <=900 seconds declared cumulative
numerical budget, with BLAS/OpenMP threads one. These guards and RSS observations
are not an aggregate OS memory limit. Direct `simulate_case` has no timeout and
must remain externally supervised for experiments, as the guide states.

The original final pilot measured **29.322163625 s**, maximum child
**2.355273625 s**, maximum child RSS **147324928 bytes**. The independent review
ran one numerical process at a time, with a 180-second timeout for each of two
children (360-second total declared envelope):

| Review child | Actual seconds | Measured peak RSS bytes | Result |
| --- | ---: | ---: | --- |
| Independent replay/coherent/guard probes | 11.728340542 | 107266048 | passed |
| Focused candidate regression suite | 7.391624083 | 149880832 | 379 passed |

Total measured child wall time: **19.119964625 s**. No numerical failure,
timeout, OOM or comparison failure occurred. Existing Python 3.10.22, NumPy
2.2.6 and Qiskit 2.1.1 were used without installation or sync. Each child had
`PYTHONPATH=C/src`; the probe asserted the actual imported candidate module path.
The pytest child ran from C with bytecode and pytest cache writes disabled.
No candidate/root source or saved result was changed.

The native executable was explicitly selected and its actual SHA-256 checked:
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`, at the supplied
private `native-contract/dump/1025025511-native-contract/build/boolean_synthesis`
path. It was neither invoked nor rebuilt. The old root executable was not used.
Cache was `/Users/mar/codex-work/logique/.cache/epfl`; no compiler ran.

## Review artifacts, preservation and release

Review artifacts are in this worktree under
`dump/1028005723-iteration-independent-review/` (`R` below). Reproduction command:

```sh
/Users/mar/codex-work/logique/.venv/bin/python R/supervise.py
```

For a new replay, copy `review_probe.py`, `supervise.py` and `protected.json` into
a **new timestamped review run directory** first; their output paths derive from
their own location. Never rerun into this frozen evidence directory. The
supervisor supplies exact candidate PYTHONPATH, native/cache paths, thread
limits, commands, child timeouts and RSS measurement. `commands.json` and logs
record the actual commands and outcomes. `replay.json` retains every compared
row and coherent probe; `summary.json` and `completed-checkpoint.json` provide
the bounded handoff. The initial checkpoint is preserved separately.

`R/candidate-identities.json` SHA-256:
`5978a24cb0977fae3e2a14eb6c686b48cac8147ccdadc0362b0dd2e0f654839e`.
`R/evidence.json` binds the review scripts, logs, identities, comparisons and
checkpoints; SHA-256:
`9ccbc7d62141725ce39e2c6501d290272434fc891f5d3397f5cb11f1435498e1`.
The post-commit receipt is separate to avoid a self-referential hash.

All 15 relevant protected files remained unchanged. Root user README SHA-256
remains `73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`.
Dependency pins, old numerical outputs, earlier failures, histories and archives
were not changed or recursively rehashed. The worker's two documented development
failures remain historical; they were not erased by this passing review.
This worker commits only ITERATION_REVIEW.md, with no integration or push.

**Scope exclusions:** no new noisy or random-trial execution, shot confidence
interval, routed evidence, cost-per-success result, preparation-rotation/FT/RUS
extension, native strategy admission, resource advantage or manuscript approval.
The random comparison remains explicitly analytical `1-(1-M/N)^(j+1)` with one
classical predicate test per draw, not an equal quantum-resource experiment.
Exact statevector probabilities have no binomial shot interval. No hardware,
physical QEC, precolored or conditional-workspace synthesis work occurred.

**Next action:** coordinator verifies these exact identities and integrates the
bounded implementation/evidence/review; dispatcher alone pushes the integration
branch. C5 R1/R2 require a separately reviewed lower-workspace complete-predicate
oracle or a newly authorized larger resource budget, followed by their full
retained sweeps. Continue the outstanding noisy/routed and broader full-plan
work through new bounded jobs. Do not repeat this completed review or infer
full-paper completion from its ADMIT decision.
