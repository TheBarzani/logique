# Independent bounded SAT mapping review

Task `native-mapping-review-1030020413`, reviewer session
`01a190d5-2d6e-7281-80ee-fb33cdaa5b7c`, 31 October 2026.
Assigned branch `codex/coloring-native-mapping-review-1030020413`, base
`e90adf3373236ef51a937480febd3cd7d669dce7`.
This assigned review is **COMPLETE**; the full paper remains open.

## Exact decisions

**Correctness/build: ADMIT `622b95001ffc68d569e4871a59821ae439c7cacb`**, the
seven paths below, for its explicit bounded ordinary AIG/XAG SAT mapping
contract. A new private serial build reproduces the exact candidate final
executable bytes. Independent semantic and adversarial checks support the
value/restoration argument below. This admission does not use the sequential
two-cone theorem as a proof of SAT schedules.

**Metric/evidence: ADMIT only bounded correctness/build observations** in
`8734910f7b3f001cdeca1d150477dd99b6ed88b0`, report SHA256
`e76ac37ae4ae067906468225a6a3c7af23735d8eed3eccf72d3e8e1ef7c5c851`.
The 24 saved generated responses and two recomputation responses were independently
checked against a separate parser/evaluator of their saved Verilog fixtures.
The worker's 423-test result is a verified saved log, not a fresh 423-test run by
this reviewer. Fresh reviewer results are listed separately below.

**BLOCK performance, optimality, larger-domain/CEC and full-paper claims.**
There is no matched qubit/T-count/T-depth benchmark study, global optimality
proof, unrestricted low-T/depth mapping admission, dirty-workspace raw oracle
proof, or general preprocessing CEC. No historical measurements are changed.
**BLOCK any claim of complete preservation of the first failed private build:**
the worker overwrote its first executables during diagnostics before saving their
identities. The acknowledged loss is real. It does not prevent reproducing and
reviewing the distinct final build, but cannot be repaired by a green test or
this review. Preserve the remaining snapshots, diagnostic binaries and logs.

Only the root integration coordinator may integrate exact admitted bytes. This
worker did not edit the candidate, integrate, push, or modify any queue/history.

## Source and build identities

Candidate worktree is the sibling `../native-mapping-sat`, clean at report HEAD
`8734910f7b3f001cdeca1d150477dd99b6ed88b0`. Each maintained source hash was
checked against both the worktree and `git show 622b950:<path>`.

| Path (relative to candidate) | SHA256 |
| --- | --- |
| `external/native/boolean_synthesis/CMakeLists.txt` | `fc3f3064755ff51b46c5c3594d2b16d1c1a95783c0ee2a394909631b0decfe4d` |
| `external/native/boolean_synthesis/include/mapping.hpp` | `06f128b1eb7c1d068ee37c50c39a5a2c2a70651bd3c8f4d5cbf3d4cef7a1333f` |
| `external/native/boolean_synthesis/include/sat_pebbling.hpp` | `29c744f676d61df24e84b39e2480325305fc5961216c0591136fb190d146ddd4` |
| `external/native/boolean_synthesis/tests/sat_pebbling.cpp` | `97ce46aa251d14e526395986122132d6f5d9a9c7da1871978444b2fef5bd15fd` |
| `src/logique/synthesis/api.py` | `f21548e0be71aa5e8efe55c73587705c0ffa1c46b40c1141da5717465c3d7d4d` |
| `src/logique/synthesis/native.py` | `e84fbfe8d09994f39b71d6ff91a1f3db2e2a882ce1185e22ff4d13b301b1f973` |
| `tests/test_native_sat_pebbling.py` | `0a3e4e9ba43a76e9c4a108bb422017b8fcd166faf5f86f9dd22b953908ad4cf1` |

Fresh evidence directory, created using candidate `logique.paths.new_dump_directory`
with an explicit reviewer-local root:
`dump/1031032135-native-mapping-independent-review/`.
The private build is `private-build/` inside it. It never replaced a binary.

Fresh and candidate final executable SHA256 both equal
`81bc6a786f29a5673881ef37c5fb0da02cec9d22a649b9d518d1b31db5d71571`.
SAT provenance SHA256 is
`b8c56a4bcc9c3dc6a235ad80e5cb4b2bc702f4a91e3f5c1e0d449ccd526c13ba`;
LHRS provenance SHA256 is
`5f07fd225e7f2eb74ca3925e808a32b312670cd328d583549e460889e7106b91`.
The same effective LHRS/best-fit overlays and effective solver/header/source
hashes match the candidate inventory. The five dependency gitlinks are unchanged.
Effective Caterpillar is pinned at `4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`.

Build commands use existing checkpoint CMake/Ninja, AppleClang 21.0.0, Release,
`-j1`, `LOGIQUE_BUILD_CONTRACT_PROBES=ON`, and explicit
`FETCHCONTENT_SOURCE_DIR_CATERPILLAR=/Users/mar/codex-work/logique/external/caterpillar`.
The exact commands, environment, exits, elapsed seconds and RSS scope are in
`review-commands.jsonl`. No download, full ABC build, dependency change or sync
was needed. CMake links the actual pinned bundled ABC `satSolver.cpp` and
`satStore.cpp`, with `LIN64 ABC_NAMESPACE=pabc`, to the native executable.

## Solver, action and value argument

The new implementation calls `caterpillar::bsat_pebble_solver`, whose Percy
wrapper uses ABC bsat2. I inspected its initial-unpebbled constraints, fanin
requirements on both sides of a transition, cardinality constraint, final
output-driver assumptions, model simplification and extracted action ordering.
It supplies a candidate schedule; its labels are not a correctness certificate.
The production emitter checks the extracted ordinary actions independently.

For the admitted domain, initialize distinct PI wires with their Boolean
functions and clean workspace with zero. All node truth tables are derived in
topological order, with explicit fanin/output complements. Every active node has
one distinct physical address. A free address contains zero. Every operand read
checks that the address exists and its physical table equals that node's table.

Compute takes a zero address disjoint from all live addresses. AND emits a
polarized exact controlled X; XOR emits exact CNOTs and complement-parity Xs.
The target table is checked against the graph function. These gates preserve
all other active values. Uncompute reads the current correct target and fanins,
toggles by the same function, verifies zero **before** releasing, and sets the
node address to -1. Recompute therefore cannot use a stale alias left by release.
Physical duplicate controls or target/control overlap reject.

Induction gives the value/free-zero invariant for **any accepted ordinary
schedule**, including recomputation, independently of the solver's optimization
or extraction correctness. An invalid extracted schedule fails closed. Buffers,
in-place/level actions, explicit leaves and cell overrides reject; no restoring
cone-frame interpretation or unproved richer action semantics is imported from
the prior sequential proof. This is a different, simpler state discipline.

At the boundary the emitter checks PI/used-constant/output values and rejects
remaining active non-output gates. Repeated output drivers receive distinct
copies with polarity corrected relative to the first occurrence. A first
complemented PI output can change that input in the raw computation. It is not
an input-restoring raw XOR oracle. Actual compute/copy/emitted-inverse and
compute/Z/emitted-inverse wrappers restore inputs and every computation wire.
All emitted primitives here have phase +1; checking all basis columns and all
joint XOR-target values establishes coherent linear action on the tested clean
workspace subspace, including arbitrary input/reference entanglement by linearity.
It does not establish dirty initial computation-workspace behavior.

## Actual limits and counterexamples

The public path requires four positive integer controls; bools reject. Maximums
are 64 raw wires, 128 SAT horizons, 100,000 conflicts per solve and 30 search
seconds. The emitter checks inputs<=6, gates<=32, nodes<=64 and outputs<=16
before its truth-table, node-map and solver allocations. Tables occupy at most
64 bits each. The action cap is 4096. These are mapping-domain limits, not a
hard memory cap for arbitrary input parsing or preprocessing.

The width includes declared unused inputs, used constants and output copies.
External XOR targets are additional. The solver receives the remaining gate
pebble budget after fixed wires; the emitter checks actual width again during
allocation/output preparation. A model needing excessive physical width can
reject. Completeness and minimum width are not promised. Zero-gate networks
bypass the solver's zero-variable case.

The solver ignores its timeout parameter. Native checks occur before and after
conflict-bounded solves; **one direct native solve has no wall interrupt**.
Python enforces `sat_time_seconds + 1` for the whole subprocess. The 70-test
fresh run includes the real sleeping-child timeout, not merely a mocked timeout.
Direct JSON callers must impose an external deadline. Horizon exhaustion and
unknown/conflict exhaustion are not unbounded infeasibility proofs. No new
experiment established worst-case solver runtime or a hard memory ceiling.

Concrete observed failures and limits:

- The preserved diagnostic binary, SHA256
  `b153f153436a345b8a4ef16092a9e5496b62f2eb5736e8efbd158fb4be7a212a`,
  fails `p=a&b; y=p^c` with `node=0 address=-1` after a valid three-action
  schedule. The final source excludes constants before the PI boundary check;
  the exact same fresh request passes on the reviewer build. Original CTest
  failures and the worker's eight-failure focused log were read and retained.
- For `p=a&b; q=p^c; r=a^c`, the adversarial schedule compute(p), uncompute(p),
  compute(r), compute(q) tries to read p after its physical wire was reused.
  The production emitter rejects `node=4 address=-1`. An inverse of q with p
  absent also rejects. Correct release/recompute of p succeeds with three
  verified zero releases in the direct probe.
- Keeping p live at the q-output boundary rejects dirty non-output workspace.
  Cell overrides, explicit empty inverse leaves and all five richer action
  alternatives reject. These are checker challenges, not accepted native
  counterexamples.
- An output-alias/constant fixture with four inputs and five outputs rejects a
  six-wire budget; duplicate copies cannot escape the total width limit. Too
  few input/gate wires, one horizon, invalid control values and an unsupported
  method also reject. The separate CTest checks the 33-gate preallocation cap.

No accepted wrong-value/restoration counterexample was found in this bounded
review. Equal/opposite parity behavior is checked without accepting duplicate
physical controls; raw complemented-input behavior is explicitly distinguished
from restoring wrappers.

## Independent execution and evidence scope

The new probe evaluates its generated straight-line Boolean programs independently
of native networks. It interprets native gates and actual Qiskit instructions
directly, using neither worker test helpers nor `_qiskit_records` nor simulator
arrays. It checks every declared input assignment, every joint XOR-target pattern,
each phase output, zero non-output workspace, inverse restoration, distinct
wiring, and logical liveness of each extracted action.

| Check | Fresh result | Supervised seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Private configure/build | pass | 0.335 / 19.480 | 37,355,520 / 854,704,128 |
| Independent semantics | 100 schedules pass | 2.803 | 69,107,712 |
| Candidate CTest | 2/2 pass | 0.459 | 12,566,528 |
| Independent action probe build/run | ten rejections and valid recomputation pass | 3.392 / 0.220 | 548,061,184 / 1,802,240 |
| Candidate SAT regressions | 70 pass, no skips | 3.062 | 80,920,576 |
| Exact identities/saved evidence/defaults | pass on second audit | 0.940 | 67,895,296 |

The 100 schedules cover 25 sources across both representations and both common
preprocessing policies. Twenty sources are generated with seed **1031032135**;
five target constants/unused inputs, output aliases, equal/opposite parity and
forced recomputation. The four-AND/five-input case uses eight raw wires and
actually recomputes under `none` for both representations.

The 26 worker saved responses have verified response/input hashes; their expected
tables were independently recovered from the saved source grammar. Fresh exact
protocol comparisons on two additional fixtures give **30 matches** across all
five existing methods and omitted/none/refactoring policies. Only `native_seconds`
and the earlier-added `mapping_strategy` field are excluded. The comparison uses
the prescribed foundation binary with verified SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the root old default is never substituted.

`independent-identities.json` records all checked source/build/evidence hashes,
the worker's actual four nonzero command receipts and its 115.620288 cumulative
supervised seconds / 913,752,064-byte maximum high-water. Saved worker broad
regressions show 423 passed/27 deselected, not a full-suite admission. My own
checks before formatting used 31.135050 seconds including a failed audit.
Final totals and exact review commit are recorded in `checkpoint.json`.

The first reviewer identity audit stopped because `None` and `none` in log names
collide on this case-insensitive filesystem. Exclusive writes prevented overwrite;
the log, source snapshot and partial receipts remain. The corrected audit uses
fresh names and `omitted`, then passes. An initial Ruff check found one unused
import; its log remains and the corrected check passes. Formatting-only changes
are checked against executed source snapshots. The interruption occurred after
the previous commands completed; no numerical job was left running.

## Resources, preservation and follow-up

Declared before execution: serial compiler/numerical children, 120s per child,
**300s cumulative including builds**, 2 GiB declared process budget; all relevant
compiler/BLAS/OpenMP/Accelerate/Rayon/Qiskit parallelism is one. The supervisor
kills/reaps a timed-out process group. RSS is Darwin wait4 child high-water,
possibly including reaped descendants, not simultaneous group RSS or a hard cap.
No statevector, density matrix or dense Operator was allocated in this review.
The original staticFT dense-four limit remains untouched.

Only `/Users/mar/codex-work/logique/.venv/bin/python` was used, with explicit
candidate `PYTHONPATH` and asserted imports for semantic/evidence execution.
AGENTS.md, CLAUDE.md and the entire plan were read, along with the hard-bound
handoff, current root continuation document (absent on this base), actual
sequential/low-T/in-place reviews, candidate report/checkpoint/source and solver.
Truncated combined reads were followed by focused reads. Two guessed checkpoint/
handoff paths were absent and resolved to the actual files; these were inspection
failures, not scientific results.

README, pins, histories, archives, candidate evidence and old failures were not
edited by this reviewer. No models/subagents/Codex subprocesses, paid/API fallback,
hardware, physical QEC, precolored or conditional-workspace research were launched.
Only this new report and distinct independent probe/supervisor files are committed.

Next: `native-mapping-integrate-1030020413` may integrate exact admitted source
bytes and this bounded decision, independently resolve/re-review overlap in
CMake/mapping/API with the native-value and profiles chains, build privately,
and validate integrated source. Conflict resolutions are new bytes, not covered
by this exact-source admission. Preserve the first-build loss qualification and
all failure/partial receipts. Broader mappings, larger-domain validation/CEC and
matched qubit/T-count/T-depth studies need separately budgeted implementation,
execution and review; neither task completion nor this ADMIT supplies them.
