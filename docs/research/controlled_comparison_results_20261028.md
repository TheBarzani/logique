# Controlled comparison implementation and evidence — 28 October 2026

This is an unreviewed bounded implementation/evidence report. The dispatcher
owns a separate independent exact-hash review. Neither execution completion nor
this report admits comparative superiority, a full protocol freeze or the paper.
The fixed post-pilot parameters are in [experimental_protocol.md](experimental_protocol.md).

## Implementation audit and reuse

| Area | Reused capability / connected change | Remaining limit |
| --- | --- | --- |
| coloring_study.py | Complete/effective predicates, actual A/inverse, signed reflection, independent XOR/phase checks, positive witnesses, saved-QPY signature/readback; explicit profile keyword and optional structure methods connected | Exhaustive through12 inputs, sampled above; no general large-function proof |
| synthesis adapters | Five existing methods; common native none/refactoring before representation conversion; balanced encoder with native none; baseline labels/LSB order/R3 power-of-two transform retained | Defaults are actual implementations, not claims about whole algorithm families; original baseline's multi-edge defect excluded |
| preprocessing | Both before/after exported networks checked against independently evaluated graph predicates; balanced AND/OR associativity preserves leaves/order | Finite larger checks are not CEC; no claim that native refactoring exposes a SAT proof |
| balancing.py | Standalone tool supports xag_balance/algebraic/esop with per-pass and serialization CEC | No end-to-end profile connected/admitted here; MC reduction also open; no silent substitution |
| MCX/costs | Existing exact restoring clean_tree/fresh_zero on disjoint raw/A/S0 pools; actual lowered inverses; barriers preserved for structure | k<=8,data<=21,controls<=20 subset; no dirty/conditional-workspace borrowing or other-policy admission |
| structure.py | Admitted sequential/parallel logical oracles exposed as distinct methods; private parallel comparator scratch retained | New common-lowering integration awaits this batch's review; no parallel timing claim at sequential width |
| provenance | Candidate source/input/native hashes, environment/versions, stage scopes, original removed precolors, readback/QPY hashes and resource receipts | Split optimization/mapping times and backend live scratch remain unavailable; wait4 is descendant-inclusive OS high-water accounting |
| metrics/routing | Counts from saved resolved QPY; common U/CX opt0 seed7; strongest matched available baseline with geometric means and W/T/L, available-baseline denominator added | Logical is mixed granularity; no general wide transpiler equivalence, FakeTorino/FT measurements or manuscript certification |

The old 144-case/720-row K3/K5/myciel3 QPY pilot is historical. The later
serialization and restoration admissions were audited; their bounded contracts
are inherited, not broadened to certify this new bundle. No old evidence,
failures, binary, dependency pin, saved output, history or root README is replaced.

## Evidence

Run: `dump/1028080100-controlled-comparison/`; checkpoint:
`dump/1028075514-comparison-protocol-checkpoint/` in the assigned worker checkout.
Runnable implementation commit: `7bacf43df5f4beac0003d5a515676f53c52e3b39`. No native/build commit.

The nine-graph requested ledger includes **729 original-method regime requests**
(9 graphs × 3 profiles × 9 methods × 3 regimes), plus162 separately named
structure requests. The supervisor records297 graph/profile/method child groups:
**253 returned normally, one timed out at the remaining cumulative deadline,
43 were not run under the budget**. Returning normally includes cases explicitly
failed or excluded; it is not correctness or scientific admission.
All profiles were attempted on K3,K5,myciel3,grid6,K10,K20,myciel4. Myciel5
has22 normally returned groups, one timed-out balanced/xag group, and10 unrun
groups; all33 2-Insertions_3 groups remain unrun. Every graph has a verified
positive witness and explicit negative/boundary assignments in the ledger.

Accepted saved rows: **4380 =1800 logical +1290 restoring-MCX +1290 common-basis**.
All4380 were reloaded in a separate recount process, hash checked and
recounted against artifact records and CSV width/gate/depth values. Accepted
logical cases:360 (K3,K5,myciel3,grid6). Accepted common/restoring cases:258
(K3,K5,grid6). There are no accepted cost rows for K10,K20,myciel4,myciel5 or
2-Insertions_3. The full nine-graph execution/comparison is therefore unfinished.

Created logical case records contain360 complete,102 excluded,297 failed and
one interrupted/running entry in the timed-out child. No timed-out child's rows
are published. Logical exclusions include69 sb_original multi-edge cases and33
instruction-cap cases. The297 failures are84 unsigned32-bit format errors and
213 argument-range errors in QPY export. Common/restoring records contain258
complete,27 sb_original exclusions and12 failed cases: six best-fit resolution
limits and six sb_simple MCX>20-control limits on K5. The requested-component
ledger overrides the interrupted child with timeout and retains every unrun row.
All partial QPY, failed manifests and command logs remain saved.

The new wide-QPY blocker is concrete: a separately logged, no-decomposition,
no-statevector/no-Operator boundary probe roundtrips closed MCX with31 and32
controls, but33 controls raises `error: 'I' format requires 0 <= number <=
4294967295`. Installed Qiskit2.1.1 `CIRCUIT_INSTRUCTION_V2_PACK` ends in `II`,
and `_write_instruction` packs `num_ctrl_qubits, ctrl_state` there. Closed
control state is2^controls−1. Larger raw/marking/diffusion export requires a new
bounded, phase/restoration-preserving representation and independent review;
changing a control state or silently choosing another decomposition is invalid.
The boundary probe is evidence of the format limit, not a repair or admission.

Study execution781.697094s; including its bounded recount **821.768766s**,
below900s. The longest child took17.593811s (configured per-child maximum30s;
the deadline-clipped timed-out child received2.641221s and took2.647851s including
cleanup). Largest sampled process-group RSS and waited-child OS high-water were
**553861120 bytes**, below7GiB. Recount:40.033229s, sampled205504512 bytes.
One near-deadline ps probe timed out; its unavailable sample is recorded, with
other group observations retained. RSS sampling is not a hard instantaneous
allocation ceiling. The separate boundary probe took0.305785s, sampled64667648
bytes. No dense quantum arrays were allocated by either experiment harness.

Final focused regressions: **313 passed,31 deliberately deselected**,23.76s
pytest time,24.177197s supervised boundary, sampled244482048 bytes. The31
exclusions are the previously identified wider dense tests. Black/Ruff/diff
checks passed on the seven committed Python paths. Earlier interrupted
sandbox-monitoring attempt and three outdated barrier-expectation failures
remain in the checkpoint; no full-suite/build/notebook/historical replay claim.

Strongest-baseline outputs contain9270 detailed metric ratios and2835 summary
context rows, with geometric means and W/T/L. Available-baseline counts are
explicit:8190 detailed rows have three baselines,1080 have two; none have an
invented missing-baseline ratio. `unmatched.csv` is empty. No weaker-baseline
averaging occurs. The following **descriptive slice** gives all seven candidates
at none/R3/oracle, seed7,j1. Ratios are candidate/strongest available baseline;
GM<1 is a lower cost. n is only the graphs surviving that exact context, not
nine. The complete per-profile/regime/component/level tables remain in saved CSV.

| Level | Method | n | Width GM (W/T/L) | Gates GM (W/T/L) | Depth GM (W/T/L) |
| --- | --- | ---: | --- | --- | --- |
| logical | xag | 4 | 1.5165 (0/0/4) | 1.5320 (1/0/3) | 2.5630 (0/0/4) |
| logical | aig_bennett | 4 | 4.3144 (0/0/4) | 2.4443 (0/0/4) | 1.6263 (0/0/4) |
| logical | xag_bennett | 4 | 2.4501 (0/0/4) | 0.9282 (1/0/3) | 0.7533 (3/0/1) |
| logical | klut_bennett | 4 | 1.2649 (1/1/2) | 0.7702 (2/0/2) | 1.9184 (1/0/3) |
| logical | best_fit | 4 | 0.7355 (4/0/0) | 1.5515 (2/0/2) | 5.8786 (2/0/2) |
| logical | structure_sequential | 4 | 1.2973 (0/0/4) | 0.9060 (1/0/3) | 1.7161 (1/0/3) |
| logical | structure_parallel | 4 | 1.3489 (0/0/4) | 0.9060 (1/0/3) | 1.3022 (1/0/3) |
| common_basis | xag | 3 | 1.2477 (1/0/2) | 1.4434 (0/0/3) | 1.5611 (1/0/2) |
| common_basis | aig_bennett | 3 | 3.5004 (0/0/3) | 4.2956 (0/0/3) | 2.5315 (0/0/3) |
| common_basis | xag_bennett | 3 | 1.9995 (0/0/3) | 1.0526 (0/0/3) | 0.8870 (2/0/1) |
| common_basis | klut_bennett | 3 | 1.1336 (1/0/2) | 2.7385 (0/0/3) | 3.9865 (0/0/3) |
| common_basis | best_fit | 3 | 0.7765 (3/0/0) | 4.7949 (1/0/2) | 6.9703 (1/0/2) |
| common_basis | structure_sequential | 3 | 1.4002 (0/0/3) | 1.1812 (1/0/2) | 1.3403 (1/0/2) |
| common_basis | structure_parallel | 3 | 1.4257 (0/0/3) | 1.1812 (1/0/2) | 1.3444 (0/1/2) |

These finite resource results show losses and tradeoffs, not superiority.
Logical and common rows use different explicit MCX/representation scopes and
must not be combined. Larger preprocessing equivalence remains sampled;
common-basis general wide transpiler equivalence remains outside prior
admissions. See the full requested ledger for unsupported MC/cut-ESOP profiles,
FakeTorino five-seed targets and static FT precision obligations. The partial
protocol is fixed for these bytes; the full protocol remains unfrozen.

Next: independent exact-hash review of implementation, process/metric controls,
structure integration and this evidence. Then a bounded wide-MCX QPY correction
and independent review, followed by a newly budgeted run of the43 unattempted
child groups and failed wide cases. Do not rerun completed successful groups or
reuse this exhausted execution budget as authority for an unbounded continuation.
No model worker or successor was launched here; dispatcher retains ownership.

## Selected immutable identities

| Evidence | SHA256 |
| --- | --- |
| `dump/1028080100-controlled-comparison/batch.json` | `249efd24052c7da480fdcfdee42eb709342484eee158d7cf9bedb6fcb44ca509` |
| `dump/1028080100-controlled-comparison/summary.csv` | `0c32248c50f7180794366acebe67bf3a0c67587ecbc7252bb0eac955e42f2517` |
| `dump/1028080100-controlled-comparison/strongest-details.csv` | `142080ef4b31bc45713eb5bf02f56459b35ba70774e3a67bb6ac295ff274213e` |
| `dump/1028080100-controlled-comparison/strongest-summary.csv` | `19bbdab4b7f7b995ad7f84e259264aad82af69fcbe1737ac9ddf1fafe7d3e34a` |
| `dump/1028080100-controlled-comparison/requested-ledger.csv` | `38b6b25dadac2ea010777151b3300ad0ce1ca4f680e9baa20b7d6da382ebad30` |
| Pre-study `experimental_protocol.md` | `d2e17e5630e3b4f30de759218ae50043edd088faa95a384e78f4eeca294676a9` |
