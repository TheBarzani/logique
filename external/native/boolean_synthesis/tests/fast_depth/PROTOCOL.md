# Fast-lowT/depth API checkpoint

Task `native-fast-depth-1101052342`, 9 November 2026, assigned branch
`codex/coloring-native-fast-depth-1101052342`, base `de230cc`.
**Implementation remains incomplete; production/scientific admission BLOCKED.**
This directory contains a private diagnostic, not a production mapping adapter.
Independent exact-source/build review of these new bytes is still pending.

## Prerequisite decision

The current authoritative decision is
[`native_certificate_integration_20261103.md`](../../../../../docs/research/native_certificate_integration_20261103.md)
in the integration checkout. Review `8933d7c` blocks whole candidate `b4bce3c`
and admits **zero paths**, explicitly prohibiting partial extraction. Its remaining
defect accepts Boolean/float aliases in duplicate serialized integer leaf fields.
No such source was imported here. A production adapter cannot claim composition
with an admitted current certificate that does not exist.

The admitted SAT source is already present through `5ec2127`; mapping, SAT header,
native Python boundary and main CMake bytes still match their admitted hashes.
The current integration API has additional unrelated changes; this probe does
not import that API or substitute its older implementation. It imports the
assigned branch's actual `circuits.records` and `synthesis.result`, with path
assertions. No public strategy dispatch, defaults or dependency pins change.

## Actual APIs and bounded observations

The non-template `caterpillar::xag_fast_lowt_mapping_strategy` and
`caterpillar::xag_low_depth_mapping_strategy` both build and emit through actual
LHRS on the pinned bundled `mockturtle::xag_network`. Both classes are declared
in `xag_mapping_strategy.hpp`, not separate similarly named headers. This is
positive API feasibility evidence: **no build/API blocker was found**.
The low-depth probe uses its default ASAP mode; ALAP is untested.
LHRS `low_tdepth_AND` remains false: the actual primitives are static exact X,
CNOT and Toffoli, with no free inverse AND or FT T-depth guarantee.

The nine fixed fixtures per strategy use four positional inputs `b,a,c,unused`:
asymmetric polarized AND; equal/opposite parity cones; shared intermediate AND;
overlapping parity cones; repeated/complemented PI and constant outputs; no
outputs; zero constant output; XOR output. All 18 emitted responses pass raw
outputs, zero non-output scratch, actual emitted inverse and real Qiskit XOR/
selected-phase wrapper checks. There are 16 input assignments per response.
For each fixture with m outputs, wrapper coverage is `16*(2**m+m)` columns;
across both strategies the denominator is **1,536 columns**. These are exact
scalar permutation/sign checks, without sampling, tolerances or simulator arrays.
Observed raw widths are 4..9 wires. These are diagnostic fixtures, not a matched
graph-family performance comparison or preprocessing-equivalence study.

Each strategy also rejects seven declared inputs, a four-wire budget on the
shared case, zero budget and floating textual budget: eight expected rejections.
Domain caps inputs6/nodes64/outputs16 precede strategy/LHRS containers; an action
cap128 precedes LHRS invocation, and every qubit allocation enforces width<=128
or a smaller explicit budget. The checker repeats caps before scalar arrays and
wrapper construction. These bounds do not cap arbitrary input parsing: this
probe accepts only its finite built-in fixtures.

## What is missing

Final columns do not certify internal operand reads, cone-frame boundaries,
temporary copies, alias restoration or zero-before-release/reuse. The sequential
two-cone theorem `92784ef` explicitly excludes level strategies; SAT has its
own ordinary-action induction. Neither is extended by this diagnostic. No
production mapping header, public label or certificate is offered for admission.

The next implementation must independently track network `f_n`, physical `W[q]`,
live addresses, forward/restoring frames and every actual Boolean read for
`compute_level`/`uncompute_level`. It must account for `copies`, `target`,
singleton/empty frontiers and output preparation, verify zero **before** each
release and match generated gates/I/O/width against actual LHRS. In particular,
the pinned `uncompute_level` restores cone values and pops target mappings but
does not call `release_ancilla` on those targets; popping is not freeing.
The missing release can affect width, and no optimal allocation is claimed.

Dispatcher/coordinator action: resolve the existing certificate whole-chain
correction/review gate first, then deliberately compose exact admitted bytes
and implement/review that separate level-action validator. Do not repeat this
small feasibility corpus as a substitute. If two mathematical attempts fail,
the dispatcher must assign the focused Astrahigh successor; no recursive launch.

## Reproduction and saved evidence

Use the existing approved interpreter with candidate `PYTHONPATH`; use the saved
CMake executable and an explicit pinned Caterpillar path. Set all compiler,
BLAS/OMP/Accelerate/Rayon/Qiskit parallelism to one. Configure this directory as
a separate CMake source in a **fresh** dump run's private build, with Release,
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`, and explicit
`FETCHCONTENT_SOURCE_DIR_CATERPILLAR`. Build target `native_fast_depth_probe`
with `-j1`. Run `check.py <private-executable> <new-evidence-directory>`.
The checker refuses an existing evidence directory. CMake is offline when the
explicit existing source is supplied; no dependency revision is changed.

Saved run: `dump/1109213456-native-fast-depth-api/` in the assigned worktree.
Final executable SHA256:
`46ce01e18be6107c6d2486ed51907f14c99ab5e773ed940561b951a0a71cbafb`.
The final depfile inventory hashes 1,135 effective files. Existing LHRS overlays
are reused without new changes; overlay hash
`edd39ec5371dc33f985d6cf1ea0c3c0dd5c394da1cc69604afe92e23f3cbe7b9`.
Initial and budget-enabled executables remain in distinct build-v1/build-v2
directories. Final source snapshots, raw responses, stderr, command/exit/time
receipts, dependency/source hashes and checkpoint are saved. The initial v1
source was not snapshotted before editing; its binary survives, but its depfile
cannot establish the original probe-source hash. It is not the offered final build.

Final check: exit0, 0.638442 seconds, 65,880,064 bytes Darwin wait4 high-water.
The final serial build took 10.184879 seconds, 585,760,768 bytes. Declared bounds
were 120s/child, 600s cumulative, 2GiB/process; no hard memory or simultaneous
group-RSS enforcement is claimed. No statevector, Operator, density matrix, C5
run or research benchmark was executed. The prescribed unchanged-experiment
binary was hash-checked only; root default and every existing binary are intact.

Failures are retained: the first v2 build was requested before configure had
returned and failed to load the not-yet-created cache; it compiled nothing.
The subsequent sequential build passed. The first identity script had an escaped
newline syntax error; the distinct second script passed. These are harness
failures, not mathematical failures or native counterexamples. Inspection-only
missing-path/outside-worktree commands and truncated displays remain in the
session record. Selected Python Black/Ruff and `git diff --check` pass; no full
research-suite admission is claimed. No queue/history, README, archives, metrics,
dependency source or other worker files changed; no model launch, sync or push.

The first commit command lacked repository author configuration and failed before
creating a commit. Subsequent explicit-path commits reused the existing HEAD author
identity for that invocation only; no global/repository configuration was changed.
Git bookkeeping has tool command/exit receipts without separate RSS measurements.
