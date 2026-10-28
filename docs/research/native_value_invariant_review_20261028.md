# Native XAG value/restoration invariant review

28 October 2026. Task `native-value-invariant-1028023823`, session
`01a18376-7db5-7223-a433-5b087f743781`.

**Decision: the sequential pinned cone schedule has the compositional value and
zero-release invariant proved below, within the stated canonical-XAG domain.
The statement that every live stack top always equals its node is false and is
not the required invariant.** No accepted native counterexample was found. This
is a mathematical review, not unrestricted implementation admission. The old
`e2d054b` implementation remains unintegrated by this task; a new coordinator
must review this proof, its domain and a concrete validation change before an
implementation admission. Passing the probes alone would not justify that step.
The present bounded review is complete. Full revision, other mappings, MC and
SAT work remain open; the two exhausted task records remain blocked and immutable.

The review read AGENTS.md, CLAUDE.md, the full renewed plan and both 28 October
scope/batch records; actual correction `e2d054b53008b70d15e591bc4dbf1bdc11fd2aaa`,
its checkpoint, review `8b1d22c`, the root blocker review, and the abandoned
coordinator's `1026021312-xag-alias-coordinator-triage` evidence/state. That
coordinator stopped after 62 passing focused tests and a model-capacity error;
it did not establish value restoration. No old session, task or branch was
restarted or integrated here.

## Exact domain and source interpretation

This proof concerns only the non-template `caterpillar::xag_mapping_strategy`
on the bundled `mockturtle::xag_network`, the effective LHRS stack-pop overlay,
and `PhysicalBooleanCircuit` from the correction. It does not apply to arbitrary
sequences of the same action variants. In particular it does not infer correctness
of fast-low-T, level, depth, pebbling, cell, nonexplicit in-place or recomputing
schedules from their action labels.

The selected network must be a finite cleaned combinational binary XAG in
construction/topological node order, with canonical uncomplemented XOR children.
`create_xor` moves the XOR of child complements to the returned signal;
`create_and`/`create_xor` simplify constant children and identical-node fanins.
Ordinary AND-edge and output polarities remain explicit. The correction calls
`cleanup_dangling` before mapping, also after refactoring, so this is the actual
intended representation. Reordered or malformed hand-constructed networks are
outside this theorem unless these conditions are checked independently.

Let `D` be the set of output driver nodes. The boundary nodes are PIs, AND nodes
and `D`; a used constant zero is also a fixed boundary value. Define `f_n(x)`
by independent evaluation of the XAG, before output preparation. Define `F(n)`
as `{n}` at a boundary and the symmetric difference of child frontiers at an
internal XOR. Canonical XOR children give, by structural induction,

`f_n(x) = XOR_{b in F(n)} f_b(x)`.

The pinned `update_fi/get_fi` implements this frontier rule, stopping at output
drivers even when they are XOR nodes. Constants surviving cleanup are projected
outputs, not unsimplified gate children; they are allocated by LHRS only when
used. This proof also treats zero parity as the empty XOR. The pinned source
asserts that a newly formed internal frontier is nonempty: empty-frontier
execution is therefore supported only when assertions are disabled, as in the
recorded Release build. Debug aborts are not successes. The zero-frontier
transition case below explains the four such internal frontiers in saved
accepted Release schedules; it does not promise Debug compatibility.

Two source details matter. `is_included(first, second)` actually tests
`first subset second`, despite its misleading comment. `get_cones` first
reverses the pair if the **second** frontier is included in the first. Also,
`topo_view` changes `foreach_node` but inherits `foreach_gate`: the actual
strategy traverses stored gate order, while serialized graph nodes may appear
in output DFS order. The replay checks both distinctions.

## Inductive state and read obligations

Write `W[q]` for the Boolean function on physical wire q and `S[n]` for a node's
stack of physical addresses. Define a **block** as the entire `gen_steps` result:
prepare up to two cones, ordinary compute/uncompute of the central boundary
node, then restore the cones in reverse order. At each block boundary:

1. Every active boundary node b has a distinguished wire `q_b = top(S[b])`,
   `W[q_b] = f_b`, and distinct active boundaries have distinct wires. A used
   constant has its correct fixed value. PIs and computed output drivers are
   retained. Internal ANDs are active from their compute until their uncompute.
2. Every free wire is zero. Every allocated wire outside these active boundary
   wires is also zero. Empty-frontier computations may leave additional live
   zero wires; the theorem does not assert optimal allocation or empty stacks.
3. Nonboundary XOR stacks may contain old aliases whose contents are no longer
   `f_n`. Such aliases are not persistent Boolean values. Before any ordinary
   central fanin read, the enclosing cone block installs a current correct top.
   A reverse buffer reads a still-valid cone value before its anchor is restored.
   Neither a stack entry nor its live generation is a value certificate.

Within a block, attach a frame recording the entry boundary addresses/values,
cone order and each temporarily overwritten target. A forward in-place parity
has postcondition `W[top(S[root])] = f_root`. Its restoring occurrence has the
different postcondition that the saved target value is restored. The target leaf
is resolved as an **address** and skipped by `compute_big_xor`; during restoration
it need not currently contain its boundary function. All actual CNOT control
reads and ordinary central fanin reads must contain their stated logical
functions. Requiring the skipped leaf to equal its original value before the
inverse would incorrectly reject the correct reversible parity operation.

This distinguishes three operations often conflated by a stack-only audit:
resolving an address, reading a Boolean operand, and reestablishing a value after
restoration. `compute_inplace` pushes on both visits; `buffer` pushes and emits
no gates. Neither action name asserts an inverse or a pop.

## Local block proof for all frontier relations

At entry treat the boundary values `y_b = f_b(x)` as arbitrary independent bits.
An identity valid for all such bits also holds when actual boundary functions
are correlated. Let `P(A) = XOR_{b in A} y_b`. Apart from the inclusion rewrite,
cone leaves are boundary nodes; a nonboundary cone root cannot secretly be a
leaf of the other original cone. A singleton cone is either an unchanged
boundary root or an alias to its unique boundary leaf.

For a nonempty frontier A and target t in A, the emitted CNOTs implement

`W[q_t] <- W[q_t] XOR P(A minus {t})`.

With entry `W[q_t]=y_t`, this gives `P(A)`. With other controls unchanged, the
same CNOTs restore `y_t`. Source ordering of these CNOTs is irrelevant because
they have one target and unchanged controls. Distinct boundary addresses make
exactly one explicit leaf the target, as required by the correction's guard.

- **Incomparable frontiers:** each cone chooses a target in its own set
  difference. Neither target occurs among the other cone's leaves. The two
  parity preparations therefore read correct unchanged controls, produce both
  desired parities, and reverse without interference. Disjoint sets are included.
- **Proper inclusion A subset B:** after ordering the smaller cone first,
  its target is in A. The second cone replaces its leaves by
  `(B minus A) followed by root(A)`, and chooses a target in `B minus A`.
  It reads the first cone's current parity, giving
  `P(B minus A) XOR P(A) = P(B)`. Restore the second cone first, while
  `root(A)` still holds `P(A)`, then restore the first. All original boundaries
  regain both their addresses and values.
- **Equal nonempty frontiers:** the second rewritten cone is a buffer of the
  first root. Both fanin aliases hold the same parity on one physical wire.
  The inverse buffer pushes that same address back to the first root; the
  first parity inverse then restores its anchor. Equal physical literals reduce
  to one literal and opposite polarities to zero under the already reviewed
  distinct-target conjunction rule. No duplicate-control physical gate is
  assigned a meaning.
- **A singleton and a larger frontier:** the special source branch removes the
  singleton from the larger cone's target candidates if it overlaps, and puts
  the singleton first in that case. A different target always exists. Thus the
  singleton wire is unchanged while the larger parity is formed and restored.
  If disjoint, the source order is also safe. The singleton-root/buffer distinction
  changes only stack pushes; the inverse buffer pushes the same boundary address.
- **Two singletons:** distinct leaves already have distinct correct values;
  equal leaves reduce to the equal-cone buffer case. Any buffer pushes preserve
  the leaf address. Structural simplification may eliminate some of these
  abstract cases before strategy selection, which only narrows the domain.
- **Empty frontier:** its `compute_action{leaves=[]}` allocates a zero wire and
  emits no gates. If included in a nonsingleton frontier, its root contributes
  zero to the rewritten second parity. If paired with a singleton, that
  singleton remains unchanged. If both are empty, the second becomes a buffer
  of zero. The source's reverse occurrence is another compute, **not an
  uncompute**: it allocates another zero wire. This wastes zero workspace but
  changes no logical value and releases no dirty wire. It must not be described
  as cleanup/freeing that first allocation.

All branches of the actual two-cone generator are covered, including aliases
whose root is an AND/PI/output driver (singleton boundary), and aliases whose
root is an internal XOR with a singleton frontier. Reverse buffers can push to
an original boundary or to the first transient root in an inclusion rewrite.
In both cases they copy the same address; they cannot redirect a boundary to a
different live wire. Stale XOR aliases persist after restoration, but cannot
pollute subsequent frontiers, which stop only at boundary nodes.

## Central operation, release, and global composition

After the forward cones the two central logical fanins have values `f_u,f_v`.
An ordinary compute allocates a zero target distinct from every live control.
The AND emission toggles by `(f_u XOR sign_u) AND (f_v XOR sign_v)`; the XOR
emission toggles by their parity, including the complement parity. For AND,
physical equal/contradictory literal normalization preserves exactly that
Boolean function. For XOR, equal physical controls cancel through the two
actual CNOTs. Both give `f_n` on the new target, preserve the cone values and
permit the proved reverse-cone restoration. This establishes the block-boundary
invariant with n newly active.

For an ordinary uncompute of n, the target starts at `f_n` and its parents have
been prepared with the same correct values. The same toggle gives
`f_n XOR f_n = 0`. LHRS releases that zero wire and the unchanged overlay pops
one n-stack entry. Earlier duplicate entries may remain, but n is now inactive.
No later block reads n as an ancestor: cleanup proceeds in reverse topological
order. The generation guard can additionally detect stale-address reuse; zero
release follows from the value argument, not that guard.

The insertion iterator in `compute_steps` places each new compute before all
previous pending uncomputes. Hence the schedule is forward compute blocks in
stored topological order, followed by reverse-order uncomputes of non-output
ANDs. Output-driver XORs/ANDs are never uncomputed here. Each block's frontier
ancestors are therefore active when needed, and no discarded nonboundary alias
is a future frontier boundary. Initialization supplies distinct PI wires and
zero clean workspace, completing the induction for any finite schedule in the
domain. This is a structural proof independent of input count and of the finite
probe coverage.

Before `prepare_outputs`, all PIs are restored, output drivers hold their Boolean
values, and other wires are zero. Output preparation may apply X to a first
complemented output, including a PI. A repeated output copies that first wire
to a zero allocation and corrects polarity relative to the first occurrence.
This produces all requested outputs even when reordered or complemented. Raw
input restoration after this output phase is **not** promised. The actual
compute-copy-emitted-inverse and compute-Z-emitted-inverse constructions restore
all computational wires because each emitted operation is an exact permutation
with phase +1, with the Z supplying the intended selected phase. This reasoning
is for clean initial computation workspace; it does not assert a dirty-workspace
raw oracle, an arbitrary new wrapper, or measurement-assisted AND cleanup.

## Independent bounded evidence and an explicit stale alias

The new tool `tools/native_value_invariant_probe.py` imports no synthesis,
verification or quantum simulator code. It independently evaluates each saved
network into exact small integer truth tables, reconstructs block boundaries
from the graph and pinned set rules, replays stack allocation and physical gates,
and compares the complete gate list/width/outputs/final stacks with saved native
responses. The set-rule transcription is checked against all actual saved step
arrays; truth-table evaluation supplies an independent semantic check. The
proof above, rather than agreement of two implementations, establishes the
general claim.

Final results: **170 saved native responses; 652 block boundaries; 992 in-place
steps; 74 buffers; 491 compute steps; 175 zero releases; 8,120 operand-value
truth-table checks** (including boundary/output checks). Four internal empty
frontiers occur in these saved accepted Release responses. The cone-only probe
checks all **1,024** ordered frontier pairs over five independent boundary bits,
with **1,369** singleton-root/buffer variants and 32 assignments per variant.
The partition is 63 pairs involving empty sets, 31 equal nonempty pairs, 360
proper-inclusion pairs and 570 incomparable pairs. Input count is capped at six
before allocating truth tables; saved cases use at most five. There are no dense
matrices or statevectors.

`results-final.json` records source-response SHA256 for every replayed input,
node truth tables and full before/after wire tables and stacks at every action
of `equal-none`, `gate_alias-none`, `boundary-none` and `cancel-none`. In the equal
fixture, node9 and node7 both represent `x0 XOR x1 XOR x2`; each aliases wire0
at the central AND. Five-input table masks at the critical steps are:

| Step | wire0 | wire5 | Relevant stack tops |
| --- | --- | --- | --- |
| Entry | `aaaaaaaa` (x0) | unallocated | node1 -> 0 |
| Forward parity, node9 | `96969696` | unallocated | node9 -> 0 |
| Buffer node7 | `96969696` | unallocated | node7,node9 -> 0 |
| Central AND, node10 | `96969696` | `96969696` | node10 -> 5 |
| Reverse buffer | `96969696` | `96969696` | node9 -> 0 |
| Restoring parity | `aaaaaaaa` | `96969696` | node1,node7,node9 -> 0 |

At the end `S[9]=[0,0,0]` and `S[7]=[0]`: both are live but stale Boolean aliases.
For assignment integer 2, `f_9=1` while wire0 is 0. This is an actual accepted
network disproving the overly strong always-valid-stack invariant, **not** a
wrong-output counterexample: those stale aliases are never read as Boolean
operands after the restoration. The next block must recreate them if needed.

Five negative controls reject a live wrong-value alias, a nonzero release with
live distinct controls, an over-budget input count, a wrong but legally wired
emitted control, and a missing parity-restoration operand. They are checker
mutation tests, not alleged native counterexamples. Black and Ruff pass for the
new tool. No new native execution, build, installation or full-suite claim is
made; this review reuses the immutable native corpus rather than re-running old
scientific sessions.

## Concrete next implementation and admission gate

A fresh coordinator should assign a **new** bounded validation slice. Preserve
the pins and the exhausted records. The minimal small-instance implementation is
to extend the selected path's audit with exact Boolean tables, with an explicit
input/allocation cap, and to recognize complete two-cone blocks. Record/check:

- Independent network `f_n`, physical `W[q]`, stacks, live generations and a
  forward/restoring frame. Check every actual Boolean control read; exempt only
  the skipped in-place target address, whose saved/post-restoration value is
  checked separately.
- Zero before allocation/reuse and after each uncompute **before** release;
  equality of active boundary addresses/values at block exit; correct forward
  cone root and central result values. Do not check stale internal tops as if
  they were permanent values, and do not pop buffers to repair the wrong invariant.
- Exact generated steps and emitted gates, including normalized conjunctions and
  output-copy allocation/polarity. Output checks occur on both sides of the raw
  output-preparation boundary.

The present probe is a reference for these obligations, not production admission
code. If only capped truth-table validation is implemented, larger instances
must explicitly remain **unsupported by that validator**, not silently pass or
be advertised as unrestricted mapping support. A scalable follow-up can replace
truth tables with a per-block GF(2) expression certificate over independent
entry-boundary symbols: prove the two parity controls, their restoration, and
match the central AND/XOR expression to the graph definition. The case proof
above makes this possible without expanding global Boolean functions or changing
Caterpillar. Validate the canonical network/order domain as part of that gate.

Independent exact-source/build review must check that new validator, actual
wrapper behavior and these proof preconditions before the coordinator decides
integration. This task admits the **mathematical transition invariant for the
specified sequential domain**, not all actions accepted by a generic stack guard,
all native compiler behavior, or any old test corpus retroactively as unrestricted
scientific evidence. No T advantage, free inverse AND, FT, RUS, general
ideal-amplitude or paper approval follows.

## Provenance, resources, failures and handoff

Worktree/branch: `dump/1028023823-full-revision-implementation-coordinator/worktrees/native-value-invariant`,
`codex/coloring-native-value-invariant-1028023823`; intake HEAD
`fc734b386449e69716d0ac3018b878a23e05ba95`. Evidence directory in this worktree:
`dump/1028130709-native-value-invariant/`, created with `new_dump_directory`.
`checkpoint.json` records final owned commits, hashes, task/session, validation
receipts and next action. `source-identities.json` checks correction bytes
against actual `git show e2d054b`, the prior review against `8b1d22c`, exact
relevant source/overlay hashes, both binary identities and five unchanged pins.

| Reviewed artifact | SHA256 |
| --- | --- |
| Pinned XAG strategy, also effective build copy | `6980dd085d51a2752a922914d5f7b9a07d0b8c9bff1e490f744d3e7852c89127` |
| Pinned action/cone definitions | `2de93fa095a50deb546f6b8c8bddc445c7ddd949c2d4ca34b4d662138a2b992e` |
| Pinned LHRS | `dab0018ff90d1901dbf4c9dee2f387f7595ddccf690e5eb6f5c94153c7150825` |
| Effective LHRS overlay | `edd39ec5371dc33f985d6cf1ea0c3c0dd5c394da1cc69604afe92e23f3cbe7b9` |
| Bundled XAG network | `bc287e675b49a8e3d6773da50dccdacf0b2b63b4a8c1eb230e3d0d6706015da5` |
| Bundled topo view | `dcca205d516013807ec221508e9a9d690be9d387cc930320ffe9f330192ad55a` |
| Correction controls/audit header | `75c15af82adc2ec11e35af684e9e4e93ee6088199edb0498245e7d5c6e56365c` |
| Correction mapping header | `05724c3cdf1090452c56d96df5965e1f0667f3c8f7741e44dd6e6c20db445885` |
| New independent probe | `37de75199640688a77a5ea3c9d6fae2bc74b325ebc39b8c8c27e28f42ea8e61e` |

Pinned Caterpillar is `4c6f766cd0ffc62d37ab45edfe80c9f1eae44764`.
The old correction binary is verified as
`a36f421af12d3fae539afdef91a82356f421935bcb2dccd7687b0760f729d1b2`;
the newly prescribed default binary is verified as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
Neither binary was executed or changed. Evidence responses remain the previous
review's exact saved bytes, individually hashed by this probe.

All new numerical probes use the existing research Python, task-source
`PYTHONPATH`, root EPFL cache and one BLAS/OpenMP thread, sequentially. The
supervisor sets a 30-second per-child and 120-second cumulative child-time budget,
256 MiB per-child and 512 MiB combined live RSS budgets via sampling when available,
and records command/environment/status/time/OS wait4 high-water receipts. `ps`
sampling was unavailable in this sandbox, so sampled child/parent/group memory
is **null**, and the sampled memory ceiling was not enforced here. Explicit
input<=6, nodes/width<=256, steps<=4096 and input-file<=2 MB limits bound the
probe's allocations before truth tables/replay; no 8 GiB or hard aggregate-memory
measurement is claimed. Final probe: 0.145769 s, wait4 high-water 23,035,904 bytes.
The high-water is OS child accounting, not sampled simultaneous aggregate RSS.

Preserved failed runs: probe-1 transcribed the initial subset test backwards;
probe-2 then exposed DFS graph order versus inherited stored gate order;
probe-3 repeated that second failure with diagnostic context; probe-4 and the
final probe pass after source-correct transcription. These were review-harness
errors, not native counterexamples. All logs/receipts remain. Initial Black
formatting succeeded and Ruff reported two ambiguous `l` names; the names were
fixed, with the failure text recorded separately and final checks passing.
Initial inspection-only absent-path/truncated reads were followed by focused
source reads; they are not numerical evidence. The user interruption occurred
after the formatting/lint command had finished, leaving no active numerical job.

Only this report and the new probe are task-owned tracked changes. Root README,
old reviews/checkpoints, failures, corpus, histories, archives, dependency pins,
production sources and binaries were not edited. No broad recursive hash scan,
model/subagent launch, API/credit use, hardware operation or push occurred.
Dispatcher alone publishes integration HEAD. Next action belongs to the new
full-research coordinator: inspect this committed bounded proof, assign the
validation/independent-review slice, and retain all other full-plan work.
