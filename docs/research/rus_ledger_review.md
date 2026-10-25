# Independent analytical k=3 RUS ledger review

**Bounded review COMPLETE. Decision: ADMIT these exact analytical ledger bytes
and supporting mathematical identities under the ideal-instrument assumptions
below. No concrete correctness blocker was found.** This admits analytical
accounting only, not dynamic RUS execution, a retry runtime, quantum control,
hardware, static compiler replacement, graph break-even or paper claims.
**Full paper remains unfinished.**

Date: 2026-10-25, America/Montreal. Review branch:
codex/coloring-rus-review-1025083656; intake HEAD
28413d805f953b3bdd242cdcb426c55cb1a988e0. Review worktree is
/Users/mar/codex-work/logique/dump/1025083656-static-ft-pilot-triage/worktrees/rus-review.
Only this artifact is owned. Read-only candidate is sibling rus-ledger,
branch codex/coloring-rus-ledger-1025083656, correctness commit
dd1aeb9a50ee3ef1d57fd279304f8013590e022d, checkpoint/HEAD
e527a424f7046ccb5087b3cc6d2dfe8901b4c37c. Both worktrees were clean at intake.

## Predecessor triage and evidence

Git and durable dispatcher state were inspected first. No previous completed
review existed. Predecessor rus-ledger-1025083656 is **complete**, attempt 1,
exit 0. Its saved result and full checkpoint report bounded implementation
complete with admission pending. It was not a blocked predecessor.
Current review is the sole durable running queue job, attempt 1, session
01a1750a-88f3-74a0-b6c7-f068a0d70058. The manifest's older active-job snapshot
is stale relative to state.json. ps was sandbox-denied; no complete OS process
visibility is claimed. Dispatcher state and queue were never changed.

Read AGENTS.md, CLAUDE.md, the full 638-line revision plan, full 441-line
worktree implementation audit, both assigned batch files, server checkpoint
manifest, root static FT pilot admission, rotation numerical contract and
the full 248-line Task 6 critical review. Later root native/QPY/parallel work
has separate owners and was not duplicated or integrated here.

Inspected all 298 candidate source lines, all 420 test lines, its entire
239-line checkpoint, both actual commits and saved dispatcher evidence in
dump/1025021922-coloring-auto-dispatch/attempts/rus-ledger-1025083656-001/.
Saved command records corroborate both 100-test runs, final Black/Ruff/mypy,
standard-library-only import, and the preliminary Ruff E741 failure fixed
before commit. There is no generated RUS run directory or observed circuit
cost dataset. Analytical outputs must not be reported as execution measurements.

Primary provenance checked live, read-only:
[Paetznick and Svore, arXiv:1311.1074v2, section 5 / Figure 8](https://arxiv.org/html/1311.1074v2#S5.F8).
This supplies the two-T, single-ancilla primitive, success 3/4 and identity
failure. The coloring extension and 14/3 expected T per vertex are local
derivations, not a quoted coloring result or a minimality claim.

## Independent mathematical assessment

Assume exact ideal H/T/CX/Clifford operations, a fresh zero ancilla per
trial, noiseless Z measurement, classical record, reset/repreparation and
feed-forward. Data/references remain coherent while each loop completes.
A cap exhaustion aborts the program; it is not treated as completed or
silently restarted. O/S0 in a program are ideal deterministic operations
with external costs: this ledger does not verify their actual semantics
or workspace restoration.

Use basis |a,h> and t=(1+i)/sqrt(2). Starting ancilla blocks [I;0] become
[I;tX]/sqrt(2) after H,T,CX, then [I+tX;X-tI]/2 after H,CX.
The final T,H yields

K0=((1-t²)I+2tX)/(2sqrt(2)), K1=(1+t²)I/(2sqrt(2)).

Thus K0=alpha U and K1=beta I, where U=(I+i sqrt(2)X)/sqrt(3),
alpha=(1-i)sqrt(3/8), beta=(1+i)/sqrt(8). Since X†=X and X²=I,
U†U=I, K0†K0=3I/4, K1†K1=I/4 and completeness holds.
For every joint data/reference density operator rho, success is
(3/4)(U tensor I) rho (U† tensor I), failure is rho/4.
This proves arbitrary-input/reference coherence and input-independent
probabilities, rather than inferring them from a zero-state example.

First success at trial r has phase-sensitive operator
alpha beta^(r-1) U and probability (3/4)(1/4)^(r-1).
Unlimited summation is trace preserving with almost-sure completion
and no finite worst case. Scalar branches also prove independent retry
counts between arbitrary ideal data operations, even on entangled vertices.
This is an ideal-instrument theorem, not runtime validation.

For vertex bits |h,l>, low bit l, set E=X_h CH_(h,l) S†_h and
V=E(U_h tensor I_l). Direct multiplication gives the four rows of V,
each divided by sqrt(3):

- (1, 1, -i/sqrt(2), -i/sqrt(2))
- (1, -1, -i/sqrt(2), i/sqrt(2))
- (1, 0, i sqrt(2), 0)
- (0, 1, 0, i sqrt(2))

All columns are checked; V|00> is uniform on 00,01,10 and zero on 11.
Let C=Rx(-pi/2), B=C T C†=exp(i*pi/8) Ry(pi/4).
Then CH=(I tensor B) CZ (I tensor B†), with two T/T† gates.
Scalar phases cancel in this conjugation; no optimality claim is made.

V†=(U†_h tensor I) E† and U†=ZUZ. The inverse time order is
X_h, CH, S_h **once**, followed by a fresh ZUZ instrument.
An inner failure is beta I, but relative to the original vertex it is
beta E†. Repeating E† after failure is wrong. Successful inverse
at trial r is alpha beta^(r-1) V†, not the adjoint of a sampled
forward branch. Forward and inverse paths of lengths r,t compose
to alpha² beta^(r+t-2) I, retaining actual scalar phases.
Discarding the record yields the inverse data channel upon completion;
no phase fitting, measurement reversal or quantum-control claim is used.

Products on disjoint vertices extend this arbitrary-input identity
to n vertices and references. Initialize A once, then time order
O,A†,S0,A for each of j iterations: L=n(1+2j) loops, n(1+j)
forward and nj inverse invocations. Every completed record is a
scalar times the same ideal program. Aborted prefixes generally differ.
The independent cap=2, n=1,j=1 instrument calculation includes all eight
successful records and all abort records, verifies completeness and
the successful joint-reference channel. It is finite Kraus algebra,
not dynamic circuit execution.

## Ledger semantics and resource roles

For p=3/4,q=1/4, geometric N has E[N]=4/3, Var(N)=4/9.
Trial T=2N has mean 8/3 and variance 16/9. A completed vertex
2N+2 has mean 14/3 and variance 16/9. L independent loops give
mean 14L/3 and variance 16L/9. Deterministic supplied O/S0 costs add
j(T_O+T_S0) to the mean, without increasing variance. This is neither
a T-depth identity nor a wall-time or optimized-gate-count result.

For cap c, M=min(N,c), s=1-q^c:
E[M]=sum(q^r,r=0..c-1)=s/p;
E[M²]=sum((2r+1)q^r,r=0..c-1)
=(1+q-q^c(2cp+1+q))/p².
Subtract c q^c and c² q^c respectively before dividing by s to
condition on success; subtract the conditional mean squared for
variance. The exhausted mass at c belongs to unconditional moments.

Exact program exhaustion is 1-s^L, with union bound min(1,L q^c).
This is retry exhaustion, not coloring/search failure. success_* fields
condition on all loops completing. stop_* fields include aborted runs,
wasted trials and inverse prefixes. A reached forward vertex costs
2E[M]+2s; a reached inverse costs 2+2E[M]. Serial position i has
reach probability s^i. O at zero-based iteration r has weight
s^(n(1+2r)); S0 has s^(n(2+2r)). Summing those weights derives the
source geometric sums. Independent binary-word probability polynomials
check the schedule without candidate helpers.

n=0 means no loops or retry failure even at c=0, while j external
charges remain symbolic; this does not assert an executable empty search.
j=0 costs only preparation. For n>0,c=0 the first forward loop aborts
before extension or O/S0. Impossible success-conditioned quantities
are None; empty successful sums are zero. Unknown external costs remain
None if reached, and contribute zero if unused/unreachable.
Finite Lc attempt and L(2c+2) vertex-T bounds are conservative, not
always attainable. Nonempty unlimited loops have no finite worst case.

Integer arguments reject bool, float, Fraction, string and negatives;
only k=3 is supported. Nonnegative external int/Fraction values are
symbolic deterministic charges, not fractional emitted gate claims.
Unsupported quantum-control/state-dependent/graph/optimal-j inputs
are rejected. Callers must bound parameter sizes because exact rational
outputs can grow with n,j,c; no general resource-limiting API is claimed.

Data width 2n and retry ancillas (one shared or n allocated parallel)
are different roles. Both policies retain the serial stop-cost schedule.
Parallel allocation does not price simultaneous abort behavior or depth.
O/S0 workspace is unknown and excluded: this is not total circuit width.
Each attempt includes one measurement. Measurement, reset/repreparation,
feed-forward, Clifford cost, physical QEC and runtime remain unpriced.

## Verification and bounds

Existing /Users/mar/codex-work/logique/.venv/bin/python (3.10.22) only.
All calls set PYTHONDONTWRITEBYTECODE=1, PYTHONPATH=$PWD/src resolving
to this REVIEW checkout, LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl,
and LOGIQUE_NATIVE_EXECUTABLE=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis.
OMP/OpenBLAS/MKL/VECLIB threads=1. Native never ran. The loader below
explicitly imports the candidate file by absolute spec and asserts
both review core and candidate module paths; no source copy or root
integration was needed.

- Candidate suite: embedded loader, then pytest.main with -q,
  -p no:cacheprovider and candidate/tests/test_rus_accounting.py.
  **100 passed in 0.08s**, no skips/deselections. Supervised wall
  0.260915s; child RSS 43,728,896 bytes.
- Independent verifier below: **1,304 checks, 56 invalid-input
  rejections, 36 exact program distributions**, n,j=0..2,c=0..3.
  Also cap moments 0..20 and n=0,1,2,5 / j=0,1,2,7 /
  c=None,0,1,7 grids. Largest phase-sensitive entrywise residual
  5.551115123125783e-15 at tolerance 2e-13, without phase fitting.
  Supervised wall 0.155428s; child RSS 36,093,952 bytes.
  Wrong inverse order/repeated-prefix faults are detected.
  Full-rank joint-reference density matrices and complete capped
  instruments are covered; largest dense matrix 8x8 (three qubits),
  vectors <=3 qubits.
- python -m black --check on both absolute candidate paths: pass,
  0.272197s.
- python -m ruff check --no-cache on both absolute candidate paths:
  pass, 0.072664s.
- python -m mypy --cache-dir=/dev/null --follow-imports=skip on
  candidate module: pass one file, 0.615075s. Not full configured mypy.
- Protected hashes/external gitlinks unchanged; review whitespace
  checked before commit.

All numerical subprocesses sequential, external timeout 60 seconds each,
**total numerical wall under one second**, below 180s. Static subprocess
timeouts 30s. Maximum recorded child RSS 97,206,272 bytes, below 8 GiB;
this is measured high-water evidence, not OS aggregate enforcement.
No build/install/sync, wider simulation, full suite, notebook, historical
replay, static compiler tests or saved-static-artifact regeneration.

Failures retained: ps sandbox denial; broad read outputs truncated and
replaced with bounded full-document chunks/focused parsed manifest reads;
one review-artifact update initially had a JavaScript template syntax
error before any mutation, then was rewritten. No numerical/assertion/
static failure or timeout occurred. Initial Git staging was sandbox-denied
when creating the shared worktree index.lock; the subsequent explicit-path
commit attempt could not find the unstaged file. Scoped Git escalation is
required because worktree metadata lives outside the writable checkout;
scoped staging then succeeded, with no automatic approval rejection.
Predecessor Ruff E741 was corrected
before commit and preserved in saved evidence. Green tests alone do not
admit the contract: the proof and explicit assumptions above are required.

## Exact identities and preservation

Candidate hashes measured before and after review are identical:

| File | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| src/logique/benchmarks/rus_accounting.py | c56af0fa743ba6a58e622a7ab5614d983bf4e0eed532256b6ddc967e65fb2b44 | c56af0fa743ba6a58e622a7ab5614d983bf4e0eed532256b6ddc967e65fb2b44 |
| tests/test_rus_accounting.py | 40837375ff6448ca8ad6cca8ed70af3b69bd2199beae62e1a8e6f4c14fcd5225 | 40837375ff6448ca8ad6cca8ed70af3b69bd2199beae62e1a8e6f4c14fcd5225 |
| RUS_LEDGER_CHECKPOINT.md | 914595b38c963fde65cf7ca3bf3ff0e462a1ddb29d8006def6339c416ed9e89c | 914595b38c963fde65cf7ca3bf3ff0e462a1ddb29d8006def6339c416ed9e89c |

Supporting hashes unchanged:

| Artifact | SHA-256 |
| --- | --- |
| Saved candidate events.jsonl | 3b472ab48a9a90da326c95413fed56fe817d30b71f72dc790dcbd674a1da93fb |
| Saved candidate result.json | 03736a419e5560df3c737446fc6a92b1e64fd014dd5fa26284d9442a331045ee |
| Server manifest | c74a753572d2fc1f5f947684f5fc5fc3d5107b30e9f1de212d7dfc95dd954dbd |
| Rotation-admission batch | 06dff702ed09059f523a6c51e6c0e8fcabadd2501642ce7e081e4d48970fda08 |
| Static-pilot triage batch | 126b2ce0eb03ded0ec5554d0f2cc248e81ce2994c3d797dab0212588f2613476 |
| Task 6 critical review | 9a9ec564b3dc4e4508061723386bf45dc22e5c74792d6043e6bb572ead020f7a |
| Static pilot admission | f357e2b0f024b1a61f46b524507c6f929da36b9cc55c91ff5334f46a791807db |
| Rotation admission | 01776d3dcc4527d7914aa1893db18eea336b76ad3518071b83eb71ce2b1c4c2d |
| Private admitted binary | 6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a |
| Old root binary | ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa |
| Root user README | 73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c |

All **766** protected paths match: regular tracked review/candidate files
(excluding this review), extant absolute paths from static-triage
preservation-before.json, rotation prototype directory, server nested-history
directory, assigned batches/manifest/root admission, both binaries, root
README and three candidate-attempt evidence files.
SHA-256 of json.dumps(path_to_sha256,sort_keys=True).encode() is
9a2b438ac326fd7175fe7a982412a23255f7ed020db3a599f7b00f16ddbb0b3b
before and after. SHA-256 of git ls-files --stage external is
c3fb8f6d6965ff6084dc71c2886070afcd2517473c07b025bae305c843c8e303
before and after. README edits, prototypes, archives, nested histories,
lockfile and pins are preserved. No saved static FT artifact was written.

Static FT source/tests retain hashes
5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595 /
88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77
for rotation, and
bc1ea4a1955d517f59c178d36d616ac67123e6e31093a8b81859534e01167c16 /
66c02665daec6f2d3b9e55c15ff455f9c70e2edb64844d6e83990459f977fe5a
for static harness. Its numerical norm-aware contract, <=64-epsilon
one-qubit matrix defect, precision floor, bounded SK/recursive restrictions
and caller obligations (clean oracle, mapping, signed S0, restoration,
explicit lowering, actual inverse and phases) remain binding. No interval
certificate, ideal-amplitude guarantee or broader admission is added.

## Next action and resumption

Dispatcher alone releases this completed review to existing
coordinate-rus-1025083656. Coordinator must triage both checkpoints,
verify these exact bytes/commits, preserve this decision and integrate
only the reviewed correctness files on its integration branch. Keep
review/audit and any build/metrics changes separate. No correction is
required for the present analytical ledger. Changed bytes or scope require
bounded correction and independent re-review with explicit differences
and counterexamples. This worker performs no root integration, queue
mutation or push; no duplicate job is needed.

On completed-review resumption verify the committed artifact, candidate
commits/hashes and clean review worktree, then return outcome=complete.
Do not repeat tests/review or launch anything. Dynamic implementation,
observed costs, quantum control, graph break-even and the full manuscript
evidence gate remain outstanding and excluded.

## Independently written bounded verifier

The code below loads the exact candidate explicitly while PYTHONPATH remains
the review worktree's src. No candidate test helpers are imported.

```python
from pathlib import Path
import importlib.util, sys
import logique, logique.benchmarks
assert Path(logique.__file__).resolve().parent == Path.cwd()/'src/logique'
candidate=Path.cwd().parent/'rus-ledger'
name='logique.benchmarks.rus_accounting'
spec=importlib.util.spec_from_file_location(name,candidate/'src/logique/benchmarks/rus_accounting.py')
rus=importlib.util.module_from_spec(spec)
sys.modules[name]=rus
spec.loader.exec_module(rus)
logique.benchmarks.rus_accounting=rus
assert Path(rus.__file__).resolve() == candidate/'src/logique/benchmarks/rus_accounting.py'

import hashlib, itertools, math, time
from fractions import Fraction as F
import numpy as np

start = time.monotonic()
assert hashlib.sha256(Path(rus.__file__).read_bytes()).hexdigest() == 'c56af0fa743ba6a58e622a7ab5614d983bf4e0eed532256b6ddc967e65fb2b44'
checks = 0
max_error = 0.0
def close(a, b):
    global checks, max_error
    error = float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    max_error = max(max_error, error)
    assert error < 2e-13, error
    checks += 1
def eq(a, b):
    global checks
    assert a == b, (a, b)
    checks += 1
I = np.eye(2, dtype=complex)
X = I[::-1]
Z = np.diag([1, -1])
H = (X+Z)/math.sqrt(2)
T = np.diag([1, (1+1j)/math.sqrt(2)])
# Different tensor ordering from candidate tests: |a,h>, a is high.
CX = np.block([[I, np.zeros((2,2))], [np.zeros((2,2)), X]])
trial = np.eye(4, dtype=complex)
for gate in (np.kron(H,I), np.kron(T,I), CX, np.kron(H,I),
             CX, np.kron(T,I), np.kron(H,I)):
    trial = gate @ trial
K0, K1 = trial[:2,:2], trial[2:,:2]
U = (I+1j*math.sqrt(2)*X)/math.sqrt(3)
alpha = (1-1j)*math.sqrt(3/8)
beta = (1+1j)/math.sqrt(8)
close(trial.conj().T@trial, np.eye(4))
close(K0, alpha*U); close(K1, beta*I)
close(K0.conj().T@K0+K1.conj().T@K1, I)
close(K0.conj().T@K0, .75*I); close(K1.conj().T@K1, .25*I)
close(Z@U@Z, U.conj().T)
# Explicit Clifford/T implementation of CH, scalar phases cancel.
C = (I+1j*X)/math.sqrt(2)
B = C@T@C.conj().T
CZ = np.diag([1,1,1,-1])
CH = np.kron(I,B) @ CZ @ np.kron(I,B.conj().T)
close(CH, np.block([[I,np.zeros((2,2))],[np.zeros((2,2)),H]]))
E = np.kron(X,I) @ CH @ np.kron(np.diag([1,-1j]),I)
V = E @ np.kron(U,I)
V_columns = np.array([[1,1,-1j/math.sqrt(2),-1j/math.sqrt(2)],
 [1,-1, -1j/math.sqrt(2),1j/math.sqrt(2)],
 [1,0,1j*math.sqrt(2),0], [0,1,0,1j*math.sqrt(2)]])/math.sqrt(3)
close(V,V_columns); close(V.conj().T@V,np.eye(4))
close(V[:,0],[1/math.sqrt(3)]*3+[0])
Ei = np.kron(np.diag([1,1j]),I) @ CH @ np.kron(X,I)
close(Ei,E.conj().T)
# General full-rank mixed input entangled with a reference; at most 3 qubits.
rng=np.random.default_rng(20261025)
M=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8))
rho=M@M.conj().T; rho/=np.trace(rho)
for failures in range(5):
    phase=beta**failures*alpha
    fwd=E @ np.kron(K0@np.linalg.matrix_power(K1,failures),I)
    inv=np.kron((Z@K0@Z)@np.linalg.matrix_power(Z@K1@Z,failures),I) @ Ei
    close(fwd,phase*V); close(inv,phase*V.conj().T)
    close(inv@fwd,phase**2*np.eye(4))
    for op,target in ((fwd,V),(inv,V.conj().T)):
        joint=np.kron(op,I)
        ref=np.kron(target,I)
        branch=joint@rho@joint.conj().T
        close(branch,abs(phase)**2*ref@rho@ref.conj().T)
        close(np.trace(branch),abs(phase)**2)
close(np.kron(Z@K1@Z,I)@Ei,beta*Ei)
# Fault-sensitivity checks: reject wrong inverse order and repeated prefix.
assert np.max(abs(Ei@np.kron(U.conj().T,I)-V.conj().T)) > .1
assert np.max(abs(np.kron(Z@K0@Z,I)@Ei@np.kron(Z@K1@Z,I)@Ei
                  -alpha*beta*V.conj().T)) > .1
# Full capped mathematical instrument for one vertex, j=1, cap=2.
# This is finite Kraus algebra, no dynamic circuit or retry runtime.
O=np.diag([1,-1,1,1]); S0=np.diag([1,-1,-1,-1])
W=V@S0@V.conj().T@O@V
schedule=[('F',None),('D',O),('B',None),('D',S0),('F',None)]
paths=[np.eye(4,dtype=complex)]; abort=[]
for kind,gate in schedule:
    if kind=='D':
        paths=[gate@v for v in paths]
        continue
    good=[]; prefix=np.eye(4) if kind=='F' else Ei
    success=np.kron(K0 if kind=='F' else Z@K0@Z,I)
    fail=np.kron(K1 if kind=='F' else Z@K1@Z,I)
    suffix=E if kind=='F' else np.eye(4)
    for path in paths:
        for r in (0,1):
            good.append(suffix@success@np.linalg.matrix_power(fail,r)@prefix@path)
        abort.append(np.linalg.matrix_power(fail,2)@prefix@path)
    paths=good
s=15/16
close(sum(p.conj().T@p for p in paths+abort),np.eye(4))
close(sum(p.conj().T@p for p in paths),s**3*np.eye(4))
close(sum(p.conj().T@p for p in abort),(1-s**3)*np.eye(4))
good_rho=sum(np.kron(p,I)@rho@np.kron(p,I).conj().T for p in paths)
close(good_rho,s**3*np.kron(W,I)@rho@np.kron(W,I).conj().T)
# Exact probability generating polynomials for the complete serial schedule.
# Keys (attempts, vertex_T, external_T); values exact probability.
# Failed paths stop, and are accumulated separately.
def distribution(n,j,c):
    sched=['F']*n
    for _ in range(j):
        sched += ['O']+['B']*n+['Z']+['F']*n
    live={(0,0,F(0)):F(1)}; stopped={}
    def add(out,key,p): out[key]=out.get(key,F(0))+p
    for op in sched:
        nxt={}
        for (a,t,e),p in live.items():
            if op in ('O','Z'):
                add(nxt,(a,t,e+(F(7,3) if op=='O' else F(11,2))),p)
            else:
                # Enumerate all binary trial words of fixed cap, then fold
                # identical first-success events via their unused suffix.
                for word in itertools.product((0,1),repeat=c):
                    prob=p
                    for bit in word: prob*=F(3,4) if bit==0 else F(1,4)
                    r=next((i+1 for i,b in enumerate(word) if b==0),None)
                    if r is None:
                        add(stopped,(a+c,t+2*c+(2 if op=='B' else 0),e),prob)
                    else:
                        add(nxt,(a+r,t+2*r+2,e),prob)
        live=nxt
    return live,stopped
program_cases=0
for n,j,c in itertools.product(range(3),range(3),range(4)):
    live,dead=distribution(n,j,c); both=dict(live)
    for key,p in dead.items(): both[key]=both.get(key,F(0))+p
    pgood=sum(live.values(),F(0)); eq(sum(both.values(),F(0)),1)
    a=rus.analytical_ledger(n,j,cap=c,oracle_t=F(7,3),zero_reflection_t=F(11,2))
    eq(a.program_failure_probability,1-pgood)
    eq(a.stop_expected_attempts,sum(p*x[0] for x,p in both.items()))
    eq(a.stop_expected_vertex_t,sum(p*x[1] for x,p in both.items()))
    eq(a.stop_expected_total_t,sum(p*(x[1]+x[2]) for x,p in both.items()))
    if pgood:
        mean=sum(p*x[0] for x,p in live.items())/pgood
        variance=sum(p*(x[0]-mean)**2 for x,p in live.items())/pgood
        eq(a.success_expected_attempts,mean)
        eq(a.success_variance_attempts,variance)
        eq(a.success_expected_vertex_t,sum(p*x[1] for x,p in live.items())/pgood)
        eq(a.success_variance_vertex_t,4*variance)
        eq(a.success_expected_total_t,sum(p*(x[1]+x[2]) for x,p in live.items())/pgood)
    else:
        eq((a.success_expected_attempts,a.success_variance_attempts,
            a.success_expected_vertex_t,a.success_variance_vertex_t,
            a.success_expected_total_t),(None,)*5)
    for x in both:
        assert x[0]<=a.capped_attempts_upper_bound
        assert x[1]<=a.capped_vertex_t_upper_bound
    program_cases+=1
for c in range(21):
    dist=[(r,F(3,4)*F(1,4)**(r-1)) for r in range(1,c+1)]
    all_events=dist+[(c,F(1,4)**c)]
    mean=sum(r*p for r,p in all_events)
    var=sum((r-mean)**2*p for r,p in all_events)
    m=rus.retry_moments(c)
    eq(m.expected_attempts,mean); eq(m.variance_attempts,var)
    eq(m.expected_trial_t,2*mean); eq(m.variance_trial_t,4*var)
    eq(m.failure_probability,F(1,4)**c)
    if c:
        s=sum(p for _,p in dist)
        cm=sum(r*p for r,p in dist)/s
        eq(m.expected_attempts_given_success,cm)
        eq(m.variance_attempts_given_success,sum((r-cm)**2*p for r,p in dist)/s)
for n,j,c in itertools.product((0,1,2,5),(0,1,2,7),(None,0,1,7)):
    a=rus.analytical_ledger(n,j,cap=c)
    L=n*(1+2*j)
    eq(a.unbounded_expected_attempts,F(4*L,3))
    eq(a.unbounded_variance_attempts,F(4*L,9))
    eq(a.unbounded_expected_vertex_t,F(14*L,3))
    eq(a.unbounded_variance_vertex_t,F(16*L,9))
    eq(a.unbounded_expected_total_t,None if j else F(14*L,3))
    q=F(0) if c is None else F(1,4)**c
    eq(a.program_failure_probability,1-(1-q)**L)
    eq(a.program_failure_union_bound,min(1,L*q))
    eq(a.retry_ancillas,int(n>0)); eq(a.data_qubits,2*n)
    eq(rus.analytical_ledger(n,j,cap=c,retry_ancillas='parallel').retry_ancillas,n)
    eq(a.forward_vertex_invocations,n*(1+j)); eq(a.inverse_vertex_invocations,n*j)
# Validation beyond candidate fixtures.
invalid=0
def rejects(fn,error):
    global invalid
    try: fn()
    except error: invalid+=1
    else: raise AssertionError('invalid argument accepted')
for key in ('n','j','k','cap'):
    for value in (False,-2,2.0,F(2),'2',complex(2),float('nan'),float('inf')):
        kw={'n':1,'j':1,key:value}
        rejects(lambda:rus.analytical_ledger(**kw),ValueError)
for key in ('oracle_t','zero_reflection_t'):
    for value in (True,-2,F(-1,3),2.0,float('nan'),float('inf'),'2'):
        rejects(lambda:rus.analytical_ledger(1,1,**{key:value}),ValueError)
for k in (0,1,2,4,5,8):
    rejects(lambda:rus.analytical_ledger(1,0,k=k),NotImplementedError)
for arg in ('quantum_controlled','state_dependent_success','graph','optimal_j'):
    rejects(lambda:rus.analytical_ledger(1,1,**{arg:True}),TypeError)
eq(set(rus.UNPRICED),{'measurement','reset/repreparation','classical feed-forward',
                     'Clifford gates','runtime','physical QEC'})
eq(rus.analytical_ledger(1,1,cap=0).stop_expected_total_t,0)
eq(rus.analytical_ledger(0,1,cap=0).stop_expected_total_t,None)
print({'checks':checks,'invalid_rejections':invalid,'enumerated_program_cases':program_cases,
       'max_entrywise_error':max_error,'wall_s':time.monotonic()-start,
       'largest_dense_qubits':3,'largest_vector_qubits':3})
```
