# Sequential structure oracle: bounded admission

Coordinator task `coordinate-structure-oracle-1025034429`, 25 October 2026.
**Admitted: exact logical sequential XOR/phase construction on clean workspace.**
Full Task 5, parallel emission, lowering, comparisons and the paper remain open.
There was no prior completed coordinator batch/handoff in the dispatcher state
or server manifest. The predecessor reports complete, not blocked; its scientific
admission was pending. The QPY blocker in the separate controls scope remains
blocked and is not removed by this review.

Only the two owned files from worker correctness commit `ed6f8a3` were integrated
as correctness commit `0a56cd2`. No build or research metrics entered that commit.
Actual candidate and integrated SHA-256 identities match the checkpoint:

| File | SHA-256 |
| --- | --- |
| `src/logique/circuits/structure.py` | `ab8ab3a5fc74c408a5bda0bf036dabb68bbd2b5a7d185866f5d88bda4ee5af8c` |
| `tests/test_structure.py` | `de4114f6318b03f51c16144212e2e5513dca96296b5065461e8ffc450fba175c` |

## Contract and independent proof assessment

Data is sorted by integer vertex label, in contiguous LSB-first words, including
isolates. `complete` marks proper colorings and rejects every unused code.
`domain_free` marks edge inequalities over all binary codes. Equivalence to the
coloring predicate requires valid-code support supplied by the caller's actual
preparation. Precolors reject. One color still uses one bit; its complete domain
accepts only zero. Empty conjunctions are true, including zero vertices.
Self-loops supply a constant-false flag and avoid aliased comparator wires.

For c>=2, the comparator's temporary right word is XNOR(left,right). Its c-1
prefix-AND scratch bits compute equality. X on the target followed by CNOT from
the final equality bit toggles inequality. Neither forward compute block uses
the target, so its arbitrary initial value does not affect cleanup. Inverting
the actual AND and XNOR blocks restores all scratch and both data words. For
c=1 two CNOTs directly toggle inequality. This is an exact permutation with no
relative phases, so the clean-subspace basis proof extends to coherent data and
arbitrary entangled targets by linearity.

The domain flags XOR mutually exclusive prefixes: the highest bit differing
from k must have x=0,k=1, with higher bits equal. Their union is exactly x<k.
The prefix value `(k >> bit) ^ 1` specifies that zero differing bit and all
required higher bits. Power-of-two domains need no flags. Flag conjunction
toggles the output; inversion of the emitted compute clears flags. Phase use
requires a zero output, toggles it, applies Z, untoggles it and inverts compute.
It restores every non-data wire and applies exactly (-1)^f(x), including the
empty predicate. Initially dirty flags/scratch and relative-phase replacements
are outside this admission.

Let n=|V|c, F=|E|+D, where D=|V| for non-power-of-two complete domains and zero
otherwise. Let s=c-1 when any non-loop edge exists, zero otherwise. The allocated
width is n+F+s+1, with F retained flags, s reusable scratch and one output.
The XOR output is arbitrary; all other workspace starts zero. Phase output also
starts zero. Domain checks use no comparator scratch. Each comparator releases
its scratch before the next one. Metadata roles partition allocated wires
without double counting. Logical MCX gates have no implied lowering ancillas.

First-fit layers cover canonical edges exactly once, and each placement rejects
both endpoints already in that layer. This proves conflict freedom, not schedule
optimality. A hypothetical layer with w non-loop edges requires w(c-1) private
scratch, width n+F+w(c-1)+1. The maximum such requirement is recorded separately.
The current emitted circuit is sequential; no parallel execution/depth at the
sequential width or superiority result is admitted.

## Reproduction and independent evidence

Evidence: `dump/1025081040-structure-oracle-triage/`. The original worker
checkpoint, queue/state/server-manifest intake and protected identities are
preserved there. Source/tests, worker command records/logs and identity evidence
were inspected; admission rests on the construction above and separate probes,
not just the worker's green tests.

Candidate and integrated focused suites each passed **84 tests**, no skips or
deselections. They cover direct classical predicates, exact phase, arbitrary
XOR targets, restored flags/scratch, compute boundaries, asymmetric k=5 codes,
noncontiguous labels, isolates, empty constraints, self-loops and unsatisfiable
graphs. Primitive dense checks use 1–4 qubits; complex statevectors use <=5.
The minimal-import regression passed. Relevant Black, Ruff and one-file mypy
passed in both checkouts; diff checks passed. No full-suite/notebook/build claim.

The independently written `independent.py` imports no worker tests or maintained
verification interpreter. It compiles emitted X/CX/CCX/MCX/Z into scalar integer
bitmask actions and uses direct integer decoding, independent edge inequalities
and `ColoringProblem.is_valid`. Seed 1025081040 gives **222 graph/policy cases**,
**27,756 full XOR/phase checks**, and **2,728 comparator checks** for c=1..5.
It also checks compute boundaries, disjoint role partitions, width formulas,
layer coverage and conflicts. Palettes include 1,2,3,4,5,7,8,9,16,17; random
graphs have <=8 data bits, comparator circuits <=15 wires. There are no dense
operators or statevectors in this extra probe. Both candidate and integrated
copies passed with asserted import resolution. These finite probes supplement
the compositional proof; they do not establish research performance claims.

All numerical/static commands ran sequentially with 180-second timeouts, existing
root research Python, explicit checkout `src` PYTHONPATH, root EPFL cache,
BLAS/OpenMP threads=1 and the explicit manifest private common-preprocessing
binary. No native build or invocation was needed. Recorded child RSS upper
bound is **93,077,504 bytes** (getrusage high-water across preceding children of
each runner); this is measured evidence, not an OS-enforced aggregate guarantee.
The private binary hash remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the old root binary remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.

## Failures, preservation and next action

No numerical or static check failed. `ps` was sandbox-denied; process visibility
is not claimed. Durable queue/state identifies this coordinator as the sole
running dispatcher job. Initial cherry-pick and worktree creation were denied
Git metadata writes by the sandbox; narrowly scoped automatic escalations then
succeeded. No automatic approval rejection occurred. A read of the nonexistent
`coloring/problem.py` was corrected to maintained `coloring/model.py`.

All 165 protected identities match intake, including README edits, archived
outputs, nested histories, prototypes, pins, rotations and both executables.
External index/gitlinks are unchanged. No agents, model/Codex launches,
API/paid fallback, hardware, pushes, publishing, sync or installation occurred.

The whole 22-job queue was inspected. Exactly two unique jobs were appended by
atomic replacement, preserving header and prior definitions: isolated
`structure-parallel-1025081040` (structure profile, 1800 seconds, four attempts)
and `coordinate-structure-parallel-1025081040` (coordinator, 1200 seconds, four
attempts, finished-dependency triage). The worker starts at `0a56cd2`, owns only
structure source/tests/checkpoint, and must prove emitted parallel dependencies,
private scratch lifetime and exact cleanup. Dispatcher alone launches it.
Existing native, controls/QPY and static FT scopes retain their owners.

This bounded admission/handoff is complete. Do not repeatedly dispatch it.
Structure integration into saved R1/R2/R3 comparisons still needs admitted QPY,
explicit common restoring MCX/workspace policies and independent evidence.
Rotation admission remains exactly hash-bound to `rotation_norm_admission.md`,
including caller semantics, limits and explicit failure reporting; this work
grants no interval certificate, ideal amplitude guarantee, RUS or paper approval.
