# Independent whole-circuit MCX review

Task `mcx-whole-review-1030020413`, session
`01a19353-3d01-7023-a645-2743119b6442`, is **COMPLETE**.
Review branch: `codex/coloring-mcx-whole-review-1030020413`;
base `e90adf3373236ef51a937480febd3cd7d669dce7`.
Candidate worktree is the sibling `mcx-whole-circuit`; its clean, unchanged HEAD
is **`751a4eb70eb31d54005410a11153d7d97187a927`**.
Fresh independent evidence: `dump/1031145904-mcx-whole-independent-review/`.
No candidate edits, integration, model launches, builds or pushes occurred.

## Decisions and exact identities

| Slice | Independent decision |
| --- | --- |
| Correctness/harness | **ADMIT** exact `dc304e9969856f4332fe7f0fba9c18f491c2ba2b` plus `865deab66564dfbe8807ca3e7c46d8ec0d13c222`, limited to the opt-in construction and bounded evidence below. No discovered source blocker. |
| Build | No changed bridge or build to admit. Existing native executable identity verified; no new build/provenance certificate. |
| Metric/evidence | **ADMIT** the selected 1,608 completed rows as explicit representation/resource observations with the stated semantic coverage, exclusions and unpriced rotations. This is independent review of saved artifacts, not inference from queue success. |
| Checkpoint prose `751a4eb` | **BLOCK verbatim reuse of “Clean policies allocate zero scratch”.** The correct statement is “Clean policies allocate **zero-initialized** scratch.” For example clean_tree at four controls appends two wires. Preserve the original checkpoint and attach this erratum; this is not a circuit or numerical-result defect. |
| General scientific claims | **BLOCK** all-width phase/restoration certification, full nine-graph comparison, strongest-baseline superiority, routing, total FT costs/precision, physical QEC, RUS, and full-paper admission. These were not established by this task. |

| Candidate path | SHA256 |
| --- | --- |
| `src/logique/benchmarks/mcx_study.py` | `7518d7c164ebb8e307e08ed284bea79194286c70813a885dcb8afad2e9d2371e` |
| `tests/test_mcx_study.py` | `ca1009fada74377c961ee47e1311f2e0bc2b4c7836b6b35cfd5d5de47862a002` |
| `tools/run_mcx_study.py` | `322897eb72a1eb53804d7361831bd8753ff10c0c17c953b9a203bec6f655af4d` |
| `MCX_WHOLE_CIRCUIT_CHECKPOINT.md` | `46ab570febc88fb6acb03195a92f99c2ae4a221a0c4b7d8377b29e0c72db6143` |

Reused `costs.py` remains
`42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8`;
`coloring_study.py` remains
`457389f1fad1ce8f87fe0e6a1a640a62ce77d8c419c0e3165b63af9c90b639d7`.
The existing binary is explicitly
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`,
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Root's old default was not selected.

Read AGENTS.md, CLAUDE.md and the entire 723-line revamp plan, both requested
handoffs (the October 30 document from root because absent at this base), actual
candidate checkpoint/code/tests/runner, original failed logs, execution receipts,
prior restoring-MCX review/admission, reused lowering/assembly/record sources,
and installed Qiskit MCX/Gray/statevector implementation. Earlier admissions
are context, not blanket admission of these new policies.

## Construction and independent semantics

The template probe calls the candidate lowering entry point but obtains expected
action from integer bit permutations and conjunctions, not worker verification
helpers or an ideal Qiskit MCX matrix. It checks all eleven policies, every
control polarity at three/four controls, and polarities 0, 1, all-ones-minus-one
and all-ones at five/six controls. Wires are reversed to exercise control order;
both target sectors, all original spare wires and an untouched reference occur
in a seeded arbitrary complex input. Appended clean scratch alone starts zero.
The reference is added after lowering so cannot be borrowed.

**352 forward and 352 marked-actual-inverse checks pass.** The forward throwaway
expectation explicitly computes its held conjunction bits, including open-control
conjugation, rather than ignoring garbage. Global phase 0.219 is retained.
Dirty constructions restore the borrowed joint state, including its reference
correlations. The four Khattar–Gidney constructors are exercised through their
actual emitted gates, including their ladder/toggle-detection branches. This is
numerical evidence through six controls, not an exhaustive operator proof at
3..20 controls. Statevectors are at most 16 qubits in this template probe.

Clean-tree correctness also has the usual compositional explanation: its
relative-phase conjunction prefix preserves original controls and external
target; the exact final CCX changes only the external target; the actual prefix
inverse restores conjunction wires and cancels phases. Throwaway uses fresh
conjunction wires per source MCX. A monomial source prefix maps basis states to
basis states with phases, so its extra garbage cannot change the computed bit.
A diagonal mark followed by its actual expanded inverse cancels those phases
and garbage. This transfers valid source predicates; it does not validate an
arbitrary unverified backend or justify interference inside the prefix.

The current code retains controlled-Rx(+/-pi) source boundaries before throwaway
substitution. Reproducing the old flat-record path gives **“Cannot track phases
for cu”**, matching the preserved xag failure. The current path passes. A first
review fixture incorrectly expected that particular expansion to fail numerical
semantics; its observed error was only 7.15e-17, so that assertion and log remain
as a **reviewer-probe failure**, not evidence against the candidate.

Two genuine negative controls show why the restrictions are needed:

- MCX(0,1,2 -> 3), then H(0), then a Z(0) mark and inverse: unrestricted
  throwaway substitution differs from the original by **0.27607174652208605**
  maximum amplitude error on the saved seeded input. Current `lower_block`
  rejects this nonmonomial prefix.
- MCX(0,1,2 -> 3), MCX(0,2,3 -> 4), then replaying the same lowered forward
  block as its inverse gives **0.15829751411695958** error against identity.
  Actual inversion is necessary when controls change.

Independent saved-circuit checks cover **all 1,335 whole cases whose oracle and
search widths meet the worker's <=18 limit**. Each oracle receives a seeded
arbitrary complex data input and is compared to an independently decoded
complete coloring predicate (R1/R2) or edge-only predicate (R3), with every
non-data output amplitude required to vanish. Each saved diffusion is checked
on an arbitrary data input against `2 a <a|v> - v`, where a is constructed
independently from original-k valid codes or all binary codes. Each signed zero
reflection is checked against +1 at zero and -1 elsewhere. Thus the unmirrored
marking and diffusion restoration are exercised beyond the worker's uniform
oracle input. No global-phase alignment is performed.

There are **4,005 such component checks**, plus **55 fresh j=2 complete searches**
(all policies; xag, k-LUT, best-fit, sb_balanced, parallel structure). Their
expected states use an independent amplification recurrence. Maximum final
semantic error is **6.78327188658573e-15** against tolerance 2e-10.
The earlier saved semantic pass additionally checked four oracle/diffusion
components whose complete-search width was excluded; those remain separate,
not four newly admitted full-search cases. Worker j0/j1/j2 regressions also run.

Native raw remains a possibly phased/garbage-bearing computation; its new
wrapper is raw/Z/actual-raw-inverse. Baseline/structure assembly uses the actual
expanded initializer/compute prefix, restoring final conjunction, actual prefix
inverse, then the verified kickback preparation/cleanup. No raw/direct-kickback
advantage is inferred. For throwaway, A, S0 and unmirrored final conjunction
explicitly substitute clean_tree. A is emitted once, its actual inverse is used,
and the signed reflection is `A(2|0><0|-I)A†`. R3 only supplies the complete
coloring service on valid-color preparation support.

## Saved measurements, workspace and allocation guards

The independent recount loads and hashes **26,676 QPY representations across
8,892 components**, recomputing gate maps, width, dependency depth, T/TDG counts,
T-depth, Rz counts/depth and CX counts directly from emitted instructions.
Explicit/common depth retains zero-weight barrier synchronization; the partial-FT
helper's documented directive-excluding depth is checked separately. No cost
helper supplies the expected recount values. All match.

A further **396 cross-representation action comparisons** cover explicit versus
U/CX and partial-FT representations of six components, all policies, and xag,
sb_balanced and parallel structure on edge-k3/R2. Inputs are arbitrary complete
physical registers with an additional reference; this checks representation
fidelity, not a clean-scratch theorem on dirty clean pools. Maximum error is
**1.7702748954631059e-15**, without phase alignment. Wider translation equivalence
is not independently certified merely by recounting counts.

Reconstructing selection from driver/repair receipts gives exactly 55 shards:
44 bind to dc304e9 and 11 repaired triangle shards bind to 865deab. Every saved
source hash agrees with its recorded Git commit. All 1,452 whole request input
hashes are verified. All 33 original sb_original failures remain; their fresh
rows correctly exclude the known multiple-higher-neighbor source limitation.
All **7,920** corresponding successful QPY hashes are unchanged. No original
failed row is promoted into a completed measurement.

The selected ledger has 189 isolated and 1,419 whole completed rows, nine Gray
and 33 baseline exclusions. **84 whole cost rows retain excluded full-statevector
validation**. Controls above six have no new independent full-state semantic
certificate from this review; above-four worker rows were already qualified as
representation/cost observations. Dutta remains an unchanged analytical helper:
34 theorem-range rows and 20 exclusions, no emitted circuit or static-unitary
T certificate. This review does not independently resolve the retained published
depth discrepancy or rederive that external theorem.

Workspace accounting is construction capacity, not process memory or backend
liveness. Restoring scratch can be reused at each gate boundary. Throwaway
scratch is held once until the actual inverse. Prefix-held garbage therefore
**adds** to the simultaneous restoring conjunction scratch; it is not doubled
for the mirror. Sequential A/oracle/S0 use their maximum; j0 uses A only despite
reserved unused pools. The recount checks these equations, disjoint physical
pool ownership and every selected row's metadata. Code inspection confirms
marking excludes the appended prefix pool, while dirty templates may borrow
other original wires without assuming their values. Optimized/routed/backend
live peaks remain unavailable. The checkpoint's zero-scratch sentence is false
literally; only its zero-initialization interpretation is admitted.

Gray preallocation is correctly scoped to the selected constructor/block.
Reading the installed chain shows at most n-1 CX and one CU1 per nonzero Gray
string; CU1 contributes three phase and two CX instructions. The bound
`(n+4)*2**n+2` is conservative. Nine n=12..20 requests and a two-n11 aggregate
are independently rejected while the selected constructor is replaced by a
failing sentinel. n11's saved forward common circuit recounts 12,283 operations
and 6,140 CX; its bound is 30,722. n12's 65,538 exceeds the frozen 50,000 cap.
The bytes/throughput coefficients are planning assumptions, not memory/time
limits. Definition resolution precedes selected-policy construction; its visit
bounds do not hard-bound arbitrary Qiskit internal definition allocation.
Admission concerns these bounded sources, not a general hostile-input allocator.

The four diagnostic comparisons against clean_tree reproduce **1,411 wins,
1,194 losses and 2,555 ties**, not 5,160 independent experiments or superiority.
Known-T savings are not total FT savings: residual Rz is unpriced, total T-count,
total T-depth and precision stay null; routing has no target/calibration identity.
No component T-depth sum is substituted for full-search dependency depth.

## Checks, failures, resource scope and handoff

Existing `/Users/mar/codex-work/logique/.venv/bin/python` only; explicit candidate
PYTHONPATH with asserted module paths. Numerical children are serial, <=120s each,
with a cumulative 300s budget. OMP/BLAS/MKL/NumExpr/Accelerate/Rayon/Qiskit/CMake
parallelism is one; QISKIT_PARALLEL is FALSE. Plan was saved before arrays:
2GiB declared process budget, statevector<=18, denseOperator<=5, at most ten
planned 4MiB vectors. Independent scripts use no dense Operator; the candidate
local-gadget regression uses three qubits. StaticFT's dense-four pilot is untouched.

Through final identity freeze, **92.690846 seconds** were supervised, including
all failed probes and formatting; longest child **44.889288s**, largest terminal
child high-water **160,071,680 bytes**. RUSAGE_CHILDREN on Darwin may include
reaped descendants; there is no hard cap, live/group memory enforcement or
claim of complete process visibility. Seeds are 1031/1032; worker seed7 and its
saved template seeds are unchanged. `commands.jsonl` retains argv, cwd, exit,
time, timeout and RSS scope; `plan.json` retains environment, hashes and limits.
`batch.json` binds snapshots/results and records the immediate follow-up.

The exact candidate command was existing Python plus
`-m pytest tests/test_mcx_study.py -q -p no:cacheprovider --basetemp <review-run>/pytest-tmp`:
**195 passed**, no skips. Independent final template, graph, edge5, recount and
identity checks pass. Three formatted review scripts have AST identity to their
executed copies. No full suite, rebuild, notebook, historical replay, target
routing, noise, rotation synthesis or full-paper validation is claimed.

Reviewer failures are retained, not hidden: relative run-path lookup failure;
the incorrect negative-fixture expectation described above; initial recount's
omitted barrier synchronization; and two representation probes with a shared
NumPy input. Installed Qiskit's circuit evolution applies global phase in-place
on shared Statevector storage, so repeated inputs must be copied. Explicit
copies remove the spurious discrepancy; final semantic passes were rerun with
that correction. Prior scripts, partial results and distinct logs are preserved.
No candidate scientific failure is inferred from these probe defects.

Candidate source/README/lockfile and evidence identities were rechecked unchanged.
No old128 run, queue, history, archive, dependency pin, failed artifact or existing
review was edited. The continuation queue was read only (max_batches128,
Nov2 00:00 local deadline); queue state is not scientific evidence or a fresh
allowance determination. No API, paid fallback, purchases, hardware, precolored
or conditional-workspace research occurred.

Next: root coordinator may integrate the exact admitted source/tests/tool bytes,
validate their overlap with its current source, and keep the metric/evidence
ledger separate. Preserve the original checkpoint and publish the scratch
wording erratum above rather than silently editing its historical record.
Any semantic conflict resolution requires renewed exact review. Larger-template
semantics, wider translation validation, nine-graph comparisons, routing and
priced rotations require separate authorized work. Dispatcher alone publishes
integration HEAD. This review ends complete; the full scientific gate remains
BLOCKED.

Administrative preservation: initial staging failed with exit128 because the
shared worktree index is outside the writable sandbox. Its exact error is saved
in `git-stage-denial.json`; scoped automatic escalation then staged only the five
named review/probe files. No automatic approval-review rejection occurred.
