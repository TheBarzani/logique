# Independent restoring-MCX review

**Bounded review COMPLETE. ADMITTED for the exact source/test identities below,
only for the declared restoring `clean_tree` / `fresh_zero` subset and the
bounded semantic and serialization contract in this review.** No blocker was
found for that subset. This is not full controls completion, a performance
result, FT/RUS admission, or paper approval. The full paper remains unfinished.

## Identity, ownership and intake

Assigned task: `restoring-mcx-review-1025125442`. Reviewer branch:
`codex/coloring-restoring-mcx-review-1025125442`, base `a57e84f`.
Reviewer worktree:
`/Users/mar/codex-work/logique/dump/1025125442-qpy-coordinator-triage/worktrees/restoring-mcx-review`.
Only `RESTORING_MCX_REVIEW.md` is a tracked deliverable. No candidate source,
root integration file, queue/state, dependency, archive or prior checkpoint was
edited. There was no prior completed own handoff: the reviewer worktree was clean
at the assigned base, with no review file. The numerical review completed in the first bounded attempt; a second dispatcher
turn resumed only the interrupted commit/handoff.

Read-only candidate: sibling `restoring-mcx` worktree, branch
`codex/coloring-restoring-mcx-1025125442`, final HEAD `f5407a3`.
Its owned correctness commits are `ea3f4e80488a3b1f63c01ae0b65652e67b55262f`
and `e3a295ed558bc1b6a136691616313eaff3f6aa53`; representation/metric ledger
commit is `0eacb132c610a54d0c2da94baa7793ab7a0353ff`. The final commit records
its completion checkpoint. Integration belongs to the queued coordinator.

| Exact candidate file | SHA-256, unchanged before/after review |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `a811e028b82b4ac1ddf01fa57e6449f5065a797302d1f676e1b4e67bd34511e5` |
| `tests/test_coloring_study.py` | `64166bd9eb17ba7d8190815164cbb7e670331561d225b913c77245f2efddd3f9` |
| Reused, unchanged `src/logique/benchmarks/costs.py` | `42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8` |

Git and dispatcher state were inspected first. The entire 39-job queue and all
32 current state entries were inspected, including blocked predecessors.
`restoring-mcx-1025125442` is complete; this review is the sole recorded running
job; `coordinate-restoring-mcx-1025125442` is queued exactly once with finished
predecessor triage. Low-T implementation and its alias coordinator have unrelated
blocked records; these were not overwritten or inferred complete. The completed
stage-controls/QPY coordinators were not redispatched. Manifest active-job/usage
snapshots are historical; durable dispatcher state takes precedence.

Read AGENTS.md, CLAUDE.md, the full 646-line
`docs/coloring-paper-revamp-codex-plan.md`, implementation audit including current
root additions, architecture, rotation batch, current QPY batch, root QPY
semantic review/admission/representation ledger, server checkpoint manifest,
assigned implementation prompt, actual candidate checkpoint, changed source/tests,
and relevant unchanged costs, baseline and synthesis-wrapper implementations.
The full manifest was parsed and its 1,345 leaves/12 historical integration
batches inventoried. This does not re-admit historical evidence by its status.
Latest no-launch/no-build/no-install instructions supersede older setup guidance.

Local evidence RUN:
`dump/1026024754-restoring-mcx-review/` in the reviewer worktree. Intake snapshots,
command logs, independent scripts/results and preservation ledger are retained.
No agent/model/Codex/API/paid fallback/hardware/push/publishing was launched.

## Declared admission and exclusions

Opt-in configuration requires both
`mcx_decomposition="clean_tree"` and `mcx_workspace="fresh_zero"`. Configured
null/missing/mismatched policies fail preflight; omission preserves the default.
Direct `assemble_case` uses `None` as its omission sentinel, so explicitly passing
both Python keyword arguments as `None` also selects the default; it is not an
opt-in. The worker's blanket null-rejection wording must be understood as the
configuration contract, not a distinct direct-API sentinel contract.

Input limits are original k <= 8, at most 21 data wires, iterations 0..2.
Source MCX controls are 3..20; definition operation width <=21, depth <=32,
visited operations <=100000 per resolver. Input-dependent limits are checked for
all input files before a run directory is created. Unsupported emitted forms
fail per case, preserving partial artifacts with zero failed-case rows.
CCX and RCCX can remain primitives; final components have <=3-wire operations
and no >=3-control X gate. The claimed metric level is explicit restoring-MCX,
not Clifford+T or a universal two-qubit lowering.

Admission covers the clean-scratch substitution theorem for these emitted
clean-tree templates, actual inverse/scalar/ordered-wire assembly, role-disjoint
fresh scratch, and QPY fidelity of bound quantum-only emitted standard definitions.
The graph evidence covers the fixtures below with the pinned existing native
foundation binary and all five native/four baseline methods where supported.
The substitution theorem transfers an already valid source computation; it
cannot make an unverified backend predicate valid. Sampled source validation
above the exhaustive limit is still sampled. No general exhaustive correctness
claim for every graph with 21 inputs follows from these tests.

Unsupported policies stay unsupported: `noaux_v24`, `gray_code`, `1_clean_b95`,
`n_clean_m15`, `n_dirty_i15`, `1_clean_kg24`, `1_dirty_kg24`, `2_clean_kg24`,
`2_dirty_kg24`, `throwaway_tree`, unknown policies, and any implicit borrowing.
No all-policy 3..20-control study or Dutta implementation is admitted here.
Dirty initial decomposition scratch, dirty initial backend workspace, arbitrary
opaque/unbound/dynamic/classical operations, adversarially modified standard
classes, and unreviewed wider lowering/transpiler claims remain excluded.

The primary restored components and their saved representations are covered.
Common-basis saved counts and fidelity checks do not certify general wider
original-to-transpiler equivalence or live-workspace bounds after arbitrary
optimization/routing. Workspace peaks describe the declared construction,
not a measured optimized/routed schedule. No routing/precision/resource-control
framework, structure-study integration, protocol freeze, complete comparison
study, historical pilot repair or superiority claim is admitted.

## Independent semantic derivation

For a clean-tree prefix P, every internal RCCX has a fresh zero target. Its
permutation computes a conjunction into that target while multiplying the basis
column by a phase. P is monomial, preserves the original controls, and does not
involve the final external target. It maps
`|c,t,0> -> exp(i phi(c)) |c,t,g(c)>`.
The final exact CCX changes only t, using the last two conjunction values.
Their conjunction is the conjunction of all controls, including the carried
odd wire at an odd layer. Since neither c nor g(c) changes in that final step,
P's actual inverse restores every internal target and cancels the same phase.
The full matrix on clean scratch is exactly MCX tensor zero-restoration, for
both target sectors. This is an equality of basis columns with phases, so it
extends to arbitrary data superpositions and entanglement with an untouched
reference by linearity. It does not assert correctness on dirty scratch.

Independent direct <=3-wire operators verify the actual RCCX convention:
`|011> -> i|111>`, `|111> -> -i|011>`, `|101> -> -|101>`, other columns unchanged
(Qiskit little-endian basis labels). Actual inverse definitions, including their
H/T/CX expansion, are retained. Open controls are X conjugations of closed MCX.
The independent scalar checks propagate actual local matrices, not gate-name
phase guesses. All 3..20-control sizes were exercised; 3 controls use all eight
polarities, 4..20 use 0, 1 and all-ones control states. Data/target columns are
exhaustive through five controls, with five specified witnesses per polarity at
larger sizes. Two existing spare wires start nonzero and remain untouched;
fresh scratch alone is appended and restored. The largest representation has
41 wires as a circuit plus integer/scalar state, never a dense quantum array.

A retained minimal exclusion witness uses three controls, target wire 3,
scratch wire 4, input integer 20 (`c0=c1=0,c2=1,t=0,scratch=1`). The emitted
clean-tree maps it to 28, with unit phase within floating tolerance. Ideal MCX
would leave it at 20. Thus the zero-scratch precondition is substantive.

Each source block is recursively resolved with scalar phases and ordered local
wire embeddings. Closed standard MCX is retained until the single clean-tree
lowering call; wider other gates are resolved first. A second bounded resolution
exposes actual inverse definitions, and a final check rejects residual wide
gates. Canonical ordered QuantumCircuit registers preserve the operation sequence
and phase while avoiding the installed mixed Qubit/AncillaQubit readback failure.
There is no repeat-until-expanded loop or independent resynthesis of mirrors.
Trusted standard class/parameters/control-state semantics are the base case of
this recursive argument. Arbitrary spoofed standard objects are outside it.

Baselines lower `initializer; compute` once, lower the final conjunction once
with a distinct pool, and use the actual emitted prefix inverse. This matches
the admitted clean baseline action on its specified initial workspace. Constant
adapters use their actual raw circuit; an empty constraint list is not assumed
true. Native raw computation keeps its original raw contract and may retain
workspace or phase. For verified arbitrary-target clean XOR, X-H/raw/H-X gives
`(-1)^predicate` and restores the kickback target. For conservative wrappers,
chronological raw/Z/actual-raw-inverse implements C† Z C; a definite computed
predicate is marked and all raw workspace and phases are uncomputed. Raw is
never relabeled a clean phase oracle merely because lowering restores MCX scratch.

A is built from original k and lowered once. The clean-scratch subspace is
invariant under the lowered unitary A; its restriction there is the original
unitary, so its actual inverse also preserves that subspace. Diffusion executes
actual A inverse, signed zero reflection, actual A. The middle block is
`-X^n MCZ X^n`, giving +1 on zero and -1 elsewhere. Hence the matrix is
`A(2|0><0|-I)A†` with the positive Grover sign, including all scalar phases.
The inverse need not be reconstructed from the original state amplitudes.

Search embeds A once, then the exact saved/lowered oracle and diffusion j times.
Data uses the explicit backend input order; scratch pools are outside every
backend wire. Raw, A and S0 pools are disjoint; baseline prefix/mark pools are
also separate. Every MCX scratch pool returns to zero at each gate boundary,
so it is zero at each component/search boundary. The original k preparation is
a product of verified two-/three-wire k3/k5 blocks in the fixtures; R3 drops
domain checks only in the predicate. Complete and edge-only predicates agree on
valid-code preparation support, and the matching reflection preserves that
support. Deliberately injected preparation-MCX fixtures test assembly/inverse
reuse only, not the original uniform-valid-color preparation claim.

## Workspace and metrics assessment

`costs.decompose_mcx(..., clean_wires=())` allocates the maximum single gate's
n-2 need for a block and reuses it only after restoration. No data/output/flag/
kickback/unknown backend wire enters the scratch list. The baseline prefix and
mark allocate separately, but their live capacities do not add: the prefix's
scratch is clean before marking and before its actual inverse. Similarly A,
S0 and oracle pools execute sequentially. Thus the recorded MCX live upper bound
is `max(raw_peak, A_peak, S0_peak)` for j>0 and A_peak for j=0. Reserved width
still includes unused pools at j=0. Per-gate scratch requirements are not summed.
These are construction capacities, not measurements of nonzero occupation,
optimal workspace, backend liveness or process memory. Full live-workspace and
peak-memory fields correctly remain unavailable/null. Native combined timing
remains nested in synthesis; mapping/optimization splits are not fabricated.

All 2,100 final saved rows were independently recounted from QPY using actual
operation maps and direct wire-dependency clocks and reconciled with CSV.
All 210 complete cases' 1,050 primary components were independently reassembled
and compared with those exact saved QPY files by ordered definitions and scalar
phase. The six sb_original multi-higher-neighbor exclusions are retained.
No final failed case appears in those 2,100 rows. The earlier 18 genuine QPY
IndexError cases retain their partial artifacts and zero failed-case rows.
They are not repaired or admitted retroactively.

All 480 saved omitted-option artifacts are byte-identical to the preserved
`a57e84f` reference artifacts, with identical width/gates/depth/maps. Static
inspection confirms opt-in defaults and the resolver's default path are
unchanged. This is saved-circuit/metric compatibility; measured timings and
source provenance hashes naturally change. Against those same 480 rows,
opting in changes 196 widths, 162 gate maps and 162 gate/depth totals, independently
recomputed here. These are decomposition/representation changes, not advantages.
The worker's separately committed representation ledger SHA-256 is
`c84e28eb807247289bc5e447225360aaddd6c78012ef82d63c07782c07bd87c7`.
No historical table was changed or newly admitted.

## Evidence and resource limits

- Candidate regressions: **164 passed, 31 deliberately deselected, zero skips**.
  Exclusions retained: 27 `matching_preparation_diffusion_and_search`, one
  `r3_keeps_asymmetric_k5_preparation`, three
  `native_asymmetric_constant_r3_and_complete_search`. No wide dense replacement.
- Independently written main harness: 117 semantic cases, 11,747 scalar column
  evaluations, 1,112 ordered composition checks, 1,113 bounded Operator calls,
  90 bounded statevector evaluations/checks, 2,100 recounted rows and 480 exact
  default artifact comparisons. Operator calls include local contractions and
  reference matrices; they are not 1,113 independent full-circuit equivalences.
- Additional independent harness: 210 saved primary cases / 1,050 components,
  j=0 construction/peak checks; 15 explicitly forced native conservative-wrapper
  cases across all five methods and R1/R2/R3 at j=2; 360 scalar column evaluations,
  1,186 composition checks, 866 bounded Operator calls and 32 statevector checks.
  The last 32 test every data basis column of a four-data-wire nested open-MCX A
  and its actual inverse in the complete five-wire physical preparation register.
  All three search scratch pools are nonempty and disjoint in that fixture.
- Semantic graph fixtures: noncontiguous-label edge k3 and edge k5, isolated k5,
  unsatisfiable triangle k2, and constant-false self-loop k3 (baseline coverage).
  R1/R2/R3, both XOR-target sectors, positive and negative independent predicates,
  actual raw phases, signed diffusion and complete search are exercised. Tiny
  complete physical search statevectors match independent amplification recurrence.
  Wider search uses the primitive proof plus ordered component composition.
- Largest observed entrywise numerical error is **1.8356350271804544e-14**;
  independent assertion tolerance is 3e-11, without global-phase alignment.
  Additional harness maximum is 1.6081975806755164e-15. Floating evidence is not
  an interval certificate or general ideal-amplitude guarantee.
- Relevant candidate Black/Ruff checks and review Git whitespace checks pass.
  No full suite/mypy/build/notebook/historical replay/routing/FT work is claimed.

The environment is existing `/Users/mar/codex-work/logique/.venv/bin/python`,
Qiskit 2.1.1 and NumPy 2.2.6. Every numerical command imports the sibling
candidate through explicit PYTHONPATH and asserts the resolved module path.
`LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl`.
The explicit manifest-admitted foundation executable is
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`,
SHA-256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
The untouched root old binary remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.
No compiler, synchronization, installation or dependency change occurred.

Numerical pipelines were sequential with synchronous native calls, single
BLAS/OpenMP/Accelerate threads, timeout <=120s per supervised command and a
300s cumulative supervisor budget. Dense operators <=4 qubits; full statevectors
<=5. Wider tests use <=3-wire local matrices and integer/scalar propagation or
ordered compositional reasoning. All five supervised numerical/static commands
total **29.049908 seconds**; largest command **15.389174 seconds**; largest
recorded child RSS **217,464,832 bytes**, below 8 GiB for these fixed fixtures.
This is measured child RSS, not an enforced OS aggregate memory limit or a claim
of complete process visibility. Definition visitation limits do not bound all
Qiskit/native internal allocation before a definition is returned. No general
resource guarantee for every accepted input is inferred.

`RUN/commands.jsonl` records actual argv, cwd, environment, exits, times and RSS.
The exact regression command is:

```sh
/Users/mar/codex-work/logique/.venv/bin/python dump/1026024754-restoring-mcx-review/supervisor.py candidate-tests /Users/mar/codex-work/logique/.venv/bin/python -m pytest ../restoring-mcx/tests/test_coloring_study.py -k 'not matching_preparation_diffusion_and_search and not r3_keeps_asymmetric_k5_preparation and not native_asymmetric_constant_r3_and_complete_search' --basetemp=dump/1026024754-restoring-mcx-review/test-artifacts -p no:cacheprovider -q
```

The two independent commands replace the supervisor label and remaining argv
with `independent python RUN/independent.py` or `additional python RUN/additional.py`,
using the same absolute research interpreter. The supervisor sets the environment
above. Do not repeat these on completed-task resumption. For a separate authorized
replay, use a fresh correctly named run directory and update the report paths;
the harness deliberately preserves its fixed evidence targets.

## Failures, preservation and next action

All review numerical/static commands passed. Initial `git add` was sandbox-denied
at the shared worktree `index.lock`; narrowly scoped automatic escalation
successfully staged only this review. Execution was interrupted after staging,
before commit (durable dispatcher record: `included_quota_exhausted`). On
resumption Git, the entire unchanged queue/current state, exact candidate and
evidence hashes were rechecked; no numerical jobs or tests were repeated. No
automatic approval rejection occurred. Expected negative checks retained:
11 unsupported-policy requests; opaque, unbound, classical and >20-control
rejections; opaque-operation and corrupted-readback-scalar mixed-success runs.
Both mixed-success runs retain failed j1 artifacts and exactly the five rows of
the successful j0 case, with no failed-case rows. The dirty-scratch counterexample
is an explicit contract exclusion, not a clean-subspace failure.

The worker's original failures remain preserved: initial scalar-harness and
Statevector-aliasing mistakes; unresolved inverse-RCCX failures; metric-level
accounting assertions; missing isolated reference runner; 18 real mixed-register
QPY readback IndexErrors; and failed-export postprocessor capture alignment.
Only the final corrected candidate is admitted. Its earlier passing counts alone
would not have admitted the failed serialization. No failing run was overwritten.

Read-only verification confirms all **250 reviewer intake identities**, all
**461 worker protected identities**, and **6,599 worker evidence-file hashes**.
README edits, prototype backups, archived results, nested histories, lockfile,
rotation source/tests and both binaries match their preserved identities;
external index/gitlinks remain unchanged. Queue SHA-256 remains
`6414beb946741b3a511c5593a02179ba54116266699f19b73a4214c6c9761879`.
Durable state has only this review running and the coordinator uniquely queued.
The review did not mutate dispatcher state. No scientific-failure correction is
needed inside this owned review slice.

**Next action:** release this completed bounded review to the already queued
`coordinate-restoring-mcx-1025125442`. The coordinator independently verifies
these exact identities and review scope, then accepts/integrates only the owned
correctness commits separately from representation/metric evidence, or records
a concrete blocker. Reviewer does not integrate, append jobs or push. Dispatcher
alone launches and pushes integration HEAD. On repeat, verify the completed
review/commit, hashes and unique handoff, then return COMPLETE without new
numerical checks, jobs or integration. Changed bytes or broader scope require
fresh review.

The existing rotation compiler admission remains exact-hash and limited to its
numerical/caller contract: rotations.py
`5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595`, tests
`88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77`.
This MCX review adds no interval certificate, ideal-amplitude guarantee, static
FT experiment approval, dynamic RUS admission or blanket paper approval.
Further policies, resource controls, affected older saved evidence, complete
studies, protocol freeze and the full research/manuscript scope remain unfinished.

## Evidence identities and executable independent checks

| RUN artifact | SHA-256 |
| --- | --- |
| `supervisor.py` | `eb59b5ce2d945753f245a6cb7ec96da7f25d114552cd5aafb6cf7eba0cc90358` |
| `independent.py` | `101d2c3fdcd445f2d0e210b194a70c91a75e7966e7651af7baa94507757a46a1` |
| `additional.py` | `bc800de6c46c3f9bf1692fb5aedd54c593da5ad344e3233f7c23188fcdfa1b3a` |
| `independent-results.json` | `d25b0e76c83095683d600b6c6dc2111e1c000127f35a7cee42a2194dd6f5c585` |
| `additional-results.json` | `f2016b462f8a9101fe82f211d9429e21b713dc91042557734f7a5d0b6d26b229` |
| `commands.jsonl` | `aa8d06440b4cade1095e65f8f17ba3e3559c408568225a3bf57c77de79e85e2d` |
| `preservation-ledger.json` | `37fc0504ff77460dafb614b47311d5f27b5cf170390188aa801073fee191c08a` |
| `intake.json` | `f35a45ce2d066519bb28689e918a1706c94843ca9fc9795f1e37130cf15e42a5` |

The following are the exact executed independent harnesses, retained inline so
the sole tracked review artifact preserves the substantive executable evidence.
They call candidate assembly/lowering as subjects under test; reference predicate,
local-matrix/scalar action, ordered-definition comparison, amplification,
recounting and failure assertions do not import candidate test helpers or its
verification interpreter. The signed middle block uses the candidate lowering
primitive after its separate clean-subspace proof and checks; it is not presented
as an independent implementation of that primitive. No wide dense object is used.

### independent.py

```python
"""Independent restoring-MCX review; no candidate tests/verification references."""
import ast, csv, hashlib, io, itertools, json, math, os, time
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import numpy as np
import qiskit
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Gate, Parameter
from qiskit.circuit.library import MCXGate, RCCXGate, StatePreparation
from qiskit.quantum_info import Operator, Statevector
from logique.benchmarks import coloring_study as s
from logique.coloring import ColoringProblem
R=Path(os.environ['REVIEW_RUN']); C=Path(os.environ['PYTHONPATH']).parent
assert Path(s.__file__).resolve()==C/'src/logique/benchmarks/coloring_study.py'
report=dict(cases=[],operators=0,statevectors=0,columns=0,composition=0,rows=0,rejections=[],max_error=0.0,versions={'qiskit':qiskit.__version__,'numpy':np.__version__})
def mat(q):
 assert q.num_qubits<=4
 report['operators']+=1
 return Operator(q).data

def close(a,b):
 err=float(np.max(abs(np.asarray(a)-np.asarray(b))));report['max_error']=max(report['max_error'],err)
 assert err<3e-11,err

def rt(q):
 f=io.BytesIO();qpy.dump(q,f);f.seek(0);return qpy.load(f)[0]

def key(o):
 return (o.base_class.__module__,o.base_class.__name__,o.name,tuple(complex(p) for p in o.params),getattr(o,'num_ctrl_qubits',0),getattr(o,'ctrl_state',None))

def flat(q):
 out=[];phase=0
 def walk(c,w,d=0):
  nonlocal phase
  assert d<=32
  phase+=float(c.global_phase)
  for it in c.data:
   o=it.operation;v=tuple(w[c.find_bit(b).index] for b in it.qubits)
   closed=getattr(o,'ctrl_state',None) in (None,(1<<getattr(o,'num_ctrl_qubits',0))-1)
   if o.base_class.__module__.startswith('qiskit.circuit.library.standard_gates.') and closed:out.append((key(o),v))
   else:
    assert o.definition is not None,o.name
    walk(o.definition,v,d+1)
 walk(q,tuple(range(q.num_qubits)))
 return out,np.exp(1j*phase)

def comp(a,b):
 assert a.num_qubits==b.num_qubits
 aa,p=flat(a);bb,r=flat(b);assert aa==bb,('composition',a.name,b.name)
 close(p,r);report['composition']+=1
 if a.num_qubits<=4:close(mat(a),mat(b))

# Compile actual short instruction groups into independently checked monomial maps.
# H/T/CX inverse-RCCX leaves are contracted as a <=3-wire unitary, never a wide state.
cache={}
def scalar_program(q):
 prog=[];i=0
 while i<len(q.data):
  it=q.data[i];o=it.operation;w=[q.find_bit(b).index for b in it.qubits]
  if isinstance(o,MCXGate):
   prog.append(('mcx',w,(o.num_ctrl_qubits,o.ctrl_state)));i+=1;continue
  group=[];support=[]
  for j in range(i,min(i+40,len(q.data))):
   it=q.data[j];v=[q.find_bit(b).index for b in it.qubits]
   support=list(dict.fromkeys(support+v));assert len(support)<=3,('local contraction',o.name,support)
   group.append((it.operation,v));sig=tuple((key(x),tuple(support.index(b) for b in vv)) for x,vv in group)
   if sig not in cache:
    local=QuantumCircuit(len(support))
    for x,vv in group:local.append(x,[support.index(b) for b in vv])
    m=mat(local)
    if np.all(np.sum(abs(m)>1e-11,axis=0)==1):
     idx=np.argmax(abs(m),axis=0);vals=m[idx,np.arange(len(m))];close(abs(vals),np.ones(len(vals)));cache[sig]=(idx,vals)
    else:cache[sig]=None
   result=cache[sig]
   if result is not None:
    prog.append(('local',support,result));i=j+1;break
  else:raise AssertionError('no monomial contraction')
 return prog,np.exp(1j*float(q.global_phase))

def scalar(program,b):
 prog,p=program
 for kind,w,op in prog:
  v=sum(((b>>k)&1)<<j for j,k in enumerate(w))
  if kind=='mcx':
   nc,cs=op;u=v^(1<<nc) if v&((1<<nc)-1)==cs else v
  else:idx,vals=op;u=int(idx[v]);p*=vals[v]
  for j,k in enumerate(w):b=(b&~(1<<k))|(((u>>j)&1)<<k)
 report['columns']+=1
 return b,p

def good(p,r,x):
 b=(p.colors-1).bit_length();v={a:(x>>(i*b))&((1<<b)-1) for i,a in enumerate(p.vertices)}
 return all(v[a]!=v[c] for a,c in p.edges) and (r=='R3' or all(z<p.colors for z in v.values()))

def tiny_templates():
 # Exact relative-phase table, independently from expected RCCX algebra.
 m=mat(RCCXGate());expected=np.eye(8,dtype=complex);expected[3,3]=expected[7,7]=0;expected[7,3]=1j;expected[3,7]=-1j;expected[5,5]=-1
 close(m,expected)
 for nc in range(3,21):
  # Exhaustive <=5 controls; wider explicit all-true/open/false witnesses.
  states=range(1<<nc) if nc==3 else (0,1,(1<<nc)-1)
  for cs in states:
   q=QuantumCircuit(nc+3,global_phase=.271);q.append(MCXGate(nc,ctrl_state=cs),list(reversed(range(nc+1))))
   lo,info=s._restoring_mcx_block(q);saved=rt(lo);comp(lo,saved)
   assert info['appended_ancillas']==nc-2 and info['clean_wires_used']==info['borrowed_dirty_wires']==0
   a=scalar_program(q);b=scalar_program(saved)
   values=range(1<<(nc+1)) if nc<=5 else (0,1,cs,cs|(1<<nc),(1<<(nc+1))-1)
   for x in values:
    start=x|(3<<(nc+1));aa,pa=scalar(a,start);bb,pb=scalar(b,start);assert aa==bb;close(pa,pb)
 # Superposition checks use 5 total wires; small logical target uses direct 4-wire operator.
 for cs in range(8):
  inner=QuantumCircuit(4,global_phase=.217);inner.append(MCXGate(3,ctrl_state=cs),[3,0,2,1])
  q=QuantumCircuit(4,global_phase=-.619);q.append(inner.to_gate().inverse(),[1,3,0,2])
  lo,_=s._restoring_mcx_block(q);lo=rt(lo)
  rng=np.random.default_rng(cs);v=rng.normal(size=16)+1j*rng.normal(size=16);v/=np.linalg.norm(v)
  expected=mat(q)@v;actual=Statevector(np.r_[v,np.zeros(16)].copy()).evolve(lo).data;report['statevectors']+=1
  close(actual,np.r_[expected,np.zeros(16)])
  close(Statevector(actual.copy()).evolve(lo.inverse()).data,np.r_[v,np.zeros(16)]);report['statevectors']+=1
 # Dirty scratch is explicitly outside the admitted identity; retain witness.
 q=QuantumCircuit(4);q.mcx([0,1,2],3);lo,_=s._restoring_mcx_block(q)
 b,p=scalar(scalar_program(lo),16|4);assert b!=(16|4);report['dirty_scratch_counterexample']={'input':20,'output':b,'phase':[p.real,p.imag]}

def semantic_cases():
 fixtures=[ColoringProblem((-7,20),((-7,20),),3),ColoringProblem((-7,20),((-7,20),),5),ColoringProblem((42,),(),5),ColoringProblem((2,8,90),((2,8),(8,90),(2,90)),2),ColoringProblem((42,),((42,42),),3)]
 for pi,p in enumerate(fixtures):
  for method,r in itertools.product(s.STUDY_METHODS,s.REGIMES):
   if pi==4 and not method.startswith('sb_'):continue
   try:original=s.assemble_case(p,method,r,iterations=1)
   except s.ExcludedCase:continue
   case=s.assemble_case(p,method,r,iterations=1,mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
   md=case.metadata;data=md['data_qubits'];n=len(data);target=md['backend_metadata']['output_qubits'][0];saved={k:rt(q) for k,q in case.circuits.items()}
   for k,q in case.circuits.items():comp(q,saved[k])
   raw0=scalar_program(original.raw);raw1=scalar_program(saved['raw'])
   isxor='kickback' in md['oracle_construction']
   for x,t in itertools.product(range(1<<n),(0,1) if isxor else (0,)):
    b=sum(((x>>i)&1)<<w for i,w in enumerate(data))|(t<<target)
    a,pa=scalar(raw0,b);z,pz=scalar(raw1,b);assert a==z;close(pa,pz)
    if isxor:assert z==b^(int(good(p,r,x))<<target);close(pz,1)
   wrapper=QuantumCircuit(case.raw.num_qubits)
   if isxor:wrapper.x(target);wrapper.h(target);wrapper.compose(case.raw,inplace=True);wrapper.h(target);wrapper.x(target)
   else:wrapper.compose(case.raw,inplace=True);wrapper.z(target);wrapper.compose(case.raw.inverse(),inplace=True)
   comp(wrapper,saved['oracle'])
   # Original preparation has no >=3-control gate in k<=5 fixtures, so it must
   # retain the same ordered emitted definitions. Local k5 blocks checked below.
   comp(original.preparation,saved['preparation'])
   owners=md['mcx_lowering']['search_scratch_ownership'];rr=owners['raw'];aa=owners['preparation'];zz=owners['zero_reflection']
   allw=rr+aa+zz;assert len(set(allw))==len(allw) and all(w>=original.raw.num_qubits for w in allw)
   assert rr==list(range(original.raw.num_qubits,case.raw.num_qubits))
   assert aa==list(range(case.raw.num_qubits,case.raw.num_qubits+len(aa)))
   assert zz==list(range(case.raw.num_qubits+len(aa),case.search.num_qubits))
   # Derive signed reflection independently, then apply the proven clean MCX
   # substitution to this one middle block. No candidate diffusion helper used.
   z=QuantumCircuit(n,global_phase=math.pi);z.x(range(n))
   if n==1:z.z(0)
   else:z.h(n-1);z.mcx(list(range(n-1)),n-1);z.h(n-1)
   z.x(range(n));zl,zi=s._restoring_mcx_block(z)
   d=QuantumCircuit(case.diffusion.num_qubits);d.compose(case.preparation.inverse(),range(case.preparation.num_qubits),inplace=True);d.compose(zl,[*range(n),*range(case.preparation.num_qubits,d.num_qubits)],inplace=True);d.compose(case.preparation,range(case.preparation.num_qubits),inplace=True);comp(d,saved['diffusion'])
   search=QuantumCircuit(case.search.num_qubits);search.compose(case.preparation,[*data,*aa],inplace=True);search.compose(case.oracle,range(case.oracle.num_qubits),inplace=True);search.compose(case.diffusion,[*data,*aa,*zz],inplace=True);comp(search,saved['search'])
   peaks=md['component_workspace'];rawpeak=max((v['appended_ancillas'] for k,v in md['mcx_lowering']['blocks'].items() if k not in ('preparation','zero_reflection')),default=0)
   assert peaks['search']['mcx_live_peak_upper_bound']==max(rawpeak,len(aa),len(zz))
   for name,q in case.circuits.items():
    w=peaks[name];assert sorted(x for group in w['roles'].values() for x in group)==list(range(q.num_qubits))
    assert w['mcx_reserved_qubits']==len(w['roles']['mcx_ancilla']);assert w['peak_live_workspace_qubits'] is None
    assert all(it.operation.num_qubits<=3 for it in q.data)
   if case.search.num_qubits<=5:
    initial=Statevector.from_instruction(original.preparation).data;report['statevectors']+=1
    expected=initial.copy();expected[np.array([good(p,r,x) for x in range(1<<n)])]*=-1;expected=2*initial*np.vdot(initial,expected)-expected
    phys=np.zeros(1<<case.search.num_qubits,dtype=complex)
    for x,v in enumerate(expected):phys[sum(((x>>i)&1)<<w for i,w in enumerate(data))]=v
    close(Statevector.from_instruction(saved['search']).data,phys);report['statevectors']+=1
   if case.diffusion.num_qubits<=4:
    a=mat(case.preparation);sign=-np.eye(len(a));sign[0,0]=1;close(mat(saved['diffusion']),a@sign@a.conj().T)
   report['cases'].append({'fixture':pi,'method':method,'regime':r,'width':case.search.num_qubits,'marked':sum(good(p,r,x) for x in range(1<<n)),'total':1<<n,'construction':md['oracle_construction']})
 for k in (3,5):
  n=(k-1).bit_length();q=QuantumCircuit(n);q.append(StatePreparation([1/math.sqrt(k)]*k+[0]*((1<<n)-k)),range(n));close(mat(q)[:,0],np.array([1/math.sqrt(k)]*k+[0]*((1<<n)-k)))

def recount():
 evidence=C/'dump/1026021845-restoring-mcx'
 for manifest in sorted((evidence/'restoring-canonical-final').glob('*/run.json')):
  m=json.loads(manifest.read_text());rows={row['artifact']:row for row in csv.DictReader((manifest.parent/'summary.csv').open())}
  for case in m['cases']:
   if case['status']!='complete':assert case['status']=='excluded';continue
   for filename,stat in case['artifact_statistics'].items():
    path=manifest.parent/filename;assert hashlib.sha256(path.read_bytes()).hexdigest()==stat['sha256']
    with path.open('rb') as f:q=qpy.load(f)[0]
    counts=Counter();clocks=[0]*q.num_qubits
    for it in q.data:
     assert it.operation.name not in ('barrier','measure');counts[it.operation.name]+=1;w=[q.find_bit(b).index for b in it.qubits];t=1+max((clocks[b] for b in w),default=0)
     for b in w:clocks[b]=t
    vals={'qubits':q.num_qubits,'gates':sum(counts.values()),'depth':max(clocks,default=0),'gate_types':dict(counts)}
    for k,v in vals.items():assert stat['metrics'][k]==v
    row=rows[filename]
    for k in ('qubits','gates','depth'):assert int(row[k])==vals[k]
    assert ast.literal_eval(row['gate_types'])==dict(counts)
    report['rows']+=1
 assert report['rows']==2100
 # Exact default compatibility uses saved baseline bytes; no dependence on metric helpers.
 count=0
 refs={p.relative_to(evidence/'reference-final'):p for p in (evidence/'reference-final').rglob('*.qpy')}
 # Run directory timestamps differ, so key by final filename and fixture run ordinal.
 ref_runs=sorted((evidence/'reference-final').glob('*/run.json'));new_runs=sorted((evidence/'default-canonical-final').glob('*/run.json'))
 assert len(ref_runs)==len(new_runs)
 for a,b in zip(ref_runs,new_runs):
  for p in a.parent.glob('*.qpy'):
   other=b.parent/p.name;assert p.read_bytes()==other.read_bytes();count+=1
 assert count==480;report['default_exact_artifacts']=count

def failures():
 for policy in ('gray_code','noaux_v24','1_clean_b95','n_clean_m15','n_dirty_i15','1_clean_kg24','1_dirty_kg24','2_clean_kg24','2_dirty_kg24','throwaway_tree','unknown'):
  try:s.run_coloring_study(dict(inputs=['missing.col'],mcx_decomposition=policy,mcx_workspace='fresh_zero'))
  except ValueError as e:report['rejections'].append(str(e))
  else:raise AssertionError(policy)
 for q in (QuantumCircuit(4),QuantumCircuit(1),QuantumCircuit(1,1),QuantumCircuit(22)):
  if q.num_qubits==4:q.append(Gate('hidden',4,[]),range(4))
  elif q.num_qubits==22:q.mcx(list(range(21)),21)
  elif q.num_clbits:q.measure(0,0)
  else:q.rx(Parameter('theta'),0)
  try:s._restoring_mcx_block(q)
  except ValueError as e:report['rejections'].append(str(e))
  else:raise AssertionError('unsupported accepted')
 # Independent partial-failure injections, preserving artifacts and zero failed rows.
 fixture=R/'failure.col';fixture.write_text('p edge 1 0\nx colors 3\n')
 original=s.assemble_case;load=qpy.load
 for fault in ('opaque','phase'):
  calls=[0];out=R/('1026025000-'+fault)
  def asm(*a,**kw):
   case=original(*a,**kw)
   if fault=='opaque' and kw['iterations']==1:case.diffusion.append(Gate('bad',1,[]),[0])
   return case
  def altered(*a,**kw):
   q=load(*a,**kw);calls[0]+=1
   if fault=='phase' and calls[0]==8:q[0].global_phase+=.19
   return q
  with patch.object(s,'assemble_case',asm),patch.object(qpy,'load',altered):
   s.run_coloring_study(dict(inputs=[str(fixture)],methods=['sb_balanced'],regimes=['R2'],iterations=[0,1],mcx_decomposition='clean_tree',mcx_workspace='fresh_zero',output=str(out)))
  m=json.loads((out/'run.json').read_text());rows=list(csv.DictReader((out/'summary.csv').open()));assert [c['status'] for c in m['cases']]==['complete','failed'];assert len(rows)==5 and all(row['iteration']=='0' for row in rows);assert m['cases'][1]['artifacts'];report['rejections'].append(m['cases'][1]['reason'])

start=time.monotonic()
try:
 tiny_templates();semantic_cases();recount();failures();report['status']='passed'
finally:
 report['seconds']=time.monotonic()-start;(R/'independent-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:(len(v) if k=='cases' else v) for k,v in report.items()},indent=2))
```

### additional.py

```python
from pathlib import Path
import os
R=Path(os.environ['REVIEW_RUN'])
exec(compile((R/'independent.py').read_text().split('start=time.monotonic()\ntry:')[0],str(R/'independent.py'),'exec'))
import logique.verification as verification
import logique.circuits.grover as grover
report['saved_primary_cases']=0
# Compare every final saved primary component to a fresh candidate assembly,
# including j=0. This supplements the independent predicate/template proofs.
evidence=C/'dump/1026021845-restoring-mcx'
for manifest in (evidence/'restoring-canonical-final').glob('*/run.json'):
 m=json.loads(manifest.read_text())
 for rec in m['cases']:
  if rec['status']!='complete':continue
  p=ColoringProblem(rec['vertices'],rec['edges'],rec['colors'])
  case=s.assemble_case(p,rec['method'],rec['regime'],iterations=rec['iteration'],mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
  for name,q in case.circuits.items():
   path=manifest.parent/rec['artifacts'][name+'_restoring_mcx']
   with path.open('rb') as f:saved=qpy.load(f)[0]
   comp(q,saved)
   w=rec['component_workspace'][name];fresh=case.metadata['component_workspace'][name]
   assert w==fresh
  if rec['iteration']==0:
   owners=case.metadata['mcx_lowering']['search_scratch_ownership'];expected=QuantumCircuit(case.search.num_qubits);expected.compose(case.preparation,[*case.metadata['data_qubits'],*owners['preparation']],inplace=True);comp(expected,case.search)
   assert case.metadata['component_workspace']['search']['mcx_live_peak_upper_bound']==len(owners['preparation'])
  stages=rec['stage_timings'];assert stages['native_combined']['included_in']=='synthesis'
  assert rec['peak_memory']=={'status':'unavailable','bytes':None}
  for stage in ('mapping','optimization'):assert stages[stage]['seconds'] is None
  report['saved_primary_cases']+=1
assert report['saved_primary_cases']==210
# Deliberately force conservative wrappers on genuine native raw circuits.
for method,r in itertools.product(s.METHODS,s.REGIMES):
 p=ColoringProblem((42,),(),5)
 with patch.object(verification,'verify_kickback_oracle',side_effect=AssertionError('independent forced fallback')):
  original=s.assemble_case(p,method,r,iterations=2)
  case=s.assemble_case(p,method,r,iterations=2,mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
 assert case.metadata['oracle_construction']=='compute_Z_inverse_compute'
 for q in (original.oracle,case.oracle,rt(case.oracle)):
  program=scalar_program(q)
  for x in range(8):
   b,phase=scalar(program,x);assert b==x;close(phase,(-1 if good(p,r,x) else 1))
 expected=case.raw.copy();expected.z(case.metadata['backend_metadata']['output_qubits'][0]);expected.compose(case.raw.inverse(),inplace=True);comp(expected,case.oracle)
 owners=case.metadata['mcx_lowering']['search_scratch_ownership'];data=case.metadata['data_qubits'];expect=QuantumCircuit(case.search.num_qubits);expect.compose(case.preparation,[*data,*owners['preparation']],inplace=True)
 for j in range(2):expect.compose(case.oracle,range(case.oracle.num_qubits),inplace=True);expect.compose(case.diffusion,[*data,*owners['preparation'],*owners['zero_reflection']],inplace=True)
 comp(expect,case.search)
# Inject a real nested open MCX into A: this is assembly coverage, not a claim
# that the deliberately altered A is a uniform valid-color preparation.
original_preparation=grover.coloring_preparation
captured=[]
def injected(enc):
 a=original_preparation(enc);inner=QuantumCircuit(4,global_phase=.329);inner.append(MCXGate(3,ctrl_state=5),[2,0,3,1]);a.append(inner.to_gate().inverse(),[1,3,0,2]);captured.append(a.copy());return a
with patch.object(grover,'coloring_preparation',injected):
 case=s.assemble_case(ColoringProblem((-9,30),((-9,30),),3),'sb_balanced','R2',iterations=2,mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
a=captured[0];lo=case.preparation;assert a.num_qubits==4 and lo.num_qubits==5
matrix=mat(a)
for x in range(16):
 v=np.zeros(32,dtype=complex);v[x]=1
 actual=Statevector(v.copy()).evolve(lo).data;report['statevectors']+=1;close(actual,np.r_[matrix[:,x],np.zeros(16)])
 close(Statevector(actual.copy()).evolve(lo.inverse()).data,v);report['statevectors']+=1
md=case.metadata['mcx_lowering'];owners=md['search_scratch_ownership'];assert all(owners[k] for k in owners)
assert len(set(sum(owners.values(),[])))==sum(len(v) for v in owners.values())
# Compare actual emitted A inverse prefix and phase-canceling full diffusion.
inv=lo.inverse();di=case.diffusion
inverse_leaves,phase=flat(inv);diff_leaves,dphase=flat(di)
assert diff_leaves[:len(inverse_leaves)]==inverse_leaves
forward_leaves,fphase=flat(lo);assert diff_leaves[-len(forward_leaves):]==forward_leaves
close(dphase,-1)
# Full independent j=2 composition, retaining all three disjoint scratch pools.
expect=QuantumCircuit(case.search.num_qubits);data=case.metadata['data_qubits'];expect.compose(lo,[*data,*owners['preparation']],inplace=True)
for j in range(2):expect.compose(case.oracle,range(case.oracle.num_qubits),inplace=True);expect.compose(di,[*data,*owners['preparation'],*owners['zero_reflection']],inplace=True)
comp(expect,rt(case.search))
report['injected_preparation']={'data_qubits':4,'preparation_width':5,'owners':owners,'status':'passed'}
report['status']='passed';(R/'additional-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
```
