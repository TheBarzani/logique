# Revision notebooks

These notebooks support the revision of "From Graph k-Coloring to Grover's Circuits via Logic Synthesis". They are
grouped by task of the revision plan; tasks without a folder have no notebook yet. Like every maintained notebook, the
sources keep empty outputs, and the runner writes executed copies and figures to `dump/`.

| Task | Notebook | Purpose |
| --- | --- | --- |
| T3. Explicit cost model and MCX decompositions | [Revision walkthrough](T3-cost-model/revision_walkthrough.ipynb) | K3 from predicate to explicitly decomposed circuits and their costs |
| T3. Explicit cost model and MCX decompositions | [MCX decompositions](T3-cost-model/mcx_decompositions.ipynb) | Multi-controlled X constructions for 3 to 20 controls |
| T4. Corrected comparison under three regimes | [Corrected comparison](T4-corrected-comparison/corrected_comparison.ipynb) | Analysis of a controlled study against the strongest baseline |
| T4. Corrected comparison under three regimes | [XAG and Belletti-Simple](T4-corrected-comparison/xag_belletti_equivalence.ipynb) | The XAG oracle and Belletti-Simple as one construction under the edge-only predicate |

```bash
uv run --no-sync logique notebook run experiments/revision/T3-cost-model/revision_walkthrough.ipynb --offline
uv run --no-sync logique notebook run experiments/revision/T3-cost-model/mcx_decompositions.ipynb --offline
uv run --no-sync logique benchmark run --config configs/corrected_comparison.json
LOGIQUE_STUDY_RUN=dump/MMDDHHMMSS-corrected-study uv run --no-sync logique notebook run experiments/revision/T4-corrected-comparison/corrected_comparison.ipynb --offline
LOGIQUE_STUDY_RUN=dump/MMDDHHMMSS-corrected-study uv run --no-sync logique notebook run experiments/revision/T4-corrected-comparison/xag_belletti_equivalence.ipynb --offline
```

The corrected comparison analyses a study run produced separately by `logique benchmark run`; name its folder in
`LOGIQUE_STUDY_RUN`, since the notebook never selects a run implicitly. The equivalence notebook uses the same variable
only to cross-check its numbers against the study and runs without it.
