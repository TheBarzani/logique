# Independent C5 calibration-order and cumulative-source review

**ADMIT the five exact source/config/test/tool paths below as a bounded C5
best-fit noise adapter. Bounded review COMPLETE; zero new shots or scientific
noise observations. Full scientific/manuscript gate remains BLOCK.**

Task `c5-calibration-order-review-1113162936`, session
`01a1f9d5-3107-72c1-a4db-2e736355d7e1`, attempts001–003, 20 November2026.
Assigned branch `codex/coloring-c5-calibration-order-review-1113162936`;
starting base `f7432e3f47593b9ab0b9a7634710c34beaeb8b60`.
The exact candidate and current admitted dependencies were deliberately composed
by fast-forward to `4d89fb6f6705204176d40e74c67adb13c4b4dbd2` in this review
worktree. No candidate bytes were edited and no root source was written.
Evidence: `dump/1120114852-c5-calibration-order-independent-review/` (R1) and
`dump/1120122319-c5-calibration-order-review-closure/` (R2). Final checkpoint is
R2 `checkpoint.json`; prior receipt/time charges are carried forward.

## Exact whole-path decision

Correctness candidate `1bf8095df78924d2eaab3e32ed79d3a08207f506`, separate
implementation handoff `4d89fb6f6705204176d40e74c67adb13c4b4dbd2`.
All committed candidate, candidate working and composed-review bytes agree.
Admission concerns this entire composition over current admitted root
`ad0191ae0d74ac3c440a371e5a53e5705f985113`, not a patch applied to an older caller.

| Newly admitted whole path | SHA256 |
| --- | --- |
| `configs/c5_best_fit_noise_adapter.json` | `2cea9cd979cd2e37824128e055a8df5ecc9643edd7df64a1f5df38d025a85d63` |
| `src/logique/benchmarks/c5_noise_adapter.py` | `340b382354409d8e157c5b4c6f3a6830c8e24a15d822397c73f92dd3a8948a10` |
| `src/logique/benchmarks/noisy_iterations.py` | `b442146d972b22a4680e123f3247d21be1aa7d6f10a85aaa7118826792cf27df` |
| `tests/test_c5_noise_adapter.py` | `bc64e715d09774c1142fb224280560b12991c3923523ca9463661f360e5e09c2` |
| `tools/check_c5_noise_adapter.py` | `248c393387610d8bea2a91ae9210dc9e5a4a4499f39ac7e176cdd5e9a33dc637` |

This supersedes the source BLOCK in review `10cecfe` only for these corrected
cumulative bytes. Original `ad6c463`/`55be27b`, the failed snapshots and the old
review remain unchanged. The complete 1,216-line noisy caller is byte-identical
to that earlier adapter candidate; it was reviewed again with the corrected
adapter, selectors, physical compaction, QPY/layout checks, persistence,
finalization and inherited component semantics.

| Inherited whole path; prior admission retained | SHA256 |
| --- | --- |
| `src/logique/benchmarks/metrics.py` | `6ff3ef194a8cb3fec5e3adb2869daa939687d2c351780c14725fde5c029e84b9` |
| `src/logique/benchmarks/costs.py` | `3500fcddd2738bdd69a6966d2d3cd06c76558bd4fdcf94ad46ccb9b4f2b89e9e` |
| `src/logique/benchmarks/routing.py` | `b35f6eaaeba466f3393f0a42c39f15c74f26fb2539056eec68ea9add6730db8d` |
| `src/logique/benchmarks/iteration_study.py` | `c941aef068bb848174652644530d9f3fafc8e4e55c872f34b619753f76bd22c5` |
| `tests/test_component_lowering.py` | `9a37625010cb4c4df6d1cfb40efc0b54d728d34fa6826f135a292742843a898a` |

The costs dependency includes the independently admitted dirty20 fail-closed
exclusion (`7a84d98`, integration `bff425e`), rather than restoring the older
unsafe constructor boundary. Other component paths retain `a689221`/`cf678f72`.
The 172-entry source/context inventory agrees with current root outside the five
offered paths, including current QPY helpers/native dependencies. Eleven actual
Logique imports are asserted into this composed checkout. New native/scaling
or resource-plan behavior is not admitted by these tests; no native call/build
occurred. Separately blocked selected-noise resource work remains blocked.

## Why the calibration repair is correct within this schema

Independent top-level local errors form a map keyed by error type, one operation
and its ordered physical qargs. These records are separate attachments, so their
serialization order does not specify channel composition. Inside a record,
branch probabilities, instruction sequence, matrix rows/scalars, instruction
qargs and readout rows do specify the channel and remain ordered and exact.
The repair discards only generated top-level error UUIDs. It rejects duplicate
identities, unsupported/default/nonlocal records, extra fields, multiple
operations/locations, wrong arity, repeated/negative/noninteger wires and
nonfinite JSON numbers. Supported operations are exactly the installed schema:
quantum `id/reset/sx/x/cz`, readout `measure`.

Canonical JSON retains scalar types; no tolerance or matrix approximation is
introduced. The guard separately binds properties/configuration bytes to the
installed backend, parses the saved noise bytes with duplicate-object-key
rejection, checks the passed snapshot against that parsed file, and returns the
SHA256 of the original raw bytes. This is exact fixed-calibration validation,
not a general channel-equivalence algorithm or a hostile-filesystem guarantee.

Two fresh independent offline FakeTorino processes each produced965 unique
records. Their raw order differs, but an independently implemented keyed index
finds exact equality of every payload after UUID removal. The second real guard
accepted the first process's snapshot. Seed20261120 shuffles also pass without
changing the raw-file hashing contract. Both fresh processes reject18 controls:
probability, matrix entry/shape, readout, physical/internal qargs, branch and
instruction order, duplicate identity, unsupported field, float/bool wire alias,
nonfinite/scalar-type changes, changed properties/configuration/noise files and
duplicate JSON keys. The candidate tests add asymmetric fixture permutations,
unsupported-schema cases and rejection even when duplicated expected/saved
models match. Reversed real CZ qargs collide with the opposite attachment and
are rejected; asymmetric fixtures independently cover payload/order differences.

The original worker snapshot and both former reviewer regenerations still have
965 equal independent payloads and differing outer orders. Their saved hashes
match; the corrected real guard now accepts the original saved calibration.
Fresh snapshot hashes are `540faeef0f5d7e147eba2b291d4159eb096f8d83a20d2f5e969b22cba589eb95`
and `51f9ba0ea165fb5db63493165379057b89334df203a319691276d15f05f772d4`.
No saved calibration was rewritten to manufacture agreement.

## Components, pre-sampling persistence and request populations

The loader authenticates the frozen manifest and all component bytes before
using the complete-predicate eleven-wire oracle, retaining all84,441 U/CX
instructions and the actual emitted preparation inverse. It does not reconstruct
structure, remove domain checks or lower the components again. R1/R2 keep ten
data wires plus a clean output. Signed oracle/preparation/reflection contracts
remain distinct from routed full-state comparison up to a global phase.

The unique probe retains the prior independent review's explicit U-matrix/CX
permutation interpreter and toy prefix, with the obsolete calibration diagnostic
replaced by separate fresh-process checks. Complex128 seed20261113 covers every
binary data word in a coherent clean-output probe. No scientific sweep is replayed.

| Fresh bounded semantic check | Observation |
| --- | --- |
| Oracle maximum signed-amplitude error, no fitted phase | `8.960262534991317e-14` |
| Dirty-output probability | `1.6977312417420117e-28` |
| Actual A/inverse round trip, R1/R2 | `2.3273757686693185e-17` / `4.0460356557118353e-17` |
| Signed reflection, R1/R2 | `1.0728672184036494e-15` / `8.895664691085529e-16` |
| Unequal-damping/complex-phase local channel versus independent Kronecker sum | residual `0`; physical `[7,2]` maps to compact `[1,0]` |
| Noncommuting toy j2 prefix, routed coherent/marginal residuals | `3.3343117592679803e-16` / `5.551115123125783e-16` |

These are finite numerical checks below1e-10, not formal floating error bounds.
Asymmetric readout survives mapping; channels touching omitted wires are omitted
whole. A toy selected j2 builds both preceding coherent steps and routes once,
with no j0/j1 output. Its sampler is replaced by an interrupt after durable
`validated_pre_sampling` metadata. Counts remain absent, status interrupted.

The separately reviewed three-wire forced-kill fixture also passes: the child
reaches the pre-Aer boundary, stops, is killed/reaped with exit−9, and retains
validation/seed/layout metadata before parent reconciliation. Its process status
is interrupted, not a scientific120-second timeout. The fixture's ps result is
mocked1024bytes for synchronization; that value is not measured RSS. Its terminal
wait4 measurement is85,884,928bytes. These checks do not supply a new general
process-supervision theorem or establish C5 routing feasibility.

The original frozen ledger still has805 keys, including50 infeasible C5 R1/R2
structure requests and separate C5 R3 membership. The new best-fit ledger has
exactly `(6 R1 + 4 R2) × 5 = 50` unique source/manifest/regime/seed/iteration
identities, null counts and no launched output folders. At64 shots each,
3,200 shots are requested, **zero executed**. The legacy runner still rejects
the distinct manifest. No original ledger status or denominator is replaced.

Fresh authentication covers1,272 worker inventory entries,86 earlier worker,
90 earlier reviewer,50 frozen best-fit,15 original structure and211 original
ideal-pilot entries, with zero mismatches. These inventories overlap and are
not independent observations. The inherited404 family records/25,856shots and
401 missing family keys are neither recounted nor enlarged by this review.

## Validation, resources and scientific limits

Selected regressions: **94 passed, nine deselected**, with actual source imports
asserted and real `AerSimulator.run` denied. Six supervisor tests, two sampling
tests and the redundant worker cross-process test were excluded; independent
cross-process and local channel checks supply the relevant new evidence.
The forced-kill fixture is included and uses a mock sampler. No test shots ran.
Selected probe Black/Ruff and whitespace checks pass; no full-suite certificate.

| Supervised boundary | Exit | Seconds | Darwin wait4 high-water bytes |
| --- | ---: | ---: | ---: |
| First calibration process, carried from attempt001 |0|45.261418|620,593,152|
| Second calibration process |0|50.063912|663,191,552|
| Independent components/channel/selector |0|4.373834|224,231,424|
| Selected source regressions |0|6.076359|149,159,936|
| Whole-chain/evidence/calibration identity audit |0|17.087767|633,028,608|

Total122.863291s, including the carried first attempt; nested fixture time is
already included, not added twice. Before arrays:120s/child,600s cumulative,
2GiB declared process budget, one numerical/compile child, all configured
compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism1. Actual independent vectors
are at most11 wires, dense test Operators5, local channels2; statevector18,
dense5 and original staticFTdense4 ceilings stay unchanged. The exclusive-log
supervisor enforces process-group deadlines. Terminal wait4 is not live/group
peak or an OS hard memory cap. Initial inspection/static/Git tools have transcript
exit/time records without separately measured RSS.

The first process finished with a saved exit0 receipt during interruption; it
was not relaunched. Both interruptions and every earlier failed/partial artifact
are preserved. Initial shared Git metadata denial was resolved by scoped automatic
escalation; no automatic approval rejection. Absent guessed files and truncated
reads were resolved by actual paths/focused reads. No candidate numerical failure
or timeout was concealed. Existing absolute root interpreter only; no sync/install.
Prescribed native SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was selected/verified and never invoked. README, pins, histories, archives and
queue remain unchanged. No model/subagent, API/paid fallback, hardware or push.

The exact structure decision `24a3c91` is retained only for saved977-instruction
oracle `226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`
on clean data and its four original j0,1 ideal observations. No22-wire replay,
further structure iteration or general authorization follows. The ten separate
11-wire best-fit ideal observations are also not noise admission. Dirty20
rejection, partial FT/unpriced rotations and final Astra `be5d36b` scientific
BLOCK remain binding. No noise resilience, matched advantage or full-paper claim.

Next: the coordinator authenticates and integrates only the five exact admitted
whole paths, retaining current admitted dependencies; any semantic merge requires
new independent review. Then the existing `c5-admitted-missing-execute-1113162936`
owner may attempt missing-only distinct requests with64 shots,18 active wires,
120-second children and its assigned cumulative envelope, preserving exclusions,
null-count failures and actual receipts. Actual new evidence needs its separate
independent review. No blind replay of the selected K3 timeout is authorized.
