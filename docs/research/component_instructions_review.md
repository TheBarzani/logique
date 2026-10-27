# Independent component-instruction acceptance review

**Bounded review COMPLETE. ADMITTED for the exact candidate bytes below, ONLY
as an optional unexpanded top-level instruction-count acceptance cap after
assembly and existing width acceptance, before artifacts.** No blocker remains
for this narrow contract. Bounded completion and scientific admission are separate
decisions. Full controls, experiments and the full paper remain unfinished.

## Identity and intake

Assigned task: `component-instructions-review-1026172157`. Assigned branch:
`codex/coloring-component-instructions-review-1026172157`. Reviewer base:
`9ba98d717866c47e7a0b3c6d57c06c6e0eb307a4`. Only this review is a tracked deliverable.
Reviewer worktree:
`/Users/mar/codex-work/logique/dump/1026172157-component-width-coordinator-triage/worktrees/component-instructions-review`.
Evidence RUN: `dump/1027033804-component-instructions-review/` inside it.

Read-only candidate: sibling `component-instructions`, branch
`codex/coloring-component-instructions-1026172157`, HEAD
`f6dad9fc962f2f8a039c6cd780ac2c2cf13e3963`. Correctness commit:
`f16b4d17654bb611cb9fed374b06ea42a84fcf78` (only source/tests). The later commit
contains only its checkpoint. Actual files and committed blobs match:

| File | SHA-256 before and after review |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `ea57eeea1541720f552ebbb3fd2d64b108e85e803923cad6a63fbbeb2336df32` |
| `tests/test_coloring_study.py` | `4ff6060d07b67bd76efbb3f240f8138c10360d2749fc2287ba4522ff00ab5346` |
| `INSTRUCTION_CONTROL_CHECKPOINT.md` | `7048823c4717fa967501edefd413ab3505ab28415cf3db301e0936f8cc4a965d` |
| Unchanged `src/logique/benchmarks/costs.py` | `42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8` |

Git and dispatcher inspected first. No completed own handoff existed: clean
assigned base, no review file or review commit. Candidate implementation was
complete, this reviewer alone recorded running. Entire queue/state parsed and
inventoried: 54 unique jobs, 50 state records (47 complete, two unrelated native
blocked, this review running), four pending jobs. Existing instruction coordinator
exists exactly once with finished-predecessor triage. Prior stage-controls, QPY,
restoring-MCX and component-width coordinators are complete and were not repeated.
Historical manifest status does not override live dispatcher state.

Read AGENTS.md, CLAUDE.md, all 646 lines of the revision plan, implementation audit
including newer root additions, architecture, rotation batch/admission, current
QPY and restoring batches and root admission/review/representation ledgers, parent
width batch and byte-preserved width review/admission. The full server manifest
was parsed into 2,298 scalar leaves; full batch/queue/state snapshots and leaf
inventories are retained in RUN. Inspected actual candidate source, complete diff,
tests and their local/scalar helpers, commits, checkpoint and saved evidence.
Older sync/build/model-launch instructions do not expand this assignment.

## Contract and independent reasoning

Exactly one configuration key is added: `max_component_instructions`. Its
configured value must satisfy `type(value) is int` and `value > 0`. Explicit
null, bool, float, NaN/Inf, string, containers, complex, int subclass and numpy
integer scalars reject. Validation precedes input parsing, run creation and
assembly. No numeric coercion occurs. Omission inserts neither a config default
nor a per-case instruction field; direct assembly gains no new keyword.

After successful assembly, metadata is copied to the case. The pre-existing
width gate runs first and can exclude without touching instruction data or
inserting an instruction-check field. If width accepts or is omitted, the new
gate reads `len(circuit.data)` once for each raw, preparation (A), oracle,
diffusion and search component. `ColoringStudyCase.circuits` returns exactly
these five in this order. All counts are collected before the decision, even
for unexecuted j0 components. Count greater than cap excludes; equality passes;
empty components count zero and pass every positive cap.

This is the number of **unexpanded top-level emitted instructions at their
current mixed granularity**, including barriers. A nested or opaque instruction
counts once. No instruction or definition traversal computes the acceptance
field. Default and restoring circuits can have different granularities before
this gate. The field is not an elementary gate count, complexity, resolved
artifact size, cost, memory, timeout, depth or liveness enforcement. It cannot
prevent assembly/native allocations, including definition resolution inside
restoring assembly, or bound later definition generation/export work.

The case record retains cap, all five counts, every offending component, accepted
or excluded status and explicit scope. An over-cap case raises `ExcludedCase`
before artifact dictionary initialization, common-basis lowering, metrics,
resolution or QPY writing. The existing handler persists status/reason in case
JSON and run.json, then continues. Rows accumulate locally and reach the global
table only after full case success, hence count-excluded cases have zero QPY
and zero rows. Diagnostic JSON is retained. Width/count acceptance does not
certify later export: later failures retain prior partial artifacts and zero
failed-case rows. Existing outputs are never deleted.

The source diff changes only the allowed config set, preflight, runner docstring
and pre-artifact gate. All 14 other function/class source segments and all 52
other library Python files match reviewer dependencies byte-for-byte. Existing
tests are an exact byte prefix of candidate tests. No metric column is added.
The acceptance gate reads integers and writes metadata; it does not change any
operation, phase, wire embedding or inverse. Omission bypasses the new branches
and enters the identical artifact pipeline.

Accordingly, the prior clean_tree/fresh_zero proof is preserved: a monomial
RCCX conjunction prefix P computes scratch with a phase while preserving controls
and external target; the exact final CCX changes only that target; actual P
inverse restores scratch and cancels phase. Clean-subspace column equality
extends to superposition/reference states by linearity, not to dirty scratch.
Actual emitted A inverse, signed -X^n MCZ X^n and ordered disjoint raw/A/S0
embedding remain unchanged. Diffusion is A(2|0><0|-I)A-dagger; search initializes
A once then repeats O,D. The independent saved-circuit checks below retain scalar
phase without alignment and ordered local wires. Tensoring identical local
definitions with identity and composing them proves wider emitted/readback
equality without a wide dense array. This does not prove arbitrary wide
original-to-transpiler equivalence or validate an unchecked backend predicate.

## Actual validation

Candidate regressions: **227 passed, 31 deliberately deselected, zero skips**.
Retained exclusions: 27 `matching_preparation_diffusion_and_search`, one
`r3_keeps_asymmetric_k5_preparation`, three
`native_asymmetric_constant_r3_and_complete_search`. Their wider dense coverage
is not replaced or admitted. Runtime guards reject circuit Operators above four
wires and Statevector.from_instruction above five; inspected direct evolve
fixtures also stay at most five wires. Existing scalar template and restoration
checks exercise wider circuits without dense allocations.

Independent instruction probes import no candidate test/reference helpers:

- 21 invalid values reject before forbidden input/run/assembly calls. Positive
  builtin 1, 17 and 10**100 validate. Omitted normalized config equals baseline.
- Twelve billion-count stand-in cases cover each component and simultaneous
  excess, with and without width cap. Noniterable count/width-only objects prove
  all five reads, ordering and no traversal. Resolver, lowering, metrics and QPY
  writer are patched to fail if called. Every offender/reason is persisted;
  excluded QPY and rows are zero. Width rejection separately forbids data access.
- Sixteen genuine isolated-k3 assemblies span sb_balanced/xag_bennett, R2/R3,
  j0/1 and default/restoring. Each identical assembled fixture is copied into
  admitted-baseline, omitted-cap and equality-with-width-cap runners. All **160
  artifact triples are byte-identical**, all 160 rows agree after dropping only
  measured lowering duration, and saved widths/counts/maps/depths/hashes are
  independently recounted. This avoids incidental fresh-name QPY differences;
  no unconditional claim about separately assembled fresh runs is made.
- **354 bounded Operator calls, 16 complete-register statevectors, 104 ordered
  composition comparisons**: original/saved components, signed diffusion,
  actual inverse, j0/1 assembly and independent amplitude amplification agree.
  Maximum entrywise error **5.65233285126159e-15**, tolerance 3e-11, no phase
  alignment. Operator count includes repeated/local references, not that many
  independent graph theorems. Semantic helpers adapt the preserved independent
  width review; new instruction/negative/evidence probes are written here.
- Genuine edge-k3 restoring j0 reserves widths raw=9, A=4, O=9, D=5, search=10;
  MCX live-capacity field is zero, with unused S0 scratch still reserved. Counts
  are **39,8,43,37,8** respectively. Cap8 excludes raw/O/D even though search
  fits; cap43 accepts. Ordered search equals A embedded once, and all five saved
  primary components preserve ordered definitions and phase. No 10-wire dense
  array is allocated. This injected-runner case uses an isolated-input config
  for acceptance coverage, not graph-benchmark provenance.
- Empty components all count zero and complete at cap1. A nested inverse with
  nonzero scalar phases and reversed wires counts once, exports three standard
  instructions, and matches the phase-sensitive four-wire operator. Barrier
  and opaque variants also count once and pass acceptance, then fail existing
  QPY resolution with explicit reasons, four retained partial QPY and zero rows.
  These synthetic components test control/codec behavior, not valid coloring.
- Default and restoring three-seed runs each produce failed/excluded/complete.
  Assembly failure has no instruction field; count exclusion has all counts;
  first two cases have zero QPY/rows. Only final complete case contributes ten
  rows; manifest remains complete_with_failures.

All **1,720 published worker evidence-file hashes** match. All actual worker
run manifests and case copies were reconciled, including omissions, width
short-circuits, assembly failures and partial export failures. The 62 instruction
records are 24 complete, 34 excluded, four failed. All 915 saved worker metric
rows across its tests/replay were independently recounted from QPY and hashes.
Repeated fixtures are records, not unique research instances. The worker's
baseline coloring_study.py plus adjacent runner.py/costs.py match reviewer
admitted baseline bytes, source SHA-256
`1b09d99a5591fe25cecb854930d489f0e0d8c914875c18bd1e504aea42d0559f`.

Unknown backend workspace, peak process memory and general live peaks remain
null/unavailable; native_combined still overlaps synthesis. No research metric,
historical table or performance result changes. Candidate final Black/Ruff checks
on these hashes were inspected, not counted as independent reruns. No full suite,
mypy, build, notebook, replay, routing, FT or complete study is claimed.

## Resources, failures and preservation

Existing interpreter: `/Users/mar/codex-work/logique/.venv/bin/python` only.
PYTHONPATH resolves to reviewer worktree `src`; bootstrap first retains its
admitted baseline, then loads exact sibling candidate bytes into the canonical
module slot. Candidate path/hash are asserted; other dependencies resolve to
reviewer src and are byte-identical. No copying into maintained source occurred.
Cache: `/Users/mar/codex-work/logique/.cache/epfl`. Explicit private executable:
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`,
SHA-256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Root old binary remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.

Numerical commands ran sequentially, one supervised numerical pipeline with
synchronous native calls, all BLAS/OpenMP/Accelerate/MKL/NumExpr threads=1.
Per-command timeout<=120s, cumulative<=300s. Actual tests **21.654335s**, RSS
**226623488 bytes**; independent harness **13.255788s**, RSS **181895168 bytes**.
Total **34.910122s**. These fixed fixtures stay below 8 GiB measured child RSS;
this is not an enforced aggregate memory cap or OS-wide process visibility.
Operators<=4, full statevectors<=5; wider checks use ordered composition/local
scalar proofs. No compiler. Exact argv/cwd/env/exits/time/RSS follow inline.

Failures retained: initial ls found no own review, establishing incomplete intake;
oversized combined plan/queue/review reads truncated, followed by bounded sections,
full JSON parsing and inventories. No independent numerical failure, timeout or
OOM occurred. Expected invalid configs, deliberate assembly failure, width/count
exclusions and later opaque/barrier failures remain explicit saved evidence.
Worker Ruff E731 and subsequent Black blank-line failures were corrected before
final checks, with their recorded failure history retained. Earlier width/QPY/
restoring harness failures, mixed-register QPY errors and archived unsafe pilot
outputs remain untouched and unadmitted, not silently treated as passing cases.

Initial `git add -- INSTRUCTION_CONTROL_REVIEW.md` was sandbox-denied at the
shared worktree index.lock. Scoped automatic escalation then staged only the
authorized review. Staged whitespace and single-file scope checks passed;
no automatic approval rejection occurred. The commit uses the same explicit path.

The first read-only post-commit finalizer rejected inline bootstrap.py because
its fence extractor omits the terminal newline while its assertion added one.
Protected identities had passed; no release/inventory write occurred. Corrected
comparison checks exact content excluding that terminal newline. This tooling
failure is retained in RUN/finalizer-initial-failure.txt; no code or numerical
test changed or reran.

Before/after audit verifies **2,856 protected identities**, including candidate
source/tests/checkpoint/evidence, root/user README edits, prototype backups,
archived manuscript outputs, nested histories, lockfiles, admitted reviews and
both native binaries. All external index entries/gitlinks match. Queue remains
SHA-256 `d0e7af5d7660f56d4e7f2a82a33eb3adbead390165fc8519fc7c452fa9bd6b49`;
all recorded job states remain unchanged. Only dispatcher usage timestamps may
refresh independently. Root status remains its existing README modification;
candidate worktree stays clean. No queue/state/manifest edits, job append,
integration, agents/model/Codex launches, API/credits/paid fallback, sync/install,
build/dependency changes, hardware, pushes or publishing occurred.

## Admission limits and handoff

This admits the exact additive count gate on the already admitted assembly/QPY
contract only. Clean_tree/fresh_zero retains fresh clean scratch, original k<=8,
data<=21, j0..2, MCX3..20, operation width<=21, definition depth<=32 and
visits<=100000 per resolver. Backend validation remains its own obligation;
sampled coverage remains sampled. Other policies/borrowing, optimized live peaks,
memory/timeout control, arbitrary opaque/unbound/dynamic/classical/adversarial
standard operations, general wide transpiler equivalence and archived-pilot
repair remain excluded. Passing the count gate is not QPY scientific admission.

Rotation source/test hashes remain
`5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595` /
`88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77`.
Its numerical/caller obligations are unchanged: no interval certificate,
ideal-amplitude guarantee, RUS admission or blanket paper approval.

**Next:** dispatcher releases the already queued
`coordinate-component-instructions-1026172157` to verify exact candidate/review
bytes, preserve this independent review and integrate only owned correctness
commit f16b4d1 on coloring-paper-revamp-codex. Reviewer does not integrate, append
jobs or push. Dispatcher alone launches models and pushes integration HEAD.
Changed bytes or broader contract require fresh review. No next native/structure/
FT/RUS slice is assigned here. On completed-own-handoff repeat, verify review
commit, exact candidate/evidence/protection and unique coordinator handoff, then
release COMPLETE without tests/jobs. Further controls, affected old QPY evidence,
full studies, protocol freeze and the full paper remain unfinished.

## Preserved executable evidence and results

The exact executed probes and results follow. Replay requires a separately
authorized fresh timestamped run; never overwrite this RUN or repeat a completed
handoff. Bootstrap/supervisor/bounds wrapper adapt the preserved width review;
the instruction probes and evidence reconciliation are contained in independent.py.

| RUN evidence | SHA-256 |
| --- | --- |
| `bootstrap.py` | `c28747439cfc969384d6b08d0db0337b40a1caeac0ffd6bc19e06055bbad1da1` |
| `supervisor.py` | `72cb0947456ddf77974edb82311d7401e0924450de7e59b854777997cd79ba18` |
| `run_tests.py` | `18883c807160eab8ed5249629369e4953d71cc0428b659daa09a1f16b233b670` |
| `independent.py` | `68da036e51c2b5c6049e1879c8513c2d39b4cc983bae1cdd9a04faa4606266dc` |
| `audit.py` | `3781b160cc00d040e83738c99ed30f560b76ee4da252802e61dd81244d66a98d` |
| `independent-results.json` | `b1ed22cbb1012962d76d8abaa867b45ee5f0108abd961c037a792011cee288a6` |
| `commands.jsonl` | `df47c8368d1662028c4b7af4203dd63f8465e402faa9676d260db0f2c0da7948` |
| `candidate-tests.log` | `a25d09ba4cc6452f9d9815c08278e863e5e9e5f7a31a872196ff8dbe53412072` |
| `protected.json` | `6fb242fba98c3222975be356f8ff83dab452c596a28cc6c31f7b803a158ec118` |
| `intake.json` | `83cae2b144c2aa9b78e4200a87cc26bd3aa089d2f597606e6e361aab9be3b1e0` |
| `verification.json` | `5908eaffbe2b3c04ae158f8c841b5208018b6c3898a842f2d94e5b9c9e13da14` |

### bootstrap.py

```python
"""Load read-only candidate bytes over hash-identical reviewer dependencies."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys

W = Path.cwd()
C = W.parent / "component-instructions"
R = Path(__file__).resolve().parent
assert Path(os.environ["PYTHONPATH"]).resolve() == W / "src"
from logique.benchmarks import coloring_study as baseline

assert Path(baseline.__file__).resolve() == W / "src/logique/benchmarks/coloring_study.py"
path = C / "src/logique/benchmarks/coloring_study.py"
assert hashlib.sha256(path.read_bytes()).hexdigest() == "ea57eeea1541720f552ebbb3fd2d64b108e85e803923cad6a63fbbeb2336df32"
name = "logique.benchmarks.coloring_study"
spec = importlib.util.spec_from_file_location(name, path)
candidate = importlib.util.module_from_spec(spec)
sys.modules[name] = candidate
spec.loader.exec_module(candidate)
import logique.benchmarks
logique.benchmarks.coloring_study = candidate
assert Path(candidate.__file__).resolve() == path
```

### supervisor.py

```python
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

R = Path(__file__).resolve().parent
records = R / "commands.jsonl"
used = sum(json.loads(x)["seconds"] for x in records.read_text().splitlines()) if records.exists() else 0
assert used < 300
env = dict(os.environ, PYTHONPATH=str(Path.cwd() / "src"),
           LOGIQUE_CACHE="/Users/mar/codex-work/logique/.cache/epfl",
           LOGIQUE_NATIVE_EXECUTABLE="/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis",
           PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
           MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
label, argv = sys.argv[1], sys.argv[2:]
start = time.monotonic()
with (R / (label + ".log")).open("w") as out:
    child = subprocess.Popen(argv, env=env, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        code = child.wait(timeout=min(120, 300-used))
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        code = child.wait()
rec = dict(label=label, argv=argv, cwd=os.getcwd(), seconds=time.monotonic()-start,
           exit_code=code, child_max_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
           environment={k: env[k] for k in ("PYTHONPATH", "LOGIQUE_CACHE", "LOGIQUE_NATIVE_EXECUTABLE", "PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")})
with records.open("a") as f:
    f.write(json.dumps(rec)+"\n")
print(json.dumps(rec))
print((R / (label + ".log")).read_text()[-5000:])
sys.exit(code)
```

### run_tests.py

```python
from bootstrap import candidate, C
import sys
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
import pytest

old_op = Operator.__init__
def bounded_op(self, data, *a, **kw):
    if hasattr(data, "num_qubits"):
        assert data.num_qubits <= 4, data.num_qubits
    old_op(self, data, *a, **kw)
Operator.__init__ = bounded_op
old_sv = Statevector.from_instruction
def bounded_sv(data):
    assert data.num_qubits <= 5, data.num_qubits
    return old_sv(data)
Statevector.from_instruction = staticmethod(bounded_sv)
sys.exit(pytest.main(sys.argv[1:]))
```

### independent.py

```python
"""Independent instruction gate probes; no candidate test/reference helpers."""
from bootstrap import candidate as s, baseline as b, R, W, C
import ast, copy, csv, hashlib, itertools, json, math
from collections import Counter
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Gate
from qiskit.quantum_info import Operator, Statevector
from logique.benchmarks import metrics, runner
from logique.coloring import ColoringProblem

names = ('raw', 'preparation', 'oracle', 'diffusion', 'search')
report = dict(invalid=[], gates=[], compatibility=0, artifacts=0, operators=0,
              vectors=0, compositions=0, max_error=0.0, granularity=[], mixed=[])
source=R/'isolated.col';source.write_text('p edge 1 0\nx colors 3\n')
serial=0
def cfg(label, **kw):
    global serial
    serial+=1
    return dict(inputs=[str(source)],methods=['sb_balanced'],regimes=['R2'],
                iterations=[0],seeds=[7],output=str(R/f'{datetime.now():%m%d%H%M%S}-{label}-{serial}'),**kw)
def forbidden(*a,**kw):raise AssertionError('forbidden input/downstream traversal')
def contents(out):
    m=json.loads((out/'run.json').read_text())
    for rec in m['cases']:
        assert rec==json.loads((out/(rec['name']+'.json')).read_text())
    rows=list(csv.DictReader((out/'summary.csv').open())) if (out/'summary.csv').exists() else []
    return m,rows
def reject_artifacts(out,rec,rows):
    assert not rec.get('artifacts') and not list(out.glob(rec['name']+'*.qpy'))
    assert not [r for r in rows if int(r['seed'])==rec['seed']]
class SubInt(int):pass
invalid=[None,False,True,0,-1,-10**100,1.0,1.5,np.nan,np.inf,-np.inf,'1','',[],{},(),{1},complex(1),SubInt(1),np.int64(1),np.uint64(1)]
for value in invalid:
    config=cfg('invalid',max_component_instructions=value)
    with patch.object(s,'read_dimacs',forbidden),patch.object(s,'assemble_case',forbidden),patch.object(runner,'new_run_directory',forbidden):
        try:s.run_coloring_study(config)
        except ValueError as error:assert str(error)=='max_component_instructions must be a positive integer'
        else:raise AssertionError(('accepted invalid',value))
    assert not Path(config['output']).exists();report['invalid'].append(repr(value))
for value in (1,17,10**100):
    assert s.validate_study_config(dict(inputs=['missing.col'],max_component_instructions=value))['max_component_instructions']==value
assert s.CONFIG_FIELDS-b.CONFIG_FIELDS=={'max_component_instructions'}
assert s.validate_study_config(dict(inputs=['missing.col']))==b.validate_study_config(dict(inputs=['missing.col']))

# Width and count-only fixtures have no iterable instructions or definitions.
class Count:
    def __init__(self,n,k,events):self.n,self.k,self.events=n,k,events
    def __len__(self):self.events.append(('count',self.n));return self.k
    def __iter__(self):return forbidden()
class Shell:
    def __init__(self,n,k,width,events):self.n,self.k,self.width,self.events=n,k,width,events
    @property
    def num_qubits(self):self.events.append(('width',self.n));return self.width
    @property
    def data(self):return Count(self.n,self.k,self.events)
for width_enabled,bad in itertools.product((False,True),[*names,'all']):
    events=[];counts={n:10**9 if bad in (n,'all') else 7 for n in names}
    shell=s.ColoringStudyCase(*(Shell(n,counts[n],3,events) for n in names),metadata={})
    with ExitStack() as stack:
        stack.enter_context(patch.object(s,'assemble_case',return_value=shell))
        for module,name in ((s,'_resolved_qpy_circuit'),(metrics,'lower_circuit'),(metrics,'circuit_metrics'),(qpy,'dump')):
            stack.enter_context(patch.object(module,name,forbidden))
        out=s.run_coloring_study(cfg('excluded',max_component_instructions=7,common_basis=True,**({'max_component_qubits':3} if width_enabled else {})))
    m,rows=contents(out);rec=m['cases'][0];ck=rec['component_instruction_check']
    expected_events=([('width',n) for n in names] if width_enabled else [])+[('count',n) for n in names]
    assert events==expected_events,events
    assert ck['top_level_instructions']==counts and ck['max_component_instructions']==7
    assert ck['over_budget_components']==[n for n in names if counts[n]>7]
    assert ck['status']==rec['status']=='excluded'
    for n in ck['over_budget_components']:assert f'{n}={counts[n]}' in rec['reason']
    assert 'mixed granularity' in ck['scope'] and 'not elementary gates' in ck['scope']
    reject_artifacts(out,rec,rows);report['gates'].append(dict(width=width_enabled,bad=bad,events=events,check=ck))
events=[]
class WidthOnly:
    @property
    def num_qubits(self):events.append('width');return 4
    @property
    def data(self):return forbidden()
with patch.object(s,'assemble_case',return_value=s.ColoringStudyCase(*(WidthOnly() for _ in names),metadata={})),patch.object(s,'_resolved_qpy_circuit',forbidden):
    out=s.run_coloring_study(cfg('width-first',max_component_qubits=3,max_component_instructions=1))
m,rows=contents(out);rec=m['cases'][0]
assert events==['width']*5 and rec['status']=='excluded' and 'component_instruction_check' not in rec
reject_artifacts(out,rec,rows);report['width_short_circuit']=rec['component_width_check']

# Ordered recursive reference, adapted from the preserved independent width
# review. Expansion here verifies semantics, NEVER computes the acceptance count.
def flat(q):
    ops=[];phase=0.0
    def visit(c,w,depth=0):
        nonlocal phase
        assert depth<=32
        phase+=float(c.global_phase)
        for it in c.data:
            op=it.operation;loc=tuple(w[c.find_bit(x).index] for x in it.qubits)
            closed=getattr(op,'ctrl_state',None) in (None,(1<<getattr(op,'num_ctrl_qubits',0))-1)
            if op.base_class.__module__.startswith('qiskit.circuit.library.standard_gates.') and closed:
                ops.append((op.base_class.__module__,op.base_class.__name__,tuple(complex(x) for x in op.params),getattr(op,'ctrl_state',None),loc))
            else:
                assert op.definition is not None
                visit(op.definition,loc,depth+1)
    visit(q,tuple(range(q.num_qubits)));return ops,np.exp(1j*phase)
def close(x,y):
    error=float(np.max(abs(np.asarray(x)-np.asarray(y))));report['max_error']=max(report['max_error'],error);assert error<3e-11,error
def comp(x,y):
    a,p=flat(x);z,r=flat(y);assert x.num_qubits==y.num_qubits and a==z;close(p,r);report['compositions']+=1
def mat(q):
    assert q.num_qubits<=4;report['operators']+=1;return Operator(q).data
def load(path):
    with path.open('rb') as f:return qpy.load(f)[0]
def recount(q):
    clocks=[0]*q.num_qubits;counts=Counter()
    for it in q.data:
        assert it.operation.name not in ('measure','barrier')
        counts[it.operation.name]+=1;w=[q.find_bit(x).index for x in it.qubits]
        t=1+max((clocks[x] for x in w),default=0)
        for x in w:clocks[x]=t
    return q.num_qubits,sum(counts.values()),max(clocks,default=0),dict(counts)

for method,regime,j,restoring in itertools.product(('sb_balanced','xag_bennett'),('R2','R3'),(0,1),(False,True)):
    controls=dict(mcx_decomposition='clean_tree',mcx_workspace='fresh_zero') if restoring else {}
    case=s.assemble_case(ColoringProblem((1,),(),3),method,regime,iterations=j,**controls)
    counts={n:len(q.data) for n,q in case.circuits.items()};cap=max(counts.values());width=max(q.num_qubits for q in case.circuits.values())
    assert width<=5
    outputs=[]
    for module,label,extra in ((b,'baseline',{}),(s,'omission',{}),(s,'equality',dict(max_component_instructions=cap,max_component_qubits=width))):
        config=cfg(label,common_basis=True,optimization_level=0,**controls,**extra);config.update(methods=[method],regimes=[regime],iterations=[j])
        with patch.object(module,'assemble_case',side_effect=lambda *a,**kw:copy.deepcopy(case)):
            outputs.append(module.run_coloring_study(config))
    tables=[]
    for idx,out in enumerate(outputs):
        m,rows=contents(out);rec=m['cases'][0];assert rec['status']=='complete'
        if idx<2:assert 'max_component_instructions' not in m['config'] and 'component_instruction_check' not in rec
        else:
            ck=rec['component_instruction_check'];assert ck['status']=='accepted' and not ck['over_budget_components'] and ck['top_level_instructions']==counts
            assert rec['component_width_check']['status']=='accepted'
        assert rec['peak_memory']==dict(status='unavailable',bytes=None)
        assert rec['stage_timings']['native_combined']['included_in']=='synthesis'
        tables.append([{k:v for k,v in r.items() if k!='lowering_seconds'} for r in rows])
    assert tables[0]==tables[1]==tables[2] and len(tables[0])==10
    for row in tables[2]:
        filename=row['artifact'];assert len({(out/filename).read_bytes() for out in outputs})==1
        saved=load(outputs[2]/filename);q=case.circuits[row['component']]
        assert recount(saved)==(int(row['qubits']),int(row['gates']),int(row['depth']),ast.literal_eval(row['gate_types']))
        assert hashlib.sha256((outputs[2]/filename).read_bytes()).hexdigest()==rec['artifact_statistics'][filename]['sha256']
        if row['metric_level']!='common_basis':comp(q,saved)
        if saved.num_qubits<=4:close(mat(q),mat(saved))
        report['artifacts']+=1
    a=mat(case.preparation);sign=-np.eye(len(a));sign[0,0]=1
    close(mat(case.diffusion),a@sign@a.conj().T)
    expected=QuantumCircuit(case.search.num_qubits);data=case.metadata['data_qubits']
    em=case.metadata['mcx_lowering']['search_embeddings'] if restoring else dict(preparation=data,oracle=list(range(case.oracle.num_qubits)),diffusion=data)
    expected.compose(case.preparation,em['preparation'],inplace=True)
    for _ in range(j):expected.compose(case.oracle,em['oracle'],inplace=True);expected.compose(case.diffusion,em['diffusion'],inplace=True)
    comp(expected,case.search)
    initial=a[:,0];amplitudes=initial.copy();marked=np.array([x<3 or regime=='R3' for x in range(4)])
    for _ in range(j):amplitudes[marked]*=-1;amplitudes=2*initial*np.vdot(initial,amplitudes)-amplitudes
    physical=np.zeros(1<<width,dtype=complex)
    for x,v in enumerate(amplitudes):physical[sum(((x>>i)&1)<<w for i,w in enumerate(data))]=v
    assert case.search.num_qubits<=5;close(Statevector.from_instruction(case.search).data,physical);report['vectors']+=1
    report['compatibility']+=1

# Real wider j0 has unused O/D and reserved pools, yet every component counts.
controls=dict(mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
edge=s.assemble_case(ColoringProblem((-7,20),((-7,20),),3),'sb_balanced','R2',iterations=0,**controls)
counts={n:len(q.data) for n,q in edge.circuits.items()};widths={n:q.num_qubits for n,q in edge.circuits.items()}
assert edge.metadata['mcx_lowering']['search_scratch_ownership']['zero_reflection']
assert edge.metadata['component_workspace']['search']['mcx_live_peak_upper_bound']==0
expected=QuantumCircuit(edge.search.num_qubits);expected.compose(edge.preparation,edge.metadata['mcx_lowering']['search_embeddings']['preparation'],inplace=True);comp(expected,edge.search)
statuses=[]
for cap in (counts['search'],max(counts.values())):
    with patch.object(s,'assemble_case',side_effect=lambda *a,**kw:copy.deepcopy(edge)):
        out=s.run_coloring_study(cfg('reserved',max_component_instructions=cap,max_component_qubits=max(widths.values()),**controls))
    m,rows=contents(out);rec=m['cases'][0];statuses.append(rec['status'])
    assert rec['component_instruction_check']['top_level_instructions']==counts
    if rec['status']=='excluded':reject_artifacts(out,rec,rows)
    else:
        for n,q in edge.circuits.items():comp(q,load(out/rec['artifacts'][n+'_restoring_mcx']))
assert statuses==['excluded','complete'];report['reserved']=dict(counts=counts,widths=widths,statuses=statuses)

# A count of one does not admit opaque export; empty circuits count zero.
tiny=s.assemble_case(ColoringProblem((1,),(),3),'sb_balanced','R2',iterations=0)
for fault in ('empty','nested','barrier','opaque'):
    case=copy.deepcopy(tiny)
    for n,q in case.circuits.items():setattr(case,n,QuantumCircuit(q.num_qubits))
    if fault=='nested':
        body=QuantumCircuit(2,global_phase=.317);body.h(1);body.cx(1,0);body.rz(.43,0)
        outer=QuantumCircuit(2,global_phase=-.219);outer.append(body.to_gate().inverse(),[1,0])
        case.search.append(outer.to_gate().inverse(),[1,0])
    elif fault=='barrier':case.search.barrier()
    elif fault=='opaque':case.search.append(Gate('review_opaque',1,[]),[0])
    counts={n:len(q.data) for n,q in case.circuits.items()}
    with patch.object(s,'assemble_case',return_value=case):out=s.run_coloring_study(cfg(fault,max_component_instructions=1))
    m,rows=contents(out);rec=m['cases'][0];ck=rec['component_instruction_check']
    assert ck['top_level_instructions']==counts and ck['status']=='accepted'
    if fault in ('barrier','opaque'):
        assert rec['status']=='failed' and fault in rec['reason'] and not rows
        assert len(list(out.glob('*.qpy')))==4 and len(rec['artifacts'])==4
    else:
        assert rec['status']=='complete' and len(rows)==5
        saved=load(out/rec['artifacts']['search_logical']);comp(case.search,saved)
        if fault=='nested':
            assert len(saved.data)>1;close(mat(case.search),mat(saved))
    report['granularity'].append(dict(fault=fault,counts=counts,status=rec['status'],reason=rec.get('reason'),qpy=len(list(out.glob('*.qpy')))))

for restoring in (False,True):
    controls=dict(mcx_decomposition='clean_tree',mcx_workspace='fresh_zero') if restoring else {}
    tiny=s.assemble_case(ColoringProblem((1,),(),3),'sb_balanced','R2',iterations=1,**controls)
    cap=max(len(q.data) for q in tiny.circuits.values());width=max(q.num_qubits for q in tiny.circuits.values())
    def outcomes(*a,seed,**kw):
        if seed==1:raise RuntimeError('independent assembly failure')
        case=copy.deepcopy(tiny)
        if seed==2:case.oracle=SimpleNamespace(num_qubits=width,data=range(cap+1))
        return case
    config=cfg('mixed',max_component_instructions=cap,max_component_qubits=width,common_basis=True,**controls);config.update(seeds=[1,2,3],iterations=[1])
    with patch.object(s,'assemble_case',side_effect=outcomes):out=s.run_coloring_study(config)
    m,rows=contents(out);assert [r['status'] for r in m['cases']]==['failed','excluded','complete']
    assert m['status']=='complete_with_failures' and len(rows)==10 and {r['seed'] for r in rows}=={'3'}
    assert 'component_instruction_check' not in m['cases'][0]
    for rec in m['cases'][:2]:reject_artifacts(out,rec,rows)
    report['mixed'].append(dict(restoring=restoring,statuses=[r['status'] for r in m['cases']],reasons=[r.get('reason') for r in m['cases']],rows=len(rows)))

# Recount every saved worker metric row; independently reconcile case/manifest
# copies, failures, exclusions, partial artifacts and the saved instruction ledger.
E=C/'dump/1027032744-component-instructions';statuses=Counter();worker_rows=0;ledger=[]
for path in sorted(E.rglob('run.json')):
    m,rows=contents(path.parent)
    for rec in m['cases']:
        matched=[r for r in rows if r['artifact'].startswith(rec['name']+'_')]
        if rec['status']!='complete':assert not matched
        ck=rec.get('component_instruction_check')
        if ck:
            statuses[rec['status']]+=1
            assert ck['over_budget_components']==[n for n,k in ck['top_level_instructions'].items() if k>ck['max_component_instructions']]
            if ck['status']=='excluded':assert rec['status']=='excluded';reject_artifacts(path.parent,rec,matched)
            ledger.append(dict(manifest=str(path),name=rec['name'],check=ck,status=rec['status']))
        for row in matched:
            artifact=path.parent/row['artifact'];q=load(artifact)
            assert recount(q)==(int(row['qubits']),int(row['gates']),int(row['depth']),ast.literal_eval(row['gate_types']))
            assert hashlib.sha256(artifact.read_bytes()).hexdigest()==rec['artifact_statistics'][row['artifact']]['sha256'];worker_rows+=1
old=json.loads((E/'instruction-ledger-final.json').read_text())
assert {(x['manifest'],x['name']):x['check'] for x in ledger}=={(x['manifest'],x['name']):x['check'] for x in old}
report['worker']=dict(statuses=dict(statuses),records=len(ledger),rows=worker_rows)
report['status']='passed';(R/'independent-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
```

### audit.py

```python
"""Read-only identity/protection audit; never modifies prior evidence."""
import ast, hashlib, json, subprocess
from pathlib import Path
W=Path.cwd();C=W.parent/'component-instructions';R=Path(__file__).resolve().parent
ROOT=Path('/Users/mar/codex-work/logique');E=C/'dump/1027032744-component-instructions'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((R/'protected.json').read_text())
for p,h in protected.items():assert sha(Path(p))==h,p
evidence=json.loads((E/'evidence-hashes.json').read_text())
for p,h in evidence.items():assert sha(E/p)==h,p
expected={'src/logique/benchmarks/coloring_study.py':'ea57eeea1541720f552ebbb3fd2d64b108e85e803923cad6a63fbbeb2336df32','tests/test_coloring_study.py':'4ff6060d07b67bd76efbb3f240f8138c10360d2749fc2287ba4522ff00ab5346'}
for p,h in expected.items():
    assert sha(C/p)==h
    assert hashlib.sha256(subprocess.check_output(['git','show','f16b4d1:'+p])).hexdigest()==h
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'],text=True)==''
assert (E/'baseline/coloring_study.py').read_bytes()==(W/'src/logique/benchmarks/coloring_study.py').read_bytes()
for name in ('runner.py','costs.py'):
    assert (E/'baseline'/name).read_bytes()==(W/'src/logique/benchmarks'/name).read_bytes()
dependency_count=0
for p in (C/'src').rglob('*.py'):
    rel=p.relative_to(C)
    if str(rel)=='src/logique/benchmarks/coloring_study.py':continue
    assert p.read_bytes()==(W/rel).read_bytes(),str(rel);dependency_count+=1
def segments(p):
    source=p.read_text();return {n.name:ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a=segments(W/'src/logique/benchmarks/coloring_study.py');b=segments(C/'src/logique/benchmarks/coloring_study.py')
unchanged=[n for n in a if a[n]==b[n]]
assert set(a)-set(unchanged)=={'validate_study_config','run_coloring_study'}
assert (C/'tests/test_coloring_study.py').read_bytes().startswith((W/'tests/test_coloring_study.py').read_bytes())
for base in (W,C,ROOT):
    assert subprocess.check_output(['git','-C',str(base),'ls-files','--stage','external'])==subprocess.check_output(['git','ls-files','--stage','external'])
queue_path=ROOT/'dump/1025021922-coloring-auto-dispatch/queue.json'
q=json.loads(queue_path.read_text());state=json.loads(queue_path.with_name('state.json').read_text())
assert q==json.loads((R/'queue-intake.json').read_text())
before=json.loads((R/'state-intake.json').read_text());assert state['jobs']==before['jobs']
for name in ('component-instructions-1026172157','component-instructions-review-1026172157','coordinate-component-instructions-1026172157'):
    assert sum(j['id']==name for j in q['jobs'])==1
for name in ('coordinate-stage-controls-1025034429','coordinate-qpy-1025074732','coordinate-restoring-mcx-1025125442','coordinate-component-width-1026071418'):
    assert state['jobs'][name]['status']=='complete'
for name in ('qpy_semantic_review','qpy_semantic_admission','qpy_representation_changes','restoring_mcx_review','restoring_mcx_admission','restoring_mcx_representation_changes','component_width_review','component_width_admission','rotation_norm_admission'):
    assert (W/f'docs/research/{name}.md').read_bytes()==(ROOT/f'docs/research/{name}.md').read_bytes()
commands=[json.loads(x) for x in (R/'commands.jsonl').read_text().splitlines()]
report=dict(status='passed',protected=len(protected),worker_evidence=len(evidence),unchanged_dependencies=dependency_count,unchanged_definitions=unchanged,
            candidate_hashes=expected,checkpoint_sha256=sha(C/'INSTRUCTION_CONTROL_CHECKPOINT.md'),
            queue_jobs=len(q['jobs']),state_records=len(state['jobs']),queue_sha256=sha(queue_path),
            numerical_seconds=sum(x['seconds'] for x in commands),max_child_rss_bytes=max(x['child_max_rss_bytes'] for x in commands),
            state_jobs_unchanged=True,root_git_status=subprocess.check_output(['git','-C',str(ROOT),'status','--short'],text=True))
(R/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'state-final.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(report,indent=2))
```

### independent-results.json

```json
{
  "invalid": [
    "None",
    "False",
    "True",
    "0",
    "-1",
    "-10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "1.0",
    "1.5",
    "nan",
    "inf",
    "-inf",
    "'1'",
    "''",
    "[]",
    "{}",
    "()",
    "{1}",
    "(1+0j)",
    "1",
    "np.int64(1)",
    "np.uint64(1)"
  ],
  "gates": [
    {
      "width": false,
      "bad": "raw",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 1000000000,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "raw"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": false,
      "bad": "preparation",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 1000000000,
          "oracle": 7,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "preparation"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": false,
      "bad": "oracle",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 1000000000,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "oracle"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": false,
      "bad": "diffusion",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 1000000000,
          "search": 7
        },
        "over_budget_components": [
          "diffusion"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": false,
      "bad": "search",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 7,
          "search": 1000000000
        },
        "over_budget_components": [
          "search"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": false,
      "bad": "all",
      "events": [
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 1000000000,
          "preparation": 1000000000,
          "oracle": 1000000000,
          "diffusion": 1000000000,
          "search": 1000000000
        },
        "over_budget_components": [
          "raw",
          "preparation",
          "oracle",
          "diffusion",
          "search"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "raw",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 1000000000,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "raw"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "preparation",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 1000000000,
          "oracle": 7,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "preparation"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "oracle",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 1000000000,
          "diffusion": 7,
          "search": 7
        },
        "over_budget_components": [
          "oracle"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "diffusion",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 1000000000,
          "search": 7
        },
        "over_budget_components": [
          "diffusion"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "search",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 7,
          "preparation": 7,
          "oracle": 7,
          "diffusion": 7,
          "search": 1000000000
        },
        "over_budget_components": [
          "search"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    },
    {
      "width": true,
      "bad": "all",
      "events": [
        [
          "width",
          "raw"
        ],
        [
          "width",
          "preparation"
        ],
        [
          "width",
          "oracle"
        ],
        [
          "width",
          "diffusion"
        ],
        [
          "width",
          "search"
        ],
        [
          "count",
          "raw"
        ],
        [
          "count",
          "preparation"
        ],
        [
          "count",
          "oracle"
        ],
        [
          "count",
          "diffusion"
        ],
        [
          "count",
          "search"
        ]
      ],
      "check": {
        "max_component_instructions": 7,
        "top_level_instructions": {
          "raw": 1000000000,
          "preparation": 1000000000,
          "oracle": 1000000000,
          "diffusion": 1000000000,
          "search": 1000000000
        },
        "over_budget_components": [
          "raw",
          "preparation",
          "oracle",
          "diffusion",
          "search"
        ],
        "status": "excluded",
        "scope": "post-assembly, post-width acceptance of unexpanded top-level emitted instructions at current mixed granularity, including barriers; opaque/nested instructions count once; not elementary gates, complexity, resolved artifact size, cost, memory, timeout, depth or liveness enforcement; does not prevent assembly/native allocations or bound later definition generation/export work"
      }
    }
  ],
  "compatibility": 16,
  "artifacts": 160,
  "operators": 354,
  "vectors": 16,
  "compositions": 104,
  "max_error": 5.65233285126159e-15,
  "granularity": [
    {
      "fault": "empty",
      "counts": {
        "raw": 0,
        "preparation": 0,
        "oracle": 0,
        "diffusion": 0,
        "search": 0
      },
      "status": "complete",
      "reason": null,
      "qpy": 5
    },
    {
      "fault": "nested",
      "counts": {
        "raw": 0,
        "preparation": 0,
        "oracle": 0,
        "diffusion": 0,
        "search": 1
      },
      "status": "complete",
      "reason": null,
      "qpy": 5
    },
    {
      "fault": "barrier",
      "counts": {
        "raw": 0,
        "preparation": 0,
        "oracle": 0,
        "diffusion": 0,
        "search": 1
      },
      "status": "failed",
      "reason": "ValueError: Unsupported opaque QPY operation: barrier",
      "qpy": 4
    },
    {
      "fault": "opaque",
      "counts": {
        "raw": 0,
        "preparation": 0,
        "oracle": 0,
        "diffusion": 0,
        "search": 1
      },
      "status": "failed",
      "reason": "ValueError: Unsupported opaque QPY operation: review_opaque",
      "qpy": 4
    }
  ],
  "mixed": [
    {
      "restoring": false,
      "statuses": [
        "failed",
        "excluded",
        "complete"
      ],
      "reasons": [
        "RuntimeError: independent assembly failure",
        "max_component_instructions=19 exceeded by oracle=20; post-assembly top-level instruction acceptance",
        null
      ],
      "rows": 10
    },
    {
      "restoring": true,
      "statuses": [
        "failed",
        "excluded",
        "complete"
      ],
      "reasons": [
        "RuntimeError: independent assembly failure",
        "max_component_instructions=28 exceeded by oracle=29; post-assembly top-level instruction acceptance",
        null
      ],
      "rows": 10
    }
  ],
  "width_short_circuit": {
    "max_component_qubits": 3,
    "allocated_qubits": {
      "raw": 4,
      "preparation": 4,
      "oracle": 4,
      "diffusion": 4,
      "search": 4
    },
    "over_budget_components": [
      "raw",
      "preparation",
      "oracle",
      "diffusion",
      "search"
    ],
    "status": "excluded",
    "scope": "post-assembly allocated component widths, including unused/reserved pools; not live workspace or process-memory enforcement; does not prevent assembly/native allocation"
  },
  "reserved": {
    "counts": {
      "raw": 39,
      "preparation": 8,
      "oracle": 43,
      "diffusion": 37,
      "search": 8
    },
    "widths": {
      "raw": 9,
      "preparation": 4,
      "oracle": 9,
      "diffusion": 5,
      "search": 10
    },
    "statuses": [
      "excluded",
      "complete"
    ]
  },
  "worker": {
    "statuses": {
      "complete": 24,
      "failed": 4,
      "excluded": 34
    },
    "records": 62,
    "rows": 915
  },
  "status": "passed"
}
```

### commands.jsonl

```text
{"label": "candidate-tests", "argv": ["/Users/mar/codex-work/logique/.venv/bin/python", "dump/1027033804-component-instructions-review/run_tests.py", "../component-instructions/tests/test_coloring_study.py", "-k", "not matching_preparation_diffusion_and_search and not r3_keeps_asymmetric_k5_preparation and not native_asymmetric_constant_r3_and_complete_search", "--basetemp=dump/1027033804-component-instructions-review/test-artifacts", "-p", "no:cacheprovider", "-q"], "cwd": "/Users/mar/codex-work/logique/dump/1026172157-component-width-coordinator-triage/worktrees/component-instructions-review", "seconds": 21.654334540944546, "exit_code": 0, "child_max_rss_bytes": 226623488, "environment": {"PYTHONPATH": "/Users/mar/codex-work/logique/dump/1026172157-component-width-coordinator-triage/worktrees/component-instructions-review/src", "LOGIQUE_CACHE": "/Users/mar/codex-work/logique/.cache/epfl", "LOGIQUE_NATIVE_EXECUTABLE": "/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis", "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}}
{"label": "independent", "argv": ["/Users/mar/codex-work/logique/.venv/bin/python", "dump/1027033804-component-instructions-review/independent.py"], "cwd": "/Users/mar/codex-work/logique/dump/1026172157-component-width-coordinator-triage/worktrees/component-instructions-review", "seconds": 13.255787792149931, "exit_code": 0, "child_max_rss_bytes": 181895168, "environment": {"PYTHONPATH": "/Users/mar/codex-work/logique/dump/1026172157-component-width-coordinator-triage/worktrees/component-instructions-review/src", "LOGIQUE_CACHE": "/Users/mar/codex-work/logique/.cache/epfl", "LOGIQUE_NATIVE_EXECUTABLE": "/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis", "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}}
```

### candidate-tests.log

```text
........................................................................ [ 31%]
........................................................................ [ 63%]
........................................................................ [ 95%]
...........                                                              [100%]
227 passed, 31 deselected in 20.94s
```

### verification.json

```json
{
  "status": "passed",
  "protected": 2856,
  "worker_evidence": 1720,
  "unchanged_dependencies": 52,
  "unchanged_definitions": [
    "_qpy_standard_gate_classes",
    "_resolved_qpy_circuit",
    "_qpy_semantic_signature",
    "_stage_timings",
    "_network_statistics",
    "_workspace_provenance",
    "ExcludedCase",
    "_integers",
    "_validate_restoring_problem",
    "_problem_without_precolors",
    "ColoringStudyCase",
    "_restoring_mcx_block",
    "_apply_restoring_mcx",
    "assemble_case"
  ],
  "candidate_hashes": {
    "src/logique/benchmarks/coloring_study.py": "ea57eeea1541720f552ebbb3fd2d64b108e85e803923cad6a63fbbeb2336df32",
    "tests/test_coloring_study.py": "4ff6060d07b67bd76efbb3f240f8138c10360d2749fc2287ba4522ff00ab5346"
  },
  "checkpoint_sha256": "7048823c4717fa967501edefd413ab3505ab28415cf3db301e0936f8cc4a965d",
  "queue_jobs": 54,
  "state_records": 50,
  "queue_sha256": "d0e7af5d7660f56d4e7f2a82a33eb3adbead390165fc8519fc7c452fa9bd6b49",
  "numerical_seconds": 34.91012233309448,
  "max_child_rss_bytes": 226623488,
  "state_jobs_unchanged": true,
  "root_git_status": " M README.md\n"
}
```
