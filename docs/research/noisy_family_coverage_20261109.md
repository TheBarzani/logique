Can the missing graph-family noise requests be measured under the frozen calibration and 18-active-wire limit? This batch returned **173 new family histograms, 11,072 shots**, including 64 rows after at least one Grover iteration. The saved circuits passed the admitted pre-sampling layout, ordered-channel, coherence and workspace-restoration gates. P4/k3/R3 at j=1, seed11, returned 7/64 proper outputs (10.94%;95% interval 5.40–20.90%), against 97.59% ideal success; 38/64 outputs used invalid color codes. This unfavorable fixed-circuit result supports no noise-resilience claim.

This extends the previous 28 conditional observations without rerunning them. The comparison denominator remains $805-28=777$ requests pending scientific admission; every one now has a saved status and reason. Each returned histogram uses 64 shots, pointwise Wilson 95% intervals and a 2048-batch classical reference with $j+1$ draws per batch. Native two-qubit-gates/success and classical draws/evaluations per success retain different units; zero observed success leaves cost/success unknown.

Independent review of this runner, its exact inheritance and new evidence is still pending. An initial scheduling error and its diagnostic/failure artifacts are preserved separately below. Original 50 C5 structure exclusions and the separately owned K3 retry remain unchanged. Best-fit C5 ideal evidence does not admit its noise adapter. Next, review the exact returned counts and extend only the missing higher-iteration requests; full-family noise resilience and manuscript conclusions remain unsupported.

<details>
<summary>Measured scope, exclusions and reproducibility</summary>

| Case/iteration | Seeds | Proper outputs/64 | Unused codes/64 |
| --- | --- | --- | --- |
| K3_k3_R1/j0 | [11, 23, 37, 41, 53] | [4, 3, 6, 4, 6] | [40, 42, 39, 38, 38] |
| K3_k3_R3/j0 | [11, 23, 37, 41, 53] | [9, 13, 13, 11, 10] | [2, 2, 3, 4, 1] |
| K3_k3_R3/j1 | [11, 23, 37, 41, 53] | [11, 10, 11, 17, 12] | [25, 24, 21, 19, 31] |
| P4_k3_R1/j0 | [11, 23, 37, 41, 53] | [8, 10, 8, 8, 5] | [46, 39, 46, 40, 48] |
| P4_k3_R2/j0 | [11, 23, 37, 41, 53] | [23, 20, 17, 19, 19] | [3, 2, 4, 4, 4] |
| P4_k3_R3/j0 | [11, 23, 37, 41, 53] | [23, 20, 17, 19, 19] | [3, 2, 4, 4, 4] |
| P4_k3_R3/j1 | [11, 23, 37, 41] | [7, 13, 7, 6] | [38, 38, 46, 43] |
| path3_k2_R2/j0 | [11, 23, 37, 41, 53] | [15, 18, 16, 11, 14] | [0, 0, 0, 0, 0] |
| path3_k2_R2/j1 | [11, 23, 37, 41, 53] | [49, 49, 55, 53, 50] | [0, 0, 0, 0, 0] |
| path3_k2_R3/j0 | [11, 23, 37, 41, 53] | [15, 18, 16, 11, 14] | [0, 0, 0, 0, 0] |
| path3_k2_R3/j1 | [11, 23, 37, 41, 53] | [49, 49, 55, 53, 50] | [0, 0, 0, 0, 0] |
| path4_k2_R1/j0 | [11, 23, 37, 41, 53] | [6, 12, 5, 6, 10] | [0, 0, 0, 0, 0] |
| path4_k2_R1/j1 | [11, 23, 37, 41, 53] | [36, 34, 32, 36, 28] | [0, 0, 0, 0, 0] |
| path4_k2_R2/j0 | [23, 37, 41, 53] | [12, 5, 6, 10] | [0, 0, 0, 0] |
| path4_k2_R2/j1 | [11, 23, 37, 41, 53] | [36, 29, 31, 25, 24] | [0, 0, 0, 0, 0] |
| path4_k2_R3/j0 | [11, 23, 37, 41, 53] | [6, 12, 5, 6, 10] | [0, 0, 0, 0, 0] |
| path4_k2_R3/j1 | [11, 23, 37, 41, 53] | [36, 29, 31, 25, 24] | [0, 0, 0, 0, 0] |
| path5_k2_R1/j0 | [11, 23, 37, 41, 53] | [5, 3, 3, 2, 3] | [0, 0, 0, 0, 0] |
| path5_k2_R1/j1 | [11, 23, 37, 41, 53] | [8, 8, 6, 8, 7] | [0, 0, 0, 0, 0] |
| path5_k2_R2/j0 | [11, 23, 37, 41, 53] | [5, 3, 3, 2, 3] | [0, 0, 0, 0, 0] |
| path5_k2_R2/j1 | [11, 23, 37, 41, 53] | [6, 8, 9, 9, 7] | [0, 0, 0, 0, 0] |
| path5_k2_R3/j0 | [11, 23, 37, 41, 53] | [5, 3, 3, 2, 3] | [0, 0, 0, 0, 0] |
| path5_k2_R3/j1 | [11, 23, 37, 41, 53] | [6, 8, 9, 9, 7] | [0, 0, 0, 0, 0] |
| path6_k2_R1/j0 | [11, 23, 37, 41, 53] | [4, 4, 0, 3, 4] | [0, 0, 0, 0, 0] |
| path6_k2_R1/j1 | [11, 23, 37, 41, 53] | [4, 4, 3, 0, 2] | [0, 0, 0, 0, 0] |
| path6_k2_R2/j0 | [11, 23, 37, 41, 53] | [4, 4, 0, 3, 3] | [0, 0, 0, 0, 0] |
| path6_k2_R2/j1 | [11, 23, 37, 41, 53] | [3, 1, 3, 1, 3] | [0, 0, 0, 0, 0] |
| path6_k2_R3/j0 | [11, 23, 37, 41, 53] | [4, 4, 0, 3, 4] | [0, 0, 0, 0, 0] |
| path6_k2_R3/j1 | [11, 23, 37, 41, 53] | [3, 1, 3, 1, 3] | [0, 0, 0, 0, 0] |
| path7_k2_R1/j0 | [11, 23, 37, 41, 53] | [0, 2, 1, 1, 1] | [0, 0, 0, 0, 0] |
| path7_k2_R2/j0 | [11, 23, 37, 41, 53] | [0, 2, 1, 1, 1] | [0, 0, 0, 0, 0] |
| path7_k2_R3/j0 | [11, 23, 37, 41, 53] | [0, 2, 1, 1, 1] | [0, 0, 0, 0, 0] |
| path8_k2_R1/j0 | [11, 23, 37, 41, 53] | [0, 1, 0, 1, 0] | [0, 0, 0, 0, 0] |
| path8_k2_R2/j0 | [11, 23, 37, 41, 53] | [0, 1, 0, 1, 0] | [0, 0, 0, 0, 0] |
| path8_k2_R3/j0 | [11, 23, 37, 41, 53] | [0, 1, 0, 1, 0] | [0, 0, 0, 0, 0] |
| unsat_K3_k2_R1/j0 | [11, 23, 37, 41, 53] | [0, 0, 0, 0, 0] | [0, 0, 0, 0, 0] |
| unsat_K3_k2_R2/j0 | [11, 23, 37, 41, 53] | [0, 0, 0, 0, 0] | [0, 0, 0, 0, 0] |
| unsat_K3_k2_R3/j0 | [11, 23, 37, 41, 53] | [0, 0, 0, 0, 0] | [0, 0, 0, 0, 0] |

All counts are local FakeTorino-model observations pending independent review. Gate/readout and per-gate thermal noise exclude idle relaxation, drift and crosstalk; ESP is a calibration diagnostic, never success. Intervals condition on each routed seed and have neither simultaneous coverage nor a cost-ratio confidence guarantee.

For P4/k3/R3 j=1 seed11,927 routed native two-qubit gates and7/64 proper outputs give $927/(7/64)=8475.43$ native two-qubit gates per proper output under IID restarts. The independent classical reference returned1067/2048 successful two-draw batches (52.10%), so $2/(1067/2048)=3.8388$ draws plus predicate evaluations per success. These are incompatible resource units, not a speedup comparison. The17-active-wire scheduled duration estimate is83.592 microseconds, not hardware time. Across returned rows the largest saved full-state residual up to global phase was 1.724e-14 and largest data-marginal residual2.387e-15 at tolerance1e-10.

Statuses: `{"admitted_observation_do_not_rerun": 28, "blocked_pending_selector_review": 1, "complete": 188, "excluded_21_active_wires": 1, "excluded_original_structure_width": 50, "failed": 15, "interrupted_scope_stop": 1, "not_launched_budget": 436, "unrun_requires_fresh_pre_aer_validation": 85}`. The maximum sampled direct-child RSS was 422.734MiB; wait4 high water was 448.578MiB. Neither measures a hard cap or simultaneous process-group peak. Conservative numerical boundary charge, including the stopped first schedule and checks: 886.448847s/900s. Serial children were bounded by120s with6GiB declared process budgets, statevectors at most18 wires, local noise matrices at most2 wires, and all compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. No full density matrix or dense Operator was used in the study. The original staticFT dense4 limit is unchanged.

Candidate contracts:61 tests passed,7 supervisor/forced-termination cases deselected, two existing Aer deprecation warnings; selected Black/Ruff pass. Six exact reviewed lowering paths from cf678f72 were deliberately imported in separate commit2ee63d4. Unique runner/config are d5385a6. All other library source remains at assigned base. A worker recount checks histogram decoding, Wilson roots, units, ordered noise compaction, calibration identity and no duplicate requests. Saved QPY compactions also pass flat gate/operand/parameter/global-phase/layout/LSB-measurement comparison without evolution. These are not independent admission. An initial scalar audit timed out at15.020s because it repeatedly parsed the same23MB snapshot; the original script/log/receipt are preserved. Caching immutable full snapshots reduced the corrected audit to5.994s; QPY audit took3.061s. Neither audit reran sampling.

The first schedule also produced 15 unsatisfiable-K3 diagnostic histograms and 15 empty-domain setup failures outside the assigned families. Its executed runner and all outputs are retained. The controlled stop leaves one empty child receipt. That raced path4/R2 seed11 j0 child saved64 shots, but its terminal ownership/RSS receipt is absent. This additional histogram is held back from the173-row offer and must not be rerun. Its process was absent at the subsequent host check; a conservative10s cleanup window is charged beyond parent termination. Every failed/partial artifact and the executed pre-filter runner are preserved. No historical output, dependency pin, binary, queue/history, archive or README was changed. No native build/invocation, 22-wire replay, model/subagent launch, sync, API/paid fallback, hardware or push occurred.

Background gates: [exact lowering admission](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md), [full research successor](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/full_research_successor_20261101.md), [selected retry decision](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_final_integration_20261101.md).

</details>
