# Independent manuscript/background review — 28 October 2026

**Decision: ADMIT the exact four-file results-independent revision below.**
This admits its background attribution, notation, methodological contracts and
explicit pending-evaluation framing. It does **not** admit experimental results,
new circuit correctness, comparative superiority, protocol freeze, broader
FT/RUS/ideal-amplitude claims, a successful PDF build, or the final paper.
The bounded review task is complete; full revision scope remains open.

Task: `manuscript-background-review-1028023823`; session ID not exposed.
Review branch: `codex/coloring-manuscript-background-review-1028023823`.
Review intake: `fc734b386449e69716d0ac3018b878a23e05ba95`.
Candidate worktree:
`/Users/mar/codex-work/logique/dump/1028023823-full-revision-implementation-coordinator/worktrees/manuscript-primary-background`.
Candidate source commit: `9a980ec7048c4b8b91b872a15cd19d173bf182e1`;
checkpoint commit/HEAD: `aa3334f1836d3543ee40fb76cf907658ad7100ae`.
Candidate status was clean. Completion of that worker was not used as evidence
of scientific admission.

Evidence/checkpoint directory in this review worktree:
`dump/1028125156-manuscript-background-review/`, created with
`logique.paths.new_dump_directory` using the actual candidate source.
`checks.json`, `check-command.json`, `check_review.py`, `web1.json` through
`web6.json`, and `checkpoint.json` retain identities, checks, retrieval evidence,
resources, failures and the next action. Browser extracts identify retrievals,
not full publisher PDF bytes. Review commit identity is recorded after commit
in the timestamped checkpoint, avoiding a self-referential document hash.

## Exact admitted bytes

Each SHA256 matches the live candidate, its source-commit Git blob, and the
worker checkpoint/manifest. Changed bytes require a new bounded decision.

| Candidate-relative path | SHA256 |
| --- | --- |
| `docs/manuscript/conference.tex` | `7d0c06583a3ae0cf759ecf20e3114e28a9324c24c62fe482258576c8ba727969` |
| `docs/manuscript/refs.bib` | `2ba64b3a2ad750eb47d62153f9a7839c19ab7e196cb5951bd46146a91ee152a1` |
| `docs/research/primary_source_revision_20261028.md` | `556375307aa310f7f4e098833f4590d6ab85da077f607ffc3728b2d68db58450` |
| `docs/research/reviewer_response_map.md` | `35ec2562655d5ed292bc81be32d5ad0c9f594e19ca3e60ab5b8c00df2725b79b` |

Candidate `MANUSCRIPT_BACKGROUND_CHECKPOINT.md` SHA256:
`0dc39d3d334dfb99d542018bfaa87e22dfedd3dc59a13481b87f7c9f1116d91a`.
All 14 evidence files listed inside the worker manifest and all nine listed
source/admission context hashes matched. This authenticates the retained
evidence identities; it is not a replay of their experiments.

## Actual review and primary-source support

Read AGENTS.md, CLAUDE.md and the 671-line full plan in full, followed by the
renewed resumption and full-batch documents. Read the actual candidate TeX,
changed bibliography entries, ledger and reviewer map; inspected the four-file
change set and bibliography diff, and verified the preserved original manuscript
identity. Historical narrow authority is not treated
as a restriction on the renewed plan. This review owns only its report and
new timestamped evidence, not the candidate manuscript or integration branch.

The following checks were made directly against primary sources on 28 October.
The scope column states the attribution checked, not endorsement of the cited
authors' empirical results or every theorem in their papers.

| Citation(s) and directly checked source | Supporting location and bounded finding |
| --- | --- |
| [Schmitt et al., DATE 2021](https://past.date-conference.com/proceedings-archive/2021/pdf/2010.pdf) (`DATE21`) | Abstract and IV–V: automated Python-function compilation, preparation, XAG/LUT oracle synthesis, cleanup and Zed-city coloring. The revised credit is accurate; treating this as manual-only prior work would be wrong. |
| [Yu et al., ASP-DAC 2025](https://si2.epfl.ch/~demichel/publications/archive/2025/ASPDAC25_YU.pdf) (`YuBackend2025`) | Abstract/introduction: XAG structure related to back-end T count, time steps and helper qubits. The manuscript does not claim to reproduce the physical/QEC model or their improvements. |
| [Häner–Soeken](https://arxiv.org/abs/2006.03845) (`HaenerSoekenDepth`) | Abstract: multiplicative depth, cut enumeration, tree balancing and ESOPs. Balancing is correctly attributed, not presented as new. |
| [Meuli et al., ICCAD](https://arxiv.org/abs/1908.01609) and [npj paper](https://www.nature.com/articles/s41534-021-00514-y?error=cookies_not_supported&code=review) (`XAGCompilation`, `XAG_npj`) | Abstracts: minimum AND complexity versus a supplied network, and alternative qubit/T-count/T-depth objectives. No canonical-XAG or universally cheapest mapping claim remains. |
| [Campbell–Khurana–Montanaro](https://arxiv.org/abs/1810.05582v2) (`CampbellColoring`) | Abstract and journal metadata: coloring/constraint satisfaction, Grover/backtracking and fault-tolerant overheads. Prior coloring cost analysis is credited without adopting its performance estimates. |
| [Mukherjee](https://arxiv.org/html/2108.09061v2) (`MukherjeeList`) | Introduction explicitly describes restricted initialization and diffusion, distinguishing plausible assignments from proper colorings. The ledger appropriately does not borrow its printed query formula as the derivation of this manuscript's success formula. DOI independently cross-checked on the arXiv abstract record. |
| [Levin](https://www.techscience.com/jqc/v6n1/56255/html) (`LevinUniform`) | Introduction, Eq. (1), coloring application and diffuser discussion support arbitrary-domain uniform preparation and coloring use. No precision-independent Clifford+T result is attributed. |
| [Shukla–Vedula](https://arxiv.org/abs/2306.11747v2) (`Shukla2024`) | Abstract: consecutive-state uniform preparation and logarithmic gate/depth scaling with no ancillas in its gate model. The candidate explicitly distinguishes rotations/controlled Hadamards from Clifford+T costing. |
| [Sen–Mukherjee](https://arxiv.org/html/2609.32348v1) (`SenMukherjee2026`) | Authors, title and 26 September 2026 version verified; abstract covers binary encoding and Grover/QAOA/annealing; VI-F explicitly identifies one small simulated graph. The restrained description does not certify that paper's reductions or rank it against this flow. |
| [Barenco et al.](https://arxiv.org/abs/quant-ph/9503016) (`Barenco1995`) | Foundational controlled-gate attribution and bibliographic identity verified. Named decomposition baselines are not represented as newly validated implementations. |
| [Iten et al.](https://arxiv.org/html/1501.06911v4) (`Iten2016`) | Appendix A, Lemma 8 and its action/reset construction support the borrowed-system-wire lineage. No unconditional phase/restoration certificate for a local adapter is inferred. |
| [Maslov](https://arxiv.org/html/1508.03273v2) (`Maslov2016`) | Phase-preserving substitution identities and IV's four-T relative-phase examples support selected gadget costs and the composition caveat. |
| [Vale et al.](https://arxiv.org/html/2302.06377v1) (`Vale2024`) | SU(2) restriction verified. Since det(X)=-1, the manuscript correctly requires any necessary controlled-phase correction for an MCX policy. It does not identify X with an SU(2) gate. |
| [Khattar–Gidney](https://quantum-journal.org/papers/q-2025-05-21-1752/) and [Dutta et al.](https://arxiv.org/html/2502.01433v3) (`KhattarGidney2025`, `toffoli_decomposition`) | Conditional knowledge, limited clean space/dirty variants, and clean-space/Toffoli-depth trade-offs are supported. No universal restoring logarithmic-depth charge is adopted. |
| [Amy et al.](https://arxiv.org/html/1206.0758v3) (`Tcount`) | Abstract, Fig. 13 discussion and Section 6.4 support the selected seven-T/three-T-layer Toffoli. The manuscript does not assert optimality across all ancilla or measurement models. |
| [Ross–Selinger](https://arxiv.org/abs/1403.2975v3) and [Paetznick–Svore](https://arxiv.org/abs/1311.1074v2) | Fixed Clifford+T approximation versus measurement-conditioned trials is correctly separated. Classical randomized synthesis is not quantum RUS. Journal volume/pages and arXiv identifier DOIs agree with the new entries. |
| [Saha et al.](https://arxiv.org/abs/2009.06073) and [Belletti et al.](https://re.public.polimi.it/handle/11311/1294152) (`saha`, `belletti`) | Author abstracts support comparator coloring and subsequent width/depth variants. These citations do not prove the maintained baseline implementation correct. |
| [Grover](https://arxiv.org/abs/quant-ph/9605043) (`grover`) | Query improvement for unstructured search supports the limited introduction claim; it does not establish advantage over the best classical coloring algorithm. |

The 22 active citation keys resolve to distinct existing bibliography keys.
The 28 uncited historical entries were retained; this is not a comprehensive
copyedit or renewed certification of those inactive references. The ledger
distinguishes preprint and journal metadata where titles differ. Its local
construction counts and RUS extension are not misattributed as published
coloring improvements.

## Mathematical and implementation-contract assessment

1. **Encoding and marking — pass.** `subsec:encoding` defines LSB-first
   `x_{v,i}`, includes isolated vertices, distinguishes `b_v<k` from edge
   inequalities, uses true empty conjunctions, and retains the maintained
   one-bit convention at k=1. Complete `f` marks proper colorings; edge-only
   `f_E` has equivalent coloring semantics only on valid-code support. The
   baseline label/bit translation requirement is explicit. The constructive
   bound `|E|(c-1)+|E|-1=|E|c-1` applies only to nonempty edge sets and excludes
   domain checks; it is neither a minimum-AND nor qubit-count claim.
2. **Preparation and reflection — pass.** For ideal prepared state `a=A|0>`,
   `D=2|a><a|-I=A S0 A†`. A vector in the valid-code subspace remains there
   under the diagonal oracle and under `D`, proving the stated ideal R3
   redundancy. This does not prove the same support for an approximation.
   With the stated MCZ convention, `-X^n MCZ X^n` gives the stated `S0` sign.
   `Q=D O_f` acts as O, A†, S0, A after one initialization. The full data
   preparation is used, and workspace must be restored. The n-1 diffusion
   controls remain explicit. Zero-data algorithm execution is not admitted.
3. **Iterations — pass.** In the good/bad plane, initial amplitudes are
   `(sin(theta),cos(theta))`; the oracle and matching reflection rotate them
   to `(sin(3 theta),cos(3 theta))`, giving the stated `(2j+1)theta` formula.
   R1 uses `2^n`, ideal R2/R3 use `k^|V|`, and arbitrary preparation uses its
   actual marked probability. Floor/ceiling first-peak candidates, smaller-j
   ties, p=0/1 and unknown-M treatment are consistent with the retained
   analytical admission. They do not optimize cost per success or later lobes.
4. **Static costs versus RUS — pass.** Counting the actual concatenation gives
   `T_A+j(2T_A+T_S0+T_O)` at a fixed selected precision, not a T-depth formula.
   Reusing the emitted inverse and charging all repeated/preprocessing errors
   are explicit. Tolerances are requested, not measured. Seven-T exact and
   four-T relative-phase gadgets are selected constructions requiring the
   stated phase proof. Measurement-assisted cleanup is not free static
   uncomputation. Local k=3 RUS accounting is analytical, with forward/inverse
   channels, branch phases and aborts requiring their separate contract.
5. **Workspace and Figure 1 — pass at source/semantic level.** The four-control
   tree computes pairwise ANDs into two scratch wires before the target action;
   the five-control tree uses a third intermediate AND. Both leave garbage.
   Caption and text restrict the displayed equivalence to target action and
   require the actual expanded inverse on the held scratch after a compatible
   intervening block. Final marking/diffusion require their own restoration;
   dirty/conditionally clean workspace is not confused with fresh zero space.
   This is a reading of the diagram source, not a rendered-layout check or
   new quantum experiment.
6. **Actual maintained source — pass for descriptive consistency.** Read
   candidate encoding, synthesis API/result and native mapping source and
   `circuits/grover.py`. Checked generic StatePreparation, the signed main
   Grover assembly, compute-Z-actual-inverse wrapper, method defaults and
   explicit common preprocessing. `tools/generate_paper_benchmarks.py`
   actually imports UniformSuperpositionGate; the installed gate source
   identifies Shukla–Vedula. Historical kickback/replay retains its different
   diffusion convention and is not retrospectively certified by this prose.

## Existing admissions remain narrow

All **15** `docs/research/*admission.md` files in the candidate equal their
`fc734b3` Git blobs; their individual SHA256s are in `checks.json`. Inspected
the relevant contracts and compared the revised text against their limits:

| Existing decision | Boundary retained by this review |
| --- | --- |
| Rotation/norm admission | Original numeric recursive targets; one-qubit matrix defect at most 64 eps; depth 32, angles within +/-2pi, precision floor 1e-12, bounded SK and caller guards. This is not Ross–Selinger optimal synthesis, an interval certificate or an ideal-amplitude guarantee. Semantic oracle/mapping/S0/restoration obligations remain external. |
| Static FT pilot | Fixed isolated-vertex numerical assembly evidence only. Its edge case's 13-wire versus four-qubit dense limit failure remains; no meaningful graph comparison or achieved break-even follows. The general host maximum of five dense-operator qubits does not enlarge that pilot's four-qubit contract. |
| Analytical RUS ledger | Ideal scalar-Kraus accounting, retry phases, once-only inverse prefix, expected/conditional/abort costs and unpriced operations remain separate; no dynamic execution or coherent-control admission. |
| Preparation break-even, success threshold and guide | Supplied-cost/probability accounting and caller comparability/renewal assumptions only; zero/unknown distinctions remain. No attained graph threshold or preparation advantage is claimed. |
| Corrected analytical ideal ledger | Exact-count bounded first-lobe decision; displayed probabilities are numerical. It is not an executed-state or noise certificate. |
| Executed ideal iterations | Only the admitted sequential clean-workspace pilot: 34 completed cases/151 rows; C5 k3 R1/R2 remain infeasible at 22>18 wires, C5 R3 at 17 wires. These are retained historical admission facts, not new measurements in this review. No noisy/FT/RUS or general amplitude extension. |
| QPY, restoring MCX, structure sequential/parallel | Exact reviewed bytes and their individual semantic/serialization, clean-workspace and logical scheduling limits; no retrospective blessing of old QPY failures, unrestricted lowering or physical timing. |
| Component width/instruction/depth | Post-assembly acceptance gates only, not complete process/allocation controls or protocol freeze. |

The new prose removes old headline percentages, claimed device fit and live
hardware figures/results. There are no live `includegraphics` references to
those old plots, first-time claim, blanket superiority claim or whole-Grover
MCT-free claim. Historical images/results remain outside the live evaluation.
Abstract, introduction, evaluation and conclusion explicitly leave resource
rankings, noise, scaling and contribution judgments open. The reviewer map's
17 referenced labels exist and describe the actual revised sections.

The full nine-graph/five-method/four-baseline R1–R3 comparison, decomposition
3–20-control study, profiles/ablations, five routing seeds, iteration/leakage/
random/confidence/cost-success work, selected-DIMACS five-repeat scaling,
meaningful graph FT and separate dynamic RUS remain required. Native
value/restoration blockers are not solved by this document. No findings from
other unintegrated workers are promoted here.

## Validation, limits and handoff

Independent `check_review.py` passed: four candidate/commit/checkpoint identities,
14 worker-evidence identities, nine context identities, 15 unchanged admission
documents, 22 cited keys, 50 unique bibliography keys, 22 unique labels, all
references/map labels, balanced TeX environments/braces and obsolete-claim
checks. Candidate source diff whitespace check passed. It is a bounded source
checker, not a TeX engine or complete BibTeX parser. The mathematical assessment
above is independent reasoning; no numerical research or circuit replay ran.

The check used `/Users/mar/codex-work/logique/.venv/bin/python`, explicit
candidate `PYTHONPATH` with asserted `logique.paths.__file__`, the required
cache and all numerical thread limits set to one. Text reads were guarded
below 1 MiB. One check child: 20-second external timeout, 256 MiB declared
memory budget, within a 60-second cumulative validation envelope. Actual child
time 0.3458904577 s; boundary wall 0.3717270410 s; measured self peak RSS
22,642,688 bytes on Darwin. Memory was assessed against self RSS, not enforced
as an address-space cap; no process-group RSS is inferred. No numerical arrays,
statevectors, Operators, native executable or compiler ran. Native binary SHA
verification was therefore inapplicable to this review.

`latexmk`, `pdflatex`, `lualatex`, `xelatex`, `tectonic`, `bibtex`, `biber` and
`chktex` are absent on PATH. The worker's failed build attempt is retained and
its unavailability independently checked. **PDF/BibTeX compilation and typeset
visual validation remain unperformed.** No installation or network TeX build
was attempted. This does not block a source-level background admission, but it
does block claiming a validated final PDF. Existing DAC'26 metadata/placeholder
DOI/ISBN must be replaced for the eventual venue. The full-plan literature
completion can additionally supply dedicated pebbling/LHRS/exact-synthesis
citations; this decision does not declare the final background exhaustive.

Operational limitations/failures: combined long reads were truncated and
followed by focused reads; exploratory nonexistent `circuits/preparation.py`
and `synthesis/expression.py` searches failed before locating the actual replay
path. Nature's initial fetch redirected unsuccessfully; the public article
was retrieved with its cookie-error URL. Quantum's Campbell page timed out on
follow-up; the author arXiv record supplied the checked attribution. These web
failures remain in the saved extracts. No failed scientific check, timeout or
OOM is concealed. Git commit handling and final hashes are in `checkpoint.json`.

**Next action:** the coordinator may integrate source commit `9a980ec` only if
these four hashes still match, and preserve this bounded review. Keep the
worker checkpoint in its original worktree. Run an offline TeX/BibTeX build and
visual inspection when a toolchain is available; obtain separate exact-hash
decisions for evaluation results and final claims. Dispatcher alone publishes
integration HEAD. This reviewer does not integrate or push and has no remaining
own scientific check. Root README edits, histories, archives, pins, saved
failures and old outputs were not edited. No models/subagents/Codex, API/credits,
purchases, hardware, physical QEC, precolored research or conditional-workspace
synthesis were launched. The full plan remains open.
