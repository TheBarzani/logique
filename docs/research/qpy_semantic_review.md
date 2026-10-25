# Independent bounded QPY semantic review

**Bounded review COMPLETE. Admission: ADMITTED for the exact metadata/QPY
candidate identified below, under the scope and limitations in this review.**
No remaining blocker was found for this bounded contract. The original inverse
serialization failure is reproduced, and the correction preserves the actual
emitted definitions, scalar phases and ordered wires in the reviewed cases.
This is neither full-paper completion nor broad scientific, FT or RUS admission.

## Identity and intake

Date: 25 October 2026. Reviewer worktree:
`/Users/mar/codex-work/logique/dump/1025074732-stage-controls-triage/worktrees/qpy-review`.
Branch: `codex/coloring-qpy-review-1025074732`; base
`3ef846fee9ebcd57e5ce48e958ea2420f992a680`. Only this review is committed.
Executable evidence is inside this worktree's ignored
`dump/1025124357-qpy-semantic-review/` (called RUN below).

Read-only candidate worktree:
`/Users/mar/codex-work/logique/dump/1025074732-stage-controls-triage/worktrees/qpy-correction`.
Correction commit `b3ba0ec56d2c8dc603c973eb5ec1dcfe0abc2545`; checkpoint HEAD
`9451cba`. Both worktrees were clean at intake. The candidate's two actual files,
not the review worktree's older copies, were read and executed. Runtime import
assertions enforce the candidate source path.

| Candidate file | SHA-256 before and after all checks (identical) |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `cd15709cc9c0e4bec932a025691db433233c175b852c4c585e114ec3d4bc4452` |
| `tests/test_coloring_study.py` | `54d32c5d519a9e41f93f0cf6145bb91afb8fe6206965ffe70f662a391cf7e644` |

The older foundation hashes are respectively
`37a04d3feb81ba3a7b00de19136ae78ce337d61230d471af057ab466a860123d` and
`8bda782c9e9a0ca50c4ccde024ea8a8919d5dc7169b05e592322a52b0406f67d`.
They are not admitted for saved inverse-preparation semantics.

Git and dispatcher state were inspected first. Full queue/state inspection
identified correction as **complete**, this reviewer as the sole running job,
and `coordinate-qpy-1025074732` queued with `dependency_policy="finished"`.
The unrelated low-T worker is blocked; predecessor completion was not inferred
from the stale server-manifest active-job snapshot. Final durable state again
shows this review as the only running job. `ps` was sandbox-denied, so complete
OS process visibility is not claimed. Queue/state/server manifest were not edited.

Read AGENTS.md, CLAUDE.md, the full 638-line revision plan, implementation audit,
architecture, rotation numerical admission, rotation-admission batch, stage
triage batch, full current server checkpoint manifest, original root
`docs/research/stage_controls_qpy_review.md`, candidate checkpoint and both
candidate files. The candidate's final saved artifacts were inspected directly.
Older instructions to sync/build/launch are superseded by this task's bounds.

## Decision and evidence

The original installed Qiskit 2.1.1 two-qubit counterexample is retained as
`original-inverse-unsafe.qpy`: append
`StatePreparation([1/sqrt(3)]*3+[0]).inverse()` to wires `[0,1]`, then QPY roundtrip.
Its name changes from `state_preparation_dg` to `state_preparation`, its inverse
flag becomes false, and phase-sensitive operator distance is exactly reproduced
as **1.9986497753173806**. The resolved saved correction's distance from the
original is **1.420252502539254e-15**. No phase alignment hides scalar errors.

Independent checks below use direct Qiskit operators, an independently written
recursive instruction comparison, direct dependency-depth counting and a scalar
monomial evaluator. They do not import candidate test helpers, candidate metric
or signature helpers, or the library verification interpreter for their reference
answers. Production assembly and serialization are the subjects under test.

- **92 supplied tests passed, 31 deliberately deselected, no skips**, in 6.83s.
  Deselected wider dense tests: `matching_preparation_diffusion_and_search` (27),
  `r3_keeps_asymmetric_k5_preparation` (1), and
  `native_asymmetric_constant_r3_and_complete_search` (3).
- **36 semantic cases**: reassembly of all 24 saved worker cases across R1/R2/R3,
  j=0/1, edge k=3, isolated k=5, unsatisfiable triangle k=2 and isolated k=3;
  eight additional noncontiguous-label k=5-edge and native k=3-edge cases in
  R2/R3 at j=0/1; four explicitly forced conservative-wrapper cases on genuine
  native k=5 raw circuits. Ordinary native fixtures selected verified kickback;
  the last four are labeled branch-coverage fixtures, not naturally occurring
  backend rejection or experiment rows.
- **381 phase-sensitive operator comparisons**, all <=4 qubits; maximum error
  **4.351856696025063e-15**. These include original/saved logical components,
  original/common-basis bounded components, emitted/readback components, the
  minimal example, 32 complex asymmetric forward/inverse/nested/controlled
  preparation cases at k=3/5, and every three-control MCX polarity.
- **32 original/saved complete-search statevector comparisons**, entire physical
  register <=5 qubits; maximum error **1.8396266905731044e-15**. Independent
  data-space amplification includes all zero-workspace amplitudes and checks
  the remaining physical register is clean. Mapping is applied explicitly.
- **408 composition checks**, **2,816 scalar monomial column checks**, and
  **24 independently recomputed serialized-network statistics**. The monomial
  count includes all three-/four-control MCX polarities and all basis columns,
  not 2,816 distinct graph instances.
- **All 240 saved rows independently reproduced**: width, actual operation
  counts, full gate-type map and direct dependency depth, plus artifact hashes,
  representation, status, wire roles and timing metadata. U/CX circuits were
  independently re-emitted with Qiskit seed 7, optimization level 0 and matched
  against saved ordered operations and scalar phase.

Positive and negative predicates are both exercised: k=3 edge has 6/16 marked
binary assignments with the original predicate and 12/16 without domain checks;
k=5 edge has 20/64 and 56/64. Unsatisfiable triangle marks 0/8. Isolated R3
cases are constant true (4/4 or 8/8), while complete predicates reject invalid
codes. No success-only sample substitutes for these exhaustive small references.

## Why the wider composition is sufficient for this scope

The largest reviewed register is 11 physical wires; largest data register is
six wires. Neither is allocated as a dense operator/statevector. Raw XOR checks
propagate a basis integer and scalar phase, using actual <=4-wire monomial gate
matrices and algebraic MCX control-state action. Both target sectors preserve
all other wires and have unit scalar phase. Exact X-H/raw/H-X composition then
proves clean phase kickback by linearity, including superposed data. Conservative
compute-Z-actual-inverse cases instead check the original phase circuit's basis
action and transfer it through exact ordered-definition composition.

The independent expansion compares actual recursive definitions, ordered local
wire embeddings, standard-gate class/parameters/control states and accumulated
scalar phase. Tensoring local equalities with identity and composing them proves
the wider logical original/readback equality without a wide dense simulation.
This relies on the trusted installed standard-gate semantics, not operation names
alone, and is not adversarial arbitrary-object or modified-standard-class support.

For six data wires, preparation is two disjoint three-wire actual preparations,
each checked against its k=5 amplitudes. Diffusion is compared to the actual
preparation inverse, `-X^n MCZ X^n`, and the actual forward preparation in order.
The middle block has +1 on zero and -1 elsewhere, proving the positive Grover
sign. This proves `A(2|0><0|-I)A†`, actual inverse reuse and preservation of the
valid-color subspace. Search is initialization once followed by oracle/diffusion
j times. Narrow diffusions also directly satisfy the full matrix identity.

Common-basis serialization is checked against independently emitted U/CX
circuits at every width. Original-to-common-basis operator equivalence is checked
only where width <=4. **General wider transpiler equivalence is not independently
certified here**; this admission covers fidelity of the saved emitted circuit,
not arbitrary transpiler transformations or all study methods/inputs.

## Metrics, failures and limits

Resolution changes representation. Relative to the original emitted circuits,
**48/240 rows change gate-type maps**, 16 each for logical preparation,
diffusion and search. **36 change total gate count and depth; zero change width**.
Raw/oracle and the 120 common-basis rows are unchanged for this ledger. Counts
are mixed-granularity resolved standard gates, explicitly marked
`resolved_standard_gates`; these are not improvements over historical opaque
operation counts. Keep future research-metric/table changes separate from this
correctness change and do not combine representations silently. Unsafe archived
QPY artifacts remain unsafe; this review does not retroactively repair the pilot.

Stage timing intervals use the monotonic clock and identify overlap:
native combined time is inside synthesis, unavailable optimization/mapping splits
remain null, and case total includes assembly/validation/artifacts/metrics while
excluding final case/manifest save. Resolution includes expected-signature work;
QPY write/read includes hash/signature verification, not a pure codec benchmark.
Network counts include serialized dangling nodes; LUT multiplicative depth is
not invented. Wire-role partitions are allocations, not live-workspace peaks;
native residual workspace stays unknown, memory/live-workspace fields stay null,
and no added-MCX-ancilla count is interpreted as a decomposition resource bound.

Two independent mixed-success runs inject failure after earlier artifacts:
opaque inverse-named gate and changed readback scalar phase. Both retain the
failed case and earlier artifacts; each summary contains exactly the five rows
of the separate successful j=0 case and **zero rows from failed j=1**. Partial
artifact presence does not admit comparison rows. Supplied regressions additionally
check depth/operation limits, classical/unbound/nonfinite rejection and lowering
failure. Unsupported opaque/dynamic/unbound forms are outside admission.

Explicit retained failures: the original inverse counterexample; the two deliberate
negative artifact fixtures; sandbox-denied `ps`; one failed read of an absent
worktree native-source glob; initial Git staging denied the shared worktree
`index.lock` (requires narrowly scoped Git escalation); and
`independent-final.log`, a reviewer-harness error.
That harness assumed every resolved inverse-CCRx leaf was monomial and rejected
an intermediate CU gate. Its original script/results are preserved as
`independent-fallback-failed.*`. The corrected proof checks the whole original
monomial block and transfers it through ordered-definition composition; intermediate
CU leaves need not be monomial. Final checks pass without changing candidate code.

No full suite, new build, mypy, notebooks, historical replay, full study, protocol
freeze, optimality or superiority claim is made. Traversal limits (depth 32,
100000 operations) do not bound all internal Qiskit definition-synthesis memory.
The fixed tiny fixtures and measured memory support this run's resource bound,
not a general production memory guarantee. Numeric preparation/operator checks
are floating-point evidence, not interval certification or an ideal-amplitude
guarantee for arbitrary inputs. Rotation admission remains restricted to the
unchanged reviewed hashes and caller obligations in `rotation_norm_admission.md`;
this review grants no FT, RUS, dynamic, hardware or paper approval.

## Resources, preservation and next action

All numerical work used the existing `/Users/mar/codex-work/logique/.venv/bin/python`,
explicit candidate `PYTHONPATH`, cache `/Users/mar/codex-work/logique/.cache/epfl`,
and private executable
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`.
Its SHA-256 remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the root old binary remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.
BLAS/OpenMP/Accelerate threads were 1. One numerical command at a time, no
compiler; each command timeout <=120s, wrapper cumulative allowance 300s.
**Total numerical child wall time 17.2374s**, including the failed harness and
all intermediate runs; maximum measured child RSS **219,987,968 bytes**.
No OS aggregate memory cap or full OS process visibility is claimed.

`commands.jsonl` records commands, environment, duration, exit codes and RSS;
logs and all intermediate harness versions/results are retained. Final result
SHA-256: `85cfe7bdc92c491d1af5091c5937b5b7ec80daeac42d38e55c10790a83941b5c`.
Final executable block SHA-256 (UTF-8 without fence/newline delimiters):
`3b89b84cb00c6b299f556f4685d083dcc759ad52e6a445e7d3cdd75caed54081`.

Before/after records verify **215 protected identities**, including candidate
source/tests and all candidate library Python files, both README files, lockfile,
root runner/rotation files/binaries, archived manuscript outputs, preserved nested
histories and rotation prototype backups. External Git index entries and pinned
gitlinks are unchanged; the dispatcher queue is byte-identical. No candidate/root
source, dependency, archive or checkpoint was edited. No agents, model/Codex
launches, API/paid fallback, sync/install, hardware, push or publishing occurred.

**Next action:** dispatcher releases the already queued coordinator to verify
these exact bytes, preserve this review and integrate the validated owned
correctness/metadata commits separately from any changed research metrics.
The reviewer performs no root integration. Re-review changed source bytes or a
broader serialization contract. Earlier affected saved pilot evidence still needs
its own correction/review. Full controls, studies and the full paper remain open.
This bounded review has no pending checks and must not be redispatched merely
because the full paper remains unfinished.

## Executable independent checks

The code below is the exact final executed independent harness. It reads the
candidate's retained final artifact ledger and writes only to a fresh local RUN.
The candidate suite command is in RUN/commands.jsonl; selection is listed above.
To replay this block from the review worktree with the existing interpreter:

```sh
PYTHONPATH=/Users/mar/codex-work/logique/dump/1025074732-stage-controls-triage/worktrees/qpy-correction/src \
LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl \
LOGIQUE_NATIVE_EXECUTABLE=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis \
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
/Users/mar/codex-work/logique/.venv/bin/python - <<'PY'
import os, signal
from datetime import datetime
from pathlib import Path
run = Path.cwd() / 'dump' / (datetime.now().strftime('%m%d%H%M%S') + '-qpy-review-replay')
run.mkdir(parents=True)
os.environ['REVIEW_RUN'] = str(run)
code = Path('QPY_SEMANTIC_REVIEW.md').read_text().split('```python\n', 1)[1].split('\n```', 1)[0]
signal.alarm(120)
exec(compile(code, 'QPY_SEMANTIC_REVIEW.md', 'exec'))
PY
```

```python
"""Independent QPY review: no candidate test helpers or verification interpreter."""
import ast
from collections import Counter
from datetime import datetime
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import resource
import time
from unittest.mock import patch

import numpy as np
import pandas as pd
import qiskit
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import Gate
from qiskit.circuit.library import StatePreparation, MCXGate
from qiskit.quantum_info import Operator, Statevector
from logique.benchmarks import coloring_study as s
from logique.coloring import ColoringProblem

RUN = Path(os.environ['REVIEW_RUN'])
SRC = Path(os.environ['PYTHONPATH']).parent
assert Path(s.__file__).resolve() == SRC / 'src/logique/benchmarks/coloring_study.py'
EXPECTED = {'src/logique/benchmarks/coloring_study.py': 'cd15709cc9c0e4bec932a025691db433233c175b852c4c585e114ec3d4bc4452',
            'tests/test_coloring_study.py': '54d32c5d519a9e41f93f0cf6145bb91afb8fe6206965ffe70f662a391cf7e644'}
def hashes():
    actual = {p: hashlib.sha256((SRC/p).read_bytes()).hexdigest() for p in EXPECTED}
    assert actual == EXPECTED
    return actual

report = dict(hashes_before=hashes(), versions=dict(qiskit=qiskit.__version__, numpy=np.__version__),
              operators=[], statevectors=[], composition_checks=0, monomial_columns=0,
              cases=[], metric_rows=0, representation_changes=[], failures=[], network_checks=0)
def save():
    (RUN/'independent-results.json').write_text(json.dumps(report, indent=2)+'\n')

def matrix(q):
    assert q.num_qubits <= 4, q.num_qubits
    return Operator(q).data

def equal(a, b, label):
    err = float(np.linalg.norm(matrix(a)-matrix(b), 2))
    report['operators'].append(dict(label=label, qubits=a.num_qubits, error=err))
    assert err < 2e-11, (label,err)

def rt(q, name=None):
    stream=io.BytesIO();qpy.dump(q,stream)
    if name: (RUN/(name+'.qpy')).write_bytes(stream.getvalue())
    stream.seek(0)
    return qpy.load(stream)[0]

def key(op):
    return (op.base_class.__module__,op.base_class.__name__,op.name,
            tuple(complex(p) for p in op.params),getattr(op,'num_ctrl_qubits',0),getattr(op,'ctrl_state',None))

def leaves(q):
    """Independent recursive reference. Standard algebraic leaves remain intact."""
    operations=[]; phase=0.0
    def visit(c, wires, depth=0):
        nonlocal phase
        assert depth <= 32
        phase += float(c.global_phase)
        for item in c.data:
            op=item.operation; mapping=tuple(wires[c.find_bit(b).index] for b in item.qubits)
            closed=getattr(op,'ctrl_state',None) in (None,(1<<getattr(op,'num_ctrl_qubits',0))-1)
            if op.base_class.__module__.startswith('qiskit.circuit.library.standard_gates.') and closed:
                operations.append((key(op),mapping))
            else:
                assert op.definition is not None,op.name
                visit(op.definition,mapping,depth+1)
    visit(q,tuple(range(q.num_qubits)))
    return operations, np.exp(1j*phase)

def composition(a,b,label):
    x,p=leaves(a);y,r=leaves(b)
    assert a.num_qubits==b.num_qubits and x==y,(label,'ordered operations')
    assert abs(p-r)<2e-11,(label,'scalar phase',p,r)
    report['composition_checks']+=1
    if a.num_qubits<=4:equal(a,b,label)

def metrics(q):
    counts=Counter(); clocks=[0]*q.num_qubits
    for item in q.data:
        assert item.operation.name not in ('measure','barrier')
        counts[item.operation.name]+=1
        wires=[q.find_bit(b).index for b in item.qubits]
        depth=1+max((clocks[b] for b in wires),default=0)
        for b in wires:clocks[b]=depth
    return dict(qubits=q.num_qubits,gates=sum(counts.values()),depth=max(clocks,default=0),gate_types=dict(counts))

def metadata(record):
    for network in ('source_network','network'):
        graph=record['backend_metadata'].get(network);stat=record['structural_statistics'][network]
        if graph is None:
            assert stat['status']=='unavailable';continue
        nodes={x['id']:x for x in graph['nodes']};counts=Counter(x['kind'] for x in nodes.values())
        def depth(i,multiplicative=False):
            node=nodes[i]
            if not node['fanins']:return 0
            return max(depth(x['node'],multiplicative) for x in node['fanins']) + (int(node['kind']=='and') if multiplicative else 1)
        assert stat['node_counts']==counts
        assert stat['logic_depth']==max(depth(i) for i in nodes)
        for field,kind in [('AND','and'),('XOR','xor'),('LUT','lut')]:assert stat[field]==counts[kind]
        if set(counts)<={'constant','input','and','xor'}:assert stat['multiplicative_depth']==max(depth(i,True) for i in nodes)
        else:assert stat['multiplicative_depth'] is None
        report['network_checks']+=1
    stages=record['stage_timings'];total=record['total_seconds']
    assert stages['case_total']['seconds']==total
    for key,seconds in record['timings'].items():
        entry=stages[key.removesuffix('_seconds')]
        assert entry['seconds']==seconds and entry['included_in']=='case_total' and 0<=seconds<=total
    native=record['backend_metadata'].get('native_seconds')
    assert stages['native_combined']['seconds']==native
    if native is not None:assert 0<=native<=stages['synthesis']['seconds']
    for name,stat in record['artifact_statistics'].items():
        for entry in stat['stage_timings'].values():
            if entry['status']=='measured':assert 0<=entry['seconds']<=total
        # common_basis suffix has two words; use the known component prefix.
        component=next(c for c in ('raw','preparation','oracle','diffusion','search') if name.endswith(c+'_logical.qpy') or name.endswith(c+'_common_basis.qpy'))
        assert stat['workspace']==record['component_workspace'][component]

local_cache={}
def monomial(q,bits):
    """Scalar basis propagation, with <=4-wire gate operators, no wide vector."""
    phase=np.exp(1j*float(q.global_phase))
    for item in q.data:
        op=item.operation;wires=[q.find_bit(b).index for b in item.qubits]
        value=sum(((bits>>b)&1)<<j for j,b in enumerate(wires))
        if isinstance(op,MCXGate):
            nc=op.num_ctrl_qubits
            output=value^(1<<nc) if value&((1<<nc)-1)==op.ctrl_state else value
            scalar=1
        else:
            k=key(op)
            if k not in local_cache:
                assert len(wires)<=4,(op.name,len(wires))
                local=QuantumCircuit(len(wires));local.append(op,range(len(wires)))
                m=matrix(local); cols=[]
                for j in range(len(m)):
                    nz=np.flatnonzero(abs(m[:,j])>1e-10)
                    assert len(nz)==1,('not monomial',op.name,j)
                    i=int(nz[0]);assert abs(abs(m[i,j])-1)<1e-10
                    cols.append((i,m[i,j]))
                local_cache[k]=cols
            output,scalar=local_cache[k][value]
        for j,b in enumerate(wires):bits=(bits&~(1<<b))|(((output>>j)&1)<<b)
        phase*=scalar
    return bits,phase

def predicate(problem,regime,x):
    c=(problem.colors-1).bit_length(); vals={v:(x>>(i*c))&((1<<c)-1) for i,v in enumerate(problem.vertices)}
    return all(vals[a]!=vals[b] for a,b in problem.edges) and (regime=='R3' or all(v<problem.colors for v in vals.values()))

def check_case(case,problem,regime,j,saved,label):
    md=case.metadata; data=md['data_qubits']; n=len(data); c=(problem.colors-1).bit_length()
    assert md['input_mapping']=={v:data[i*c:(i+1)*c] for i,v in enumerate(problem.vertices)}
    target=md['backend_metadata']['output_qubits'][0]
    for name,original in case.circuits.items():composition(original,saved[name],label+'/'+name)
    marked=[predicate(problem,regime,x) for x in range(1<<n)]
    if 'kickback' in md['oracle_construction']:
        for x,t in itertools.product(range(1<<n),(0,1)):
            initial=sum(((x>>i)&1)<<b for i,b in enumerate(data)) | (t<<target)
            expected=initial^(int(marked[x])<<target)
            for q in (case.raw,saved['raw']):
                bits,phase=monomial(q,initial)
                assert bits==expected and abs(phase-1)<1e-10,(label,x,t,bits,expected,phase)
                report['monomial_columns']+=1
        wrapper=QuantumCircuit(case.raw.num_qubits);wrapper.x(target);wrapper.h(target)
        wrapper.compose(case.raw,inplace=True);wrapper.h(target);wrapper.x(target)
        composition(wrapper,saved['oracle'],label+'/kickback')
    else:
        for x in range(1<<n):
            initial=sum(((x>>i)&1)<<b for i,b in enumerate(data))
            # The original inverse CCRx is monomial as a whole; its saved
            # definition can contain nonmonomial CU leaves. Exact ordered-leaf
            # composition above transfers this proof to saved, without claiming
            # each intermediate CU is monomial.
            for q in (case.oracle,):
                bits,phase=monomial(q,initial)
                assert bits==initial and abs(phase-(-1 if marked[x] else 1))<1e-10
                report['monomial_columns']+=1
    # Exact instruction composition proves reuse of the actual inverse.
    zero=QuantumCircuit(n,global_phase=math.pi);zero.x(range(n))
    if n==1:zero.z(0)
    else:zero.h(n-1);zero.mcx(list(range(n-1)),n-1);zero.h(n-1)
    zero.x(range(n))
    expected_d=case.preparation.inverse().compose(zero).compose(case.preparation)
    composition(expected_d,saved['diffusion'],label+'/actual-inverse')
    if n<=4:
        a=matrix(case.preparation); d=matrix(saved['diffusion'])
        sign=-np.eye(1<<n);sign[0,0]=1
        err=float(np.linalg.norm(d-a@sign@a.conj().T,2));assert err<2e-11
        initial=a[:,0]
        support=[all(((x>>(i*c))&((1<<c)-1))<problem.colors for i in range(len(problem.vertices))) for x in range(1<<n)]
        ideal=np.full(1<<n,1/math.sqrt(1<<n)) if regime=='R1' else np.array(support)/math.sqrt(problem.colors**len(problem.vertices))
        assert np.linalg.norm(initial-ideal)<2e-11
    else:
        # Two-vertex k5 preparation is a tensor product of disjoint 3-wire blocks.
        assert n==6 and problem.colors==5
        seen=[]
        for item in case.preparation.data:
            assert len(item.qubits)==3
            local=QuantumCircuit(3);local.append(item.operation,range(3))
            assert np.linalg.norm(matrix(local)[:,0]-np.array([1/math.sqrt(5)]*5+[0]*3))<2e-11
            seen.extend(case.preparation.find_bit(b).index for b in item.qubits)
        assert sorted(seen)==list(range(6))
        # -X^n MCZ X^n gives +1 only for zero and -1 elsewhere, algebraically.
        assert zero.global_phase==math.pi
    expected_search=QuantumCircuit(case.search.num_qubits)
    expected_search.compose(case.preparation,data,inplace=True)
    for _ in range(j):expected_search.compose(case.oracle,inplace=True);expected_search.compose(case.diffusion,data,inplace=True)
    composition(expected_search,saved['search'],label+'/search-assembly')
    if case.search.num_qubits<=5:
        expect=initial.copy()
        for _ in range(j):expect[np.array(marked)]*=-1;expect=2*initial*np.vdot(initial,expect)-expect
        physical=np.zeros(1<<case.search.num_qubits,dtype=complex)
        for x,v in enumerate(expect):physical[sum(((x>>i)&1)<<b for i,b in enumerate(data))]=v
        for kind,q in [('original',case.search),('saved',saved['search'])]:
            err=float(np.linalg.norm(Statevector.from_instruction(q).data-physical));assert err<2e-11
            report['statevectors'].append(dict(label=label+'/'+kind,width=q.num_qubits,error=err))
    for name,q in case.circuits.items():
        w=md['component_workspace'][name]
        assert sorted(b for group in w['roles'].values() for b in group)==list(range(q.num_qubits))
        assert w['peak_live_workspace_qubits'] is None and w['peak_reserved_qubits']==q.num_qubits
    assert md['peak_memory']=={'status':'unavailable','bytes':None}
    for stage in ('mapping','optimization'):assert md['stage_timings'][stage]['seconds'] is None
    assert md['stage_timings']['native_combined']['included_in']=='synthesis'
    report['cases'].append(dict(label=label,n=n,width=case.search.num_qubits,marked=sum(marked),total=len(marked),construction=md['oracle_construction']))

def main():
    inverse=QuantumCircuit(2);inverse.append(StatePreparation([1/math.sqrt(3)]*3+[0]).inverse(),[0,1])
    unsafe=rt(inverse,'original-inverse-unsafe')
    err=float(np.linalg.norm(matrix(inverse)-matrix(unsafe),2))
    assert err>1.99 and unsafe.data[0].operation._inverse is False
    fixed,_=s._resolved_qpy_circuit(inverse);fixed=rt(fixed,'original-inverse-corrected')
    equal(inverse,fixed,'minimal-correction')
    report['original_failure']=dict(error=err,original=inverse.data[0].operation.name,readback=unsafe.data[0].operation.name)
    for k,inv,nested,controlled in itertools.product((3,5),(False,True),(False,True),(False,True)):
        n=(k-1).bit_length();v=np.zeros(1<<n,dtype=complex);v[:k]=np.arange(1,k+1)*np.exp(1j*np.arange(k)*0.413);v/=np.linalg.norm(v)
        a=QuantumCircuit(n,global_phase=-0.321);op=StatePreparation(v)
        a.append(op.inverse() if inv else op,list(reversed(range(n))))
        if nested:
            b=QuantumCircuit(n,global_phase=.197);b.append(a.to_gate().inverse(),list(reversed(range(n))));a=b
        if controlled:
            b=QuantumCircuit(n+1,global_phase=.263);b.append(a.to_gate().control(1,ctrl_state=0),list(reversed(range(n+1))));a=b
        resolved,_=s._resolved_qpy_circuit(a)
        equal(a,rt(resolved),f'complex-k{k}-{inv}-{nested}-{controlled}')
    for controls in (3,4):
        for state in range(1<<controls):
            q=QuantumCircuit(controls+1,global_phase=.31);q.append(MCXGate(controls,ctrl_state=state),range(controls+1))
            r,_=s._resolved_qpy_circuit(q);r=rt(r)
            if controls==3:equal(q,r,f'mcx-{controls}-{state}')
            for x in range(1<<(controls+1)):
                a,p=monomial(q,x);b,t=monomial(r,x);assert a==b and abs(p-t)<1e-12
                report['monomial_columns']+=1
    # Independently recount and validate every artifact in the final worker ledger.
    evidence=SRC/'dump/1025122708-qpy-correction/admission-candidate'
    for path in sorted(evidence.glob('*/run.json')):
        m=json.loads(path.read_text());table=pd.read_csv(path.parent/'summary.csv')
        assert m['status']=='complete'
        for record in m['cases']:
            metadata(record)
            problem=ColoringProblem(record['vertices'],record['edges'],record['colors'])
            case=s.assemble_case(problem,record['method'],record['regime'],iterations=record['iteration'])
            saved={}
            for component,original in case.circuits.items():
                for level in ('logical','common_basis'):
                    filename=record['artifacts'][component+'_'+level];p=path.parent/filename
                    with p.open('rb') as stream:q=qpy.load(stream)[0]
                    row=table[table.artifact==filename].iloc[0];stat=record['artifact_statistics'][filename]
                    actual=metrics(q)
                    assert stat['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
                    assert stat['metrics']==dict(actual,metric_level=level)
                    assert row.representation=='resolved_standard_gates'
                    for field in ('qubits','gates','depth'):assert row[field]==actual[field]
                    assert ast.literal_eval(row.gate_types)==actual['gate_types']
                    assert stat['status']=='verified'
                    assert stat['readback_signatures']['actual']==stat['readback_signatures']['expected']
                    report['metric_rows']+=1
                    if level=='logical':
                        saved[component]=q
                        old=metrics(original)
                        if old!=actual:report['representation_changes'].append(dict(case=record['name'],component=component,emitted=old,saved=actual))
                    else:
                        # Independently re-emit the configured basis, without
                        # the candidate lowering/signature/metric helpers.
                        emitted=transpile(original,basis_gates=['u','cx'],optimization_level=0,seed_transpiler=7)
                        composition(emitted,q,record['name']+'/'+component+'/common-emitted')
                        assert {item.operation.name for item in q.data}<={'u','cx'}
                        if original.num_qubits<=4:equal(original,q,record['name']+'/'+component+'/common-original')
            check_case(case,problem,record['regime'],record['iteration'],saved,record['name']+'/'+str(problem.colors))
    assert report['metric_rows']==240
    # Additional noncontiguous labels, k5 edge, and native compute-Z-inverse path.
    for problem,method in [(ColoringProblem((-7,20),((-7,20),),5),'sb_balanced'),
                           (ColoringProblem((-7,20),((-7,20),),3),'xag_bennett')]:
        for regime,j in itertools.product(('R2','R3'),(0,1)):
            case=s.assemble_case(problem,method,regime,iterations=j)
            saved={name:rt(s._resolved_qpy_circuit(q)[0]) for name,q in case.circuits.items()}
            check_case(case,problem,regime,j,saved,f'extra-{method}-{regime}-{j}')
    # Force the conservative fallback, using genuine native emitted raw gates.
    # Ordinary native fixtures above all select verified kickback; do not claim
    # they naturally exercise this branch.
    import logique.verification as verification
    for regime,j in itertools.product(('R2','R3'),(0,1)):
        problem=ColoringProblem((42,),(),5)
        with patch.object(verification,'verify_kickback_oracle',side_effect=AssertionError('review forces conservative wrapper')):
            case=s.assemble_case(problem,'xag',regime,iterations=j)
        assert case.metadata['oracle_construction']=='compute_Z_inverse_compute'
        expected=case.raw.copy();expected.z(case.metadata['backend_metadata']['output_qubits'][0]);expected.compose(case.raw.inverse(),inplace=True)
        saved={name:rt(s._resolved_qpy_circuit(q)[0]) for name,q in case.circuits.items()}
        composition(expected,saved['oracle'],f'fallback-{regime}-{j}/raw-actual-inverse')
        check_case(case,problem,regime,j,saved,f'forced-fallback-{regime}-{j}')
    # Real runner failure after earlier artifacts, alongside a successful case.
    fixture=RUN/'failure-input.col';fixture.write_text('p edge 1 0\nx colors 3\n')
    assemble=s.assemble_case
    for fault in ('opaque','readback_phase'):
        out=RUN/(datetime.now().strftime('%m%d%H%M%S')+'-'+fault)
        config=dict(inputs=[str(fixture)],methods=['sb_balanced'],regimes=['R2'],iterations=[0,1],seeds=[7],output=str(out))
        def injected(*args,**kwargs):
            case=assemble(*args,**kwargs)
            if fault=='opaque' and kwargs['iterations']==1:case.preparation.append(Gate('state_preparation_dg',2,[]),[0,1])
            return case
        original_load=qpy.load; calls=[0]
        def corrupted(*args,**kwargs):
            circuits=original_load(*args,**kwargs);calls[0]+=1
            if fault=='readback_phase' and calls[0]==7:circuits[0].global_phase+=.125
            return circuits
        with patch.object(s,'assemble_case',injected),patch.object(qpy,'load',corrupted):s.run_coloring_study(config)
        manifest=json.loads((out/'run.json').read_text());rows=pd.read_csv(out/'summary.csv')
        assert [c['status'] for c in manifest['cases']]==['complete','failed']
        assert len(rows)==5 and set(rows.iteration)=={0}
        fail=manifest['cases'][1];assert fail['artifacts']
        assert all((out/p).exists() for p in fail['artifacts'].values())
        report['failures'].append(dict(fault=fault,reason=fail['reason'],rows=len(rows),output=str(out)))
    report['hashes_after']=hashes();report['status']='passed'

start=time.monotonic()
try:main()
finally:
    report['seconds']=time.monotonic()-start
    report['max_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    save()
print(json.dumps({k:v for k,v in report.items() if k not in ('operators','statevectors','cases','representation_changes')},indent=2))
print('COUNTS',len(report['operators']),len(report['statevectors']),len(report['cases']),len(report['representation_changes']))
```
