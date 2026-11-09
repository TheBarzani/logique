Which missing noisy Grover requests fit the 18-active-wire budget? This continuation returned **1 additional histograms, 64 shots**, all from previously unlaunched higher-iteration requests. For K3_k3_R1 at j=3, seed 53, proper outputs were 6/64 (9.38%; Wilson 95% interval 4.37–18.98%), versus 67.42% ideal success; 38/64 outputs used invalid color codes. These fixed-circuit observations remain pending independent review, and do not establish general noise resilience.

The current batch also retained 0 active-width exclusions and 6 timeouts. These unavailable measurements restrict five-seed coverage.

Together with the previous batch, 331 assigned-family histograms (21,184 shots) are now offered for review. The separately preserved 15 unsatisfiable diagnostics and one 64-shot histogram lacking a terminal receipt are excluded from that offer. No completed or held-back request was repeated. Scientific admission remains 28 original observations; the frozen denominator is $805-28=777$, with a saved status and reason for each request.

Every returned row retains 64 shots, pointwise Wilson 95% success/leakage intervals, a 2048-batch classical reference with $j+1$ draws, and explicit cost units. Zero observed success leaves cost/success unknown. The differing quantum/classical cost units cannot establish a speedup. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged; best-fit ideal C5 evidence still does not admit its noise adapter. Next, independently review the exact returned bytes and resource exclusions, then extend only requests that remain unattempted. Full-family and manuscript conclusions remain blocked.

<details>
<summary>New observations, resource scope and restrictive gates</summary>

| Case/j | Seed | Proper/64 | Unused/64 | Active wires | Native2q gates |
| --- | ---: | ---: | ---: | ---: | ---: |
| K3_k3_R1/3 | 53 | 6 | 38 | 14 | 3879 |

| Unavailable request | Seed | Status | Reason |
| --- | ---: | --- | --- |
| path7_k2_R1/j3 | 11 | timeout | Configured 120s; observed 120.011418s; stage=validated_pre_sampling; no counts returned; no identical retry |
| path7_k2_R1/j3 | 37 | timeout | Configured 120s; observed 120.018168s; stage=validated_pre_sampling; no counts returned; no identical retry |
| path7_k2_R1/j3 | 53 | timeout | Configured 120s; observed 120.016583s; stage=validated_pre_sampling; no counts returned; no identical retry |
| path7_k2_R2/j3 | 11 | timeout | Configured 120s; observed 120.021855s; stage=validated_pre_sampling; no counts returned; no identical retry |
| path7_k2_R2/j3 | 37 | timeout | Configured 120s; observed 120.022013s; stage=validated_pre_sampling; no counts returned; no identical retry |
| path7_k2_R2/j3 | 53 | timeout | Configured 120s; observed 120.016084s; stage=validated_pre_sampling; no counts returned; no identical retry |

R1 uses Hadamard preparation and the complete predicate; R2 uses valid-color preparation and the complete predicate; R3 removes the redundant domain checks with valid-color preparation. Coherent validation uses complex128 statevectors and1e-10 tolerance; noisy histograms use64 shots.

Frozen 805 statuses (including 28 admitted and all 777 remaining): `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "compact_noise_infeasible": 20, "complete": 346, "deferred_after_failed_lower_iteration": 182, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 55, "timeout": 21, "unrun_requires_fresh_pre_aer_validation": 85}`. Intervals condition on one routed circuit, without seed pooling or simultaneous coverage. Request counts enumerate the frozen case/regime keys; two-color regimes may share circuits and simulator seeds, so these histograms must not be pooled as independent replications across regimes. The illustrated row is selected by highest iteration, then case name and seed, without reference to measured success. Cost/p is an IID-restart point estimate without a ratio interval. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP remains a calibration-product diagnostic.

For the illustrated seed, the native two-qubit count is 3879; cost divided by measured success is 41376.0 native two-qubit gates per proper output under IID restarts. The classical reference returned 664/2048 successful 4-draw batches, with pointwise 95% interval [0.3042917563202995, 0.34480393920491736]. Its IID-restart point cost is 12.337349397590362 uniform draws plus predicate evaluations per success. These units cannot be equated. The unused-code shot interval is [0.4714520812860451, 0.7054309075028039].

Current-batch schedule and checks/audits charged 822.259372s/900s; the previous completed batch's 844.901s is separate and preserved. Before allocation:850s schedule,120s per child,6GiB declared process budget, statevectors<=18,local channels<=2,no full density,one numerical child and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No dense Operator or 22-wire run occurred; original staticFT dense4 is unchanged. RSS is sampled direct-child kill monitoring, not an OS hard cap or group peak; terminal wait4 may include reaped descendants. Scientific-child sampled peak was 445.531MiB; maximum terminal wait4 high water was 475.062MiB.

The prior path7/k2/R3 seed37 j1 request had only5.304s of schedule left. It reached durable validated_pre_sampling and returned no counts before termination. Partial Aer shots, if any, are unavailable; this is not a full120s feasibility failure. A fresh attempt requires a separately justified full-child budget, not an identical short-timeout loop. Six higher requests for that case/seed remain deferred without execution.

The unchanged runner's seven prior resume regressions are reused after source-hash verification; none were rerun in this batch. This batch reserves a full120s child window before launch. Resume reopens only never-launched budget rows; duplicate/changed request sets and attempted budget rows fail closed. Exactly 86 fresh higher-iteration requests were prepared. All 196 entries of the previous frozen inventory verified before launch, and all six cf678f72 lowering paths still match exactly. Actual candidate imports were asserted. Every original ideal/noisy inventory was authenticated before preparation. The unchanged prescribed native binary was hash-selected and never invoked. New source, inheritance and evidence require exact independent admission.

The worker recount checks newly returned counts, independent LSB color classification, Wilson quadratic roots, classical trial denominators, cost units, calibration identities, ordered physical channel/readout remapping, no duplicate request and saved coherent norm/restoration residuals. Previous recounted histograms and QPY audits are reused only after their frozen inventories and result hashes verify. A separate new-row QPY readback audit checks flat gate/operand/parameter/scalar/layout/measurement compaction without new evolution. All earlier failures, 15 out-of-scope diagnostics,15 empty-domain failures and the missing-receipt histogram remain preserved and qualified.

[Prior family observations](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_coverage_20261109.md), [exact lowering integration](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md). No queue/history,README,pin,binary,archive or earlier checkpoint was edited; no model/subagent,Codex subprocess,sync,API/paid fallback,hardware or push occurred.

</details>
