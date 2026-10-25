# Rotation norm critical review

**Bounded task outcome: COMPLETE. Scientific admission: ADMITTED for static FT
comparison experiments under the declared numerical contract and limits below.**
This decision applies to THESE exact corrected bytes, not the old repair or an
integration prototype. No concrete remaining blocker was found in this bounded
review. This is not paper completion, publication approval, a certified error
theorem for floating-point arithmetic, or authorization to launch experiments.

## Checkpoint and identity

Date: 2026-10-25. Review worktree:
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/rotation-norm-review`.
Branch: `codex/coloring-rotation-norm-review-1025024643`.
Source worktree (read-only):
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/rotation-norm`.
Source branch: `codex/coloring-rotation-norm-1025024643`.
Both HEADs: `b422c759735437a45b42fcf81ce5e226ac594bd3`.

Git was inspected first. The review worktree was clean. The source worktree
contained only its three untracked deliverables: `ROTATION_NORM_CHECKPOINT.md`,
`src/logique/benchmarks/rotations.py`, and `tests/test_rotations.py`. The upstream
checkpoint explicitly declares its bounded implementation complete, with these
candidate hashes. The files remain untracked; HEAD alone does not identify them.

Read the assigned AGENTS.md, CLAUDE.md, full revision plan, implementation audit,
source checkpoint and source `docs/research/task6_rotation_rereview.md`.
Inspected the actual corrected Python files, supporting lowering/cleanup and
ordinary coloring preparation code, and CURRENT manuscript assembly text.
Only this review file was written. No staging, commits, integration, dependency
changes, environment sync, archive changes, README changes or external launches.

Both Python files were hashed before substantive review and after all numerical
checks. The exact SHA-256 values were identical before and after:

| Source-relative file | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| `src/logique/benchmarks/rotations.py` | `5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595` | `5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595` |
| `tests/test_rotations.py` | `88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77` | `88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77` |

Context SHA-256s:

| File | SHA-256 |
| --- | --- |
| `src/logique/benchmarks/costs.py` | `42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8` |
| `docs/manuscript/conference.tex` | `4cfeeb3be527540a902bd5f103b566e581ddffbbd5a57707274b1242236f1b76` |
| `docs/research/task6_rotation_rereview.md` | `1180ddc766800136456f663c49bbf8d9ab1c76566448abac47aab128c6a5bb2a` |
| `uv.lock` | `8f3f048c23341b811dd311d1b6e4cd78e5c17de17d0223e2fd3730408c357b5c` |

Explicit PYTHONPATH and runtime assertions confirm `rotations.__file__` and
`costs.__file__` resolve to the source worktree's `src/logique/benchmarks/`, not
this review checkout or an integration copy. Environment: Python 3.10.22,
Qiskit 2.1.1, NumPy 2.2.6, pytest 8.4.2. One numerical process at a time;
dense operators <=4 qubits. The sole five-qubit simulation is the retained
cleanup statevector. No build was needed.

**Next action:** the ordinary dispatcher may integrate the hash-matching
correctness files separately from bridge/build and metric changes, preserve
this decision and provenance, and schedule bounded static FT comparisons that
meet the caller obligations below. Re-review changed implementation bytes or a
broader target contract. Other revision tasks and the paper evidence gate
remain outstanding; this bounded task has no unfinished checks.

## Contract and independent mathematical assessment

The new matrix admission checks finite one-qubit matrices using measured
`d = ||M†M-I||_2 <= 64*eps = 1.4210854715202004e-14` (source lines 285–312).
This is much narrower than Qiskit's default matrix admission. It is enforced
recursively and for unused j=0 components. No normalization or polar projection
changes the target: original stored matrix entries remain the reference.

The original counterexample `A=(1+1e-6)I`, `O=S0=Z`, j=2 has unchanged target
distance `5.000009999589494e-6` from identity. It now rejects with matrix-defect
ValueError at budgets `1e-3` and `5.000005e-6`, also at j=0 and j=1. This is an
honest admission restriction; it does not claim to approximate that matrix
within either budget. Contractions and complex anisotropic deviations reject
under the same rule, including in nested and unused O/S0 definitions.

For admitted matrices, `nextafter(sqrt(1+d+64*eps), +infinity)` supplies an
engineering norm bound. Bounds >=1 propagate through recursive products.
The component lowering bound multiplies the local error sum by the source
norm product; already bounded child errors may be scaled again, conservatively.
Subsequent rotation replacement acts on the lowered algebraic unitary circuit,
so its error can be added without multiplying it by the original source norm.

For a product of original factors X and emitted unitary factors V, telescoping
each replacement bounds its term by the local error times the product of
remaining original norms. Taking every norm bound >=1 permits the same full
product N for every term. Also `||A†-V†||=||A-V||`, including nonunitary numeric
A. Thus the declared search bound is conservative:

`E <= N*((1+2j)*e_A + j*e_O + j*e_S0 + e_assembly)`,
`N >= n_A**(1+2j)*n_O**j*n_S0**j`.

This is a valid norm-aware extension of the unitary argument, subject to the
explicit numerical qualifications. Divide the requested budget by N, round
down, subtract unscaled preprocessing, then distribute residual precision by
weighted rotation occurrences. Both preprocessing and final error metadata
include N. A final bound check rejects overspend. Pure algebraic-unitary inputs
retain N=1. No fixed allowance was inflated to conceal the original failure.

The boundary sweep used scalar, dense complex and complex anisotropic matrices
at deltas `{-1e-6,-1e-14,-8e-15,-7e-15,-6e-15,0,6e-15,7e-15,8e-15,1e-14,1e-6}`,
with nesting depths 0 and 3: 38 rejected fixtures and 28 admitted fixtures,
the latter yielding 84 original-target searches at j=0,2,7. Largest measured
search error: `2.0985344453392726e-13`, within its bound. Rejected fixtures
were checked in all three roles at j=0,2. Boundary classification follows the
measured defect, not an idealized delta threshold.

Additional repeated-factor probes used 64 matrices per preparation, two nested
wrappers, both signs of delta=6e-15 and j=0,2,25. At j=25 the expansion error
was `1.9466421780229347e-11`, below bound `6.812683750786416e-11`; the norm factor
was `1.0000000000442328`. All six probes accepted budget 1e-8 and rejected
budget 1e-12. Original matrices and numeric adjoints are multiplied directly;
no reference path relies on Qiskit's inverse of a nonunitary gate.

## Disposition of all original 37 probes

No case was silently dropped or treated as an expected failure. The embedded
runner executes each parameter combination, retaining 32 cases unchanged,
adapting only accounting assertions in 3 cases, and replacing 2 obsolete
blocker-presence expectations with explicit fix checks. The code records every
transformation. The source path is changed to the actual corrected worktree.

| Original cases | Count | Current disposition |
| --- | ---: | --- |
| Near-pi CCRx, all control states and both perturbation signs | 16 | Tight-budget rejection; loose-budget phase-sensitive error bounded |
| Near-pi whole search j=0,1,2 | 3 | Original targets bounded; preprocessing charged |
| Near-Clifford matrix and recursive custom definitions | 1 | Original matrix discrepancy charged; phases retained |
| Spoofed/modified standard gates, opaque/reset, nested MCX, wide matrix | 6 | Reject; unused nested MCX rejects at j=0 |
| Large positive/negative angles | 4 | Explicit range rejection |
| Precision floor and phase-sensitive norm | 1 | Subfloor rejects; injected phase error remains visible |
| Weighted preprocessing, actual inverse, mapping [3,1] | 3 | Pass with N-aware metadata assertions; original circuits/targets/count checks retained |
| Monomial cleanup and actual expanded inverse | 1 | Near-pi impostors reject; five-qubit cleanup passes |
| Manuscript blocker presence | 1 | Replaced by CURRENT-text correction assertions and matrix/j=0 checks; old blocker closed |
| Nonunitary budget violation | 1 | Replaced by original numeric target plus explicit rejection at both budgets; old blocker closed |
| **Total** | **37** | **All passed** |

Weighted probes independently verify `(1+2j,j,j)`, exact emitted assembly,
one synthesis per source residual rotation, actual inverse reuse, untouched
auxiliary wire and `T_A+j*(2T_A+T_O+T_S0)`. Their measured errors and bounds:

| j | Error | Bound | Emitted T count |
| ---: | ---: | ---: | ---: |
| 0 | 0.007768017338085722 | 0.00776801735421466 | 633 |
| 1 | 0.00019472675804861365 | 0.0005841804967593973 | 8535 |
| 2 | 0.0001947267580899635 | 0.0009736341626553201 | 14225 |

T counts differ between searches because allocated precision changes. The
identity is for concatenated gate counts; it is not a T-depth identity.
Additional complex residual-rotation probes independently reconstruct N-scaled
preprocessing and adjusted allocation and observe three synthesis calls at
each j=0,1,2, rather than resynthesis for inverse occurrences.

The cleanup statevector has data error `4.684427951246116e-16` and scratch
amplitude norm `2.3891998240481017e-16`. This supports monomial compute-Z-actual
inverse with fresh zero scratch, not arbitrary throwaway interference/diffusion.
The deliberate scalar-phase shift produces error `0.10015282146685173`.

Ordinary `coloring_preparation` with three colors and vertex label 7 produces
the actual StatePreparation gate. Complete searches at j=0,1,2 with mapping
[3,1] pass against original recursive definitions: errors
`0.015060878816384233`, `0.004672185473545391`, `0.006170598950291622`, below
bounds `0.01506087881995237`, `0.007211701538499893`, `0.012019502564186086`.
Measured invalid-code preparation leakage is respectively
`7.703719777548943e-34`, 0, 0. These tiny illustrative values are not a general
leakage result. No precolored case or coloring study was run.

## Current manuscript and limits of admission

The inspected manuscript hash differs from the older repair prose hash
`fb72f485ac771872e3d0d1d45e0f52f44d50107a8c965777408f45c7efc2da28`.
Its last manuscript commit is `eef059dca2211cef92331e1951c2e5f91c17657a`.
Current lines 381 and 512–521 explicitly specify no prepared marked amplitude
at p=0, floor/ceiling and fewer-iteration ties, full-data A,
`S0=-X^n MCZ X^n`, restored workspace, and initialization once with only oracle
and diffusion repeated. The two-qubit bare-MCZ discrepancy remains 2.0, but
the current text no longer prescribes that incorrect construction. The old
manuscript blocker must not be carried forward. This was a focused contract
inspection, not a review of all manuscript claims, figures or historical metrics.

Admission limits and caller obligations remain explicit:

- Errors and admission decisions are numerical, not interval-certified.
  The 64*eps allowance is an engineering margin for local products, SVDs and
  scalar assembly. Measured threshold decisions have floating-point uncertainty.
  Algebraic standard leaves are not a guarantee for arbitrary-length floating
  simulation, nor is this bounded review exhaustive over all inputs.
- Matrix support is one qubit and roundoff-sized deviations only. Recursive
  definitions have depth limit 32; public angles lie in +/-2*pi. Requested and
  allocated precision have floor 1e-12. Bounded Solovay–Kitaev may fail above
  that floor and can emit long circuits; failure must be recorded, not replaced
  by an analytic cost estimate. This is not Ross–Selinger optimal synthesis.
- Composite/StatePreparation targets mean resolved definitions, not a certified
  ideal amplitude vector. Original admitted matrix entries remain the numerical
  targets; accepted nonunitarity is numerical storage error, not a physical gate.
- The caller must establish clean phase-oracle semantics, data mapping, correct
  S0 sign/conjugation, and restoration of workspace. This compiler validates
  syntax/admission, not these semantic contracts. The deliberate generic O/S0
  matrix probes test norm accounting and are not physical search benchmarks.
- Preserve scalar phases, including inverses and subsequent control. Use the
  actual emitted inverse. Explicitly lower MCX with the chosen restoring policy
  before this API. Count complete emitted circuits and compute T-depth from their
  dependencies. Keep static unitary comparisons separate from RUS,
  measurement-assisted uncomputation and dynamic constructions.
- Report invalid-code leakage and proper-coloring success separately. For a
  truly unitary ideal reference with zero invalid-code amplitude, a valid state
  norm error E gives leakage <=E^2; success-event deviations are <=2E. Applying
  these statements to the ideal coloring problem requires accounting for any
  gap from recursive numeric targets to the intended ideal preparation/oracle.
- No physical QEC, hardware, API/paid fallback, agents, model subprocesses,
  publication approval or blanket scientific approval for the full revision.

## Exact validation and reproducibility

Supplied tests: **187 passed in 17.22s**, no skips. Independent in-memory
parameterized replay: **37 passed in 4.480s**. New independent cases:
**79 passed in 6.658s** (66 boundary fixtures, 6 repeated-factor cases,
3 complex residual searches, 3 ordinary compiler preparations, 1 depth/nonfinite
admission case). No failing preliminary run or deselection was hidden. The
independent checks use pytest assertions/raises and an explicit parameter runner,
not pytest collection; all code is preserved below. No temporary files or new
dump artifacts were needed; this is the sole durable review output.

Run the supplied tests from the SOURCE worktree, using exactly:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /Users/mar/codex-work/logique/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rotations.py
```

Run the independent checks from the REVIEW worktree, using exactly:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/rotation-norm/src LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /Users/mar/codex-work/logique/.venv/bin/python - <<'PY'
from pathlib import Path
text = Path('CRITICAL_REVIEW.md').read_text()
code = text.split('```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, 'CRITICAL_REVIEW.md', 'exec'))
PY
```

SHA-256 of the exact extracted Python block (UTF-8, excluding fence delimiters
and their adjacent newlines):
`6327b4a46e50dfe049fbea3756b55f421698b5f4c354578b7aabf9e4eb5ceb98`.
The source historical review is hash-checked before extracting its original
37-case suite. Review did not independently rerun formatting, type checking,
the full repository suite or native builds; those are outside this read-only
bounded numerical/compiler review. Upstream formatting results are recorded in
its checkpoint, not counted as independent results here.

## Executable independent review

```python
import ast
import hashlib
import itertools
import platform
import time
import traceback
from pathlib import Path

ROOT = Path('/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/rotation-norm')
identities = {
    'src/logique/benchmarks/rotations.py': '5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595',
    'tests/test_rotations.py': '88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77',
    'docs/research/task6_rotation_rereview.md': '1180ddc766800136456f663c49bbf8d9ab1c76566448abac47aab128c6a5bb2a',
    'docs/manuscript/conference.tex': '4cfeeb3be527540a902bd5f103b566e581ddffbbd5a57707274b1242236f1b76',
}
def check_hashes():
    for path, expected in identities.items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert actual == expected, (path, actual)
        print('SHA256', path, actual)
check_hashes()

# Replay the original 37 cases. Retain all circuits and independent targets.
# Change only the source root, three norm-aware accounting assertions, and
# replace the two deliberately blocker-confirming functions below.
old = (ROOT / 'docs/research/task6_rotation_rereview.md').read_text()
old = old.split('```python\n', 1)[1].split('\n```', 1)[0]
replacements = {
    'math.isclose(preprocessing, m["preprocessing_error_bound"]':
        'math.isclose(preprocessing, m["unscaled_preprocessing_error_bound"]',
    '(budget-preprocessing)*(1-1e-12)/occurrences':
        '(math.nextafter(budget/m["source_norm_product_bound"], 0.0)-preprocessing)*(1-1e-12)/occurrences',
    'math.isclose(bound, m["error_bound"]':
        'math.isclose(bound*m["source_norm_product_bound"], m["error_bound"]',
}
for before, after in replacements.items():
    assert old.count(before) == 1
    old = old.replace(before, after)
tree = ast.parse(old)
tree.body = [node for node in tree.body if not (
    isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ROOT' for t in node.targets)
)]
exec(compile(tree, '<original-review-with-explicit-accounting-updates>', 'exec'), globals())

assert Path(r.__file__).resolve() == ROOT / 'src/logique/benchmarks/rotations.py'
import logique.benchmarks.costs as costs
assert Path(costs.__file__).resolve() == ROOT / 'src/logique/benchmarks/costs.py'
print('IMPORT', r.__file__, costs.__file__)
print('VERSIONS', platform.python_version(), qiskit.__version__, np.__version__, pytest.__version__)

def test_manuscript_previous_blocker_still_present():
    # Replacement: require the present fix, not the obsolete blocker.
    text = (ROOT / 'docs/manuscript/conference.tex').read_text()
    for phrase in [
        r'S_0=2|0^n\rangle\langle0^n|-I=-X^{\otimes n}\,\mathrm{MCZ}\,X^{\otimes n}',
        'Apply initialization $A$ once, then repeat only the oracle and diffusion',
        'at $j=0$ the circuit consists only of $A$',
        'denotes the full data preparation',
        'the preparation has no marked amplitude',
        'floor and ceiling candidates',
        'breaking ties toward fewer iterations',
    ]:
        assert phrase in text, phrase
    assert 'This sequence is repeated $j$ times' not in text
    s = zero_reflection(2)
    bare = QuantumCircuit(2); bare.cz(0, 1)
    assert distance(s, bare) > 1.99
    a = QuantumCircuit(1); a.h(0)
    got = r.compile_search(a, QuantumCircuit(1), zero_reflection(1), data_qubits=[0], iterations=0)
    assert got.circuit == a
    assert distance(a, QuantumCircuit(1)) > 1.99
    print('CURRENT_MANUSCRIPT_FIX_CONFIRMED', distance(s, bare))

def test_reproducer_near_unitary_matrix_understates_whole_search_error():
    # Replacement: original numeric target is unchanged; rejection is expected.
    a = QuantumCircuit(1); a.unitary((1+1e-6)*np.eye(2), [0])
    o = QuantumCircuit(1); o.z(0)
    s = zero_reflection(1)
    analytic = (1+1e-6)**5 - 1
    err = float(np.linalg.norm(np.eye(2)-target(a,o,s,[0],2), 2))
    assert abs(err-analytic) < 2e-15
    assert err > 5.000005e-6
    for budget in [1e-3, 5.000005e-6]:
        for j in [0, 1, 2]:
            with pytest.raises(ValueError, match='matrix unitarity defect'):
                r.compile_search(a,o,s,data_qubits=[0],iterations=j,error_budget=budget)
    print('ORIGINAL_COUNTEREXAMPLE_REJECTED', err, analytic)

original_names = [name for name in globals() if name.startswith('test_')]

def wrap(q, depth):
    for _ in range(depth):
        outer = QuantumCircuit(q.num_qubits, global_phase=0.21)
        outer.append(q.to_gate(), range(q.num_qubits))
        q = outer
    return q

observations = []

@pytest.mark.parametrize('delta', [-1e-6, -1e-14, -8e-15, -7e-15, -6e-15, 0.0, 6e-15, 7e-15, 8e-15, 1e-14, 1e-6])
@pytest.mark.parametrize('kind', ['scalar', 'complex_axes', 'dense'])
@pytest.mark.parametrize('depth', [0, 3])
def test_independent_matrix_boundary(delta, kind, depth):
    if kind == 'scalar':
        m = (1+delta)*np.eye(2)
    elif kind == 'complex_axes':
        m = np.diag([1+delta,1-delta]) @ np.array([[0,1j],[1j,0]])
    else:
        m = (1+delta)*np.array([[1,1j],[1j,1]])/math.sqrt(2)
    defect = float(np.linalg.norm(m.conj().T@m-np.eye(2),2))
    q = QuantumCircuit(1, global_phase=0.37); q.unitary(m, [0])
    q = wrap(q, depth)
    if defect > 64*np.finfo(float).eps:
        with pytest.raises(ValueError, match='matrix unitarity defect'):
            r.synthesize_component(q, error_budget=1e-8)
        # Reject bad matrices in every role, including unused O and S0.
        for position in range(3):
            parts = [QuantumCircuit(1), QuantumCircuit(1), zero_reflection(1)]
            parts[position] = q
            for j in [0, 2]:
                with pytest.raises(ValueError, match='matrix unitarity defect'):
                    r.compile_search(*parts, data_qubits=[0], iterations=j, error_budget=1e-8)
        observations.append(('rejected', kind, delta, depth))
        return
    local = r.synthesize_component(q, error_budget=1e-8)
    assert local.metadata['source_norm_bound'] >= max(1, np.linalg.norm(matrix(q),2))
    assert distance(local.circuit,q) <= local.metadata['error_bound'] <= 1e-8
    # All roles have admitted nonunitarity; use original matrices and adjoints.
    for j in [0, 2, 7]:
        out = r.compile_search(q,q,q,data_qubits=[0],iterations=j,error_budget=1e-8)
        err = float(np.linalg.norm(matrix(out.circuit)-target(q,q,q,[0],j),2))
        md = out.metadata
        assert err <= md['error_bound'] <= 1e-8
        assert md['norm_adjusted_error_budget'] <= 1e-8/md['source_norm_product_bound']
        assert md['error_bound'] >= md['source_norm_product_bound']*md['unscaled_error_bound']
        assert out.preparation_inverse == out.preparation.circuit.inverse()
        observations.append(('admitted', kind, delta, depth, j, err, md['error_bound']))

@pytest.mark.parametrize('delta', [-6e-15, 6e-15])
@pytest.mark.parametrize('j', [0, 2, 25])
def test_independent_many_matrix_factors(delta,j):
    m = (1+delta)*np.eye(2)
    a = QuantumCircuit(1)
    for _ in range(64):
        a.unitary(m,[0])
    a = wrap(a, 2)
    o = QuantumCircuit(1); o.z(0)
    s = zero_reflection(1)
    out = r.compile_search(a,o,s,data_qubits=[0],iterations=j,error_budget=1e-8)
    err = float(np.linalg.norm(matrix(out.circuit)-target(a,o,s,[0],j),2))
    assert err <= out.metadata['error_bound'] <= 1e-8
    measured_norm = max(1, np.linalg.norm(matrix(a),2))**(1+2*j)
    assert out.metadata['source_norm_product_bound'] >= measured_norm
    with pytest.raises(r.PrecisionNotReachedError):
        r.compile_search(a,o,s,data_qubits=[0],iterations=j,error_budget=1e-12)
    print('MANY_MATRIX_FACTORS', delta, j, err, out.metadata['error_bound'], out.metadata['source_norm_product_bound'])

@pytest.mark.parametrize('j',[0,1,2])
def test_independent_complex_residual_budget(j):
    body = QuantumCircuit(1,global_phase=0.19); body.rx(0.731,0); body.rz(-1.123,0)
    m = (1+3e-15)*matrix(body)
    a = QuantumCircuit(2,global_phase=0.27)
    a.unitary(m,[0]); a.cx(0,1); a.rz(0.731,1)
    a = wrap(a,2)
    o = QuantumCircuit(4); o.z(3)
    s = zero_reflection(2)
    mapping=[3,1]; budget=0.02
    with patch.object(r,'approximate_rz',wraps=r.approximate_rz) as calls:
        out = r.compile_search(a,o,s,data_qubits=mapping,iterations=j,error_budget=budget)
    md=out.metadata
    parts=[out.preparation,out.oracle,out.zero_reflection]; weights=[1+2*j,j,j]
    assert calls.call_count == sum(p.metadata['rotation_count'] for p,w in zip(parts,weights) if w)
    pre=md['assembly_error_bound']+sum(w*(p.metadata['lowering_error_bound']+p.metadata['assembly_error_bound']) for p,w in zip(parts,weights))
    n=md['source_norm_product_bound']
    assert n>1
    assert math.isclose(md['preprocessing_error_bound'],n*pre,rel_tol=1e-14,abs_tol=0)
    expected=(math.nextafter(budget/n,0)-pre)*(1-1e-12)/md['rotation_occurrences']
    assert math.isclose(md['per_rotation_precision'],expected,rel_tol=1e-14,abs_tol=0)
    err=float(np.linalg.norm(matrix(out.circuit)-target(a,o,s,mapping,j),2))
    assert err <= md['error_bound'] <= budget
    print('COMPLEX_RESIDUAL',j,err,md['error_bound'],n,calls.call_count)

@pytest.mark.parametrize('j',[0,1,2])
def test_independent_ordinary_compiler_statepreparation(j):
    from logique.circuits.grover import coloring_preparation
    from logique.coloring import ColoringEncoding, ColoringProblem
    enc=ColoringEncoding(ColoringProblem(vertices=[7],edges=[],colors=3))
    a=coloring_preparation(enc)
    assert a.num_qubits==2
    assert any(item.operation.name=='state_preparation' for item in a.data)
    o=QuantumCircuit(4); o.z(3)
    s=zero_reflection(2); mapping=[3,1]
    out=r.compile_search(a,o,s,data_qubits=mapping,iterations=j,error_budget=0.02)
    err=float(np.linalg.norm(matrix(out.circuit)-target(a,o,s,mapping,j),2))
    assert err <= out.metadata['error_bound'] <= 0.02
    # Ideal preparation has no invalid-code amplitude; record approximation
    # leakage separately, without conflating it with proper-coloring success.
    prep_col=matrix(out.preparation.circuit)[:,0]
    leak=float(abs(prep_col[3])**2)
    assert abs(matrix(a)[3,0]) < 1e-14
    assert leak <= out.preparation.metadata['error_bound']**2
    print('STATEPREPARATION',j,err,out.metadata['error_bound'],leak)

def test_independent_depth_and_nonfinite_matrix():
    q=QuantumCircuit(1); q.h(0)
    with pytest.raises(ValueError,match='depth limit'):
        r.synthesize_component(wrap(q,34))
    from qiskit.circuit.library import UnitaryGate
    for value in [np.nan,np.inf]:
        q=QuantumCircuit(1)
        q.append(UnitaryGate(np.diag([value,1]),check_input=False),[0])
        with pytest.raises(ValueError,match='finite one-qubit'):
            r.synthesize_component(q)

def run_cases(names):
    passed=0
    start=time.monotonic()
    for name in names:
        fn=globals()[name]
        cases=[{}]
        for mark in getattr(fn,'pytestmark',[]):
            assert mark.name=='parametrize'
            keys=[s.strip() for s in mark.args[0].split(',')]
            cases=[dict(case,**dict(zip(keys,(v,) if len(keys)==1 else v))) for case in cases for v in mark.args[1]]
        for case in cases:
            try:
                fn(**case)
            except BaseException:
                print('FAILED',name,case)
                traceback.print_exc()
                raise
            passed+=1
    print('CASES_PASSED',passed,'SECONDS',round(time.monotonic()-start,3))
    return passed

assert run_cases(original_names)==37
new_names=[name for name in globals() if name.startswith('test_independent_')]
assert run_cases(new_names)==79
print('MATRIX_GRID',sum(row[0]=='rejected' for row in observations),'rejected fixtures;',sum(row[0]=='admitted' for row in observations),'admitted searches')
print('MAX_GRID_ERROR',max(row[-2] for row in observations if row[0]=='admitted'))
check_hashes()
```
