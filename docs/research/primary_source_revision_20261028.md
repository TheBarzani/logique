# Primary-source manuscript revision — 28 October 2026

Task `manuscript-primary-background-1028023823`; results-independent writing only.
The renewed full plan governs. No numerical experiment, new model, hardware job,
installation, sync, dependency change, or publication was performed. Independent
exact-hash claim review follows this batch; the full manuscript is not approved.

## Retrieval and scope

Sources were opened with the browsing tool on 28 October 2026. The timestamped
run `dump/1028124044-manuscript-primary-background/` retains browser-returned
primary-source extracts in `logic-primary.json`, `preparation-primary.json`,
`workspace-primary.json`, `cost-primary.json`, and `additional-primary.json`.
These are retrieval evidence, not local copies or SHA256 identities of the full
publisher PDFs. Their byte hashes are bound in `MANUSCRIPT_BACKGROUND_CHECKPOINT.md`
and the run manifest. Titles, URLs, identifiers, and bounded paraphrase notes
below identify exactly what each citation supports. No secondary summary is
used as technical proof; search results served only to locate primary sources.
The ledger does not certify any source's experiments or transplant its metrics.

## Logic synthesis and coloring costs

- **DATE21 — Schmitt, Mozafari, Meuli, Riener, De Micheli (2021), “From Boolean
  functions to quantum circuits: A scalable quantum compilation flow in C++.”**
  [Official DATE proceedings PDF](https://past.date-conference.com/proceedings-archive/2021/pdf/2010.pdf),
  DOI `10.23919/DATE51398.2021.9474237`. Abstract and Sections IV–V establish
  automated Python-function compilation, XAG/LUT synthesis, cleanup, and the
  Zed city coloring example. The old live description as a manual-only flow was
  incorrect. This source defeats a first-automated-coloring-flow claim; its own
  experimental ratios are not adopted.
- **YuBackend2025 — Yu, Tempia Calvino, Soeken, De Micheli (2025), “Back-end-aware
  Fault-tolerant Quantum Oracle Synthesis.”**
  [Author-hosted ASP-DAC paper](https://si2.epfl.ch/~demichel/publications/archive/2025/ASPDAC25_YU.pdf),
  DOI `10.1145/3658617.3697776`. Abstract and introduction link XAG structure to
  back-end T count, logical time steps, and helper qubits. Supports positioning
  and the need to declare a back-end objective, not claimed replication,
  superiority, or physical-QEC estimates in this work.
- **HaenerSoekenDepth — Thomas Häner and Mathias Soeken (2020), “Lowering the
  T-depth of Quantum Circuits By Reducing the Multiplicative Depth Of Logic
  Networks.”** [Author preprint](https://arxiv.org/abs/2006.03845),
  DOI `10.48550/arXiv.2006.03845`. Abstract defines multiplicative depth and
  identifies cut enumeration, tree balancing, and ESOP representations. Cite
  the verified preprint as such; no new balancing priority is claimed here.
- **XAGCompilation — Meuli, Soeken, Campbell, Roetteler, De Micheli (2019),
  “The Role of Multiplicative Complexity in Compiling Low T-count Oracle Circuits.”**
  [Author preprint](https://arxiv.org/abs/1908.01609), published DOI
  `10.1109/ICCAD45719.2019.8942093`. Abstract distinguishes the minimum AND count
  of a function from a supplied network count and describes qubit/T trade-offs.
  Its low-T construction does not license free static uncomputation here.
- **XAG_npj — Meuli, Soeken, De Micheli (2022), “Xor-And-Inverter Graphs for
  Quantum Compilation.”** [Publisher paper](https://www.nature.com/articles/s41534-021-00514-y),
  DOI `10.1038/s41534-021-00514-y`. Abstract and Methods present multiple
  XAG mappings targeting different resources. Supports non-uniform costs across
  networks/mappings; no canonical XAG or universal advantage follows.
- **CampbellColoring — Campbell, Khurana, Montanaro (2019), “Applying quantum
  algorithms to constraint satisfaction problems.”**
  [Quantum publisher record and paper](https://quantum-journal.org/papers/q-2019-07-18-167/),
  DOI `10.22331/q-2019-07-18-167`, Quantum 3, 167. Abstract identifies graph
  coloring, Grover and quantum backtracking, and fault-tolerant overhead analysis.
  We credit prior coloring cost analysis without importing its physical-resource
  model or quantum-speedup estimates.

## Valid-code preparation and concurrent work

- **MukherjeeList — Sayan Mukherjee (2022), “A Grover Search-Based Algorithm
  for the List Coloring Problem.”**
  [Author paper v2](https://arxiv.org/html/2108.09061v2), DOI
  `10.1109/TQE.2022.3151137`; arXiv `2108.09061`. Introduction explicitly
  uses modified initialization and diffusion to restrict evolution to plausible
  assignments; the empty-graph qualification distinguishes codes from solutions.
  We use this prior-work fact, not its printed complexity expressions as a
  derivation of our solution-fraction formula. List/precolor research is not
  added to the authorized experiments.
- **LevinUniform — Mark Ariel Levin (2024), “Optimized General Uniform Quantum
  State Preparation.”**
  [Publisher full text](https://www.techscience.com/jqc/v6n1/56255/html), DOI
  `10.32604/jqc.2024.047423`, Journal of Quantum Computing 6(1), 15–24.
  Introduction, Eq. (1), and coloring application discuss arbitrary-size uniform
  domains and their use in restricted coloring search. Supports preparation
  prior art, not an independently established Clifford+T cost or performance
  ranking. Matching-diffusion attribution rests explicitly on Mukherjee.
- **Shukla2024 — Alok Shukla and Prakash Vedula (2024), “An efficient quantum
  algorithm for preparation of uniform quantum superposition states.”**
  [Author preprint v2](https://arxiv.org/abs/2306.11747v2), DOI
  `10.1007/s11128-024-04258-4`, Quantum Information Processing 23, 38.
  Abstract gives consecutive-state uniform preparation, logarithmic gate/depth
  scaling, and no ancillas or multiply controlled gates in its rotation model.
  This is not a finite-precision Clifford+T resource bound. Generic maintained
  `StatePreparation` is distinguished from this specialized circuit path.
- **SenMukherjee2026 — Lord Sen and Shyamapada Mukherjee (2026), “A Quantum
  Framework for K Coloring of Graphs.”**
  [Verified arXiv record v1](https://arxiv.org/abs/2609.32348v1) and
  [full author text](https://arxiv.org/html/2609.32348v1), DOI
  `10.48550/arXiv.2609.32348`. The record gives submission 26 September 2026;
  authors are distinct from Sayan Mukherjee above. Abstract discusses binary
  encoding, constraints, Grover/QAOA/annealing. Section VI-F explicitly limits
  its empirical work to a single small simulated graph. This preprint was
  accessible, so a real citation was added. No assertion of comparative
  superiority, validation of its formulas, or reproduction of its results is
  made. The plan's more specific “hand-designed” characterization is not needed
  and is not repeated as a verified claim.

## MCX and workspace

- **Barenco1995 — Barenco et al. (1995), “Elementary gates for quantum
  computation.”** [Author paper](https://arxiv.org/abs/quant-ph/9503016),
  DOI `10.1103/PhysRevA.52.3457`. Foundational controlled-gate constructions;
  retained as a decomposition baseline. Its costs are not assigned to all MCX
  instructions without emitting and checking the selected construction.
- **Iten2016 — Iten, Colbeck, Kukuljan, Home, Christandl (2016), “Quantum
  circuits for isometries.”**
  [Author full text](https://arxiv.org/html/1501.06911v4), DOI
  `10.1103/PhysRevA.93.032318`. Appendix A, especially Lemma 8 and its proof,
  supplies controlled-X constructions using additional system wires without an
  initialization requirement. This is the borrowed-workspace lineage; a local
  adapter still must prove restoration and phase, including entangled references.
- **Maslov2016 — Dmitri Maslov (2016), “Advantages of using relative-phase
  Toffoli gates with an application to multiple control Toffoli optimization.”**
  [Author paper v2](https://arxiv.org/abs/1508.03273v2) and
  [publisher](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.93.022311),
  DOI `10.1103/PhysRevA.93.022311`. Abstract identifies smaller relative-phase
  constructions and the importance of phase-preserving compositions. No
  arbitrary replacement of exact Toffolis is inferred.
- **Vale2024 — Vale, Azevedo, Araújo, Araujo, da Silva (2024), “Circuit
  Decomposition of Multicontrolled Special Unitary Single-Qubit Gates.”**
  [Author paper](https://arxiv.org/html/2302.06377v1), journal DOI
  `10.1109/TCAD.2023.3327102`, IEEE TCAD 43(3), 802–811. The preprint title
  omits “Circuit”; journal metadata is also identified on the
  [authors' university publication page](https://portal.cin.ufpe.br/2023/12/13/).
  The paper treats SU(2) gates. A no-extra-ancilla MCX policy must preserve the
  necessary controlled phase; X itself has determinant -1. No phase-free
  substitution is claimed.
- **KhattarGidney2025 — Tanuj Khattar and Craig Gidney (2025), “Rise of
  conditionally clean ancillae for efficient quantum circuit constructions.”**
  [Quantum publisher paper](https://quantum-journal.org/papers/q-2025-05-21-1752/),
  DOI `10.22331/q-2025-05-21-1752`, Quantum 9, 1752. Abstract distinguishes
  conditional knowledge from globally clean/dirty workspace and describes
  controlled-gate constructions with limited clean space and dirty variants.
  This is included MCX decomposition work, not authorization for excluded
  automatic conditional-workspace synthesis.
- **toffoli_decomposition — Dutta, Wang, Baksi, Chattopadhyay, Maitra (2025),
  “Exact space-depth trade-offs in multicontrolled Toffoli decomposition.”**
  [Author preprint v3](https://arxiv.org/html/2502.01433v3), published DOI
  `10.1103/PhysRevA.111.052611`. Abstract and organization identify clean-space
  versus Toffoli-depth trade-offs. Figure 1 of our manuscript is separately
  described as a throwaway target-action tree, not a borrowed-dirty restoring
  construction or a universal optimal decomposition.

## Static and dynamic costs

- **Tcount — Amy, Maslov, Mosca, Roetteler (2013), “A Meet-in-the-Middle Algorithm
  for Fast Synthesis of Depth-Optimal Quantum Circuits.”**
  [Author preprint](https://arxiv.org/abs/1206.0758), DOI
  `10.1109/TCAD.2013.2244643`. The abstract identifies the three-T-layer
  Toffoli construction. Seven-T counts refer to the selected static exact
  gadget, not an optimality claim over ancillary or measurement-assisted models.
- **RossSelinger — Neil J. Ross and Peter Selinger (2016), “Optimal ancilla-free
  Clifford+T approximation of z-rotations.”**
  [Author paper v3](https://arxiv.org/abs/1403.2975v3), identifier DOI
  `10.48550/arXiv.1403.2975`; Quantum Information and Computation 16(11–12),
  901–953. Abstract concerns fixed Clifford+T approximations at requested
  precision. The classical search may be probabilistic; emitted circuits are
  static. No runtime RUS semantics follows.
- **PaetznickSvore — Adam Paetznick and Krysta M. Svore (2014), “Repeat-Until-Success:
  Non-deterministic decomposition of single-qubit unitaries.”**
  [Author paper v2](https://arxiv.org/abs/1311.1074v2), identifier DOI
  `10.48550/arXiv.1311.1074`; Quantum Information and Computation 14(15–16),
  1277–1301. Abstract explicitly uses measurement-conditioned trials. Supports
  separation of static and dynamic accounting, not direct coherent substitution.
  The repository's color-preparation extension and expected cost are local
  analytical derivations; no new dynamic execution or optimality is admitted.

## Additional retained comparison references and limitations

Saha et al., “Circuit Design for K-coloring Problem and its Implementation on
Near-term Quantum Devices,” DOI `10.1109/iSES50453.2020.00015`, is supported by
[the authors' preprint record](https://arxiv.org/abs/2009.06073). Belletti, Reale,
and Di Nitto, “Analyzing, Fixing and Optimizing a Space-Efficient Quantum Circuit
for the Graph K-Coloring Problem,” DOI `10.1109/Q-SE66736.2025.00011`, is
supported by [their university repository](https://re.public.polimi.it/handle/11311/1294152).
The latter's author abstract identifies three width/depth trade-off variants;
this revision makes only that bounded background attribution, not a technical
proof of baseline correctness. Actual baseline admission remains a code/evidence
obligation. A search/open of arXiv `2504.00898` returned an unrelated materials
paper and was not used as a citation or technical evidence.

## Local derivations, exclusions, and open admission

The complete predicate, empty conjunction convention, LSB ordering, ideal
support-invariance argument, direct construction AND bound, and right-to-left
assembly are given explicitly in the manuscript. They are not reported new
experimental findings. The first-peak formula uses actual marked fraction;
unknown solution counts stay parametric. The manuscript retains the full
comparison/scaling/noise/FT/RUS evaluation scope as pending work and removes old
percentages, hardware results, and device-fit claims from live text. Historical
outputs and image files remain unchanged. Old embedded bit labels and circuit
images are omitted from live text rather than relabeled without validation.

Reviewed static numerical rotation, analytical RUS, and bounded ideal-iteration
admissions remain separate. There is no blanket ideal-amplitude, FT, RUS,
comparison, scalability, or full-paper approval. The native value/restoration
blocker is not solved by this prose. Hardware, physical QEC, precolored research,
and conditional-workspace synthesis remain excluded. Independent claim review
must identify exact manuscript, bibliography, ledger, and map hashes and decide
only this results-independent slice.
