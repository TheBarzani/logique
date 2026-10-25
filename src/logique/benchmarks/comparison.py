"""Per-instance comparisons against the strongest matched baseline."""

import math

CONTEXT_COLUMNS = (
    "regime",
    "component",
    "metric_level",
    "iteration",
    "seed",
    "optimization_profile",
    "mcx_method",
    "workspace_policy",
    "target",
    "precision",
)


def strongest_baseline_comparison(frame, *, metrics=("qubits", "depth", "gates")):
    """Return detailed ratios and geometric summaries in matched contexts.

    The strongest baseline is selected independently for each input and metric.
    Methods prefixed ``sb_`` are baselines. Each context retains its regime,
    component, level and any available compilation controls; different seeds
    are never silently averaged. Input hashes distinguish equal graph names.

    Zero-versus-zero is a tie with ratio one. A positive cost versus a zero
    baseline is a loss with an undefined finite ratio, explicitly omitted from
    geometric aggregation. Missing baselines and duplicate cost rows fail.
    Failed/excluded cases must have no cost rows, as in the study runner.
    """
    import pandas as pd

    required = {"benchmark", "method", "metric_level", *metrics}
    if not required <= set(frame.columns) or frame.empty:
        raise ValueError("Require nonempty cost rows with method, level and metrics")
    if not metrics or len(set(metrics)) != len(metrics):
        raise ValueError("metrics must be a nonempty distinct sequence")
    frame = frame.copy()
    for metric in metrics:
        frame[metric] = pd.to_numeric(frame[metric], errors="raise")
    contexts = [name for name in CONTEXT_COLUMNS if name in frame.columns]
    inputs = ["benchmark"] + (
        ["input_sha256"] if "input_sha256" in frame.columns else []
    )
    keys = [*contexts, *inputs]
    if frame[[*keys, "method"]].isna().any().any():
        raise ValueError("Comparison context and method cannot be missing")
    if frame.duplicated([*keys, "method"]).any():
        raise ValueError("Duplicate method costs in the same comparison context")
    if not frame["method"].map(lambda value: isinstance(value, str)).all():
        raise ValueError("method must contain names")
    values = frame[list(metrics)].to_numpy(dtype=float)
    if any(not math.isfinite(value) or value < 0 for row in values for value in row):
        raise ValueError("Costs must be finite and nonnegative")
    rows = []
    for group_key, group in frame.groupby(keys, sort=True, dropna=False):
        group_key = group_key if isinstance(group_key, tuple) else (group_key,)
        context = dict(zip(keys, group_key))
        baseline_mask = group.method.str.startswith("sb_")
        baselines = group[baseline_mask]
        proposed = group[~baseline_mask]
        if baselines.empty and not proposed.empty:
            raise ValueError(f"No baseline for comparison context {context}")
        for metric in metrics:
            if baselines.empty:
                continue
            best = float(baselines[metric].min())
            winners = sorted(baselines.loc[baselines[metric] == best, "method"])
            for candidate in proposed.to_dict("records"):
                cost = float(candidate[metric])
                outcome = "win" if cost < best else "tie" if cost == best else "loss"
                ratio = cost / best if best else 1.0 if cost == 0 else None
                rows.append(
                    {
                        **context,
                        "method": candidate["method"],
                        "metric": metric,
                        "cost": cost,
                        "baseline_cost": best,
                        "baseline_methods": "|".join(winners),
                        "ratio": ratio,
                        "outcome": outcome,
                        "ratio_status": (
                            "finite" if ratio is not None else "zero_baseline"
                        ),
                    }
                )
    details = pd.DataFrame(rows)
    summaries = []
    if details.empty:
        return details, pd.DataFrame()
    for group_key, group in details.groupby([*contexts, "method", "metric"], sort=True):
        ratios = group.ratio.dropna().tolist()
        geometric = (
            0.0
            if ratios and 0 in ratios
            else (
                math.exp(math.fsum(math.log(value) for value in ratios) / len(ratios))
                if ratios
                else None
            )
        )
        summaries.append(
            {
                **dict(zip([*contexts, "method", "metric"], group_key)),
                "instances": len(group),
                "wins": int((group.outcome == "win").sum()),
                "ties": int((group.outcome == "tie").sum()),
                "losses": int((group.outcome == "loss").sum()),
                "finite_ratios": len(ratios),
                "undefined_ratios": len(group) - len(ratios),
                "geometric_cost_ratio": geometric,
            }
        )
    return details, pd.DataFrame(summaries)
