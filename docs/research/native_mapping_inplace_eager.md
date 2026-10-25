# Native mapping checkpoint

Bounded Task 5 mapping integration: **complete**, 25 October 2026.
This is an implementation handoff, not full-paper completion or scientific
performance admission. No metrics, benchmark profiles, rotation/FT decisions,
archived results or dependency revisions changed.

Worktree: `/Users/mar/codex-work/logique/dump/1025030802-native-integration/worktrees/inplace-eager`.
Branch: `codex/coloring-inplace-eager-1025030802`.
Intake: clean `7aeacb6000073fe303f66d803d6e349704cff02e`.
Implementation commit: `3cd712e86111f911eac02a6492524e71e37c2e19`
(`Expose opt-in in-place Bennett and eager mappings`). This commit contains only
six owned implementation, bridge-documentation and focused-test files. There
are no CMake/build-system, dependency or research-metric changes to combine with
this mapping implementation. This checkpoint is a separate documentation commit.

Before editing, inspected Git and the dispatcher state/queue; read `AGENTS.md`,
`CLAUDE.md`, `docs/coloring-paper-revamp-codex-plan.md`,
`docs/research/implementation_audit.md`, `docs/architecture.md`, the supplied
`dump/1025030802-native-integration/batch.json`, and the foundation checkpoint.
The latter is absent from this intake worktree's docs but was read at the supplied
original path and at `/Users/mar/codex-work/logique/docs/research/native_contract_foundation.md`.
Dispatcher state identified this job as running and its coordinator as queued.
The sandbox denied `ps`; no process or dispatcher mutation was attempted.
Dispatcher exclusively owns model launches. No agents, model subprocesses,
API/paid fallback, hardware, pushes, publishing, environment sync or dependency
updates were used. The queue was read, never edited.

## Delivered contract

The five method names remain exactly `xag`, `aig_bennett`, `xag_bennett`,
`klut_bennett`, `best_fit`. `synthesize(..., strategy=...)` and native JSON
`strategy` accept `bennett`, `bennett_inplace`, `eager` only on `aig_bennett`
and `xag_bennett`. Omission retains each method's prior algorithm/preprocessing.
Explicit `None` at the Python API means omission; native JSON null rejects.

The bridge instantiates the actual pinned classes:
`caterpillar::bennett_mapping_strategy`,
`caterpillar::bennett_inplace_mapping_strategy`, and
`caterpillar::eager_mapping_strategy`. It records selected `name`, whether
`explicit`, and qualified `implementation` in `mapping_strategy`. Full actual
steps are serialized through the already-admitted exhaustive action visitor.
Explicit Python requests appear in `parameters` and require the requested name,
explicit flag, exact implementation and a step array in the native response.
An older/nonconfirming bridge cannot silently ignore the control.

All strategy overrides on `xag`, `klut_bennett` and `best_fit` reject, including
an explicit `bennett`. Unknown strategy values and unsupported method/control
combinations reject at the Python API and native boundary. Historical expression
synthesis is unchanged and still uses its original tweedledum network.

## LHRS audit and limits

- Input allocation preserves every declared PI, including unused inputs.
  Cleanup/conversion keeps positional input order; tests use asymmetric functions
  with deliberately ordered inputs and an unused input under both common policies.
- In-place Bennett decrements full fanout references and overwrites an eligible
  last-use fanin only for a non-output XOR node. Its actions contain **node**
  indices; LHRS resolves `target_index` through the target node's live stack top,
  pushes that same wire for the XOR result, and emits only the other XOR control
  plus any complemented parity. It restores XORs in reverse order before earlier
  ancestors need their original values for uncomputation. Nested aliases to a
  single physical wire are intentional, not additional live copies.
- The pinned in-place inverse leaves its node stack entry. In these admitted
  schedules each node computes once, with no recomputation or second live copy;
  the stale entry is never subsequently read as a recomputed value. Arbitrary
  recomputation, mixed in-place/best-fit schedules and other strategy classes
  are not exposed or certified. The existing ordinary-uncompute stack-pop
  overlay remains necessary and byte-identical to the admitted foundation.
- Eager computes topologically, cleans fanins when their remaining references
  reach zero at an output, and reuses released wires. Full gate fanout counts
  include POs, so intermediate output drivers and shared fanout stay live.
  Tests cover early cleanup before later output computation, a shared internal
  node, and repeated/complemented output aliases. No recomputation is introduced.
- LHRS prepares output aliases after mapping; the first complemented output of a
  PI may flip that PI in the raw circuit. Raw input restoration is not promised
  for that case; actual compute/copy/uncompute XOR and phase wrappers restore it.
  Tests check every joint XOR-target pattern and every selected phase output,
  including repeated projections, complements, zero and one.
- AIG has no XOR gates. Selecting in-place Bennett on AIG is supported but emits
  only ordinary compute/uncompute. XAG also needs an eligible internal XOR for
  actual in-place actions. Both behaviors are explicit and tested; no in-place
  width reduction is claimed for AIG. There are no level actions in these maps.

`emitted-action-evidence.json` saves eight actual schedule/gate records under
both policies. The XAG input-target fixture has three in-place compute/inverse
pairs, beginning with target node 2 and then targets 5/6 on the same live wire.
The gate-target fixture has two pairs, beginning at gate node 5 (wire 4), proving
that node and physical target indices differ. Both restore raw inputs/workspace.
The eager AIG/XAG fixture emits `compute, compute, uncompute, compute, compute,
uncompute`, reusing a released wire. These are deterministic acceptance fixtures,
not benchmark or superiority results. Serializer probes alone were not used to
certify gate emission.

## Private build and exact commands

All new artifacts are in the ignored worktree-local
`dump/1025071722-native-mapping/` (`$RUN` below). Root binaries were preserved.
Existing root research Python: `/Users/mar/codex-work/logique/.venv/bin/python`
(Python 3.10.22). Existing checkpoint CMake 3.31.6/Ninja 1.11.1.4; compiler
AppleClang 21.0.0.21000099. Effective clean Caterpillar source:
`/Users/mar/codex-work/logique/external/caterpillar`, revision
`4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`, with unchanged bundled dependencies.
No download or source initialization occurred.

`$RUN/run.py` records exact argv, cwd, exit status, elapsed time and child peak
RSS in `commands.jsonl`, and stdout/stderr in each named log. It sets these for
every child (no environment synchronization):

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$PWD/src
export LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl
export RUN=$PWD/dump/1025071722-native-mapping
export LOGIQUE_NATIVE_EXECUTABLE=$RUN/build/boolean_synthesis
export PY=/Users/mar/codex-work/logique/.venv/bin/python
export TOOLS=/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/build-tools/bin
```

Exact underlying private build/probe commands:

```bash
$TOOLS/cmake -S external/native/boolean_synthesis -B dump/1025071722-native-mapping/build -G Ninja -DCMAKE_MAKE_PROGRAM=$TOOLS/ninja -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_CATERPILLAR=/Users/mar/codex-work/logique/external/caterpillar -DLOGIQUE_BUILD_CONTRACT_PROBES=ON
$TOOLS/cmake --build dump/1025071722-native-mapping/build -j1
$TOOLS/ctest --test-dir dump/1025071722-native-mapping/build --output-on-failure -V
```

Build passed; CTest **1/1 passed**, including **13 exact complete serialized
rows across seven variants**. `configure.log`, `build.log`, `ctest.log` retain
all output. CMake and both compatibility-overlay recipes are unchanged.

Final Python acceptance command:

```bash
$PY -m pytest tests/test_native_mapping_strategies.py tests/test_native_contract.py tests/test_provenance.py tests/test_interfaces.py tests/test_verification_assignments.py tests/test_benchmark_synthesis.py tests/test_phase_study.py -k 'not teaching_functions and not constants_aliases_and_output_order and not lut_lowering_bit_order_and_negative_controls and not phase_notebook_smoke and not borrowing_restores_entanglement_and_phase' -q -p no:cacheprovider
```

Result: **353 passed, 27 deselected, no skips**, 14 existing matplotlib/pyparsing
warnings (`regressions-final.log`). This comprises **221 new focused mapping
cases and 132 existing regressions**. Existing EPFL, best-fit cleanup, metadata,
phase/lowering and input/verification regressions pass. The 27 exclusions are
15 broader teaching statevectors, five alias/projection statevectors, five LUT
operator tests, one notebook smoke and one borrowed-workspace simulation.
New alias/constant behavior receives exhaustive monomial checks instead.
All actual dense quantum checks in this selection are <=5 qubits; new tests
assert oracle width <=5 before statevector simulation. The existing dense Rx
operator check is three qubits. Other tests track monomial permutation/phases
compositionally; no large statevectors/dense operators are constructed. New
Boolean fixtures have at most six inputs; joint target enumeration is bounded.
Coloring checks use independent `problem.is_valid` via encoding verification for
noncontiguous labels, isolates/invalid codes, empty and unsatisfiable constraints.

Earlier focused run: **83 failed, 122 passed**, because the new fixture writer
omitted structural Verilog token/line separators. Corrected the writer to the
pinned reader's accepted format; retry **205 passed, no skips**. Added 16 targeted
fanout/target/boundary cases before the final 353-case run. All failure and retry
logs are retained; no bridge correctness failure was hidden or skipped.

Compatibility/evidence commands:

```bash
$PY dump/1025071722-native-mapping/compare_intake.py
$PY dump/1025071722-native-mapping/save_evidence.py
$PY dump/1025071722-native-mapping/record_identity.py
$PY dump/1025071722-native-mapping/run.py preserve
```

**135/135 exact native comparisons** pass against the admitted intake executable:
nine input/projection cases times all five methods times omitted/common-none/
common-refactoring preprocessing, with strategy omitted. Every pre-existing
response field, full action payload, gate and wire mapping matches, excluding
only nondeterministic `native_seconds` and the new additive `mapping_strategy`.
Fixtures: `xor_and`, `and4`, `shared`, factoring, aliases and reordered/repeated
projection, zero/one constants, cached `ctrl.aig`. **3/3 historical expression
comparisons** also match gates, networks, circuit, order, source Verilog/hash and
parameters. This does not rerun or modify the 135 archived paper metrics.
`intake-comparison.json` records controls, fixture/source/executable hashes and
full matches. The admitted executable was reused after verifying its exact hash
and bridge/API source identities against intake `7aeacb6`; no old bridge rebuild
or root binary overwrite was necessary.

Static checks, all passed:

```bash
$PY -m black --check src/logique/synthesis/api.py src/logique/synthesis/native.py tests/test_native_mapping_strategies.py
$PY -m ruff check src/logique/synthesis/api.py src/logique/synthesis/native.py tests/test_native_mapping_strategies.py
$PY -m mypy
git diff --check
```

Mypy checks the configured five core files; it adds no static coverage of the
synthesis modules. Only relevant Python files were formatted.

One numerical/compiler job ran at a time, build parallelism `-j1`. Observed
maximum child RSS: **942,342,144 bytes** during compilation; final regression
peak **252,231,680 bytes**. Both are below 8 GiB; fixtures and serialized jobs
bound memory. No new OS memory-limit guarantee is claimed (the foundation
checkpoint establishes Darwin RLIMIT_AS is unavailable). Parent logging Python
is small and holds no circuit/statevector. No other numerical job was launched.

## SHA-256 and preservation evidence

`identity.json` contains all maintained bridge/API/test source hashes, effective
header hashes, compiler/build provenance, tool hashes, dependency status/pins,
and overlay hashes. It verifies admitted headers/overlays and clean dependency
source. Its recorded revision is implementation commit `3cd712e`.

| Artifact | SHA-256 |
| --- | --- |
| Private executable | `b4f1df2cc6c7928313b52bb5d062c3a835279f41f2a04edcc6eed9455af36032` |
| Admitted intake executable | `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a` |
| Compiled serializer probe | `25fbc68d9a5e74c270b3d48199f901b459e40c77f2a7eced855bb2fc51ffddb4` |
| `include/mapping.hpp` | `ecaf85e004e6b5f9db23dfe5647ddd596af9ca73844fcdb94caa56836073251e` |
| `include/types.hpp` | `98288e251c285edad545ab63a06b88f3fe364b38776bbb8643ee2cc866251ca0` |
| Python `api.py` | `0ea3bc243d3dbe0f1881a64f8642abb67dd700bd7562361933eca17e226829de` |
| Python `native.py` | `d44edda7e0441eaae21564ec5c2f451e0378e90ede5e22607b0ab6a2f7bca7bd` |
| Focused mapping tests | `506da223df7d73f3bea2ad517d47a70a28909e4a867eeaec8522d949d618100b` |
| Pinned Bennett/in-place header | `a69e00b282b3ecd96e30a6e8dbfaedcfb6ac96bcc7eafdb68382f0130d66208f` |
| Pinned eager header | `95ef093716a90fc43e326c32a8b046778b880c8441ddfa3d30b583309e77c2fe` |
| Pinned LHRS header | `dab0018ff90d1901dbf4c9dee2f387f7595ddccf690e5eb6f5c94153c7150825` |
| LHRS compatibility overlay | `edd39ec5371dc33f985d6cf1ea0c3c0dd5c394da1cc69604afe92e23f3cbe7b9` |
| Best-fit compatibility overlay | `45783c86d522924f074fa18f31f58059ae8c799312286403497315cb49e39518` |
| Build provenance JSON | `5f07fd225e7f2eb74ca3925e808a32b312670cd328d583549e460889e7106b91` |
| `identity.json` | `5a8e3db8a50f12a68fccce4cd0f81707c106df934bac6a823c2ea155ced00050` |
| `artifact-hashes.json` | `ad03aa683ba190c1e3b840b8d72adaab8b6c04062bc58bbad7bb1fa80118152f` |

`artifact-hashes.json` hashes the run's direct logs/scripts/JSON and saved fixture
sources. `protected-before.json`/`preservation.json` confirm all **158** protected
root files unchanged, including README, rotation files, root executable, archived
manuscript results, nested Git metadata and history bundles. Worktree README
matches intake. All five dependency gitlinks match root/intake pins. Root status
still shows only the pre-existing README change. No dependency checkout changed.

## Concrete remaining scope and handoff

No requested in-place/eager strategy remains blocked in this bounded contract.
The queued `coordinate-mapping-1025030802` owns independent review and any root
integration; neither was performed here. Preserve this private run directory
before deleting the isolated worktree. Do not rerun implementation or append
queue jobs merely because the full research remains open.

Explicitly unsupported and untested beyond rejection: low-T/low-depth XAG
strategies, level-based gate emission, SAT/pebbling and solver linkage, in-place
LUT/best-fit overrides, arbitrary mixed/recomputing schedules, MC reduction,
optimization-profile integration, balancing integration, structure scheduling,
new stage statistics, broad benchmark/scaling/noise studies and performance
claims. Those need separate bounded work and acceptance evidence. Larger-instance
formal equivalence and general asymptotic behavior were not established here.

Rotation/FT remains blocked for this batch pending the separate exact hash-bound
scientific admission process; this implementation and its passing tests grant no
admission and make no FT change. Full comparisons, complete-search accounting,
protocol freeze and evidence-gated manuscript/final review remain outside this
batch. Full-paper completion is not asserted.
