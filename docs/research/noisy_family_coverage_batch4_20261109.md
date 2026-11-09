Which missing noisy Grover requests fit the 18-active-wire budget? This continuation returned **58 additional histograms, 3,712 shots**, all from previously unlaunched higher-iteration requests. For K3_k3_R3 at j=2, seed 11, proper outputs were 8/64 (12.50%; Wilson 95% interval 6.47–22.77%), versus 40.24% ideal success; 31/64 outputs used invalid color codes. These fixed-circuit observations remain pending independent review, and do not establish general noise resilience.

The current batch also retained 7 active-width exclusions and 0 timeouts. These unavailable measurements are not zero-success observations; they restrict the frozen five-seed family coverage. P4_k3_R1 j=1, seed23, routes 17 logical wires to 23 active physical wires.

Together with the previous batch, 258 assigned-family histograms (16,512 shots) are now offered for review. The separately preserved 15 unsatisfiable diagnostics and one 64-shot histogram lacking a terminal receipt are excluded from that offer. No completed or held-back request was repeated. Scientific admission remains 28 original observations; the frozen denominator is $805-28=777$, with a saved status and reason for each request.

Every returned row retains 64 shots, pointwise Wilson 95% success/leakage intervals, a 2048-batch classical reference with $j+1$ draws, and explicit cost units. Zero observed success leaves cost/success unknown. Quantum native-gates/success and classical draws/evaluations per success cannot establish a speedup. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged; best-fit ideal C5 evidence still does not admit its noise adapter. Next, independently review the exact returned bytes and resource exclusions, then extend only requests that remain unattempted. Full-family and manuscript conclusions remain blocked.

<details>
<summary>New observations, resource scope and restrictive gates</summary>

| Case/j | Seed | Proper/64 | Unused/64 | Active wires | Native2q gates |
| --- | ---: | ---: | ---: | ---: | ---: |
| path3_k2_R2/2 | 11 | 22 | 0 | 6 | 137 |
| path3_k2_R2/2 | 23 | 19 | 0 | 6 | 137 |
| path3_k2_R2/2 | 37 | 13 | 0 | 6 | 137 |
| path3_k2_R2/2 | 41 | 17 | 0 | 6 | 137 |
| path3_k2_R2/2 | 53 | 19 | 0 | 6 | 137 |
| path3_k2_R3/2 | 11 | 22 | 0 | 6 | 137 |
| path3_k2_R3/2 | 23 | 19 | 0 | 6 | 137 |
| path3_k2_R3/2 | 37 | 13 | 0 | 6 | 137 |
| path3_k2_R3/2 | 41 | 17 | 0 | 6 | 137 |
| path3_k2_R3/2 | 53 | 19 | 0 | 6 | 137 |
| path4_k2_R1/2 | 11 | 24 | 0 | 8 | 277 |
| path4_k2_R1/2 | 23 | 20 | 0 | 8 | 225 |
| path4_k2_R1/2 | 37 | 18 | 0 | 8 | 214 |
| path4_k2_R1/2 | 41 | 25 | 0 | 8 | 214 |
| path4_k2_R1/2 | 53 | 12 | 0 | 8 | 270 |
| path4_k2_R2/2 | 11 | 13 | 0 | 8 | 277 |
| path4_k2_R2/2 | 23 | 27 | 0 | 8 | 225 |
| path4_k2_R2/2 | 37 | 20 | 0 | 8 | 214 |
| path4_k2_R2/2 | 41 | 20 | 0 | 8 | 214 |
| path4_k2_R2/2 | 53 | 17 | 0 | 8 | 270 |
| path4_k2_R3/2 | 11 | 13 | 0 | 8 | 277 |
| path4_k2_R3/2 | 23 | 27 | 0 | 8 | 225 |
| path4_k2_R3/2 | 37 | 20 | 0 | 8 | 214 |
| path4_k2_R3/2 | 41 | 20 | 0 | 8 | 214 |
| path4_k2_R3/2 | 53 | 17 | 0 | 8 | 270 |
| path5_k2_R1/2 | 11 | 9 | 0 | 10 | 572 |
| path5_k2_R1/2 | 23 | 6 | 0 | 10 | 538 |
| path5_k2_R1/2 | 37 | 6 | 0 | 10 | 570 |
| path5_k2_R1/2 | 41 | 2 | 0 | 10 | 586 |
| path5_k2_R1/2 | 53 | 7 | 0 | 10 | 591 |
| path5_k2_R2/2 | 11 | 9 | 0 | 10 | 572 |
| path5_k2_R2/2 | 23 | 7 | 0 | 10 | 538 |
| path5_k2_R2/2 | 37 | 10 | 0 | 10 | 570 |
| path5_k2_R2/2 | 41 | 6 | 0 | 10 | 586 |
| path5_k2_R2/2 | 53 | 14 | 0 | 10 | 591 |
| path5_k2_R3/2 | 11 | 9 | 0 | 10 | 572 |
| path5_k2_R3/2 | 23 | 7 | 0 | 10 | 538 |
| path5_k2_R3/2 | 37 | 10 | 0 | 10 | 570 |
| path5_k2_R3/2 | 41 | 6 | 0 | 10 | 586 |
| path5_k2_R3/2 | 53 | 14 | 0 | 10 | 591 |
| path6_k2_R1/2 | 11 | 1 | 0 | 12 | 1417 |
| path6_k2_R1/2 | 23 | 1 | 0 | 12 | 1390 |
| path6_k2_R1/2 | 37 | 3 | 0 | 12 | 1408 |
| path6_k2_R1/2 | 41 | 2 | 0 | 12 | 1334 |
| path6_k2_R1/2 | 53 | 2 | 0 | 16 | 1321 |
| path6_k2_R2/2 | 11 | 2 | 0 | 12 | 1417 |
| path6_k2_R2/2 | 23 | 3 | 0 | 12 | 1390 |
| path8_k2_R3/1 | 41 | 2 | 0 | 16 | 1780 |
| path8_k2_R3/1 | 53 | 0 | 0 | 16 | 1885 |
| K3_k3_R3/2 | 11 | 8 | 31 | 11 | 998 |
| K3_k3_R3/2 | 23 | 5 | 30 | 11 | 1023 |
| K3_k3_R3/2 | 37 | 5 | 33 | 11 | 1010 |
| K3_k3_R3/2 | 41 | 8 | 34 | 16 | 1083 |
| K3_k3_R3/2 | 53 | 7 | 35 | 14 | 1044 |
| P4_k3_R1/1 | 11 | 8 | 40 | 17 | 2126 |
| P4_k3_R1/1 | 37 | 3 | 45 | 17 | 2202 |
| P4_k3_R2/1 | 23 | 8 | 41 | 17 | 2232 |
| P4_k3_R2/1 | 41 | 3 | 41 | 17 | 2273 |

| Unavailable request | Seed | Status | Reason |
| --- | ---: | --- | --- |
| path8_k2_R3/j1 | 37 | compact_noise_infeasible | 20 active > 18 |
| P4_k3_R1/j1 | 23 | compact_noise_infeasible | 23 active > 18 |
| P4_k3_R1/j1 | 41 | compact_noise_infeasible | 20 active > 18 |
| P4_k3_R1/j1 | 53 | compact_noise_infeasible | 28 active > 18 |
| P4_k3_R2/j1 | 11 | compact_noise_infeasible | 19 active > 18 |
| P4_k3_R2/j1 | 37 | compact_noise_infeasible | 20 active > 18 |
| P4_k3_R2/j1 | 53 | compact_noise_infeasible | 19 active > 18 |

R1 uses Hadamard preparation and the complete predicate; R2 uses valid-color preparation and the complete predicate; R3 removes the redundant domain checks with valid-color preparation. Coherent validation uses complex128 statevectors and1e-10 tolerance; noisy histograms use64 shots.

All 777 statuses: `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "compact_noise_infeasible": 9, "complete": 273, "deferred_after_failed_lower_iteration": 63, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 275, "timeout": 4, "unrun_requires_fresh_pre_aer_validation": 85}`. Intervals condition on one routed circuit, without seed pooling or simultaneous coverage. Request counts enumerate the frozen case/regime keys; two-color regimes may share circuits and simulator seeds, so these histograms must not be pooled as independent replications across regimes. The illustrated row is selected by highest iteration, then case name and seed, without reference to measured success. Cost/p is an IID-restart point estimate without a ratio interval. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP remains a calibration-product diagnostic.

For the illustrated seed, the native two-qubit count is 998; cost divided by measured success is 7984.0 native two-qubit gates per proper output under IID restarts. The classical reference returned 1082/2048 successful 3-draw batches, with pointwise 95% interval [0.5066674906724182, 0.5498670917151858]. Its IID-restart point cost is 5.678373382624769 uniform draws plus predicate evaluations per success. These units cannot be equated. The unused-code shot interval is [0.36633551665432623, 0.6041839852141989].

Current-batch schedule and checks/audits charged 762.049734s/900s; the previous completed batch's 750.787s is separate and preserved. Before allocation:850s schedule,120s per child,6GiB declared process budget, statevectors<=18,local channels<=2,no full density,one numerical child and compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No dense Operator or 22-wire run occurred; original staticFT dense4 is unchanged. RSS is sampled direct-child kill monitoring, not an OS hard cap or group peak; terminal wait4 may include reaped descendants. Scientific-child sampled peak was 422.641MiB; maximum terminal wait4 high water was 456.641MiB.

The prior path7/k2/R3 seed37 j1 request had only5.304s of schedule left. It reached durable validated_pre_sampling and returned no counts before termination. Partial Aer shots, if any, are unavailable; this is not a full120s feasibility failure. A fresh attempt requires a separately justified full-child budget, not an identical short-timeout loop. Six higher requests for that case/seed remain deferred without execution.

Seven resume regressions passed. This batch reserves a full120s child window before launch. Resume reopens only never-launched budget rows; duplicate/changed request sets and attempted budget rows fail closed. Exactly 357 fresh higher-iteration requests were prepared. All 156 entries of the previous frozen inventory verified before launch, and all six cf678f72 lowering paths still match exactly. Actual candidate imports were asserted. Every original ideal/noisy inventory was authenticated before preparation. The unchanged prescribed native binary was hash-selected and never invoked. New source, inheritance and evidence require exact independent admission.

The worker recount checks counts, independent LSB color classification, Wilson quadratic roots, classical trial denominators, cost units, calibration identities, ordered physical channel/readout remapping, no duplicate request and saved coherent norm/restoration residuals. A separate QPY readback audit checks flat gate/operand/parameter/scalar/layout/measurement compaction without new evolution. All earlier failures, 15 out-of-scope diagnostics,15 empty-domain failures and the missing-receipt histogram remain preserved and qualified.

[Prior family observations](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_coverage_20261109.md), [exact lowering integration](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md). No queue/history,README,pin,binary,archive or earlier checkpoint was edited; no model/subagent,Codex subprocess,sync,API/paid fallback,hardware or push occurred.

</details>
