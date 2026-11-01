# Exact bounded dynamic RUS integration — 1 November 2026

Task `dynamic-rus-integrate-1030020413` is **COMPLETE**. Independent review
`d1a94e9c3b9def742db695408dca2ba1230a3795` **ADMITs exact bounded correctness
and saved evidence**; the broader graph-search/manuscript gate remains open.
Integration intake `0da04596b7a6c6ccbd16e2a2fed072fcace84ca5` is later than assigned base `e90adf3`;
no reset occurred. Checkpoint: `dump/1101005901-dynamic-rus-exact-integration/checkpoint.json`.

## Exact bytes and preservation

Correctness-only candidate `849bcc765dd140342d83f181469b4b8f29fa8893` was
cherry-picked without conflicts as **`78c98a164a289b52ce6251e5495848e71b4bb193`**. Only
`src/logique/benchmarks/dynamic_rus.py` and `tests/test_dynamic_rus.py` enter
that commit. Their SHA256s are respectively
`4212abaaae4e3bb031ac28baa624c1d88c6ff574aa82701894688458529d44c9` and
`5de0b20abb2fbeb2d655b93fe082536e5ab8e78618ce0386a4fb2933e7ee22e3`.
No semantic resolution/new source bytes required inferred admission.

The [verbatim independent review](dynamic_rus_independent_review_20261101.md)
has SHA256 `afad1eb1f5d776a76b7f82ac2536718f6567b023132800ac1baa9390fcb13bdb`.
Candidate evidence/checkpoint commit remains
`c655f5e905051a51316f33e87dd243cafa2239cf`; its checkpoint SHA256 is
`4b723770f363a672dac6a748c67064169eb4692fe996c2052da53aa87eab5d50`.
All **100 candidate evidence entries** and **36 independent-review entries**
match their byte lengths and SHA256s. Candidate index SHA256 is
`a8f7fc74fdf36cb42f261439bdd8d025723dbe0fe671743a929d116523a362cf`;
review index SHA256 is
`647dbda2f5d66610c771ad4cf5f9dc4b25b3bc4981b9af3c12edd55203661c95`.
Saved worker/reviewer circuits, arrays, inputs, failures and histories remain in
place. No metrics were recalculated or changed by integration. This separate
documentation commit records the admitted observations without changing metrics.

## Scientific decision and precise limits

Admitted domain: ideal uncontrolled instruments on **one two-bit vertex
register**, cap0..4, at most three serial forward/inverse invocations on that
same register, three untouched reference wires and four operator/purification
columns. Every measurement outcome, reset, retry, branch phase and capped abort
is explicit. Inverse E† occurs once before retries, including cap0. The ideal
fresh-zero retry ancilla and noiseless classical control are assumptions.
NumPy/Qiskit remain lazy; no bridge, binary, build or pin changed.

The admitted worker evidence contains20 finite-cap cases/220 terminal branches,
10 dynamic QPYs and four primitive QPYs. Independent evidence covers75 schedules/
1,375 branches and5,169 comparisons: maximum absolute residual
2.842170943040401e-14 at tolerance3e-13. This maximum mixes scalar resource sums
and matrix/state entries; it is neither an operator-norm certificate nor an
uncertainty interval. Seeds and exact input hashes are retained in provenance;
there are zero stochastic shots and no sampling confidence intervals.

For c=4, completion is1-4^-4=255/256. Expected reached attempts are
(4/3)(255/256)=1.328125. Unconditional stop costs, including aborts, are
2(1.328125)+2(255/256)=4.6484375 T forward and
2(1.328125)+2=4.65625 T inverse. At cap0 the inverse still costs2 T;
forward costs0. Non-T operations remain unpriced, not free.
The analytical unlimited14/3 limit is not executed unlimited evidence.

The saved naive controlled trial leaves purity0.8125 from a pure input when
records are discarded, because its control sectors succeed with probabilities
1 and3/4. Retain **BLOCK** on quantum control, static A/A† substitution,
executed multi-vertex graph/search semantics or advantage, runtime/T-depth,
noise/physical costs, achieved preparation break-even and full-paper claims.
Preliminary worker five-wire dense checks remain excluded under its stricter
dense4 bound. Original failed test expectations/lint/type-check receipts and
quota interruption remain preserved; no scientific failure is inferred from quota.

## Integration verification and resources

Candidate and integrated suites each passed286 tests, no skips/deselections.
Selected Black/Ruff, one-file mypy and stdlib-only import/preflight pass.
Both source import paths were asserted explicitly. RUS accounting/preparation
source/tests match between candidate and root. No new study or reviewer probe
was rerun; these are integration checks of independently admitted bytes.

| Check | Exit | Boundary seconds | Terminal wait4 high-water bytes |
| --- | ---: | ---: | ---: |
| candidate-pytest | 0 | 0.866056 | 83,099,648 |
| integrated-pytest | 0 | 0.647425 | 83,214,336 |
| black | 0 | 0.270034 | 37,568,512 |
| ruff | 0 | 0.103436 | 19,529,728 |
| mypy | 0 | 2.353211 | 209,125,376 |
| lazy-import | 0 | 0.028419 | 19,742,720 |

Budget declared before arrays:120s per child,300s cumulative,1GiB declared
process budget, one numerical child at a time, dense4/dynamic6/four columns,
cap4/three loops/85 branches. All supervised checks took
4.268580s; numerical candidate+integrated tests
used1.513481s. Process-group timeout and
bounded allocations are safeguards; terminal wait4 is not live/group monitoring
or hard memory enforcement. Original staticFT dense4 cap stays unchanged.
Existing explicit venv interpreter only; compiler/BLAS/OMP/Accelerate/Rayon/
Qiskit parallelism1. The prescribed private binary SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was checked, never invoked or rebuilt; root default stays old.

Initial cherry-pick failed exit128 on sandbox index.lock permission; scoped
automatic escalation succeeded. No approval-review rejection occurred. Command
output is retained in the task transcript and a local Git receipt; terminal
RSS/time for that initial Git failure were not independently measured. Numerical
checks have full command/exit/time/RSS receipts. Initial truncated reads were
followed by focused chunks; guessed checkpoint.json was absent and actual
terminal-checkpoint.json was read. These are inspection limits, not experiments.

README, lockfile, gitlinks, binaries, inspected evidence and review hashes match
intake. No history/archive/dependency/queue changes, push, sync, hardware,
precolored/conditional-workspace work, API/paid fallback, model/subagent or
Codex launch occurred. Dispatcher alone publishes committed integration HEAD.

Next scientific action: implement actual multi-vertex marking/reflection with
flagged abort prefixes and explicit unpriced-operation costs, then obtain an
independent graph-level review before claiming whole-search benefit. The existing
full-research successor owns remaining work. This assigned exact integration
ends here; no prerequisite polling or broader paper completion is claimed.
