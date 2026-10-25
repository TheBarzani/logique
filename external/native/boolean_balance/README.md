# Standalone Boolean balancing tool

This C++17 tool uses the pinned standalone Mockturtle checkout, independently
of Caterpillar's bundled version. It exposes existing `xag_balance`, algebraic
depth rewriting and ESOP balancing algorithms; these are not new algorithms.
Häner and Soeken's balancing work must be credited in research comparisons.

Build with `logique native balance-build --source external/native/boolean_balance`
and set `LOGIQUE_BALANCER_EXECUTABLE` to the printed path. Python callers use
`logique.synthesis.balancing.optimize_verilog(path, passes=("xag_balance",))`.
Each subprocess accepts one JSON request and emits Verilog plus stage statistics.
The structural Verilog frontends preserve primary-input index order.

Every pass uses an independent deep snapshot and a SAT equivalence check. The
serialized Verilog is parsed again and checked too, including a maintained
zero-input constant export workaround. SAT exhaustion, parse errors and process
timeouts fail explicitly. Counts include AND/XOR gates, network depth and
multiplicative depth. Build provenance records the clean pinned dependency
revision, source hashes and compiler. No dependency source is modified or fetched.

The tool is not yet connected to all controlled optimization profiles or native
mapping strategies. Merely building it does not validate a complete experiment.
