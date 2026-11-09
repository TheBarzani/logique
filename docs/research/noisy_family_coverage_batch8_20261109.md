Which missing noisy Grover requests fit the 18-active-wire budget? This continuation returned **15 additional histograms, 960 shots**, all from previously unlaunched higher-iteration requests. For K3_k3_R1 at j=3, seed 11, proper outputs were 7/64 (10.94%; Wilson 95% interval 5.40–20.90%), versus 67.42% ideal success; 40/64 outputs used invalid color codes. These fixed-circuit observations remain pending independent review, and do not establish general noise resilience.

The current batch also retained 0 active-width exclusions and 3 timeouts. These unavailable measurements restrict five-seed coverage.

K3 R1 seeds23/37/41 returned no counts at j=3.

Together with the previous batch, 330 assigned-family histograms (21,120 shots) are now offered for review. The separately preserved 15 unsatisfiable diagnostics and one 64-shot histogram lacking a terminal receipt are excluded from that offer. No completed or held-back request was repeated. Scientific admission remains 28 original observations; the frozen denominator is $805-28=777$, with a saved status and reason for each request.

Every returned row retains 64 shots, pointwise Wilson 95% success/leakage intervals, a 2048-batch classical reference with $j+1$ draws, and explicit cost units. Zero observed success leaves cost/success unknown. The differing quantum/classical cost units cannot establish a speedup. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged; best-fit ideal C5 evidence still does not admit its noise adapter. Next, independently review the exact returned bytes and resource exclusions, then extend only requests that remain unattempted. Full-family and manuscript conclusions remain blocked.

<details>
<summary>New observations, resource scope and restrictive gates</summary>

| Case/j | Seed | Proper/64 | Unused/64 | Active wires | Native2q gates |
| --- | ---: | ---: | ---: | ---: | ---: |
| path6_k2_R1/3 | 23 | 0 | 0 | 16 | 2180 |
| path6_k2_R1/3 | 37 | 0 | 0 | 16 | 2139 |
| path6_k2_R1/3 | 41 | 0 | 0 | 12 | 2096 |
| path6_k2_R1/3 | 53 | 0 | 0 | 12 | 2211 |
| path6_k2_R2/3 | 11 | 1 | 0 | 12 | 2091 |
| path6_k2_R2/3 | 23 | 0 | 0 | 16 | 2180 |
| path6_k2_R2/3 | 37 | 0 | 0 | 16 | 2139 |
| path6_k2_R2/3 | 41 | 3 | 0 | 12 | 2096 |
| path6_k2_R2/3 | 53 | 2 | 0 | 12 | 2211 |
| path6_k2_R3/3 | 11 | 1 | 0 | 12 | 2091 |
| path6_k2_R3/3 | 23 | 0 | 0 | 16 | 2180 |
| path6_k2_R3/3 | 37 | 0 | 0 | 16 | 2139 |
| path6_k2_R3/3 | 41 | 3 | 0 | 12 | 2096 |
| path6_k2_R3/3 | 53 | 2 | 0 | 12 | 2211 |
| K3_k3_R1/3 | 11 | 7 | 40 | 15 | 4066 |

| Unavailable request | Seed | Status | Reason |
| --- | ---: | --- | --- |
| K3_k3_R1/j3 | 23 | timeout | Configured 120s; observed 120.019829s; stage=validated_pre_sampling; no counts returned; no identical retry |
| K3_k3_R1/j3 | 37 | timeout | Configured 120s; observed 120.015325s; stage=validated_pre_sampling; no counts returned; no identical retry |
| K3_k3_R1/j3 | 41 | timeout | Configured 120s; observed 120.020986s; stage=validated_pre_sampling; no counts returned; no identical retry |

R1 uses Hadamard preparation and the complete predicate; R2 uses valid-color preparation and the complete predicate; R3 removes the redundant domain checks with valid-color preparation. Coherent validation uses complex128 statevectors and1e-10 tolerance; noisy histograms use64 shots.

Frozen 805 statuses (including 28 admitted and all 777 remaining): `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "compact_noise_infeasible": 20, "complete": 345, "deferred_after_failed_lower_iteration": 158, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 86, "timeout": 15, "unrun_requires_fresh_pre_aer_validation": 85}`. Intervals condition on one routed circuit, without seed pooling or simultaneous coverage. Request counts enumerate the frozen case/regime keys; two-color regimes may share circuits and simulator seeds, so these histograms must not be pooled as independent replications across regimes. The illustrated row is selected by highest iteration, then case name and seed, without reference to measured success. Cost/p is an IID-restart point estimate without a ratio interval. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP remains a calibration-product diagnostic.

For the illustrated seed, the native two-qubit count is 4066; cost divided by measured success is 37174.857142857145 native two-qubit gates per proper output under IID restarts. The classical reference returned 656/2048 successful 4-draw batches, with pointwise 95% interval [0.30045697048100245, 0.34084085161144134]. Its IID-restart point cost is 12.487804878048781 uniform draws plus predicate evaluations per success. These units cannot be equated. The unused-code shot interval is [0.5025037868400452, 0.7333401982117536].

Current-batch schedule and checks/audits charged 844.901254s/900s; the previous completed batch's 748.804s is separate and preserved. Before allocation:850s schedule,120s per child,6GiB declared process budget, statevectors<=18,local channels<=2,no full density,one numerical child and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No dense Operator or 22-wire run occurred; original staticFT dense4 is unchanged. RSS is sampled direct-child kill monitoring, not an OS hard cap or group peak; terminal wait4 may include reaped descendants. Scientific-child sampled peak was 430.828MiB; maximum terminal wait4 high water was 454.297MiB.

The prior path7/k2/R3 seed37 j1 request had only5.304s of schedule left. It reached durable validated_pre_sampling and returned no counts before termination. Partial Aer shots, if any, are unavailable; this is not a full120s feasibility failure. A fresh attempt requires a separately justified full-child budget, not an identical short-timeout loop. Six higher requests for that case/seed remain deferred without execution.

The unchanged runner's seven prior resume regressions are reused after source-hash verification; none were rerun in this batch. This batch reserves a full120s child window before launch. Resume reopens only never-launched budget rows; duplicate/changed request sets and attempted budget rows fail closed. Exactly 104 fresh higher-iteration requests were prepared. All 413 entries of the previous frozen inventory verified before launch, and all six cf678f72 lowering paths still match exactly. Actual candidate imports were asserted. Every original ideal/noisy inventory was authenticated before preparation. The unchanged prescribed native binary was hash-selected and never invoked. New source, inheritance and evidence require exact independent admission.

The worker recount checks newly returned counts, independent LSB color classification, Wilson quadratic roots, classical trial denominators, cost units, calibration identities, ordered physical channel/readout remapping, no duplicate request and saved coherent norm/restoration residuals. Previous recounted histograms and QPY audits are reused only after their frozen inventories and result hashes verify. A separate new-row QPY readback audit checks flat gate/operand/parameter/scalar/layout/measurement compaction without new evolution. All earlier failures, 15 out-of-scope diagnostics,15 empty-domain failures and the missing-receipt histogram remain preserved and qualified.

[Prior family observations](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_coverage_20261109.md), [exact lowering integration](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md). No queue/history,README,pin,binary,archive or earlier checkpoint was edited; no model/subagent,Codex subprocess,sync,API/paid fallback,hardware or push occurred.

</details>
