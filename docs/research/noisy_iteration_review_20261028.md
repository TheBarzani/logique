# Independent noisy-iteration review — 28 October 2026

**Decision: BLOCK** the exact candidate below for integration/scientific noisy
iteration admission. This bounded review is complete. Full Task 7 and the full
revision remain open. Passing local probes do not admit general noise resilience,
FT, RUS, ideal-amplitude guarantees, comparative advantage, or manuscript claims.

Candidate: `/Users/mar/codex-work/logique/dump/1028023823-full-revision-implementation-coordinator/worktrees/noisy-iteration-study`.
Its HEAD is `fc734b386449e69716d0ac3018b878a23e05ba95`; the three new candidate
files are **untracked**, not a committed implementation. At intake and final
inspection, `NOISY_ITERATION_CHECKPOINT.md` and the candidate's `dump/` directory
do not exist. There are no supplied noisy results, saved routed circuits, run
manifest, or completed five-seed ledger to admit. The reviewer did not modify
the candidate or substitute another branch's implementation.

## Exact bytes and evidence

| Candidate file | SHA256 |
| --- | --- |
| `src/logique/benchmarks/noisy_iterations.py` | `cb611ac797cbe90bdd39dfd7cb473ca3292c26d5536d8efeb70f0dee3a6cc243` |
| `configs/noisy_iteration_pilot.json` | `ee8b9b628e89539346ca656a0ec13511bead494335e6208a4fc4c2752ae1709a` |
| `tests/test_noisy_iterations.py` | `c4e16dbd2dc4559dcab429466de17ca48c754c0e97187a8908f395bdc4282b99` |
| inherited `src/logique/benchmarks/coloring_study.py` | `3df109e3d8a368ad552ca8f628a6ee96736e306af488c9e1481493845399ce62` |
| inherited `src/logique/benchmarks/routing.py` | `b2341cf2cb17eda7c0f2d54f7b02293ec1f8e66981c4c474869fd95cedf5d275` |

Checkpoint directory relative to this review worktree:
`dump/1028073812-noisy-iteration-review/` (called `RUN` below).
`RUN/attempt2/checks.json` records thirteen relevant source/input hashes and
explicit candidate import paths; source snapshots and end-of-run equality checks
are retained. `RUN/checkpoint.json` inventories this review's evidence, commands,
commits and next action. No unrelated recursive repository hash scan was made.

| Review evidence relative to RUN | SHA256 |
| --- | --- |
| `attempt2/probes/results.json` | `e708e4ff3df0e8907b21f407825a63835be836055807d61c5abf337bf03df6b6` |
| `attempt3/probes/results.json` | `e4421239af8830277480d463112c879e655a6862041218554d881d9f4d4acc46` |
| `attempt2/candidate_smoke.log` | `dfcfda7f1b7bb0a607e2f9371ee76d94743edbb73ec1da0e457bcc1cd61b0899` |
| `sweep_ledger.json` | `b7bf5b6e134e9f0be5b3487b0dffec6db11e7bdc632e2c6e07ae0c2e0cfdd3f8` |

The inherited ideal pilot manifest SHA256 is
`0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811`.
The reviewer independently verified that hash and the eight selected path3 R1 /
K3 R2 result/component hashes against it; `RUN/ideal_inputs.json` records them.
This verifies those selected ideal inputs, not nonexistent noisy outputs.

## Blocking findings

1. **Measured QPY cannot pass the candidate's readback gate.**
   `save_qpy()` at candidate lines 208–220 calls the inherited
   `_qpy_semantic_signature()`, which rejects any classical bits. `execute_seed()`
   creates a measured circuit and calls this helper at line 350 before routing.
   A real path3 R1 seed11 child failed there at j=0, before any noisy sampling.
   A separate one-qubit measured circuit and the candidate's own compaction test
   reproduce `ValueError: Unsupported classical or unbound QPY readback`.
   Implement a measured/scheduled-circuit serializer validation contract that
   checks quantum operations, scalar phase, measurement qarg/carg order, delays
   and layout. Do not simply delete semantic validation.

2. **Expired setup has an uninitialized process-status path.**
   If process creation consumes the deadline before the first `wait4`,
   `supervise()` breaks at lines 493–495 without assigning `pid`, then reads it
   at line 527. An independent deterministic delayed-clock probe reproduces
   `UnboundLocalError`. The child is killed but the function fails before a
   receipt/reap, defeating the retained-failure contract. Initialize ownership
   and wait status before the loop, and ensure every exception/timeout reaps the
   child and saves a truthful receipt. The initial sandbox probe also exposed
   an uncaught `PermissionError` when `ps` is unavailable; record unavailable
   sampling explicitly and enforce a documented fallback or stop safely.

3. **Experimental evidence and completion ledger are absent.**
   The configuration selects only path3 k2 R1 and K3 k3 R2, 64 shots, five fixed
   transpiler seeds and 2048 random batches; it is not the full requested sweep.
   No candidate seed has a saved completed run. `RUN/sweep_ledger.json` retains
   all 36 ideal case/regime entries and all five missing noisy seeds per entry.
   C5 R1/R2 remain explicitly ideal-infeasible at 22>18 qubits; no domain checks
   were removed. The review's path3 seed11 smoke is a saved failure, and its
   synthetic routing probes are not substitute coloring-study results.

4. **Inherited routed `gates` includes measurements.**
   `_seed_metrics()` excludes barriers/delays but sums measurements into `gates`.
   Each independent routed fixture reports 22 versus 20 unitary gates and two
   measurements. This violates the plan's gate-count convention. Correct or
   explicitly relabel that metric before admitting tables. The routed native
   two-qubit denominator is unaffected by this particular finding.

## Bounded positive checks and limits

`tools/review_noisy_iterations.py` is an independent review probe, committed as
`7bfc23d`. Every numerical child explicitly imported the actual candidate source
through `PYTHONPATH`; the resolved module path and SHA256 are in its output.

- Independent signed-amplitude recurrence checks passed j=0,1,2 for a path on
  noncontiguous labels, K3 k3 R2, a zero-solution one-color edge, and an isolated
  three-color vertex. The emitted preparation and matched reflection restore
  clean workspace. Maximum width was 14, maximum signed vector residual
  `8.93e-15`, and maximum nonzero-workspace probability `7.00e-30`. These are
  twelve finite probes, not a general preparation or ideal-amplitude certificate.
- Ordered asymmetric quantum noise and distinct readout noise on physical
  wires [6,2], with reversed classical measurement order, produced the independently
  predicted deterministic counts before and after compaction. Physical labels,
  channel payloads and ordered qargs were checked independently.
- For seeds **11,23,37,41,53**, a three-wire phase-sensitive fixture passed full
  coherent routed-state equivalence up to one global phase, including clean
  workspace and reversed measurement-bit order. Maximum residual was `2.38e-16`.
  Independent QPY dump/load was used after preserving the candidate helper's
  failure. All five used physical [65,66,81], and each of the 17 retained FakeTorino
  channels reconstructed an identical original serialized channel after inverse
  wire relabeling. The seeds were not pooled or treated as independent shot samples.
- FakeTorino properties, configuration and serialized noise snapshots are saved.
  Active-wire extraction retains all operated/measured wires and delays on those
  wires; only otherwise-idle delay wires disappear. The stated model includes
  per-gate thermal relaxation and readout noise, excludes idle-delay relaxation,
  crosstalk and drift, and preserves ordered physical calibration qargs. The
  probe supports these finite mappings, not a completed calibrated noisy sweep.
- Wilson 95% endpoints, all-success/zero-success cases, binary-domain invalid-code
  leakage and random-batch denominators passed independent scalar checks. A random
  batch uses j+1 draws and reports any-success per batch; leakage uses total draws.
  Thus its analytical comparator is `1-(1-M/N)^(j+1)`, not single-draw M/N.
  Quantum cost/p uses routed two-qubit gates per measured proper output; random
  cost/p uses draws plus classical evaluation. These resource units cannot establish
  a speedup. Zero observed success yields null cost/p, not proof of zero true success;
  the ratio has no supplied confidence interval. Wilson intervals are pointwise,
  conditional on a fixed routed circuit, not simultaneous across the sweep.
- The candidate itself calls ESP a calibration error product. **ESP is not noisy
  success.** No candidate noisy-success/leakage count was produced or admitted.
  Its routed validation compares data marginals and final logical-workspace zero
  probability; that does not independently establish full coherent equivalence.

## Execution, resource accounting and preserved failures

Python: `/Users/mar/codex-work/logique/.venv/bin/python`.
PYTHONPATH: the absolute candidate `src` above. Cache:
`/Users/mar/codex-work/logique/.cache/epfl`. Qiskit parallelism disabled;
OpenMP/BLAS/VECLIB/NumExpr/Rayon threads all one. The prescribed private native
executable hash `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was verified; it was not invoked. No native build, sync, model launch or hardware.

| Run | Result | Boundary seconds | Sampled direct-child peak bytes | wait4 invocation high-water bytes |
| --- | --- | ---: | ---: | ---: |
| Candidate focused suite, attempt2 | 14 passed, 1 failed | 0.841 | 90,980,352 | 91,045,888 |
| Independent initial probes | 3 passed, 2 failed | 3.773 | 371,261,440 | 371,589,120 |
| Real candidate path3 seed11 child | QPY failure before routing | 3.760 | 471,646,208 | 498,221,056 |
| Focused independent follow-up | routing passed; QPY/deadline failed | 4.534 | 379,437,056 | 379,453,440 |

The measured numerical boundaries total 12.908 seconds. Per-child limits were
45/125/80 seconds in attempt2 with a 240-second cumulative guard; the follow-up
was allowed 90 seconds after observing completion, within the review's 300-second
total ceiling. Only one numerical child ran at a time. Supervisors sampled a
2 GiB direct-child limit; this is not a hard OS allocation cap or process-group
RSS guarantee. `wait4` may include reaped descendants. The candidate config's
working-set guard is at most 18 wires, eight complex vectors plus 128 MiB;
its simulator ceiling is 6 GiB. Review allocations were guarded before arrays,
used at most 14 statevector qubits and **no dense full Operators**.

An initial sandbox attempt failed in the review supervisor on unavailable `ps`;
the candidate pytest log completed with 13 passed/2 failed (one environment failure),
and is preserved. That first attempt has no boundary RSS/time receipt; pytest
reported 0.51 seconds, not an independently measured process duration. The retry
with process visibility is separately retained, not an overwrite. Initial
deadline-probe cleanup also encountered an exited-child signaling error; its
traceback is retained. The follow-up reaps before cleanup and cleanly reproduces
the candidate `UnboundLocalError`. No numerical child remains owned/running.

Commands, stdout/stderr, failed QPY artifacts, original probe source, corrected
probe, source snapshots and resource receipts remain under `RUN`. Black/Ruff
and `git diff --check` passed for the task-owned review probe. This is not a
full repository suite or a claim that failing candidate tests passed.

## Handoff

Keep the candidate unadmitted. A fresh implementation task must correct measured
QPY validation and process cleanup/receipt paths, fix the gate metric separately,
commit its own tested source, and execute a bounded five-seed pilot with hashed
circuits/calibrations/results and truthful timeout/infeasible/unexecuted statuses.
Then obtain a new exact-hash independent review. Retain old failures and the full
scope ledger. The coordinator may integrate this review/probe as a blocker record;
it must not integrate or publish the candidate as admitted noisy research.
Only the dispatcher publishes integration HEAD; this reviewer did not push.
