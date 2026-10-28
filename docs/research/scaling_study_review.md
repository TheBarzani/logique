# Independent Task 8 compiler-study review

**Decision: BLOCK the candidate process/resource contract pending the two
corrections below. This assigned review batch is COMPLETE.** Passing tests and
reproduced pilot predicates do not confer scientific approval. No source,
research metric, archived output, dependency pin or integration branch was changed.

Reviewed on 28 October 2026 in `codex/coloring-scaling-review-1028004102`.
Task: `scaling-review-1028004102`; session ID not supplied. Candidate:
`../scaling-harness`, HEAD `f095a5c` (implementation commits `5da2e1e`,
`fd62200`, `36e730e`; checkpoint `f095a5c`). The independent reviewer read
AGENTS.md, CLAUDE.md and the complete revamp plan, the resumption audit/intake,
the candidate checkpoint, source/tests/results, and relevant implementation and
claim-evidence audit entries. Renewed full-plan authorization and all scientific
exclusions remain in force. No models/subagents, builds, sync, hardware, push,
root integration or queue changes were made.

## 1. Blocking counterexamples and required corrections

**B1 — An over-deadline child can be accepted as successful.** In
`src/logique/synthesis/process.py:81–87`, a completed `wait4` result exits the
loop before checking the elapsed deadline. The unconditional 100 ms sleep at
line 115 permits a child to finish after its budget and before the next poll.
Three actual calls with `timeout=0.02` and a child sleeping 0.05 seconds returned
success (`status="exited"`, return code 0). Child-measured elapsed times were
0.0600078753, 0.0600175420 and 0.0600329172 seconds; reported boundary times were
0.1145780827, 0.1046572500 and 0.1064597499 seconds. This is incorrect
classification, beyond ordinary uncertainty in kill latency. The same boundary
is used when only a small cumulative study budget remains.

Minimal reproduction using the candidate source:

```python
import sys
from logique.synthesis.process import run_bounded
run_bounded([sys.executable, "-c", "import time; time.sleep(0.05)"],
            "", timeout=0.02)  # Currently succeeds; must report timeout.
```

Correction: use a monotonic deadline, cap waits and resource-probe delays by the
remaining budget, and ensure that completion observed after the defined deadline
cannot silently become an eligible success. State whether the deadline measures
process execution or the enclosing boundary, and record observation uncertainty
if needed. Retain owned-group cleanup on all exits. Add regressions for this
race, a remaining-budget deadline and an ordinary successful child. A watchdog
may have scheduling latency; it must not turn that latency into successful
out-of-budget compiler evidence.

**B2 — The recorded RSS scope is false for a child that reaps descendants.**
Darwin byte conversion is correct, but `rss_scope="wait4 direct child; ..."`
(line 141), the docstring, guide and checkpoint overstate isolation of the peak.
In an actual bounded probe, the immediate child reported its own
`RUSAGE_SELF.ru_maxrss` as **16,072,704 bytes**, its waited descendant reported
**81,231,872 bytes**, and the caller's `wait4` result was **81,362,944 bytes**.
The descendant only allocated a 64 MiB bytearray. The result plainly does not
measure only the immediate child's peak. A second regression independently
reproduced 81,313,792 versus 15,974,400 bytes.

Correction: accurately label the OS wait4 accounting scope, including observed
reaped-descendant contribution, or collect a genuinely isolated direct-process
peak. Do not call it simultaneous aggregate group RSS either. Keep unavailable
`ps` sampling null and distinct. Retain the per-invocation versus earlier
unrelated children distinction, and add a parent/reaped-descendant regression.
Update documentation and future manifests without overwriting this pilot.
The tiny native pilot's byte values are preserved; no descendant behavior or
whole-harness RSS can be inferred from those numbers alone.

Review-only regressions in `test_review_contract.py` fail **2/2** against these
exact candidate bytes. Their log preserves the failures. The fixes belong in a
separate task-owned correctness commit and need independent re-review; this
review does not modify the candidate.

## 2. Independently corroborated evidence and limits

- The candidate focused suite passed **105 tests in 15.87 s** (16.090260 s
  measured job wall; Darwin wait4 peak 84,459,520 bytes). It includes the actual
  five-repeat native test, existing contract regressions, output/timeout limits,
  default request compatibility, deterministic families, explicit witnesses,
  budget/missing/unsupported rows and the huge-DIMACS preallocation guard.
  These tests do not cover B1/B2.
- Separate reviewer probes passed: same-group descendant termination after
  successful parent exit, interruption cleanup with KeyboardInterrupt propagated,
  survival of an unrelated process group, and terminal memory-limit detection
  when `ps` sampling is denied. The candidate timeout test separately checks
  same-group descendants of a timed-out parent. These checks establish the tested
  owned POSIX process-group behavior, not termination of deliberately detached
  sessions or a hard RAM reservation.
- All **331** pilot artifacts and the explicit source/test/config/input/evidence
  protection entries matched their saved SHA256 values. No unrelated artifact
  tree was recursively hashed. The admitted native executable's required SHA256
  matched. The pilot used Python 3.10.22 and the recorded locked environment;
  source resolution in the reviewer is explicitly the candidate, not this
  review worktree or the installed package.
- The pilot has **110 real attempts**: 11 inputs × 2 profiles × 5 repetitions,
  all labelled `ok`. Each of the 22 groups has repetition indices 0–4, seeds
  11/23/37/53/71 and five separate responses. All 110 bridge timer values differ;
  the candidate calls the native boundary on every repetition. The independent
  small integration test also executed five real calls. Within a group, graph
  and Verilog hashes match across repetitions.
- Independent scalar evaluation reproduced **8,660 graph-assignment checks**
  and **25,980 network-assignment checks** across source, preprocessed and mapped
  networks. The reviewer implemented graph decoding/predicates and scalar truth
  evaluation separately from the candidate encoder, graph checker and NumPy
  evaluator. There are 90 exhaustive rows and 20 sampled n=8,k=3 rows; 100 rows
  exercise positive branches and ten K3/k2 rows independently exhaust the domain
  with zero positives. Larger solution counts remain unknown. Recorded edge and
  unused-code violations reject, and satisfying witnesses accept.
- Family edges were regenerated from seed 1729 and the declared n/density/k
  settings. These are planted multipartite families with actual densities saved,
  not uniformly random graphs or chromatic-number claims. Method identity is
  `xag_bennett` tied to the exact native binary, with native preprocessing `none`
  for both profiles; `balanced` changes encoder association. Repetition seeds
  affect validation only. There is no native random seed or transpiler experiment.
- Config/file/resolved-config hashes, source identities, DIMACS hashes, generated
  graph/Verilog/response hashes, environment versions and declared build records
  are present. Checkout submodule entries have `-` prefixes: these record pinned
  revisions with uninitialized candidate submodules, not fresh builds or verified
  currently populated dependencies. The binary hash identifies the actual tool.

The independent replay and process-probe job took **2.809848 s**, with wait4 peak
**47,742,976 bytes**; the explicit descendant probe used at most a 64 MiB test
allocation and measured the values above. These are OS wait4 job measurements,
subject to B2, not guaranteed direct-only parent peaks. No statevector, dense
Operator, large study or new native build was used. Jobs ran serially with BLAS/
OpenMP limits 1, existing research Python and candidate PYTHONPATH.

## 3. Timing, quantum semantics and remaining study scope

The pilot's **12.4020618736 seconds** is accumulated boundary elapsed time,
including process setup, polling/probing and delayed exit observation. Saved
bridge responses also contain a combined `native_seconds` timer summing to
**0.9708516220 seconds**. These are different scopes, neither a decomposition
into disjoint optimization/mapping/lowering stages. The 100 ms polling interval
dominates these tiny boundary measurements. Preserve these old values; do not
use them as precise native execution runtimes or as evidence of compiler speed
improvements. For future studies, expose the existing combined bridge timer
with its scope and distinguish boundary overhead/observation granularity.

Encoding time covers encoding and writing Verilog. Optimization, mapping and
quantum lowering times are correctly null with explicit overlap/unavailability
text. The bridge timer starts after request JSON parsing, covers reading the
source and synthesis/network JSON construction, and ends before final JSON
serialization to stdout (`main.cpp`). It is not a new disjoint stage timer.
The pilot max wait4 RSS is **4,161,536 bytes**, correctly converted from Darwin
bytes; observed group RSS is null with `ps` permission errors in every row.
The `/usr/bin/time -l` wrapper exited 1 after `kern.clockrate` denial; whole-job
RSS is unavailable there. The harness wrote its finished ledger. Neither a
zero wrapper exit nor a whole-harness memory measurement is asserted.

**Boolean marking-branch coverage and quantum marking/cleanup are separate.**
The pilot verifies exported Boolean networks. It does not execute native quantum
gate records, build a phase oracle, or prove raw/arbitrary-target action, phases,
compute–phase–uncompute cleanup, entangled workspace restoration or Grover
behavior. Even exhaustive Boolean coverage cannot establish those quantum
properties. No phase/restoration, ideal-amplitude, full-search, FT, RUS or
low-T/alias admission follows. Network AND count is a statistic of the emitted
network, not a proof of the function's minimum multiplicative complexity; peak
live quantum workspace is also not measured here.

The complete selected-input ledger was checked against actual files:

| Selected input | Saved status |
| --- | --- |
| queen family | unsupported: family unspecified |
| myciel6, myciel7, DSJC125.1, le450_5a | missing input |
| queen8_8 | present, not run in pilot |
| 5-FullIns_3, 4-Insertions_3 | unsupported raw precolored inputs |

No large-input repetition claim is made. Restoring missing sources, defining
explicit eligible inputs/colors/witnesses, broader family/method/profile choices,
at least five large-case repetitions and a frozen full protocol remain open.
This review neither reduces that scope nor authorizes precolored work.
The implementation's previously reported **145 mapping-suite failures** against
this older admitted preprocessing-contract binary remain preserved. Its
compatibility evidence shows the same explicit-strategy rejection from baseline
and candidate; the focused green suite is not a green full-suite claim.

## 4. Exact reviewed identities and replay

Candidate root:
`/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/scaling-harness`.
Pilot: `dump/1028011425-synthesis-scaling/run.json` under that root.
Source/test/config identities below bind this BLOCK decision, not an admission.

| Candidate file | SHA256 |
| --- | --- |
| `src/logique/benchmarks/scaling.py` | `43070e357be798003868db28585e648b8ba6158703eabe2f4b11cc8fe8454d1d` |
| `src/logique/synthesis/native.py` | `24e9c4ebb6f7604956b9328490257bbdeac635374dd3c2f58cf5cb3cc63647c5` |
| `src/logique/synthesis/process.py` | `dabcf653d375986848359f94b471974761d6853bedf0851fbc295184ba8d00b1` |
| `src/logique/coloring/encoding.py` | `000bb92b33757dbb576199f44c82003da4e12c40185ad2d99813b54427f6b837` |
| `src/logique/coloring/dimacs.py` | `9b10db884cc75828443a77f03fa22ad2ebe664990ce0474e1ef644f71bd5b2b1` |
| `src/logique/coloring/model.py` | `b99c29bf82e6767974d411dd2dd3b9d8bd7a71816253de9d707d9d3e682248fb` |
| `src/logique/verification/classical.py` | `4d7d0e4747e2e1203a35ed6069635422768a172e94dfe00518f7f40a2853928c` |
| `src/logique/benchmarks/runner.py` | `6f08f2934833452e89d6a23c9c1debfd4ee158644e2cb4f427324cfbd0548dc4` |
| `src/logique/benchmarks/provenance.py` | `1ee14c4da081385ae6a6569e01021e103c6555e8592e4bcbde09e4eb3599c8d3` |
| `tests/test_native_process.py` | `b12143e4692d60a305c04c6bd5cc5db46b74b44f88c9d5edb98530418bce625f` |
| `tests/test_scaling.py` | `3e5dd58876ac87595c37809fda485ab870bc89177110a598f37d1975e2f9ad0b` |
| `tests/test_native_contract.py` | `3b3addc84897833768be6732f9946a63f231335d5c41b856d6498faf2adb093c` |
| `tests/test_native_mapping_strategies.py` | `be86f804f92eb573d21d9009677853248fd9ef127a6a404d7a828ffb84205c25` |
| `configs/coloring_scaling_pilot.json` | `9de032188f76097f436763d4c5a2f442470ac0aeac303f81ca7689f580057b92` |
| `docs/scaling-harness.md` | `d25efd28fd2716c9a8fad6b1ad97f812fce1969692e705e1fc335b6446f702bb` |
| `SCALING_CHECKPOINT.md` | `89f0d5c22bcbab5ab3fdd0c27fa81ab9c494707f6cd459bbcb87790b475ede62` |
| `dump/1028011425-synthesis-scaling/run.json` | `9863302f936ea41c43fc102e89d7b1322242e4fc48bc003d77185a773cff7f12` |
| `dump/1028011425-scaling-evidence/protection.json` | `5335ffe3acf864c9a8d732414d20fb642e0877f24f3ca960c6b654e04056cd31` |
| `external/native/boolean_synthesis/main.cpp` | `dcab4d7f3e6530a0071dde894776e1ae2ca4ae351807dfe27b7750ebbc375635` |

Native executable SHA256: `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.

Review artifacts are retained in this review worktree at
`dump/1028011928-scaling-independent-review/`. `review-protection.json` binds the
review scripts, logs and results individually. Its SHA256 is
`82efd962104b03802aa65d2d0f3848513e1b957bba188e6281a4a9650e1756c4`.
The candidate protection manifest above transitively identifies the executed
DIMACS and original evidence; the pilot manifest identifies all 331 generated
artifacts. Every referenced hash was checked, not merely copied into this review.

Reproduction commands from the review worktree (existing interpreter only):

```bash
export PYTHONPATH=/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/scaling-harness/src
export LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
/Users/mar/codex-work/logique/.venv/bin/python dump/1028011928-scaling-independent-review/run_checks.py
/Users/mar/codex-work/logique/.venv/bin/python dump/1028011928-scaling-independent-review/independent_checks.py
/Users/mar/codex-work/logique/.venv/bin/python -m pytest -p no:cacheprovider dump/1028011928-scaling-independent-review/test_review_contract.py -q
```

These record the original commands; any repeat must save into a new run folder
and adjust the scripts' output locations to preserve these logs. The first
script sets the admitted binary and explicitly runs the candidate's three test
files. `independent-execution.json` records the 60-second review-job timeout,
actual wall/RSS and candidate PYTHONPATH. `rss-scope.json` contains the full
standalone parent/descendant reproduction command. The blocker pytest log
records two actual failures; its shell invocation ended with `cat`, so shell
exit 0 is not a passing-test claim.

## 5. Bounded handoff

This review is complete with an actionable BLOCK decision. The dispatcher/
coordinator should route B1/B2 to a bounded process-contract correction, preserve
these exact old results, then obtain an independent review of the changed hashes.
Future timing tables must distinguish boundary observation from the existing
combined bridge timer. Do not integrate this candidate as admitted based on
105 passing tests, completed worker status or Boolean-only replay.

No further attempt is needed for this completed review batch. Full paper work
remains unfinished. The checkpoint in the review run records the review commit,
commands/results, protected identities and next action; only SCALING_REVIEW.md
is committed by this worker. The dispatcher alone handles later integration and
publication.
