# Independent reusable-component lowering review

Task `component-lowering-review-1101052342`, 3 November 2026. Assigned base
`de230cce74089344343fcdf1c12d553cc4cf8607`; candidate correctness
`8d1909189b775e8629f76b56dd653065d0b9913b`, final candidate
`fe85746e9dd5abebf045ea5b50fc7ff02621ecbe`.

**ADMIT the exact six-path source correction below within its stated domain.
This bounded independent review is complete. No new scientific study, build,
cost comparison, noisy observation, or 22-wire result is admitted.**

Fresh checkpoint: `dump/1103161917-component-lowering-independent-review/` in
this review worktree. Independent probe:
`tools/probe_component_lowering_review_1101052342.py`.

## Exact source decision and domain

The reviewed chain consists of the correctness commit and its separate factual
handoff `docs/research/component_lowering_fix_20261103.md` at `fe85746` (SHA256
`54d826728f6c1973a23d45c71eadd4ed65ed6b1317ebf899baafd21dcf013e8c`).
The documentation is an implementation report, not an independent admission.
All six working-file hashes match their committed blobs. All 30 entries in the
worker checkpoint's evidence inventory were independently rehashed, including
its initial failed fixture and partial measurement receipts.

| Admitted correctness path at 8d19091 | SHA256 |
| --- | --- |
| `src/logique/benchmarks/metrics.py` | `6ff3ef194a8cb3fec5e3adb2869daa939687d2c351780c14725fde5c029e84b9` |
| `src/logique/benchmarks/costs.py` | `8529ad29d6457ed784c700ae26a7579b72bc0221857eb575a884ee4dc6c7a7b0` |
| `src/logique/benchmarks/routing.py` | `b35f6eaaeba466f3393f0a42c39f15c74f26fb2539056eec68ea9add6730db8d` |
| `src/logique/benchmarks/iteration_study.py` | `c941aef068bb848174652644530d9f3fafc8e4e55c872f34b619753f76bd22c5` |
| `src/logique/benchmarks/noisy_iterations.py` | `0630dc70ecd0a8490acdff8dd661c2e939644be18bd500dd8be91dbae5e22385` |
| `tests/test_component_lowering.py` | `9a37625010cb4c4df6d1cfb40efc0b54d728d34fa6826f135a292742843a898a` |

Admission covers removing the false program-entry zero assumption from the six
transpilation calls in these five modules, and explicitly serial execution.
It concerns bound static components handled by the installed Qiskit 2.1.1
translation/synthesis path, preserving arbitrary data, target and spectator
inputs. It does **not** remove any explicit clean-workspace precondition of
the source circuit or MCX construction. A throwaway block still requires held
initially zero scratch and its actual inverse; it is not a restoring standalone
MCX. Structure phase oracles still require clean flags, scratch and output.
Clifford+T arbitrary rotations remain unpriced unless separately synthesized;
positive snapping tolerance remains approximation, not exactness.

This decision does not certify every Qiskit plugin, opaque/dynamic operation,
arbitrary rotation convention, native synthesis result, wider resource policy,
or historical lowered artifact. The inherited controlled-Rx routing gadget is
assessed for its intended exact +/-pi angles, not arbitrary near-pi inputs.
Installed `HighLevelSynthesis` source explicitly explains that the default
assumes zero inputs and supplies clean ancillas to synthesis. Setting the flag
false removes that unsupported assumption. The finite numerical checks below
support this source reasoning; passing tests alone is not the admission basis.

## Whole offered chain, inheritance and call sites

The complete five modules, the new tests, both offered commits, emitted inverse
assembly, relevant QPY resolver and common-comparison call sites were inspected.
Current root was `9e289cb` at audit. The parent bytes of all five changed source
paths equal current root. The branch already inherits selector integration
`7943385` and C5 integration `2fff3ea`; no missing prerequisite or stale source
substitution was found. No dependency was imported from the review base during
execution: imports were explicitly asserted into the candidate checkout.

Root's newer `coloring_study.py` differs in profile selection, metadata and
failure-payload handling. Those differences were inspected, and the five
resolver/signature/standard-gate/wide-MCX helper definitions are byte-identical
between root and candidate. Grover/structure, the standalone C5 tool, noisy
selector tool/test/config also match current root exactly. These identities
are recorded in `source-chain-audit.json`. No new profile/native behavior is
admitted by these component tests. The coordinator must retain newer root
profile changes and independently review any semantic conflict resolution.

| Call site | Review conclusion |
| --- | --- |
| `metrics.lower_circuit` | Public reusable component entry; common-basis comparison artifacts inherit the corrected assumption. No historical counts are replaced. |
| `costs.clifford_t` | The same assumption is corrected after explicit gadget/MCX expansion. Scalar corrections in rotation snapping remain present. |
| `routing.routed_metrics` | Arbitrary component inputs survive lowering/layout; explicit policy expansion still precedes routing. |
| `iteration_study.simulate_case` | Saved preparation/oracle/diffusion blocks are reused across iterations; all now disable initial-zero inference before QPY save/readback. |
| `noisy_iterations._components` | Separate reusable blocks disable that inference; fixed lowering seed7 is explicit. |
| `noisy_iterations._execute_seed` | Conservative false flag is valid for the assembled measured program too; routing seed, ALAP schedule, layout and validation remain intact. |

The noisy selector still rejects malformed/nonordered subsets before output or
setup, builds every preceding coherent iteration, and routes/samples only the
requested rows. Physical-qarg channel compaction, local two-wire matrix bounds,
QPY/layout signatures, active-width guards, mapped workspace restoration,
full-state comparison up to global phase, and pre-Aer persistence remain in the
offered source. Its historical 805-request ledger and completed-count rules are
unchanged. Direct child execution still relies on the parent/preparer's admitted
ideal-evidence authentication. Existing supervisor limitations and restricted
noise model remain; this review does not broaden them. Eight supervisor/forced
kill regressions were deliberately deselected; their source was inspected.

`decompose_phase_oracle` expands once and appends `forward.inverse()` on the
same held scratch. Common-comparison assembly also inverts emitted prefixes,
raw computation and preparation definitions. Reflection orders A-dagger, the
zero reflection, then A in circuit execution order, including its positive
Grover sign. QPY resolution follows the actual inverse definition, not its
preparation amplitudes. These construction facts were checked independently
of the new tests. The separate terminal sampler in `execution.local` is outside
this component correction; there is no blanket repository transpiler admission.

## Independent failures and corrected action

The probe imports the candidate, but its expected MCX action is an independent
integer XOR permutation multiplied by the declared scalar exp(0.37i), without
phase alignment. It executes the actual base `metrics.py` implementation from
`de230cc` for the failing comparison. Complex128 inputs use seed `20261103 +
width`; synthesis seed7. Controls3/4/5, total wires5/6/7, open/closed controls,
permuted controls, nonadjacent target, and a coherent spectator are covered at
optimization levels0/1/3: **18 cases**. Five-wire cases additionally compare all
32 operator columns, including both target and spectator sectors.

| Check | Measured observation |
| --- | --- |
| Old coherent MCX maximum signed-amplitude error | 0.129475442246 to 0.335122951469 across 18 cases |
| Corrected coherent maximum signed error | at most 6.113e-16 |
| Corrected five-wire all-column error | at most 5.468e-16 |
| Actual emitted inverse round-trip error | at most 4.550e-16 |
| Six-wire held-scratch phase construction | signed error 5.303e-16; dirty probability 1.164e-31 |
| Incorrect repeated-forward marking construction | signed error 0.279240742505, including its uncancelled scalar |
| Explicit MCX then Clifford+T translation | all-column error 3.003e-16 |
| Actual five-wire synthetic hardware-target routing, seeds11/23 | layout-corrected all-column error 6.827e-16 each |
| Real small noisy component builder | oracle all-column error 1.225e-16 |
| Actual emitted valid-k3 preparation inverse | signed error 1.689e-16 |
| Valid-k3 reflection against independent 2s(s-dagger a)-a | signed error 5.662e-16 |

Routing uses a five-wire `GenericBackendV2` target with recorded seed7, no
hardware submission or shot sampling. This is a layout/translation check, not
FakeTorino scientific cost evidence. Qiskit is shared by circuit construction
and evolution; XOR/reflection expectations are independent. The numerical
residuals are observed floating-point errors, not rigorous uniform bounds.

The separately prebudgeted saved **11-wire word8** probe reproduces the original
C5 best-fit failure without rerunning its study. Word8 decodes to (0,2,0,0,0),
an edge-violating word that the complete phase oracle must leave unchanged.
Old oracle hash `4a1eb969d6dcc55402ac4b13cd20e336d13b5ba076b96ea40a063060b435de75`
has dirty-output probability **0.9999999999994125** and signed error nearly1.
Corrected hash `8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268`
has signed error **8.341283395596873e-13**, dirty probability **8.802e-29**.
Both saved files were hash-verified before execution. Their original histories
remain intact; no native compilation, full C5 sweep, or new probability claim
was made.

Selected candidate tests: **96 passed, 8 deselected**, two existing Aer
deprecation warnings. These include all new component tests, selector tests,
small ideal components, routing and noisy channel/ledger checks. Independent
probe exit0:7.891322s, wait4 high water208,896,000bytes. Selected tests exit0:
15.236597s,155,697,152bytes. Fresh logs, command receipts, probe results and
pytest temporary artifacts are preserved in the checkpoint.

## Scientific exclusions, resource limits and next action

No new build is offered. The prescribed unchanged native SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was verified and explicitly selected, but not invoked. No metric patch or new
common/routed/FT/noisy study is admitted. Corrected lowering can change emitted
costs; future comparisons require fresh matched evidence and separate review.

There is **no blanket invalidation of existing artifacts**. The ten admitted
best-fit ideal rows and the 28 conditional noisy observations keep their exact
prior scope. The original 22-wire structure pilot and exact 977-instruction
oracle hash `226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`
remain **PENDING independent reachable-domain lowering proof**. A best-fit or
small-MCX counterexample does not decide that different construction. No
22-wire statevector, new noisy shot, density study, or full iteration replay
was executed. The inherited configurable22/180s ideal harness does not grant
general22-wire execution authority.

Before arrays, the checkpoint declared120s/child,300s cumulative numerical,
2GiB/process, one numerical child, threads/processes1, dense Operators<=5,
vectors<=11 (2,048 amplitudes; the later explicit saved-word8 addition to the
initial seven-wire probe plan). Original staticFT dense4 remains unchanged.
Selected small fixtures stay within11; channel matrices are at most two local
wires. No OS hard memory cap is claimed. Sandbox ps visibility was unavailable:
sampled RSS is null, not zero; terminal wait4 high water is not group peak RSS.
No numerical failure/timeout occurred. Initial probe lint found an unused import;
it was removed after preserving the executed original. Formatting/import cleanup
does not change the probe's mathematical action. Final static checks and exact
identity audit are recorded alongside the checkpoint. Read-only inspection
truncations, absent guessed paths and malformed read-only Git invocations are
retained in the task transcript; their individual RSS was not measured.

Only this uppercase review and its unique probe are owned tracked changes.
No candidate source, README, dependency pin, binary, history, archived metric,
queue, previous review or failed artifact was edited. No push, models/subagents,
Codex subprocess, sync, API/paid fallback, purchase, hardware or excluded research.

Next: the assigned coordinator verifies these six exact hashes and integrates
the source correction, preserving newer root dependencies. Any semantic overlap
requires exact independent review. Then the separately assigned common-lowering
and noise workers may produce new bounded evidence for independent review.
The structure22 proof and all wider manuscript claims retain their own gates.
