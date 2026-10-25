# Analytical k=3 RUS ledger: bounded coordinator admission

Coordinator `coordinate-rus-1025083656`, 25 October 2026. **ADMITTED only for
exact analytical accounting under the ideal-instrument assumptions below.**
Both predecessors completed, neither was blocked. This coordinator had no prior
completed batch/handoff. Full paper remains unfinished. No dynamic execution,
retry runtime, quantum-controlled instrument, static compiler substitution,
hardware, graph break-even or paper admission is supplied.

## Exact integration and evidence

Correctness commit `dd1aeb9a50ee3ef1d57fd279304f8013590e022d` was integrated as
`e3e6141`; only these two owned files entered that commit:

| File | SHA-256 |
| --- | --- |
| src/logique/benchmarks/rus_accounting.py | c56af0fa743ba6a58e622a7ab5614d983bf4e0eed532256b6ddc967e65fb2b44 |
| tests/test_rus_accounting.py | 40837375ff6448ca8ad6cca8ed70af3b69bd2199beae62e1a8e6f4c14fcd5225 |

Actual bytes, Git blobs, clean worker branches, checkpoint `e527a42` and review
commit `6361acc` were inspected. The independent [review](rus_ledger_review.md)
is preserved byte-for-byte, including its executable verifier and limitations.
Its source checkpoint SHA-256 is
`914595b38c963fde65cf7ca3bf3ff0e462a1ddb29d8006def6339c416ed9e89c`.
Worker saved events/result hashes match the review. Thirty-seven completed
command events corroborate tests/static checks and the corrected preliminary
Ruff E741 failure. These are analytical outputs, not observed execution costs.

Evidence: `dump/1025175909-rus-coordinator-triage/`, including `check.py`,
`commands.jsonl`, `coordinator-probes.py`, review replay, original manifest/queue
and protection identities. All 1,310 intake protected identities must match at
handoff, including user README, worker evidence, archives, prototypes, nested
histories, pins, admitted static source/tests and both native binaries.

## Mathematical and accounting contract

The retained Task 6 derivation and independent review establish the trial
operators K0=alpha U and K1=beta I, with U=(I+i sqrt(2)X)/sqrt(3),
alpha=(1-i)sqrt(3/8), beta=(1+i)/sqrt(8). Completeness and scalar probabilities
3/4 and 1/4 hold for arbitrary input and entangled references. Assumptions are
ideal gates, fresh zero ancilla, noiseless measurement, classical record and
reset/repreparation/feed-forward. None of those operations is executed here.
The two-T primitive has literature provenance in the retained review; its
coloring extension and 14/3 expectation are local derivations, not a quoted
coloring result or an optimality claim.

For |h,l> with l the low bit, E=X_h CH_(h,l) S†_h and V=E U_h.
CH uses two T/T† gates with cancelling scalar phases. All columns, rather
than only V|00>, are checked. The inverse applies E† once, followed by a fresh
ZUZ instrument because U†=ZUZ. Failure then leaves beta E† on the original
input. Repeating E† on retries is wrong. Successful forward/inverse records
have actual scalar phases alpha beta^(r-1), not conjugated sampled-path phases.
The completed data channel is the inverse; a capped abort is a different output
and cannot be counted as completed unitary execution. Quantum control needs a
separate instrument analysis.

Initialize once, then O,A†,S0,A for j iterations: L=n(1+2j) loops.
Unlimited vertex T expectation is 14L/3, variance 16L/9; add externally supplied
j(T_O+T_S0). Unlimited retries have no finite worst case. Finite cap c gives
exact exhaustion 1-(1-4^-c)^L and union bound min(1,L4^-c), concerning retry
exhaustion rather than proper-coloring success. Success-conditioned costs and
unconditional serial stop-at-first-exhaustion costs are distinct. Inverse
prefixes are charged even when their reached loop aborts. Unknown external
charges stay unknown if reached; n=0 remains symbolic, j=0 costs preparation
only. Finite upper bounds are conservative. Callers must bound exact-rational
parameter growth; the module is not a general resource-limiting API.

Only logical T/T† charges are priced. Retry ancillas are one shared or n
allocated, separate from 2n data wires and unknown O/S0 workspace. Parallel
allocation retains the serial stop schedule and supplies no depth/runtime
claim. Measurement, reset/repreparation, feed-forward, Clifford gates, runtime
and physical QEC stay unpriced. Costs do not verify O/S0 semantics, choose j,
measure advantage, or establish preparation break-even.

## Verification, failures and limits

Candidate and integrated suites each passed **100 tests**, no skips/deselections.
The exact independent review replay passed **1,304 checks**, **56 invalid-input
rejections**, and **36 exact distributions**. Largest entrywise residual was
5.551115123125783e-15 at tolerance 2e-13 without phase fitting. Coordinator
probes separately walked **288 serial schedules**, with **1,152 exact rational
checks**, and **49 unequal forward/inverse branch lengths**; largest residual
1.1155500767743927e-16. The inverse identities and scalar probabilities are the
algebraic basis of admission; green tests alone are insufficient.

Relevant Black/Ruff and one-file mypy passed. Existing Python 3.10 environment,
explicit checkout src/cache/private native paths, sequential children and
single BLAS/OpenMP threads; native never invoked. Each numerical child had a
60-second external timeout, total numerical wall below two seconds. Peak child
RSS 97,239,040 bytes, below 8 GiB; this is measured high-water evidence, not an
OS aggregate cap. Largest dense matrix/vector in replay is three qubits; new
phase probes use one-qubit matrices. No wider simulation, static compiler
suite, full suite, build/install/sync, notebook or historical replay ran.

Failures retained: ps sandbox-denied (durable dispatcher state only); absent
.codex in initial discovery; broad read output truncation, followed by focused
chunks; initial Git index.lock denial followed by scoped successful escalation.
A coordinator supervisor import accidentally repeated candidate tests/review
replay while adding probes; both passed and both invocations remain recorded.
No numerical/static failure, timeout or automatic approval rejection occurred.
Predecessor Ruff E741 and review staging/template failures remain in their
unchanged evidence. Correctness, admission documentation and future metrics
remain separate commits.

Static FT retains its exact [rotation contract](rotation_norm_admission.md) and
[isolated-vertex pilot limits](static_ft_pilot_admission.md). Original numeric
recursive targets, norm-aware accounting, measured one-qubit defect <=64 eps,
precision floor 1e-12, bounded SK/recursion, explicit restoring lowering, clean
oracle, mapping, signed S0, restored workspace, actual emitted inverse and scalar
phases remain binding. No interval certificate or ideal-amplitude guarantee.
Meaningful graph FT remains resource-blocked; this analytical admission cannot
remove that blocker or extend the static compiler's scope.

## One next bounded slice

After inspecting all 36 existing queue entries, append one symbolic preparation
break-even ledger slice, with isolated independent review and coordinator.
It compares externally supplied component costs and separately supplied j,
retains unknowns, distinguishes static counts from RUS expectations and capped
abort/renewal accounting, and asserts no achieved graph break-even. It neither
implements the already queued ideal-iteration study nor edits native, controls,
QPY, structure or static FT files. Dispatcher alone launches models and pushes
committed integration HEAD. Queue header/prior definitions stay immutable.

Full controls/post-pilot freeze, meaningful static graph FT, nine-graph/multilevel
comparisons, actual preparation break-even, iteration/noise/scaling studies,
remaining mappings/profiles/SAT, research acceptance, evidence-gated manuscript
and independent final reviews remain open. The batch checkpoint contains exact
jobs/hashes and idempotent release instructions; do not redispatch this completed
handoff. Full paper remains unfinished.
