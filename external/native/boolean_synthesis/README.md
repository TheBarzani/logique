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
strategies. No new mapping algorithms or SAT controls are exposed by this batch.

The notebook compares these specific configurations, not published optimal
resource counts. It explicitly distinguishes raw clean-output computations from
the compute/copy/uncompute wrapper that accepts arbitrary XOR targets.
