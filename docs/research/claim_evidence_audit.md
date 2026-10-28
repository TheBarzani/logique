# Claim–Evidence Audit for "From Graph k-Coloring to Grover's Circuits via Logic Synthesis"

This audit maps each claim of the DAC 2026 manuscript (`docs/manuscript/conference.tex`) and each concern of the DAC
reviewers (`docs/research/DAC_2026_Reviewer_Feedback.md`) to the implementation and experiment that support it, the
assumptions behind it, its current status, and the evidence that must replace it. Task numbers refer to the approved
revision plan (`docs/coloring-paper-revamp-codex-plan.md`). Hardware executions are outside the revised paper,
so claims that rest only on them are marked for removal rather than re-examined.

The status of each claim is one of the following:

- **Supported**: the claim follows from the implementation and the archived data.
- **Qualified**: the claim holds only in a narrower sense than stated.
- **Not supported**: the claim depends on accounting choices or data that do not establish it.
- **Incorrect**: the statement contradicts the implementation or the literature.
- **Removed**: the claim depends on evidence outside the revised paper.

## 1. Archived Evidence Used by the Manuscript

The resource figures and the improvement table come from
`experiments/manuscript/legacy/data/output/benchmark_results.csv`, which the maintained replay
(`tools/generate_paper_benchmarks.py`) reproduces exactly (135 of 135 values). The replay makes the following choices,
which this audit treats as the assumptions behind every resource claim.

1. The proposed circuit prepares valid color codes with the Shukla–Vedula construction but reflects about the Hadamard
   state. On the unprecolored K₃ graph, one iteration then reaches a success probability of 47.9% and leaks 30.1% of the
   probability into unused codes, whereas reflecting about the actual preparation reaches 99.0% with no leakage. With
   the matching reflection, the K₃ costs under the historical accounting become 11 qubits, depth 34 and 79 gates,
   instead of the archived 11, 30 and 73.
2. The baselines are built by the `saha_belletti` package with one-based vertex labels (`preserve_labels=True`). The
   package maps a label i to the qubits qn·i to qn·(i + 1) − 1 (`saha_belletti/problem.py:92-100`), so the register of
   the last vertex falls into the ancilla region for every variant, and the `original` variant additionally skips the
   edges incident to the last vertex (`saha_belletti/original.py:108-114`).
3. Width adds n − 2 ancillas for every n-control gate except the last, summed over the whole circuit. This allowance
   corresponds to the throwaway-ancilla decomposition of Figure 1, whose ancillas are held until the mirrored gate of the
   uncompute phase restores them; the sum therefore counts each held ancilla twice. The proposed circuits receive no
   allowance because they contain no gate with more than two controls outside the diffusion operator.
4. Depth uses a patched Qiskit function that assigns ⌈log₂ n⌉ to each n-control gate and one unit to every other gate,
   including Toffoli gates, controlled rotations and the UQS rotations (`tools/patch_qiskit_depth.py`).
5. Gate counts use `len(circuit)`, which includes barriers and measurements; the baselines are measured and the proposed
   circuits are not.
6. Precolors present in the nine benchmark files are removed, and the proposed predicate checks only edge
   inequalities.

Counted by allocated qubits alone, the proposed flow uses about twice as many qubits as the baselines (archived
September 2025 table). Against the best baseline on each graph, the archived data give a mean width reduction of 27.4%
(proposed wider on 3 of 9 graphs: 2-Insertions_3, zed-city_2019 and myciel3), a mean depth change of −13.1% (proposed
deeper on 6 of 9 graphs: 2-Insertions_3, zed-city_2019, myciel5, myciel4, K₂₀ and K₃) and a mean gate reduction of
33.6% (no losses).

## 2. Claims of the Manuscript

| # | Claim (location) | Evidence and assumptions | Status | Replacement evidence |
|---|---|---|---|---|
| 1 | Existing Grover circuits for coloring rely on MCT gates whose decomposition incurs large overheads (abstract, introduction) | Baselines contain multi-controlled gates; overheads were estimated analytically, not decomposed | Qualified | Explicit decompositions of every multi-controlled gate (Task 3) |
| 2 | The flow generates MCT-free Grover circuits (abstract, Section 3, conclusion) | The oracle contains only gates with at most two controls; the diffusion operator retains an (n − 1)-control gate (`circuits/grover.py`) | Qualified | Restrict the claim to the oracle; decompose the diffusion gate with the same policy for every flow (Task 3) |
| 3 | Edge constraints are compiled into GF(2) functions designed to avoid multi-fan-in AND gates (abstract, Section 3.2.1) | Algorithm 1 writes n-ary conjunctions and disjunctions; two-input gates arise from the XAG representation, not from the function | Qualified | Describe the encoding and its AND count (c − 1 per edge, \|E\|·c − 1 in total) precisely (Task 4, analytical model) |
| 4 | UQS preparation restricts the search to valid colorings and improves success probability (abstract, Section 3.3) | Preparation is correct, but the evaluated circuits reflect about the Hadamard state (Section 1, item 1) | Not supported as evaluated | Matching reflection in every flow; success versus iteration count (Tasks 2 and 7) |
| 5 | Depth and width are reduced by 49.4% and 41.7%, and gate count by 60.1% (abstract, Section 4.3, conclusion) | Section 1, items 2–5; averages over all four baselines, including Belletti-Minimal, and truncated (41.79, 49.46, 60.16) | Not supported | Per-graph comparison against the strongest fair baseline under three regimes (Task 4) |
| 6 | The flow is the first end-to-end automated framework of its kind (introduction) | Schmitt et al. (DATE 2021) compile Boolean functions to quantum circuits through XAGs and demonstrate a coloring oracle; Mukherjee (2021/2022) and Levin (2024) combine restricted preparation with coloring | Incorrect | Remove; position against prior work (plan, Section 1.3) |
| 7 | Contribution: a constraint-to-Boolean-function compilation algorithm (introduction) | Algorithm 1 is a direct encoding | Qualified | Present as the encoding of the analytical resource model rather than as an algorithmic contribution |
| 8 | Contribution: integration of state-of-the-art UQS preparation (introduction) | Restricted preparation with a matching diffusion operator exists in prior work | Qualified | Quantify its effect through regimes R1–R3 (Task 4) and its fault-tolerant cost (Task 6) |
| 9 | An n-control MCT needs at least ⌈log₂ n⌉ depth and n − 2 dirty ancillae; Figure 1 shows the decomposition (Section 2.1) | Figure 1 shows a throwaway-ancilla tree (clean ancillas left in a garbage state); the caption calls them dirty | Incorrect label | Relabel; state the validity condition; compare with other decompositions (Task 3) |
| 10 | Costs are measured over Clifford+Toffoli, an extension of Clifford+T, with Toffoli decomposed by its optimal ancilla-free construction (Section 2.1) | Toffoli gates count as one unit; multi-controlled gates receive analytical weights; Clifford+Toffoli is not an extension of Clifford+T | Incorrect | Explicit Clifford+T lowering with T-count and T-depth (Task 3) |
| 11 | Grover's algorithm needs ⌊(π/4)√N⌋ iterations (Sections 2.2 and 3.4) | Ignores the number of solutions M and the restricted domain size N = k^\|V\| | Incorrect | Iteration count from the solution fraction (Tasks 3 and 7) |
| 12 | The diffusion operator is U_Ψ†(2\|0⟩⟨0\| − I)U_Ψ (Section 3.4) | Operator order is reversed with respect to the stated sequence; the evaluated circuits used a Hadamard reflection | Incorrect | A(2\|0⟩⟨0\| − I)A† with A the actual preparation |
| 13 | The XAG is a canonical representation (Section 3.2.2) | XAGs are not canonical | Incorrect | Remove |
| 14 | The oracle marks invalid colorings (Sections 3.2.3 and 3.4) | The implemented predicate is true on proper colorings, which are marked | Incorrect | State that valid colorings are marked |
| 15 | The benchmark suite contains complete graphs K₃ to K₂₀ (Section 4.1) | Only K₃, K₅, K₁₀ and K₂₀ are evaluated | Incorrect | State the actual suite and add controlled scaling families (Task 8) |
| 16 | On K₁₀, the flow outperforms Belletti-Simple by at least 3× in width, 1.4× in depth and 1.8× in gate count (Section 4.3) | Archived ratios are 3.05×, 1.31× and 1.76×; all three depend on the accounting of Section 1 | Not supported (depth ratio overstated) | Recompute under the explicit cost model (Task 4) |
| 17 | Belletti-Simple achieves better depth on some instances (up to 1.7× on myciel5), while the flow keeps better width (1.7×) and gate count (1.5×) (Section 4.3) | Archived depth ratio is 1.79×; Belletti-Simple is shallower on 5 of the 9 graphs and ties on one; Saha et al. is also shallower on K₃ | Qualified | Report all losses explicitly (Tasks 4 and 5) |
| 18 | Belletti-Simple circuits for myciel5 and K₂₀ do not fit IBM's 1,121-qubit Condor processor, whereas the proposed circuits do (Section 4.3) | Based on qubit counts with the width allowance, without connectivity or routing | Not supported | Remove; report routed metrics where circuits fit (Task 3) |
| 19 | The advantage grows for k > 4 because baselines need larger MCT gates for comparison and invalid-color detection (Section 4.3) | Plausible mechanism; not isolated from the preparation and accounting choices | Qualified | Regimes R1–R3 and width breakdown by qubit role (Task 4) |
| 20 | Avoiding MCT gates during synthesis is a fundamentally more efficient compilation strategy (Section 4.3, conclusion) | A comparator built from logical-AND gates uses the same c − 1 AND gates per edge; no controlled comparison exists | Not supported | Mechanism study (Task 5) and evidence gate (plan, Section 5) |
| 21 | Hardware runs on IBM Heron-r1 show improved success probabilities and noise resilience (abstract, introduction, Section 4.2, conclusion) | Hardware is outside the revised paper | Removed | Simulated success versus iteration count (Task 7) |
| 22 | Applications of k-coloring in chemical storage, power systems and compilers (abstract, introduction) | Cited background | Supported | — |

## 3. Reviewer Concerns

| Reviewer concern | Related claims | Replacement evidence |
|---|---|---|
| Novelty beyond a combination of existing techniques (Reviewers 1, 2 and 3) | 6, 7, 8, 20 | Explanatory research question; regimes R1–R3 (Task 4); mechanism study and structure-aware oracle (Task 5) |
| Why the width is lower despite ancillas (Reviewer 1) | 5, 9, 19 | Peak-workspace accounting (Task 3); width breakdown by qubit role (Task 4) |
| Accuracy for larger graphs and more iterations (Reviewer 1) | 4, 21 | Success versus iteration count with ideal, noisy and random-sampling references (Task 7) |
| Width overhead of MCT decomposition versus the proposed approach (Reviewer 1) | 9, 10 | MCX decomposition study (Task 3) |
| NISQ acronym and x/v notation (Reviewer 1) | — | Manuscript revision |
| T-count, T-depth and mapped two-qubit counts (Reviewers 2 and 4) | 10 | Clifford+T lowering and routed metrics (Task 3) |
| Runtime and XAG size as graphs grow (Reviewer 2) | 15 | Scalability study (Task 8) |
| Better MCT decompositions, such as conditionally clean ancillae (Reviewer 3) | 1, 9 | Khattar–Gidney and other decompositions (Task 3) |
| AIG and k-LUT representations; LHRS, Bennett and best-fit strategies (Reviewer 3) | 20 | Design space of the five existing methods and additional strategies (Task 5) |
| Balancing on the XAG (Reviewer 3) | 17 | Optimization profiles, credited to Häner and Soeken (Task 5) |
| Rotation cost of UQS in fault-tolerant settings (Reviewer 4) | 4, 8 | Whole-algorithm error budget and complete-search cost (Tasks 3 and 6) |
| Multi-controlled behavior of the diffusion operator (Reviewer 4) | 2 | Same decomposition policy for every diffusion operator (Task 3) |
| Belletti-Simple outperforms the flow on some instances (Reviewer 4) | 17 | Depth-oriented profiles and parallel clause scheduling (Task 5) |
| Scalability is an open question (Reviewer 4) | 15 | Scalability study (Task 8) |

## 4. Consequences for the Revision

No headline percentage of the manuscript can be retained, because each depends on the accounting of Section 1 and on
baseline circuits built with mismatched labels. The qualitative claims that survive are narrower: the oracle contains no
gate with more than two controls, valid-color preparation removes unused codes from the search space, and the
synthesized oracle is verified against an independent coloring predicate. Every quantitative comparison must be
regenerated under the semantic contract and the explicit cost model of the experimental protocol, and the comparison must
be stated against the strongest baseline on each graph.


## 28 October: bounded executed ideal-iteration evidence

The [exact-hash independent review](iteration_study_review.md) and
[integration admission](iteration_study_admission.md) add actual ideal-only
saved-circuit execution: 34 graph/regime cases, 151 iteration rows, including
K3 k3 R2 j1 success 0.9903978052126163 and path8 k2 R1 j1 success
0.06885528564453086. This supports matching-reflection behavior only within
the reviewed clean-workspace construction and numerical tolerance. C5 R1/R2
remain unexecuted (22 wires > 18); their requested sweeps remain open.

This evidence does not replace the historical claims in rows 4/11/21, certify
arbitrary ideal amplitudes or FT/RUS preparations, or establish noisy success,
shot confidence, random-trial costs, comparative savings or paper approval.
Analytical random references remain distinct from execution. Full Task7 and
the paper's evidence gate remain open.


## Scaling integration triage — 28 October

The completed independent review BLOCKS the scaling process/resource contract:
late child completion can bypass its timeout, and wait4 RSS is mislabeled as
isolated direct-child memory. Coordinator reproduced both failures (2 failed);
the existing focused suite still passes 105 tests. All scaling implementation
commits remain withheld. See [triage](scaling_study_triage.md) and the
[byte-preserved review](scaling_study_review.md). The saved 110-attempt five-repeat
tiny compiler pilot is neither a complete DIMACS scaling study nor quantum
circuit correctness evidence. Original metrics, missing/unsupported input ledger,
unknown larger counts and 145 mapping-suite failures remain explicit.

Checkpoint: `dump/1028012936-scaling-integration-triage/batch.json`. This dependency
triage is COMPLETE; `continue-full-revision-1028004102` owns a bounded B1/B2
correctness correction -> independent exact-hash re-review -> integration chain
and subsequent full-scope priorities. No duplicate queue/coordinator jobs were
added. The executed-iteration chain and its bounded admissions are unchanged;
full paper and full Task8 remain open.
