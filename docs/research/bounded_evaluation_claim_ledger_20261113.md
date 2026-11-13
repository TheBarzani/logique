# Bounded evaluation claim ledger — 13 November 2026

Task `manuscript-bounded-evaluation-1101052342`; assigned base
`de230cce74089344343fcdf1c12d553cc4cf8607`, branch
`codex/coloring-manuscript-bounded-evaluation-1101052342`.
**Implementation draft complete only after its recorded checks; independent
presentation/exact-byte review PENDING. Full manuscript gate BLOCKED.**
This dated ledger does not replace historical ledgers, reviews, or artifacts.
It is a presentation candidate, not a new scientific admission. The current
authoritative root successor includes the separate 9 November noisy-family
decision; the original task's 28-row slice is retained rather than relabeled.
Calendar and total-batch limits in older handoffs are superseded by the latest
user overrides. This worker changes neither queue nor operational limits.

## Candidate and reproduction

New owned source directory:
`docs/manuscript/bounded-evaluation-20261113/`. It contains the evaluation TeX,
ten generated table rows, byte-identical saved figure/CSV/script assets, an
input verifier, source index, and a copy assembler. The original
`docs/manuscript/conference.tex` and bibliography remain byte-identical to the
admitted background revision. The assembler inserts the evaluation in a
new dump copy, marks its title/abstract as provisional/full gate BLOCKED, and
updates the copy's concluding status to describe a bounded evaluation draft.
Its contribution paragraph makes no new novelty or superiority assertion.

Run `verify_saved.py --root ROOT --output NEW_JSON` using the existing root
venv Python and explicit candidate `PYTHONPATH=WORKTREE/src`. It asserts the
actual logique import path. The recorded `source-index.json` stores root-relative
source/evidence paths and SHA256s: no reliance on missing-equals-missing contexts.
Then `build_copy.py --root ROOT --output NEW_COPY` emits the offline Tectonic
command. Execute it serially with `--only-cached`; original sources/PDFs stay
untouched. The plotting script is the original saved script and expects its CSV
beside it; any regeneration must first copy both to a new evidence directory.
This task reuses the saved figure bytes rather than rerunning quantum work.

Fresh local checkpoint:
`dump/1113061703-manuscript-bounded-evaluation-finalize/checkpoint.json` in this
worktree; earlier interrupted work and the failed first TeX build remain in
`dump/1113014653-manuscript-bounded-evaluation/`.
It records commands, exits, time, RSS scope, inputs, task/session/commits,
failures and next actions. The local full draft PDF is a new build artifact;
neither a historical PDF nor a new tracked submission PDF is overwritten.

## Number-to-byte map and admission scope

All paths below are relative to the authoritative integration ROOT unless
explicitly labeled candidate. The source index supplies full hashes for the
individual artifacts, including the saved QPY underlying the tables. Counts
of rows, metric details, summaries, branches and shots are different units.
The verifier independently recounts scalar data and checks byte identities;
it does not rerun state evolution or re-admit the underlying experiments.

| ID / draft location | Exact numerical source and locator | Independent authority / restrictive interpretation |
| --- | --- | --- |
| E1, comparison table | `dump/1030020413-full-scope-continuation-coordinator/worktrees/comparison-evidence-review/dump/1030165059-comparison-continuation-review/`: `admitted-component-intersection.json` length 230, components preparation/diffusion; `admitted-matched-service-details.csv` 492 rows all ratio=1/outcome=tie; `admitted-matched-service-summary.csv` 378 groups summing 492 instances. Each of the 230 QPY hashes checked against `dump/1030122806-wide-qpy-execution/checkpoint.json`. | Review `0620e7e`, verbatim `comparison_continuation_admission_review_20261101.md`, SHA256 `c6e271f0e63e055280da0998f96415334be6ba3eb0799961d5f3dcecd98f8da2`; root coordinator `fc8177c`. Unrestricted logical component reuse only in the reviewed k4/k6 construction. Zero all-input oracle/search comparative rows admitted in this slice. |
| E1, diagnostic losses | Same exact review and `full_research_successor_20261101.md`: full arithmetic 984 details =84 wins+492 ties+408 losses; all wins/losses sample-qualified. | Not an unrestricted strongest-baseline table, common-basis, routed, FT, nine-graph or novelty admission. No pooled geometric mean. |
| E2, all ten C5 rows and figure | `dump/1030020413-full-scope-continuation-coordinator/worktrees/c5-complete-execute/dump/1101010944-c5-complete-best-fit/{R1,R2}/result.json`, `rows[iterations]`, `width`, `artifacts.oracle`; manifest SHA256 `fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4`. R1 result `a8767957a8257922c082f0cfba4cceffaf2808c5fe2c62cccfc8712ac6fb049a`; R2 `361da4b32ea4357a6fe07a60bcb6a3c022a2f3f151ba7e68b2272412dbcf1954`. | Review `4fbf3d0`, integration `2fff3ea`, separately admitted evidence `5317668`. Complete predicate, 30 proper colorings, ten data wires+output=11; seed7, cuts16/4, legacy refactoring, unbalanced encoder. Complex128 ideal observations, tolerance1e-10; no shots, confidence interval, noise, FT, or general native admission. |
| E2, instruction/width and probabilities | Saved phase oracle SHA256 `8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268`; metadata 84,441 U/CX instructions/11 wires. R1 support1024 and peak j4→j5: .999484622396888→.9002601836987874. R2 support243 and j2→j3: .9505090848309111→.34556716099272616. R1 peak unused .0004049395437978435; R2 observed max1.8165258781287765e-27 (review bound1.98e-27). | Saved results, independent review and exact manifest; scalar formula independently recalculated for each row. R2 fewer iterations but lower discrete first peak; both overshoot. Width does not establish gate/resource advantage. |
| E2, figure presentation | `dump/1101052342-full-research-successor/figure-manifest.json`; CSV `c788a1c7bafef6d54c1df7b2627b2957697045d5a6d2ce3e7adaa748bf230417`; script `4cd9e4df80ed784686a49f7148ac67e0e0b40a03f630a191cb847aaece423771`; PNG `666bf58b6c7b9a1416141bcbc284567831b411b07ff1b01b1e33fc9c52efeca7`; PDF `f3830b64b5fdd7aeea6eb74945ee673833ec063115a46fc51d183e6e709dde81`. Copied assets match all four hashes. | Worker inspected PNG: common probability scale, labeled axes, analytical line and saved-state markers distinguishable, integer iterations, panel-specific ranges. Caption explicitly says segments join discrete predictions and probability is dimensionless. Presentation still needs independent review. |
| E3, MCX coverage/caveats | `dump/1030020413-full-scope-continuation-coordinator/worktrees/mcx-whole-review/dump/1031145904-mcx-whole-independent-review/recount-results.json`: rows1608 complete/42 excluded, coherent1335/84 full-statevector exclusions, diagnostic wins1411/losses1194/ties2555. Exact reviewed/integrated reports supply189 isolated+1419 whole, nine Gray12..20+33 sb_original exclusions. | Review `3f76e78`, correctness `9670b88`/`fdefc19`; reports `mcx_whole_review_20261031.md`, `mcx_whole_integration_20261031.md`. Cost observations are not all-width coherent proofs. Dutta analytical; residual rotations unpriced, total FT null. Candidate erratum: clean policies allocate zero-initialized scratch, not zero scratch. |
| E4, static FT table and precision failures | `dump/1030020413-full-scope-continuation-coordinator/worktrees/graph-ft-execute/dump/1031151632-graph-ft-execution/summary.json`, rows selected by j=1/budget=.001: full T271982/353792/353624; depth194958/222800/222764; widths13/13/7. `component_metrics`: A0/27270/27270, O182/182/14, S0=271800. All15 study rows=12 complete+3failed; tight j1/1e-4 search costs null. `artifact-hashes-final.json` SHA256 `6f20f0abb3870f251652f80a8b0ae860b67d02d5ff3719d4d83796ccb87132da`; each selected result/component/search QPY streamed and checked. | Review `78107e1`, evidence `b84b2df`, exact integration `4c58971`/`6d590a8`; edge(7,11), k3, xag_bennett/none, restoring Gray, clean workspace only. Original static dense4 limit unchanged. Numerical errors satisfy the original caller contract, not a general FT theorem. |
| E4, losses/break-even | Arithmetic353792−271982=81810,353624−271982=81642. Primary valid j0 T5810; H/j0 T0/proper success3/8. Actual full T-count uses T_A+j(2T_A+T_O+T_S0); full T-depth uses dependency graph. Separate final-source smoke reuses identical R2 primary emitted circuits. | `graph_ft_independent_review_20261031.md` and `graph_ft_integration_20261031.md`. First-peak schedules differ; no optimized cost/verified solution or achieved break-even. Verification, Clifford/runtime and physical overheads unpriced. |
| E5, separate RUS | `dump/1030020413-full-scope-continuation-coordinator/worktrees/dynamic-rus-execute/dump/1031201007-dynamic-rus-execution/{summary,cases}.json`; summary20cases/220branches. Select `forward-cap4` and `inverse-cap4`: completion255/256, expected T595/128=4.6484375 and149/32=4.65625, including abort. Scalar Fraction recount and observed sums agree within1e-12. | Review `d1a94e9`, integration `78c98a1`; one uncontrolled two-bit vertex, caps0..4, at most three serial calls/same register, untouched references. No multi-register graph, coherent quantum control or static A/A† substitution. Non-T unpriced. Naive-control purity .8125 from exact independent review, not a fresh experiment. Unlimited14/3 is analytical only. |
| E6, original noisy pilot | `dump/1030015553-noisy-channel-integration-triage/audit.json`, rows28, sum shots1792. Filter K3/j1, ordered seeds11/23/37/41/53: successes3/10/10/3/7, leakage37/28/24/34/33, each64shots. Original pilot manifest `f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278`. Saved per-circuit bitstrings/intervals remain at the original run. | Evidence review `672dc5f`, original source BLOCK separately superseded for corrected bytes by `efc74db`/integration `9a766b1`; source correction adds no shots. Noise conditional on frozen routing/calibration. Pointwise Wilson95% only; no seed pooling. Noisy counts are not ideal-state predictions. |
| E6, later current-root context | `docs/research/noisy_family_integration_20261109.md`, independently reviewed by `622269d` (`noisy_family_independent_review_20261109.md`, SHA256 `a9681ad0aeca395b5183eb8daf01608827c0a60707dbeb7617eec335c5134b1d`). New376histograms/24064shots; original28/1792 retained; total404records/25856shots;805−404=401 without admitted family observations at this admission. K3R1j2seed11 proper4/64=6.25%, Wilson2.46–15.00%, ideal99.9779%, unused37/64. | Exact source integration `fe6c498`. This draft hashes and cites the later restrictive review/decision; it does not re-recount all later histograms or rerun sampling. Totals are inventory arithmetic, not pooled statistics. One missing-receipt histogram withheld; width/timeouts/deferrals remain unmeasured. No C5noise/full-family/speedup admission. |

## Claim decisions

| Proposed language | Draft decision | What could change it |
| --- | --- | --- |
| Shared preparation/diffusion is cheaper under logic synthesis | Reject: all492 admitted matched details tie | Exact comparable emitted components with a real measured difference and independent review |
| R2 needs fewer C5 iterations | Support only at known M30 and these ideal first peaks; lower R2peak and both overshoots mandatory | Different graph/domain/discrete schedule may reverse the peak relation |
| 11 wires demonstrates overall superiority | Reject;84,441logical instructions, unmatched routing/FT | Matched context resource/cost-success evidence |
| All1608 MCX rows have coherent proof | Reject;84 whole rows lack full statevector checks | Wider template/translation proof and independent exact admission |
| Valid preparation reduces static T cost | Reject generalization; loses at matched j1 on admitted edge | Matched emitted schedules with verification/runtime objective and full precision coverage |
| RUS gives a graph-search improvement | BLOCK; one-vertex uncontrolled slice only | Independently reviewed multi-register flagged-abort marking/reflection instrument |
| Noisy simulations demonstrate resilience | Reject; poor K3counts and leakage retained | Completed relevant families with model/seed/uncertainty controls; still no hardware implication |
| Original22-wire structure pilot is independently admitted | PENDING under assigned handoff; exclude from draft figure | Exact saved977-instruction QPY clean-data absolute-phase/restoration proof, no automatic rerun |
| Final title/abstract/contribution or resubmission decision | Provisional/full gate BLOCKED | Full matched study, scientific final claims review and exact manuscript presentation review |

## Excluded and unrun obligations

These tables supply no new quantum runs, compiler invocation, noise shots,
density matrix, large operator, native build, notebook execution or historical
135-metric replay. They do not close full nine-graph strongest-baseline ranking,
larger CEC, common lowering, routed five-seed comparisons, full FT sensitivity,
profile/MCX ablations, selected/full-DIMACS five-repeat scaling, full noisy
first-lobe coverage, coherent graph RUS, or final-paper validation. Each remains
owned by its dispatcher chain and requires its own exact admission; older
zero-run snapshots are not assertions about all later workers. Hardware,
physical QEC, precolored and conditional-workspace research remain excluded.

Next: independent manuscript reviewer checks exactly this candidate's TeX,
generated rows, figure bytes, source index, copy-build/rendering and claim map.
The coordinator alone integrates independently admitted exact bytes. Any semantic
resolution needs new independent review. Existing final quantum/claim review
and future complete scientific gate remain separate. No worker push.

## Draft validation receipt

Final saved-data verification passed: **539 input/evidence SHA256s**,
230 component QPYs,492 matched ties,378 summaries,ten C5 rows,MCX review
coverage,all15 original graph-FT statuses and saved circuits,finite-cap RUS
expectations,and the original noisy pilot inventory. It used scalar arithmetic
and streaming hashes only:0.408492s,29,425,664bytes child high water.
No quantum libraries were imported by the verifier; only the candidate core
package import was asserted. The later family observations are attributed to
their exact independently reviewed report, not newly reclassified here.

The final new offline Tectonic0.17.0 copy build passed in10.828094s,
351,993,856bytes child high water, producing six pages. Saved Quantikz sources
were copied and hashed. PDFKit rendering passed in4.558750s,
602,423,296bytes child high water. The title/status and evaluation tables/figure
were visually inspected; captions, decimals, axes and losses are readable.
The final PDF/rendered images and extracted text stay in the new local checkpoint.
Font substitutions and inherited/new minor box warnings remain in the TeX log;
this is draft inspection, not camera-ready typography or independent admission.
Selected Black and Ruff pass; no library tests or final-paper checks are claimed.

Budget declared before work:120s/child,300s cumulative numerical,1GiB declared
process budget,serial numerical/compile work and configured thread counts1.
There were no statevectors,dense operators,density arrays,compiler experiments
or new shots. Darwin wait4 is terminal child high water,possibly including
reaped descendants; it is neither a hard allocation cap nor live/group RSS.
The unchanged prescribed native executable was hash-checked,never invoked.

The first TeX copy failed with a table-input closing-rule error; its source,
log and exit1 receipt remain in the earlier run. The corrected table input
uses the primitive input command. Both subsequent successful copies are
preserved. Atomic documentation patches that failed matching context changed
no bytes; corrected smaller patches succeeded. Read-only inspection commands
have transcript exits but no separate RSS measurement. The dispatcher interruption
is not a scientific failure. No old source,PDF,README,pin,history,archive,
candidate/review result,failed artifact or queue state was overwritten.
