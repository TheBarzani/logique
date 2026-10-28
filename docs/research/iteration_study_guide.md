# Executed ideal iteration pilot

`logique.benchmarks.iteration_study` executes actual coloring preparation,
structure phase oracle and matching diffusion circuits. It reuses the admitted
exact-count analytical ledger for the sweep extent, not as simulated evidence.
This is an ideal-only pilot; noise, routing, FT/RUS, physical resources and paper
approval remain separate work. No earlier numerical result or contract changes.

Run with the existing research environment, candidate checkout source on
`PYTHONPATH`, and one numerical process at a time:

```sh
export PYTHONPATH="$PWD/src"
export LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl
export LOGIQUE_NATIVE_EXECUTABLE=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
/Users/mar/codex-work/logique/.venv/bin/python -m logique.benchmarks.iteration_study --config configs/iteration_pilot.json
```

The structure construction invokes no native executable. The selected executable
and its hash are recorded for provenance; this study does not build anything.
The admitted executable hash is
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Do not substitute the older root build in experiments needing native synthesis.

The maintained configuration includes paths3..8 k2, K3/C5/P4 k3, an unsatisfiable
two-color triangle, the zero-vertex empty graph, and a three-color edge plus an
isolate with noncontiguous labels. Every case retains R1/R2/R3. There are no
supplied or assumed solution counts: exhaustive integer evaluation counts the
support and proper colorings, capped at 12 binary data bits. An independent
packed-word decoder cross-checks these counts before interpreting probabilities.
Positive, invalid-code and edge-violation witnesses are retained when those
classes exist. Binary witnesses are retained even for restricted R2/R3 support.

## Construction and validation

The method is the admitted sequential structure oracle, with complete checks for
R1/R2 and edge-only checks for R3. Data wires follow sorted labels and contiguous
LSB-first vertex words. Flags, shared comparator scratch and phase output start
zero. Metadata records their actual disjoint allocation. R1 uses Hadamards;
R2/R3 use maintained `coloring_preparation` on the original k. Diffusion reuses
`_reflection` and its actual emitted inverse, correcting its scalar sign to
A(2|0><0|-I)A†. For zero data wires, diffusion is explicitly the scalar identity;
the true empty predicate still supplies an oracle phase of -1 each iteration.

The harness exhaustively interprets the original oracle's exact X/CX/CCX/MCX/Z
instructions on every binary data word, checking the absolute +/-1 phase and
restoration of all non-data wires. This supplements the existing compositional
proof; it does not claim an exhaustive quantum operator for wide circuits.

The existing QPY resolver expands actual definitions (including inverse
StatePreparation and scalar phases). Components are then transpiled to U/CX
with optimization level zero and the declared seed, without routing. Every
instruction must act on at most two qubits before statevector execution: a wide
MCX is never passed to statevector evolution as a potentially dense matrix.
QPY readback must exactly preserve ordered gate signatures, numeric parameters,
control states and scalar global phase. The saved readback components are the
objects evolved. No full dense Operators are constructed by the harness.
This numerical pilot does not extend the rotation compiler's admission or prove
general wider transpiler equivalence outside the checked prepared subspace.

After preparation and after each oracle/diffusion iteration, the harness reports
valid-solution probability, unused-code leakage, total norm, and restored-workspace
probability. It compares the full clean-register signed amplitudes and all dirty
workspace amplitudes against an independent first-order rational good/bad
recurrence starting u=v=1:

```
p = M/N
u_next = (1-2p)u + 2(1-p)v
v_next = -2pu + (1-2p)v
P(j) = p*u(j)^2
```

Uniform initial amplitudes are 1/sqrt(N). The comparison fits no global scalar
and performs no column or relative-phase alignment. A deliberate opposite-sign
diffuser regression demonstrates that equal probabilities alone cannot pass.
The declared tolerance applies to signed amplitude residual, probability error,
ledger agreement, norm/restoration and R2/R3 leakage. R1 unused-code population
is expected and is reported, not artificially constrained to zero.

The random reference is **analytical independent uniform trials**, with j+1
trials for row j and a cost of one uniform support draw plus one independent
classical predicate evaluation per trial. That choice is explicit, not an
assertion of equal quantum gate cost. Exact statevector probabilities have no
binomial shot confidence interval. No noisy or sampled probability is reported.

## Limits, failures and replay

Use `run_study` or the module CLI for supervised experiments. The direct
`simulate_case` helper is intended for tiny tests and has no process timeout.
The supervisor launches serial Python children with at most 180 seconds each,
a cumulative wall budget at most 900 seconds, and BLAS/OpenMP threads one.
The actual allocated full-register width must be <=18 before preparation or
statevector arrays are constructed. This is a pre-array guard, not a guarantee
about arbitrary assembly/import allocations or aggregate OS memory enforcement.
`wait4` records each child's measured peak RSS, including killed children, with
platform-specific units converted to bytes. Seeds, Python/NumPy/Qiskit versions,
source revision, dependency gitlinks and relevant source/input hashes are saved.

A finished schedule is not necessarily successful: inspect every case status.
`infeasible`, `timeout`, `failed`, `failed_comparison` and `budget_excluded` retain
the requested scope and follow-up. Timeouts preserve logs, requests and any
partial construction. The sequential C5 k3 complete oracle allocates 22 qubits;
R1/R2 must be explicitly excluded under this pilot's cap. R3 allocates 17.
A concrete successor is to evaluate a separately admitted lower-workspace oracle
for the two complete-predicate cases, retaining complete-domain semantics and
absolute-phase/restoration tests. Alternatively obtain an explicitly larger
resource budget; do not silently remove domain checks or label ledger rows as
simulations.

Each fresh timestamped run contains config, manifest, requests, logs, per-case
results and resolved preparation/oracle/diffusion QPY. Results record exact
component signatures and file hashes. To replay a completed case, start a zero
state on the full recorded register, load these QPY components, apply preparation
to the ordered data wires, then repeat oracle and data-only diffusion j times.
The result's `replay`, mapping and row extent specify the complete construction;
no synthetic supplied probability substitutes for a circuit. Requests can be
re-executed via the internal `--child` interface with a **new** output directory,
under an external <=180-second supervisor; prefer a new configured run. Never
overwrite old outputs. Verify saved evidence hashes before independent replay.
Scientific admission requires a separate explicit review of exact file hashes.
