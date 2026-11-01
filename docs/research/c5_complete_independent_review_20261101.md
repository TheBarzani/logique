# Independent complete-predicate C5 review

Task `c5-complete-review-1030020413`, session
`01a19588-d074-76d2-95a6-55985ec870c6`, 1 November 2026.
Assigned branch `codex/coloring-c5-complete-review-1030020413`, base
`e90adf3373236ef51a937480febd3cd7d669dce7`.
**Bounded review COMPLETE. Exact final best-fit correctness and ten ideal rows
ADMITTED within the scope below. Separate structure22 scientific admission
remains PENDING/BLOCKED on the specified independent lowering review.**
No candidate edits, integration, push, native build or new noisy admission.

## Exact decisions

Candidate: sibling `c5-complete-execute`, clean HEAD
`53176684beef47c29c244f7d329d977234a0b9a8`.
Its actual committed checkpoint, complete source/test files, native response,
saved circuits/states, failed-attempt evidence and related source were read.
The required AGENTS.md, CLAUDE.md and 723-line revision plan were read in full.
The 29 October handoff was read locally; the missing 30 October continuation
was read from the integration checkout identified by the active queue.
The current integration C5 pilot report and linked checkpoint were also read.

| Layer | Decision |
| --- | --- |
| Correctness | **ADMIT the final cumulative bytes** of `tools/check_c5_complete.py` and `tests/test_c5_complete.py` at `ab31ae784380e1b039b3cf5dc545f8f999597750`, unchanged at candidate HEAD. These are a bounded C5 experiment harness, not a general native or production lowering repair. |
| Commit sequence | `dd6432d654b549400124d2c7ffceb959cb374b85`, `df4a232fe4cbb5c141c1afa395643715d60a6996`, `ab31ae784380e1b039b3cf5dc545f8f999597750`. Initial/intermediate versions are **not independently admitted**. The first version had a real counterexample; all corrections are required. |
| Build/native | No changed bridge/build to admit. The prescribed unchanged executable hash is verified. Saved native output and actual allocation are independently checked; no new source-to-binary build attestation is inferred. |
| Metrics/evidence | **ADMIT exactly ten ideal best-fit C5/k3 rows** from `dump/1101010944-c5-complete-best-fit/`, R1 j=0..5 and R2 j=0..3, and the checkpoint evidence in separate commit `5317668`. Gates and width describe these saved logical U/CX components only. |
| Structure22 | Saved bytes, logical predicate/cleanup, data-only preparation/reflection and scalar arithmetic checked independently. **Full scientific admission remains pending** for the exact lowered 22-wire oracle. No full first-lobe sweep exists there. See separate assessment below. |
| Other science | No noise, routed/FT cost, native-family superiority, whole Task7, general 22-wire authorization or manuscript admission. Existing historical exclusions remain intact. |

Exact SHA256s, checked against candidate working files and committed blobs:

| File | SHA256 |
| --- | --- |
| `tools/check_c5_complete.py` | `39ba9de8be5917b0c81d46331c48c2acbf425a18e45902233b5ee29a9e1dcd9d` |
| `tests/test_c5_complete.py` | `65c7300a10b8670e130080465d8f2d9a5bdf32a911cae1f368738f4fa13ae3d9` |
| `C5_COMPLETE_CHECKPOINT.md` | `5f4a36e9df3d3105c23bf90110599a70ed9b90312b74f35d4447a480ae282a01` |
| final experiment `manifest.json` | `fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4` |
| shared final `oracle.qpy` | `8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268` |
| R1 `result.json` | `a8767957a8257922c082f0cfba4cceffaf2808c5fe2c62cccfc8712ac6fb049a` |
| R2 `result.json` | `361da4b32ea4357a6fe07a60bcb6a3c022a2f3f151ba7e68b2272412dbcf1954` |

All final experiment manifest hashes and recorded candidate Python source hashes
match. Native request remains best_fit, cuts16/4, legacy refactoring and complete
unbalanced encoder. The prescribed executable is
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
It was not invoked by this reviewer; saved invocation exit/provenance was
inspected. No root default binary or environment synchronization was used.

## Independent semantics and evidence

The independent probe is `tools/probe_c5_independent_1030020413.py`.
It never imports the worker harness, tests, predicate verifier, recurrence or
Statevector evolution for its numerical checks. Qiskit only reads QPY and
constructs the logical circuits for a separate scalar interpreter. A small
NumPy interpreter directly implements the U gate's trigonometric matrix and CX
index permutation, including global phases. It allocates at most 11-wire
vectors, never a dense Operator. This provides a different evolution
implementation from the worker's Qiskit Statevector, though both share the
QPY parser and NumPy floating arithmetic.

Explicit color-tuple enumeration covers all 1,024 binary words: 30 proper
colorings, 243 valid-code words, 781 unused-code words and 213 valid-code edge
violations. Four exported source/preprocessing/network representations each
match all 1,024 words under a fresh Boolean interpreter. The actual native
response contains one ten-input LUT, data0..9 and output10: **11 allocated
wires**, not an assumed feasibility estimate. Its truth table matches the
complete predicate. The reconstructed logical raw circuit is independently
interpreted on all **2,048 data/target basis cases**, including both output
values; it is exactly the requisite XOR with unit phase. Compute-Z-uncompute
therefore restores the zero output and marks exactly all 30 proper colorings.

The saved lowered raw QPY is independently evolved on complex amplitudes over
both target values (seed1030020413); maximum XOR residual is5.05e-14. A separate
clean-output complex probe supports every input word; its saved-oracle signed
residual is1.37e-13. Explicit QPY basis probes cover positive word70, invalid
word3, edge violation0 and the original failure8, with maximum residual1.19e-12.
No fitted global phase is used. These numerical probes are finite checks, not
an exhaustive floating-point operator certificate.

Preparation and its actual emitted inverse restore arbitrary complex vectors,
including both output sectors, with maximum residual5.01e-17. Independent
reflection checks use `2*s*vdot(s,a)-a`, with maximum residual1.25e-15. This
checks the sign as well as probabilities. The saved preparation is emitted
once, inverted as actual gates and used in the diffusion. Domain checks stay
present in both regimes.

For p=M/N and theta=asin(sqrt(p)), good-word amplitudes are
`sin((2j+1)*theta)/sqrt(M)` and supported bad-word amplitudes are
`cos((2j+1)*theta)/sqrt(N-M)`, with zero amplitude elsewhere. This signed
trigonometric solution is independent of the worker's rational two-class
recurrence. Checking the two nearest integers to the first continuous maximum
selects j=4 for N=1024 and j=2 for N=243; the retained sweeps include the next
iteration. The fresh interpreter executes every saved QPY iteration and
compares both against this solution and against the worker's saved full states.

| Regime | Independent observed success, in increasing j | First peak | Extra-iteration success |
| --- | --- | --- | --- |
| R1, j=0..5 | .029296875000, .243474841118, .574376138501, .871435021790, .999484622397, .900260183699 | j4, .999484622397 | j5, .900260183699 |
| R2, j=0..3 | .123456790123, .775420037219, .950509084831, .345567160993 | j2, .950509084831 | j3, .345567160993 |

Maximum independent signed residual is9.63e-13; maximum saved-versus-independent
amplitude discrepancy is7.40e-14, both below1e-10. Independent dirty-output
probability stays below2.59e-26. The R1 peak unused-code probability is
.000404939543798; R2 unused-code probability stays below1.98e-27. R1's unused
population is expected because it starts on all binary words: for any j it is
`(1-Pj)*781/994`. R2's support contains no unused codes. There are no shots or
binomial intervals; observed floating residuals are not rigorous error bounds.

The lower width does not establish lower gate cost: each saved phase oracle
contains84,441 U/CX instructions, versus42,220 for the raw computation.
Preparation has10/20 instructions and diffusion1,175/1,195 for R1/R2.
No common-context baseline, routing, rotation approximation or FT comparison
is supplied. R2 requires fewer iterations but has a lower first peak, and both
regimes lose success on overshoot. These losses must remain in any manuscript.

## Concrete failures and exclusions

The preserved first failed oracle, SHA256
`4a1eb969d6dcc55402ac4b13cd20e336d13b5ba076b96ea40a063060b435de75`,
acts incorrectly on word8 = colors(0,2,0,0,0). The fresh interpreter measures
**0.999999999999524 dirty-output probability**; correct phase action should
leave that rejected word unchanged. Corrected lowering gives8.80e-13 residual.
This independently confirms the need for `qubits_initially_zero=False` when
lowering reusable components. Initial green basis samples did not cover this
failure. The final source also fixes the transpiler process count at1.

The second partial run's saved R2 A/inverse independently round-trips a fresh
complex input with1.56e-16 residual when input/reference buffers are distinct.
The failed worker diagnostic's aliased reference is not evidence of a bad
inverse. Source now explicitly copies input buffers. Both failed/partial
runs and the worker's failed regression remain unchanged.

Removing domain checks would mark **240 rather than30** words. A concrete
edge-only positive but invalid-code word is71 = colors(3,1,0,1,0). It must be
rejected in R1 and R2's complete predicate, even though R2 never prepares it.
All781 invalid-code words were retained in the semantic review.

## Separate structure22 pilot assessment

Pilot source/config commit `ed7811408c1523b9cac1881b1311500ecf3a4b35`,
handoff `0da04596b7a6c6ccbd16e2a2fed072fcace84ca5`;
checkpoint `dump/1031221547-c5-22-qubit-resource-pilot/checkpoint.json`;
evidence `dump/1031221648-executed-ideal-iterations/` in integration checkout.
Manifest SHA256 `7fbb194c2109398bc67ddcb5705b832601d5806c15f405b4b946d4a159d8ea87`;
shared oracle SHA256
`226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`.
All saved evidence hashes and protected source blobs match the declared commit.

The logical sequential structure oracle is independently interpreted on all
1,024 words, checking exact signed phase and restoration of every non-data bit.
Its allocation is10 data +10 constraint flags +1 comparator scratch +1 output
=22. Data-only saved A and diffusion pass independent numerical checks.
The four saved scalar observations agree with p and p(3-4p)^2:
R1 .029296875000 → .243474841118;
R2 .123456790123 → .775420037220.
Reported child times50.478s/51.135s and wait4 RSS527,548,416/501,514,240bytes
are historical measurements, not fresh reviewer measurements. Both reports
correctly say partial_sweep; R1 j2..5 and R2 j2..3 remain unexecuted.

**Do not promote these consistency checks to full independent scientific
admission of the lowered oracle.** The pilot retains default zero-initialized
transpilation, unlike the corrected best-fit harness. This is not proof the
structure pilot is wrong: its additional clean scratch and reachable flags
may make that lowering valid. However, logical scalar checks and two uniform
trajectories do not prove its arbitrary clean-data phase/restoration contract.
The pilot saved scalar residuals but no full state arrays for independent
reconciliation. The instruction to reuse this evidence instead of repeating
the 22-wire run was respected; no wider numerical replay occurred.

Precise follow-up: independently validate the saved977-instruction oracle
against the logical construction on its reachable clean-data/flag/scratch
subspace, using a compositional lowering proof or separately authorized bounded
probes; bind its QPY hash and absolute phases. Only then decide pilot evidence
admission. A general22-wire configuration gate/source admission is also outside
this C5-only authorization. Full structure sweeps require separate execution;
no missing rows may be inferred. Best-fit admission does not depend on this
pending pilot review and does not retroactively change old18-wire exclusions.

## Resources, failures, preservation and handoff

Fresh evidence: `dump/1101011631-c5-independent-review/`, created through
`new_dump_directory` in local time. Per-child limit120s, cumulative300s;
declared process budget2GiB, maximum independent statevector11 wires, no dense
Operator/density arrays, one numerical child at a time, every configured
compiler/BLAS/OpenMP/Accelerate/Rayon/Qiskit parallelism1. No compiler ran.
Memory controls are prebounded arrays and recorded wait4 high water, not an OS
hard cap or process-group RSS enforcement. Maximum observed child high water
142,376,960bytes; all numerical/test/static children together consumed<22s.

Independent main/failure/pilot/witness probes exited0 in8.455s,3.237s,.457s,
5.936s respectively. Focused candidate suites finished **205 passed**, zero
skips/deselections. First invocation had204 passed/1 failed because its
standard-library import test compares against cwd-relative source; reviewer
cwd and explicit candidate PYTHONPATH differed. Running with candidate cwd
fixed that invocation without source edits. The failed log/exit1 receipt is
preserved. Probe Black/Ruff passed. No full repository test/build claim.

`identities.json`, per-child command/exit/time/RSS receipts, seed, all result
JSON, retained initial probe source and final artifact inventory bind this
review. Initial inspection included absent guessed checkpoint/continuation
paths and truncated combined reads; actual paths were subsequently read.
There were no independent numerical failures or timeouts. Final Git and
notification-checkpoint outcomes are recorded separately in `final-receipt.json`.

Only this new review and its distinct independent probe are committed. Candidate
status remains clean. No README, dependency pins, history, archive, failed
artifact, queue, integration checkout source or previous review is modified.
No subagents/models/Codex processes, API/paid fallback, purchases, hardware,
precolored or conditional-workspace research, sync or push occurred.

Next: root coordinator verifies exact final hashes and integrates the cumulative
correctness pair separately from this research-evidence decision. Any overlap
resolution requires re-review. Downstream noise code does not automatically
inherit this standalone harness's lowering correction and has no admission
from this review. Dispatcher alone launches successors and pushes integration
HEAD. The separate structure oracle lowering proof and all new noisy/matched
cost/manuscript work remain explicitly open; this assigned review is complete.
