**Decision: do not admit this layer to FT comparison experiments yet.** The
search derivation is sound, but preprocessing can exceed the requested error
budget while reporting an exact circuit and zero error. Fix the lowering and
gate-admission contracts first. This is an independent Task 6 review dated
2026-10-25, not final paper approval. Old abstract/evaluation claims remain
outside scope. No code, dependency pins, or commits were changed.

**Findings, in priority order**

1. **High — uncharged approximation before the measured SK stage.**
   `rotations.py:137–151,187–205,245–307,386–420` assumes lowering is exact.
   Three independently reproduced paths violate that assumption:

   | Input | Requested budget | Actual phase-sensitive operator error | Reported bound |
   | --- | ---: | ---: | ---: |
   | `RXGate(pi + 1e-9).control(2)` | 1e-12 | 4.9999984e-10 | 0 |
   | `UnitaryGate(RZGate(2*pi + 1e-12).to_matrix())` | 1e-14 | 9.9964481e-13 | 0 |
   | `rz(1e6 * 2*pi)` | 1e-12 | 3.2391776e-10 | 0 |
   | `rz(1e16)` | 1e-12 | 0.6850993 | 0 |

   All return `status="exact"`, with no residual rotations. The first comes
   from `costs.py:386–389`: `math.isclose` retains its default relative
   tolerance, accepting deviations up to approximately 3.14e-9 around pi.
   Passing `tolerance=0.0` does not affect that selector. Negative deviations
   and +3e-9 also reproduce; +4e-9 leaves rotations and fails tight synthesis
   as expected. The second comes from Qiskit 2.1.1 numerical unitary
   translation (`costs.py:446–448`), before Rz approximation. The final two
   expose floating division/argument reduction in zero-tolerance snapping
   (`costs.py:403–411`); an integral floating quotient does not establish exact
   equivalence for all admitted finite angles. The large-angle case makes this
   more than an academic sub-machine-precision objection.

   The complete API inherits the defect: using the first circuit as A, a clean
   `Z(2)` oracle, exact three-data-qubit S0, and budget 1e-12 returns bound zero
   for both j=0 and j=2, with measured errors approximately 5e-10. Thus this is
   not merely inaccurate component metadata. Tests at `test_rotations.py:111–118`
   exercise a direct near-Clifford Rz, which bypasses the lossy input translation.

   **Required:** preserve noncanonical angles or charge every preprocessing
   perturbation, including translation, phase handling, and snapping. Include
   these errors in the weighted whole-search allocation. Restrict unsupported
   angle magnitudes/precision ranges if reliable accounting is unavailable.
   Test both direct rotations and equivalent matrix/custom input forms against
   the original input, not just the lowered target. A generic Qiskit
   `optimization_level=0` is not an exactness certificate.

   Minimal reproducer, Qiskit 2.1.1:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD/src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
     /Users/mar/codex-work/logique/.venv/bin/python - <<'PY'
   import math
   import numpy as np
   from qiskit import QuantumCircuit
   from qiskit.circuit.library import RXGate, RZGate
   from qiskit.quantum_info import Operator
   from logique.benchmarks import rotations as r
   cases = []
   q = QuantumCircuit(3)
   q.append(RXGate(math.pi + 1e-9).control(2), [0, 1, 2])
   cases.append(("near-pi CCRx", q, 1e-12))
   q = QuantumCircuit(1)
   q.unitary(RZGate(2*math.pi + 1e-12).to_matrix(), [0])
   cases.append(("near-Clifford matrix", q, 1e-14))
   for angle in (1e6 * 2*math.pi, 1e16):
       q = QuantumCircuit(1)
       q.rz(angle, 0)
       cases.append((str(angle), q, 1e-12))
   for label, original, budget in cases:
       result = r.synthesize_component(original, error_budget=budget)
       error = np.linalg.norm(
           Operator(result.circuit).data - Operator(original).data, 2)
       print(label, error, result.metadata["error_bound"],
             result.metadata["status"])
   PY
   ```

2. **Medium — gate validation trusts names and only checks the surface.**
   `rotations.py:119–150` checks `Gate`, then operation names after lowering;
   `costs.py:424–448` checks only top-level MCX. A normal composite gate
   containing a three-control MCX is accepted and automatically translated
   instead of requiring the caller's explicit decomposition policy. More
   seriously, `b=QuantumCircuit(1); b.rz(.731,0); g=Gate('x',1,[]);
   g.definition=b`, appended to a circuit, is accepted as an exact zero-rotation
   Clifford circuit: the emitted gate still contains that arbitrary Rz.
   This is a reproducible generic-input contract failure, not a claim that
   ordinary Qiskit X gates are wrong.

   **Required:** recursively resolve supported composite definitions and verify
   actual supported gate types/semantics; reject opaque or conflicting names.
   Enforce the MCX policy recursively or document and record the selected
   lowering. Ordinary measurement, reset, initialize, parameter, barrier,
   delay, and a nested reset were rejected in the tests/probes.

3. **Medium — monomial cleanup claim has a numerical loophole.**
   The algebraic contract at `costs.py:235–279` is valid for genuinely monomial
   compute blocks and fresh zero scratch. However, line 261 accepts Rx angles
   within 1e-12 of pi, which are not monomial. Reproduce with:

   ```python
   from qiskit.quantum_info import Statevector
   from logique.benchmarks.costs import decompose_phase_oracle
   b = QuantumCircuit(4)
   b.mcx([0, 1, 2], 3)
   b.rx(math.pi + 5e-13, 0)
   oracle, info = decompose_phase_oracle(b, 0)
   final = Statevector.from_int(3, 2**oracle.num_qubits).evolve(oracle).data
   print(np.linalg.norm(final[16:]), info["garbage_ancillas_at_end"])
   # 4.999219856e-13 amplitude in scratch=1; metadata claims 0.
   ```

   This uses a five-qubit statevector, not a dense operator. With exactly pi,
   the residual is about 1.2e-16. **Required:** reject noncanonical angles or
   explicitly account for an approximate cleanup contract; do not advertise
   exact monomial coverage for tolerant admission. This is a small numerical
   overclaim, not a refutation of the expanded-inverse construction.

4. **Medium — corrected manuscript assembly still has conflicting instructions.**
   `conference.tex:512` describes S0 as a multi-controlled Z. A bare MCZ marks
   all ones, not zero: the stated convention requires
   `S0 = -X^n MCZ X^n` (and restoring workspace). Omitting the leading minus
   changes only the uncontrolled search's global phase, but absolute phase
   matters to this compiler's contract. Omitting the X conjugation changes
   the reflection itself. At lines 514–520, “This sequence is repeated j
   times” includes initialization; specify A once, then only O,D repeated j
   times, including j=0. The formulas at lines 388 and 524 already give the
   correct interpretation. Clarify that `U_Psi` in line 512 denotes the full
   data preparation, not only one vertex's state in line 502.

   The ancilla definitions (292), workspace lifetime/peak accounting (314,
   369), ideal success formula and iteration choice (377–381), and T-count
   formula/inverse reuse (522–526) are otherwise sound under their stated
   clean-oracle/unitary assumptions. Specify floor/ceiling nonnegative
   candidates for the first continuous peak and a tie convention; this is not
   optimization over every later oscillation or over cost per success. For
   arbitrary A, p=0 means no *prepared marked amplitude*; “no marked solution”
   additionally requires full support on the intended domain.

**Retained derivation and precision limitations**

Let `D=A S0 A†`. Time order A, followed by j copies of O,A†,S0,A, gives
`U_j=(A S0 A† O)^j A`. Therefore the emitted, unoptimized concatenation has
`T_A+j(2T_A+T_O+T_S0)`: inversion swaps T/T† and preserves their count. It is
not a lower bound or a T-depth identity. At j=0 only A is synthesized/costed;
unused O/S0 are still validated/lowered. Noncontiguous ordered data mapping
is correct and leaves auxiliary wires alone. Independent matrix multiplication
with mapping [3,1], nonzero scalar phases, and j=0,1,2 agreed to at most
1.32e-15, with T counts 1,3,5.

For genuine component norm bounds e_A,e_O,e_S0, unitary telescoping gives
`||U_j-Uhat_j|| <= (1+2j)e_A+j e_O+j e_S0` because
`||A†-Ahat†||=||A-Ahat||`. Compiling A once and inverting its emitted circuit
is the correct implementation. Allocation across weighted residual rotation
occurrences, the rounding margin, and failure instead of an analytic cost
substitution are appropriate **after** lowering errors are included.

The measured 2x2 differences are phase-sensitive; the explicit pi sign repair
does not freely fit away arbitrary phase. Scalar phases survive composition
and inversion. Keep them when controlling a circuit. The allowance
`64*eps*(length+1)` (`rotations.py:219–221`) is numerical engineering, not a
proved interval enclosure. The module correctly disclaims certification.
The exact fast path nevertheless accepts `approximate_rz(pi/4,1e-18)` with
measured error 7.02e-16 and bound zero. Distinguish algebraically exact gates
from floating implementation error and enforce/document a usable numerical
precision floor. Do not present these metadata as certified absolute bounds.

For exact monomial expanded B,
`B|x,0> = exp(i phi_x)|f(x),g(x)>`; inserting output Z multiplies each branch
by a sign, so the *actual expanded* B† removes both phase and garbage.
This extends linearly to coherent inputs/references. A five-qubit statevector
test with open-control MCX, controlled Rx(-pi), CZ, and a complex superposition
agreed with the original compute–Z–inverse action to 3.74e-16, with scratch
amplitude 3.40e-17. It does not justify throwaway diffusion, arbitrary
intervening interference, or a separately recreated forward-tree “inverse.”

**RUS primary evidence and independently checked extension**

[Paetznick and Svore, arXiv:1311.1074v2, Section 5/Figure 8 (PDF p.14)](https://arxiv.org/pdf/1311.1074v2)
and its [primary HTML Figure 8](https://arxiv.org/html/1311.1074v2#S5.F8)
specify a two-T, one-ancilla trial implementing
`U=(I+i sqrt(2) X)/sqrt(3)` on arbitrary input with success probability 3/4;
failure implements identity. Section 3 describes measurement and retry.
The source supports this single-qubit primitive; the graph-color preparation
and **14/3** below are a derivation here, not a quoted per-vertex result.

I reconstructed the trial with ancilla a and data h in time order
`H(a),T(a),CX(a,h),H(a),CX(a,h),T(a),H(a)`, then Z-measure a.
Its Kraus matrices are
`K0 = exp(-i*pi/4)*sqrt(3)/2 * U` and
`K1 = exp(i*pi/4)/2 * I` (numerical residuals <3.4e-16).
Thus outcomes reveal no data information, including on an entangled input.
Reset/reprepare the ancilla and retry on 1; the expected T cost is 2/(3/4)=8/3.

For vertex bits h (high) and l (low), initially 00, apply U(h), S†(h),
CH(h,l), X(h). The intermediate amplitudes are
`(|0>+sqrt(2)|1>)/sqrt(3)` on h after S†; the final state is exactly
`(|00>+|01>+|10>)/sqrt(3)`. CH costs two T gates: conjugate CZ by
Ry(±pi/4) on its target. Both this identity and the final state were checked
locally. Hence **8/3+2=14/3 expected T per vertex** is justified for this
specific measurement-assisted construction, with Clifford gates, ideal
measurement/reset/feed-forward unpriced, and unlimited retries. It is an
expectation, not a worst-case count or static depth. After r attempts the
remaining failure probability is 4^-r; capped protocols must report failure.

Can a Grover reflection use it? **In a separately validated dynamic model,
yes for this arbitrary-input unitary instrument; not by inserting a
probabilistic state-preparation routine into the static API.** Reverse the
extension's deterministic gates and implement U† using ZUZ, which has the
same RUS cost and identity failure branch. The scalar Kraus identities prove
preservation of coherence with other data, and local Bell-branch checks agreed
below 3e-16. Complete each retry loop before proceeding. This realizes A and
A† as data channels with random runtime, not by reversing measurements or
inverting an emitted static gate list. Quantum-controlled versions require a
new analysis of branch probabilities/phases. A preparation-only rejection
sampler would not supply this arbitrary-input inverse. No dynamic Grover
implementation or cost experiment is approved by this derivation alone.

[Brassard et al., Quantum Amplitude Amplification and Estimation](https://arxiv.org/abs/quant-ph/0005055)
provides the primary unitary A/inverse framework. Here, writing
`A|0>=sin(theta)|good>+cos(theta)|bad>` derives
`P_j=sin²((2j+1)theta)` for exact clean phase marking and matched reflection;
p=M/N only for the relevant uniform domain.

**Restricted preparation and review limits**

If ideal A prepares only valid codes and `||Ahat-A||<=eta`, initial invalid-code
probability is at most eta². If the entire implemented search is within
operator distance E of an ideal search confined to that subspace, final
invalid-code probability is at most E², and any success-event probability
differs by at most min(1,2E). These are consequences of a *valid* whole-search
bound, which the current preprocessing breaks. With Ahat, even its exact
matched reflection need not preserve the ideal valid-code subspace. R3's
edge-only oracle can mark leaked invalid codes; report actual proper-coloring
success and leakage separately. Domain checks are redundant only on the
supported ideal subspace, not globally equivalent predicates. The ideal sine
formula is not automatically exact for independently approximated O/S0.

Validation used the requested Python executable and `PYTHONPATH=$PWD/src`,
one local process at a time, with Qiskit 2.1.1. Ran
`python -m pytest -q -p no:cacheprovider tests/test_rotations.py`: **49 passed
in 15.76s**. Independent probes covered the failures above, direct near-Clifford
Rz/Rx/Ry/P rejection at tight budgets, exact/inverse phases, j=0/1/2 matrix
order and counts, gate admission, monomial cleanup, and RUS branch/state
identities. Dense operators were at most four qubits; the two scratch checks
used five-qubit statevectors only. The larger `test_costs.py` cases were read,
not run. Literature access used native live web retrieval of primary sources.
No hardware, paid/model API calls, other model jobs, physical QEC estimates,
or authentication artifacts were used. Only this review file was written.
