# Final quantum-correctness and claim review — 13 November 2026

**Bounded review COMPLETE. Full scientific/manuscript evidence gate: BLOCK.**
The evidence supports specific improvements and substantial losses within a
comparative trade-off study. It does not support general compiler superiority,
noise resilience, complete scaling, achieved preparation break-even, a final
novelty verdict, or a submission-ready paper. Passing final regression shards
does not reverse the concrete MCX counterexample below.

Task `final-quantum-claim-review-1101052342`; assigned worker branch
`codex/coloring-final-quantum-claim-review-1101052342`, base
`de230cce74089344343fcdf1c12d553cc4cf8607`. The actual reviewed integration HEAD
is **`1f348d4e1f8c94c941d6452fbca6767b0e004666`**, unchanged across the interrupted
first attempt and closure. The worker base is not the reviewed implementation.
An exact Git archive of current source/docs/tests/tools/native source was
deliberately copied into this worker's ignored evidence directory; actual
`logique` imports were asserted there. No candidate or root source was edited.

Evidence in this worktree:

- `dump/1113115001-final-quantum-claim-independent-review/` (R1): intake,
  predeclared budget, integrated snapshot, identity/chain audits, independent
  dirty20 witness, commands and terminal resource receipts.
- `dump/1113161827-final-quantum-claim-review-closure/` (R2): continuation,
  saved-intersection audit, retained failed first audit, final provenance,
  result/checkpoint and researcher brief. Prior charge is carried forward.

Only this report and `tools/probe_final_quantum_claim_review_1101052342.py`
are owned tracked changes. No models, subagents, Codex subprocesses, scientific
replay, hardware, sync, installation, paid fallback or push occurred.

## Material correctness finding: the saved two-dirty20 MCX is wrong

The later exact wider review `3878f140d02db84d986bfa05d92f62d0ba194721`
rejects `2_dirty_kg24` with 20 controls. I independently reproduced its witness
from the saved QPY, without its Boolean-diagram implementation or its test
helpers. The 39-wire register has controls0–19, target20, borrowed wires21/22
and unused spares23–38. Input bits0,1,22 are one; all others are zero.
Because the controls are not all one, a correct MCX must leave this state alone.

| Saved action | Required | Independently observed |
| --- | --- | --- |
| Forward basis word | 4,194,307 | 5,242,883 = input + 2^20 |
| Compute–Z–actual-inverse output word | 4,194,307 | 4,194,307 |
| Paired output amplitude | +1 | −0.9999999999999655 |
| Forward / paired L2 discrepancy | 0 / 0 | 1.4142135623730872 / 1.9999999999999654 |

The independent dictionary evaluator used primitive matrices of at most three
wires, at most two surviving basis entries, no full-register statevector and
no phase alignment. Summed discarded-amplitude L2 allowances were
2.7413e-15/8.5222e-15. These discrepancies are not numerical uncertainty: the
actual inverse removes garbage but cannot undo a mark applied to the wrong
computed target. On a superposition with an unaffected basis state the sign
becomes a relative-phase error, so restored bits alone do not certify an oracle.

Exact rejected files in the original `mcx-whole-circuit` worker's
`dump/1031080140-mcx-whole-circuit/1031081106-mcx-isolated-2-dirty-kg24/20/`:

| Path | SHA256 |
| --- | --- |
| `forward-explicit.qpy` (also primary) | `712d3bfc8a652233f2692c81fb3716b3bd0185e70abebdca12a89fcff017babe` |
| `paired_phase-explicit.qpy` (also primary) | `33e5795b262cef319a94a71e69ed455871d538e9cf79436ae8f95a22c5c50793` |

The wider review's already checked common/partial-FT translations faithfully
carry the same defect; translation fidelity is not semantic repair. Current
`src/logique/benchmarks/costs.py` still dispatches this policy directly to the
installed constructor, without a 20-control exclusion. Its whole-file hash is
`8529ad29d6457ed784c700ae26a7579b72bc0221857eb575a884ee4dc6c7a7b0`.
Reject an arbitrary-dirty correctness claim for this saved construction and
withhold its costs from correct-MCX comparisons. The diagnosis concerns exact
Qiskit2.1.1-derived bytes, not the published Khattar–Gidney theorem or other
versions. It does not invalidate the separately checked small whole fixtures.

Required successor: a fail-closed exclusion or corrected construction, covering
this basis witness, coherent relative phase and borrowed-reference restoration,
then exact independent source/evidence review. Preserve the old cost row and
all representations as rejected historical observations; do not alter pins or
rerun the completed study to conceal the failure.

## Reconcile the current manuscript with the offered later decisions

I read the complete inherited manuscript, new evaluation TeX, claim ledger,
reviewer map, copy assembler and restrictive presentation review. The eleven
bounded-draft paths retain `f7ceb08`'s presentation admission, integrated as
`669b618`. The draft explicitly dates its evidence slices and makes no broad
advantage claim. That protects its historical interpretation; it is not a
current complete synthesis of every offered result.

Four changes must be reconciled in a new reviewed manuscript/ledger revision,
without rewriting frozen reviews:

1. **Wider MCX:** the dated 1,608 completed cost rows are not 1,608 correct-MCX
   certificates. The wider decision closes the 84 whole-row gap and gives
   144 supported/one rejected saved isolated constructions at controls7–20.
   Its initial 53-pending status is superseded by its own addendum. Publication
   must expose the dirty20 rejection; the remaining correct-cost denominator
   requires explicit filtering/recount, not silently subtracting one from
   every historical metric aggregation.
2. **C5 structure:** `24a3c91` closes the particular saved977-instruction
   clean-data lowering gate. Older root and draft PENDING language is stale
   relative to that offered decision. Only four original j0/1 observations
   are covered; no additional simulation or C5 noise is admitted.
3. **Large logical equivalence:** `0fc7d72` admits 103 exact oracle/search pairs
   beyond the earlier component-only slice. The older zero-all-input sentence
   is valid for its dated slice, not the entire current offered evidence.
4. **Graph RUS:** the current integrated two-register instrument extends the
   one-register evidence. The draft may retain E5 as a dated local slice, but
   a current account must distinguish the admitted heralded single-edge
   construction from still-blocked deterministic/static or quantum-controlled
   substitution. Its unfavorable overshoot must accompany any update.

These are substantive claim decisions, not permission to edit admitted prose
silently. A later semantic amendment needs exact independent review.

## Quantum contracts and scientific interpretation

**Regimes, order and phase.** The maintained encoding and manuscript separate
LSB-first vertex bits, valid codes, and proper colorings. R1 uses H with the
complete predicate; R2 uses valid-code A with that predicate; R3 drops domain
checks only on ideal valid support. The signed reflection is
`D=A(2|0><0|−I)A†`; time order is oracle, actual A†, signed S0, A.
The scalar minus in `S0=−X MCZ X` is required. The maintained Grover entry
adds that phase; the explicitly historical kickback path retains its historical
convention and is not interchangeable evidence. Generic StatePreparation and
the specialized replay preparation are distinct constructions.

Raw output agreement is not arbitrary-target XOR or coherent phase admission.
Compute–phase–actual-inverse cancels raw phases and garbage only within its
proved input/restoration contract. Direct kickback needs arbitrary-target action.
Clean scratch, arbitrary dirty/reference correlations, held throwaway scratch
and conditionally clean branches remain different promises. The reusable
component fix correctly disables program-entry zero inference at six sites;
it does not make source workspace arbitrary or retroactively repair old QPY.

**C5 structure proof.** I inspected the entire exact-ring checker and its
mathematical induction. Each basis input uses22 one-wire factors; every CX
control must be a definite bit before that step. Checking all1024 clean data
columns then extends by linearity to data entangled with an untouched reference;
it does not assume a general superposition remains a product state. The
cyclotomic arithmetic, absolute final sign, actual wire identities and rational
Machin enclosure bind the saved U parameters to the canonical proof. The
stored-angle oracle bound is <5e-14, distinct from simulation roundoff and
from any complete-search bound. This resolves the exact gate, not a general
zero-input transpiler theorem. The original15 pilot hashes were independently
authenticated through the proof inventory. No22-wire evolution was repeated.

**C5 best-fit ideal evidence.** Ten separate 11-wire observations retain
`4fbf3d0`'s admission. The84,441-U/CX oracle is not the977-instruction structure
oracle. With M=30, R1 N=1024 peaks at j4 with .999484622397 then falls to
.900260183699; R2 N=243 peaks at j2 with .950509084831 then falls to
.345567160993. Earlier peak does not mean higher discrete peak. R1 peak unused
probability is .000404939543798; R2's tiny observed leakage is numerical, not
an exact zero certificate. No shots/confidence intervals, routing, FT or
matched-width advantage follow from these ideal values.

**FT repeated errors.** The current graph harness preserves the emitted A
and its actual inverse, signed original numeric targets, clean restoration and
the original static-pilot dense4 contract. At j1, weights `(3,1,1)` charge
21 R1 or27 R2/R3 rotation occurrences. Local degree6 precision success is not
complete-search success: conservative operation bounds7,875,644/10,125,710/
10,125,196 exceed the3,000,000 guard. The permitted R3 degree6/depth3 attempt
fails at .00139294 versus required3.7037e-6. Three original tight-precision
failures remain failures. Numerical engineering bounds are not interval proofs.
At primary1e-3 and matched j1, actual T counts271982/353792/353624 mean R2/R3
lose81810/81642 T. T-depth is dependency-based, not additive. H/j0 gives3/8
proper probability at zero T; unpriced verification/Clifford/runtime prevents
an achieved break-even or speedup conclusion.

**Dynamic aborts.** The integrated fixed-edge graph source explicitly uses an
MSB interface, distinct from the general LSB encoder. It applies inverse vertex
loops first in reflection time order and retains every abort prefix and flag.
For s=1−4^(−cap), completed reflection is `s^4 DρD†`; full prepare-plus-one-
iteration completion is s^6. Discarded abort records do not yield deterministic
D. At cap2, completion .678934156895 times conditional proper probability
2/27 gives .0502914190292 joint success. The edge starts at2/3 proper success,
so one completed iteration overshoots badly. The saved149.651656747 expected
stop T includes aborts, but reset/feedforward/runtime remain unpriced. The
naive-control purity13/16 obstructs that construction, not every possible
controlled algorithm. Retain only the admitted caps, references and23 cases.

## Comparisons, noise, native mechanisms and scaling

Fresh scalar/hash checks independently recover the following intersections.
They are not new compiled circuits or observations, nor pooled experiments.

| Evidence slice | Actual denominator and result | Restriction |
| --- | --- | --- |
| Large logical CEC `0fc7d72` | 436 service artifacts =230 components+103 oracles+103 searches;912 metric details =80 wins+492 ties+340 losses | myciel5/k6 and2-Insertions_3/k4, saved seed7/j1/profile/context;12 chains unresolved; logical mixed granularity, no common/routed/FT inference |
| Common comparison `0819f5e` | 141 artifacts =120 shared components+21 oracles; complete three-baseline oracle intersection15 details =3 wins+12 losses | K3/k3 R3, U/CX opt0, clean_tree/fresh_zero, profile none;39 other small oracles/all60 searches unproved in this slice |
| Noisy family `622269d` | 376 new64-shot histograms/24,064 shots +28 original/1,792 =404 records/25,856 shots |401 of805 frozen keys lack admitted family observations; generations/seeds/regimes not pooled |

The large CEC proof is conditional on the trusted ABC UNSAT solver and intended
standard-gate angles, with exact saved sequence/predicate/phase binding. Its
pre-CNF estimate underbounds allocation and its C++ wrapper can accept a
contradictory prefix before validating a malformed tail; general checker reuse
remains blocked. UNKNOWN is not inequivalence. All baseline proofs succeeded
in the admitted logical intersection; filtering did not artificially weaken
that denominator. XAG's72 admitted oracle/search comparisons all lose.
The concrete217/83 width ratio on2-Insertions_3 is2.61446, not a saving.

In the common intersection best-fit supplies all3 wins:7/10 wires,94/181
instructions and64/90 depth, against the metric-specific strongest of all
three corrected baselines. The other four admitted methods lose all12 details.
K5's32 seeded assignments+4 witnesses are not universal CEC; absent sb_simple
R1/R2 cannot be replaced by a weaker baseline and called strongest. The frozen
K5 request has25 constraints>20 and is not rerun-authorized. The14,850-entry
ledger still includes3,780 unrun cost,6,750 routing and4,050 FT requests.

The noisy count audit authenticated all4,397 execution inventory entries and
the admitted result hashes. K3 R1/j2/seed11 has4/64 proper outputs versus
.999778747559 ideal,37/64 unused codes; independent Wilson95% is
[.0245712014,.1499748509]. This is conditional on one fixed circuit/model,
not simultaneous coverage or a between-seed estimate. Noise excludes idle
relaxation, drift and crosstalk.74 five-seed groups and13 complete sweeps do
not close all families.23 timeouts,20 new width exclusions,190 deferrals and
one missing-receipt histogram remain nonmeasurements/withheld. The5.288070s
path7 window is not evidence of a120s failure. C5 adapter's965-record order
defect is fail-closed; preserve internal channel order/ordered qargs and fix
only independent top-level record ordering before new reviewed execution.
No C5 shots are admitted by either ideal chain or this review.

Private MC's2→1 AND fixture and fast/depth's accepted bounded final graphs
establish neither family performance nor production-profile admission. Current
private source/build admissions remain capped and opt-in. The native certificate
whole-chain BLOCK persists on typed duplicate-leaf aliases (`True`, `1.0`);
it is a boundary-contract defect, not a demonstrated wrong Boolean output.
Ordinary admitted SAT is distinct and retains its caps/outer-timeout assumption.
The newer scaling composition still loses genuine receipt fields across SIGINT
transfer; zero selected compiler invocations and220 pending slots cannot support
five-repeat scaling. DSJC125.1/le450_5a positive witnesses and larger M remain
prerequisites; unavailable compiler stage splits stay null.

## Final validation and actual preservation limits

I authenticated all four final-check inventories:1173+198+1381+231=**2983**
entries, zero mismatches. An independent JUnit recount finds2532 passing
invocations,2523 unique identifiers,9 repeated passes,16 historical skips of
which15 later pass, and one current skip. There are no reported test failures
in these XML shards. This is not a full-suite certificate:26 dense-cost and7
teaching/visual exclusions, further deferred maintained tests and notebook
scope/allocation gaps remain. Only two teaching notebooks executed offline;
source notebooks remain output-empty. Package build is blocked by the absent
setuptools/wheel backend in the authorized environment.

The copied-Qiskit historical replay saved135/135 matching scalar metrics. Its
installed Qiskit remained unchanged; the copied analytical patch is explicitly
reconstructed, not a recovered original. The lost supervising exit/time/RSS
receipt is not recreated by the saved CSV or by charging120s conservatively.
Accept the saved equality as qualified replay evidence, not fully receipted
execution or validation of historical diffusion/accounting.

The final worker rebuilt private fast/depth and ordinary SAT in new directories;
their hashes reproduce `d1a26b3f...` and `81bc6a78...`, respectively. The
unchanged-experiment bridge remains `6aa7357d...`; root's old default remains
`ea78b720...`. The6149 absolute bindings freshly checked here include proof
artifacts and1136 fast/depth,1139 SAT and1323 MC/balancer effective dependency
entries. These counts overlap; they are not independent experiments. No build
or native invocation was performed by this reviewer.

Retain the actual historical losses: missing first failed SAT/value executable
bytes, unavailable ephemeral profile pytest inputs, missing pre-fix dynamic-RUS
source snapshots, the unsealed first CEC pilot, the noisy histogram without a
terminal receipt, and the replay supervisor receipt. Later successful hashes,
tests and builds do not reconstruct them. Earlier overlapping audits/child-plan
violations remain disclosed in their original reviews; this batch had serial
supervised children. No old artifact was repaired or overwritten.

## Exact decisions and integration boundaries

All513 current tracked blobs were hashed and checked against Git blob IDs;
the sole working-tree difference is the preserved README edit. The archived
review snapshot matches current source. All539 manuscript source-index entries
match. Twelve current-root independent-review copies match their committed
reviewer blobs; nine additional offered report/probe files match their actual
worker HEADs. Of72 explicit table identities checked against root,60 match;
all12 differences belong to deliberately withheld native/scaling/C5-adapter
offers, not admitted-byte drift. See R1 `chain-audit.json` for every identity.

**ADMIT the following final-check paths only as bounded validation records and
the frozen executed supervisory tool**, at `cb1014fbe64124d5232fe3dc8567ea83d8bbaa3d`:

| Path | SHA256 |
| --- | --- |
| `docs/research/final_isolated_checks_20261113.md` | `e729071ccaa5c6e6d412000928de361a995a5dbb2d9d695d84a6a9631af51a01` |
| `tools/final_isolated_checks_1101052342.py` | `69c276ab25297cc27c665eb5af4cf23e0f0e662a4921734b18dd452ef8ba8843` |

This is not a new general process-control/interrupt/memory theorem, a native
production admission, or permission to run unexamined fixtures. Preserve all
failed setup scripts and the replay-receipt qualification with the report.

**Endorse the exact C5 proof and restrictive report for the saved oracle only**,
at `24a3c91c20bbfe53dddcda25fa7de472cb4b090a` (proof implementation `37c09c8`):

| Path | SHA256 |
| --- | --- |
| `C5_STRUCTURE_LOWERING_REVIEW.md` | `39f026211e90f84845302511f37fd286f4e13b570e239052abb151389304dcc8` |
| `tools/prove_c5_structure_lowering_1101052342.py` | `47e3703e0bf89d82a5ff9f73a71972ffb89ea8ae65b0115f86d7e6369269e98d` |

The exact oracle remains
`226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`.
Its four saved observations retain their ideal-only partial-sweep restrictions.

**Retain and publish the following restrictive decisions**, not new blanket
source/proof-engine admissions:

| Decision record | Commit | SHA256 |
| --- | --- | --- |
| `MCX_WIDER_SEMANTIC_REVIEW.md` | `3878f140d02db84d986bfa05d92f62d0ba194721` | `7201e8a0032a41dd211f3b5e39f1477094ec21b785614936d367fcfeda20920b` |
| `COMPARISON_CEC_INDEPENDENT_REVIEW_1101052342.md` | `0fc7d724842efb7b6b73cacc0e45d297e35a1979` | `7fba7222f010f6447106bc71c31181a24b37e07fc5f1e212c3182386ec62a0da` |

Their bounded84-whole/144-isolated and103-pair admissions remain exactly
indexed by their original manifests. I independently authenticated the relevant
artifacts, traced the proof arguments and reproduced the dirty20 rejection;
I did not rerun every certificate or confer arbitrary-input proof-tool approval.
Existing integrated source/build/metric decisions retain their distinct scopes.
This review admits no new library correction, performance measurement or
blocked candidate fragment. Coordinator alone integrates exact admitted bytes;
any semantic conflict resolution needs a new review.

## Evidence gate, literature boundary and next actions

The most defensible direction is a **comparative synthesis trade-off study**,
with named narrow improvements and explicit losses. Full evidence gate remains
**BLOCK**, rather than choosing a final contribution/title/abstract now.
Automated Boolean/coloring compilation already appears in
[Schmitt et al.](https://past.date-conference.com/proceedings-archive/2021/pdf/2010.pdf);
back-end-aware XAG resource optimization in
[Yu et al.](https://si2.epfl.ch/~demichel/publications/archive/2025/ASPDAC25_YU.pdf);
and cut/balancing/ESOP multiplicative-depth optimization in
[Häner–Soeken](https://arxiv.org/abs/2006.03845). Fresh primary-source retrieval
confirms these attribution boundaries. Their methods cannot be claimed as new
here. This is not an exhaustive novelty survey. If completed matched ablations
cannot establish a distinct useful result, reconsider resubmission rather than
restore the rejected historical superiority claims.

The coordinator's concrete order is: publish the dirty20 exclusion and request
its focused correction/review; reconcile C5/CEC/MCX/graph-RUS decisions in a new
claim-ledger/manuscript revision; close remaining exact common-service and
large-equivalence obligations without weakening baselines; resolve native typed
leaves, scaling receipt transfer and C5 calibration ordering before dependent
execution; finish resource-justified precision/noise/scaling axes and actual
matched ablations; obtain an approved offline package backend and remaining
bounded validation/notebook decisions. Keep all exclusions and missing receipts.
No prerequisite polling or blind retry is needed to finish this review.

Resource declaration precedes arrays:120s/child,300s cumulative across both
attempts,1GiB declared process budget, one numerical/compile child, all configured
compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. The only fresh quantum
calculation is the sparse saved failing witness with local matrices<=3 wires;
statevector18/dense5/staticFT4 limits are unchanged. Darwin terminal wait4 is
not a hard cap or live/group peak. R1's three checks total2.999084s; R2's failed
then corrected scalar audit total2.842142s. Maximum measured child high-water
is66,322,432bytes. Read-only inspection/Git/style commands have tool timings,
not fabricated separate RSS. The values audit initially resolved a relative
proof path from the wrong directory; its failed source/log/exit1 receipt remain.
The corrected version authenticates the actual hash-bound proof files. The
user interruption occurred with no supervised child pending; no lost new receipt
or rerun is concealed. Earlier identity/witness-mode script versions were not
separately copied before the chain-mode extension; their executed functions
remain in the final probe. The executed closure script is separately preserved
and AST-identical after formatting. This version-preservation limitation does
not supply missing historical evidence. Final checkpoint binds formatting,
commits and briefing.
