Which missing noisy Grover requests fit the 18-active-wire budget? This continuation returned **19 additional histograms, 1,216 shots**, all from previously unlaunched higher-iteration requests. For K3_k3_R1 at j=2, seed 11, proper outputs were 4/64 (6.25%; Wilson 95% interval 2.46–15.00%), versus 99.98% ideal success; 37/64 outputs used invalid color codes. These fixed-circuit observations remain pending independent review, and do not establish general noise resilience.

Together with the previous batch, 277 assigned-family histograms (17,728 shots) are now offered for review. The separately preserved 15 unsatisfiable diagnostics and one 64-shot histogram lacking a terminal receipt are excluded from that offer. No completed or held-back request was repeated. Scientific admission remains 28 original observations; the frozen denominator is $805-28=777$, with a saved status and reason for each request.

Every returned row retains 64 shots, pointwise Wilson 95% success/leakage intervals, a 2048-batch classical reference with $j+1$ draws, and explicit cost units. Zero observed success leaves cost/success unknown. Quantum native-gates/success and classical draws/evaluations per success cannot establish a speedup. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged; best-fit ideal C5 evidence still does not admit its noise adapter. Next, independently review the exact returned bytes and resource exclusions, then extend only requests that remain unattempted. Full-family and manuscript conclusions remain blocked.

<details>
<summary>New observations, resource scope and restrictive gates</summary>

| Case/j | Seed | Proper/64 | Unused/64 | Active wires | Native2q gates |
| --- | ---: | ---: | ---: | ---: | ---: |
| path6_k2_R2/2 | 37 | 0 | 0 | 12 | 1408 |
| path6_k2_R2/2 | 41 | 2 | 0 | 12 | 1334 |
| path6_k2_R2/2 | 53 | 3 | 0 | 16 | 1321 |
| path6_k2_R3/2 | 11 | 2 | 0 | 12 | 1417 |
| path6_k2_R3/2 | 23 | 3 | 0 | 12 | 1390 |
| path6_k2_R3/2 | 37 | 0 | 0 | 12 | 1408 |
| path6_k2_R3/2 | 41 | 2 | 0 | 12 | 1334 |
| path6_k2_R3/2 | 53 | 3 | 0 | 16 | 1321 |
| path7_k2_R1/2 | 11 | 2 | 0 | 14 | 2502 |
| K3_k3_R1/2 | 11 | 4 | 37 | 14 | 2695 |
| K3_k3_R1/2 | 23 | 4 | 36 | 14 | 2482 |
| K3_k3_R1/2 | 37 | 3 | 28 | 14 | 2567 |
| K3_k3_R1/2 | 41 | 5 | 39 | 17 | 2694 |
| K3_k3_R1/2 | 53 | 4 | 39 | 16 | 2622 |
| P4_k3_R3/2 | 11 | 6 | 47 | 13 | 1967 |
| P4_k3_R3/2 | 23 | 1 | 47 | 13 | 1893 |
| P4_k3_R3/2 | 37 | 3 | 46 | 13 | 1884 |
| P4_k3_R3/2 | 41 | 8 | 43 | 17 | 1925 |
| P4_k3_R3/2 | 53 | 6 | 48 | 16 | 1848 |

| Unavailable request | Seed | Status | Reason |
| --- | ---: | --- | --- |

R1 uses Hadamard preparation and the complete predicate; R2 uses valid-color preparation and the complete predicate; R3 removes the redundant domain checks with valid-color preparation. Coherent validation uses complex128 statevectors and1e-10 tolerance; noisy histograms use64 shots.

All 777 statuses: `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "compact_noise_infeasible": 9, "complete": 292, "deferred_after_failed_lower_iteration": 63, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 256, "timeout": 4, "unrun_requires_fresh_pre_aer_validation": 85}`. Intervals condition on one routed circuit, without seed pooling or simultaneous coverage. Request counts enumerate the frozen case/regime keys; two-color regimes may share circuits and simulator seeds, so these histograms must not be pooled as independent replications across regimes. The illustrated row is selected by highest iteration, then case name and seed, without reference to measured success. Cost/p is an IID-restart point estimate without a ratio interval. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP remains a calibration-product diagnostic.

For the illustrated seed, the native two-qubit count is 2695; cost divided by measured success is 43120.0 native two-qubit gates per proper output under IID restarts. The classical reference returned 503/2048 successful 3-draw batches, with pointwise 95% interval [0.22745073520787037, 0.26471275748279066]. Its IID-restart point cost is 12.214711729622266 uniform draws plus predicate evaluations per success. These units cannot be equated. The unused-code shot interval is [0.4561003154008289, 0.6913021752565454].

Current-batch schedule and checks/audits charged 775.383600s/900s; the previous completed batch's 762.050s is separate and preserved. Before allocation:850s schedule,120s per child,6GiB declared process budget, statevectors<=18,local channels<=2,no full density,one numerical child and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No dense Operator or 22-wire run occurred; original staticFT dense4 is unchanged. RSS is sampled direct-child kill monitoring, not an OS hard cap or group peak; terminal wait4 may include reaped descendants. Scientific-child sampled peak was 453.453MiB; maximum terminal wait4 high water was 454.203MiB.

The prior path7/k2/R3 seed37 j1 request had only5.304s of schedule left. It reached durable validated_pre_sampling and returned no counts before termination. Partial Aer shots, if any, are unavailable; this is not a full120s feasibility failure. A fresh attempt requires a separately justified full-child budget, not an identical short-timeout loop. Six higher requests for that case/seed remain deferred without execution.

The unchanged runner's seven prior resume regressions are reused after source-hash verification; none were rerun in this batch. This batch reserves a full120s child window before launch. Resume reopens only never-launched budget rows; duplicate/changed request sets and attempted budget rows fail closed. Exactly 275 fresh higher-iteration requests were prepared. All 605 entries of the previous frozen inventory verified before launch, and all six cf678f72 lowering paths still match exactly. Actual candidate imports were asserted. Every original ideal/noisy inventory was authenticated before preparation. The unchanged prescribed native binary was hash-selected and never invoked. New source, inheritance and evidence require exact independent admission.

The worker recount checks newly returned counts, independent LSB color classification, Wilson quadratic roots, classical trial denominators, cost units, calibration identities, ordered physical channel/readout remapping, no duplicate request and saved coherent norm/restoration residuals. Previous recounted histograms and QPY audits are reused only after their frozen inventories and result hashes verify. A separate new-row QPY readback audit checks flat gate/operand/parameter/scalar/layout/measurement compaction without new evolution. All earlier failures, 15 out-of-scope diagnostics,15 empty-domain failures and the missing-receipt histogram remain preserved and qualified.

[Prior family observations](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_coverage_20261109.md), [exact lowering integration](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md). No queue/history,README,pin,binary,archive or earlier checkpoint was edited; no model/subagent,Codex subprocess,sync,API/paid fallback,hardware or push occurred.

</details>
