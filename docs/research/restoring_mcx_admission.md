# Restoring MCX coordinator admission

Coordinator `coordinate-restoring-mcx-1025125442`: bounded integration COMPLETE;
ADMITTED only for the exact clean_tree/fresh_zero source identities below and
the declared clean-subspace semantic/serialization contract. Both predecessor
jobs completed. No earlier own completed handoff existed; the completed QPY
and stage-controls coordinators were inspected, not repeated. Full controls,
scientific studies and the paper remain unfinished.

The byte-preserved [independent review](restoring_mcx_review.md), commit
`8b23d5c59af6d1cab47f33371fdcbd4921827f24`, has SHA-256
`3a52b581b286e6fa9c9afc7139a73fa510d9234f2f7902ac1fb8651c99a416da`.
The complete worker checkpoint is preserved in the coordinator run. Only owned
correctness commits ea3f4e8/e3a295e entered integration 93bba09/b4ed5fa.
Only the source/test portion of 0eacb13 plus the
[representation ledger](restoring_mcx_representation_changes.md) entered separate
metric commit 7e8615c; no checkpoint-only worker commit, build, dependency or
historical research table was integrated.

| Exact integrated file | SHA-256 |
| --- | --- |
| src/logique/benchmarks/coloring_study.py | a811e028b82b4ac1ddf01fa57e6449f5065a797302d1f676e1b4e67bd34511e5 |
| tests/test_coloring_study.py | 64166bd9eb17ba7d8190815164cbb7e670331561d225b913c77245f2efddd3f9 |
| Unchanged src/logique/benchmarks/costs.py | 42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8 |

Opt-in configuration requires both mcx_decomposition=clean_tree and
mcx_workspace=fresh_zero; null/missing/mismatched configured controls reject.
Direct assemble_case uses None as omission sentinel: explicitly passing both
Python keywords as None selects default. This distinction corrects the worker
checkpoint's overbroad null-rejection wording. Limits: original k<=8, <=21 data
wires, j0..2, source MCX 3..20 controls, operation width<=21, definition depth<=32
and <=100000 visited operations per resolver. These traversal bounds do not
bound Qiskit's internal definition-generation memory or all native allocation.
Unsupported opaque/unbound/dynamic/classical/nonfinite forms fail closed.
CCX/RCCX can remain; this is neither general two-qubit nor Clifford+T lowering.

The independently assessed proof uses a monomial internal RCCX conjunction
prefix P that leaves original controls and the external target unchanged.
On zero scratch, P computes conjunctions with a scalar phase. The exact final
CCX flips only the external target. The actual P inverse therefore restores
every internal bit and cancels its phase, including the carried odd-layer wire.
Equality of clean-subspace columns extends to superposition/reference states by
linearity. Open controls are X conjugations, not discarded control states.
Dirty scratch is excluded: the retained three-control witness maps input 20 to
28, whereas ideal MCX would retain 20. This is a real precondition, not an
unconditional full-register unitary identity.

Baselines lower initializer/compute once and marking once with distinct fresh
pools, then invert the actual lowered prefix. Constant adapters retain their
actual raw predicate. Native raw retains its backend workspace/phase contract;
restored MCX scratch does not make raw a clean phase oracle. Verified arbitrary-
target XOR uses X-H/raw/H-X; conservative wrappers use raw/Z/actual raw inverse.
A is built at original k, lowered once and inverted as actually emitted.
Diffusion is actual A inverse; signed -X^n MCZ X^n; actual A, proving
A(2|0><0|-I)A†. Search embeds A once and exact saved O,D j times, with explicit
ordered data mapping. Raw/A/S0 scratch pools are pairwise disjoint and outside
all backend wires; no data, constraints, output, kickback or unknown native
workspace is borrowed. The clean-scratch subspace of A is invariant, including
under its inverse. Backend predicates remain subject to their own validation;
this theorem transfers valid source computation, not validity to an unchecked
backend. Source sampling remains sampled.

Each gate restores its fresh scratch, permitting within-block reuse. The MCX
live field is a construction-capacity upper bound, max(raw,A,S0) for j>0 and A
only for j0. Reserved j0 width still includes unused pools. It is not measured
liveness, an optimal workspace proof or optimized/routed peak. Unknown backend
workspace, general live workspace and memory remain unavailable/null. Native
combined timing overlaps synthesis; no fabricated optimization/mapping split.
Actual decomposition intervals have explicit nested scope. QPY retains bound
emitted definitions, scalar phase and ordered wires. Canonical ordered quantum
registers fix mixed Qubit/AncillaQubit readback without changing the embedding.
General wider original-to-transpiler equivalence is excluded.

Coordinator replay of the reviewer-written independent harness on candidate
and integrated bytes each passes 117 semantic cases, 11,747 scalar columns,
1,112 ordered compositions, 1,113 bounded operator calls, 90 statevector checks,
2,100 direct saved-row recounts and 480 byte-identical omitted-option artifacts.
The operator count includes local contractions/reference matrices, not that many
independent whole-circuit equivalences. Largest entrywise error:
1.8356350271804544e-14 (tolerance 3e-11, no phase alignment).
An integrated additional replay freshly checks all 210 complete cases / 1,050
primary saved components and metadata, 15 explicitly forced conservative native
wrappers across methods/regimes at j2, and a five-wire nested/open-MCX A with
three nonempty disjoint pools. It passes 360 scalar columns, 1,186 compositions,
866 bounded operator calls and 32 statevectors; maximum error
1.6081975806755164e-15. Injected A is assembly coverage, not a valid-color
preparation claim. Wider fixtures use <=3-wire local contractions and scalar or
ordered compositional proof, never a wide dense state/operator.

Integrated regression command (existing research interpreter):

```sh
/Users/mar/codex-work/logique/.venv/bin/python -m pytest tests/test_coloring_study.py -k 'not matching_preparation_diffusion_and_search and not r3_keeps_asymmetric_k5_preparation and not native_asymmetric_constant_r3_and_complete_search' --basetemp=dump/1026071418-restoring-mcx-coordinator-triage/integrated/test-artifacts -p no:cacheprovider -q
```

Result: 164 passed, 31 deliberately deselected, zero skips. Exclusions remain
27 matching_preparation_diffusion_and_search, one
r3_keeps_asymmetric_k5_preparation, three
native_asymmetric_constant_r3_and_complete_search. Relevant Black/Ruff and
Git diff checks pass. No full suite, mypy, build, notebook, historical replay,
routing, static FT or full study was run in this batch.

Fresh command argv/environment/exit/time/RSS, exact replay scripts, expected
negative artifacts and result hashes are in
`dump/1026071418-restoring-mcx-coordinator-triage/commands.jsonl` and batch.json.
The scripts retain the independent reasoning and change only output/evidence
paths, leaving original evidence unchanged. Numerical commands are sequential,
<=120s each and <=300s cumulative; BLAS/OpenMP/Accelerate threads=1. Operators
<=4 and complete statevectors<=5. Maximum measured child RSS 221544448 bytes;
these fixed fixtures stay below 8 GiB. This is not an enforced aggregate memory
cap or complete OS process-visibility claim. Existing Python only, explicit
checkout src, cache /Users/mar/codex-work/logique/.cache/epfl and manifest-admitted
private foundation executable SHA-256
6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a.
Root old executable retains
ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa.

All worker 461 protected and 6599 evidence identities, reviewer 250 protected
identities and coordinator 7300 intake identities are checked. README edits,
prototype backups, archived results, nested histories, lockfile and dependency
pins remain unchanged. Entire 39-job queue/state inspected: unrelated native
low-T and alias coordinator blocked records are retained; no new native scope
or status mutation. Expected rejection fixtures include 11 other policies,
opaque/unbound/classical/>20 controls, corrupted scalar readback and dirty-scratch
counterexample. Earlier worker harness failures and 18 genuine mixed-register
QPY IndexErrors retain their partial artifacts and zero failed-case rows.
Fresh numerical checks all pass. Exploratory absent worker intake.json read
failed before mutation. Initial Git sequencer sandbox denial was resolved by
scoped automatic escalation; no automatic approval rejection occurred.

Next is only max_component_qubits acceptance after assembly and before artifacts,
not memory enforcement: isolated component-width-1026071418, independent
component-width-review-1026071418, coordinate-component-width-1026071418.
Queue append is atomic with immutable prior header/definitions/prompts.
Dispatcher alone launches and pushes integration HEAD. On repeat verify this
completed batch/commits/hash-bound evidence/unique handoff and release COMPLETE
without new tests, integration or jobs.

Remaining full scope: other restoring/ancilla-free/dirty/conditionally-clean/
throwaway policies, bounded 3..20-control studies/infeasibility, full workspace,
stage/routing/precision/limits controls; post-pilot protocol freeze; affected old
QPY/pilot evidence correction/review; nine-graph R1/R2/R3 multilevel saved-circuit
strongest-baseline comparisons, ablations and five fixed routing seeds; remaining
native mappings, MC reduction/balancing profiles and SAT; common-lowered structure
comparisons; meaningful graph-domain static FT under unchanged exact-hash
rotation numerical/caller contract; separate RUS/dynamic and preparation
break-even; ideal/noisy iterations through first peak plus one, leakage,
confidence intervals, random sampling/cost-per-success; scaling/DIMACS with five
repetitions, resources/timeouts and positive/negative larger witnesses; full
research acceptance/build/provenance, offline notebooks and isolated 135-metric
historical replay; traced manuscript numbers, reviewer responses, evidence gate
and independent final quantum-correctness/claim/reproducibility reviews.
No interval certificate, ideal-amplitude guarantee, new RUS/static FT experiment
or blanket paper admission is granted. Bounded completion is distinct from
scientific admission and full-paper completion.
