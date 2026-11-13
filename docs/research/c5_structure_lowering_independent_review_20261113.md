# Independent saved C5 structure lowering review

Task `c5-structure-proof-1101052342`, assigned branch
`codex/coloring-c5-structure-proof-1101052342`, base
`de230cce74089344343fcdf1c12d553cc4cf8607`, 9 November 2026.
Fresh evidence: `dump/1109011235-c5-structure-lowering-proof/` in this worktree.

**ADMIT the exact saved 977-instruction structure oracle on its clean-data
subspace, and the four previously saved R1/R2 j=0,1 pilot observations within
their existing ideal-only scope.** This resolves the particular pending
lowering gate in independent review `4fbf3d023878617cfad9236470bb3ba8f3b28e83`.
It does not admit general zero-initialized reusable-component transpilation,
other circuits, initially dirty scratch, further iterations, noise, routing,
FT costs, a width advantage, or the whole manuscript. No 22-wire statevector
was replayed, and no new iteration observation was generated.

## Exact identities and restrictive admission

Original source/config commit:
`ed7811408c1523b9cac1881b1311500ecf3a4b35`; pilot handoff:
`0da04596b7a6c6ccbd16e2a2fed072fcace84ca5`. Pilot evidence directory in the
authoritative integration checkout is
`dump/1031221648-executed-ideal-iterations/`; checkpoint is
`dump/1031221547-c5-22-qubit-resource-pilot/checkpoint.json`.

| Admitted or reused artifact | SHA256 |
| --- | --- |
| Both `C5_k3_R1/oracle.qpy` and `C5_k3_R2/oracle.qpy` | `226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b` |
| Pilot `manifest.json` | `7fbb194c2109398bc67ddcb5705b832601d5806c15f405b4b946d4a159d8ea87` |
| `C5_k3_R1/result.json` | `de6900865099d0ca25550187b744d9d79ec3725dd4a7e1f5bcf7309560abe8a4` |
| `C5_k3_R2/result.json` | `2259b862a20fdede9dc7b77d1fbe1da925b62bd3df07259680376906fd8f2d88` |
| Prior independent review, `docs/research/c5_complete_independent_review_20261101.md` | `226cd36abb83df90a0c1c97103918a5a17f0910a1abbf604c135d01e13d3d13c` |
| New `tools/prove_c5_structure_lowering_1101052342.py` at `37c09c898f0afb19de22f18a7e349a19aaa17a93` | `47e3703e0bf89d82a5ff9f73a71972ffb89ea8ae65b0115f86d7e6369269e98d` |

All 15 pilot evidence hashes were checked afresh. All nine protected source
hashes agree with the original committed blobs and this worktree. No source
substitution, dependency import, library modification or new transpilation was
needed. The independent checker imports no production predicate, lowering,
verification or iteration implementation; Qiskit only deserializes the QPY.
Its import is asserted inside the existing interpreter prefix. The run helper's
`logique.paths` import is separately asserted to this assigned worktree.

The earlier review's exact saved data-only preparation/reflection checks are
reused, as are its logical 1,024-input predicate/restoration checks. They are
not relabeled as new checks. The new proof below supplies the missing link to
the actual saved oracle. All associated preparation/diffusion QPY identities
are included in `identities.json`; their former restrictive admission remains.
Neither the unrelated best-fit word8 failure nor two uniform trajectories is
used to decide this structure oracle's correctness.

## Compositional reachable-subspace proof

The contract is

$$V|x\rangle|0^{12}\rangle=(-1)^{f(x)}|x\rangle|0^{12}\rangle,$$

where the ten low data bits encode five two-bit colors in vertex order,
least-significant bit first. Independently, the checker defines
$f(x)=[\forall v:c_v<3]\land[\forall v:c_v\ne c_{(v+1)\bmod5}]$.
It enumerates all 1,024 binary words, including unused codes and edge violations;
exactly 30 satisfy the complete predicate. Scratch roles are ten flags10..19,
comparator scratch20 and output21. All twelve start and finish at zero.

Every saved U gate is bound to its **actual three stored binary64 parameters**
and wire; each CX is checked closed-control, with its exact ordered wires.
The saved global phase is exactly zero. The canonical gate inventory is
132 H,90 X,200 T,166 T-dagger,one Z and388 CX, totaling977. There is no fitted
global phase. The independent U convention is

$$U(\theta,\phi,\lambda)=\operatorname{diag}(1,e^{i\phi})
R_y(\theta)\operatorname{diag}(1,e^{i\lambda}).$$

At canonical angles this gives H, X and the specified diagonal phase gates
with their absolute phases. These are proved one-wire blocks. The two-wire
block identity is $CX(|b\rangle\otimes v)=|b\rangle\otimes X^b v$.
The crucial precondition that the control is a definite bit is **checked at
every CX for every input**, rather than inherited from the transpiler's
zero-initialization assumption.

The checker maintains an exact tensor product of22 two-component factors.
All coefficients lie in $\mathbb Z[\zeta_8,1/2]$, represented as
$(a+b\zeta_8+c\zeta_8^2+d\zeta_8^3)/2^k$, with integer arithmetic,
$\zeta_8^4=-1$, and $1/\sqrt2=(\zeta_8-\zeta_8^3)/2$.
H combines both coefficients exactly; X swaps them; phase gates multiply by
the relevant power of $\zeta_8$. Zero tests are exact; no tolerance prunes terms.
CX leaves the control's scalar phase intact and conditionally swaps the target.
Local identities therefore preserve the represented state inductively.

All **388×1,024=397,312** CX preconditions pass:179,696 zero controls and217,616
one controls. At most ten factors are simultaneously in superposition, but
each remains a separate one-wire factor. Only44 coefficient slots are needed
per input; the potentially1,024-term tensor product is never materialized.
At the final cut every factor has its required basis bit, and the product of
all surviving scalar coefficients is exactly $(-1)^{f(x)}$. The exact
canonical-angle residual is zero on every column. Linearity then proves the
contract for every coherent superposition on the clean-data subspace, including
an external reference entangled with those data. Intermediate superpositions
of different input columns need not themselves be product states; the proof
uses linearity, not an assumption that arbitrary coherent inputs factor.

The checker emits a hash of the entire deterministic reachable trace:
`2c3da2254065dd590d0d102994ddbc754db3d02d45e54a40ab5d04bc7cd5011a`.
`proof-validated.json` also contains all977 instruction/parameter bindings.
This is an executable exact-arithmetic certificate and a mathematical induction,
not a proof-assistant kernel artifact or a floating-point simulation.

### Stored angles, rather than silently idealized floats

The serialized U angles are binary64 approximations to multiples of pi.
The proof does not claim their transcendental matrices are exactly Clifford+T.
Machin's identity $\pi=16\arctan(1/5)-4\arctan(1/239)$ and80-term alternating
series produce rational lower/upper bounds. Comparing each exact stored float
rational with these bounds certifies its angle error. Since

$$\|U-U_0\|\le |\delta\theta|/2+|\delta\phi|+|\delta\lambda|,$$

telescoping the product of unitaries bounds the full saved-oracle operator error
by the sum over all gates. The computed rational bound is approximately
**4.8067386866533615e-14**, and is rigorously **less than5e-14**. This applies to
arbitrary normalized clean inputs without a dimension multiplier or phase
alignment. Oracle-only dirty-workspace probability is consequently bounded by
$(5e-14)^2=2.5e-27$ in mathematical exact evaluation of the stored-angle gates.
This is not a bound on floating-point simulation roundoff, preparation,
diffusion or the complete saved iteration computation. It lies well below the
pilot's1e-10 comparison tolerance.

## What the four saved observations support

The current lowering gate is now closed for the exact shared oracle. Together
with the prior independent data-only checks and the newly verified identities,
admit the following existing ideal observations, without replaying them:

| Regime | Domain N | j0 success | j1 success |
| --- | ---: | ---: | ---: |
| R1, H preparation | 1,024 | 0.029296875000 | 0.243474841118 |
| R2, valid-code preparation | 243 | 0.123456790123 | 0.775420037220 |

For30 marked inputs, $p=30/N$ and $P_1=p(3-4p)^2$. These are saved complex128
observations, not new measurements or shot estimates. The saved maximum signed
residual is5.63166374574918e-15; minimum restored-workspace probability is
0.999999999999986. R1 unused-code probability after j1 is0.5944126248359602,
while R2 is2.621660116980404e-30. These exclusions/losses remain visible.
Historical wall times50.478321s/51.134987s and peak RSS527,548,416/501,514,240bytes
are reused pilot measurements, not fresh proof-run resource measurements.

Both ledgers remain `partial_sweep`. **R1 j2,3,4,5 and R2 j2,3 are unexecuted.**
No value is promoted from an analytical prediction to an observation. The
separately admitted ten best-fit rows, their11-wire/84,441-instruction oracle,
and the original18-wire exclusions remain distinct and unchanged. This decision
does not establish that either construction has better matched costs or noise.

## Validation, failures and resource limits

Final exact proof: exit0,18.545109s boundary,66,109,440bytes Darwin wait4 high
water. Negative checks: exit0,1.830339s; they deliberately reject a nonclassical
CX control, dirty scratch20, missing marking Z (first failureword70), and altered
QPY bytes. Exact local H², HZH=X, T/T-dagger, CX², eighth-root and ring-product
identities pass. Selected Black and Ruff pass. No whole-repository suite or
native build is claimed.

Two initial checker strategies stopped safely and are retained with their
sources, logs and receipts. First, a global sparse expansion reached its
preallocation64-term guard. Second, a greedy five-wire monomial partition could
not close a block beginning at instruction305/H20 because independent ready
work was excluded by that heuristic. Neither was a circuit counterexample.
An exact tensor-factor implementation then passed all inputs in12.115738s,
revealing that every actual factor stayed one-wire. The final simpler checker
directly verifies that invariant; it does not use the unsuccessful partition.
The dispatched profile is `critical_review` (Astra/high), not a recursively
launched successor or a third Sol mathematical attempt.

Before allocations:120s/child,600s cumulative,2GiB declared process budget,
one scientific child at a time, all configured compiler/BLAS/OMP/Accelerate/
Rayon/Qiskit parallelism1. Intermediate tensor work had a predeclared1024-term
per-factor cap; final proof uses44 coefficients, no statevector, dense Operator
or density matrix. All numerical checks together used under60s. RSS is terminal
child high water, not a simultaneous process-group peak or hard memory cap.
Native executable hash
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was selected and verified but never invoked. No synchronization or build ran.

The required current root handoffs, pilot, independent review, integration
decision, saved checkpoint, logical construction, U convention and applicable
transpiler/HLS source were read. Initial large JSON reads truncated; focused
source reads and structured identity extraction followed. Initial Git stage
was sandbox-denied; scoped escalation succeeded. All failed/partial artifacts
and historical reviews remain unchanged. No README, dependency pin, queue,
archive, binary or candidate source was modified; no push or model/subagent
launch occurred. The final checkpoint records task/attempt, commits, hashes,
commands, receipts and briefing delivery.

Next: the coordinator may integrate this exact proof and restrictive decision
after checking their identities. Any semantic edit requires independent review.
Further structure iterations require a separately assigned and budgeted
execution; C5 noise and matched resource comparisons retain their own gates.
This assigned proof/review is complete; the full research gate remains open.
