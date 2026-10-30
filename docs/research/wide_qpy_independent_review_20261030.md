# Independent wide-MCX QPY review — 30 October 2026

**Review COMPLETE. Correctness ADMIT for the exact paired candidate below, within
its bounded serialization contract. Representation-label ADMIT; new comparative
research evidence BLOCK.** No candidate correctness counterexample was found.
This decision does not admit general transpiler equivalence, new comparison
results, FT synthesis or the full paper. The reviewer did not integrate or push.

Task `wide-qpy-review-1030020413`, session
`01a18d97-ca21-7b13-a437-0003985bff69`; dispatched `gpt-6-astra`, high, Standard.
Review branch `codex/coloring-wide-qpy-review-1030020413`, base
`e90adf3373236ef51a937480febd3cd7d669dce7`. The assigned review worktree is the
sibling of the read-only `wide-qpy-fix` candidate under
`dump/1030020413-full-scope-continuation-coordinator/worktrees/`.

Fresh independent evidence: this worktree's
`dump/1030121648-wide-qpy-independent-review/` (RUN), created by
`logique.paths.new_dump_directory` in local time. Tracked executable probes:
`wide_qpy_independent_probe.py`, `wide_qpy_independent_regressions.py`,
`wide_qpy_independent_audit.py`, `wide_qpy_independent_supervisor.py`.
The supervisor records exact argv, environment, exits, elapsed time, scoped RSS
and log hashes. `intake.json`, `audit-results.json` and `batch.json` bind source,
input, evidence and task identities. Original failed attempts remain in RUN.

## Exact candidate and separate decisions

Candidate correctness commit:
`574fa242cebc759648669efe35f5bbb556d81f65`.
Separate representation/metric-label commit:
`9049c7b758bb43ffc00f4db9bf23c4a284782302`.
Committed checkpoint HEAD:
`e040e9cd17371128e943d58a1a2abec1330fc0a5`.

| Exact final file | SHA256 |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `6ea7d188cb6a1727b549ebce95bcc1683b3c1c1af88e9d6158c48991d69ff80e` |
| `tests/test_coloring_study.py` | `5ea969ee8cd5c280e022e81133887a3755e4508b38d838cd24a3bc5a4de972a0` |
| `WIDE_QPY_CHECKPOINT.md` | `a80f1e5e814380b908c33c8588ff2d6a6aebcf9169caf275ebe524f2a7c144ac` |

**Correctness ADMIT:** integrate the final paired source/test bytes, retaining
both commit boundaries. The bounded MCX conversion preserves arbitrary-input
control/target action, ordered embeddings, scalar phase, actual inverse action
and scratch restoration under the standard-gate assumptions below. It handles
33..512 controls without truncation, extra wires, wide definitions or dense
expansion. Direct closed MCX31/32 remains intact. Existing restoring-MCX20,
definition-depth32 and unsupported-operation exclusions remain intact.

**Build decision:** no bridge, dependency, installed package or build changes
exist in this candidate. No new build admission is requested or granted. The
unchanged prescribed binary was hash-verified; no compiler/build was run here.

**Representation/metric-label ADMIT:** v2 serialization metadata, source-control
histogram, no-added-wire contract and distinct `mcx_method` correctly describe
the saved representation. Five synthetic export rows were independently
recounted from actual QPY. These are plumbing observations, not comparison data.

**Research-metric/evidence BLOCK:** no newly executed missing/clipped comparison
groups, strongest-baseline intersection, wide common-basis equivalence proof,
routed/FT table or superiority claim is present. The candidate changes logical
granularity: a closed MCX33 becomes263 saved operations. Neither that increase
nor any apparent reduction elsewhere is a research improvement. Preserve old
failed artifacts and measurements; do not silently pool v1/direct-MCX and v2
rows. The current comparison context includes `mcx_method`, so the new label
separates these rows; a missing matched baseline remains missing.

## Independent reasoning about arbitrary inputs

The candidate implements a controlled-P ladder, conjugated by H on the target.
For real theta,
`C^n P(theta) = C^n RZ(theta) * C^(n-1) P(theta/2)`, where the second phase acts
on the last control. Both factors are diagonal. Iteration ends with
`P(pi/2^n)` on the first ordered control. This last phase is essential, including
on inputs where the full conjunction is false.

For two disjoint conjunction values a,b and a target bit t, the two repetitions
of `RZ(theta/4), X^a, RZ(-theta/4), X^b` restore t. Their accumulated phase is
`theta*(t-1/2)*[1-(-1)^a+(-1)^(a+b)-(-1)^b]/4`, which equals
`theta*a*b*(t-1/2)`. Thus the block is precisely controlled RZ, with its scalar
phase retained. For one control the shorter two-CX identity gives the same
result. H then converts the complete controlled-P(pi) into the required MCX.

Every recursive larger X leaf uses a borrowed control d. A toggles d by a;
B toggles the target by b*d. Chronological ABAB produces target change
`b*(d XOR a) XOR b*d = a*b`, returning d to its initial value. The split
conjunctions are disjoint. The recursive call borrows a wire outside its own
controls and target; the other partition is restored before it is read.
Both recursive sizes decrease above32, so induction terminates in trusted exact
closed MCX leaves. This proves all-input restoration, not merely zero-initialized
scratch. Equality on every basis vector, including its phase, extends by
linearity to superposition and entanglement with arbitrary external references.

X conjugation implements the full ordered open-control pattern. No external
workspace is touched. Each recursive definition is embedded with its actual
wire order and scalar phase; composing these equalities transfers preservation
to nested emitted inverses. Inverting the *actual resolved sequence* also yields
the inverse action. This argument is about exact real-angle gate semantics;
finite floating-point parameters and numerical checks are not interval proofs.

## Executed independent checks

The independent probe uses its own permutation reference, sparse interpreter,
bit-mask gate semantics, exact rational phase propagation and serialization
signature. It does not use worker test helpers, candidate signature/metric
helpers or the library verification interpreter for reference answers.

- **Original boundary reproduced:** forward and inverse closed MCX31/32
  roundtrip; MCX33 fails with `'I' format requires 0 <= number <= 4294967295`.
  All six original files, including both partial33 files, remain in RUN.
  All corrected files roundtrip with ordered gates and phase unchanged.
- **30 dense comparisons**, every polarity for1..4 controls, at most five
  wires, against an independently constructed permutation matrix including
  scalar phase. Maximum entry error `4.47545209131181e-16`.
- **20 wide fixtures**, controls31,32,33,64,65,66,127,129,283,512, each closed
  and mixed-polarity, shuffled wire order, complex coherent inputs, two external
  reference wires, both target sectors across marked/violating inputs and
  actual resolved inverse. Largest sparse vector-distance error
  `1.1008064355126504e-15`; inverse restoration error
  `1.801871086775803e-15`. At most128 stored basis entries; no wide dense array.
- **128 exact dyadic-phase columns** between the conjugating H gates, plus
  prefix/suffix checks, verify unchanged controls/references and the required
  controlled sign. These are finite regressions supporting the compositional
  proof, not an exhaustive enumeration of wide inputs. Sixteen abstract
  a,b,d,t assignments independently check both identities above.
- **Four nested inverse fixtures** include noncommuting P/X operations,
  nonzero nested scalar phases and reversed embeddings; compare actual source
  and saved resolved action independently. Generic MCX definitions are forbidden
  throughout the wide-resolution/readback fixture loop.
- **Original inverse-StatePreparation failure reproduced** on reversed wires.
  Frobenius distance is `3.144140277272011`; corrected distance is
  `2.1523162138265013e-15`, without global-phase alignment. This uses a different
  norm from the earlier review's reported spectral distance.
- **Six saved worker boundary QPY files** independently loaded and checked for
  action/phase. All74 declared candidate evidence hashes match, all83 intake
  identities remain unchanged, and committed Git blobs match the actual files.
- **301 supplied regressions passed,31 deselected**, with explicit runtime
  Operator<=5 and statevector<=18 guards. Exclusions are the prior27
  matching-preparation/search, one asymmetric-k5 R3 and three native
  asymmetric/constant wider dense tests. No full-suite claim.
- **Five fresh synthetic export rows independently recounted:** width, gate
  histogram, gate count and dependency depth. The34-wire diffusion has401 gates
  and depth267, v2 representation and the distinct phase-ladder method; the
  workspace record reserves34 wires. Seed7,17 isolated vertices/k3/j0 is an
  export fixture, not evidence for the missing graph comparison groups.

Independent semantic RNG seed:1030020413. Sparse inputs include marked cases;
random inputs alone would almost never exercise a wide conjunction. Small
matrices, abstract truth rows and negative fixtures are deterministic.

## Counterexamples, exclusions and limitations

Concrete rejected alternatives are retained in `second-probe/independent-results.json`:
truncating a33-control predicate to32 toggles the target on control input
`2^32-1` although the missing top control is zero. Deleting the ladder's final
P gives phase `-pi/2^33` on control input1 with target0, where the correct phase
is zero; exact rational propagation detects this small error. Neither defect
was found in the admitted candidate.

Independent negative probes reject513 controls, wide controlled-Z, restoring
MCX33, and a prefix-aware emitted-operation cap before the prohibited expansion.
The candidate's supplied tests also cover multiple expansions and all-open
controls. Width512 and100,000 emitted/visited operations are supported limits,
not a guarantee every circuit below512 controls fits the total instruction cap.
The preflight includes the already emitted prefix.

Standard Qiskit gate class semantics are trusted, as in the prior admission;
adversarially modified standard objects, opaque/dynamic/unbound operations and
arbitrary custom-definition generation are not certified. Definition traversal
bounds do not bound all Qiskit-internal allocations. No leaf decomposition,
wide transpilation or common-basis numerical equivalence is inferred from QPY
signature equality. The borrowed bits here are original MCX controls, not an
admission of general conditional-workspace synthesis or a new workspace policy.
Logical role reservations are not measured live workspace peaks. Ordinary pi
and dyadic float parameters are not FT-synthesized or interval-certified.

## Resources, failures and follow-up

Existing `/Users/mar/codex-work/logique/.venv/bin/python` only; explicit candidate
PYTHONPATH and asserted imported file paths. Native executable is the prescribed
`native-contract/dump/1025025511-native-contract/build/boolean_synthesis`, SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No sync, install or build. Serial children, numerical/compiler thread settings1;
predeclared120s per child,300s cumulative,2GiB process budget. Checks through
final formatting/lint consumed111.180685s; largest observed wait4 high-water
520,863,744 bytes. Terminal child/possibly reaped-descendant RSS is not sampled
process-group peak and does not enforce a hard memory cap. No hard cap claimed.
Later scalar sealing/Git receipts are separately retained in the same ledger.
Initial staging was sandbox-denied at the shared worktree index.lock; the exact
owned-path Git operation was retried with scoped escalation.

Retained reviewer failures: first signature comparator incorrectly used the
singleton implementation module instead of the stable base class; the first
artifact audit counted pytest's `current` symlink twice; initial lint flagged
the intentionally deferred candidate-path import. All were reviewer harness
issues, corrected without candidate changes. Initial versions, logs and partial
QPY remain; final Black/Ruff pass. No failed mathematical candidate attempt is
being relabeled as a success. Prior worker failures remain independently hashed.

AGENTS.md, CLAUDE.md and the full revision plan were read in full, together with
the29October handoff, authoritative root30October continuation, original QPY
review/admission, comparison checkpoint/results and actual candidate sources,
committed checkpoint and saved evidence. The root continuation file is absent
from this older base and was read at its authoritative root path. Truncated
combined reads were followed by focused reads.

No candidate/root edit, dependency-pin change, old-history/archive rewrite,
queue/state change, model/subagent/Codex launch, hardware, physicalQEC,
precolored/conditional-workspace research, API/paid fallback or push occurred.
Only this new review and distinctly named probe files are committed here.

Next: the authorized coordinator verifies these exact paired bytes and overlap
before integration on `coloring-paper-revamp-codex`; dispatcher alone publishes.
The existing execution successor may then run only the authorized missing43
and clipped comparison groups under fresh budgets, recording unsupported widths
and caps. Obtain separate exact saved-circuit/context evidence review before
admitting new comparative metrics. Re-review semantic conflict resolutions or
changed source. The completed bounded review does not close the paper gate.
