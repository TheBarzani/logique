# Boolean synthesis bridge

This C++17 executable imports combinational AIGER or structural Verilog with
Lorina/mockturtle and invokes Caterpillar's Bennett or best-fit mapping. It is
isolated from the installed tweedledum Python extension because their APIs differ.

```bash
cmake -S external/native/boolean_synthesis -B external/native/boolean_synthesis/build -DCMAKE_BUILD_TYPE=Release
cmake --build external/native/boolean_synthesis/build -j 2
```

The configuration uses `external/caterpillar/` by default, pinned by the Git
submodule to revision `4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`, including its
vendored headers and MIT license. Standalone builds without that checkout download
the same revision. `-DFETCHCONTENT_SOURCE_DIR_CATERPILLAR=/path/to/source` remains
an explicit override. No dependency submodules are changed.
`Network<Base>` supplies the optional predicates that the reference LHRS visitor
instantiates even for strategies that never use level actions. CMake also makes
a local header overlay with two correctness fixes: pop the node's qubit mapping
after uncomputation. Without that pop, nested best-fit recomputation can read a
freed wire instead of the previous live copy. Also expose the mapped cell's
fanout counts to eager cleanup, instead of inheriting the original gate fanout
counts. Otherwise a cell may be erased while later cells still need it.
The optional `router` regression exercises both problems. The
downloaded reference and repository submodules remain unchanged. This fix is
recorded as `lhrs_uncompute_stack_pop` and `best_fit_cell_fanout` in result
metadata. The reference strategies run with these corrections.
Each fresh build writes `build_provenance.json` beside the executable, identifying
the effective Caterpillar, bundled Mockturtle and Kitty source paths, representative
header hashes, compiler, and applied fixes. Phase benchmark manifests retain this
record together with the executable SHA-256. The declared reference revision is
not a claim that an arbitrary FetchContent source override matches that revision.
`RecordingCircuit` and `RecordLut`
export gate semantics instead of linking the older quantum IR into Python.

The executable reads one JSON request from stdin and writes one JSON result to
stdout. Diagnostics go to stderr; nonzero exit codes indicate failure.

```json
{"path":"/absolute/path/ctrl.aig","method":"klut_bennett","k":4,"outputs":[0]}
```

Methods: `xag`, `aig_bennett`, `xag_bennett`, `klut_bennett`, `best_fit`.
`xag` exports a refactored XAG for Python's specialized `xag_synth`. LUT sizes
range from 2 through 6. Best-fit defaults to `outer_cut=16`, `inner_cut=4`.
Omitting `outputs` selects all outputs. Input order is preserved when projecting
outputs. Sequential AIGER is rejected.

AIG/XAG Bennett accept an independent opt-in `"strategy":"bennett"`,
`"bennett_inplace"` or `"eager"` control (Python: `synthesize(...,
strategy="eager")`). These instantiate the pinned Caterpillar
`bennett_mapping_strategy`, `bennett_inplace_mapping_strategy` and
`eager_mapping_strategy` classes, respectively, after the selected preprocessing
and representation conversion. Omission still uses Bennett. The other three
methods reject every explicit strategy control, including `bennett`. Unknown
values and strategy-specific tuning reject. The bounded sequential XAG and SAT
opt-ins are specified below.
`mapping_strategy` records `name`, `explicit`, and the qualified `implementation`;
Python requires this confirmation and a step array for every explicit request,
so the control cannot silently disappear at an older bridge. `steps` contains
the actual strategy's full action payloads, as consumed by LHRS.

In-place Bennett overwrites only last-use XOR fanins of non-output nodes and
restores them in reverse order. The pinned AIG representation has no XOR gates,
so this selection is supported but emits ordinary Bennett steps there. XAG may
also emit no in-place steps if its graph offers no eligible XOR. `target_index`
is a mapped **node** index, resolved through that node's live qubit stack, not a
physical wire index. The pinned in-place uncompute handler leaves a stale node
stack entry; these Bennett schedules compute each node once and restore every
overwrite before earlier ancestors are uncomputed, so they never reuse that
entry. This does not certify arbitrary recomputation or mixed in-place schedules.
Eager computes nodes topologically and recursively cleans fanins when their last
reference is released at an output. Output references keep output drivers live;
fanout counts include repeated and complemented output aliases. The existing
out-of-place uncompute stack-pop overlay remains necessary and unchanged.

LHRS output preparation may complement a primary-input wire in the raw circuit
when that input drives a complemented output; raw input restoration is therefore
not guaranteed for aliases. The compute/copy/uncompute XOR and phase wrappers
restore it. Unused primary inputs remain declared. Focused tests in
`tests/test_native_mapping_strategies.py` check actual emitted gates against
independent functions and coloring predicates, all joint XOR-target patterns,
phase/workspace restoration, nested in-place targets, shared fanout, early eager
cleanup and bounded superpositions. This is no admission of low-T/low-depth,
level-based, LUT in-place or best-fit strategy overrides; the separate bounded
SAT opt-in is described below. No performance claim follows.

Common preprocessing is **opt-in**. Add `"preprocessing":"none"` or
`"preprocessing":"refactoring"` to the native request, or pass
`preprocessing="none"` / `"refactoring"` to Python's `synthesize`. The bridge
cleans the selected XAG, applies the selected pass once, then converts that same
XAG to the requested representation. Refactoring uses the pinned bundled
Mockturtle bidecomposition resynthesis and default refactoring parameters,
followed by dangling cleanup. `none` performs only dangling cleanup.
Omission retains legacy defaults: `aig_bennett` converts the unrefactored XAG;
the other four methods use the refactored XAG. Historical expression synthesis
continues to synthesize its original tweedledum network directly.
Unsupported preprocessing values, unknown request controls, and method-specific
controls on other methods are rejected. The Python process boundary requires
confirmation of an explicit policy so older bridges cannot silently ignore it.

`source_network` remains the selected input graph **before** preprocessing;
`network` remains the graph actually supplied to mapping (the underlying XAG
for best-fit, rather than its cell covering). Verification uses the former;
structural summaries and drawings use the latter. The additive `preprocessing`
record has `policy`, `common` (whether explicitly requested), `before_network`
and `after_network`. These full ordered graphs record the common XAG evidence
before representation conversion. Node indices are local to each graph;
input/output position is the semantic interface. Explicit Python requests also
appear in `metadata["parameters"]`. Existing summary metrics are unchanged.

Results contain source and mapped graphs, gate records, explicit wire mappings,
and mapping steps. Truth-table strings use most-significant bit first; fanin 0
is the least-significant assignment bit. Control polarity `true` means control
on one. Python expands LUTs with the installed tweedledum PPRM implementation.

Step serialization uses an exhaustive visitor over the seven pinned Caterpillar
action types: `compute`, `uncompute`, `compute_inplace`, `uncompute_inplace`,
`buffer`, `compute_level`, and `uncompute_level`. `node` is the strategy's graph
node index. Compute actions retain `explicit_leaves` (null means unspecified;
an empty array means explicitly empty) and `cell_override` (null or an object
with MSB-first `truth` and ordered `leaves`). The legacy `lut_inputs` and `leaves`
columns remain for cell overrides; use `explicit_leaves` to distinguish the
action's own leaves when both exist. In-place actions also have `target_index`;
buffer actions have `target` and `leaf`. Level actions contain ordered `level`
entries with `node` and `cones`; every cone retains `root`, ordered `leaves`,
`complemented`, `target` and `copies`, including empty arrays. These payloads
retain the pinned strategy's indices; they do not imply physical qubit indices.
Adding a new upstream variant without a visitor overload fails compilation.

Configure with `-DLOGIQUE_BUILD_CONTRACT_PROBES=ON` and run
`ctest --test-dir YOUR_BUILD --output-on-failure` to check exact serialization of
every variant, including populated and empty payloads. These probes validate
serialization; they do not certify the gate-emission semantics of additional
strategies. Gate-emission acceptance is separate from these serializer probes;
The bounded SAT opt-in is described below.

The notebook compares these specific configurations, not published optimal
resource counts. It explicitly distinguishes raw clean-output computations from
the compute/copy/uncompute wrapper that accepts arbitrary XOR targets.

## Capped sequential XAG value certificate

The explicit `xag_bennett` / `strategy="xag_low_t"` path uses the pinned
non-template `caterpillar::xag_mapping_strategy`. It requires
`xag_value_validation.policy="canonical_sequential_two_cone_truth_tables_v1"`.
This is a sequential two-cone schedule with exact static X/CNOT/Toffoli gates;
the name makes no T-count or free inverse-AND claim. Fast/depth/level mappings
are separate and unsupported by this policy.

The supported domain is a cleaned combinational binary XAG in stored topological
order, with consecutive canonical PIs, distinct earlier nonconstant fanins and
uncomplemented XOR children. AND/output complements and unused PIs are retained.
Initial computation workspace must be clean. Release/NDEBUG supports empty
internal XOR frontiers; Debug explicitly rejects them. The native validator checks
caps before allocating its Boolean tables: **6 inputs, 256 stored nodes, 256
physical wires, 4096 mapping steps**, plus at most 256 outputs. Parsing and
preprocessing occur earlier; these are not general parser memory limits.
Above-cap requests reject as unsupported, without a silent fallback.

The certificate must declare exactly these four `caps` and integer
`inputs`, `nodes`, `width`, `steps`, `assignments`, `blocks`, `operand_reads`
and `zero_releases` counts. `assignments` equals $2^{\mathrm{inputs}}$; node and
wire truth tables contain at most 64 assignment bits. `node_values` is indexed by
stored node ID. `block_checks` records central node/undo identity, entry/exit
active boundary addresses, generations and values, and two cone frames containing
saved/prepared/restored values. Native validation checks actual operand values,
restoring frames, zero-before-release/reuse, and exact schedule/gate/I/O emission.
A stack generation or address alone never proves its Boolean value.

Python requires this certificate before `records_to_qiskit`. Missing, malformed,
unknown-policy, wrong-cap, inconsistent-count or invalid-address responses raise
`RuntimeError`. Boolean and floating-point substitutes for integer fields reject.
Python checks canonical network/table consistency, steps against audit actions,
block/read/release counts, trace addresses and restoration, gate wiring/polarity,
and scalar emitted output/input/workspace tables. It accepts the exact saved
valid response and rejects the saved historical seven-input response without a
certificate. This handshake is not an unrestricted proof for arbitrary schedules
or an authenticated assertion by an untrusted executable.

The redundant action `leaves` list is independently checked as a bounded list
of distinct integer node IDs before comparison with `explicit_leaves`. Its
length, order and values must match exactly. In particular, `true` and `1.0`
cannot stand in for node ID `1`, even if both the step and its audit action
contain the same malformed payload. Other node/wire indices in the mapped
network, action trace, frames, stacks, gates and normalization records also use
strict integer checks. Unread stale stack aliases remain valid addresses.

Internal XOR aliases can remain live but stale after a cone restores its anchor.
Their final stacks are checked as addresses, never admitted as persistent values;
only an actual prepared operand or active block boundary supplies a value.
Raw complemented PI outputs may change that PI. The actual emitted inverse in
the compute/copy/inverse and compute/Z/inverse wrappers restores computation
inputs/workspace on the clean-workspace subspace; dirty initial scratch is excluded.

The current bridge also retains the independently bounded `sat_pebbling` strategy
for AIG/XAG Bennett with all four explicit positive integer controls:
`qubit_budget<=64`, `sat_max_steps<=128`, `sat_conflict_limit<=100000`,
`sat_time_seconds<=30`. Its separate ordinary-action emitter and value checks
remain unchanged; the sequential cone certificate does not certify SAT schedules.
SAT domain limits are 6 inputs, 32 gates, 64 nodes and 16 outputs. Python's
whole-process timeout is `sat_time_seconds+1`; direct JSON clients must impose
an external deadline. Horizon/conflict exhaustion does not establish global
infeasibility. Bennett, in-place Bennett, eager and the other methods retain
their existing behavior and do not require this cone certificate.

Build this composition into a new private directory with serial `-j1`, preserving
older executables. With `LOGIQUE_BUILD_CONTRACT_PROBES=ON`, CTest runs action,
value and SAT probes. Keep `build_provenance.json`, `sat_build_provenance.json`,
compiler commands, effective dependency hashes and the executable SHA256 together.
Exact whole-composition independent review remains necessary before integration;
a passing implementation test or queue completion is not scientific admission.
