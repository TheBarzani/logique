# Independent two-register dynamic RUS instrument review

**Assigned review COMPLETE. Exact bounded source ADMIT; exact saved evidence
ADMIT under the separate restrictions below.** Successful completion implements
the requested reflection, including on entangled inputs. The finite-cap
unconditional channel is different. Deterministic/static substitution,
quantum-controlled RUS, performance advantage and the full manuscript remain
**BLOCKED / outside admission**. No candidate correction is required.

Task `dynamic-rus-graph-review-1101052342`, 9 November 2026, America/Montreal.
Review branch `codex/coloring-dynamic-rus-graph-review-1101052342`, assigned base
`de230cce74089344343fcdf1c12d553cc4cf8607`. Attempt 1 was interrupted during
read-only inspection; it produced no numerical run or file changes. Attempt 2
continues that review. No model, subagent, subprocess Codex, API, paid fallback,
purchase, hardware job, queue mutation or push was used. The current queue has
`deadline: null`; earlier calendar dates confer neither a stop nor admission.

## Exact decisions

Read-only candidate branch `codex/coloring-dynamic-rus-graph-1101052342`, clean
HEAD **`b9f82978ed964ef9270c34545e4b0dcc9f47ca4f`**. Its entire difference from
the assigned base consists of the following two correctness files and the
separate report `DYNAMIC_GRAPH_RUS_CHECKPOINT.md`. There is no hidden inherited
candidate implementation diff.

| Decision | Exact scope |
| --- | --- |
| Source **ADMIT** | Commit **`48b820388712a247f91aab8e8459543bb036bd1d`**, only `src/logique/benchmarks/dynamic_graph_rus.py` and `tests/test_dynamic_graph_rus.py`. Fixed single edge, two distinct two-bit registers, k=3; prepare/mark/reflect/iterate cap0..4 and search cap0..2. Arbitrary data, up to three untouched reference wires and four purification/operator columns. All aborts and zero-norm records retained. |
| Inherited source | Exact integrated `78c98a164a289b52ce6251e5495848e71b4bb193` primitive source/tests are already in the assigned base. Candidate, reviewer and current-root bytes match. The generic tensor action was inspected afresh for the wider graph axes. This review extends its use only through the bounded graph interface; it does not change the original primitive API's caps. |
| Build/dependencies | No build, bridge, binary or dependency changes offered or admitted. The prescribed unchanged executable was explicitly selected and hash-verified, never invoked. NumPy/Qiskit remain lazy. |
| Saved evidence **ADMIT** | Exactly 23 cases / 1,183 terminal records, six graph QPYs and associated phase-sensitive maps, reference/purification outputs, channels and event counts in the 72-entry worker index. These are ideal deterministic numerical checks and unoptimized logical operation counts, not stochastic or hardware measurements. |
| Whole search | The actual **heralded single-edge preparation plus one iteration** is supported for cap0..2, with zero completion at cap0. No general graph, additional iteration, cap3/4 full-search execution, deterministic finite-cap Grover or performance claim follows. |

| Admitted or bound item | SHA256 |
| --- | --- |
| New graph source | `934022995306673975bded34f8aec94704200c29e95ab2fede142cb56c8063b0` |
| New graph tests | `6859f95e38cdeec4606e0fd7729444a217d898bd4bd02db66068e0c71cf75bb5` |
| Inherited primitive source | `4212abaaae4e3bb031ac28baa624c1d88c6ff574aa82701894688458529d44c9` |
| Inherited primitive tests | `5de0b20abb2fbeb2d655b93fe082536e5ab8e78618ce0386a4fb2933e7ee22e3` |
| Worker report at b9f8297 | `9de583f71368c5af3a9ad5114d6d48ae3d8e9f84074d180d4c485ca5ddffe299` |
| Worker evidence index | `7cfa0c1be0f86aacf608c6fd719a1f810a5eeb25517c34dfe777438c4491983d` |
| Worker summary | `672201a4f32bbc52daed185e2bf6e1fa95eed2748eaf8f015a6c93d4f25d0648` |
| Worker branch/event ledger | `43c3e1ea81486d4a2d3bdb5c76c06c44a9c02076ab9610a6e582b126b4f79cfa` |
| Worker inputs | `9cda440dee0a3a575784dd6ce48097c751a9711563cbd744e6a2282885e28587` |

Worker evidence root is sibling
`../dynamic-rus-graph/dump/1109163219-dynamic-graph-rus-execution/`.
All 72 new, 100 inherited worker and 36 prior independent-review inventory
entries match saved lengths and hashes. The inherited index hashes remain
`a8f7fc74fdf36cb42f261439bdd8d025723dbe0fe671743a929d116523a362cf` and
`647dbda2f5d66610c771ad4cf5f9dc4b25b3bc4981b9af3c12edd55203661c95`.
Working source equals the identified committed blobs. Queue completion and
earlier single-register admission were not used as substitutes for these checks.

## Independent derivation: completion versus the flagged instrument

Take the emitted H,T,CX,H,CX,T,H trial on ancilla a and high color bit h.
For t=(1+i)/sqrt(2), its zero-input-ancilla blocks evolve as
`[I;tX]/sqrt(2)`, then `[I+tX;X-tI]/2`. Final T,H and Z projection give

$$K_0=\frac{(1-t^2)I+2tX}{2\sqrt2}=\alpha U,\qquad
K_1=\frac{1+t^2}{2\sqrt2}I=\beta I,$$

where $U=(I+i\sqrt2 X)/\sqrt3$, $\alpha=(1-i)\sqrt{3/8}$ and
$\beta=(1+i)/\sqrt8$. Thus the two effects are 3I/4 and I/4 on every
input, including data entangled with a reference. Reset moves the selected
ancilla sector back to zero without normalization or a new phase.

Independently multiply $E=X_h\,CH_{h,l}\,S_h^\dagger$ with U on h to obtain
$V=E(U\otimes I)$. The saved two-T controlled-H extension and its actual
expanded inverse agree with this matrix, including scalar phases. V is
unitary and V|00>=(|00>+|01>+|10>)/sqrt(3).

First success at trial r has forward map $\alpha\beta^{r-1}V$ and inverse
map $\alpha\beta^{r-1}V^\dagger$. Inverse E-dagger occurs once, before all
ZUZ trials, including cap0. Exhaustion maps are $\beta^c I$ forward and
$\beta^c E^\dagger$ inverse. A fresh inverse branch scalar is not conjugated
from a sampled forward branch; at r=2 it happens to be real.

Data order is explicitly MSB `(v0.h,v0.l,v1.h,v1.l)`, with references trailing.
This fixed interface is not a generic replacement for the library encoder's
LSB ordering. Let $A=V\otimes V$, $S_0=2|0000\rangle\langle0000|-I$ and
$D=AS_0A^\dagger$. The time sequence inverse v1, inverse v0, S0, forward v0,
forward v1 yields, for each completed record,

$$L_{\mathbf r}=\alpha^4\beta^{\sum r_i-4}D.$$

No fitting of a global phase is allowed: for example the four first-attempt
successes have scalar $\alpha^4=-9/16$. At cap c, put $s=1-4^{-c}$.
The completed subchannel on any data/reference density operator is exactly

$$\mathcal C(\rho)=s^4(D\otimes I_R)\rho(D^\dagger\otimes I_R).$$

For c>0, normalization by its input-independent trace yields the requested
reflection, not a measurement of the graph register or a different filtered
channel. At c=0 this conditioned channel is undefined because completion has
zero probability. Mark then reflect gives $DM$; full preparation plus one
iteration gives $DMA$, with completion $s^6$ for the admitted full-search caps.

An abort at the next reached invocation is the actual prefix product, followed
by $\beta^c I$ or $\beta^c E^\dagger$ on its vertex. Any already reached M or S0
remains; every later operation is absent. Every branch is scalar times a
unitary prefix, so effects sum to identity and abort trace is $1-s^L$ for L
invocations. This proves completeness also on entangled inputs. The instrument
has classical orthogonal record/flag labels; the emitted circuit infers flags
from reached measurement slots, without measuring data. Unused classical slots
are not additional outcomes. Discarding these flags yields a mixture of prefix
unitaries, generally different from D. The saved cap4 reference-state fidelity
to D after discarding flags is 0.9854492967096983, corroborated independently
within 1.3e-14; this is an input-specific fidelity, not a worst-case guarantee.

## Actual primitive marking, signed reflection and costs

The complete marker has minus signs exactly on integer words 1,2,4,6,8,9:
six unequal pairs of valid colors 0,1,2. Equal colors and every pair containing
code3 retain plus signs. Each point phase computes two controls into zero
scratch with an exact seven-T CCX, applies CCZ via H/CCX/H, and uncomputes.
The expanded seven-T CCX is exactly self-inverse, so repeating this specific
expansion is valid. Scratch restoration and all relative phases were checked.
S0 uses the zero point phase plus time-ordered X,Z,X,Z=-I, fixing its absolute
sign. Missing that minus produces Frobenius map discrepancy 8, even though it
would not alter an uncontrolled output density matrix.

Per point: 21 T and 26 Clifford operations before bit masks. Six marker points
add 32 mask Xs: **126 T, 188 Clifford**. S0 adds eight mask Xs and four sign
gates: **21 T, 38 Clifford**. CX/CZ each count once. These counts concern this
unoptimized emitted construction, not optimal synthesis.

For a reached loop, expected attempts are $m=\sum_{r=0}^{c-1}4^{-r}=4s/3$.
Forward expected stop T is $F=2m+2s=14s/3$; inverse is $I=2m+2$.
The separate prefix charge explains cap0 reflection's nonzero cost. Summing
reach probabilities gives

$$R=I(1+s)+21s^2+F(s^2+s^3),$$

$$T_{\rm search}=F(1+s)+126s^2+I(s^2+s^3)+21s^4+F(s^4+s^5).$$

| Program/cap | Records | Completion | Saved observed unconditional stop T |
| --- | ---: | ---: | ---: |
| prepare/4 | 21 | 0.9922027587890625 | 9.278717041015584 |
| reflect/0 | 1 | 0 | 1.9999999999999967 |
| reflect/1 | 5 | 0.31640625 | 22.257812499999773 |
| reflect/2 | 31 | 0.7724761962890625 | 34.62588500976521 |
| reflect/4 | 341 | 0.9844663145486265 | 39.33693810412615 |
| iterate/4 | 341 | 0.9844663145486265 | 165.33693810412186 |
| search/2 | 127 | 0.6789341568946838 | 149.65165674685932 |

Independent exact-rational event sums give reflect/4 T=39.3369381041266 and
search/2 T=149.65165674686432. The table's observations use branch effects on
the maximally mixed graph input, denominator16. Exact scalar effects establish
input independence. These are unconditional costs including aborted prefixes,
not success-conditioned costs or costs per proper coloring. Reflect/4 has
5.281453053466976 expected reached measurements, resets and outcome dispatches,
1.3048295779153705 retries and 128.9463995944243 Clifford operations. Their
prices, runtime, latency and T-depth remain unknown; null does not mean free.

This edge has M/N=6/9. Preparation gives proper probability2/3; one completed
iteration overshoots to $\sin^2(3\arcsin\sqrt{2/3})=2/27$. At search cap2,
joint completion-and-proper probability is **0.05029141902923401**, rather than
2/27 unconditionally. Aborted output states are not counted as successful
searches. No improvement, break-even, noise robustness or scalability follows.

## Independent checks and adverse cases

Fresh run: `dump/1109211855-dynamic-graph-rus-independent-review/`, created with
`new_dump_directory` in local time. Unique reviewer probe:
`tools/dynamic_graph_rus_review_probe.py`. It imports exact candidate source
only for comparison, never candidate test helpers for reference semantics.

* Reconstructed all four inherited primitive QPY matrices by independent
  little-endian row-index gate action. Derived E directly from controlled H;
  no offered target matrix was used as the reference definition.
* Independently enumerated all23 schedules/caps and all1,183 success/abort
  prefixes; checked every saved16x16 map, effect and graph-density channel,
  pure-reference output, four-column mixed purification, record and event count.
  A fresh seed20261111 Schmidt-rank-eight reference with four purification
  columns checks candidate tensor action on every branch. Saved seed20261109
  evidence is reused, not regenerated.
* Interpreted all six actual saved graph QPYs: nested classical conditions,
  block-wire maps, both projections, reset and primitive gates. All16 input
  columns are checked in four-column blocks for522 terminal records (2,088
  block comparisons), including all341 reflect/cap4 records and127 search/cap2
  records. Every QPY trace agrees with saved events after excluding the abstract
  dispatch/retry labels; full traces include actual primitive gates and outcomes.
  Helpers return to zero. The loaded circuits also equal the offered builders.
* Six preflight rejections include full-search cap3/4 (1,093/5,461 records),
  insufficient branch budget, Boolean cap and unknown program. All341 zero-state
  reflect/cap4 records remain present. No excluded full-search cap was executed.

There are **11,667 numeric comparisons**, complex128, entrywise tolerance3e-13;
resource sums use relative3e-13 against max(1, exact magnitude). Largest saved
map residual9.881140848133644e-15; QPY map9.54933597147793e-15; fresh-reference
amplitude1.1172481126437302e-15; effect2.842170943040401e-14; channel
3.150257849963527e-15; fidelity3.141931159689193e-14. Largest normalized resource
residual3.3756713448514735e-14. These different quantities are not one certified
operator norm, statistical uncertainty or interval guarantee. There are zero
shots or sampling confidence intervals. Exact algebra supplies the semantic
argument; floating-point checks corroborate the actual bytes.

The saved naive controlled-trial QPY independently reproduces discarded-record
purity **0.8124999999999973=13/16** from a pure input: control sectors have
success probabilities1 and3/4, so the record leaks control information.
Quantum-control admission remains blocked. The independently reproduced wrong
inverse prefix/order and sampled-adjoint errors are respectively1.224744871391589,
2.3094010767585034 and2.449489742783178 in Frobenius norm. The r=2 scalar
alpha*beta=sqrt(3)/4 equality is preserved; it is not a counterexample.
A new cap0-abort-versus-requested-reflection check differs by5.537749241945385.

The candidate's saved first run had ten failing assertions/160 passes: cap0
tuple-versus-bool summation and resource absolute tolerance below accumulated
floating-point roundoff. Its four type errors and later fixes were inspected.
The recorded correction to relative resource tolerance does not relax matrix
or branch semantics. Original pre-fix source was not saved before those runs;
that preservation limitation remains, alongside intact original failure logs.
Neither these test issues nor the earlier r=2 mistaken expectation are two
failed mathematical construction attempts.

Fresh candidate graph/primitive suites pass **78 tests**, no skips/deselections.
No broad accounting/staticFT suite was replayed merely to increase test counts.
Black and Ruff pass for the review probe; formatting after execution changes
no AST (checked separately). The executed preformat snapshot is retained.

## Resources, preservation and next action

Before arrays:120s/child,300s cumulative,1GiB declared process memory, one
numerical child, dense<=4 wires, state<=9 wires, reference<=3, columns<=4,
cap<=4, records<=341. Actual graph tensors use<=8 wires and QPY replay6;
naive-control dense matrix uses3 wires. Original staticFT dense4 scope remains
unchanged. Numerical probe13.221049s and tests4.738905s total **17.959954s**.
Largest numerical direct-child wait4 high-water **386,973,696 bytes
(369.046875MiB)**. Process-group timeout and fixed bounds are safeguards;
terminal wait4 may include reaped descendants and is neither live/group peak
monitoring nor a hard memory cap. Serial compiler/BLAS/OMP/Accelerate/Rayon/
Qiskit settings and explicit candidate imports are saved in receipts.

The first reviewer audit failed before numerical imports on a historical
dictionary-form index instead of the newer entries-list schema. That failed
run `dump/1109211841-dynamic-graph-rus-independent-review/` and its original
probe/log/exit1 receipt remain. The parser was corrected; a new run verified
all208 entries. No scientific failure occurred. Initial inspection reads have
tool transcript commands/exits but no separately measured RSS; oversized reads
were followed by focused chunks. No failed/partial historical artifact changed.

Independent results SHA256:
`dac44e2169907ccf09d558b9087aea4a2ae3f3de8aa70968300626302d8414ea`.
Fresh inputs SHA256:
`db2f7ef2f7f447da82c10fec41abcc42be56d72a1d598fd7c2a6aec8054a825f`.
Executed probe SHA256:
`fadbeda431c9ed68324f940d1c1f4dd8983b858cebca1b41ef313ed51c3ee5c1`.
Formatted probe SHA256:
`9701e267ade07754b3f7ae5832f98a5993d169e30aae5eb6e26655409706868a`.
Final index/checkpoint binds receipts, inputs, probe, conclusions and commit
identities without a self-referential index. Task/session details stay local.

Read AGENTS.md, CLAUDE.md and the entire revision plan, current-root appendices
and full successor, the29/30October handoffs, architecture, the actual new and
inherited source/tests, report, scripts, failure receipts and prior analytical/
dynamic review/integration chain. C5 was not executed or reviewed; its separate
22-wire lowering/noise gates are untouched. README, pins, lockfile, candidate,
prior reviews, queue/history and archive bytes remain unchanged. Existing
absolute root venv only, no sync/install/build. Native SHA256 remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.

Next, the assigned `dynamic-rus-graph-integrate-1101052342` coordinator may
integrate **only the two exact admitted correctness paths**, preserve this
restrictive review and worker report separately, and check integrated bytes.
Any semantic merge resolution requires fresh exact independent review.
Further scientific work must choose a useful graph/iteration and price all
reached operations, including aborted attempts, before testing an advantage.
This bounded independent review ends here; broader research completion is not
inferred and no prerequisite polling is needed. Dispatcher alone publishes.
