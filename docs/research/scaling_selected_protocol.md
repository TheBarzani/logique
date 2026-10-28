# Selected Task8 preparation and execution protocol — 28 October 2026

This is a preparation protocol, not a frozen full experimental protocol or a
scientific admission. Integration `a9dbc55` withholds the scaling implementation.
Its exact-hash gate, `docs/research/scaling_study_admission.md` on the integration
branch, binds re-review `5411998`, report SHA256
`da9a3ac97a5f1aa1918cc4c213a1fa333421aeec7e9c435fc9f581faa38c12ca`.
No compiler experiment is authorized by this preparation's completed status.

The worker stays on its assigned fresh branch at intake `fc734b3`; it has not
fast-forwarded to a purported validated implementation. The integration gate is
BLOCK, not an admission. Original scaling source, B1/B2 evidence, cleanup-race
failures, tiny pilot and 145 mapping-suite failures remain unchanged. The full
plan's selected scope is retained below and in the configuration/ledger.

## Inputs and colors

Primary acquisitions use the [CMU DIMACS archive](https://mat.tepper.cmu.edu/COLOR/instances.html).
Original bytes, URLs and SHA256 values are in
`datasets/graphs/scaling/primary/provenance.json`. No secondary mirror was used.
Local/legacy audit found only myciel3–5 and the three already-restored selected
inputs; it found no missing requested larger inputs in legacy/vcgc.

| Requested entry | Explicit parameters | Preparation result |
| --- | --- | --- |
| queen families | Generated square boards n=5,7,9; k=5,7,11 | 25/49/81 vertices, 160/476/1056 undirected edges; verified formula witnesses |
| myciel6 | Primary DIMACS, k=7 | 95 vertices, 755 edges; verified greedy witness |
| myciel7 | Primary DIMACS, k=8 | 191 vertices, 2360 edges; verified greedy witness |
| DSJC125.1 | Primary binary DIMACS, k=5 | Decoded 125 vertices, 736 undirected edges; witness unknown |
| le450_5a | Primary DIMACS, k=5 | 450 vertices, 5714 edges; witness unknown |
| queen8_8 | Preserved legacy DIMACS, k=11 | 64 vertices, 728 unique edges; verified formula witness |
| 5-FullIns_3 | Explicit unprecolored legacy transform, k=8 | 154 vertices, 792 edges; verified greedy witness |
| 4-Insertions_3 | Explicit unprecolored legacy transform, k=4 | 79 vertices, 156 edges; verified greedy witness |

All k values are experiment parameters, never chromatic-number assertions.
For square queen families, vertex `1+r*n+c` denotes square (r,c), and attacks
are equal rows, equal columns or either diagonal. The positive assignment is
`(r+2*c) mod k`, checked on every edge. The generated family has no claim of
byte identity with primary DIMACS files. The legacy queen8_8 edges and labels
match this generated definition exactly after undirected deduplication.

DSJC decoding follows primary
[README.binformat](https://mat.tepper.cmu.edu/COLOR/format/README.binformat) and
`bin2asc.c` from the linked `binformat.shar`, read as data without executing it.
Rows use `(i+8)//8` bytes and MSB-first column bits. The original header says
1472 edges; its lower triangle contains 736 edges. The decoded file records
736 and retains the original binary and discrepancy receipt. Likewise the
legacy queen8_8 header/records count both orientations (1456), which the graph
model reduces to 728 unique undirected edges. Neither discrepancy is hidden.

The full-plan unprecolored normalization policy is applied only to exact-hash
allowlisted `5-FullIns_3` and `4-Insertions_3`. Their original `n 1 0` records
are removed in **new** dump files; the original bytes, edge records and source
provenance remain intact. These are new unprecolored graph predicates, with no
fixed-precolor claim. Other precolored inputs remain unsupported; the helper
refuses arbitrary precolor removal. No precolored experiment is run.

Greedy saturation-degree selection has deterministic label tie-breaking and
no search/retries. A failed greedy attempt means unknown, not UNSAT. All M
values remain unknown; positive witnesses establish existence only. The
independent graph predicate checks labels, range and every edge. These checks
do not establish source/preprocessed/mapped Boolean equivalence, phase,
arbitrary-target action, workspace restoration or quantum performance.

## Bounded next execution, after admission

`configs/coloring_scaling_selected.json` is deliberately preparation-only and
cannot be passed to the old `synthesis_scaling` runner. It specifies five real
repeats per case, `xag_bennett`, two encoder profiles (left-associated and
balanced), and native preprocessing `none` for both. Validation seeds are
11/23/37/53/71; the bridge has no native random seed control. Controlled planted
multipartite graphs use n=16/32/64, densities 0.2/0.6, k=2/3, graph seed1729.
The corrected harness's planted-family generator is to be reused after its
admission; no unadmitted runner is imported or executed here.

There are 22 cases × 2 profiles × 5 repetitions = 220 explicit pending rows.
Every row currently says `blocked_admission_not_launched`, with all measurements,
responses and circuits null. Compiler attempts are zero. After release, prioritize
queen-family-5, queen8_8 and planted n32 before other cases, so the next bounded
execution produces meaningful larger evidence rather than only tiny fixtures.
Unknown-witness cases remain in the ledger; they cannot supply eligible positive
branch evidence without a checked witness or an independent UNSAT proof.

Each child gets at most90 wall seconds, charged against900 cumulative boundary
wall seconds including failures/cleanup; last calls get only the remaining
budget. The limit is below the user ceiling180. All remaining cases/repeats
receive explicit exhausted/unsupported/missing/unknown statuses. Six GiB is the
memory budget (<7 GiB), threads1, one numerical process at a time. Current
withheld runner lacks a configurable6 GiB limit and robust failure accounting;
both must be implemented and independently admitted before using this config.
No hard memory reservation is claimed from polled RSS. Wait4 high-water can
include reaped descendants and is not simultaneous group RSS; unavailable group
sampling is null. Validate estimated allocations before arrays; max64 MiB
response, max512 MiB estimated Boolean-validation arrays. No quantum simulation,
lowering, statevector or dense Operator is planned for this compiler batch.

Before release, correct leader-exit cleanup/reap and charge failed launched work
or stop conservatively; retain the independent race/ledger regressions and get
a fresh exact-hash bounded review/integration. Verify the required private binary
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No build or pin change is part of this preparation.

## Timer export

`python -m logique.benchmarks.scaling_timers SAVED_RUN_JSON NEW_OUTPUT_JSON`
performs a read-only saved-response export with SHA256 verification. Bridge
`main.cpp` writes the key `native_seconds` after stdin JSON decoding and before
final `result.dump()`/stdout write. It includes source file read/parse, output
selection, preprocessing, representation conversion, mapping and construction
of response graph/gate/action JSON. It is **combined**, not disjoint native
optimization and mapping time. The required private build's main.cpp bytes
match this checkout (SHA256
`dcab4d7f3e6530a0071dde894776e1ae2ca4ae351807dfe27b7750ebbc375635`).

Boundary wall covers setup, communication, observing completion and cleanup and
overlaps native time. Their nonnegative difference is an aggregate residual,
not a measured polling/cleanup stage. Missing timers stay null; optimization,
mapping, lowering, polling and cleanup fields stay null. Historical timer export
does not repair old resource labels or retroactively admit the pilot. Saved
response artifacts are reused; no new circuit artifact exists in this batch.

Independent review must bind exact source/config/input/ledger/export hashes and
state a bounded decision. Full Task8, broader methods/profiles, quantum semantic
validation and the full manuscript remain open. No superiority, FT/RUS or
ideal-amplitude approval follows from this preparation.
