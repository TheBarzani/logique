"""Aggregate controlled studies into comparisons with the strongest baseline.

A study (``kind: study``) exports one long-form row per measurement. These
helpers select the complete-search rows, compare every Logique method with the
strongest Saha–Belletti baseline on each graph and regime, summarize the
comparison by geometric means and win, tie and loss counts, and break widths
down by qubit role, as the experimental protocol prescribes.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

BASELINE_PREFIX = "sb_"
SEARCH_COLUMNS = [
    "benchmark",
    "regime",
    "method",
    "mcx_policy",
    "iterations",
    "t_count",
    "t_exact",
    "rotation_count",
    "rotation_t",
    "success",
    "t_per_success",
    "qubits_total",
    "priced",
]
ROLES = ["data_qubits", "output_qubits", "oracle_workspace", "mcx_ancillas"]


def load_study(run: str | Path) -> tuple[pd.DataFrame, dict]:
    """Read a completed study's rows and manifest."""
    run = Path(run)
    manifest = json.loads((run / "run.json").read_text())
    if manifest.get("status") != "complete":
        raise ValueError(f"{run} is not a completed study")
    return pd.read_csv(run / "summary.csv", low_memory=False), manifest


def search_costs(rows: pd.DataFrame, level: str = "fault-tolerant") -> pd.DataFrame:
    """One row per graph, regime, method, MCX policy and iteration count."""
    search = rows[(rows.component == "search") & (rows.metric_level == level)]
    columns = [c for c in SEARCH_COLUMNS if c in search.columns]
    return search[columns].reset_index(drop=True)


def compare_with_baselines(
    costs: pd.DataFrame,
    metric: str = "t_count",
    *,
    matched_policy: bool = True,
    tolerance: float = 0.01,
) -> pd.DataFrame:
    """Compare every Logique method with the strongest baseline per graph and regime.

    With ``matched_policy`` both sides use the same MCX policy, and the
    strongest baseline is the best of the four variants under that policy.
    Otherwise each method and the baselines take their best policy. A method
    wins when it is lower than the baseline by more than ``tolerance``
    (relative), loses when it is higher by more than that, and ties otherwise.
    Rows without a value of ``metric`` are left out.
    """
    costs = costs.dropna(subset=[metric])
    keys = ["benchmark", "regime", "iterations"]
    if matched_policy:
        keys.append("mcx_policy")
    is_baseline = costs.method.str.startswith(BASELINE_PREFIX)
    baselines, methods = costs[is_baseline], costs[~is_baseline]
    strongest = baselines.loc[baselines.groupby(keys)[metric].idxmin()]
    renamed = {"method": "baseline", metric: "baseline_value"}
    if not matched_policy:
        renamed["mcx_policy"] = "baseline_policy"
        methods = methods.loc[methods.groupby([*keys, "method"])[metric].idxmin()]
    strongest = strongest[[*keys, *renamed]].rename(columns=renamed)
    columns = [*keys, "method", metric]
    if not matched_policy:
        columns.append("mcx_policy")
    table = methods[columns].merge(strongest, on=keys)
    table["ratio"] = table[metric] / table["baseline_value"]
    table["outcome"] = np.select(
        [table.ratio < 1 - tolerance, table.ratio > 1 + tolerance],
        ["win", "loss"],
        "tie",
    )
    return table.reset_index(drop=True)


def summarize_outcomes(
    table: pd.DataFrame, by: tuple[str, ...] = ("regime", "method")
) -> pd.DataFrame:
    """Geometric-mean ratio and win, tie and loss counts of a comparison."""
    groups = table.groupby(list(by))
    return pd.DataFrame(
        {
            "graphs": groups.size(),
            "geometric_mean_ratio": groups.ratio.apply(
                lambda r: float(np.exp(np.log(r).mean()))
            ),
            **{
                plural: groups.outcome.apply(lambda o, x=outcome: int((o == x).sum()))
                for outcome, plural in (
                    ("win", "wins"),
                    ("tie", "ties"),
                    ("loss", "losses"),
                )
            },
        }
    )


def width_breakdown(rows: pd.DataFrame) -> pd.DataFrame:
    """Qubits by role for every graph, regime, method and MCX policy.

    Oracle workspace is the computational workspace of a Logique oracle or the
    comparator and check ancillas of a baseline; MCX ancillas are those that
    the decomposition appends.
    """
    keys = ["benchmark", "regime", "method", "mcx_policy"]
    search = rows[rows.component == "search"].drop_duplicates(keys)
    frame = search[keys].copy()
    frame["data_qubits"] = search["data_qubits"]
    frame["output_qubits"] = search["output_qubits"]
    frame["oracle_workspace"] = sum(
        search[column].fillna(0)
        for column in ("workspace_qubits", "ancillas_qubits")
        if column in search
    )
    frame["mcx_ancillas"] = search["mcx_ancillas"]
    frame["qubits_total"] = search["qubits_total"]
    for role in ROLES:
        frame[role] = frame[role].astype(int)
    frame["qubits_total"] = frame["qubits_total"].astype(int)
    return frame.reset_index(drop=True)


def pareto_front(points: pd.DataFrame, x: str, y: str) -> pd.DataFrame:
    """Points not dominated in both ``x`` and ``y`` (lower is better), sorted by ``x``."""
    ordered = points.sort_values([x, y])
    best = np.inf
    keep = []
    for index, value in ordered[y].items():
        if value < best:
            keep.append(index)
            best = value
    return ordered.loc[keep]
