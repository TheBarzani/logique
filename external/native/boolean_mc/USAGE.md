# Private pass-aware multiplicative-complexity recipe

This separate research executable instruments the actual bundled tweedledum
`xag_optimize` recipe at pin `a3cb238d132825b8e0367d5e96618c5753c1879a`.
Independent exact-source/build review is required before production use.
It does not enable `mc_reduction` in the synthesis API or comparison study.
The admitted balancing profile is a separate implementation and is not imported.

The exact sequence is constant-fanin, cleanup, satisfiability don't-care,
cleanup, refactoring, cleanup, xag_minmc cut rewriting, cleanup, constant-fanin,
cleanup, satisfiability don't-care, cleanup. Refactoring allows zero gain and
uses `free_xor_cost`; cut rewriting uses cut size 5 and `mc_cost`, exactly as the
pinned aggregate. Constant-fanin's internal cleanup is part of that pinned
operation; the subsequent explicit cleanup remains its own checked boundary.
The xag_minmc database is the bundled header, without downloaded extensions.

Every boundary compares all output bits on every positional input assignment
against both the original and preceding boundary. This is exhaustive classical
CEC, not a SAT certificate or an optimality proof. Each boundary also emits
Verilog, parses it back, and checks the readback with the same exhaustive domain.
Primary input indices (including unused inputs), primary output indices,
complements, repeated outputs and constants are preserved; names are regenerated.
The source and each active-node graph, truth strings, serialization and readback
graph remain available. Raw storage size includes dead slots; public graph nodes
omit dead slots and include dangling live nodes. Statistics count reachable AND
and XOR gates and their multiplicative depth, separately from raw storage size.
Truth strings enumerate assignment integers increasingly, input bit i = PI i.

The supported existing combinational Verilog frontend is capped at ten inputs,
4096 storage nodes and 1..16 outputs. Those caps precede CEC tables and each
optimizer operation. Source bytes are limited to one MiB. Parsing and optimizer
internals are not hard memory bounded; manual protocol callers also need an
outer input-size/process budget. This is not a general Verilog frontend proof.

Build in a **new** timestamped run, with a distinct copied source and output
directory, preserving every prior attempt. Use the existing project interpreter
and `logique.paths.new_dump_directory("mc-pass-aware")` to allocate that run.
The dependency checkout must be explicit, clean, and at the pin above:

```sh
cmake -S "$RUN/source" -B "$RUN/build" \
  -DTWEEDLEDUM_SOURCE_DIR="$PINNED_TWEEDLEDUM" -DCMAKE_BUILD_TYPE=Release
cmake --build "$RUN/build" -j1
```

No fetch, install or dependency build occurs. Save configure/build commands,
logs, exits, elapsed time and scoped RSS; enforce <=120s per child and the
assigned cumulative budget. Set compiler/BLAS/OMP/Accelerate/Rayon/Qiskit
parallelism to one. `build_provenance.json`, `compile_commands.json`, the compiler
depfile `CMakeFiles/boolean_mc.dir/main.cpp.o.d`, and `link.txt` identify the
actual compilation. Inventory and hash every resolved depfile input, verify
dependency files against the pinned Git blobs, and hash the final executable.
CMake's short record alone is not a complete depfile inventory or an admission.

`logique.synthesis.mc.reduce_mc_verilog(source, executable=private_binary,
artifacts=new_child_directory)` is the separate adapter. It independently
evaluates the returned graphs, validates literal Boolean CEC flags and the full
ordered protocol, and saves source/request/stdout/stderr/evidence. The artifact
directory must not exist. A missing/failed pass, changed function, malformed
protocol or timeout raises `MCOptimizationError` with `mc_evidence`; successful
earlier events and partial JSONL remain on disk. A timeout kills/reaps the
process group. Default timeout is 120 seconds, with no larger value accepted.
The caller must supervise cumulative time and memory. Persistence I/O failure,
SIGKILL of the adapter, host failure and arbitrary tool allocation are not
certified recoverable.

Run focused regressions with explicit candidate `PYTHONPATH`, import-path
assertions, `LOGIQUE_MC_EXECUTABLE` pointing at that exact build, and a fresh
permanent pytest basetemp. No installed tweedledum/native executable is changed.
This tool performs Boolean preprocessing only: no quantum mapping, coherent
oracle guarantee, matched nine-graph resource advantage or manuscript admission
follows from a successful run.
