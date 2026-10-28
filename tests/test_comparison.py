"""Matched comparisons must use per-instance strongest-baseline ratios."""

import pytest

pd = pytest.importorskip("pandas")

from logique.benchmarks.comparison import strongest_baseline_comparison  # noqa: E402


def costs():
    return pd.DataFrame(
        [
            {
                "benchmark": graph,
                "method": method,
                "metric_level": "logical",
                "gates": cost,
            }
            for graph, methods in (
                ("a", (("xag", 5), ("sb_simple", 10), ("sb_minimal", 20))),
                ("b", (("xag", 200), ("sb_simple", 300), ("sb_minimal", 100))),
            )
            for method, cost in methods
        ]
    )


def test_strongest_baseline_is_selected_per_graph_and_geometric_mean_is_ratio():
    details, summary = strongest_baseline_comparison(costs(), metrics=("gates",))
    assert details.baseline_methods.tolist() == ["sb_simple", "sb_minimal"]
    assert details.ratio.tolist() == [0.5, 2]
    row = summary.iloc[0]
    assert (row.wins, row.ties, row.losses, row.instances) == (1, 0, 1, 2)
    assert row.geometric_cost_ratio == pytest.approx(1)


def test_levels_and_seeds_never_share_aggregation():
    first = costs().assign(seed=7)
    second = costs().assign(seed=9, metric_level="common_basis")
    _, summary = strongest_baseline_comparison(
        pd.concat([first, second], ignore_index=True), metrics=("gates",)
    )
    assert len(summary) == 2
    assert set(zip(summary.metric_level, summary.seed)) == {
        ("logical", 7),
        ("common_basis", 9),
    }


def test_numeric_text_costs_are_compared_numerically():
    frame = costs()
    frame["gates"] = frame.gates.astype(str)
    details, _ = strongest_baseline_comparison(frame, metrics=("gates",))
    assert details.baseline_cost.tolist() == [10, 100]


def test_zero_costs_and_tied_best_baselines_are_explicit():
    frame = costs()
    frame.loc[frame.benchmark == "a", "gates"] = 0
    frame.loc[
        (frame.benchmark == "b") & frame.method.str.startswith("sb_"), "gates"
    ] = 0
    details, summary = strongest_baseline_comparison(frame, metrics=("gates",))
    assert details.iloc[0].baseline_methods == "sb_minimal|sb_simple"
    assert details.iloc[0].ratio == 1
    assert details.iloc[1].ratio_status == "zero_baseline"
    assert summary.iloc[0].undefined_ratios == 1
    assert summary.iloc[0].ties == 1 and summary.iloc[0].losses == 1


@pytest.mark.parametrize(
    "failure", ["duplicate", "missing_baseline", "negative", "nan"]
)
def test_invalid_comparisons_fail(failure):
    frame = costs()
    if failure == "duplicate":
        frame = pd.concat([frame, frame.iloc[:1]], ignore_index=True)
    elif failure == "missing_baseline":
        frame = frame[frame.method == "xag"]
    else:
        frame.loc[0, "gates"] = -1 if failure == "negative" else float("nan")
    with pytest.raises(ValueError):
        strongest_baseline_comparison(frame, metrics=("gates",))


def test_strongest_comparison_records_available_baseline_denominator():
    details, _ = strongest_baseline_comparison(costs(), metrics=("gates",))
    assert details.available_baseline_count.tolist() == [2, 2]
    assert details.available_baseline_methods.tolist() == [
        "sb_minimal|sb_simple",
        "sb_minimal|sb_simple",
    ]
