How does the missing family evidence change once Grover steps are included? This continuation returned **18 additional histograms, 1,152 shots**, all from previously unlaunched higher-iteration requests. For K3_k3_R1 at j=1, seed 11, proper outputs were 1/64 (1.56%; Wilson 95% interval 0.28–8.33%), versus 64.60% ideal success; 41/64 outputs used invalid color codes. Across all five seeds, proper-output counts were [1, 5, 4, 9, 7]/64; this loss matters for the manuscript's noise claims. These fixed-circuit observations remain pending independent review, and do not establish general noise resilience.

Together with the previous batch, 191 assigned-family histograms (12,224 shots) are now offered for review. The separately preserved 15 unsatisfiable diagnostics and one 64-shot histogram lacking a terminal receipt are excluded from that offer. No completed or held-back request was repeated. Scientific admission remains 28 original observations; the frozen denominator is $805-28=777$, with a saved status and reason for each request.

Every returned row retains 64 shots, pointwise Wilson 95% success/leakage intervals, a 2048-batch classical reference with $j+1$ draws, and explicit cost units. Zero observed success leaves cost/success unknown. Quantum native-gates/success and classical draws/evaluations per success cannot establish a speedup. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged; best-fit ideal C5 evidence still does not admit its noise adapter. Next, independently review the exact returned bytes and resource exclusions, then extend only requests that remain unattempted. Full-family and manuscript conclusions remain blocked.

<details>
<summary>New observations, resource scope and restrictive gates</summary>

| Case/j | Seed | Proper/64 | Unused/64 | Active wires | Native2q gates |
| --- | ---: | ---: | ---: | ---: | ---: |
| path7_k2_R1/1 | 11 | 2 | 0 | 18 | 1210 |
| path7_k2_R1/1 | 23 | 2 | 0 | 16 | 1198 |
| path7_k2_R1/1 | 37 | 1 | 0 | 14 | 1086 |
| path7_k2_R1/1 | 41 | 2 | 0 | 14 | 1217 |
| path7_k2_R1/1 | 53 | 3 | 0 | 16 | 1263 |
| path7_k2_R2/1 | 11 | 3 | 0 | 18 | 1210 |
| path7_k2_R2/1 | 23 | 1 | 0 | 16 | 1198 |
| path7_k2_R2/1 | 37 | 0 | 0 | 14 | 1086 |
| path7_k2_R2/1 | 41 | 0 | 0 | 14 | 1217 |
| path7_k2_R2/1 | 53 | 1 | 0 | 16 | 1263 |
| path7_k2_R3/1 | 11 | 3 | 0 | 18 | 1210 |
| path7_k2_R3/1 | 23 | 1 | 0 | 16 | 1198 |
| K3_k3_R1/1 | 11 | 1 | 41 | 14 | 1248 |
| K3_k3_R1/1 | 23 | 5 | 35 | 18 | 1172 |
| K3_k3_R1/1 | 37 | 4 | 37 | 14 | 1278 |
| K3_k3_R1/1 | 41 | 9 | 40 | 14 | 1285 |
| K3_k3_R1/1 | 53 | 7 | 36 | 14 | 1283 |
| P4_k3_R3/1 | 53 | 5 | 37 | 14 | 911 |

All 777 statuses: `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "complete": 206, "deferred_after_failed_lower_iteration": 6, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 411, "timeout": 1, "unrun_requires_fresh_pre_aer_validation": 85}`. Intervals condition on one routed circuit, without seed pooling or simultaneous coverage. Cost/p is an IID-restart point estimate without a ratio interval. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP remains a calibration-product diagnostic.

For the illustrated seed, the native two-qubit count is 1248; cost divided by measured success is 79872.0 native two-qubit gates per proper output under IID restarts. The classical reference returned 350/2048 successful 2-draw batches, with pointwise 95% interval [0.1552156312422837, 0.18781353204659457]. Its IID-restart point cost is 11.702857142857143 uniform draws plus predicate evaluations per success. These units cannot be equated. The unused-code shot interval is [0.5182085060977909, 0.7471159770854826].

Current-batch schedule and checks/audits charged 864.543658s/900s; the previous completed batch's 886.449s is separate and preserved. Before allocation:850s schedule,120s per child,6GiB declared process budget, statevectors<=18,local channels<=2,no full density,one numerical child and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No dense Operator or 22-wire run occurred; original staticFT dense4 is unchanged. RSS is sampled direct-child kill monitoring, not an OS hard cap or group peak; terminal wait4 may include reaped descendants.

The final path7/k2/R3 seed37 j1 request had only5.304s of schedule left. It reached durable validated_pre_sampling and returned no counts before termination. Partial Aer shots, if any, are unavailable; this is not a full120s feasibility failure. A fresh attempt requires a separately justified full-child budget, not an identical short-timeout loop. Six higher requests for that case/seed remain deferred without execution.

Seven resume regressions passed. Resume reopens only never-launched budget rows; duplicate/changed request sets and attempted budget rows fail closed. Exactly 436 fresh higher-iteration requests were prepared. All 1887 entries of the previous frozen inventory verified before launch, and all six cf678f72 lowering paths still match exactly. Actual candidate imports were asserted. Every original ideal/noisy inventory was authenticated before preparation. The unchanged prescribed native binary was hash-selected and never invoked. New source, inheritance and evidence require exact independent admission.

The worker recount checks counts, independent LSB color classification, Wilson quadratic roots, classical trial denominators, cost units, calibration identities, ordered physical channel/readout remapping, no duplicate request and saved coherent norm/restoration residuals. A separate QPY readback audit checks flat gate/operand/parameter/scalar/layout/measurement compaction without new evolution. All earlier failures, 15 out-of-scope diagnostics,15 empty-domain failures and the missing-receipt histogram remain preserved and qualified.

[Prior family observations](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_coverage_20261109.md), [exact lowering integration](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md). No queue/history,README,pin,binary,archive or earlier checkpoint was edited; no model/subagent,Codex subprocess,sync,API/paid fallback,hardware or push occurred.

</details>
