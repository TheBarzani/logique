# Independent capped native value review

30 October 2026. Task `native-value-review-1030020413`, session
`01a18eaa-ef78-7981-b077-daf6a532eb63`, dispatcher-approved Astra/high/Standard.
Assigned review **COMPLETE**. Whole candidate integration **BLOCKED** on the
Python/native certificate handshake described below. This is a concrete
compatibility counterexample, not a rejection of the two-cone proof or a
wrong-output counterexample for the new private binary. Full paper remains open.

Review branch `codex/coloring-native-value-review-1030020413`, intake
`e90adf3373236ef51a937480febd3cd7d669dce7`. Candidate worktree is the sibling
`native-value-validator`, HEAD `35618f44f0cd529a10556314f113f1bf16b66f2b`.
Fresh evidence `$RUN` is this review worktree's
`dump/1030214922-native-value-independent-review/`, created through candidate
`logique.paths.new_dump_directory`. Only this new report and
`tools/native_value_review_1030020413.py` are tracked review outputs.

## Exact decisions

| Object | Decision and scope |
| --- | --- |
| Inherited `e2d054b53008b70d15e591bc4dbf1bdc11fd2aaa` | **No blanket admission.** Its physical-literal normalization is valid for a distinct target; retained stack audit alone is insufficient. Its Python boundary is part of the defect below. |
| Correctness `3f73c324f0ebc8b0fa066e681634c352bd66058d` on that ancestor | **ADMIT the C++ validator/mapping composition within its explicitly checked domain**, when executed using the exact new private build. This is component admission, not permission to integrate the whole inherited Python/source chain. No admitted support above the caps. |
| Build `a8a53a5888d4cd1c3449cd2403611aa23a838d7f` and private binary | **ADMIT build/provenance** for the reviewed Release/NDEBUG sequential implementation. No rebuilt default, dependency update, Debug execution, or new independent compilation is claimed. |
| Full offered chain through `35618f4` | **BLOCK production integration** until the public Python boundary requires the new validator protocol and rejects old/missing/malformed certificates. The checkpoint-only commit is evidence, not source admission. |
| Semantic evidence | **ADMIT only the exact bounded correctness observations** below: 50 saved and 28 fresh responses, scalar clean-workspace XOR/phase checks, boundary-cap diagnostics. Worker cone/mutation results are corroborating source-reviewed evidence, not independent new coverage. |
| Research metrics/evaluation | **BLOCK** any performance, low-T advantage, free AND inverse, large-instance, FT/RUS, unrestricted mapping, or paper claim. No new research-metric commit/table is offered. Logical gate emission is static X/CNOT/Toffoli. |

## Concrete production-boundary counterexample

`src/logique/synthesis/native.py` checks the requested strategy implementation,
step list, physical-normalization list and old stack-audit policy. It never
checks `xag_value_validation`. `api.py` immediately builds the circuit from that
accepted response. Both files remain the exact inherited `e2d054b` bytes.

Fresh `seven-input.v` declares seven PIs `a,b,c,d,e,f,g`, one output, and
`y = a & b`. With `method=xag_bennett`, `strategy=xag_low_t`,
`preprocessing=none`:

* New binary `8941c1dc...` exits **1**, diagnostic
  `xag_low_t value validator: unsupported: inputs exceed 6`.
* Preserved old alias-fix binary
  `a36f421af12d3fae539afdef91a82356f421935bcb2dccd7687b0760f729d1b2`
  exits **0** and returns seven inputs with **no** value certificate.
* The **actual candidate Python `run_native`**, explicitly pointed to that old
  executable, returns the response successfully. A separate missing-certificate
  mutation of a real new response also passes the boundary.

See `protocol-results.json`, `seven-input.request.json`, `seven-api-response.json`,
both exact native stdout/stderr files and receipts. The old executable was used
only for this historical compatibility diagnostic, never to admit above-cap
scientific results. The prescribed unchanged-experiment binary was hash-checked
and not replaced. This counterexample does not allege that the trivial AND
function is wrong: the broken guarantee is mandatory capped value validation.

Required follow-up: add an explicit version/policy handshake for
`canonical_sequential_two_cone_truth_tables_v1`; require valid certificate
structure, exact supported caps and consistency with actual input/node/width/
step counts. Missing/unknown/inconsistent certificates must fail before circuit
construction, and actual above-cap counts must reject. Test the old real binary
or its exact saved response, absent/malformed/wrong-policy/wrong-count/wrong-cap
responses, and a valid new response. Update the maintained API/native protocol
documentation to state the bounded domain (the implementation checkpoint alone
is not public API documentation). Preserve all old bytes and evidence. Obtain a
new exact-source independent review of that correction; no blanket re-run of
completed research is needed. The root coordinator owns conditional integration.

## Proof preconditions and implementation audit

I read AGENTS.md, CLAUDE.md and the entire 723-line plan, the full 29 October
bound handoff, and the full 30 October continuation at the authoritative root
path (absent on this review base). I read the committed new checkpoint, actual
changed sources and wrappers, original blocker report, `8b1d22c` alias review,
`e911a13` checkpoint, and `92784ef` proof and relevant pinned strategy/LHRS code.
The new validator does not inherit unrestricted acceptance from those reviews.

`Domain` checks <=6 PIs, <=256 stored nodes and <=256 outputs before its
graph-sized containers. It checks combinational status, canonical consecutive
PI order, live stored nodes, a zero constant, strictly earlier nonconstant
binary fanins, distinct logical children and uncomplemented XOR children. Gates
must be reachable from the selected outputs. These enforce the cleaned,
construction-topological domain required by `92784ef`; unused PIs remain.
AND-edge and output complements remain explicit. Stored gate order, rather
than serialized DFS order, controls the schedule.

The frontier symmetric difference stops at PI/AND/output-driver boundaries.
The smaller-first inclusion rewrite, singleton special case, equal-frontier
buffer and reverse cone order agree with the pinned `get_cones/gen_steps`.
Compute blocks occur in stored order; non-output AND cleanup occurs in reverse.
Generated steps are appended with the 4096 limit; allocation/free-list
cardinality and output copies determine the exact width <=256 **before** the
truth-table evaluator. `expected` rechecks all four caps before its shift/table
allocation. At six inputs the 64-bit full mask avoids shifting by 64. These
are validator allocation guarantees: source parsing, selected-network copying,
cleanup and optional refactoring run earlier and are not globally memory-capped.

The independent `f_n` uint64 tables and physical `W[q]` tables check actual
ordinary fanin and CNOT control reads. `top` is only an address/generation check;
the skipped parity target is deliberately not a Boolean operand during restore.
`read` checks value equality. An ordinary uncompute must leave zero before
release; reused wires must still be zero. Forward/restoring frames check the
saved target value, and block exit checks active boundary values, addresses,
distinctness and zero on all other allocated wires. Equal physical literals
reduce to one literal; opposite literals emit no gate. Target aliases reject
before this normalization. No invalid duplicate-control gate gets a unitary
interpretation.

Empty internal parity is permitted only in the tested Release/NDEBUG path.
Its restoring compute allocates a second zero wire rather than freeing the
first. The frame admits the different zero-wire address; the full boundary
check still rejects garbage. Debug source explicitly rejects empty internal
frontiers before the pinned assertion; no Debug build admission follows.

The expected schedule, action audit and final stacks are compared to the
pinned audit, and expected steps/gates/width/input/output addresses are compared
to actual LHRS emission. A valid stack generation is never treated as a value
certificate. Pre-output checks happen before a first complemented output may
flip a PI. Repeated outputs allocate/copy from that first polarity and correct
relative polarity; all final outputs are rechecked. Input restoration is not
promised for the raw complemented-PI circuit. Actual compute/copy/emitted-inverse
and compute/Z/emitted-inverse wrappers restore computation workspace and inputs
for clean initial scratch. Scalar +1 permutation gates and the selected Z sign
give coherent action by linearity, including arbitrary joint target/reference
states within that clean-scratch contract. Dirty initial scratch is excluded.

## Independent execution and retained stale-alias counterexample

The new reviewer probe imports no worker tests, verification helpers, gate-record
reader, or earlier invariant probe. It evaluates sorted network IDs itself,
replays allocation/actions/control reads/zero releases and output preparation,
and compares the entire reconstructed gate list, width, outputs and stacks.
It separately interprets actual Qiskit operation objects from the real
`SynthesisResult.oracle()` and `phase_oracle()` methods, including control
states, emitted inverse and scalar phase. Each input/joint target and each
selected phase output is checked; no statevector or dense operator is allocated.

* All **50 saved final-build responses** pass: **6,976 wrapper columns** and
  **63 zero releases**. Their node truth tables and certificate entry/exit/frame
  values agree with the independent graph evaluator. Each response is hashed.
* **28 fresh real responses**, both none/refactoring, pass **17,664 wrapper
  columns** and **74 zero releases**. Twelve independently generated 18-node
  source DAG specifications use seed **1030020413**, six PIs in asymmetric
  `c,a,b,unused,d,e` order, complemented edges and multiple outputs. Direct
  source functions agree with returned graphs and actual wrappers. Two further
  fixtures exercise the original equal/opposite-cone failures under both policies.
* Fresh width diagnostics use three inputs and repeated output copies: 253
  copies yield **width256 and acceptance**; 254 copies require width257 and
  reject; 257 outputs reject at the output cap. Seven-input new-binary rejection
  is tested separately. These are boundary tests, not width256 state simulations.

The original duplicate-control failures are exercised rather than bypassed by
forced refactoring: none-policy equal cones emit a legal single-control action;
opposite cones emit identity. The fresh equal fixture also preserves the
**stale-but-unread alias**. Nodes8 and10 both represent `c XOR a XOR b`, with
truth mask `0x9696969696969696`, but after restoration both alias wire0 whose
mask is `0xaaaaaaaaaaaaaaaa` (c). Their final stacks are `[0]` and `[0,0,0]`.
At assignment integer2, the node function is1 and wire0 is0. This is the same
kind of counterexample as proof92784ef's nodes7/9; those original artifacts
remain intact. It refutes an always-valid-stack invariant without indicating
wrong output. Subsequent actual operand reads require a newly prepared value.

## Exact provenance and resource limits

`identity-results.json` binds all13 changed paths to exact `35618f4` Git blobs.
Key SHA256s:

| Artifact | SHA256 |
| --- | --- |
| New validator header | `9120bdec631307c5d09ee59770b6300f694eb185f343d1af758265292dd33d3d` |
| Mapping header | `dc18451d5ae61e4c343e17a17f6b42b17acacbbd4c00f2854807a54ae061f946` |
| Physical controls/audit header | `75c15af82adc2ec11e35af684e9e4e93ee6088199edb0498245e7d5c6e56365c` |
| Python native boundary | `f8b9233f697b9c332162a4eda950bf63904d546265d4bf331844314dd8a6c65c` |
| CMakeLists | `1822429c57e0d7bb4bd293d1241dfb2e891703d146384978b7374359801c2d36` |
| Private executable | `8941c1dcfbede0e570ac02d252f5d0de845e8068df65778c3e8d9b18327e0fc0` |
| Candidate committed checkpoint | `db1022f00fb001bd921152c6dd6439d6fa87c2d8de7ab4f1a6ca54741863aaf7` |

The private executable is candidate
`dump/1030170047-native-value-validator/canonical-build/boolean_synthesis`.
I independently resolved the three compiler depfiles and matched their exact
union to all **1,141** recorded effective dependencies, then hashed those bytes.
The final executable, both compiled probes, CMake cache, compiler command list,
build provenance and all **310** indexed evidence artifacts match. Candidate
command logs match their recorded hashes. Five Git pins and actual dependency
HEADs match. The preserved pinned strategy hash is `6980dd08...c89127` and
effective LHRS overlay `edd39ec5...3cbe7b9`, exactly as in92784ef.

The build uses explicit local pinned Caterpillar, C++17, Release `-O3 -DNDEBUG`,
AppleClang21 and serial `-j1`. Existing stack-pop/best-fit overlays are unchanged.
The new three-line CMake change adds only the value probe target/test. This
audit establishes saved build provenance; it is not a new reproducible-build
experiment. The candidate's unavailable first transient development binary
remains a documented historical limitation, not the admitted executable.

All review checks use existing `/Users/mar/codex-work/logique/.venv/bin/python`,
explicit candidate PYTHONPATH with import assertions, and one compiler/BLAS/
OMP/Accelerate/Rayon/Qiskit process/thread. Declared **2GiB process allocation
budget**, **120s outer child**, **300s cumulative independent checks**, and
**10s direct native children**, before allocation. No statevector/dense arrays,
installation, sync, native rebuild, model/subagent, hardware, paid/API fallback,
queue edit, integration or push occurred. Maximum observed wait4 child high-water
was **67,616,768 bytes** in the semantic probe; it is not simultaneous group RSS
or a hard memory cap. Exact final cumulative seconds and receipts are in
`checkpoint.json`; native children are nested inside and not double-counted
against outer charged time. Scalar source inspection/Git bookkeeping is excluded.

Retained reviewer failures: first evidence-index audit resolved the top-level
checkpoint against the dump directory (exit1); corrected resolution passes.
The first formatting supervisor invocation rejected `-m` before spawning a
child (exit2, no child RSS receipt); a failed quotation-style patch was atomic.
The corrected supervisor preserves command arguments. Initial Ruff found one
ambiguous loop variable, fixed with final Ruff passing. These are review-tool
failures, not scientific failures. Sources/logs/receipts remain. Earlier quota
interruption is not a failed mathematical attempt. Initial missing older-base
document reads and truncated displays were followed by authoritative/focused
reads. No automatic approval rejection occurred.

README, pins, candidate source/build/evidence, prior reviews/checkpoints,
histories, archives and failed artifacts remain unchanged. This review finishes
its assigned task. `native-value-integrate-1030020413` must retain the whole-chain
BLOCK and arrange the small protocol correction plus exact independent review;
only the root coordinator may integrate admitted bytes, and only the dispatcher
may publish integration HEAD. No need to poll or relaunch this completed review.
