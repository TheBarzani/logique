# Independent component-width acceptance review

**Bounded review COMPLETE. ADMITTED for the exact candidate source/test bytes
below, only as a post-assembly allocated-component acceptance bound.** No
remaining blocker was found for that narrow contract. This is not a memory or
timeout guarantee, new decomposition policy, protocol freeze, performance result,
FT/RUS extension, or paper approval. The full paper remains unfinished.

## Identity, intake and ownership

Assigned task: `component-width-review-1026071418`. Branch:
`codex/coloring-component-width-review-1026071418`. Reviewer base:
`7e8615ce72e2318337884db87c3e89222d646bf2`. Only this file is a tracked deliverable.
Reviewer worktree:
`/Users/mar/codex-work/logique/dump/1026071418-restoring-mcx-coordinator-triage/worktrees/component-width-review`.
Evidence RUN is `dump/1026171306-component-width-review/` inside that worktree.

Read-only candidate is sibling `component-width`, branch
`codex/coloring-component-width-1026071418`, HEAD
`414fd4694db7841a29f14c5fd28451e032b20496`. Correctness commit:
`ef0c372b7971adb1d1d8c333b2135cc2efcb9aa5`, containing only source/tests.
The later documentation commits record its handoff and correct the historical
dispatcher-state inventory count; they do not change the candidate implementation.
The actual checkpoint and evidence were inspected, not inferred from job status.

| Candidate file | SHA-256, unchanged before/after review |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `1b09d99a5591fe25cecb854930d489f0e0d8c914875c18bd1e504aea42d0559f` |
| `tests/test_coloring_study.py` | `b9f1d07b760fd375a1ebefcec5612209883fb93d2b7b0024a91856886383c200` |
| `WIDTH_CONTROL_CHECKPOINT.md` | `95651443b9a729ed9fbc657fd07b0106815e66fa3c6af41763963ff892bc2870` |
| Unchanged `src/logique/benchmarks/costs.py` | `42c524609e77e0e0db1b3fd4dcd98d91c0bf6e5ecfbd74dafeabd8b9b92eb2e8` |

Git and dispatcher state were inspected first, and again after interruption.
There was no completed own handoff: clean assigned base, no review file or
review commit. The first attempt performed read-only intake; it was interrupted
before edits or numerical commands. Durable state records included-quota
exhaustion. On resumption the full queue still had 48 unique jobs, 41 recorded
state entries: 38 complete, two unrelated native jobs blocked, this reviewer
alone running, and seven pending jobs. Width implementation is complete;
`coordinate-component-width-1026071418` exists exactly once with finished
predecessor triage. Completed stage-controls, QPY and restoring-MCX coordinators
were not redispatched. Historical manifest status/usage snapshots do not override
dispatcher state. No OS-wide process-visibility claim is made.

Read AGENTS.md, CLAUDE.md, all 646 lines of the revision plan, implementation
audit including current root additions, architecture, rotation-admission batch,
current QPY/restoring batches, root QPY and restoring admission/review/representation
records, and the rotation numerical contract. The full server manifest was
parsed and its 2,031 scalar leaves / 15 historical integration batches inventoried
in RUN. Both candidate checkpoint and changed source/tests, actual saved evidence,
and the surrounding runner/assembly path were inspected. Old setup/launch guidance
does not authorize sync, builds or dispatch in this slice.

## Bounded contract and independent reasoning

`max_component_qubits` is optional. An explicit value must be a positive builtin
`int`; bool, null, floats, strings, containers, nonpositive integers, numpy integer
scalars and int subclasses reject. Configuration validation runs before DIMACS
reading, run creation or assembly. Omission inserts neither a config default nor
a per-case width field. No direct `assemble_case` width keyword is introduced.

Immediately after successful assembly, the gate reads the actual `num_qubits`
of raw, preparation, oracle, diffusion and search. `ColoringStudyCase.circuits`
always returns those five components. It gathers every width before deciding,
including components not executed by j=0, all idle wires, and every reserved
raw/A/S0 pool. It does not use stale role metadata or a live-workspace estimate.
A component is over budget exactly when its width is **greater than** the cap;
equality passes. Python integer comparison introduces no floating boundary.

For configured assembled cases the persisted record contains the cap, all five
widths, every offending name, accepted/excluded status and explicit scope.
On excess, `ExcludedCase` is raised before initializing the artifact dictionary
or entering artifact-stage resolution, common-basis lowering, metrics or QPY
writing. The handler records the cap/name/width reason and excluded status in
both case JSON and run.json, then the enclosing loops proceed to later cases.
`case_rows` is local and appended to global rows only after full case success.
Consequently a width exclusion produces **zero cost rows and zero QPY artifacts**.
Diagnostic config/provenance/case/manifest JSON is intentionally retained.

Scope qualification: assembly has already happened, including any native work,
source validation and restoring definition resolution/lowering inside assembly.
The control cannot prevent those allocations or Qiskit's definition generation.
An accepted case can still fail later. Existing later export failures may retain
partial diagnostic QPY artifacts, with zero failed-case rows, as required by the
prior QPY/restoring contracts. This review does **not** claim that all possible
failures leave zero files, nor authorize deleting retained failure evidence.
Independent pre-artifact failure/exclusion fixtures below do leave zero QPY.

Acceptance performs integer reads/comparisons and metadata insertion; it does
not alter any quantum component. The source diff changes only CONFIG_FIELDS,
config validation, the runner docstring and this pre-artifact gate. All 14 other
function/class source segments are byte-identical to the admitted baseline,
including `assemble_case`, `_apply_restoring_mcx`, `_restoring_mcx_block`,
`_resolved_qpy_circuit`, `_qpy_semantic_signature`, workspace and timing helpers.
All other candidate library Python files match reviewer dependencies byte-for-byte.
Omission bypasses both new branches and retains the exact old artifact pipeline.

Thus the existing clean-tree theorem remains unchanged: on fresh zero scratch,
the monomial RCCX conjunction prefix computes controls with phases; the exact
final CCX changes only the external target; the actual prefix inverse restores
scratch and cancels phases. Column equality extends to superposition/reference
inputs by linearity, not to dirty scratch. Actual emitted A inverse, signed
reflection, ordered data embeddings and disjoint raw/A/S0 pools are untouched.
QPY admission still concerns bound quantum-only emitted definitions, scalar
phase and ordered wires. No general wide-transpiler equivalence, arbitrary
opaque/dynamic/adversarial-standard support or archived-pilot repair is inferred.

## Independent checks and actual evidence

Candidate regressions: **185 passed, 31 deliberately deselected, zero skips**.
The retained exclusions are 27 `matching_preparation_diffusion_and_search`, one
`r3_keeps_asymmetric_k5_preparation`, and three
`native_asymmetric_constant_r3_and_complete_search` wider dense tests. This review
does not replace their excluded coverage. Runtime guards reject circuit Operator
construction above four wires and Statevector.from_instruction above five;
the retained direct vector/evolve fixtures remain at most five wires.

The separate independent harness imports no candidate test/reference helpers:

- Seventeen invalid values reject before patched input reading, run creation
  and assembly; no output directory appears. Positive 1, 5 and a 101-digit int
  pass config validation without allocating a circuit.
- Six width-only injected assemblies independently isolate raw/A/oracle/diffusion/
  search excess and simultaneous excess. All five properties are read exactly
  once. Patched resolver, lowering, metrics and QPY writer are forbidden. All
  cases retain exact widths/reasons, zero rows and zero QPY, without constructing
  oversized quantum objects.
- Sixteen genuine tiny assemblies: isolated k3, sb_balanced/xag_bennett,
  R2/R3, j0/1, default/restoring. The exact same assembled objects are copied into
  admitted-baseline, candidate-omitted and candidate-equality runs to isolate the
  runner and avoid incidental autogenerated circuit-name differences. All **160
  artifact triples are byte-identical**; all 160 metric rows match after removing
  only measured lowering duration. Width, counts, full gate maps and dependency
  depth are independently recounted, and actual artifact hashes match manifests.
- **352 bounded operator calls**, **16 complete-register statevectors** and
  **102 ordered composition comparisons** check original/saved components,
  signed matching diffusion, j0/j1 search and scalar phases without alignment.
  Maximum entrywise error: **5.65233285126159e-15**, tolerance 3e-11. Operator
  calls include repeated/local references, not 352 independent graph theorems.
- The real noncontiguous-label edge-k3 restoring j0 fixture has allocated widths
  raw=9, A=4, oracle=9, diffusion=5, search=10. Raw scratch is wire 8 and unused
  S0 scratch wire 9; MCX live-capacity field is zero. Cap 9 excludes; cap 10
  completes. Wider search equals A embedded once on the same ordered wires,
  including idle pools, and every saved primary component matches its ordered
  definitions/scalar phase. No 10-wire operator or statevector is allocated.
  This injected-runner fixture tests acceptance of a real assembled object;
  its retained isolated-input config is not a graph benchmark provenance claim.
- A sequential mixed-outcome run yields `failed`, `excluded`, `complete` for
  seeds 1,2,3. The deliberate assembly failure and width exclusion have zero QPY
  and rows; only the later success contributes ten logical/common-basis rows.
  Explicit reasons survive; the manifest remains complete_with_failures.

Actual worker evidence was separately read and hash-verified, including its
retained initial failures. The final width ledger's **18 records across 15
manifests** agree with actual case bytes: 12 excluded, six complete, three of
the complete records omit the control. Every width-excluded case has zero QPY
and zero summary rows. **80 actual worker compatibility rows** (40 reference,
40 candidate) were independently recounted from saved circuits. Worker fresh-run
comparison reports 12 byte-identical artifacts and 28 differences only in
automatically generated circuit names, with semantic/normalized-byte equality;
its saved baseline source matches admitted hash
`a811e028b82b4ac1ddf01fa57e6449f5065a797302d1f676e1b4e67bd34511e5`.
Our fixed-assembly triple comparison is the separate independent exact-byte
evidence; no unconditional byte-identical fresh-run claim is made.

Unknown backend workspace, peak process memory and general live peaks remain
null/unavailable. Native combined time remains included in synthesis; mapping/
optimization splits are not fabricated. No circuit representation, historical
research table or numerical performance claim changes here. Worker Black/Ruff
checks passed on these exact source/test hashes; this reviewer did not repeat
them. Owned review whitespace and explicit staged-file scope are checked before
commit. No full suite, mypy, build, notebook, replay, routing or FT run is claimed.

## Execution resources, failures and preservation

Existing interpreter only: `/Users/mar/codex-work/logique/.venv/bin/python`.
PYTHONPATH is explicitly this review worktree's `src`. `bootstrap.py` asserts
that path, retains its admitted baseline module, then loads the exact sibling
candidate file explicitly into the canonical module slot. Candidate imports are
asserted and its hash checked; unchanged dependencies resolve to reviewer src.
This reviews candidate bytes without copying or editing candidate/root source.

`LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl`.
Explicit manifest-admitted native executable:
`/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`,
SHA-256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Root old binary remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.

Commands were sequential with synchronous native calls, all thread limits set
to one, timeout <=120s each, cumulative numerical allowance <=300s. Actual
regressions: **17.836162s**, child RSS **223887360 bytes**. Independent harness:
**10.881210s**, child RSS **180944896 bytes**. Total numerical wall time:
**28.717372s**. The maximum is below 8 GiB for these fixed fixtures; this is
measured child RSS, not an OS aggregate cap or global process-visibility proof.
Wider checks use integer widths/ordered compositional equality only. No compiler.

Exact numerical argv, cwd, environment, exit codes, wall times and RSS are in
RUN/commands.jsonl; both commands exit zero. From this worktree:

```sh
/Users/mar/codex-work/logique/.venv/bin/python dump/1026171306-component-width-review/supervisor.py candidate-tests /Users/mar/codex-work/logique/.venv/bin/python dump/1026171306-component-width-review/run_tests.py ../component-width/tests/test_coloring_study.py -k 'not matching_preparation_diffusion_and_search and not r3_keeps_asymmetric_k5_preparation and not native_asymmetric_constant_r3_and_complete_search' --basetemp=dump/1026171306-component-width-review/test-artifacts -p no:cacheprovider -q
/Users/mar/codex-work/logique/.venv/bin/python dump/1026171306-component-width-review/supervisor.py independent /Users/mar/codex-work/logique/.venv/bin/python dump/1026171306-component-width-review/independent.py
```

Retained failures/qualifications:

- First dispatcher attempt stopped during read-only intake; no numerical work
  or edits needed replay. Some oversized discovery/combined reads were truncated;
  required plan/reviews were subsequently read in bounded sections and JSON
  records parsed/inventoried. Queue and state were never written.
- Post-test read-only evidence audit initially indexed component_width_check
  unconditionally and raised KeyError on an omitted-control worker record after
  preservation checks passed. The corrected reader requires absence only for
  omission and passes all 18 records; failure is retained in
  RUN/audit-initial-failure.txt. No numerical test was repeated for this reader fix.
- Worker preliminary flat-only StatePreparation signature assertion and fresh
  QPY autogenerated-name assertion failures remain preserved. Their failed
  runs are not admitted evidence. The worker's preliminary reference provenance
  shim is not proof of baseline bytes; its corrected saved baseline is used.
- Expected invalid configuration, deliberate pre-artifact assembly failure and
  width exclusions remain explicit. There was no candidate numerical failure,
  timeout or OOM in the independent run. Existing historical QPY failures and
  dirty-scratch exclusions remain unmodified and unadmitted.

Initial explicit `git add -- WIDTH_CONTROL_REVIEW.md` was sandbox-denied at the
shared worktree `index.lock`. Narrow automatic escalation successfully staged
only the already-authorized review file; staged whitespace/scope checks pass.
A subsequent documentation patch
used a nonexistent context line and failed without mutation; its corrected
patch records this tooling failure. No automatic approval rejection occurred.

Before/after checks verify **8,192 protected identities**, including all 768
worker evidence hashes, its checkpoint/source/tests, both README copies, root
README edits, prototype backups, archived outputs, nested histories, admitted
reviews, lockfiles and both binaries. Root/reviewer/candidate external index
entries are unchanged. Queue SHA-256 remains
`cc5a2f6592a5b920302e50f04946e240e5f368f66f1a22052e852c360ef9bd9e`.
No agents/model/Codex/API/paid fallback/hardware/push/publishing, sync/install,
dependency changes, queue append or integration occurred.

## Admission limits and next action

This decision admits only the identified additive width gate on the existing
admitted assembly/serialization contract. Clean_tree/fresh_zero still requires
fresh clean scratch and the prior bounds (k<=8, data<=21, j0..2, MCX3..20,
operation width<=21, definition depth<=32, visits<=100000 per resolver).
Backend predicate validation remains its own obligation; sampled coverage is
sampled. Other policies, borrowing, optimized live peaks, memory/timeout
enforcement, general wide transpiler equivalence and archived-pilot repair are
outside this decision.

Unchanged rotation source/test hashes remain
`5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595` /
`88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77`.
Its numerical/caller contract is not extended: no interval certificate,
ideal-amplitude guarantee, dynamic RUS admission or blanket paper approval.
Root QPY/restoring reviews and representation ledgers are hash-verified in
RUN/verification.json; passing tests alone did not grant this admission.

**Next action:** dispatcher releases the already queued
`coordinate-component-width-1026071418` to verify these exact candidate/review
identities and integrate only the owned correctness commit, preserving this
independent decision separately from any future metrics/build changes. Reviewer
does not integrate, append jobs or push. Dispatcher alone launches/pushes
integration HEAD. Changed source bytes or a broader contract require fresh review.
On completed-own-handoff repeat, verify commit, candidate/evidence/protected
hashes and unique handoff, then release COMPLETE without tests or jobs.
Further controls, full studies, protocol freeze and the full paper remain open.

## Preserved executable evidence

The following scripts are the actual executed evidence, retained inline because
this review is the sole tracked deliverable. Replay requires a separately
authorized fresh timestamped run; do not overwrite RUN or repeat completed work.

| Evidence file | SHA-256 |
| --- | --- |
| `bootstrap.py` | `c5bd0730a2b3f3e132a7c37e1402598a2f362da3cf62e3a3dd39d8def9a54d78` |
| `supervisor.py` | `72cb0947456ddf77974edb82311d7401e0924450de7e59b854777997cd79ba18` |
| `run_tests.py` | `18883c807160eab8ed5249629369e4953d71cc0428b659daa09a1f16b233b670` |
| `independent.py` | `d24238a03674fc752428a4fbb4e5846d14aa10c8a3fae39e60fd2487dd25e2b2` |
| `independent-results.json` | `f86c24f1629645553496dafc335755b6ab65388a0a0e8c8f05a120dbf70f82d6` |
| `commands.jsonl` | `ed77d5bcfb3640fad42d26d4cac0bc34a7ed563cefb20d8c37760096ab436e82` |
| `candidate-tests.log` | `36fac12b05bf3cabc9b940f97b67a678d176095f12f6beb515c4059792343112` |
| `independent.log` | `f86c24f1629645553496dafc335755b6ab65388a0a0e8c8f05a120dbf70f82d6` |
| `protected.json` | `726522a6095509dc8458120adbacfbc47143550ec23e4207a91b46434c7d5b82` |
| `intake.json` | `1b8d1ce8ccbbebcb41f5f2497b022e5bf6ee4c8b32604516b0d1db639c3f0176` |
| `verification.json` | `e6a27cd8b7bdda99f14b20e21dcf72a140ad4c8b303a483f0f727e423406e4ee` |
| `audit-initial-failure.txt` | `d9dca7294ac2de5a31069f9c370b674b3e0bb43942dedd791adf66022864ee5f` |

### bootstrap.py

```python
"""Load read-only candidate bytes over hash-identical reviewer dependencies."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys

W = Path.cwd()
C = W.parent / "component-width"
R = Path(__file__).resolve().parent
assert Path(os.environ["PYTHONPATH"]).resolve() == W / "src"
from logique.benchmarks import coloring_study as baseline

assert Path(baseline.__file__).resolve() == W / "src/logique/benchmarks/coloring_study.py"
path = C / "src/logique/benchmarks/coloring_study.py"
assert hashlib.sha256(path.read_bytes()).hexdigest() == "1b09d99a5591fe25cecb854930d489f0e0d8c914875c18bd1e504aea42d0559f"
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
"""Independent acceptance-bound checks; no candidate test/reference helpers."""
from bootstrap import baseline as b, candidate as s, C, R, W
import ast
from collections import Counter
import copy
import csv
from datetime import datetime
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
from unittest.mock import patch
import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.quantum_info import Operator, Statevector
from logique.coloring import ColoringProblem
from logique.benchmarks import metrics, runner

report = dict(rejections=[], gates=[], compatibility_cases=0, rows=0,
              equal_artifacts=0, operators=0, statevectors=0, compositions=0,
              max_error=0.0)
names = ('raw', 'preparation', 'oracle', 'diffusion', 'search')
source = R / 'isolated.col'
source.write_text('p edge 1 0\nx colors 3\n')
counter = 0
def config(label, **kw):
    global counter
    counter += 1
    return dict(inputs=[str(source)], methods=['sb_balanced'], regimes=['R2'],
                iterations=[0], seeds=[7],
                output=str(R / f'{datetime.now():%m%d%H%M%S}-{label}-{counter}'), **kw)

def forbidden(*a, **kw):
    raise AssertionError('forbidden downstream work')

class IntSubclass(int):
    pass

invalid = [None, False, True, 0, -1, -10**100, 1.0, float('nan'), float('inf'),
           '5', '', [], {}, (), complex(1), np.int64(5), IntSubclass(5)]
for cap in invalid:
    cfg = config('invalid', max_component_qubits=cap)
    with patch.object(s, 'read_dimacs', forbidden), patch.object(s, 'assemble_case', forbidden), patch.object(runner, 'new_run_directory', forbidden):
        try:
            s.run_coloring_study(cfg)
        except ValueError as e:
            assert str(e) == 'max_component_qubits must be a positive integer'
            report['rejections'].append(repr(cap))
        else:
            raise AssertionError(('invalid accepted', cap))
    assert not Path(cfg['output']).exists()
for cap in (1, 5, 10**100):
    assert s.validate_study_config(dict(inputs=['missing.col'], max_component_qubits=cap))['max_component_qubits'] == cap

class Width:
    def __init__(self, name, width, reads):
        self.name, self.width, self.reads = name, width, reads
    @property
    def num_qubits(self):
        self.reads.append(self.name)
        return self.width

for bad in [*names, 'all']:
    reads = []
    widths = {n: 6 if bad in (n, 'all') else 5 for n in names}
    case = s.ColoringStudyCase(*(Width(n, widths[n], reads) for n in names), metadata={})
    with patch.object(s, 'assemble_case', return_value=case), patch.object(s, '_resolved_qpy_circuit', forbidden), patch.object(metrics, 'circuit_metrics', forbidden), patch.object(metrics, 'lower_circuit', forbidden), patch.object(qpy, 'dump', forbidden):
        out = s.run_coloring_study(config('width-'+bad, max_component_qubits=5, common_basis=True))
    assert reads == list(names), reads
    manifest = json.loads((out/'run.json').read_text()); rec = manifest['cases'][0]
    check = rec['component_width_check']; assert check['allocated_qubits'] == widths
    assert check['over_budget_components'] == [n for n in names if widths[n] > 5]
    assert rec['status'] == 'excluded' and check['status'] == 'excluded'
    assert json.loads((out/(rec['name']+'.json')).read_text()) == rec
    assert not rec.get('artifacts') and not list(out.glob('*.qpy')) and not (out/'summary.csv').exists()
    report['gates'].append(dict(component=bad, widths=widths, reason=rec['reason']))

def flat(q):
    seq=[]; phase=0.0
    def visit(c, wires, depth=0):
        nonlocal phase
        assert depth <= 32
        phase += float(c.global_phase)
        for it in c.data:
            op=it.operation; loc=tuple(wires[c.find_bit(x).index] for x in it.qubits)
            closed=getattr(op,'ctrl_state',None) in (None,(1<<getattr(op,'num_ctrl_qubits',0))-1)
            if op.base_class.__module__.startswith('qiskit.circuit.library.standard_gates.') and closed:
                seq.append((op.base_class.__module__,op.base_class.__name__,tuple(complex(x) for x in op.params),getattr(op,'ctrl_state',None),loc))
            else:
                assert op.definition is not None
                visit(op.definition,loc,depth+1)
    visit(q,tuple(range(q.num_qubits)))
    return seq,np.exp(1j*phase)

def close(a, z):
    e=float(np.max(abs(np.asarray(a)-np.asarray(z)))); report['max_error']=max(e,report['max_error']); assert e<3e-11,e

def composition(a,z):
    aa,pa=flat(a);zz,pz=flat(z)
    assert a.num_qubits==z.num_qubits and aa==zz
    close(pa,pz); report['compositions']+=1

def matrix(q):
    assert q.num_qubits<=4
    report['operators']+=1
    return Operator(q).data

def load(path):
    with path.open('rb') as f:return qpy.load(f)[0]

def recount(q):
    counts=Counter(); clocks=[0]*q.num_qubits
    for it in q.data:
        assert it.operation.name not in ('measure','barrier')
        counts[it.operation.name]+=1
        wires=[q.find_bit(x).index for x in it.qubits]
        t=1+max((clocks[x] for x in wires),default=0)
        for x in wires:clocks[x]=t
    return q.num_qubits,sum(counts.values()),max(clocks,default=0),dict(counts)

# Existing valid assembly is shared identically among runs, so the comparison
# isolates the runner and prevents incidental autogenerated circuit-name noise.
for method,regime,j,restoring in itertools.product(('sb_balanced','xag_bennett'),('R2','R3'),(0,1),(False,True)):
    controls=dict(mcx_decomposition='clean_tree',mcx_workspace='fresh_zero') if restoring else {}
    assembled=s.assemble_case(ColoringProblem((1,),(),3),method,regime,iterations=j,**controls)
    widths={n:q.num_qubits for n,q in assembled.circuits.items()}; cap=max(widths.values())
    assert cap<=5, widths
    outputs=[]
    for module,label,extra in [(b,'baseline',{}),(s,'omitted',{}),(s,'equal',{'max_component_qubits':cap})]:
        cfg=config(label,common_basis=True,optimization_level=0,**controls,**extra)
        cfg.update(methods=[method],regimes=[regime],iterations=[j])
        with patch.object(module,'assemble_case',side_effect=lambda *a,**kw:copy.deepcopy(assembled)):
            outputs.append(module.run_coloring_study(cfg))
    old,omitted,capped=outputs
    manifests=[json.loads((x/'run.json').read_text()) for x in outputs]
    for idx,m in enumerate(manifests):
        assert m['cases'][0]['status']=='complete'
        if idx<2:
            assert 'max_component_qubits' not in m['config'] and 'component_width_check' not in m['cases'][0]
        else:
            ck=m['cases'][0]['component_width_check']; assert ck['allocated_qubits']==widths and ck['status']=='accepted' and not ck['over_budget_components']
        assert m['cases'][0]['peak_memory']=={'status':'unavailable','bytes':None}
        assert m['cases'][0]['stage_timings']['native_combined']['included_in']=='synthesis'
    tables=[list(csv.DictReader((x/'summary.csv').open())) for x in outputs]
    normalize=lambda rows:[{k:v for k,v in row.items() if k!='lowering_seconds'} for row in rows]
    assert normalize(tables[0])==normalize(tables[1])==normalize(tables[2])
    assert len(tables[0])==10
    for row in tables[2]:
        fn=row['artifact']; assert (old/fn).read_bytes()==(omitted/fn).read_bytes()==(capped/fn).read_bytes()
        saved=load(capped/fn); width,gates,depth,counts=recount(saved)
        assert (int(row['qubits']),int(row['gates']),int(row['depth']),ast.literal_eval(row['gate_types']))==(width,gates,depth,counts)
        stat=manifests[2]['cases'][0]['artifact_statistics'][fn]
        assert hashlib.sha256((capped/fn).read_bytes()).hexdigest()==stat['sha256']
        component=row['component']; original=assembled.circuits[component]
        if row['metric_level']!='common_basis':composition(original,saved)
        if width<=4:close(matrix(original),matrix(saved))
        report['rows']+=1;report['equal_artifacts']+=1
    a=matrix(assembled.preparation);sign=-np.eye(len(a));sign[0,0]=1
    close(matrix(assembled.diffusion),a@sign@a.conj().T)
    expected=QuantumCircuit(assembled.search.num_qubits)
    if restoring:
        em=assembled.metadata['mcx_lowering']['search_embeddings']
        expected.compose(assembled.preparation,em['preparation'],inplace=True)
        for _ in range(j):expected.compose(assembled.oracle,em['oracle'],inplace=True);expected.compose(assembled.diffusion,em['diffusion'],inplace=True)
    else:
        expected.compose(assembled.preparation,assembled.metadata['data_qubits'],inplace=True)
        for _ in range(j):expected.compose(assembled.oracle,inplace=True);expected.compose(assembled.diffusion,assembled.metadata['data_qubits'],inplace=True)
    composition(expected,assembled.search)
    initial=a[:,0];amp=initial.copy();marked=np.array([x<3 or regime=='R3' for x in range(4)])
    for _ in range(j):amp[marked]*=-1;amp=2*initial*np.vdot(initial,amp)-amp
    physical=np.zeros(1<<cap,dtype=complex)
    for x,v in enumerate(amp):physical[sum(((x>>i)&1)<<w for i,w in enumerate(assembled.metadata['data_qubits']))]=v
    close(Statevector.from_instruction(assembled.search).data,physical);report['statevectors']+=1
    report['compatibility_cases']+=1

# Real j0 reserved scratch and equality on a wider register: no dense arrays.
edge=s.assemble_case(ColoringProblem((-7,20),((-7,20),),3),'sb_balanced','R2',iterations=0,mcx_decomposition='clean_tree',mcx_workspace='fresh_zero')
owners=edge.metadata['mcx_lowering']['search_scratch_ownership']
assert owners['zero_reflection']
assert edge.metadata['component_workspace']['search']['mcx_live_peak_upper_bound']==0
expected=QuantumCircuit(edge.search.num_qubits)
expected.compose(edge.preparation,edge.metadata['mcx_lowering']['search_embeddings']['preparation'],inplace=True)
composition(expected,edge.search)
widths={n:q.num_qubits for n,q in edge.circuits.items()};cap=max(widths.values())
outcomes=[]
for bound in (cap-1,cap):
    with patch.object(s,'assemble_case',side_effect=lambda *a,**kw:copy.deepcopy(edge)):
        out=s.run_coloring_study(config('reserved',max_component_qubits=bound,mcx_decomposition='clean_tree',mcx_workspace='fresh_zero'))
    rec=json.loads((out/'run.json').read_text())['cases'][0];outcomes.append(rec['status'])
    assert rec['component_width_check']['allocated_qubits']==widths
    if bound<cap:
        assert not list(out.glob('*.qpy')) and not (out/'summary.csv').exists()
    else:
        for n,q in edge.circuits.items():composition(q,load(out/rec['artifacts'][n+'_restoring_mcx']))
assert outcomes==['excluded','complete']
report['reserved_j0']=dict(widths=widths,owners=owners,outcomes=outcomes,cap=cap)

# Three sequential outcomes distinguish a pre-artifact assembly failure, width
# exclusion and later success. No failed/excluded rows or QPY can be emitted.
tiny=s.assemble_case(ColoringProblem((1,),(),3),'sb_balanced','R2',iterations=0)
cap=max(q.num_qubits for q in tiny.circuits.values())
def outcomes(*a,seed,**kw):
    if seed==1:raise RuntimeError('independent pre-artifact failure')
    result=copy.deepcopy(tiny)
    if seed==2:result.preparation=Width('preparation',cap+1,[])
    return result
cfg=config('continued',max_component_qubits=cap,common_basis=True);cfg['seeds']=[1,2,3]
with patch.object(s,'assemble_case',side_effect=outcomes):out=s.run_coloring_study(cfg)
m=json.loads((out/'run.json').read_text());rows=list(csv.DictReader((out/'summary.csv').open()))
assert [c['status'] for c in m['cases']]==['failed','excluded','complete']
assert len(rows)==10 and {r['seed'] for r in rows}=={'3'}
for c in m['cases'][:2]:
    assert not c.get('artifacts') and not list(out.glob(c['name']+'*.qpy'))
report['continuation']=dict(statuses=[c['status'] for c in m['cases']],rows=len(rows),reasons=[c.get('reason') for c in m['cases']])

# Recount actual worker compatibility evidence; retain failed preliminary runs.
E=C/'dump/1026124756-component-width'
worker_rows=0
for folder in ('1026125123-reference-False','1026125123-current-False','1026125123-reference-True','1026125124-current-True'):
    d=E/folder
    for row in csv.DictReader((d/'summary.csv').open()):
        q=load(d/row['artifact']);v=recount(q)
        assert (int(row['qubits']),int(row['gates']),int(row['depth']),ast.literal_eval(row['gate_types']))==v
        worker_rows+=1
report['worker_rows_recounted']=worker_rows
assert worker_rows==80
report['status']='passed'
(R/'independent-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
```
