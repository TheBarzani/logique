"""Controlled comparison of complete Grover searches under explicit cost models.

For every input graph, method and regime, the study builds a verified search
instance, expands its multi-controlled gates with each decomposition policy,
and prices the preparation, the oracle and the diffusion operator separately at
the requested metric levels. Search rows combine the components for the chosen
iteration counts, synthesize rotations under a whole-algorithm error budget,
and record widths, stage timings and validation coverage.
"""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import time

from logique.coloring import read_dimacs
from logique.coloring.counting import count_colorings
from .provenance import checkout_revision, environment, native_provenance
from .runner import new_run_directory

REGIMES = ("R1", "R2", "R3")
PRICING = ("static", "measurement")
TARGETS = ("logical", "toffoli", "fault-tolerant", "routed")
PROFILES = ("refactor",)
DEFAULTS = {
    "regimes": list(REGIMES),
    "mcx_policies": ["clean_tree"],
    "pricing": ["static"],
    "optimization_profile": "refactor",
    "targets": ["logical", "toffoli", "fault-tolerant"],
    "rotation_budget": 1e-3,
    "iterations": "optimal",
    "seeds": [11, 23, 37, 41, 53],
    "relative_phase_mirrored": True,
    "drop_precolors": True,
    "samples": 256,
    "seed": 7,
}
LIMITS = {
    "exhaustive_inputs": 12,
    "witnesses": 16,
    "synthesis_timeout_s": 180,
    "count_budget": 10_000_000,
    "route_qubits": None,
}


def study_settings(config: dict) -> dict:
    """Fill defaults and reject unknown or inconsistent study settings."""
    from logique.benchmarks.costs import MCX_DECOMPOSITIONS
    from logique.synthesis import METHODS
    from logique.synthesis.saha_belletti import VARIANTS

    settings = {**DEFAULTS, **config}
    settings["limits"] = {**LIMITS, **config.get("limits", {})}
    unknown_limits = set(settings["limits"]) - set(LIMITS)
    if unknown_limits:
        raise ValueError(f"Unknown limits: {sorted(unknown_limits)}")
    known = {*METHODS, *(f"sb_{v}" for v in VARIANTS)}
    checks = {
        "methods": known,
        "regimes": set(REGIMES),
        "mcx_policies": set(MCX_DECOMPOSITIONS),
        "pricing": set(PRICING),
        "targets": set(TARGETS),
    }
    for key, allowed in checks.items():
        values = settings.get(key, ["xag"] if key == "methods" else [])
        if not values or not set(values) <= allowed:
            raise ValueError(f"{key} must be selected from {sorted(allowed)}")
    if settings["optimization_profile"] not in PROFILES:
        raise ValueError(
            f"optimization_profile {settings['optimization_profile']!r} is not "
            f"available yet; choose from {list(PROFILES)}"
        )
    iterations = settings["iterations"]
    if not (
        iterations == "optimal"
        or (type(iterations) is int and iterations >= 0)
        or (
            isinstance(iterations, list)
            and iterations
            and all(type(j) is int and j >= 0 for j in iterations)
        )
    ):
        raise ValueError(
            "iterations must be 'optimal', an integer, or a list of integers"
        )
    if not 0 < settings["rotation_budget"] < 1:
        raise ValueError("rotation_budget must lie strictly between 0 and 1")
    return settings


def _pad(circuit, width):
    from qiskit import QuantumCircuit

    padded = QuantumCircuit(width)
    padded.compose(circuit, qubits=range(circuit.num_qubits), inplace=True)
    return padded


def expand_oracle(instance, policy: str, *, relative_phase: bool = True):
    """Expand the oracle's multi-controlled gates; return the circuit and records.

    A mirrored oracle (initialization, compute block, kick-back gate, inverse
    compute block, inverse initialization) is rebuilt around the expanded
    compute block, whose inverse restores any throwaway garbage; its Toffoli
    gates may use relative phases because only the kick-back gate acts in
    between. Gates without a mirror use the restoring tree when the policy is
    the throwaway tree.
    """
    from qiskit import QuantumCircuit
    from .costs import decompose_mcx, relative_phase_toffolis

    restoring = "clean_tree" if policy == "throwaway_tree" else policy
    oracle = instance.oracle
    if instance.mirrored is None:
        expanded, info = decompose_mcx(oracle, restoring)
        return expanded, [info]
    start, stop = instance.mirrored
    data = oracle.data
    width = oracle.num_qubits

    def copy(instructions, size):
        circuit = QuantumCircuit(size)
        for inst in instructions:
            wires = [circuit.qubits[oracle.find_bit(q).index] for q in inst.qubits]
            circuit.append(inst.operation, wires)
        return circuit

    compute, compute_info = decompose_mcx(copy(data[start:stop], width), policy)
    if relative_phase:
        compute = relative_phase_toffolis(compute)
    kick = copy(data[stop : stop + 1], compute.num_qubits)
    reusable = (
        [] if policy == "throwaway_tree" else list(range(width, compute.num_qubits))
    )
    kick, kick_info = decompose_mcx(kick, restoring, clean_wires=reusable)
    full = QuantumCircuit(kick.num_qubits)
    initialization = copy(data[:start], width)
    full.compose(initialization, range(width), inplace=True)
    full.compose(compute, range(compute.num_qubits), inplace=True)
    full.compose(kick, inplace=True)
    full.compose(compute.inverse(), range(compute.num_qubits), inplace=True)
    full.compose(initialization.inverse(), range(width), inplace=True)
    return full, [compute_info, kick_info]


def _component_metrics(decomposed, clean, pricing, targets):
    """Metrics of one expanded component, keyed by metric level."""
    from .costs import clifford_t, ft_metrics, toffoli_metrics
    from .logical_and import measurement_assisted_metrics

    levels = {}
    if "toffoli" in targets:
        levels["toffoli"] = toffoli_metrics(decomposed)
    if "fault-tolerant" in targets:
        if "static" in pricing:
            levels["fault-tolerant"] = ft_metrics(clifford_t(decomposed))
        if "measurement" in pricing:
            levels["fault-tolerant, measurement-assisted"] = (
                measurement_assisted_metrics(decomposed, clean_wires=clean)
            )
    return levels


def run_study(config: dict, *, executable=None) -> Path:
    """Run a controlled comparison and export one long-form row per measurement."""
    import pandas as pd
    from qiskit import qpy
    from logique.circuits.search import baseline_instance, logique_instance
    from .costs import (
        decompose_mcx,
        grover_success,
        optimal_iterations,
        rotation_t_count,
    )
    from .metrics import circuit_metrics
    from .routing import default_backend, routed_metrics

    settings = study_settings(config)
    limits = settings["limits"]
    inputs = [Path(p).resolve() for p in settings["inputs"]]
    methods = settings["methods"]
    native = (
        native_provenance(executable)
        if any(not m.startswith("sb_") for m in methods)
        else None
    )
    output = new_run_directory(settings.get("output"), description="corrected-study")
    manifest = {
        "schema_version": 1,
        "run_id": output.name,
        "config": config,
        "settings": settings,
        "versions": environment(),
        "checkout": checkout_revision(Path.cwd()),
        "native": native,
        "status": "running",
        "cases": [],
    }
    rows = []
    backend = default_backend() if "routed" in settings["targets"] else None
    route_qubits = limits["route_qubits"] or (backend.num_qubits if backend else 0)

    def save():
        (output / "run.json").write_text(
            json.dumps(manifest, indent=2, default=str) + "\n"
        )
        if rows:
            pd.DataFrame(rows).to_csv(output / "summary.csv", index=False)

    verification = {
        "samples": settings["samples"],
        "witnesses": limits["witnesses"],
        "exhaustive_inputs": limits["exhaustive_inputs"],
        "seed": settings["seed"],
    }
    save()
    try:
        for path in inputs:
            problem = read_dimacs(path)
            if settings["drop_precolors"]:
                problem = replace(problem, precolored={})
            solutions = count_colorings(problem, budget=limits["count_budget"])
            graph = {
                "benchmark": path.stem,
                "vertices": len(problem.vertices),
                "edges": len(problem.edges),
                "colors": problem.colors,
            }
            for method in methods:
                for regime in settings["regimes"]:
                    name = f"{path.stem}_{method}_{regime}"
                    case = {"name": name, **graph, "method": method, "regime": regime}
                    manifest["cases"].append(case)
                    case["status"] = "running"
                    save()
                    try:
                        if method.startswith("sb_"):
                            instance = baseline_instance(
                                problem, method[3:], regime, verification=verification
                            )
                        else:
                            instance = logique_instance(
                                problem,
                                method,
                                regime,
                                executable=executable,
                                parameters=settings.get("parameters", {}),
                                verification=verification,
                                timeout=limits["synthesis_timeout_s"],
                            )
                    except subprocess.TimeoutExpired:
                        case["status"] = "timeout"
                        rows.append(
                            {
                                **graph,
                                "method": method,
                                "regime": regime,
                                "status": "timeout",
                            }
                        )
                        save()
                        continue
                    case.update(
                        oracle_form=instance.form,
                        validation=instance.validation,
                        roles={k: len(v) for k, v in instance.roles.items()},
                        structure=instance.structure,
                        timings=instance.timings,
                        domain=instance.domain,
                        solutions=solutions,
                    )
                    with (output / f"{name}.qpy").open("wb") as stream:
                        qpy.dump(
                            [instance.preparation, instance.oracle, instance.diffusion],
                            stream,
                        )
                    coverage = instance.validation["coverage"]
                    common = {
                        **graph,
                        "method": method,
                        "regime": regime,
                        "oracle_form": instance.form,
                        "validation": instance.validation["status"],
                        "witnesses": coverage.get("witnesses"),
                        "marked_assignments": instance.validation["marked_assignments"],
                        "domain": instance.domain,
                        "solutions": solutions,
                    }
                    if "logical" in settings["targets"]:
                        for component in ("preparation", "oracle", "diffusion"):
                            rows.append(
                                {
                                    **common,
                                    "component": component,
                                    **circuit_metrics(getattr(instance, component)),
                                }
                            )
                    width = instance.oracle.num_qubits
                    p_initial = (
                        None if solutions is None else solutions / instance.domain
                    )
                    for policy in settings["mcx_policies"]:
                        started = time.perf_counter()
                        oracle, oracle_info = expand_oracle(
                            instance,
                            policy,
                            relative_phase=settings["relative_phase_mirrored"],
                        )
                        restoring = (
                            "clean_tree" if policy == "throwaway_tree" else policy
                        )
                        diffusion, diffusion_info = decompose_mcx(
                            instance.diffusion, restoring, clean_wires=instance.clean
                        )
                        decomposition_s = time.perf_counter() - started
                        total_width = max(oracle.num_qubits, diffusion.num_qubits)
                        appended = list(range(width, total_width))
                        clean = [*instance.clean, *appended]
                        started = time.perf_counter()
                        parts = {
                            "preparation": _component_metrics(
                                instance.preparation,
                                [],
                                settings["pricing"],
                                settings["targets"],
                            ),
                            "oracle": _component_metrics(
                                oracle, clean, settings["pricing"], settings["targets"]
                            ),
                            "diffusion": _component_metrics(
                                diffusion,
                                clean,
                                settings["pricing"],
                                settings["targets"],
                            ),
                        }
                        pricing_s = time.perf_counter() - started
                        policy_common = {
                            **common,
                            "mcx_policy": policy,
                            "mcx_ancillas": total_width - width,
                            "qubits_total": total_width,
                            **{
                                f"{role}_qubits": len(q)
                                for role, q in instance.roles.items()
                            },
                        }
                        for component, levels in parts.items():
                            for level, metrics in levels.items():
                                rows.append(
                                    {
                                        **policy_common,
                                        "component": component,
                                        **{
                                            k: v
                                            for k, v in metrics.items()
                                            if k != "metric_level"
                                        },
                                        "metric_level": level,
                                    }
                                )
                        if settings["iterations"] == "optimal":
                            sweep = (
                                []
                                if p_initial is None
                                else [optimal_iterations(p_initial)]
                            )
                        elif isinstance(settings["iterations"], list):
                            sweep = settings["iterations"]
                        else:
                            sweep = [settings["iterations"]]
                        for level in (
                            "fault-tolerant",
                            "fault-tolerant, measurement-assisted",
                        ):
                            if level not in parts["oracle"]:
                                continue
                            for j in sweep:
                                prep = parts["preparation"][level]
                                orc, dif = (
                                    parts["oracle"][level],
                                    parts["diffusion"][level],
                                )
                                rotations = prep["rotation_count"] + j * (
                                    orc["rotation_count"] + dif["rotation_count"]
                                )
                                per_rotation = (
                                    rotation_t_count(
                                        settings["rotation_budget"] / rotations
                                    )
                                    if rotations
                                    else 0
                                )
                                exact = prep["t_count"] + j * (
                                    orc["t_count"] + dif["t_count"]
                                )
                                total = exact + rotations * per_rotation
                                success = (
                                    None
                                    if p_initial is None
                                    else grover_success(p_initial, j)
                                )
                                rows.append(
                                    {
                                        **policy_common,
                                        "component": "search",
                                        "metric_level": level,
                                        "iterations": j,
                                        "t_exact": exact,
                                        "rotation_count": rotations,
                                        "rotation_t": per_rotation,
                                        "t_count": total,
                                        "success": success,
                                        "t_per_success": (
                                            None if not success else total / success
                                        ),
                                        "decomposition_s": decomposition_s,
                                        "pricing_s": pricing_s,
                                        **{
                                            f"{stage}": value
                                            for stage, value in instance.timings.items()
                                        },
                                    }
                                )
                        if "routed" in settings["targets"]:
                            iteration = instance.preparation.copy()
                            iteration = _pad(iteration, total_width)
                            iteration.compose(
                                oracle, range(oracle.num_qubits), inplace=True
                            )
                            iteration.compose(
                                diffusion, range(diffusion.num_qubits), inplace=True
                            )
                            started = time.perf_counter()
                            if total_width > route_qubits:
                                record = {
                                    "routed": False,
                                    "reason": f"needs {total_width} qubits; limit {route_qubits}",
                                }
                            else:
                                record = routed_metrics(
                                    iteration, backend=backend, seeds=settings["seeds"]
                                )
                                record.pop("per_seed", None)
                            rows.append(
                                {
                                    **policy_common,
                                    "component": "iteration",
                                    **{k: v for k, v in record.items() if k != "seeds"},
                                    "routing_s": time.perf_counter() - started,
                                    "metric_level": "routed",
                                }
                            )
                        case.setdefault("policies", {})[policy] = {
                            "oracle": oracle_info,
                            "diffusion": diffusion_info,
                            "qubits_total": total_width,
                        }
                    case["status"] = "complete"
                    save()
        manifest["status"] = "complete"
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = {"type": type(error).__name__, "message": str(error)}
        if manifest["cases"]:
            manifest["cases"][-1]["status"] = "failed"
        save()
        raise
    save()
    return output
