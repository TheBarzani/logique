# Coloring paper revamp: agreed server execution plan

Prepared on 24 October 2026 (America/Toronto). This file is the durable handoff
for the conversation `01a156b2-ea71-7222-aca2-2a6276244f86`.

## Goal and precedence

Implement the full research and manuscript revision for **From Graph k-Coloring
to Grover's Circuits via Logic Synthesis**, targeting **26 October–1 November
2026**, on the home MacBook server. Work only within the user's included ChatGPT
Plus allowance; scientific validity and the spending limit take precedence over
the completion date. Do not silently reduce the scope or claim completion when
quota or research blockers leave work unfinished.

The operating plan below incorporates the user's latest choice: run Codex CLI
directly on the server over SSH, inside `tmux`. It supersedes the earlier
five-week dates and the proposal to require a `launchd` dispatcher before starting
research. The complete user-supplied scientific specification is preserved later
in this file; its research tasks, validation requirements and exclusions remain
in scope. Numerical findings and candidate contributions in that specification
must be checked against the current code and reproduced before being cited as
new results. Old planning-only statements are historical, not a prohibition on
the implementation authorized by the server startup prompt.

The older `docs/research/roadmap.md` proposes conditional-workspace synthesis.
That is a separate direction and does not expand this task's agreed scope.

## Spending, models and execution

- Authenticate with **ChatGPT**, using the same Plus account. No API keys,
  purchased-credit continuation, automatic purchases or plan upgrades. Verify
  account credit-continuation settings before unattended work; ChatGPT login
  alone does not establish that additional credits cannot be consumed.
- Use **Standard speed**. Use the full included allowance, with no reserved 20%
  margin. All agents and machines share account limits. Do not treat an old usage
  snapshot or a guessed token budget as the current allowance.
- Default to **one active implementation agent**. Allow a second model worker
  for genuinely independent work or review; never exceed two active inference
  workers, counting the coordinator when it is actively working. Normally pair
  a Sol/Astra worker with Luna. Do not recursively spawn agents or enable Max or
  Ultra effort for this workflow.
- Keep the three specialist queues (oracles, costs, native synthesis) but run
  bounded tasks according to dependencies. Use fresh, concise task context for
  independent work and resume the recorded session ID for interrupted work.
- Builds, tests, simulations, benchmark repetitions and routine status checks
  run as ordinary local processes. Do not spend model calls on frequent polling.
- Before each model batch, inspect current applicable rate-limit windows and
  reset times. On exhaustion, checkpoint and stop new model work. If allowance
  cannot be established, pause new model jobs. Numerical jobs may continue.
- Start with an interactive coordinator in `tmux` and saved task checkpoints.
  A live terminal does not itself resume work after a model turn ends or quota
  resets. Manual resumption is acceptable. If unattended continuation is needed,
  add only a small bounded queue using `codex exec`/resume, rate-limit inspection
  and the same spending rules; do not make a monitoring platform the first task.
- Save each task's dependencies, model, effort, worktree, status, session ID,
  acceptance checks, outputs and next action in a checkpoint manifest inside a
  timestamped `dump/` run directory. Record the manifest path in this plan when
  execution starts. Never store credentials or authentication responses there.

| Work | Default model | Effort |
|---|---|---|
| Coordination, interfaces and integration | `gpt-6.1-sol` | medium |
| Task 1: notebook cleanup, reference fixes and audit formatting | `gpt-6-luna` | high |
| Task 2: configuration, metadata and baseline adapters | `gpt-6.1-sol` | medium |
| Predicate, phase, bit order and workspace correctness | `gpt-6.1-sol` | high |
| Task 3: MCX lowering, fault-tolerant costs and workspace accounting | `gpt-6.1-sol` | high |
| Task 4: comparison pipeline and statistical summaries | `gpt-6.1-sol` | medium |
| Task 5: native mappings, balancing and SAT integration | `gpt-6.1-sol` | high |
| Structure-aware oracle and parallel scheduling | `gpt-6.1-sol` | high |
| Task 6: independent fault-tolerant derivation and RUS review | `gpt-6-astra` | high |
| Tasks 7–8: simulation and scaling harnesses | `gpt-6.1-sol` | medium |
| Log triage, table formatting and references | `gpt-6-luna` | high |
| Manuscript drafting from verified evidence | `gpt-6.1-sol` | medium |
| Final independent quantum-correctness and claim review | `gpt-6-astra` | high |
| Builds, tests, simulations and repetitions | Local processes | No model |

Use Astra additionally for a focused mathematical blocker after two unsuccessful
Sol attempts. Give it the construction, derivation, counterexample and tests,
rather than the entire project history. Check model availability on the server
before dispatch; report unavailable models rather than silently choosing a more
expensive one. Routine independent reviews can use Sol; Astra reviews critical
reasoning. [Model guidance](https://learn.chatgpt.com/docs/models),
[usage guidance](https://learn.chatgpt.com/docs/pricing).

## Workspace, transfer and current state

Integration branch: **`coloring-paper-revamp-codex`**. Server integration checkout:
`~/codex-work/logique`. Preserve the laptop checkout and its existing changes.
Workers use separate worktrees and branches such as `codex/coloring-oracles`,
`codex/coloring-costs` and `codex/coloring-native`; only the coordinator integrates
reviewed changes. Worker branches must not be named underneath the integration
branch, since a Git branch and its directory prefix cannot coexist.

At handoff, the laptop is on `vcgc-paper-revision`, HEAD
`3ec511dfd98c40ccd66364b440f93a13697453ef`, seven commits ahead of its recorded
upstream. `README.md` is modified and `CLAUDE.md` is untracked. Both are existing
user work. These handoff documents are new, uncommitted documentation; the
research implementation has not been started by this handoff operation.

Recent commits already add provenance, notebook repairs, explicit MCX/Clifford+T
costs, routed FakeTorino metrics, mirrored-Toffoli costs and an MCX study. Audit
and reuse that work; the original specification's statements that a capability
is missing may now be stale. Re-read Git status and commits after transfer.

`docs/manuscript/` and `docs/research/` are ignored by the parent project and are
currently **separate nested Git repositories**, both on `main`. Copy their files
and histories during transfer. Before integrating their sources into the parent
revision branch, preserve each nested history in a Git bundle outside the source
directories, with the required timestamped dump naming. Move their Git metadata
into that preserved location rather than deleting it. Then deliberately track
their source files in the parent branch, excluding generated files. Do not stage
them accidentally as gitlinks, or let an agent change an unrelated manuscript
repository branch without noticing the boundary.

Copy the project to a fresh destination, including `.git`, submodule metadata,
uncommitted work and ignored manuscript/research sources. Exclude `.env` and
other credential files, virtual environments, build caches and `dump/`. Keep old
run artifacts on the laptop; transfer a specific old run later only if needed.
Do not re-run the initial copy over a server checkout that has begun changing.

SSH address: `mar@ssh.mergasori.com`. The earlier automated attempt failed with
`Permission denied (publickey)`; successful user SSH access is required. Port
5900 forwarding is for VNC and is not required for terminal execution. Server
RAM, CPU, repository state and authentication still need inspection. Default to
one memory-heavy numerical job until measured capacity supports more.

## First server task and seven-day schedule

1. Read `AGENTS.md`, `CLAUDE.md`, this file and the existing claim–evidence audit.
   Confirm the integration branch, transferred files and latest commit. Preserve
   existing changes; commit only deliberately selected inputs and handoff files.
2. Verify ChatGPT authentication, Standard speed, included usage and model
   availability. Inspect server RAM/CPU/disk and keep the powered Mac awake.
3. Audit the recent implementation commits and mark each research task as
   complete, partially complete or outstanding, with its validation evidence.
4. Initialize pinned submodules, set up the research environment, build the native
   bridge, and run a small smoke test. Probe SAT, balancing and rotation-tool
   build feasibility early without changing dependency pins casually.
5. Record task ownership and interfaces; begin the next unblocked correctness
   and experiment-control work. Continue through the complete specification.

| Day | Required milestone |
|---|---|
| **26 Oct** | Branch/worktrees, tmux, spending checks and checkpoints; audit existing work; freeze interfaces; native/SAT/rotation build probes. |
| **27 Oct** | Validated baseline components, R1–R3 assembly, positive witnesses, paired throwaway cleanup and pilot comparisons. |
| **28 Oct** | Integrate and validate mappings, balancing, structure-aware oracle, scheduling and explicit cost models; freeze protocol. |
| **29 Oct** | Original-benchmark comparisons, decomposition/optimization studies, iteration sweeps and scaling experiments. |
| **30 Oct** | Finish analyses; Astra reviews critical derivations and candidate claims; apply the evidence gate. |
| **31 Oct** | Complete manuscript, figures, tables and reviewer-response mapping from verified evidence. |
| **1 Nov** | Full checks, offline notebooks, historical replay, independent review and reproducibility handoff. |

All extended research remains included. Hardware executions, physical QEC
estimates, automatic conditional-workspace synthesis and precolored instances
remain excluded. Conditionally clean MCX decompositions remain included.

## Implementation cautions established during planning

- Match diffusion to the actual preparation: `A (2|0><0| - I) A†`. Normalize
  baseline vertex labels and explicitly translate MSB/LSB color bit ordering.
  Test asymmetric encodings such as k=5 as well as k=3.
- A lowered throwaway Toffoli tree is generally not self-inverse. Build the
  forward block once and invert the actual expanded block for its mirror, using
  the same held scratch qubits. Final marking and diffusion must restore scratch.
- Count peak simultaneous workspace and count explicit lowered constructions.
  Do not equate controlled-Rx(±pi) pairs with an RCCX solely from gate names;
  verify phases and exact gate conventions. Relative phases must cancel in the
  full intended composition, including entangled borrowed workspace.
- Published measurement-assisted zero-T uncomputation cannot be silently used
  in a static unitary cost model. Keep those constructions in a separate model.
- Synthesize preparation A once and use the inverse of the emitted approximation
  for A†. Account for all repeated rotations under the whole-algorithm budget.
  A probabilistic RUS preparation cannot simply be substituted for unitary A/A†.
- When M is unknown, report costs parametrically in iteration count or use a
  documented solution-count estimate; never assume one solution.
- Native mapping work requires auditing serialization of richer strategy
  actions. Existing labels that treat every non-compute step as uncompute are
  insufficient. Check bundled Caterpillar SAT support before building full ABC;
  Z3 support is a separate integration.
- The low-width structure-aware construction and parallel edge schedule have
  different scratch requirements. Report sequential and parallel trade-offs;
  do not claim fully parallel execution at the sequential width without proof.
- Use compositional proofs and verified templates when full statevectors are
  infeasible; explicitly label coverage. On a 32 GiB server, begin with at most
  24 active statevector qubits or 11 density-matrix qubits and one heavy job,
  reducing those limits if overhead requires it. Inspect actual server capacity.
  Do not simulate all idle FakeTorino wires just because routing allocated them;
  preserve layout and noise semantics when extracting the active circuit.
- Keep historical replay in an isolated environment. The historical depth
  patch changes installed Qiskit; it must not contaminate corrected experiments.
- Historical artifacts stay unchanged. New results use
  `new_run_directory()`/`new_dump_directory()` and recorded provenance.

## Acceptance and handoff

Use the validation and evidence-gate requirements in the scientific
specification below. Every reported result must identify its semantic regime,
construction, workspace policy, metric level, seeds, precision and provenance.
Report losses, unsupported cases, timeouts and infeasible cases explicitly.

Run the research environment checks from `AGENTS.md`:

```bash
git submodule update --init --recursive
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy
uv build --no-sources
```

Rebuild and check provenance of additional native tools. Run the maintained
notebooks offline into dump copies with empty source outputs. Reproduce all 135
historical metrics in isolation. Trace every manuscript number to saved circuits
and a run manifest. Preserve separate commits for correctness, build/bridge and
research-metric changes.

If an unattended queue is added, test quota exhaustion/reset, unknown quota,
interruption, duplicate launches and the concurrency limit without spending
model calls on the tests. Confirm each worker owns its own worktree. `tmux`
survives SSH disconnection, not a server reboot; checkpoints must survive both.

The final handoff lists completed tasks, checks, run directories, claim–evidence
links and unfinished work. Evidence determines whether the manuscript claims
specific improvements, presents a comparative trade-off study, or advises
reconsidering resubmission.

---

## Original full scientific specification

The following is preserved verbatim from the user's replacement research plan.
Its five-week calendar and 15 November evidence-gate date are superseded by the
seven-day calendar above (protocol freeze 28 October; evidence gate 30 October).
Everything else is the requested scientific scope, subject to the explicit
correctness cautions and current-state audit above.

# Plan for Refining the Research and Manuscript of "From Graph k-Coloring to Grover's Circuits via Logic Synthesis"

## Context

The manuscript was rejected at DATE 2026 and DAC 2026. The DAC reviewers found the paper clear (clarity scores of 4, 4, 4
and 3) but questioned its originality (2, 3, 2 and 4) and impact (2, 3, 2 and 3). They asked for a clearer statement of
novelty beyond the combination of existing techniques, an explanation of the reported width reductions, fault-tolerant
metrics (T-count and T-depth), mapped two-qubit gate counts for NISQ devices, an analysis of the rotation cost of
uniform quantum superposition (UQS) preparation, comparisons with other logic representations, mapping strategies and
multi-controlled Toffoli (MCT) decompositions, and an assessment of synthesis runtime and accuracy as instances grow.

The paper needs a methodological revision before a prose revision, because the investigation found correctness and
experimental-control issues that could change the headline results. The revision targets a complete draft before
December 2026, which leaves five weeks (26 October to 29 November). The venue remains open, and the full (extended)
scope is pursued. The scope includes conditionally clean ancilla decompositions of MCX gates; it excludes
conditional-workspace synthesis, hardware executions and physical quantum-error-correction estimates, and precolored
instances are deferred. This version integrates a second, independent investigation (Appendix A).

## 1. Findings of the Investigation

### 1.1 Issues in the Current Methodology

1. **Diffusion operator.** The manuscript defines the diffusion operator from the UQS preparation, whereas the historical
   benchmark generator reflects about the Hadamard state (`tools/generate_paper_benchmarks.py:121-136`). On the
   unprecolored K₃ graph, one iteration with the Hadamard reflection yields a success probability of 47.9% and leaks
   30.1% of the probability into unused color codes; reflecting about the actual preparation yields 99.0% with no leakage
   (recomputed during this investigation). The illustrative example (`experiments/tutorials/illustrative_example_v2.ipynb`,
   cell 39) already uses the matching reflection, but its explanatory text (cells 0, 34, 36, 40 and 43) still describes
   the Hadamard reflection, and the assertion in cell 41 expects leakage that the corrected circuit does not produce.
2. **Vertex labels in the baselines.** The baselines are produced by the `saha_belletti` package, which maps a vertex
   label i directly to the qubits qn·i to qn·(i + 1) − 1 (`node_qubits` in `external/saha-belletti/saha_belletti/problem.py:92-100`)
   and checks invalid colors over the indices 0 to n − 1. The historical replay passes one-based labels
   (`preserve_labels=True`), so the register of the last vertex falls into the ancilla region for every variant, and the
   `original` variant additionally skips the edges incident to the last vertex (`saha_belletti/original.py:108-114`). On a
   three-vertex path, the ideal success probability of the Saha et al. circuit is 25% with the historical labels and
   100% with normalized labels. Every variant must therefore be revalidated with normalized labels.
3. **Resource accounting.** The reported baseline width adds n − 2 ancillas for every n-control gate except the last,
   summed over all gates, while the proposed circuits are counted by their allocated qubits
   (`tools/generate_paper_benchmarks.py:39-52`). This allowance corresponds to the throwaway-ancilla decomposition of
   Figure 1 (item 4). In the baselines, the oracle is computed, applied to the kick-back qubit and uncomputed in reverse
   order, so each gate of the compute phase is mirrored in the uncompute phase, which returns its ancillas to the clean
   state; the ancillas are held between a gate and its mirror and are free afterwards. Summing over all gates therefore
   counts each held ancilla twice, and the correct quantity is the peak number of simultaneously held ancillas. Two gates
   have no mirror, namely the gate acting on the kick-back qubit and the diffusion gate; their garbage would remain
   entangled with the data and destroy the interference of Grover's algorithm, so they require a decomposition that
   restores its ancillas. Depth assigned ⌈log₂ n⌉ to each n-control gate and one unit to every other gate
   (`tools/patch_qiskit_depth.py`), which matches the throwaway tree but omits this restoration. Gate counts used
   `len(circuit)`, which includes barriers, measurements and undecomposed operations, with measurements counted for the
   baselines only.
4. **Illustrated MCT decomposition.** Figure 1 illustrates a throwaway-ancilla decomposition: the ancillas are clean
   before the gate and left in a garbage state afterwards, which avoids uncomputation and keeps the depth of the
   baselines low. The caption describes them as dirty ancillas, which denotes a different construction (borrowed qubits
   in an unknown state that must be restored, as distinguished by Dutta et al.). The caption must be corrected, the
   validity condition stated (the garbage must be removed by a mirrored gate before the end of the oracle), and the
   decomposition compared with the alternatives of Task 3.
5. **Aggregation of improvements.** The headline percentages average the per-graph reductions over all four baselines,
   including Belletti-Minimal, whose inflated width and depth dominate the mean, and they were truncated rather than
   rounded (41.79, 49.46 and 60.16). Against the best baseline on each graph, the proposed flow is deeper on 6 of the 9
   graphs (mean depth change of −13.1%).
6. **Verification coverage.** The sampled checks of the larger instances contain no satisfying assignment (6 of the 9
   graphs in the archived replay, and all eight sampled graphs of the five-method study), so the marking branch of their
   oracles was never exercised, and the baseline oracles were never verified independently. The maintained correctness
   tests pass, which supports reusing the maintained implementation but does not validate the historical methodology.
7. **Statements in the manuscript.** The diffusion formula applies U_Ψ and U_Ψ† in the reverse order; the iteration
   count ⌊(π/4)√N⌋ ignores the number of solutions M and the restricted domain size N = k^|V|; the text states that the
   oracle marks invalid colorings, whereas the implementation marks valid ones; valid color encodings and proper
   colorings are not distinguished; Clifford+Toffoli is described as an extension of Clifford+T, and XAGs as canonical;
   "for the first time" is not supported; the Grover circuit is called MCT-free although its diffusion operator retains
   an (n − 1)-control gate; compatibility with IBM's Condor processor is claimed from qubit counts alone; the benchmark set
   is described as K₃ to K₂₀ although only K₃, K₅, K₁₀ and K₂₀ are evaluated; NISQ is used before it is defined; the
   notation alternates between x and v (Figure 5 and Equation 4); the caption of Figure 4 lacks parentheses; and the
   order of the graphs differs between Figures 6a and 6b.
8. **Repository maintenance.** `tests/test_notebooks.py` and `tests/test_boolean_visuals.py` refer to a deleted notebook,
   two tutorial notebooks contain saved outputs, the provenance record hard-codes the Caterpillar revision
   (`src/logique/benchmarks/provenance.py:14`), and `docs/manuscript/` and `docs/research/` are excluded from version
   control.

### 1.2 Reviewer Concerns and Planned Responses

| Concern | Cause identified | Planned response |
|---|---|---|
| Novelty beyond a combination of known techniques (Reviewers 1, 2 and 3) | Automated Boolean compilation, XAG oracle synthesis and coloring applications already exist; an equality comparator built from logical-AND gates needs the same c − 1 AND gates per edge as the XAG encoding | Explanatory research question (Section 2); ablation across three controlled regimes (Task 4); structure-aware oracle and design space (Task 5) |
| Lower width despite ancillas (Reviewer 1) | Accounting described in Section 1.1, item 3 | Peak-workspace accounting for every decomposition (Task 3); width breakdown by qubit role (Task 4) |
| T-count, T-depth and mapped two-qubit counts (Reviewers 2 and 4) | Not computed anywhere in the library | Clifford+T lowering and routed metrics (Task 3) |
| Rotation cost of UQS in fault-tolerant settings (Reviewer 4) | Never analyzed; a uniform superposition over k states cannot be prepared exactly with Clifford+T gates when k is not a power of two | Whole-algorithm error budget and rotation synthesis (Tasks 3 and 6) |
| Multi-controlled gate in the diffusion operator (Reviewer 4) | Scope of the MCT-free claim | Same explicit MCX decomposition for every flow (Task 3); claim restricted to the oracle |
| Belletti-Simple achieves lower depth on some graphs (Reviewer 4) | No depth-oriented optimization in the flow | Balancing, depth-oriented mapping and parallel clause scheduling (Task 5) |
| Runtime and XAG size as graphs grow (Reviewer 2) | Not measured; nine small graphs only | Controlled scaling families (Task 8) |
| Accuracy for larger graphs and more iterations; MCT width overhead (Reviewer 1) | One iteration, k = 2 only, no ideal reference | Iteration sweeps with ideal, noisy and random-sampling success (Task 7); width breakdown (Task 4) |
| AIG, k-LUT and LHRS mappings, Bennett and best-fit strategies, XAG balancing, conditionally clean ancillae (Reviewer 3) | One mapping in the paper, although the library provides five methods | Design space with balancing and additional strategies (Task 5); MCX decompositions including conditionally clean ancillae (Task 3) |
| NISQ acronym and x/v notation (Reviewer 1) | Editing | Manuscript revision (Section 6) |

### 1.3 Positioning with Respect to Prior Work

The contribution statement must survive comparison with the following works. Schmitt et al. (DATE 2021), already cited,
compile Boolean functions to quantum circuits through XAGs and demonstrate a coloring oracle. Yu, Tempia Calvino, Soeken
and De Micheli ("Back-end-aware Fault-tolerant Quantum Oracle Synthesis", ASP-DAC 2025) relate XAG properties to the T
count, logical time steps and helper qubits of back-end-compiled oracles. Häner and Soeken (arXiv:2006.03845) reduce
T-depth by reducing multiplicative depth with cut enumeration, tree balancing and ESOP representations; balancing must be
credited to this line of work. Mukherjee (arXiv:2108.09061) and Levin (2024) prepare uniform states over each vertex's
allowed colors with a matching diffusion operator, so integrating UQS preparation is not a contribution by itself.
Campbell, Khurana and Montanaro (Quantum 3:167, 2019) estimate fault-tolerant costs of Grover and backtracking circuits
for coloring. The MCX decompositions of Barenco et al. (1995), Iten et al. (2016), Maslov (2016), Vale et al. (2024),
Khattar and Gidney (2025) and Dutta et al. (2025) define the decomposition baselines. Pebbling and best-fit mapping
(Meuli et al.), LUT-based hierarchical reversible synthesis (Soeken et al.), rotation synthesis (Ross and Selinger) and
exact synthesis (Giles and Selinger) complete the background. Sen and Mukherjee (arXiv:2609.32348, September 2026) is
concurrent work with a hand-designed oracle evaluated on one four-vertex graph.

### 1.4 Capabilities Available in the Repository

The library provides the five synthesis methods `xag`, `aig_bennett`, `xag_bennett`, `klut_bennett` and `best_fit`
(`src/logique/synthesis/native.py`), the complete coloring predicate (`src/logique/coloring/encoding.py`), phase oracles
with workspace restoration (`SynthesisResult.phase_oracle()`), a reflection about an arbitrary preparation
(`src/logique/circuits/grover.py`), phase, restoration and kick-back verification (`src/logique/verification/`), basis
lowering (`lower_circuit()` in `src/logique/benchmarks/metrics.py`), the benchmark runners (`src/logique/benchmarks/runner.py`
and `phase.py`) and the adapter to the `saha_belletti` package (`src/logique/synthesis/saha_belletti.py`). The installed
Qiskit 2.1.1 includes the MCX decompositions of Task 3 and `UniformSuperpositionGate`, and qiskit-ibm-runtime 0.41.1
includes the `FakeTorino` device model. Multiplicative-complexity optimization in tweedledum (`classical.optimize`) and
Caterpillar's low-T and low-T-depth XAG strategies exist but are not connected. Balancing exists only in the standalone
mockturtle submodule, which the native bridge does not compile against, and SAT-based pebbling requires building ABC's
SAT solver. The library computes no T-count, T-depth, rotation cost or routed metric, and the encoder builds left-deep
AND and OR chains (`src/logique/coloring/encoding.py:49-55`).

## 2. Research Question and Candidate Contributions

The revised paper addresses the following question: under matched correctness requirements, preparation, workspace and
compilation settings, when does logic-synthesis-based construction of graph-coloring oracles improve quantum resource
costs, and what explains those improvements?

The following contributions are candidates, to be retained only if the corrected results support them (c = ⌈log₂ k⌉).

1. **An analytical resource model**, validated against synthesized circuits. The edge-only predicate needs at most
   |E|·c − 1 AND gates, exactly c − 1 per edge. The current XAG construction allocates (|V| + |E|)·c − 1 qubits, which
   matches all nine archived widths. Restricting each vertex to k valid codes reduces the search space by (2^c/k)^|V|,
   that is, the number of iterations by a factor of 10.5 for K₁₀, 223 for myciel4, 863 for myciel5 and 110 for K₂₀, and
   by no factor when k is a power of two.
2. **A structure-aware oracle** that computes each edge constraint into one qubit, uncomputes its intermediate AND gates,
   schedules constraints on disjoint edges in parallel, and combines all constraints with a single multi-controlled gate
   decomposed with conditionally clean ancillae. Its width is approximately |V|·c + |E| + c, which reduces K₂₀ from 1,049
   to about 295 qubits and myciel5 from 848 to about 380 qubits, at the cost of additional Toffoli gates.
3. **A controlled comparison** of representations, optimizations, mapping strategies, preparations and MCX
   decompositions that identifies which mechanism produces each saving and where each method loses.

## 3. Experimental Protocol

The protocol is piloted on K₃, K₅ and myciel3, then frozen on 8 November in `docs/research/experimental_protocol.md`,
which documents every departure from the historical accounting. Parameters, resource limits and seeds are fixed before
the final evaluation, and timeouts and infeasible cases are recorded explicitly.

**Semantic contract.** Every method implements the same independently evaluated coloring predicate, with explicit input
ordering and restored workspace. The diffusion operator is A(2|0⟩⟨0| − I)A†, where A is the actual preparation. Direct
phase kick-back is used when the arbitrary-target XOR action and the cleanup of the oracle are verified
(`verify_kickback_oracle()`); otherwise the oracle is compute–phase–uncompute (`phase_oracle()`). The construction used is
recorded. A baseline that fails validation is corrected in the maintained adapter or excluded from performance
conclusions; historical code and results remain unchanged.

**Controlled regimes.** Each supported method is evaluated under three regimes: (R1) Hadamard preparation with the
complete predicate, which rejects unused color codes; (R2) valid-color preparation with the complete predicate; and (R3)
valid-color preparation with the redundant domain checks removed. Comparing R1 with R2 isolates the preparation, and
comparing R2 with R3 isolates the removal of redundant checks. For the baselines, R3 is obtained without modifying the
package: the number of invalid-color checks is 2^c − k (`saha_belletti/problem.py:112-120`), so building the baseline
with 2^c colors removes them while keeping the edge comparators. The nine graphs are used without precolors, and this
transformation is documented.

**Optimization profiles.** Five profiles are compared, with the same preprocessing for every representation: no
optimization; the current refactoring; a balanced conjunction construction in the encoder; multiplicative-complexity
reduction; and cut- or ESOP-based balancing (Task 5).

**Decomposition and workspace policies.** MCX gates are decomposed with the policies of Task 3. Peak simultaneous
workspace is reported instead of a sum of per-gate requirements. Garbage left by a throwaway-ancilla decomposition is
permitted only when a mirrored gate removes it before the end of the oracle; gates without a mirror use a decomposition
that restores its ancillas.

**Benchmarks.** The nine graphs of the manuscript ensure continuity. Controlled scaling families vary the vertex count,
the edge density and the number of colors, including powers of two and other values. Small graphs (K₄, C₅, P₄ and the
Petersen graph) and non-power-of-two examples support the success-probability study.

**Metrics.**

| Layer | Required evidence |
|---|---|
| Compiler | Encoding, optimization, mapping and lowering times; peak memory; AND, XOR and LUT counts; multiplicative depth; peak workspace |
| Logical circuits | Separate costs for the oracle, preparation, diffusion operator and complete algorithm |
| NISQ | Common-basis counts; routed native two-qubit count and depth, active physical qubits and scheduled duration on `FakeTorino` |
| Logical fault tolerance | Clifford+T counts, T-depth computed on the circuit dependency graph, logical qubits and rotation-synthesis cost at a stated precision |
| Algorithm | Ideal and noisy success probability versus iteration count, invalid-code leakage, random-sampling success and cost per successful solution |

**Targets and precision.** Mapped experiments use the installed `FakeTorino` snapshot, whose calibration data and version
are recorded, with the same optimization settings and five fixed transpiler seeds for every method. Circuits that do not
fit receive logical and common-basis results with an explicit infeasibility label. The fault-tolerant analysis uses a
static unitary model: arbitrary rotations are synthesized with a documented method under a whole-algorithm error budget
that includes every repeated preparation and inverse preparation, with 10⁻³ as the primary budget and 10⁻² and 10⁻⁴ as
sensitivity checks. Measurement-assisted constructions, such as repeat-until-success rotations, are reported separately.

**Validation requirements.**
- Exhaustive predicate checks and coherent phase and restoration checks on small cases, including noncontiguous labels,
  isolated vertices, empty constraint sets and unsatisfiable instances.
- Explicit verification assignments for larger cases: known solutions as positive witnesses, together with invalid
  colors, edge violations and boundary cases; sampled checks are labelled as such.
- Boolean equivalence checks after every optimization pass.
- Superposition checks for relative-phase substitutions, entangled-reference checks for borrowed dirty and conditionally
  clean workspace, and checks that throwaway garbage is removed by the end of each oracle.
- Operator equivalence after lowering for small cases, and numerical error checks for approximate rotations.
- Agreement of multi-iteration simulations with independent amplitude-amplification calculations.
- Reproduction of every table from saved circuits, with consistent measurement accounting and deterministic seeds.

## 4. Work Plan (26 October to 29 November 2026)

| Week | Dates | Research | Writing |
|---|---|---|---|
| 1 | 26 Oct – 1 Nov | Tasks 1 and 2; Task 3 starts; pilot on K₃, K₅ and myciel3 | — |
| 2 | 2 – 8 Nov | Task 3 ends; Task 4 (Milestone 1); Task 5: encoder balancing, multiplicative-complexity reduction, Caterpillar strategies; Task 8 starts; protocol frozen on 8 Nov | Background, related work, notation |
| 3 | 9 – 15 Nov | Task 5: structure-aware oracle, balancing tool, SAT-based pebbling; Tasks 6 and 7; evidence gate on 15 Nov | Method section |
| 4 | 16 – 22 Nov | Task 5: edge-coloring schedule; Task 8 ends; remaining runs, figures and tables | Evaluation section |
| 5 | 23 – 29 Nov | Tracing every reported number to a saved run | Abstract, introduction, conclusion, proofreading; complete draft by 27 Nov |

All tasks extend the maintained toolkit rather than creating another manuscript-specific implementation. Results are
written to new `dump/MMDDHHMMSS-description` folders created with `new_run_directory()`; dependency revisions stay fixed;
bridge and build changes, correctness fixes and metric changes are committed separately; and the historical artifacts in
`experiments/manuscript/` are retained unchanged. Results from Task 5 items completed after the evidence gate enter the
evaluation section; they change the framing only if they reverse a conclusion.

### Milestone 1: a valid comparison (Weeks 1–2)

**Task 1. Claim–evidence audit and repository preparation.**
- Write `docs/research/claim_evidence_audit.md`, mapping each reviewer concern and manuscript claim (percentage savings,
  scalability, noise resilience, whole-circuit MCT-free, device compatibility) to its implementation, experiment and
  assumptions, its status, and the evidence required to replace it.
- Fix the tests that refer to the deleted notebook, remove saved notebook outputs, update the narrative and the cell-41
  assertion of the illustrative example, read the Caterpillar revision from `build_provenance.json`, and place
  `docs/manuscript/` and `docs/research/` under version control.

**Task 2. Experiment controls in the toolkit.**
- Add configuration keys to the runner for the preparation and domain policy, optimization profile, decomposition and
  workspace policy, target, precision, iteration sweep, seeds and execution limits.
- Expose the baseline oracle components independently of their preparation and diffusion, through `make_problem`,
  `compose` and `decompose` (`external/saha-belletti/saha_belletti/core.py:255-293`), with normalized labels and explicit
  handling of the package's most-significant-bit-first color encoding.
- Extend the result metadata with stage timings, structural statistics, workspace roles, validation coverage and the
  metric level (logical, common-basis, decomposed, routed or fault-tolerant).
- Allow explicit verification assignments, as required in Section 3.

**Task 3. Explicit cost model and MCX decompositions.**
- Implement a cost module (`src/logique/benchmarks/costs.py`). Gate counts exclude barriers and measurements. In the
  Clifford+T lowering, a Toffoli gate costs 7 T gates and a T-depth of 3; the controlled Rx(±π) pairs produced by
  `xag_synth` are relative-phase Toffoli gates costing 4 T gates each; a controlled Hadamard costs 2 T gates; arbitrary
  rotations are synthesized under the error budget of Section 3.
- Compare the following MCX decompositions, each recorded for every circuit:
  - the throwaway-ancilla tree of the manuscript (Figure 1), with clean ancillas left in a garbage state, valid only for
    mirrored gates, and accounted by the peak number of held ancillas;
  - clean ancillas with uncomputation;
  - Barenco et al. (one clean ancilla), Iten et al. (n − 2 dirty ancillas), Maslov (n − 2 clean ancillas with
    relative-phase Toffoli gates), Vale et al. (no ancilla) and the Gray-code construction, available in Qiskit 2.1.1
    through `HLSConfig`;
  - Khattar and Gidney (one or two clean or dirty ancillas), which exploit conditionally clean ancillae;
  - the space–depth trade-offs of Dutta et al., implemented or evaluated analytically.
- Apply the same policy to the comparators, invalid-color checks and final conjunction of the baselines, to the
  multi-controlled Z gate of every diffusion operator, and to the multi-controlled gates of the k-LUT and best-fit methods.
  Report each decomposition for isolated gates (3 to 20 controls) and within complete circuits.
- Add routed metrics on `FakeTorino` and helper functions for the ideal success probability and optimal iteration count.

**Task 4. Corrected comparison under the three regimes (end of Milestone 1).**
- Evaluate the five synthesis methods and the four baselines on the nine graphs under regimes R1, R2 and R3.
- Break down the width of each circuit into data qubits, AND workspace, constraint qubits, MCX ancillas and the phase
  kick-back qubit, which answers Reviewer 1's question on width.
- Report results per graph against the strongest baseline, with geometric means and win, tie and loss counts.
- Deliverables: the corrected small-instance comparison, regression tests and the frozen experimental protocol.

### Milestone 2: explaining the resource trade-offs (Weeks 2–4)

**Task 5. Mechanisms behind the savings.**
- Describe each method by its actual configuration (for example, `aig_bennett` is Caterpillar's LHRS with the Bennett
  strategy on an unrefactored AIG), not as a representative of its whole algorithm family, and apply the same
  preprocessing to every representation.
- Optimization profiles: balanced AND and OR trees in the encoder; multiplicative-complexity reduction through
  tweedledum's `classical.optimize` (refactoring followed by cut rewriting with the `xag_minmc` database); and cut- or
  ESOP-based balancing (`balancing`, `xag_balance` and `xag_algebraic_depth_rewriting`) in a separate tool built on the
  standalone mockturtle, using `external/mockturtle/experiments/balancing.cpp` as a template, with Verilog exchanged
  with the native bridge.
- Mapping strategies: expose Caterpillar's `xag_mapping_strategy` (low T-count), `xag_fast_lowt_mapping_strategy`,
  `xag_low_depth_mapping_strategy` (low T-depth), in-place Bennett and eager strategies in the native bridge
  (`external/native/boolean_synthesis/include/mapping.hpp`, correcting its step labels), and add SAT-based pebbling under a
  qubit budget, which requires building ABC's SAT solver from `external/abc`.
- Implement the structure-aware oracle of Section 2, including the schedule of edge constraints derived from an edge
  coloring of the graph, so that constraints on disjoint edges are computed in parallel.
- Plot qubits against T-count and T-depth for all strategies, report the achievable trade-offs under common total-qubit
  limits, include the graphs on which Belletti-Simple wins, and explain the savings through network size,
  multiplicative depth, cleanup and workspace reuse.

**Task 6. Fault-tolerant cost of the complete search.**
- Report separately the costs of the preparation, oracle and diffusion operator, and the cost of the complete search,
  T_A + j·(2T_A + T_S0 + T_O), with j chosen from the solution fraction when it is known.
- Determine when valid-color preparation, with its rotation cost, is cheaper than Hadamard preparation with the complete
  predicate. Report the exact repeat-until-success preparation for k = 3 (Paetznick and Svore; 14/3 expected T gates per
  vertex) separately, as a measurement-assisted construction.

**Task 7. Success probability versus iteration count.**
- Sweep the number of iterations up to the first ideal maximum and one iteration beyond. More iterations are not
  automatically better: an eight-vertex two-color path reaches only 6.89% ideal success after one iteration.
- Include the path graphs with 3 to 8 vertices and non-power-of-two examples (K₃, C₅ and P₄ with three colors) that
  exercise the valid-color preparation. Report ideal, `FakeTorino`-noise and random-sampling success, invalid-code
  leakage and confidence intervals, distinguishing analytical predictions from simulated results.

**Task 8. Scalability of the synthesis flow.**
- Run the controlled scaling families and selected DIMACS instances (queen, myciel6 and myciel7, DSJC125.1, le450_5a and
  `queen8_8`, `5-FullIns_3` and `4-Insertions_3` restored from legacy commit `95f6167`), recording stage times over at least
  five repetitions, peak memory, network statistics and timeouts. The 180-second bridge timeout
  (`src/logique/synthesis/native.py:36`) is raised for this study.

## 5. Evidence Gate (15 November)

Result-dependent sections of the manuscript are written only after the following conditions hold:

1. Every headline comparison satisfies the same semantic contract.
2. Resource estimates come from explicit and reproducible constructions.
3. Ablations identify which mechanisms produce the improvements and where they lose.
4. The verification of larger instances exercises satisfying assignments.
5. The scalability and iteration studies support precisely bounded claims.
6. The contribution statement survives comparison with Schmitt et al. (DATE 2021), established XAG methods and Yu et al.
   (ASP-DAC 2025).

If the corrected results retain a meaningful advantage, the paper is framed around the demonstrated improvements in
graph-coloring compilation and their operating conditions. If they establish useful trade-offs without general
superiority, it is framed as a comparative synthesis study. If neither yields a defensible contribution, the
resubmission should be reconsidered rather than preserving unsupported claims. Results-independent sections
(background, related work, notation and the cost-model description) are drafted before the gate.

## 6. Manuscript Revision Plan

- **Title and abstract.** Replace the headline percentages with results against the strongest baseline under the
  explicit cost model, and scope "MCT-free" to the oracle.
- **Introduction.** Restate the research question and the contributions that pass the evidence gate.
- **Background.** Define the cost models (Clifford+T, relative-phase and logical-AND constructions, MCX decompositions
  with clean, dirty, throwaway and conditionally clean ancillae, rotation synthesis); relabel Figure 1 as a
  throwaway-ancilla decomposition and state its validity condition; state the iteration count with M and N = k^|V|;
  write the diffusion operator as A(2|0⟩⟨0| − I)A†; define NISQ at first use.
- **Related work.** Add the works of Section 1.3 and position the paper against them.
- **Method.** Present the encoding, distinguishing valid color encodings from proper colorings, a short argument that the
  restricted search space makes unused-code checks unnecessary, the synthesis strategies and the analytical cost table.
  Use the notation x_{v,i} throughout and state that the oracle marks valid colorings.
- **Evaluation.** Describe the protocol, then the regimes and ablations, the MCX decompositions, the optimization
  profiles and trade-offs, the fault-tolerant cost of the complete search, the routed NISQ metrics, the success
  probability versus iteration count and the scalability study. Discuss the cases where the proposed flow loses.
- **Removals.** Remove the hardware experiments and the device-compatibility claims based on qubit counts alone.
- **Length.** The full scope suits a journal paper of 10 pages or more; a conference version would select the regimes,
  the MCX study, the main trade-offs and the fault-tolerant analysis.
- **Reviewer responses.** Keep a table mapping each reviewer comment to the revised text in `docs/research/`.

## 7. Verification of the Implementation

- Run `uv run --no-sync pytest`, `black --check`, `ruff check` and `mypy` as described in CLAUDE.md, in the research
  environment created by `python3 tools/sync.py --all-extras`; rebuild the native bridge and the new balancing tool and
  check their provenance records.
- Apply the validation requirements of Section 3 to every new method, decomposition and optimization profile.
- Confirm that the corrected Grover iteration reproduces the analytical values on small graphs (99.0% for K₃ after one
  iteration, with no leakage), and that the historical replay still reproduces the 135 archived values.
- Execute notebooks with `logique notebook run ... --offline`, and trace every number in the paper to a `dump/` run with
  its provenance record.

## Appendix A. Elements Integrated from the Second Investigation

Adopted: the explanatory research question; the K₃ leakage figure (30.1%, recomputed) and the three-vertex-path result
for the Saha et al. baseline (25% versus 100%); the claim–evidence audit; the semantic contract, including the choice
between direct kick-back and compute–phase–uncompute; the rule that failing baselines are corrected or excluded; the
three controlled regimes; the optimization profiles and the credit to Häner and Soeken; the description of methods by
their actual configurations; the five-layer metric table, including active physical qubits, scheduled duration,
invalid-code leakage, random-sampling success and cost per successful solution; controlled scaling families with a pilot
and a frozen protocol; five fixed transpiler seeds; the whole-algorithm error budget of 10⁻³ with sensitivity checks;
iteration sweeps up to the first maximum and one beyond; extension of the maintained toolkit instead of a
manuscript-specific generator; the validation requirements; the evidence gate and its three outcomes; and the removal of
device-compatibility claims based on qubit counts.

Adapted: the evidence gate is dated 15 November, and results-independent sections are drafted before it, to meet the
December deadline. The second plan described the Figure 1 construction as failing to restore its ancillas; it is
instead treated as a throwaway-ancilla decomposition whose garbage must be removed by mirrored gates, and it is
compared with the other decompositions. Precolored instances, which the second plan evaluates separately, remain deferred.

Retained from this plan and absent from the second: the schedule, the analytical resource model, the structure-aware
oracle with parallel clause scheduling, the explicit list of MCX decompositions including the throwaway tree and Dutta
et al., the construction of baselines without domain checks through 2^c colors, the exact repeat-until-success
preparation for k = 3, and the code locations.

## Server execution checkpoint

Started 2026-10-24T23:58:24.867768-04:00. Checkpoint: `dump/1024235721-coloring-paper-server-checkpoint/manifest.json`.
Model dispatch paused: live five-hour allowance exhausted; credit continuation and automatic-purchase settings unresolved.
Numerical setup status is recorded in `setup-state.json` and `setup.log` beside the manifest.

## Automatic dispatch enabled by user request

On 25 October the user requested implementation and activation of an automatic
dispatcher and attributed observed credit decreases to another session. The
confirmed disabled credit-continuation/automatic-purchase settings remain in
force. The bounded queue is `dump/1025021922-coloring-auto-dispatch/queue.json`.
See [dispatcher operations](coloring-dispatcher.md). The process checks live
included usage, uses the model table above at Standard speed, resumes recorded
sessions, and redeems free resets only after weekly exhaustion. Queue/task
completion is never evidence-gate or manuscript approval.

On 25 October the user additionally authorized automatic commits and pushes.
This supersedes earlier no-push instructions for this workflow: workers commit
validated task-owned changes, the coordinator integrates on
`coloring-paper-revamp-codex`, and the dispatcher pushes only that branch to
`origin`. Preserve unrelated user edits, dependency pins and historical results;
never force push or publish worker branches. See dispatcher operations for the
explicit publication policy and failure checkpoints.

## Full-scope continuation renewed 28 October

The user explicitly requested continuation of the full revision after the first
57 bounded queue jobs reached 55 complete/two blocked. This renews authority to
implement the remaining plan and append unblocked implementation/review jobs;
older narrow task handoffs do not prohibit work newly assigned under this
request. See [the resumption audit](research/full_scope_resumption_20261028.md).
Checkpoint: `dump/1028004102-coloring-full-scope-resumption/`.
Seven new jobs cover executed ideal iterations, a five-repeat scaling pilot,
independent reviews/integration, and fresh full-scope coordination. Completed
tasks are not redispatched. Correctness admissions remain limited to their
reviewed evidence, and full research/manuscript completion remains open.


## Full research implementation successor batch — 28 October

Checkpoint: `dump/1028023823-full-revision-implementation-coordinator/batch.json`.
[Updated tasks1–8 matrix](research/full_revision_batch_20261028.md) records an
implemented/tested scaling timeout/RSS correction awaiting independent review,
twelve atomic successor jobs for selected scaling/noisy iterations/comparisons/
protocol/manuscript/native-value review and a new integration coordinator.
104/128 batches used at append, 76 immutable-preserving task definitions; hard
bounds and included-usage gates unchanged. Full research and manuscript remain
open; no new scientific admission follows from this handoff.


## Bounded full research integration — 28 October

Checkpoint: `dump/1028174846-full-research-integration/batch.json`.
[Current full tasks1–8 matrix](research/full_research_integration_20261028.md)
records exact admitted preparation/comparison/background integration, withheld
scaling/noisy source, native transition-proof scope, private tested comparison
correction pending independent review, and complete-predicate C5 allocation audit.
Eight successors appended atomically at120/128 batches,84 definitions total;
header/prior definitions/prompts and hard deadline/usage gates preserved.
Full revision remains open. Final successor owns exact admissions/integration
and hard-bound actionable resume covering all remaining scope. No scientific
admission follows from job completion; dispatcher alone publishes HEAD.

## Hard-bound final integration and resume — 29 October

Checkpoint: `dump/1029034135-full-research-bound-handoff/batch.json`.
[Authoritative remaining tasks1–8 matrix](research/full_research_bound_handoff_20261029.md)
records exact service/context admission5c0b872 → integration4c5f3e4,
candidate319/integrated356 tests, withheld scaling/noisy source and interrupted
independent reviews,220 unexecuted scaling rows, actual partial-noise failures,
and all remaining scientific/manuscript/final-validation work. Hard128/128
reached; no extra queue/model launches or gate changes. This bounded integration
and actionable handoff completes; the full revision remains OPEN. Dispatcher
alone publishes integration HEAD. Earlier snapshots and failures are historical
and preserved; no full-paper or blanket FT/RUS/ideal-amplitude admission follows.

## 29 October included-usage resumption

After the original dispatcher stopped at128 total batches, the user explicitly
authorized resuming with remaining included usage. New bounded continuation:
`dump/1029204240-coloring-dispatch-continuation/queue.json`, up to128 additional batches,
same deadline and spending/model/review rules. Old state, completed jobs and
scientific exclusions remain intact. Saved interrupted review session resumes;
new tasks allow multiple bounded attempts and explicit transient model-capacity
errors retry without changing models. See dispatcher operations and the new
run's continuation/activation receipts. Full revision remains unfinished.
