# Stage controls and saved-QPY semantic review

Bounded coordinator: `coordinate-stage-controls-1025034429` (25 October 2026).
Worker implementation: complete. **Integration admission: BLOCKED.**
Full controls, studies and the paper remain unfinished.

## Bytes, provenance and independent checks

Worker HEAD is `3ef846f`, implementation `71ed6a4`; its worktree is clean.
Actual SHA-256 identities match its checkpoint:

- `src/logique/benchmarks/coloring_study.py`: `37a04d3feb81ba3a7b00de19136ae78ce337d61230d471af057ab466a860123d`.
- `tests/test_coloring_study.py`: `8bda782c9e9a0ca50c4ccde024ea8a8919d5dc7169b05e592322a52b0406f67d`.

Only those two files are implementation candidates. Neither is integrated.
Additive stage/role metadata truthfully distinguishes overlapping durations,
backend combined time, unavailable split optimization/mapping/memory,
reserved width and unknown live workspace. Native residual workspace is not
classified as AND-only; unsupported controls stay rejected. This does not
establish the semantics of serialized artifacts.

Coordinator evidence: `dump/1025074732-stage-controls-triage/`. Intake and
queue/state/manifest snapshots verify this coordinator had not completed an
earlier handoff, also checked after an interrupted turn. Durable dispatcher
state lists this as the sole running job. `ps` was sandbox-denied; complete OS
process visibility is unavailable.

Independent rerun: **79 passed, 31 deliberately deselected, no skips**;
relevant Black/Ruff pass. Deselections are the worker's existing wider dense
search tests. Direct operation counts and dependency depths reproduce all
**240 saved QPY rows across 24 complete cases**. Recursive independent network
checks cover 24 serialized source/mapped networks. Another 18 tiny cases check
native/baseline independent edge/domain predicates, noncontiguous labels,
constant and unsatisfiable predicates and restoration, without dense simulation.

## Concrete serialization blocker

Installed Qiskit 2.1.1 QPY readback turns an inverse `StatePreparation` into a
forward preparation. A minimal two-qubit example is:

```python
q = QuantumCircuit(2)
q.append(StatePreparation([1 / sqrt(3)] * 3 + [0]).inverse(), [0, 1])
# qpy.dump(q, stream); loaded = qpy.load(stream)[0]
```

Original operation: `state_preparation_dg`, `_inverse=True`. Readback:
`state_preparation`, `_inverse=False`. Phase-sensitive spectral distance from
original to readback: **1.9986497753173806**. Readback to forward preparation:
**0.0**. Exact artifacts: `minimal_qpy_reproducer.py`,
`minimal-qpy-reproducer.json`, `inverse-preparation.qpy` in the coordinator run.
This finding concerns installed serialization, not the separately admitted
static rotation compiler; no dependency was modified.

Original/saved preparation and diffusion comparisons, all at most four qubits,
find **16 failures among 48 operators**, all R2/R3 logical diffusion artifacts.
Maximum distance: **1.93829197958024**. Every success and failure is retained in
`qpy-semantics.json`. Wider search was not densely simulated; its saved inverse
composition is not admitted by reproduced counts.

A pre-integration run on the same tiny inputs has identical width, total gates
and depth in all 240 rows. In-memory and saved-QPY gate-type maps disagree in
24 logical diffusion/search rows because inverse names become forward names.
Trace such representation/metric changes separately from correctness. The
failure predates the candidate and is exposed by independent review. Earlier
runs, including the pilot, are preserved; affected saved preparation/search
paths need semantic review before admission as paper evidence. Count
reproduction alone does not establish their circuit semantics.

Retained failing checks: `legacy-compatibility.log` (full metric-map comparison)
and `qpy-semantics.log` (first operator mismatch). The subsequent all-case
check records failures explicitly; successful enumeration is not a semantic
pass. The worker's original clock-mocking failure also remains in its evidence.
An initial documentation patch failed context matching and changed no files.

## Bounds, preservation and bounded handoff

Sequential existing research-interpreter commands used explicit checkout
`PYTHONPATH`, one BLAS/OpenMP thread, explicit cache and private common-
preprocessing native executable. Its SHA-256 is
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
The root binary remains the old build. Maximum recorded numerical child RSS:
178,913,280 bytes. Operators <=4 qubits; no statevectors, builds, syncs or
installs. Numerical commands had 180-second timeouts. Small sequential fixtures
and measured per-process RSS support the 8 GiB policy; no OS aggregate-memory
enforcement is claimed.

Handoff verifies 175 protected intake identities and five dependency gitlinks,
including README edits, native sources/root binary, rotations/admission,
prototype backups, manuscript archives, nested histories and lockfile. Worktree
creation initially failed on a sandbox-denied Git ref lock, then succeeded with
a narrowly scoped escalation. No agents, model subprocesses, API/paid fallback,
hardware, pushes or publishing ran.

Next bounded work is QPY semantic correction, independent review, and
coordinator triage: `qpy-correction-1025074732`, `qpy-review-1025074732`,
`coordinate-qpy-1025074732`. Separate worker/review `codex/coloring-` worktrees
start at `3ef846f`. Worker owns the two candidate files and its checkpoint;
reviewer owns its review. Review/coordinator handle blocked predecessors.
Queue header and 19 prior definitions remain immutable. Dispatcher alone
launches models. Exact jobs, prompt hashes, tests, failures and remaining scope
are in this run's `batch.json` and `queue-validation.json`.

Correction must preserve actual forward/inverse/nested preparation semantics,
scalar phase, signed diffusion, clean oracle/workspace and mapping across QPY.
Fail unsupported cases explicitly, retain partial evidence and omit cost rows.
Require bounded operator/statevector and compositional coverage plus exact-byte
independent admission before integration. Keep correctness, build and changed
metrics separate; do not patch installed dependencies or overwrite old runs.
No arbitrary opaque-operation guarantee follows from a local repair.

After admission, opt-in restoring MCX decomposition with explicit fresh scratch
and no cross-role borrowing is the next controls slice. All decomposition,
workspace, routing, precision/limits, instrumentation, post-pilot freeze,
nine-graph/multilevel comparisons, separate RUS/preparation break-even,
iteration/noise, scaling, evidence-gated manuscript and independent final
reviews remain in scope. Existing native, structure and static-FT jobs keep
ownership. Exact-byte rotation admission/caller obligations are unchanged: no
interval certificate, ideal-amplitude guarantee, RUS or paper approval.
This bounded triage/handoff is complete once queue and manifest are saved;
do not redispatch it on resumption. The full paper remains unfinished.
