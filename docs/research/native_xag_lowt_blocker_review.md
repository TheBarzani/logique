# Pinned XAG low-T mapping: independent blocker review

25 October 2026. Coordinator `coordinate-xag-lowt-1025072819`:
**BLOCKED; no low-T implementation admitted or integrated.** This is distinct
from completed predecessor coordinator `coordinate-mapping-1025030802`.
The original worker reached its four-attempt bound with dispatcher status
`blocked`; its `outcome=continue` checkpoint describes unresolved scientific
work, not admission. Its sole offered commit `09020b0` records the blocker.
All maintained candidate files were restored to `ce93291`; there is no owned
implementation commit to cherry-pick.

The full queue (27 jobs), dispatcher state, Git/worktrees, full research plan,
implementation audit, server manifest and supplied predecessor batch were read.
No prior completed batch for this assigned coordinator was found. Evidence is
in `dump/1025121607-xag-lowt-coordinator-triage/`. The original worktree and all
rejected candidate/build/test evidence remain in
`dump/1025072819-native-mapping-triage/worktrees/xag-lowt/`.

## Reproduced semantic failure

Let `p = a ^ b`, `q = b ^ c`, `l = p ^ c`, `r = a ^ q`.
The independently evaluated function `l & r` is parity `a ^ b ^ c`;
`l & ~r` is zero. With common preprocessing `none`, the frozen native candidate
selects the actual non-template pinned `caterpillar::xag_mapping_strategy`, on
bundled `mockturtle::xag_network`, and emits respectively:

```json
{"kind":"x","controls":[0,0],"polarity":[true,true],"target":4}
{"kind":"x","controls":[0,0],"polarity":[true,false],"target":4}
```

The coordinator fixture includes a fourth unused PI; the worker's original
three-input fixture has target 3. Both forms are invalid physical gate wiring.
Python rejects both with `ValueError: Invalid gate wiring`. No monomial
interpretation or circuit semantics is assigned to these invalid records.
Common `refactoring` simplifies these fixtures and passes coherent checks, but
cannot discharge the required `none` policy. Preprocessing was not forced.

The coordinator separately tested seven Boolean fixtures under both policies:
equal, opposite and included XOR cones, shared AND/XOR, XOR output, repeated
complemented PI outputs and an inner-AND cleanup fixture. The actual API
`oracle()` and `phase_oracle()` inverse compositions were interpreted with an
independent scalar X/Z interpreter on every input, every joint XOR-target value
and each selected phase output, including complete computational-wire restoration.
The admitted predecessor was checked for all fixtures; the candidate was checked
only where wiring was valid. **1,760 coherent checks passed**, with exactly the
two invalid-control cases retained as blockers. Monomial action on every tested
basis column establishes linear coherent action for those fixtures, including
relative phases; it is not a proof for all pinned schedules or dirty workspace.
No dense operators/statevectors were allocated.

All **105 omitted-control native comparisons** match the hash-verified admitted
build, across seven fixtures, five methods and omitted/none/refactoring policies;
only `native_seconds` is excluded. **Three historical-expression comparisons**
match gates, circuits, networks, mappings, steps and source parameters. Candidate
and predecessor preprocessing payloads match exactly for the 14 targeted rows.
These checks preserve defaults; they do not admit the opt-in strategy.

Two initial coordinator probe runs failed parsing compact Verilog emitted by the
new harness. The harness was corrected to conventional structural-Verilog lines
and explicit intermediate XORs; both failure logs remain. Neither failure was
excluded as a native semantic result. Final probe exit status is zero with both
blockers asserted. Sequential children used the existing research interpreter,
explicit root src/native/cache, single BLAS/OpenMP threads and 180-second timeout;
maximum recorded child RSS was **72,220,672 bytes**, below 8 GiB. No rebuild,
installation, fresh broad suite, notebook execution or historical replay ran.

## Actual pinned action and gate audit

Pinned Caterpillar revision is
`4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`. `get_fi` uses symmetric-difference
XOR leaves, retaining PI/AND/output-driver boundaries. For equal leaf sets,
`get_cones` places one root in the other's leaves and `gen_steps` emits
in-place parity computation, a buffer alias, the AND, then reversed cone
restoration. Restoration can be another `compute_inplace`, not a label named
`uncompute_inplace`. Its payload `target_index` denotes a node whose live stack
top supplies the physical target, not a physical wire number.

LHRS buffer actions push live physical-wire aliases without gates. The two AND
fanins therefore resolve to the same wire; `compute_node` forwards both to
`compute_and`, which emits an MCX. `RecordingCircuit` accepts and serializes
them without wiring validation. This is an emitter/alias contract failure despite
correct class selection and full action payloads. Repeated alias pushes also
require an independent restoration invariant before general admission. Existing
ordinary-uncompute stack-pop/best-fit compatibility overlays are separate;
no dependency patch, new shim, level strategy or solver was used here.

Input indices, output indices and raw phases were checked directly, including
nonstandard input order, an unused PI and complemented/repeated PI outputs.
Raw complemented PI outputs can modify data; the actual compute-copy-inverse
and compute-Z-inverse wrappers must restore it. The inner-AND fixture emits
**five actual Toffolis**, including its two inverse ANDs. A measurement-assisted
zero-T inverse is unavailable in this static X/CNOT/Toffoli emitter. Neither the
strategy's name nor serializer coverage establishes a low-T resource improvement.

## Identities, preservation and next bounded task

Verified identities include:

| Artifact | SHA-256 |
| --- | --- |
| Frozen rejected binary | `ff7b43b3c465b4096d91ea61a9a6aa8d9ffb870ea3cc145a289ab139f06e538e` |
| Admitted predecessor binary | `b4f1df2cc6c7928313b52bb5d062c3a835279f41f2a04edcc6eed9455af36032` |
| Pinned XAG strategy header | `6980dd085d51a2752a922914d5f7b9a07d0b8c9bff1e490f744d3e7852c89127` |
| Pinned LHRS header | `dab0018ff90d1901dbf4c9dee2f387f7595ddccf690e5eb6f5c94153c7150825` |
| Pinned bundled XAG header | `bc287e675b49a8e3d6773da50dccdacf0b2b63b4a8c1eb230e3d0d6706015da5` |

The 160 protected root/archive/history/prototype identities, 93 worker evidence
files and 52 source/header/overlay/build identities match. Original checkpoint,
README edits, rotations, prototype backups, histories, archives, binaries and
five Git pins stay unchanged. Existing queue definitions and prompt bytes stay
immutable. The exact rotation gate remains the separate restricted numerical
admission in `rotation_norm_admission.md`; this review extends no target,
contract, FT/RUS or paper admission.

Queue exactly one bounded correction slice: `native-xag-alias-fix-1025121607`,
then `native-xag-alias-review-1025121607`, then
`coordinate-xag-alias-1025121607`. The implementation and independent reviewer
use distinct isolated `codex/coloring-` worktrees at intake `f9a32d3`. Approved
profiles: native 1800s, critical_review 1200s, coordinator 1200s, four attempts
each; review/coordinator can triage blocked predecessors. Dispatcher alone
launches them. No additional mapping or MC/balancing slice is queued here.

The correction must derive explicit physical literal normalization for the
selected opt-in only: repeated equal polarities reduce to one literal;
contradictory polarities yield zero conjunction when the target is distinct.
Target aliases/noninvertible cases must fail explicitly and remain blockers.
No invalid gates, silent fallback, forced refactoring, changed pins or free AND
inverse is allowed. Equal/opposite cones under both policies, alias-stack
restoration, full coherent semantics and exact legacy compatibility require
independent review of exact source/build hashes. Rejection of required cases
must not be advertised as full acceptance. Full remaining research scope is
retained in the audit and batch/manifest; the paper remains open.
