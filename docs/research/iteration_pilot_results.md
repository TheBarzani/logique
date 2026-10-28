# Executed ideal iteration pilot — worker evidence

**Scientific review pending.** This is a bounded ideal-only implementation/pilot, not paper approval.

Implementation: `ca4315b15583823c44e5a2b9d6059212511853f0`. Final run: `/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/executed-iterations/dump/1028005202-executed-ideal-iterations`.
Validation: `/Users/mar/codex-work/logique/dump/1028004102-coloring-full-scope-resumption/worktrees/executed-iterations/dump/1028005123-iteration-validation`.

The final committed harness completed 34/36 graph/regime cases and retained two explicit C5 k3 R1/R2 width exclusions (22 > 18), with 151 simulated rows and no failed comparisons, timeouts or budget exclusions.

Pilot wall time: 29.322164 s; maximum child time: 2.355274 s; measured maximum child RSS: 147324928 bytes. Per-child cap 180 s, cumulative declared cap 900 s. These are measured per-process values, not an aggregate OS memory guarantee.

Tolerance: 1e-10. Maximum absolute probability error: 4.4408920985006262e-14; maximum signed full-vector residual without phase alignment: 6.512331117749953e-14; maximum norm error: 4.4853010194856324e-14; maximum restoration error: 4.4853010194856324e-14; maximum R2/R3 unused-code leakage: 1.1214291536936009e-29.

| Case | Regime | M | N | Width | Peak j | Simulated rows | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| path3_k2 | R1 | 2 | 8 | 6 | 1 | 3 | complete |
| path3_k2 | R2 | 2 | 8 | 6 | 1 | 3 | complete |
| path3_k2 | R3 | 2 | 8 | 6 | 1 | 3 | complete |
| path4_k2 | R1 | 2 | 16 | 8 | 2 | 4 | complete |
| path4_k2 | R2 | 2 | 16 | 8 | 2 | 4 | complete |
| path4_k2 | R3 | 2 | 16 | 8 | 2 | 4 | complete |
| path5_k2 | R1 | 2 | 32 | 10 | 3 | 5 | complete |
| path5_k2 | R2 | 2 | 32 | 10 | 3 | 5 | complete |
| path5_k2 | R3 | 2 | 32 | 10 | 3 | 5 | complete |
| path6_k2 | R1 | 2 | 64 | 12 | 4 | 6 | complete |
| path6_k2 | R2 | 2 | 64 | 12 | 4 | 6 | complete |
| path6_k2 | R3 | 2 | 64 | 12 | 4 | 6 | complete |
| path7_k2 | R1 | 2 | 128 | 14 | 6 | 8 | complete |
| path7_k2 | R2 | 2 | 128 | 14 | 6 | 8 | complete |
| path7_k2 | R3 | 2 | 128 | 14 | 6 | 8 | complete |
| path8_k2 | R1 | 2 | 256 | 16 | 8 | 10 | complete |
| path8_k2 | R2 | 2 | 256 | 16 | 8 | 10 | complete |
| path8_k2 | R3 | 2 | 256 | 16 | 8 | 10 | complete |
| K3_k3 | R1 | 6 | 64 | 14 | 2 | 4 | complete |
| K3_k3 | R2 | 6 | 27 | 14 | 1 | 3 | complete |
| K3_k3 | R3 | 6 | 27 | 11 | 1 | 3 | complete |
| C5_k3 | R1 | 30 | 1024 | 22 | 4 | 0 | infeasible |
| C5_k3 | R2 | 30 | 243 | 22 | 2 | 0 | infeasible |
| C5_k3 | R3 | 30 | 243 | 17 | 2 | 4 | complete |
| P4_k3 | R1 | 24 | 256 | 17 | 2 | 4 | complete |
| P4_k3 | R2 | 24 | 81 | 17 | 1 | 3 | complete |
| P4_k3 | R3 | 24 | 81 | 13 | 1 | 3 | complete |
| unsat_K3_k2 | R1 | 0 | 8 | 7 | 0 | 2 | complete |
| unsat_K3_k2 | R2 | 0 | 8 | 7 | 0 | 2 | complete |
| unsat_K3_k2 | R3 | 0 | 8 | 7 | 0 | 2 | complete |
| empty_k3 | R1 | 1 | 1 | 1 | 0 | 2 | complete |
| empty_k3 | R2 | 1 | 1 | 1 | 0 | 2 | complete |
| empty_k3 | R3 | 1 | 1 | 1 | 0 | 2 | complete |
| noncontiguous_edge_isolate_k3 | R1 | 18 | 64 | 12 | 1 | 3 | complete |
| noncontiguous_edge_isolate_k3 | R2 | 18 | 27 | 12 | 0 | 2 | complete |
| noncontiguous_edge_isolate_k3 | R3 | 18 | 27 | 9 | 0 | 2 | complete |

M and N come from exhaustive independent integer counting, cross-checked by packed-word decoding. Every executed row starts from saved/read-back QPY preparation/oracle/diffusion components. All flags, comparator scratch and output start zero; full non-data restoration is measured. R2/R3 retain valid-code support. Scalar phases are compared without fitted alignment. See the replay guide and per-case artifacts, signatures, witnesses and results.

Reproduction checks (computed from the circuits, not inserted as evidence):
- `K3_k3_R2`, j=1: simulated solution probability 0.99039780521261633; independent rational prediction 0.99039780521262; unused-code leakage 4.795928757244131e-31.
- `K3_k3_R3`, j=1: simulated solution probability 0.99039780521261778; independent rational prediction 0.99039780521262; unused-code leakage 5.5926609890049419e-31.
- `path8_k2_R1`, j=1: simulated solution probability 0.068855285644530861; independent rational prediction 0.06885528564453125; unused-code leakage 0.

The separately labeled random reference uses j+1 independent uniform draws and classical predicate evaluations. It is analytical and does not equate a trial to a quantum iteration. Exact statevector probabilities have no shot confidence interval. No noise or routing result is claimed.

Validation: 379 tests passed (21 harness regressions plus admitted ideal/structure suites), no skips/deselections; relevant Black and Ruff passed; staged diff check passed. The supervised validation command/RSS records are in commands.json. The final pilot records Python/NumPy/Qiskit versions, fixed transpiler seed, candidate source path, source/input hashes, Git revision and dependency gitlinks. The admitted native executable hash was checked and recorded; no native invocation/build was required.

The first pilot at `dump/1028004848-executed-ideal-iterations/` is preserved. It has the same 34 completed / two infeasible cases and 151 rows, but predates the added revision/platform provenance fields. Its output is not overwritten or relabeled as the final committed run.

Earlier development failures are retained in the checkpoint: zero-wire Hadamard broadcasting rejected an empty R1 fixture; it was corrected locally without changing the existing reflection contract. A supervisor mock intercepted platform metadata subprocesses; its test setup was isolated and corrected. Initial Git staging failed on shared worktree index.lock and then succeeded under scoped automatic escalation. No approval rejection occurred.

Next: independent exact-hash quantum review and dispatcher-owned integration. For C5 R1/R2, evaluate a separately admitted lower-workspace complete-predicate oracle within the cap, or obtain a larger explicitly authorized budget; retain all requested sweeps. Noise/routing and the rest of the full Task7/full-paper scope remain open. Existing rotation/ideal/structure admissions and all scientific exclusions are unchanged.
