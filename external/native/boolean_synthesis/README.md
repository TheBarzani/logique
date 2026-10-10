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

Results contain source and mapped graphs, gate records, explicit wire mappings,
and mapping steps. Truth-table strings use most-significant bit first; fanin 0
is the least-significant assignment bit. Control polarity `true` means control
on one. Python expands LUTs with the installed tweedledum PPRM implementation.

The notebook compares these specific configurations, not published optimal
resource counts. It explicitly distinguishes raw clean-output computations from
the compute/copy/uncompute wrapper that accepts arbitrary XOR targets.
