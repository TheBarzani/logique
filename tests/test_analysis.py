"""Aggregation of controlled studies against the strongest baseline."""

import pytest

pd = pytest.importorskip("pandas")

from logique.benchmarks import analysis  # noqa: E402


def costs():
    rows = []
    values = {
        ("G1", "xag"): {"clean_tree": 90, "throwaway_tree": 95},
        ("G1", "sb_simple"): {"clean_tree": 100, "throwaway_tree": 80},
        ("G1", "sb_balanced"): {"clean_tree": 120, "throwaway_tree": 110},
        ("G2", "xag"): {"clean_tree": 200, "throwaway_tree": 200},
        ("G2", "sb_simple"): {"clean_tree": 199, "throwaway_tree": 300},
        ("G2", "sb_balanced"): {"clean_tree": 400, "throwaway_tree": 150},
    }
    for (graph, method), policies in values.items():
        for policy, t in policies.items():
            rows.append(
                dict(
                    benchmark=graph,
                    regime="R3",
                    method=method,
                    mcx_policy=policy,
                    iterations=1,
                    t_count=t,
                )
            )
    return pd.DataFrame(rows)


def test_matched_policies_compare_with_the_best_variant():
    table = analysis.compare_with_baselines(costs()).set_index(
        ["benchmark", "mcx_policy"]
    )
    assert table.loc[("G1", "clean_tree"), "baseline"] == "sb_simple"
    assert table.loc[("G1", "clean_tree"), "outcome"] == "win"
    assert table.loc[("G1", "throwaway_tree"), "outcome"] == "loss"
    # 200 against 199 lies within the 1% tolerance.
    assert table.loc[("G2", "clean_tree"), "outcome"] == "tie"
    assert table.loc[("G2", "throwaway_tree"), "baseline"] == "sb_balanced"


def test_best_policies_and_summary():
    table = analysis.compare_with_baselines(costs(), matched_policy=False)
    table = table.set_index("benchmark")
    assert table.loc["G1", "baseline_value"] == 80
    assert table.loc["G1", "baseline_policy"] == "throwaway_tree"
    assert table.loc["G1", "mcx_policy"] == "clean_tree"
    summary = analysis.summarize_outcomes(table.reset_index())
    row = summary.loc[("R3", "xag")]
    assert (row["wins"], row["ties"], row["losses"]) == (0, 0, 2)
    assert row["geometric_mean_ratio"] == pytest.approx((90 / 80 * 200 / 150) ** 0.5)


def test_pareto_front_keeps_undominated_points():
    points = pd.DataFrame({"q": [10, 12, 12, 20, 30], "t": [100, 90, 95, 90, 50]})
    front = analysis.pareto_front(points, "q", "t")
    assert list(front.index) == [0, 1, 4]
