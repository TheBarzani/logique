# Bounded native SAT pebbling candidate — 31 October 2026

Task `native-mapping-sat-1030020413`, session
`01a190c5-7239-7413-aeab-d02f508d796a`, assigned branch
`codex/coloring-native-mapping-sat-1030020413`, intake
`e90adf3373236ef51a937480febd3cd7d669dce7`.
Implementation: `622b950` (seven explicitly owned source/test paths).
This implementation batch is complete. **Independent exact-source/build review
and scientific admission remain pending.** No full-paper or performance claim
follows from passing these checks.

Evidence is worktree-local, created with `new_dump_directory`:
`dump/1031030426-native-mapping-sat/`. `commands.jsonl` and exclusive named logs
retain supervised commands, exit codes, elapsed time, environment and RSS scope.
`identity.json` binds source/dependency/review/build hashes; `semantic-evidence.json`
and `responses/` retain actual emitted schedules and gates with their inputs.
The final checkpoint records both worker commits and the actionable review gate.

## Actual missing path and solver feasibility

The existing in-place/eager admission, low-T rejection and sequential cone proof
were read with the full plan and current continuation/hard-bound handoffs. The
latest continuation is absent at this older worktree base and was read at
`/Users/mar/codex-work/logique/docs/research/full_scope_continuation_20261030.md`.
The separate native-value-validator branch was neither changed nor incorporated.
No exhausted low-T mathematical attempt was rerun, and no low-T name was exposed.

A minimal private C++ probe compiled and executed the actual pinned
`caterpillar::bsat_pebble_solver`, backed by `percy::bsat_wrapper` and bundled ABC
bsat2. Only Caterpillar's existing `lib/abcsat/satSolver.cpp` and `satStore.cpp`
were required. A two-gate chain returned a three-action SAT schedule. Full ABC,
Z3, dependency updates, downloads and source patches were unnecessary. The first
minimal compile failed because its include list omitted bundled Sparsepp; the
failure log and corrected build command are retained.

The maintained CMake target now links those two solver sources and writes
`sat_build_provenance.json`, separately from unchanged LHRS provenance. Effective
Caterpillar revision remains `4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`.
All five dependency gitlinks match intake. Existing LHRS and best-fit overlay
hashes remain unchanged.

## Public contract and explicit limits

Opt in on `aig_bennett` or `xag_bennett`:

```python
result = synthesize(
    source,
    "xag_bennett",
    strategy="sat_pebbling",
    preprocessing="none",
    qubit_budget=8,
    sat_max_steps=64,
    sat_conflict_limit=10000,
    sat_time_seconds=3,
    executable=private_binary,
)
```

All four integer budgets are mandatory; booleans, missing values, nonintegers,
zero, negatives and values above the caps reject. Caps are 64 total raw wires,
128 SAT horizons, 100,000 conflicts per solve and 30 search seconds. Inputs<=6,
gates<=32, nodes<=64, outputs<=16 are checked before truth tables/node maps/SAT
allocations. Each Boolean value is a single <=64-bit table. The emitted action
cap is 4,096. Larger networks are unsupported by this path, never silently
accepted without validation. Gates must be binary AND/XOR in stored topological
order. AIG conversion supplies ANDs only; unused PIs remain declared.

`qubit_budget` limits actual allocated raw circuit width, including every PI,
used constant, workspace wire and output alias/copy. External arbitrary-target
XOR wrapper targets are additional. The SAT pebble capacity subtracts fixed
input/constant wires; output-copy allocations and transient extraction order are
checked by the actual emitter. A SAT model that cannot be emitted within the
width cap rejects. There is no completeness or global width/depth optimality
claim. A zero-gate network bypasses the pinned solver's zero-variable case.

The pinned solver ignores its timeout argument. Native search checks a steady
clock between and after conflict-bounded solves. **Direct JSON clients need an
external process timeout**: a single solve has no native wall-time interrupt.
The Python boundary enforces `sat_time_seconds + 1` seconds for the whole native
process, including parsing/output, and kills/reaps it on timeout. One second is
explicit grace, not additional scientific search time. A real sleeping-child
regression verifies that timeout. Horizon/conflict/time exhaustion is reported
as bounded exhaustion/unknown, never as unbounded infeasibility.

The five existing methods and omitted defaults stay unchanged. Other methods,
unknown strategy names and SAT budgets on non-SAT strategies reject. Results name
`logique::bounded_sat_pebbling`, rather than mislabeling this custom bounded
search/emitter as the upstream unrestricted strategy. Metadata identifies the
actual pinned solver, horizons, budgets, unsupported native timeout and checked
value/release counts. Python requires matching strategy and budget confirmation.
README files are preserved as instructed; this new focused document describes
SAT support beyond their older unsupported-SAT statement.

## Value, restoration and action semantics

The new `sat_pebbling.hpp` is independent of the sequential cone/alias proof.
It uses the pinned solver and its extracted action sequence, then emits a
restricted exact static unitary computation. Only ordinary `compute_action` and
`uncompute_action` with neither explicit leaves nor cell override are supported.
Buffers, in-place actions, level actions and payload overrides reject. No
successful serialization is used as a semantic certificate.

An independent graph evaluation first gives every node its Boolean table
`f_n`. The emitter keeps one physical address per active node, a table `W[q]`
per allocated wire, and a zero-only free list. Initialization supplies distinct
PI addresses with their assigned functions and clean constant/workspace wires.
Every actual operand read requires an active address whose table equals `f_n`.
A compute allocates a distinct zero target, emits AND as an exact polarized MCX
or XOR as exact CNOTs plus complement parity, and checks `W[target] == f_n`.
An uncompute reads the same correct operands and target, emits the same toggle,
checks zero **before** release, and erases the node address. Recompute therefore
cannot read a stale stack alias. Every gate rejects repeated controls or a target
among controls. Allocation enforces the actual physical width before growth.

Inductively these exact reversible toggles preserve all other active values;
all free wires stay zero and all operand reads retain their graph meanings.
At the mapping boundary every PI, used constant and output driver is checked,
and every non-output gate must be absent/zero. Output preparation retains order
and complement, checks each requested value, and allocates distinct copies for
repeated drivers. A complemented PI output may flip that PI in the raw result.
The actual compute/copy/emitted-inverse and compute/Z/emitted-inverse wrappers
restore it and every computational wire. Each emitted X/CNOT/MCX is a phase+1
permutation, so checking every basis column and joint XOR target establishes
coherent linear action for the checked fixtures. Initial computation workspace
is clean; arbitrary dirty-workspace raw action is not asserted.

No preprocessing CEC was added. Metadata explicitly says `cec=not_performed`.
Small independently evaluated fixtures check both common preprocessing policies;
this is not large-instance equivalence or an extension of the old sequential
cone theorem. AND inverse remains a real unitary gate; no measurement-assisted
free uncomputation, low-T advantage or low-depth improvement is claimed.

## Actual build and checks

Existing interpreter only: `/Users/mar/codex-work/logique/.venv/bin/python`.
Candidate `PYTHONPATH` is this worktree's `src`; import paths are asserted in the
initial run creation, evidence and identity scripts. No environment sync ran.
CMake 3.31.6/Ninja from the existing server checkpoint, AppleClang 21.0.0;
explicit effective source `/Users/mar/codex-work/logique/external/caterpillar`.
Exact argv are in the receipts; final commands are:

```text
<checkpoint-tools>/cmake -S external/native/boolean_synthesis
  -B dump/1031030426-native-mapping-sat/build-final -G Ninja
  -DCMAKE_MAKE_PROGRAM=<checkpoint-tools>/ninja -DCMAKE_BUILD_TYPE=Release
  -DFETCHCONTENT_SOURCE_DIR_CATERPILLAR=/Users/mar/codex-work/logique/external/caterpillar
  -DLOGIQUE_BUILD_CONTRACT_PROBES=ON
<checkpoint-tools>/cmake --build dump/1031030426-native-mapping-sat/build-final -j1
<checkpoint-tools>/ctest --test-dir dump/1031030426-native-mapping-sat/build-final --output-on-failure -V
```

The private final build passed. **CTest 2/2 passed**: exhaustive action
serialization and actual SAT/action/value/release guards, including all five
unsupported richer action alternatives, missing operands, duplicate live
computes, dirty boundaries, missing uncomputes, bounded horizon exhaustion and
33-gate preallocation rejection.

**423 passed, 27 deselected**, no skips, in 25.343 supervised seconds with
254,246,912-byte wait4 high-water. Selection: new SAT tests plus existing mapping,
contract, provenance, interfaces, verification assignments, benchmark synthesis
and phase study; exact exclusion expression is in `commands.jsonl`. The 27
exclusions match the existing bounded mapping selection: 15 broader teaching
statevectors, five alias statevectors, five LUT operators, one notebook smoke
and one borrowed-workspace simulation. Actual selected dense checks stay <=5
qubits. New SAT checks allocate no statevectors or dense matrices.

The **70 new Python tests** include asymmetric/unused inputs, shared fanout,
equal/opposite parity cones, complements/constants, no-gate cases, six-input
64-column masks, reordered/repeated output aliases, exact arbitrary joint XOR
targets and every selected phase output with full computational restoration.
Independent coloring references include noncontiguous labels, k=3 invalid codes,
isolates, empty constraints and unsatisfiable self-loops. Negative tests exercise
Python and raw JSON budgets, unsupported methods, above-cap inputs/outputs,
insufficient physical width, output-copy width, horizon exhaustion, missing budget
confirmation and real process timeout.

A four-AND chain on five inputs actually fits eight raw wires with three gate
pebbles and recomputation. Its full emitted records and zero releases are saved
for both representations. This is a correctness fixture, not a benchmark gain.
Seed **1030020413** generated six further tiny circuits; **24 actual schedules**
(two representations/two policies) pass independent scalar coherent checks.
Sources, expected values and exact response SHA256s are saved. **30 exact omitted-
strategy protocol comparisons** on two tiny fixtures match the prescribed hash-
verified foundation executable across all five methods and omitted/none/
refactoring policies. Excluded fields are only `native_seconds` and
`mapping_strategy` (the latter was added by the earlier in-place/eager admission).
No archived historical metric/replay was rerun or changed.

Selected Black and Ruff pass. Configured Mypy passes its five core files; this
adds no synthesis-module type coverage. `git diff --check` passes.

Final executable SHA256:
`81bc6a786f29a5673881ef37c5fb0da02cec9d22a649b9d518d1b31db5d71571`.
SAT provenance SHA256:
`b8c56a4bcc9c3dc6a235ad80e5cb4b2bc702f4a91e3f5c1e0d449ccd526c13ba`.
The prescribed unchanged default remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.

## Failures, resource scope and preservation limits

Initial CTest failed and the initial focused suite had **8 failed/50 passed**.
The pinned `is_pi(0)` can also return true for constant zero when PIs exist;
the final-boundary audit incorrectly read that unused/unallocated constant.
Diagnostic output identified node0/address-1 after a valid schedule. The fix
excludes constants before testing the PI boundary. This was an implementation
boundary-check bug, not an exhausted mathematical low-T attempt. Full failure
logs, first/diagnostic header snapshots and subsequent successful checks remain.

Preservation limitation: the first new private `build/` executables were rebuilt
in place once for diagnostics before a separate first-binary hash/copy was made.
Those original candidate binaries are unavailable; their source snapshots and
build/test/failure logs remain. The diagnostic `build/`, corrected `build-3/`
and `build-final/` binaries are now separately retained and hashed. No existing
root, prescribed, historical or other-worker binary was overwritten. Future
revisions must use a fresh build directory from the start. No old candidate,
review, queue history, failed research artifact, dependency pin or README was
modified. Root README observations and unchanged worktree README are recorded;
there is no blanket claim that all root files were rehashed.

Declared before allocations: one compiler/numerical child at a time, -j1 and
BLAS/OpenMP/Accelerate/Rayon/Qiskit parallelism1; 120s per supervised child,
900s cumulative numerical budget, 6GiB declared process memory. Cumulative
supervised work was about115s before documentation/final scalar checks. Maximum
wait4 high-water **913,752,064 bytes** occurred in a private compile. This is
Darwin child accounting, potentially including reaped descendants, not sampled
simultaneous group memory or a hard memory cap. No hard cap or sampled aggregate
RSS enforcement is claimed. Static domain/width/table bounds control allocations.
No statevector>18 or dense Operator>5 was created; the separate staticFT pilot's
four-qubit limit is untouched.

Initial Git staging was sandbox-denied on this worktree's `index.lock`; the
scoped authorized escalation succeeded. No automatic approval-review rejection
occurred. Git commands/receipts are saved separately with RSS unavailable.
No model/subagent/Codex subprocess, API/paid fallback, purchase, sync, hardware,
physicalQEC, precolored or conditional-workspace research was launched. No push
was run; dispatcher alone publishes root integration HEAD.

## Concrete next action

Queued `native-mapping-review-1030020413` must independently inspect exact
`622b950`, the final source/build identities and saved outputs, including this
preservation limitation, the pinned solver/extraction contract, width accounting,
zero-gate bypass, conflict/time unknowns and ordinary-action invariant. It should
rebuild in a **new** private directory at -j1 and repeat bounded coherent/negative
checks. Do not infer admission from queue status. Then
`native-mapping-integrate-1030020413` may integrate only exact independently
admitted bytes, reconciling API/mapping/CMake overlap with the separately reviewed
native-value path. No worker integrates root. Larger SAT/CEC, other fast/depth/
low-T paths and comparative qubit/T-count/T-depth research remain open tasks.
