# Private level-value adapter — 9 November 2026 continuation

Task `native-fast-depth-1101052342`; bounded implementation is complete.
**Independent exact-source/build review is PENDING. Public/shared production
integration and all performance claims remain BLOCKED.** This adds implementation
to the earlier feasibility-only checkpoint; its files and claims remain historical.

`adapter.run_level(path, executable=..., strategy="fast"|"depth", ...)` invokes
the new private executable's `--json` interface and returns metadata only after
`validate_level_response` completes. `adapter.synthesize_level` constructs the
raw circuit and usual restoring XOR/phase wrappers only after that gate. The
private bridge calls the actual non-template Caterpillar fast-lowT/default-ASAP
low-depth classes. It does not substitute Bennett or modify public dispatch.
Private result summaries retain their usual metadata fields; the saved seconds
measure the native process plus certificate boundary, not unavailable compiler
stage splits. Both `none` and `refactoring` preprocessing are explicit. Output selection may
be empty; declared inputs are retained. A 5-second process deadline surrounds
each adapter child. Original source files are capped at 2,000,000 bytes.

## Separate value argument and exact domain

This implementation does not use the sequential two-cone theorem as its proof,
and imports no files from the blocked certificate offer `b4bce3c`. The current
root decision/review `8933d7c` still admits zero paths from that offer. Current
admitted SAT source is already present in the assigned base through `5ec2127`;
its mapping/CMake/native Python hashes are explicitly compared with their admitted
blobs. The new private Python boundary and new native entry point are independent
of the rejected public sequential boundary. Their entire inherited/new chain
must be reviewed, including that distinction. No extraction is authorized here.

Before integer truth tables: inputs<=6, stored nodes<=64, outputs<=16,
width<=128 or the smaller requested budget, steps<=128, gates<=4096.
Canonical node IDs are consecutive; PIs are consecutive positional IDs;
gates are cleaned, reachable binary AND/XOR nodes in stored topological order,
with distinct earlier nonconstant fanins, uncomplemented XOR edges and exact
AND/XOR truth strings. All serialized indices reject bool/float substitutes.
The parser and optional refactoring run before this Python gate; these caps
are not a hard memory guarantee for arbitrary parsing/preprocessing.

For each accepted graph, independent `f_n` tables contain every assignment of
the declared inputs (at most 64 bits per table). The replay maintains physical
`W[q]`, address stacks, active boundary nodes and the actual LIFO free list.
Every emitted CNOT operand read checks `W[q] == f_n`; resolving the skipped
in-place target is an address operation. Every central control is checked against
its cone root. Cone leaf parity is checked against the graph, not an action name.

The replay follows the pinned level visitor's copy preparation, per-node parity
preparation, central operation, reverse parity restoration, stack pushes/pops,
copy removal and actual output preparation. Each node frame compares all prior
wire values and stacks, allowing only its computed/uncomputed target to change;
new residual scratch must be zero. Every action boundary checks distinct correct
active values and zero other wires. Copy release requires zero, no live top alias,
and no duplicate release. Reuse independently checks zero again.

The actual pinned `uncompute_level` zeros and pops central targets but **does not
release those wires**. The replay retains that behavior and separately counts
`zeroed_unreleased`; it never invents a free operation or credits a free AND inverse.
The native `low_tdepth_AND` flag is false. ALAP, measurement assistance, dirty
initial computation scratch and arbitrary strategy variants are excluded.

Before output preparation, PIs/output drivers have correct values and other
workspace is zero. A first complemented PI output can change the raw input;
later copies account for the first output's polarity. Actual compute/copy/inverse
and compute/Z/inverse wrappers restore the clean computation subspace. The
replay requires an exact typed JSON match to every actual emitted gate, I/O map
and width. These finite function checks establish the intended acceptance
condition in code; independent review of its implementation remains necessary.
Preprocessing/source-parser equivalence is outside this certificate.

## Fresh evidence and limits

Final corpus: 34 responses = two strategies times nine fixed fixtures plus eight
generated 12-operation Boolean programs (seeds1101052342..1101052349). Programs
and independently interpreted positional source operations are saved. Every
four-input assignment, every joint XOR-target pattern and selected phase output
is checked using actual Qiskit wrapper instructions, without simulator arrays.
The denominator is `2*16*(48+8*(8+3)) = 4,352` wrapper columns. The replay records
1,252 operand-value checks,100 frames,nine zero releases,five zero reuses and30
zeroed-but-unreleased central targets. Raw widths are at most nine wires.
Eight native cap/budget requests reject as expected.

The final 47-test suite additionally checks wrong live values, nonzero/live/double
release/reuse guards, a missing restoring parity, legally wired wrong gates,
strict nested/gate/I/O indices, canonical caps, dirty final workspace, and a
constructor sentinel showing malformed responses reject before construction.
Four actual file-adapter cases cover both strategies/policies, two cover empty
output selection, and two six-input file cases check64 assignments each and
384 additional actual wrapper columns. Thus the separate final numerical
denominator is4,736 columns, not a claim about all graphs or all preprocessing.
No accepted wrong-output counterexample was observed in this bounded corpus.
The adversaries are negative controls, not alleged native counterexamples.

Evidence: `dump/1109214935-native-level-value/` in the assigned worktree. The final
private executable is `build-v4/native_fast_depth_probe`; all earlier builds and
source snapshots remain distinct. Reproduction uses this directory's private
CMake project, explicit existing pinned Caterpillar source, Release,
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`, target `native_fast_depth_probe`, and `-j1`.
Use existing root venv Python with explicit candidate PYTHONPATH. Run `check.py`
with a new evidence directory, then pytest on `test_level_value.py` with
`LOGIQUE_LEVEL_CORPUS` and `LOGIQUE_LEVEL_EXECUTABLE` set to that corpus/binary.
Pytest's basetemp must also be new and inside the run directory. Actual candidate
imports are asserted. No existing executable or dependency source is changed.

Final build: exit0,10.734417s,619,839,488 bytes wait4 high-water. Corpus: exit0,
1.197444s,67,141,632 bytes. Final47 tests: exit0,0.793703s,77,316,096 bytes.
Declared limits were120s outer children,600s cumulative,2GiB/process,all relevant
parallelism1. Direct native children have5s deadlines. No hard RSS or simultaneous
group cap is claimed; inner native RSS/time in pytest is unavailable separately.
No statevector/Operator/density/noise/C5/research benchmark was run.

Preserved failures: build-v3 used `json.contains`, unavailable in the pinned old
JSON library. Build-v4 uses `find`; dependency pins are unchanged. A corpus command
was mistakenly attempted after build-v3 failed; it retained an empty directory,
FileNotFoundError and exit1 receipt. No native process ran in that failed attempt.
No failed mathematical attempt or wrong-output native case was suppressed. Earlier
scalar intake checks have tool receipts rather than separate RSS; final compile,
corpus,tests and identity receipts are supervised. The previous batch's v1 source
snapshot limitation remains in its immutable checkpoint, not repaired retroactively.

## Exact next gate

The already queued `native-fast-depth-review-1101052342` should inspect the entire
private offer and inherited admitted source, independently challenge this new
level-value induction, typed fields, cap order, frames, copy cleanup and emitted
gate/I/O matching, and state exact path/hash/commit ADMIT or BLOCK. Root coordinator
alone decides integration. Shared public composition with the sequential chain
requires correcting its existing typed-leaf blocker and new whole-chain admission;
no old decision is overridden. Semantic merges need independent exact rereview.
Larger domains, source/preprocessing CEC and matched qubit/T-count/T-depth studies
remain separate future work. No performance or manuscript conclusion follows here.
