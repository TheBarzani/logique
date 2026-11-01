# Selected noisy retry execution — 1 November 2026

Task `noisy-selected-retry-1101051610`, session
`01a198ac-7b25-71d0-ae36-bc6b0ab55a51`, branch
`codex/coloring-noisy-selected-retry-1101051610`, exact base
`794338514a3032a5f43b61251a56c107910767c0`.
**Bounded assignment COMPLETE; scientific sampling BLOCKED by timeout.**
Exactly one missing request was launched, once. No completed noisy observation
was added. Independent exact evidence review remains pending.

Worker-relative evidence root (`R`):
`dump/1101145422-noisy-selected-retry-execution/`.
Prepared request:
`R/prepared/1101145422-noisy-remaining-requests/retry-request.json`.
All fresh outputs are worker-owned and created through `new_dump_directory`.
Only this checkpoint is committed; no scientific source/build/metric changes.

## Exact admission and execution scope

Read AGENTS.md, CLAUDE.md, all779 lines of the revamp plan, 29 October scaling
and hard-bound handoffs, 30 October finalization/continuation and noisy-ledger
handoffs, current root noisy integration and its verbatim independent review,
current C5 structure22 report/checkpoint, C5 best-fit integration, actual selector,
preparer/tests, supervisor/reconciliation, routing and relevant evidence. Combined
truncated reads were followed by focused reads. Older histories remain intact.

The four files exactly match selector `1453b8434f20746d350f68dcf8d56fa5df703305`
integrated as base7943385, and review
`a922cea99b3142d4971f8aa65e47052200931bf3`'s committed blob matches current
root review SHA256 `4afe0d0e41b7f01063420f9ef361100f379a0a1f6802f5fd4bdb94eb3dc757fc`:

| Path | SHA256 |
| --- | --- |
| `src/logique/benchmarks/noisy_iterations.py` | `35b96be7e07f0beaadb4b6dad7b189c51643578f289f6485eae54139bcdb39bd` |
| `tools/run_noisy_remaining.py` | `f1942f0ecff26493c4ad7382291d912263aea3f5395fc077b58c0402970213bf` |
| `tests/test_noisy_remaining.py` | `ad79606b0e207c2d246dcee1b9869518eb535da84439f12bd75d6b7de18b3d05` |
| `configs/noisy_remaining_retry.json` | `9f850c369545718f450f96a9f4fe8ec17f986eeb5037f3d6ab36176f0380ccf4` |

No dependency was replaced. Retained reviewed inherited noisy correctness9a766b1
and routing metric0a0e605; routing hash
`65c502f94955779db4976fa671d86a26387be31b74a48ade8963ddbe4a0a1ca4`.
Newer inherited resolver4e44215 (wide-QPY exact review), native5ec2127 (bounded
SAT review475eff6), iterationed78114 (structure22 still pending), C5 standalone
2fff3ea (best-fit review4fbf3d0) remain unchanged. Their presence does not extend
scientific admissions. `dependency-identities.json` records exact hashes/commits;
`intake.json` binds all candidate Python source hashes and asserted actual import.
Native was never invoked; there was no new source-to-binary attestation.

The admitted preparer's `prepare` function was loaded directly from
`tools/run_noisy_remaining.py`, with exact retry config and frozen noisy root
from the integration audit. It made the full805-minus28 ledger and one request,
without launching. Both original manifests and all211 ideal/163 noisy inventory
entries verified before preparation and again after execution. Original manifests
are copied unchanged into R; original paths/hashes are in intake.audit.
Ideal manifest SHA256:
`0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811`;
noisy manifest SHA256:
`f90015531f0513d275f187fb62fcd2b96bfcff7610fa2fe56f8cde0b81026278`.

Only prepared `--child` **K3_k3_R2, transpiler seed37, iterations[2],64shots**
ran under unchanged `noisy_iterations.supervise`, with120-second limit. Request
SHA256 `99819a66a61f6b793fbd90e5ced4f4be58d192357a902ab5f9cb51a2c193d5cb`.
The full-study `--config` path was never invoked. Both preceding coherent steps
were built; neither j0 nor j1 was routed/sampled or given an output directory.

## Observations and terminal ownership

| Quantity | Fresh saved value |
| --- | ---: |
| Child boundary wall time | 120.006279041 s |
| Exit / reason | -9 / timeout |
| Sampled direct-child peak RSS | 463,667,200 bytes (442.188 MiB) |
| wait4 invocation high-water RSS | 486,834,176 bytes (464.281 MiB) |
| Logical width / active physical width | 14 /18 wires |
| Preallocation estimate | 167,772,160 bytes (160 MiB) |
| Native two-qubit count / depth | 2,590 /1,885 |
| Scheduled ALAP duration | 224.284 microseconds |
| Routed coherent residual up to global phase | 6.916174040839297e-15 |
| Maximum data-marginal residual | 3.164135620181696e-15 |
| Restored workspace probability | 1.0 |
| State norm squared | 1.0000000000000342 |
| Noiseless success / unused-code leakage | 0.4024115565039334 /2.4670660072214868e-29 |
| Requested / returned noisy shots | 64 / unavailable |

The child reached durable `validated_pre_sampling`, seed74730, before timing
out inside sampling. **No counts, noisy-success estimate, noisy Wilson interval
or quantum cost/p exists.** Partial Aer shots, if any, are unavailable, not zero.
Noiseless success agrees with saved ideal0.4024115565039176 and analytical
0.4024115565039206; it is not a noisy observation. ESP2.010032900520201e-7 is a
calibration-product diagnostic only. Fresh classical reference:1104/2048 batches
succeed with3 draws per batch (6144 draws), seed74730; zero unused-code draws.
Different quantum-gate and classical-evaluation units cannot establish speedup.

Supervisor receipt records available RSS sampling, reaped child77470, no cleanup
errors. Post-reap PID absence was checked. Original receipt stays unchanged;
`execution.json` names this actual task/session. Raw pre-reconciliation result is
retained separately. `finalize_result` reconciles its sole running row to timeout,
keeps all pre-Aer evidence and records no completed iteration. No retry loop ran.

## Post-run checks and preserved failed comparisons

`final-validation.json` records exact routed→compact QPY signature equality,
physical initial/final layout, LSB measurement order[4,5,1,3,6,10], 126 compact
channel entries with ordered qargs and local widths<=2, preallocation and coherent/
norm/restoration checks. There was no post-run statevector or sampler replay.
Calibration properties/configuration bytes match the frozen original exactly.
Their SHA256s are respectively
`116c5692ad5669219571ce4c13132fdd68394aa543537b5ccf14a6bd2df10b11` and
`5ee2380a9ac055523b80cde987725216a1b63c1089b6e208bc08db5d2be626f8`.

Two overly strict comparisons failed and are retained: raw noise JSON equality,
then equality after removing only generated error IDs. Outer error-record order
also differs (`sx` versus `x` records). Matching all965 records by error type,
operation and **ordered** physical qargs yields exact payload equality after
omitting only generated IDs. Internal instruction/branch/probability/matrix and
readout order/values are unchanged. Canonical SHA256:
`372fc85d49a2c65fe5f962d7ce0072ba8193e380b206a99a14fbfc320c96193a`.
Actual fresh snapshots and all differences remain saved; no old bytes were edited.
Independent review must assess this explicit comparison scope.

Final metadata/QPY audit passed in0.874022 internal seconds (1.043082 tool boundary),
Darwin self high-water213,565,440 bytes. Initial failed post-audit wall0.975442s
and ID-only failure0.433252s have no measured RSS. Numerical child time is
120.006279s total, not multiplied by parent checks. Initial source/input/preparation
used0.391844s tool boundary; inspection commands lack separate RSS measurement.
No new regression suite was necessary for this execution-only checkpoint; the
admitted base's prior tests are attributed history, not newly rerun results.

## Resources, preservation and next scientific owner

Before arrays: <=120s child,<=900s cumulative,<=6GiB process budget,statevectors
<=18,dense Operators<=5,local channels<=2,no full density. Original staticFT
dense4 unchanged. Existing absolute root venv Python only, candidate PYTHONPATH,
no sync. Compiler/BLAS/OMP/Accelerate/NumExpr/Rayon threads1; Qiskit parallelism
off/processes1; one numerical child. Sampled direct-child RSS is not a hard cap
or group RSS; wait4 high-water may include reaped descendants.

Sandbox `ps` denial was detected before launch; scoped escalation supplied host
RSS visibility. No scientific child was launched without it. One guessed wide-QPY
integration document was absent (inspection exit1); actual representation/native
admission documents were read. No auto-review rejection occurred. Explicit Git
staging/ref writes and required briefing delivery may require scoped escalation.

The prescribed unchanged native binary SHA256 remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
build declaration remains
`5f07fd225e7f2eb74ca3925e808a32b312670cd328d583549e460889e7106b91`.
README,lockfile,submodule declarations/external tree and all source identities
were rechecked. Root README stays
`73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`.
No pins,binaries,old outputs,failures,archives,histories or queue/state changed.
No subagent/model/Codex subprocess,API/paid fallback,purchase,hardware,excluded
research or push occurred. Dispatcher alone launches models and publishes root.

The denominator remains **805-28=777 without completed observations**, including
this missing request, seed23/j2 exclusion at21 wires,50 original C5 structure-width
exclusions and725 other unrun requests. Original28/1792 shots remain the only
conditionally admitted noisy observations. Poor K3 j1 results and all original
failure metadata are preserved. C5 best-fit ideal admission licenses no noisy
adapter; structure22 absolute-phase/scratch proof remains pending.

**Next:** existing `noisy-selected-evidence-review-1101051610` reviews this exact
receipt, pre-Aer artifacts, hashes and absence of counts without scientific replay.
Then `noisy-final-coordinator-1101051610` integrates only exact admissions and
owns a separately justified resource/algorithm plan if missing K3 sampling is to
be attempted again. This worker does not raise limits, optimize unreviewed source
or replay the request. Full-family/five-seed/noise resilience/speedup and manuscript
claims remain BLOCKED. Required narrative and result/manifest are in R; completion
receipt records this checkpoint commit separately to avoid self-hashing cycles.
