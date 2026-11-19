# Selected noisy resource candidate — 13 November 2026

Task `noisy-resource-plan-1101151114`, worker branch
`codex/coloring-noisy-resource-plan-1101151114`, base `f82f0a7`.
Checkpoint: `dump/1113164414-noisy-resource-candidate/checkpoint.json` in the
assigned worker checkout. Source correctness commit: **`f0a2a06`**.
**Bounded implementation complete; independent exact review PENDING.
Scientific execution BLOCKED: feasibility of64 shots within120s is unestablished.**
No saved scientific circuit was evolved, sampled, rerouted or regenerated.

## Scientific question and decision

Can a distinct exact execution path complete the missing K3/k3 R2 seed37/j2
request under the original64-shot/120s protocol? The saved request has18 active
physical wires,12,098 instructions and126 local channel records. Static analysis
counts8,127 quantum-channel applications and six readout applications per shot.
Its two preserved timeouts remain failures without counts. In particular, the
reviewed120.006279s receipt identifies termination after durable pre-sampling
validation; it does not identify the internal Aer setup/sampling split.

The new candidate explicitly disables fusion while keeping dense complex128
statevector trajectories and the exact inherited noise decoder. It avoids an
additional approximation or changed channel representation, but **the measured
synthetic workload does not support a speed benefit**. No scientifically
justified retry is offered. Passing checks and completing this implementation
do not admit the method, the whole caller, resource feasibility or new counts.

Current root separately admits404 request records; this batch adds **zero**.
The original28 and later376 observations remain separate source generations.
No full-family, C5-noise, resilience, speedup or manuscript admission follows.

## Offered source and inherited identities

| Path at f0a2a06 | SHA256 |
| --- | --- |
| `tools/noisy_resource_candidate.py` | `77022826bd9cd6da860ec5ba20bb7bb4a0c6c44416454e3bf729b00400fc7ff8` |
| `tests/test_noisy_resource_candidate.py` | `33f12cbc4b88e2b4b7c301a84a2d633a9d356ea162fce36eb258d6bbfbabe211` |
| `configs/noisy_resource_candidate.json` | `0fc5d404d00330bd988fae6e371b2215b49115d0790628fcb9f9d51f0e6dd0e9` |
| `src/logique/benchmarks/noisy_iterations.py` | `0630dc70ecd0a8490acdff8dd661c2e939644be18bd500dd8be91dbae5e22385` |
| `src/logique/benchmarks/iteration_study.py` | `c941aef068bb848174652644530d9f3fafc8e4e55c872f34b619753f76bd22c5` |

The last two whole files were deliberately extracted from admitted integration
`cf678f72a0a293a7c1b97956565c8f50176fc313` and matched current root. They retain
the reusable-component initial-zero correction and explicit serial transpilation;
no new lowering claim is made. The decoder and supervisor used here are unchanged
by that correction. Their initial frozen-base checks are preserved separately;
final checks assert the current inherited file paths and hashes. The other four
cf678f72 paths are outside this tool's executed dependency path and were not
imported as a partial scientific lowering stack. This candidate never invokes
the component builder, router or scientific execution loop. The coordinator must
retain its complete newer root stack; these two already integrated paths do not
need reinstalling. Future whole-caller execution requires its own exact review.

The CLI has only static `analyze` and internally generated `fixture` commands.
There is no saved-scientific-circuit execution command. Final source snapshots,
exact input identities and installed Aer Python/controller identities are saved
in the checkpoint. Native synthesis was not invoked or rebuilt.

## Saved-input analysis and resource arithmetic

All35 worker-manifest entries and the explicit selected input identities verify.
Compact QPY remains SHA256
`534974314f3d5d39cd30a62b6391b50548d216ea741fcbff2b9fe21014561691`;
compact noise remains
`860eacdc1413b166a32bd1b21f8953a93f080a5255a3326a9875320d0783d548`.
The analysis preserves ordered channel payload hashes, physical layout and
LSB measurement order `[4,5,1,3,6,10]`. It does not reconstruct or modify any
channel. Physical-remapping and complete coherent validation are attributed to
the saved independent review, **not rerun or newly proved here**.

The circuit contains2,590 CZ,5,377 SX,160 X,2,454 RZ,1,511 delay and six
measurement instructions. Thus64 shots entail520,128 quantum-channel locations
and165,760 native two-qubit gate locations before trajectory-specific branching.
The absolute deadline allows120/64=1.875s per requested shot only if setup were
free; allocating all120s to channels would allow230.71 microseconds per channel
location. These are arithmetic constraints, not measured kernel costs or runtime
predictions. Import, decode, validation and completion also consume the boundary.

One18-wire complex128 vector occupies4,194,304bytes (4MiB). The inherited
eight-vector-plus128MiB estimate is160MiB; this is neither a guarantee nor RSS.
A full dense density matrix would require1,099,511,627,776bytes (1TiB) before
overhead and is forbidden. No such allocation occurred.

## Synthetic evidence, with exclusions

Installed versions are Qiskit2.1.1, Aer0.17.2 and NumPy2.2.6. Fixed fixtures use
four layers of asymmetric RY/RZ rotations, reversed adjacent CX gates and SX;
unequal damping acts on an ordered two-wire pair, another damping channel acts
on SX, and readout is asymmetric. They contain only eight quantum-channel
locations per shot. The18-wire fixture has218 instructions, **not12,098**, and
does not reproduce the scientific circuit's entanglement or noise density.
Each measured fixture requests and returns64 shots with simulator seed74730.
These histograms are explicitly **non-observations** for the coloring study.

| Final-source fixture | Boundary wall seconds | Aer reported seconds | wait4 high-water bytes |
| --- | ---: | ---: | ---: |
| 18 wires, fusion disabled | 5.929408 | 5.586565 | 96,731,136 |
| 18 wires, fusion enabled | 5.136565 | 4.782486 | 96,698,368 |

Earlier preserved repetitions were6.011891/5.181576s respectively. Two small
repetitions give no reliable runtime distribution, throughput model, speedup or
full-row forecast. Disabling fusion was slower on these fixtures. Aer reports
`noise=kraus`, serial shot/state execution and fusion of at most two wires in the
enabled fixture. This metadata does not prove the scientific row's kernel path.

For the final18-wire disabled-fusion fixture, fixture construction ends at
0.070221s; decoding ends at0.071258s and construction at0.071478s.
`run()` consumes almost the entire5.59s Aer interval; `result()` adds less than
one millisecond. Exact timestamps are saved. **Submission can itself block**:
these API-stage timings do not separate internal noise compilation from sampling.
No analogous timestamps exist for the earlier scientific timeout.

Final focused checks: **23 passed**,0.632350s boundary,108,134,400bytes wait4
high water. Checks include all complex amplitudes/global phase of a three-wire
fixture, explicit asymmetric local Kraus algebra, readout/operand order,
identity rejection, allocation bounds and durable stages after result failure.
Only local at-most-two-wire SuperOps are used; no full-system density matrix.
Existing Aer deprecation warnings remain. Selected Black/Ruff and diff checks
pass. This is not full-suite or scientific admission.

## Why MPS and shot branching are withheld

A two-wire synthetic state
$\cos(5\times10^{-9})|00\rangle+\sin(5\times10^{-9})|11\rangle$
was prepared with RY(1e-8) followed by CX. Dense statevector retained the
5e-9 amplitude with measured maximum residual0. MPS returned zero for it,
maximum residual5e-9, despite public truncation threshold0, unlimited bond
dimension, `zero_threshold=0` and `chop_threshold=0`. MPS metadata reported
bond dimension1. This is a finite installed-binary observation, not a claim about
the missing coloring row's error or an asymptotic theorem.

Aer0.17.2's tagged [SVD implementation](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/src/simulators/matrix_product_state/svd.cpp)
starts coefficient reduction using the separately defined positive cutoff in
its [SVD header](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/src/simulators/matrix_product_state/svd.hpp).
This source is consistent with the observation; it is not a wheel-build
attestation. Zeroing the public tolerance alone therefore does not establish
the required exactness. No MPS scientific candidate or private Aer build is
offered. Installed [Aer simulator documentation](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/qiskit_aer/backends/aer_simulator.py)
also flags shot branching as unstable on macOS. It was not enabled or benchmarked.

## Concrete later execution contract and blocking followup

The assigned independent reviewer must distinguish source/tool admission from
resource-plan admission. Review the whole inherited decoder and proposed caller,
including physical ordered channels/readout, full coherent prefix, layout,
measurement mapping and seed semantics. Fusion can change random-number usage;
identical seeds do not guarantee identical histograms across methods. It must
preserve the probability law, not silently substitute channels or tolerances.

Before any later scientific attempt, the coordinator needs an independently
admitted exact caller and positive resource justification. A future caller must:

1. Authenticate the saved request, compact/logical/routed QPY, all126 channels,
   physical calibration and prior evidence. Use fresh outputs; no resynthesis,
   rerouting, new noise, shortened protocol or overwritten timeout artifacts.
2. Retain all admitted complete coherent-state, norm, marginal and workspace
   checks at1e-10 before sampling. Cached values alone are not a new execution
   gate. Any validation reuse needs its own exact caller/identity proof.
3. Persist monotonic stages before/after QPY load, validation, noise decode,
   simulator construction, `run()` and `result()`, together with source hashes.
   A timeout must preserve the last durable stage without inventing internal
   stack attribution or partial counts.
4. Use the fixed dense options,64shots, seed37/74730 and serial execution under
   the original120s boundary. Own/reap one child; stop on unavailable RSS or
   sampled2GiB excess. Sampled RSS/Aer memory settings are not hard OS caps.
5. Admit completion only after successful result and exactly64 returned counts,
   with per-circuit Wilson95% intervals and existing distinct cost units.
   Require separate independent exact evidence review after any authorized run.

**Present resource decision: BLOCK step4.** The low-noise synthetic fixture
does not justify spending another scientific120s window. An actionable resource
successor would first develop/review an exact ordered local-channel trajectory
optimization, or benchmark synthetic channel-density/entanglement fixtures
without loading the scientific circuit. It must address520,128 channel locations,
preserve seed/64-shot/caller gates and provide evidence under the existing bounds.
Only a separate positive review could change the no-retry decision. The queued
resource reviewer/integration owner decides this; no new model job is launched
or queue definition changed by this worker. Other family/C5/proof owners remain.

## Preservation and bounded resources

Budget was declared before arrays:120s/child,300s cumulative,2GiB/process,
vectors<=18, local channels<=2, dense Operators<=5, original staticFT dense4
unchanged. Serial supervised children use sampled direct-child RSS monitoring
and kill/reap on deadline/observed excess; terminal wait4 may include reaped
descendants and is not simultaneous group RSS or a hard allocation cap.
Numerical check/probe boundaries total25.987481s. All pre-report supervised
children total32.102924s including scalar audit/Git/style children; final exact
totals/commands/exits and scope are in checkpoint receipts.

Only existing absolute root research Python was used, with explicit candidate
PYTHONPATH and final import/hash assertions. The prescribed unchanged native
SHA2566aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a
was verified and selected but not invoked. Initial inspection commands have
tool exit records without separately measured RSS; sandbox `ps` denial led to
scoped supervised checks with visibility. Absent guessed documentation paths
and truncated reads were corrected. No automatic approval-review rejection.
All earlier receipts, source snapshots and synthetic repetitions remain.
README, pins, binaries, queue/state/history, archives, original28 observations,
later family evidence and both selected timeouts are untouched. No push,
model/subagent/Codex subprocess, paid/API fallback, sync, purchase or hardware.

Binding prior evidence: [selected timeout review](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_selected_retry_independent_review_20261101.md),
[current family admission](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/noisy_family_integration_20261109.md),
and [component source admission](https://github.com/TheBarzani/logique/blob/coloring-paper-revamp-codex/docs/research/component_lowering_integration_20261103.md).
