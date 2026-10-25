# Independent critical quantum/mathematical re-review

**Review outcome: COMPLETE. Scientific gate: BLOCKED — do not yet approve the full advertised rotation layer for static FT comparison experiments.**

Date: 2026-10-25. This is a read-only review of the repair worktree, with only this `CRITICAL_REVIEW.md` written in the separate review worktree. The earlier rotation-layer blockers are repaired in the tested cases. A new admitted-matrix counterexample violates the whole-search error budget, and the earlier manuscript assembly instructions remain inconsistent. This decision is not a rejection of the unitary telescoping derivation or of the tested standard-unitary paths. It is not publication approval.

## Reviewed identity and scope

Source root: `/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/worktrees/rotation-repair`.

The **actual two reviewed files**, hashed before and after the substantive review, were:

| File relative to source root | SHA-256 |
| --- | --- |
| `src/logique/benchmarks/rotations.py` | `5a811a35f2f3d6203d68bb441213d521883b8b56235054df7384fd00db679457` |
| `tests/test_rotations.py` | `5513b65b67831e9100e76db00fadbbe22890da125f1abe8492d65c026cd924a1` |

The decision applies to these bytes in this dependency context, not to a similarly named integration copy. Both files were already untracked in the repair worktree. The repair checkpoint was read as context, not accepted as proof.

Read both worktrees' `AGENTS.md` and the requested prior review at `/Users/mar/codex-work/logique/docs/research/task6_critical_review.md`. To verify its other blockers, also inspected and probed the repair worktree's existing `costs.py` and read its manuscript. Context hashes:

- `src/logique/benchmarks/costs.py`: `42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8`.
- `docs/manuscript/conference.tex`: `fb72f485ac771872e3d0d1d45e0f52f44d50107a8c965777408f45c7efc2da28`.

No implementation, dependencies, integration copies, or historical results were changed. No agents/model subprocesses, API calls, purchases, hardware, pushes, or publication were used. No literature searches or unrelated derivations were repeated.

## Remaining findings

### 1. High: admitted nonunitary numeric matrices invalidate the advertised search bound

Location: `rotations.py:259–267` (matrix admission), `306–310` (local error accounting), and `615–680` (unitary-weighted allocation and final bound).

Qiskit's normal `UnitaryGate` admission accepts `(1 + 1e-6) * I` with its default numerical tolerances. Reconstructing another `UnitaryGate` therefore does not establish the unitarity required by the telescoping proof. No `check_input=False`, monkeypatch, custom subclass, or forged gate is needed.

Use that one-qubit matrix as A, O=Z, S0=Z, and j=2. The documented numeric target is `(A S0 A† O)^2 A = (1+delta)^5 I`; emitted A is I. All matrices in this counterexample are 2x2. The independently multiplied target and analytic scalar expression agree within 2e-15:

| Quantity | Observed value |
| --- | ---: |
| delta | 1e-6 |
| Measured phase-sensitive search error | 5.000009999589494e-6 |
| Reported search error bound | 5.000000212751493e-6 |
| Understatement | 9.786838001593482e-12 |
| Requested budget in second reproduction | 5.000005e-6 |

The second call succeeds with **reported bound < requested budget < actual error**. The local discrepancy is charged, but weights of five alone miss higher-order terms from nonunitary target factors: `(1+delta)^5 - 1 > 5*delta`.

This is an admission/contract failure, not a physically implementable nonunitary gate or a counterexample to the theorem for genuine unitaries. The module explicitly targets supplied numeric Qiskit operators and advertises finite one-qubit matrix support; a caller using Qiskit's ordinary constructor can reach this case. The “numerical, not certified” caveat does not explain away a measured requested-budget violation.

**Required before approving that path:** reject sufficiently nonunitary matrix inputs using a tolerance tied to the available numerical allowance, or explicitly normalize/project to a unitary and redefine/account for the target, or use norm-aware product bounds for supplied numeric operators. Preserve a regression that requires rejection or a valid bound for this input. Do not merely increase a fixed floating-point allowance to mask the example. If integration instead excludes all matrix input, that is a narrower contract requiring an explicit enforced restriction and review; this report does not silently grant that exemption.

### 2. Medium: the previous manuscript assembly blocker remains

In the inspected repair worktree, `docs/manuscript/conference.tex:512` still describes the zero reflection as a bare multi-controlled Z. The independent two-qubit calculation gives operator distance **2.0** between that gate and `S0=2|00><00|-I`. The required construction is `-X^n MCZ X^n`, preserving scalar phase and restoring workspace.

Line 520 still says the sequence including initialization is repeated j times. The correct circuit initializes with A once, then repeats O,A†,S0,A. At j=0, the two descriptions differ by A versus identity; the embedded H example has norm distance 2. Clarify that the preparation in the diffusion expression acts on all data registers.

Line 381 also retains “p=0 ... no marked solution”; for arbitrary A this only establishes zero prepared marked amplitude. The floor/ceiling candidates for the first continuous peak and a tie convention remain unspecified. These are previously identified manuscript limitations, not new research claims. Implementation experiments must use the explicit compiler contract, not the conflicting prose; no manuscript/paper approval is given.

## Disposition of every previous blocker

| Prior issue | Independent concrete check | Result |
| --- | --- | --- |
| Near-pi controlled Rx silently reported exact | CCRx(pi+delta), delta in {-3e-9,-1e-9,1e-9,3e-9}, all four control states; tight 1e-12 and loose 1e-7 budgets | Tight calls reject; loose results have nonzero accounted errors within budget. Fixed for these cases. |
| Near-Clifford matrix translation uncharged | Original matrix Rz(2*pi+1e-12), including nested custom wrappers and scalar phases | 1e-14 rejects at floor; 1e-12 rejects preprocessing; loose error 9.99644811372491e-13 <= bound 1.0280665208028956e-12. Fixed for this unitary matrix. |
| Large-angle snapping | Both signs of 1e6*2*pi and 1e16, direct Rz/Rx/Ry/P; standalone approximate_rz | Explicit rejection. Range restriction is a legitimate resolution, not an approximation claim. |
| Name-only/surface-only gate admission | Gate("x") with Rz definition, modified X definition, opaque gate, nested reset, three nested wrappers around open-control MCX, two-qubit matrix | Rejected. Nested MCX also rejects as an unused j=0 oracle. Ordinary recursive custom unitary definitions remain supported. |
| Whole-search preprocessing omitted | Original-input matrix products for near-pi j=0,1,2; mixed A/O/S0 preprocessing with mapping [3,1] and repeated residual rotations | Original unitary targets satisfy measured bounds; preprocessing is subtracted before rotation allocation and carries (1+2j,j,j) weights. Fixed for tested unitary inputs, subject to new matrix-admission finding above. |
| Approximate monomial cleanup admitted | Original 4-wire MCX plus Rx(pi±5e-13) | Both rejected by current costs.py. Exact open-control MCX/controlled-Rx(-pi)/CZ compute–Z–actual-inverse passes coherent statevector check with fresh zero scratch. |
| Bare MCZ and repeated initialization in prose | Current text plus 2-qubit zero-reflection matrix and j=0 H example | Still unresolved; see finding 2. |
| Exact fast path bypassed practical precision floor | pi/4 at 1e-14 and 1e-18; canonical angles at 1e-12 | Subfloor requests reject, canonical outputs carry nonzero numerical lowering allowance. Fixed as a documented numerical contract, not certified arithmetic. |

Near-pi whole-search results (original input, not just lowered target):

| j | Measured norm error | Reported bound |
| ---: | ---: | ---: |
| 0 | 4.999999858597314e-10 | 7.509836419737957e-10 |
| 1 | 5.000002641499217e-10 | 2.2532355872070205e-9 |
| 2 | 5.000003230035745e-10 | 3.7554875324402454e-9 |

The dependencies already have stricter near-pi gadget and monomial admission than the previous review described. That contextual change was inspected directly; it was not attributed solely to rotations.py.

## Mathematical and phase checks retained

For unitary components, the emitted ordering agrees with `U_j=(A S0 A† O)^j A`. Independent tests compute this by matrix multiplication/power, separately from the compiler's circuit assembly. They use scalar phases, ordered noncontiguous data mapping [3,1], an untouched auxiliary wire, and j=0,1,2.

An instrumented call observes one synthesis of A's residual rotation for each search compilation, independent of j. The returned inverse equals the actual emitted A inverse, agrees with its matrix adjoint, and appears in the actual assembled gate sequence. The emitted T counts in the mixed probe are 633, 8535, and 14225 for j=0,1,2 (precision allocation changes between these searches). Within each search, counts obey `T_A+j(2T_A+T_O+T_S0)`; this is a concatenation identity, not a T-depth formula or optimality claim.

For genuine unitaries the norm argument remains:
`E <= (1+2j)e_A + j e_O + j e_S0 + e_assembly`.
The local errors include lowering, rotation approximations, and scalar assembly allowances. Independent reconstruction of preprocessing and final sums agrees with metadata at relative tolerance 1e-14, with zero absolute tolerance. The mixed-search results were:

| j | Measured norm error | Bound | Preprocessing charged |
| ---: | ---: | ---: | ---: |
| 0 | 0.007768017338085722 | 0.007768017354214598 | 1.0849099396637034e-12 |
| 1 | 0.00019472675804861365 | 0.000584180496759366 | 7.423571506948765e-12 |
| 2 | 0.0001947267580899635 | 0.0009736341626552238 | 1.3762233074233827e-11 |

All comparisons use the spectral norm of the difference, without free phase alignment. Deliberately adding scalar phase 0.1 gives error 0.10015282146685173, exposing phase loss. Canonical ±2*pi and other Clifford angles also preserve phase within their charged bounds.

The cleanup check uses a deterministic complex superposition and a **five-qubit statevector only**: data discrepancy 4.684427951246116e-16, scratch amplitude 2.3891998240481017e-16. No dense operator exceeds four qubits. This supports the genuine monomial/actual-inverse contract and does not extend it to arbitrary interference or throwaway diffusion.

## Numerical limitations and experiment gate

Retain all numerical-not-certified qualifications. The 64*eps allowances are engineering margins, not interval enclosures. Requested and allocated precision have a 1e-12 floor; bounded SK may still fail above that floor. Unchanged standard Clifford+T gates are algebraic operations, not a certification of floating simulation of arbitrarily long products. Numerical targets are stored Qiskit operators; composite/StatePreparation targets mean resolved definitions, not a certified ideal amplitude vector. Angles are restricted to +/-2*pi, matrix inputs to one qubit, and recursion to bounded work.

Clean-oracle and zero-reflection semantics remain caller obligations. This review does not approve measurement/RUS/dynamic search, quantum-controlled routines that discard scalar phase, physical QEC estimates, or hardware submission. Leakage and proper-coloring success must still be reported separately for approximate restricted preparations; their prior error consequences require a valid whole-search bound.

**Static FT experiments: not approved for the full current API.** Close the admitted-matrix norm/accounting gap and the existing assembly instructions, then re-review changed bytes. The standard-unitary paths tested here are encouraging evidence, not a substitute for resolving the explicit remaining gate.

## Validation and preserved reproducers

Environment: Python 3.10.22, Qiskit 2.1.1, NumPy 2.2.6, pytest 8.4.2. Confirmed imported `rotations.__file__` resolves to the reviewed repair-worktree source. Runs used the exact requested interpreter and source path, bytecode disabled, pytest cache provider disabled, and one local numerical process at a time.

- Supplied test file: **78 passed in 16.60s**.
- Independent embedded suite below: **37 passed in 4.67s**. Two tests deliberately assert the presence of blockers (manuscript and admitted near-unitary matrix); their passing is evidence of those blockers, not implementation approval.
- After adding the tighter requested-budget assertion, reran that affected probe: **1 passed, 36 deselected in 0.45s**, confirming the accepted budget violation. Unchanged independent cases were not rerun.
- Read larger costs tests, but did not run their dense-operator cases; used the bounded independent cleanup check instead.

Reproduce supplied tests from any directory:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/worktrees/rotation-repair/src \
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/mar/codex-work/logique/.venv/bin/python -m pytest -q -p no:cacheprovider \
/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/worktrees/rotation-repair/tests/test_rotations.py
```

To run the exact independent code preserved below, from this review worktree run this shell command. The temporary pytest file is removed automatically; this Markdown artifact remains the sole durable review output.

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/worktrees/rotation-repair/src \
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/mar/codex-work/logique/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
import sys
import tempfile
text = Path("CRITICAL_REVIEW.md").read_text()
code = text.split("```python\n", 1)[1].split("\n```", 1)[0]
with tempfile.TemporaryDirectory(prefix="rotation-rereview-") as directory:
    path = Path(directory) / "test_independent_review.py"
    path.write_text(code)
    raise SystemExit(subprocess.call([
        sys.executable, "-m", "pytest", "-q", "-s",
        "-p", "no:cacheprovider", str(path)
    ]))
PY
```

The independent suite (assertions and numeric output preserved in executable form):

```python
import math
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RXGate, RZGate, XGate
from qiskit.quantum_info import Operator, Statevector
from logique.benchmarks import rotations as r
from logique.benchmarks.costs import decompose_phase_oracle, ft_metrics

ROOT = Path("/Users/mar/codex-work/logique/dump/1024235721-coloring-paper-server-checkpoint/worktrees/rotation-repair")

def matrix(q):
    assert q.num_qubits <= 4
    return Operator(q).data

def distance(a, b):
    return float(np.linalg.norm(matrix(a) - matrix(b), 2))

def embed(q, width, wires):
    out = QuantumCircuit(width)
    out.compose(q, qubits=wires, inplace=True)
    return matrix(out)

def target(a, o, s, mapping, j):
    am = embed(a, o.num_qubits, mapping)
    sm = embed(s, o.num_qubits, mapping)
    return np.linalg.matrix_power(am @ sm @ am.conj().T @ matrix(o), j) @ am

def zero_reflection(n):
    q = QuantumCircuit(n, global_phase=math.pi)
    q.x(range(n))
    if n == 1:
        q.z(0)
    elif n == 2:
        q.cz(0, 1)
    else:
        q.h(2); q.ccx(0, 1, 2); q.h(2)
    q.x(range(n))
    expected = -np.eye(2**n)
    expected[0, 0] = 1
    assert np.linalg.norm(matrix(q) - expected, 2) < 2e-15
    return q

@pytest.mark.parametrize("delta", [-3e-9, -1e-9, 1e-9, 3e-9])
@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_near_pi_controls(delta, state):
    a = QuantumCircuit(3)
    a.append(RXGate(math.pi + delta).control(2, ctrl_state=state), range(3))
    with pytest.raises(r.PrecisionNotReachedError):
        r.synthesize_component(a, error_budget=1e-12)
    out = r.synthesize_component(a, error_budget=1e-7)
    err = distance(out.circuit, a)
    assert err <= out.metadata["error_bound"] <= 1e-7
    assert out.metadata["status"] == "approximated"

@pytest.mark.parametrize("j", [0, 1, 2])
def test_near_pi_whole_search(j):
    a = QuantumCircuit(3)
    a.append(RXGate(math.pi + 1e-9).control(2), range(3))
    o = QuantumCircuit(3); o.z(2)
    s = zero_reflection(3)
    with pytest.raises(r.PrecisionNotReachedError):
        r.compile_search(a, o, s, data_qubits=[0, 1, 2], iterations=j, error_budget=1e-12)
    out = r.compile_search(a, o, s, data_qubits=[0, 1, 2], iterations=j, error_budget=1e-7)
    err = np.linalg.norm(matrix(out.circuit) - target(a, o, s, [0, 1, 2], j), 2)
    assert err <= out.metadata["error_bound"] <= 1e-7
    print("near_pi_search", j, float(err), out.metadata["error_bound"])

def test_matrix_and_recursive_custom_forms():
    a = QuantumCircuit(1)
    a.unitary(RZGate(2*math.pi + 1e-12).to_matrix(), [0])
    for budget in [1e-14, 1e-12]:
        with pytest.raises(r.PrecisionNotReachedError):
            r.synthesize_component(a, error_budget=budget)
    out = r.synthesize_component(a, error_budget=1e-8)
    err = distance(out.circuit, a)
    assert 1e-13 < err <= out.metadata["lowering_error_bound"]
    assert out.metadata["rotation_count"] == 0
    print("matrix_translation", err, out.metadata["error_bound"])
    for phase in [0.0, 0.37]:
        child = a.copy(); child.global_phase = phase
        outer = QuantumCircuit(1, global_phase=0.21)
        outer.append(child.to_gate(label="matrix wrapper"), [0])
        nested = QuantumCircuit(1, global_phase=0.13)
        nested.append(outer.to_gate(), [0])
        got = r.synthesize_component(nested, error_budget=1e-8)
        assert distance(got.circuit, nested) <= got.metadata["error_bound"]
    body = QuantumCircuit(1, global_phase=0.37); body.rx(0.731, 0)
    q = QuantumCircuit(1, global_phase=0.21); q.append(body.to_gate(), [0])
    got = r.synthesize_component(q)
    assert distance(got.circuit, q) <= got.metadata["error_bound"] <= 1e-3

@pytest.mark.parametrize("kind", ["name", "modified", "opaque", "reset", "nested_mcx", "wide_matrix"])
def test_gate_admission(kind):
    q = QuantumCircuit(1)
    body = QuantumCircuit(1); body.rz(0.731, 0)
    if kind == "name":
        g = Gate("x", 1, []); g.definition = body
    elif kind == "modified":
        g = XGate().to_mutable(); g.definition = body
    elif kind == "opaque":
        g = Gate("opaque", 1, [])
    elif kind == "reset":
        g = Gate("nested_reset", 1, [])
        g.definition = QuantumCircuit(1); g.definition.reset(0)
    elif kind == "nested_mcx":
        body = QuantumCircuit(4); body.mcx([0, 1, 2], 3, ctrl_state=2)
        for _ in range(3):
            wrapper = QuantumCircuit(4); wrapper.append(body.to_gate(), range(4))
            body = wrapper
        q = body
    else:
        q = QuantumCircuit(2); q.unitary(np.eye(4), [0, 1])
    if kind in ["name", "modified", "opaque", "reset"]:
        q.append(g, [0])
    with pytest.raises(ValueError):
        r.synthesize_component(q)
    if kind == "nested_mcx":
        with pytest.raises(ValueError):
            r.compile_search(QuantumCircuit(1), q, zero_reflection(1),
                             data_qubits=[0], iterations=0)

@pytest.mark.parametrize("angle", [1e6*2*math.pi, -1e6*2*math.pi, 1e16, -1e16])
def test_large_angles(angle):
    for method in ["rz", "rx", "ry", "p"]:
        q = QuantumCircuit(1); getattr(q, method)(angle, 0)
        with pytest.raises(ValueError, match="angle parameters"):
            r.synthesize_component(q, error_budget=1e-12)
    with pytest.raises(ValueError, match="angle parameters"):
        r.approximate_rz(angle, 1e-12)

def test_precision_floor_and_phase_sensitive_norm():
    for budget in [1e-14, 1e-18]:
        with pytest.raises(r.PrecisionNotReachedError, match="precision floor"):
            r.approximate_rz(math.pi/4, budget)
    for angle in [-2*math.pi, -math.pi/4, 0, math.pi/4, 2*math.pi]:
        q = QuantumCircuit(1); q.rz(angle, 0)
        out = r.approximate_rz(angle, 1e-12)
        assert distance(out.circuit, q) <= out.metadata["error_bound"] <= 1e-12
    out = r.approximate_rz(0.731, 1e-3)
    q = QuantumCircuit(1); q.rz(0.731, 0)
    assert distance(out.circuit, q) <= out.metadata["error_bound"]
    bad = out.circuit.copy(); bad.global_phase += 0.1
    assert distance(bad, q) > 0.09
    print("phase_shift_error", distance(bad, q))

@pytest.mark.parametrize("j", [0, 1, 2])
def test_weighted_preprocessing_actual_inverse_and_mapping(j):
    u = RZGate(2*math.pi + 1e-12).to_matrix()
    a = QuantumCircuit(2, global_phase=0.23)
    a.unitary(u, [0]); a.h(0); a.rz(0.731, 1); a.cx(0, 1)
    o = QuantumCircuit(4, global_phase=0.17)
    o.unitary(u, [3]); o.z(3); o.unitary(u.conj().T, [3])
    s = QuantumCircuit(2)
    s.unitary(u, [0]); s.compose(zero_reflection(2), inplace=True)
    s.unitary(u.conj().T, [0])
    mapping = [3, 1]; budget = 0.02
    with patch.object(r, "approximate_rz", wraps=r.approximate_rz) as tracked:
        out = r.compile_search(a, o, s, data_qubits=mapping, iterations=j, error_budget=budget)
    m = out.metadata
    parts = [out.preparation, out.oracle, out.zero_reflection]
    weights = [1+2*j, j, j]
    counts = [p.metadata["rotation_count"] for p in parts]
    assert tracked.call_count == sum(c for c, w in zip(counts, weights) if w)
    occurrences = sum(c*w for c, w in zip(counts, weights))
    assert occurrences == m["rotation_occurrences"]
    preprocessing = m["assembly_error_bound"] + sum(
        w*(p.metadata["lowering_error_bound"] + p.metadata["assembly_error_bound"])
        for p, w in zip(parts, weights))
    assert math.isclose(preprocessing, m["preprocessing_error_bound"], rel_tol=1e-14, abs_tol=0)
    assert math.isclose(m["per_rotation_precision"],
        (budget-preprocessing)*(1-1e-12)/occurrences, rel_tol=1e-14, abs_tol=0)
    bound = m["assembly_error_bound"] + sum(w*p.metadata["error_bound"] for p,w in zip(parts,weights))
    assert math.isclose(bound, m["error_bound"], rel_tol=1e-14, abs_tol=0)
    assert out.preparation_inverse == out.preparation.circuit.inverse()
    assert np.linalg.norm(matrix(out.preparation_inverse) -
                          matrix(out.preparation.circuit).conj().T, 2) < 1e-11
    assembled = QuantumCircuit(4)
    assembled.compose(out.preparation.circuit, qubits=mapping, inplace=True)
    for _ in range(j):
        assembled.compose(out.oracle.circuit, inplace=True)
        assembled.compose(out.preparation_inverse, qubits=mapping, inplace=True)
        assembled.compose(out.zero_reflection.circuit, qubits=mapping, inplace=True)
        assembled.compose(out.preparation.circuit, qubits=mapping, inplace=True)
    assert assembled == out.circuit
    err = np.linalg.norm(matrix(out.circuit) - target(a, o, s, mapping, j), 2)
    assert err <= m["error_bound"] <= budget
    assert all(out.circuit.qubits[2] not in item.qubits for item in out.circuit.data)
    expected_t = sum(w*p.metadata["metrics"]["t_count"] for p,w in zip(parts,weights) if w)
    assert ft_metrics(out.circuit)["t_count"] == expected_t
    print("weighted_search", j, float(err), m["error_bound"],
          preprocessing, tracked.call_count, expected_t)

def test_cleanup_previous_tolerant_admission_and_exact_inverse():
    for delta in [-5e-13, 5e-13]:
        b = QuantumCircuit(4); b.mcx([0, 1, 2], 3); b.rx(math.pi+delta, 0)
        with pytest.raises(ValueError, match="monomial"):
            decompose_phase_oracle(b, 0)
    b = QuantumCircuit(4)
    b.mcx([0, 1, 2], 3, ctrl_state=3)
    b.append(RXGate(-math.pi).control(2), [0, 3, 1]); b.cz(1, 2)
    actual, info = decompose_phase_oracle(b, 1)
    reference = b.copy(); reference.z(1); reference.compose(b.inverse(), inplace=True)
    rng = np.random.default_rng(6025)
    psi = rng.normal(size=16) + 1j*rng.normal(size=16); psi /= np.linalg.norm(psi)
    extended = np.zeros(2**actual.num_qubits, complex); extended[:16] = psi
    observed = Statevector(extended).evolve(actual).data
    expected = Statevector(psi).evolve(reference).data
    err = np.linalg.norm(observed[:16]-expected); scratch = np.linalg.norm(observed[16:])
    assert err < 2e-14 and scratch < 2e-14
    assert info["garbage_ancillas_at_end"] == 0
    print("cleanup_statevector", actual.num_qubits, err, scratch)

def test_manuscript_previous_blocker_still_present():
    text = (ROOT/"docs/manuscript/conference.tex").read_text()
    assert "a multi-controlled Z gate" in text
    assert "This sequence is repeated $j$ times" in text
    s = zero_reflection(2)
    bare = QuantumCircuit(2); bare.cz(0, 1)
    assert distance(s, bare) > 1.99
    a = QuantumCircuit(1); a.h(0)
    assert distance(a, QuantumCircuit(1)) > 1.99
    print("manuscript_bare_mcz_error", distance(s, bare))

def test_reproducer_near_unitary_matrix_understates_whole_search_error():
    # A passing assertion here CONFIRMS the new blocker, not a valid bound.
    delta = 1e-6
    a = QuantumCircuit(1); a.unitary((1+delta)*np.eye(2), [0])
    o = QuantumCircuit(1); o.z(0)
    s = zero_reflection(1)
    out = r.compile_search(a, o, s, data_qubits=[0], iterations=2, error_budget=1e-3)
    err = float(np.linalg.norm(matrix(out.circuit)-target(a,o,s,[0],2), 2))
    analytic = (1+delta)**5-1
    assert abs(err-analytic) < 2e-15
    assert err > out.metadata["error_bound"] + 9e-12
    print("CONFIRMED_BLOCKER", qiskit.__version__, err,
          out.metadata["error_bound"], err-out.metadata["error_bound"])
    tight_budget = 5.000005e-6
    tight = r.compile_search(a, o, s, data_qubits=[0], iterations=2,
                             error_budget=tight_budget)
    tight_error = float(np.linalg.norm(matrix(tight.circuit)-target(a,o,s,[0],2), 2))
    assert tight.metadata["error_bound"] < tight_budget < tight_error
    print("CONFIRMED_REQUESTED_BUDGET_VIOLATION", tight_error,
          tight.metadata["error_bound"], tight_budget)

```
