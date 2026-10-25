# Native contract foundation checkpoint

Bounded Task 5 foundation: **complete**, 25 October 2026. This is an
implementation handoff, not scientific or paper approval. No performance claim,
research-metric change, or FT gate change is made.

Worktree: `/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract`.
Branch: `codex/coloring-native-contract-1025024643`.
Intake was clean at `b422c759735437a45b42fcf81ce5e226ac594bd3`.
Read `AGENTS.md`, `CLAUDE.md`, `docs/coloring-paper-revamp-codex-plan.md`,
`docs/research/implementation_audit.md`, and `docs/architecture.md` before editing.

Implementation commits, in order:

- `78a514cb531207f5e62c02cf0c6ff484a855826d` — Serialize every pinned Caterpillar action.
- `6c34eb4af904ecc60991d573f6ef8b911444ec3f` — Add opt-in common native preprocessing.

The first isolates serializer correctness and its compiled probe source; the
second adds the preprocessing bridge/API, optional probe build target, and
regressions. No metrics or dependency commits are included.

## Delivered contract

`synthesize(..., preprocessing="none" | "refactoring")` and the matching native
JSON control select a shared XAG after output selection, before representation
conversion. Refactoring runs once with pinned bidecomposition/default pass
parameters, then dangling cleanup. The selected policy, whether it was explicit
(`common`), and ordered `before_network` / `after_network` graphs are recorded.
Explicit requests appear in Python parameters and require bridge confirmation;
an older bridge cannot silently ignore them. Unsupported policies, unknown
native request controls, and native method-specific controls on other methods
fail. Public method selection is unchanged.

Omission preserves the legacy policy: unrefactored AIG Bennett, refactored XAG
for the other four methods. Historical expression synthesis is unchanged.
`source_network` remains the selected graph before preprocessing, and `network`
remains the mapped representation (underlying XAG for best-fit). Before editing,
the consumers were inspected: classical/phase/quantum verification uses
`source_network`; `SynthesisResult.summary()` and drawings use `network`;
visualization exports mapping rows through pandas without classifying actions.
No consumer or summary metric definition changed.

The action visitor explicitly covers all seven pinned alternatives:
compute/uncompute, compute/uncompute in place, buffer, and compute/uncompute
level. It preserves optional explicit leaves distinctly from cell leaves,
MSB-first cell truth tables, in-place target indices, buffer target/leaf, ordered
level entries and every cone's root/leaves/complemented/target/copies. Empty
and unspecified payloads remain distinguishable. Legacy cell `leaves` and
`lut_inputs` columns remain. There is no generic visitor overload; an added
variant requires a compile-time serialization decision.

## Private build and identity

All outputs are in the ignored worktree-local run
`dump/1025025511-native-contract/` (called `$NATIVE_CONTRACT_RUN` below).
The root bridge executable was never overwritten or selected for tests.
The private executable is `$NATIVE_CONTRACT_RUN/build/boolean_synthesis`.
An additional private intake-source executable was built from `git show b422c75`
under `legacy-source/` and `legacy-build/`, solely for default compatibility.
No dependencies were initialized, fetched, or changed; no environment sync ran.

Effective dependency source:
`/Users/mar/codex-work/logique/external/caterpillar`, clean at actual revision
`4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`, with its bundled headers.
Compiler: AppleClang `21.0.0.21000099`; Python `3.10.22`; isolated CMake
`3.31.6` and Ninja `1.11.1.4`. The two pre-existing compatibility overlays
(`lhrs_uncompute_stack_pop`, `best_fit_cell_fanout`) are unchanged.

SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| Private bridge | `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a` |
| Private action probe | `25fbc68d9a5e74c270b3d48199f901b459e40c77f2a7eced855bb2fc51ffddb4` |
| Private intake bridge | `ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa` |
| `build/build_provenance.json` | `5f07fd225e7f2eb74ca3925e808a32b312670cd328d583549e460889e7106b91` |
| `include/actions.hpp` | `d11b186854d9e8103f568d4a5a2b91f67ef7c4614b9674af956b272139934257` |
| `include/mapping.hpp` | `e35fb2386f8f1a253bc82c8102ae3b2807844878879fbb550e927052b93e3843` |
| `tests/action_serialization.cpp` | `4d16c1d9ce99deb3e38ead280cdf72604e8ff709a3c0a4e06820f84985564638` |
| `src/logique/synthesis/api.py` | `9ab5ec58f1479ed4035b27e474629e81268740a686ef91cd88b217d6bcfd0c9c` |
| `src/logique/synthesis/native.py` | `604d66fd3c43a3e6fbc964f12c70e9454acc42728bf1ea0726756e8d0b95c292` |
| `tests/test_native_contract.py` | `2dd5bf913d4625a5ce3cc53a33fcb48fa16a3fc242e87a347108b566945359ae` |
| Pinned `strategies/action.hpp` | `2de93fa095a50deb546f6b8c8bddc445c7ddd949c2d4ca34b4d662138a2b992e` |
| `identity.json` | `69cdc0c56b721f260882ef4ea7cd6706eac75bc7d9934c6d7adaa54af26e236e` |
| `artifact-hashes.json` | `2ac770735dda0bdbd8f2a64e6a8cdcd7b08bdf199cd7d3338cba1e3012c55683` |

`identity.json` records all bridge sources, dependency/header and overlay hashes,
tool hashes, exact paths, revisions and executable provenance. `artifact-hashes.json`
hashes the direct run artifacts, including logs and reproduction scripts.
`preprocessing-evidence.json` contains native records for both policies through
all existing methods on the deterministic factoring fixture, excluding timing.

## Exact validation

Commands were run from the assigned worktree with these settings:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$PWD/src
export LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl
export NATIVE_CONTRACT_RUN=$PWD/dump/1025025511-native-contract
export LOGIQUE_NATIVE_EXECUTABLE=$NATIVE_CONTRACT_RUN/build/boolean_synthesis
export NATIVE_CONTRACT_TOOLS=/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/build-tools/bin
```

Private build and compiled probe:

```bash
$NATIVE_CONTRACT_TOOLS/cmake -S external/native/boolean_synthesis -B "$NATIVE_CONTRACT_RUN/build" -G Ninja -DCMAKE_MAKE_PROGRAM="$NATIVE_CONTRACT_TOOLS/ninja" -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_CATERPILLAR=/Users/mar/codex-work/logique/external/caterpillar -DLOGIQUE_BUILD_CONTRACT_PROBES=ON
$NATIVE_CONTRACT_TOOLS/cmake --build "$NATIVE_CONTRACT_RUN/build" -j1
$NATIVE_CONTRACT_TOOLS/ctest --test-dir "$NATIVE_CONTRACT_RUN/build" --output-on-failure -V
```

Result: **1/1 CTest passed**, checking **13 exact complete JSON rows across all
7 action variants**, including populated cones, ordered vectors, null/empty
leaves, cell truth/leaves and empty levels. See `native-probes-final.log`.
`configure.log`, `build-retry.log` and `build-final.log` retain build evidence.
The first build failed because bundled JSON lacks `contains`; the code now uses
`find`, with the successful build against the unchanged pin retained.

Final Python suite:

```bash
/Users/mar/codex-work/logique/.venv/bin/python -m pytest tests/test_native_contract.py tests/test_provenance.py tests/test_interfaces.py tests/test_verification_assignments.py tests/test_benchmark_synthesis.py tests/test_phase_study.py -k 'not teaching_functions and not constants_aliases_and_output_order and not lut_lowering_bit_order_and_negative_controls and not phase_notebook_smoke and not borrowing_restores_entanglement_and_phase' -q
```

Result: **132 passed, 27 deselected, no skips**, 14 existing matplotlib/pyparsing
deprecation warnings (`regression-tests-final.log`). This includes **88 new
contract cases**, the existing EPFL regressions, best-fit stack/router cleanup,
phase/lowering and metadata consumers. New tests cover independent asymmetric
Boolean values, an observable refactoring, common before/after evidence across
all five methods, unused inputs, output projection/repetition, complements and
both constants. Independent graph predicates cover an edge with noncontiguous
labels, an isolated vertex with invalid codes, an unsatisfiable self-loop and
an empty graph, with Boolean/phase/restoration checks under both policies.
Tiny superposition tests assert total oracle width <=5 before simulation.
Other coverage uses exact monomial permutation/phase tracking, not large dense
operators or statevectors. The selected existing statevector checks fit <=5
qubits; the selected dense operator check uses 3 qubits.

The earlier focused command was
`/Users/mar/codex-work/logique/.venv/bin/python -m pytest tests/test_native_contract.py -q`:
initially 86 passed/1 failed because the original fixture was below the pinned
refactoring MFFC-size threshold, then 87 passed after using an observable
four-gate fixture (`contract-tests.log`, `contract-tests-retry.log`). One further
old-bridge malformed-evidence regression accounts for the final 88 contract cases.

Intake compatibility build and comparison:

```bash
$NATIVE_CONTRACT_TOOLS/cmake -S "$NATIVE_CONTRACT_RUN/legacy-source" -B "$NATIVE_CONTRACT_RUN/legacy-build" -G Ninja -DCMAKE_MAKE_PROGRAM="$NATIVE_CONTRACT_TOOLS/ninja" -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_CATERPILLAR=/Users/mar/codex-work/logique/external/caterpillar
$NATIVE_CONTRACT_TOOLS/cmake --build "$NATIVE_CONTRACT_RUN/legacy-build" -j1
/Users/mar/codex-work/logique/.venv/bin/python "$NATIVE_CONTRACT_RUN/compare_legacy.py"
/Users/mar/codex-work/logique/.venv/bin/python "$NATIVE_CONTRACT_RUN/record_identity.py"
```

Result: **45/45** intake/new native comparisons match every legacy semantic,
structural, gate/wire and old action field. Only nondeterministic timing and
additive metadata are excluded. Inputs: `xor_and.v`, `and4.v`, `shared.v`, the
factoring fixture, constants/aliases with reordered/repeated output projection,
zero-input false/true constants, and pinned cached `ctrl.aig`, across all five
methods. Exact fixture hashes and per-case controls are in
`legacy-comparison.json`; logs are `legacy-comparison-final.log`,
`legacy-configure.log` and `legacy-build.log`. `legacy-source/` is an exact copy
of tracked bridge files from the intake commit, not a dependency checkout.

Static checks:

```bash
/Users/mar/codex-work/logique/.venv/bin/python -m black --check src/logique/synthesis/api.py src/logique/synthesis/native.py tests/test_native_contract.py
/Users/mar/codex-work/logique/.venv/bin/python -m ruff check src/logique/synthesis/api.py src/logique/synthesis/native.py tests/test_native_contract.py
/Users/mar/codex-work/logique/.venv/bin/python -m mypy
git diff --check
```

All passed (`black.log`, `ruff.log`, `mypy.log`). Mypy uses the repository's
configured five core files; it does not provide new static coverage of synthesis.
One numerical/compiler process ran at a time, builds used `-j1`, and no model
subprocesses, agents, environment synchronization, remote/API jobs or hardware ran.
The sandbox required escalation only for the authorized Git index/commit writes
in parent worktree metadata; those succeeded.

## Limits and next action

The public bridge still exposes exactly `xag`, `aig_bennett`, `xag_bennett`,
`klut_bennett`, `best_fit`. In-place Bennett/eager and the low-T/low-depth XAG
classes exist in the pin but remain unsupported public controls. Their emitted
circuits were not certified by these serialization-only probes. The existing
`Network<Base>::is_nary_xor` shim still returns false; future level-based mapping
integration must audit its network representation and gate emission separately.
Pinned pebbling and solver headers are present (including Z3-guarded classes),
but this build does not enable Z3 or expose SAT/pebbling. Their compilation/link
feasibility was not tested or inferred. No new mapping/optimization profile,
balancing integration, MC reduction, SAT, or scheduling was enabled.

This bounded suite does not rerun the entire repository, notebooks, the 135-value
historical replay or full comparisons/scaling studies. The 27 deselections avoid
unneeded broader simulations/notebook execution; the changed constants/alias
contract receives exhaustive monomial checks and the new tiny quantum checks.
The native 45-case identity comparison supports preserved defaults without
claiming the archived experiment has been rerun. Larger-instance Boolean and
phase coverage remains the existing exhaustive/sampled contract, not general
formal equivalence. No precolored study was introduced. All histories, pins,
archived results and root/integration README changes were left untouched; the
worktree README matches intake bytes.

Next action belongs to the coordinator: review/cherry-pick the two implementation
commits and this checkpoint, preserve the private run directory before removing
the worktree, then select a separate mapping/optimization queue item and its
acceptance checks. No model launches or queue edits were made. Scientific approval,
FT acceptance and the paper evidence gate remain separate decisions.
