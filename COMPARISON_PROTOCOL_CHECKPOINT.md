# Comparison protocol checkpoint — 28 October 2026

Worker task `controlled-comparison-study-1028023823`; branch `codex/coloring-controlled-comparison-study-1028023823`. Implementation commit `7bacf43df5f4beac0003d5a515676f53c52e3b39`. This bounded implementation/run is complete as an evidence-producing batch; the full Task2/4 comparison and protocol freeze are **unfinished**, pending exact-hash independent review and concrete work below.

Runnable from this candidate checkout (never sync):

```sh
export PYTHONPATH="$PWD/src"
export LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl
export LOGIQUE_NATIVE_EXECUTABLE=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
/Users/mar/codex-work/logique/.venv/bin/python -m logique.benchmarks.controlled_comparison
```

This creates a fresh timestamped run. It does not resume or overwrite the saved study. Do not launch another full experiment merely to finish this checkpoint. The bounded recount entry point is `python -m logique.benchmarks.controlled_comparison --recount <saved-run>`; original recount is already complete.

Actual study: `dump/1028080100-controlled-comparison/`. Durable commands, tests, failures, receipts, source/input identities, resource scopes and preservation: `dump/1028075514-comparison-protocol-checkpoint/`. Tool numerical session35535 finished before the user interruption; QPY boundary probe also finished. Model-session ID was not exposed. No numerical child remains owned by this batch.

Results:4380 saved-QPY rows (1800 logical,1290 restoring-MCX,1290 common), all recounted;821.768766s total; peak sampled group553861120 bytes. 253 normally returned groups include failed/excluded cases; one deadline timeout and43 not-run-budget groups remain. Full requested nine-graph ledger exists, but only K3,K5,myciel3,grid6 contribute logical costs, and K3,K5,grid6 common costs.313 tests pass with31 wider dense exclusions; relevant Black/Ruff/diff checks pass.

Read [the fixed partial protocol](docs/research/experimental_protocol.md) and [the actual results/audit](docs/research/controlled_comparison_results_20261028.md). Profiles none/refactoring/balanced are connected across the five Boolean representations; hand-built baselines/structure references explicitly report profile inapplicability. Sequential/parallel structure remains separately named with distinct scratch. Stage/workspace unknowns remain null. Strongest available baseline selection is fully matched, with GM/W/T/L and available-baseline counts.

Concrete remaining work: independent exact-hash review; correct and review wide closed-MCX QPY serialization (31/32 controls roundtrip,33 fails unsigned32-bit control-state field); then newly budget the43 unrun groups (all33 2-Insertions_3 and10 myciel5), the deadline-clipped myciel5 balanced/xag group and failed wide cases. Larger shared-profile CEC, connected MC/cut-ESOP, broader MCX/workspace, routed five-seed and FT precision controls remain full-study open. No silent default or decomposition replacement is admitted. Preserve all partial/failing evidence.

The full paper remains open. No superiority/manuscript, FT/RUS or general ideal-amplitude certificate. No subagents/models/Codex processes, API/paid fallback, hardware, sync, build, dependency changes or pushes were launched. Root README, pilot, protected sources and pins match intake. Correctness and research evidence are separate commits; dispatcher alone publishes integration HEAD.

## Exact candidate and evidence hashes

| Path | SHA256 |
| --- | --- |
| `src/logique/benchmarks/coloring_study.py` | `e212d4984675f15125c4d460f15f1926c442e17eeea6e71c9d137820cd10f938` |
| `src/logique/benchmarks/comparison.py` | `c66a960e271988dffe54d507c497d47e10666c4316fa011f7ecb056c5709a277` |
| `src/logique/benchmarks/controlled_comparison.py` | `1b8452966bbbb9c4fcbb8f63b916fcaa34744ebb7112500cde9346d76fd2bfe0` |
| `src/logique/circuits/records.py` | `53a82c53b947b9813fc779f64054532b8984a620aa93a52f491b11beec195cad` |
| `tests/test_coloring_study.py` | `8b831f3843fbd2cceff236bce4a12ee45b8a431e4c41b6b85e33939419febac2` |
| `tests/test_comparison.py` | `9cedf37e64d944d00396974a085bf67efb632602e8d3280531cf2643f91928c8` |
| `tests/test_controlled_comparison.py` | `32d9083ee4845033e7c76b768d008e926d6e70f6f051203a650974a69d7a27bb` |
| `docs/research/experimental_protocol.md` | `d2e17e5630e3b4f30de759218ae50043edd088faa95a384e78f4eeca294676a9` |
| `docs/research/controlled_comparison_results_20261028.md` | `5d543e2e1936a642a482d08adf906f9af84e92a1d0f411a7f859bd5dc3780524` |
| `dump/1028080100-controlled-comparison/batch.json` | `249efd24052c7da480fdcfdee42eb709342484eee158d7cf9bedb6fcb44ca509` |
| `dump/1028080100-controlled-comparison/summary.csv` | `0c32248c50f7180794366acebe67bf3a0c67587ecbc7252bb0eac955e42f2517` |
| `dump/1028080100-controlled-comparison/strongest-details.csv` | `142080ef4b31bc45713eb5bf02f56459b35ba70774e3a67bb6ac295ff274213e` |
| `dump/1028080100-controlled-comparison/strongest-summary.csv` | `19bbdab4b7f7b995ad7f84e259264aad82af69fcbe1737ac9ddf1fafe7d3e34a` |
| `dump/1028080100-controlled-comparison/requested-ledger.csv` | `38b6b25dadac2ea010777151b3300ad0ce1ca4f680e9baa20b7d6da382ebad30` |
| `dump/1028075514-comparison-protocol-checkpoint/results.json` | `f152684b8db162392947d9482f1c65534487203bf2784e4650c3359a5374af93` |
| `dump/1028075514-comparison-protocol-checkpoint/tests-final/receipt.json` | `0e56de479c4f7e2eb092ef37c802fd8a45c6c908d1b31afff1b932345bc635cb` |
| `dump/1028075514-comparison-protocol-checkpoint/qpy-control-boundary.json` | `90c2698d057240bc750f212c6ee37495c717db6736722d93dc86224cf763ca56` |
| `dump/1028075514-comparison-protocol-checkpoint/preservation.json` | `2253376c31cb36b0cde9fefccd33ff719fd902d4aff9367de54097b8037f297a` |

Native executable SHA256: `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`. No private rebuild was needed. Protocol SHA is the pre-study fixed SHA saved in `protocol-before-study.json`; no post-result rewrite of its fixed parameters occurred.
