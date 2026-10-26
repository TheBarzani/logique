"""Controlled R1/R2/R3 assembly and a sequential, local coloring pilot.

Only logical and optional unrouted U/CX metrics are implemented. Validation uses
monomial records, never statevectors. Sampled coverage is evidence, not proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import time
from typing import TYPE_CHECKING

from logique.coloring import ColoringProblem, encode_coloring, read_dimacs
from logique.synthesis.native import METHODS
from logique.synthesis.saha_belletti import VARIANTS

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

STUDY_METHODS = (*METHODS, *(f"sb_{variant}" for variant in VARIANTS))
REGIMES = ("R1", "R2", "R3")
CONFIG_FIELDS = {
    "kind",
    "inputs",
    "methods",
    "regimes",
    "iterations",
    "seeds",
    "colors",
    "validation",
    "samples",
    "verification_assignments",
    "remove_precolors",
    "common_basis",
    "basis_gates",
    "optimization_level",
    "output",
    "mcx_decomposition",
    "mcx_workspace",
}

RESTORING_MCX_POLICIES = ("clean_tree",)


def _qpy_standard_gate_classes() -> set[type]:
    """Return recognized QPY gate classes with explicit numeric/control state."""
    from qiskit.circuit.library import MCXGate
    from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping

    # The fixed-arity catalogue omits generic MCX. Retain this serializable
    # class so preparation resolution does not implicitly lower logical MCX.
    return {gate.base_class for gate in get_standard_gate_name_mapping().values()} | {
        MCXGate
    }


def _resolved_qpy_circuit(
    circuit: QuantumCircuit, *, expand_wide: bool = False
) -> tuple[QuantumCircuit, dict]:
    """Resolve emitted definitions to standard gates, preserving order and phase.

    Qiskit 2.1.1 QPY reconstructs inverse StatePreparation as forward. Never
    serialize that object, even inside another definition. Use its *actual*
    definition (including its inverse and scalar phases), not its amplitudes.
    This is a bounded definition-based representation, not support for arbitrary
    opaque operations, dynamic circuits, or an ideal-amplitude certificate.
    """
    standard = _qpy_standard_gate_classes()
    resolved = circuit.copy_empty_like()
    resolved.global_phase = 0
    expanded = Counter()
    visited = 0

    def visit(block, wires, depth):
        nonlocal visited
        if depth > 32:
            raise ValueError("QPY definition resolution exceeds depth limit 32")
        if block.num_clbits or block.parameters:
            raise ValueError("QPY resolution requires bound, quantum-only circuits")
        if not math.isfinite(float(block.global_phase)):
            raise ValueError("QPY resolution requires finite scalar phases")
        resolved.global_phase += block.global_phase
        for item in block.data:
            visited += 1
            if visited > 100_000:
                raise ValueError("QPY definition resolution exceeds 100000 operations")
            operation = item.operation
            mapped = [wires[block.find_bit(q).index] for q in item.qubits]
            controls = getattr(operation, "num_ctrl_qubits", 0)
            closed_controls = getattr(operation, "ctrl_state", None) in (
                None,
                (1 << controls) - 1,
            )
            # QPY 2.1.1 also loses generic MCX open-control state. Its emitted
            # definition is X conjugation around a closed-control instance.
            # Resolve open controls consistently, without lowering closed MCX.
            mcx = (
                controls >= 3
                and getattr(getattr(operation, "base_gate", None), "name", None) == "x"
            )
            if expand_wide and mcx and controls > 20:
                raise ValueError("Restoring MCX subset is limited to 20 controls")
            if expand_wide and operation.num_qubits > 21:
                raise ValueError("Restoring definition operation exceeds 21 wires")
            if (
                operation.base_class in standard
                and closed_controls
                and (not expand_wide or operation.num_qubits <= 3 or mcx)
            ):
                # Standard gates have numeric parameters; reject nonfinite ones
                # before QPY, including hidden NaN/Inf in a nested definition.
                for param in operation.params:
                    value = complex(param)
                    if not (math.isfinite(value.real) and math.isfinite(value.imag)):
                        raise ValueError("QPY resolution requires finite parameters")
                resolved.append(operation, mapped)
            else:
                definition = operation.definition
                if definition is None:
                    raise ValueError(
                        f"Unsupported opaque QPY operation: {operation.name}"
                    )
                if definition.num_qubits != operation.num_qubits:
                    raise ValueError("QPY operation definition changes register width")
                expanded[operation.name] += 1
                visit(definition, mapped, depth + 1)

    visit(circuit, list(circuit.qubits), 0)
    return resolved, {
        "policy": "recursive_emitted_definitions_to_standard_gates_v1",
        "representation": "resolved_standard_gates",
        "expanded_definitions": dict(expanded),
        "visited_operations": visited,
        "source_global_phase": float(circuit.global_phase),
        "resolved_global_phase": float(resolved.global_phase),
        "limits": {"definition_depth": 32, "visited_operations": 100_000},
        "semantic_scope": "actual recursive definitions and scalar phases; no ideal-amplitude guarantee",
    }


def _qpy_semantic_signature(circuit: QuantumCircuit) -> dict:
    """Describe flat standard-gate semantics without allocating an operator."""
    standard = _qpy_standard_gate_classes()
    if circuit.num_clbits or circuit.parameters:
        raise ValueError("Unsupported classical or unbound QPY readback")
    operations = []
    for item in circuit.data:
        op = item.operation
        if op.base_class not in standard:
            raise ValueError(f"Unsupported unresolved QPY operation: {op.name}")
        operations.append(
            {
                "class": f"{op.base_class.__module__}.{op.base_class.__qualname__}",
                "name": op.name,
                "qubits": [circuit.find_bit(q).index for q in item.qubits],
                "parameters": [
                    [complex(p).real.hex(), complex(p).imag.hex()] for p in op.params
                ],
                "controls": getattr(op, "num_ctrl_qubits", 0),
                "control_state": getattr(op, "ctrl_state", None),
            }
        )
    return {
        "qubits": circuit.num_qubits,
        "global_phase": float(circuit.global_phase).hex(),
        "operations": operations,
    }


def _stage_timings(timings: dict, backend: dict) -> dict:
    """Describe overlapping measurements without inventing native stage splits."""
    stages = {
        name.removesuffix("_seconds"): {
            "status": "measured",
            "seconds": seconds,
            "clock": "time.perf_counter",
            "source": "coloring_study",
        }
        for name, seconds in timings.items()
    }
    scopes = {
        "encoding": "original coloring encoding; excludes input parsing",
        "effective_encoding": "regime-specific effective problem and encoding",
        "synthesis": "whole Python synthesis/baseline adapter call, including native invocation when used",
        "oracle_wrapper": "initial phase wrapper; selected kickback wrapper may be built during validation",
        "validation": "predicate/phase/restoration checks and selection/construction of final oracle wrapper",
        "preparation_diffusion_search": "combined preparation, diffusion and search assembly; no split measurements",
        "mcx_decomposition": "resolve and lower source blocks once; assemble actual inverses and explicit disjoint scratch embeddings",
    }
    for name, stage in stages.items():
        stage["scope"] = scopes[name]
        stage["included_in"] = "case_total"
    for name in ("optimization", "mapping"):
        stages[name] = {
            "status": "unavailable",
            "seconds": None,
            "reason": "Backend does not expose a separate stage duration",
        }
    native = backend.get("native_seconds")
    stages["native_combined"] = {
        "status": "backend_reported" if native is not None else "unavailable",
        "seconds": native,
        "clock": "std::chrono::steady_clock" if native is not None else None,
        "source": "backend_metadata.native_seconds",
        "scope": "read/select/preprocess/map/serialize network; excludes Python XAG synthesis and JSON output",
        "included_in": "synthesis",
    }
    for name in ("routing", "fault_tolerant_synthesis"):
        stages[name] = {"status": "not_enabled", "seconds": None}
    return stages


def _network_statistics(graph: dict | None, source: str) -> dict:
    """Count serialized node kinds; multiplicative depth is XAG/AIG-only."""
    if graph is None:
        return {"status": "unavailable", "source": source}
    counts = Counter(node["kind"] for node in graph["nodes"])
    depth: dict[int, int] = {}
    and_depth: dict[int, int] = {}
    supported = set(counts) <= {"constant", "input", "and", "xor"}
    for node in graph["nodes"]:
        fanins = [f["node"] for f in node["fanins"]]
        depth[node["id"]] = (
            1 + max((depth[q] for q in fanins), default=0) if fanins else 0
        )
        if supported:
            and_depth[node["id"]] = max(
                (and_depth[q] for q in fanins), default=0
            ) + int(node["kind"] == "and")
    return {
        "status": "derived",
        "source": source,
        "scope": "all serialized nodes, including any dangling nodes",
        "node_counts": dict(counts),
        "AND": counts["and"],
        "XOR": counts["xor"],
        "LUT": counts["lut"],
        "inputs": len(graph["inputs"]),
        "outputs": len(graph["outputs"]),
        "logic_depth": max(depth.values(), default=0),
        "multiplicative_depth": (
            max(and_depth.values(), default=0) if supported else None
        ),
        "multiplicative_depth_status": (
            "derived_AND_weighted_depth"
            if supported
            else "unavailable_for_LUT_or_unknown_nodes"
        ),
    }


def _workspace_provenance(
    width: int,
    data: list[int],
    outputs: list[int],
    constraints: list[int],
    *,
    kickback: bool,
    source: str,
) -> dict:
    """Partition reserved wires; allocation is not a measured live-scratch peak."""
    roles = {
        "data": list(data),
        "output": [] if kickback else list(outputs),
        "kickback": list(outputs) if kickback else [],
        "constraint": list(constraints),
        "mcx_ancilla": [],
    }
    assigned = [q for wires in roles.values() for q in wires]
    if len(set(assigned)) != len(assigned) or not set(assigned) <= set(range(width)):
        raise AssertionError("Workspace roles overlap or lie outside the register")
    roles["unknown"] = sorted(set(range(width)) - set(assigned))
    return {
        "roles": roles,
        "role_counts": {role: len(wires) for role, wires in roles.items()},
        "source": source,
        "role_sources": {
            "data": "ordered data-only register or backend input_qubits",
            "output": "backend output_qubits in raw/compute-Z-inverse-compute blocks",
            "kickback": "backend output_qubits with selected verified XOR kickback wrapper",
            "constraint": "backend constraint_qubits; absent native classification gives no inferred constraints",
            "mcx_ancilla": "no explicit added wires; lowering must preserve register width",
            "unknown": "complement of classified wires within allocated register",
        },
        "unknown_reason": "Residual workspace has no proven per-wire function; not classified as AND-only",
        "mcx_scope": "No explicit added MCX ancillas at this metric level; logical MCX may remain",
        "policy": "persistent_allocated_register; no cross-role borrowing or per-gate summation",
        "peak_reserved_qubits": width,
        "peak_reserved_nondata_qubits": width - len(data),
        "peak_live_workspace_qubits": None,
        "peak_live_status": "unavailable; no liveness/scheduling analysis",
    }


class ExcludedCase(ValueError):
    """A scientifically unsupported construction, whose costs must be omitted."""


def _integers(values, name: str, minimum: int = 0) -> None:
    if (
        not isinstance(values, list)
        or not values
        or any(type(v) is not int or v < minimum for v in values)
        or len(set(values)) != len(values)
    ):
        raise ValueError(
            f"{name} requires a nonempty list of distinct integers >= {minimum}"
        )


def validate_study_config(config: dict) -> dict:
    """Validate every supported control before opening a run or doing synthesis.

    Verification assignments are a mapping from resolved input paths to lists of
    input-register integers. Missing inputs receive the selected default coverage.
    Exhaustive monomial checks are limited to 12 data bits; auto samples above it.
    Unknown controls (including target, precision, limits, and profiles) fail.
    """
    unknown = set(config) - CONFIG_FIELDS
    if unknown:
        raise ValueError(f"Unsupported coloring-study controls: {sorted(unknown)}")
    if {"mcx_decomposition", "mcx_workspace"} & set(config):
        if config.get("mcx_decomposition") not in RESTORING_MCX_POLICIES:
            raise ValueError("mcx_decomposition supports only restoring clean_tree")
        if config.get("mcx_workspace") != "fresh_zero":
            raise ValueError("mcx_workspace must explicitly be fresh_zero")
    result = {
        "kind": "coloring_study",
        "methods": list(STUDY_METHODS),
        "regimes": list(REGIMES),
        "iterations": [1],
        "seeds": [7],
        "validation": "auto",
        "samples": 256,
        "remove_precolors": False,
        "common_basis": False,
        **config,
    }
    if result["kind"] != "coloring_study":
        raise ValueError("kind must be coloring_study")
    inputs = result.get("inputs")
    if (
        not isinstance(inputs, list)
        or not inputs
        or any(not isinstance(p, str) or Path(p).suffix != ".col" for p in inputs)
    ):
        raise ValueError("inputs requires a nonempty list of DIMACS .col paths")
    result["inputs"] = [str(Path(p).resolve()) for p in inputs]
    if len(set(result["inputs"])) != len(inputs):
        raise ValueError("inputs must be distinct")
    for key, known in (("methods", STUDY_METHODS), ("regimes", REGIMES)):
        values = result[key]
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(v, str) or v not in known for v in values)
            or len(set(values)) != len(values)
        ):
            raise ValueError(f"{key} must be distinct selections from {known}")
    _integers(result["iterations"], "iterations")
    if "mcx_decomposition" in config and max(result["iterations"]) > 2:
        raise ValueError("Restoring MCX subset supports iterations 0..2")
    _integers(result["seeds"], "seeds")
    if any(seed >= 1 << 32 for seed in result["seeds"]):
        raise ValueError("seeds must be smaller than 2**32")
    for key in ("remove_precolors", "common_basis"):
        if type(result[key]) is not bool:
            raise ValueError(f"{key} must be boolean")
    if "colors" in result and (
        type(result["colors"]) is not int or result["colors"] < 2
    ):
        raise ValueError("colors must be an integer >= 2")
    if result["validation"] not in ("auto", "sampled", "exhaustive"):
        raise ValueError("validation must be auto, sampled, or exhaustive")
    if type(result["samples"]) is not int or result["samples"] < 1:
        raise ValueError("samples must be a positive integer")
    if result.get("basis_gates", ["u", "cx"]) != ["u", "cx"]:
        raise ValueError("Only the common U/CX basis ['u', 'cx'] is supported")
    optimization = result.get("optimization_level", 1)
    if type(optimization) is not int or optimization not in range(4):
        raise ValueError("optimization_level must be 0, 1, 2, or 3")
    if not result["common_basis"] and {"basis_gates", "optimization_level"} & set(
        config
    ):
        raise ValueError("basis_gates/optimization_level require common_basis=true")
    assignments = result.get("verification_assignments", {})
    if not isinstance(assignments, dict) or set(assignments) - set(result["inputs"]):
        raise ValueError(
            "verification_assignments must map resolved input paths to lists"
        )
    for values in assignments.values():
        if not isinstance(values, list) or any(
            type(v) is not int or v < 0 for v in values
        ):
            raise ValueError(
                "verification assignments must be lists of nonnegative integers"
            )
    if "output" in result and result["output"] is not None:
        if not isinstance(result["output"], (str, Path)) or not re.fullmatch(
            r"\d{10}-[a-zA-Z0-9][a-zA-Z0-9_-]*", Path(result["output"]).name
        ):
            raise ValueError("output directory must be named MMDDHHMMSS-description")
        result["output"] = str(result["output"])
    return result


def _validate_restoring_problem(problem: ColoringProblem) -> None:
    """Bound this initial runner slice before preparation or artifact allocation."""
    if (
        problem.colors > 8
        or len(problem.vertices) * (problem.colors - 1).bit_length() > 21
    ):
        raise ValueError("Restoring MCX subset requires k<=8 and <=21 data wires")


def _problem_without_precolors(problem: ColoringProblem, remove: bool):
    if type(remove) is not bool:
        raise ValueError("remove_precolors must be boolean")
    if problem.precolored and not remove:
        raise ValueError("Precolors require explicit remove_precolors=true")
    transformations = []
    if problem.precolored:
        transformations.append(
            {"operation": "remove_precolors", "removed": dict(problem.precolored)}
        )
    return (
        ColoringProblem(problem.vertices, problem.edges, problem.colors),
        transformations,
    )


@dataclass
class ColoringStudyCase:
    """Reusable blocks; preparation/diffusion use the ordered data register.

    Raw/oracle/search use physical synthesis wires. ``data_qubits`` maps the
    data-only blocks onto those wires. Reflection has the positive Grover sign,
    A(2|0><0|-I)A†, and is built from the actual emitted preparation and inverse.
    """

    raw: QuantumCircuit
    preparation: QuantumCircuit
    oracle: QuantumCircuit
    diffusion: QuantumCircuit
    search: QuantumCircuit
    metadata: dict

    @property
    def circuits(self) -> dict[str, QuantumCircuit]:
        """Return the five independently saved and measured components."""
        return {
            name: getattr(self, name)
            for name in ("raw", "preparation", "oracle", "diffusion", "search")
        }


def _restoring_mcx_block(circuit: QuantumCircuit) -> tuple[QuantumCircuit, dict]:
    """Lower bound emitted definitions with fresh zero scratch, never borrowing.

    The declared subset is clean_tree, 3..20 controls. Its internal RCCX prefix
    computes conjunction bits with phases; the exact final CCX changes only the
    external target, so the prefix inverse cancels every phase and cleans every
    internal bit. This clean-subspace identity extends to superpositions and an
    external reference by linearity. It does not admit dirty initial scratch.
    """
    from .costs import decompose_mcx, is_mcx

    flat, resolution = _resolved_qpy_circuit(circuit, expand_wide=True)
    if any(
        is_mcx(item.operation, 3) and item.operation.num_ctrl_qubits > 20
        for item in flat.data
    ):
        raise ValueError("Restoring MCX subset is limited to 20 controls")
    lowered, info = decompose_mcx(flat, "clean_tree", clean_wires=())
    lowered, emitted = _resolved_qpy_circuit(lowered, expand_wide=True)
    if any(
        is_mcx(item.operation, 3) or item.operation.num_qubits > 3
        for item in lowered.data
    ):
        raise ValueError("Restoring MCX lowering left an unsupported wide gate")
    return lowered, {
        **info,
        "source_width": circuit.num_qubits,
        "source_resolution": resolution,
        "emitted_resolution": emitted,
        "emitted_max_controls": max(
            (getattr(i.operation, "num_ctrl_qubits", 0) for i in lowered.data),
            default=0,
        ),
        "scratch_qubits": list(range(circuit.num_qubits, lowered.num_qubits)),
        "restoration": "clean-subspace prefix/exact-target/prefix-inverse identity; coherent by linearity",
    }


def _apply_restoring_mcx(case: ColoringStudyCase, result) -> ColoringStudyCase:
    """Assemble saved blocks once, with dedicated disjoint scratch per role."""
    from qiskit import QuantumCircuit
    from .costs import MCX_DECOMPOSITIONS

    started = time.perf_counter()
    md = case.metadata
    data = md["data_qubits"]
    n = len(data)
    physical = result.circuit.num_qubits
    target = result.metadata["output_qubits"][0]
    blocks = {}
    if md["method"].startswith("sb_"):
        # The adapter's package uncompute is not re-lowered independently.
        # Lower the actual initializer/compute prefix once and invert that block.
        prefix, blocks["baseline_prefix"] = _restoring_mcx_block(
            result.initializer.compose(result.compute)
        )
        mark = QuantumCircuit(physical)
        constraints = result.metadata["constraint_qubits"]
        # Constant predicates have no constraints; retain the adapter's exact
        # raw action rather than inferring a truth value from an empty list.
        if not constraints:
            raw, blocks["raw"] = _restoring_mcx_block(result.circuit)
        else:
            mark.mcx(constraints, target)
            mark, blocks["baseline_mark"] = _restoring_mcx_block(mark)
            prefix_scratch = list(range(physical, prefix.num_qubits))
            mark_scratch = list(
                range(prefix.num_qubits, prefix.num_qubits + mark.num_qubits - physical)
            )
            raw = QuantumCircuit(prefix.num_qubits + len(mark_scratch))
            raw.compose(prefix, [*range(physical), *prefix_scratch], inplace=True)
            raw.compose(mark, [*range(physical), *mark_scratch], inplace=True)
            raw.compose(
                _resolved_qpy_circuit(prefix.inverse())[0],
                [*range(physical), *prefix_scratch],
                inplace=True,
            )
            blocks["baseline_prefix"]["scratch_qubits"] = prefix_scratch
            blocks["baseline_mark"]["scratch_qubits"] = mark_scratch
    else:
        raw, blocks["raw"] = _restoring_mcx_block(result.circuit)

    oracle = QuantumCircuit(raw.num_qubits)
    if "kickback" in md["oracle_construction"]:
        oracle.x(target)
        oracle.h(target)
        oracle.compose(raw, inplace=True)
        oracle.h(target)
        oracle.x(target)
    else:
        oracle.compose(raw, inplace=True)
        oracle.z(target)
        oracle.compose(_resolved_qpy_circuit(raw.inverse())[0], inplace=True)

    preparation, blocks["preparation"] = _restoring_mcx_block(case.preparation)
    zero = QuantumCircuit(n, global_phase=math.pi)
    zero.x(range(n))
    if n == 1:
        zero.z(0)
    else:
        zero.h(n - 1)
        zero.mcx(list(range(n - 1)), n - 1)
        zero.h(n - 1)
    zero.x(range(n))
    zero, blocks["zero_reflection"] = _restoring_mcx_block(zero)
    a_scratch = list(range(n, preparation.num_qubits))
    z_scratch = list(
        range(preparation.num_qubits, preparation.num_qubits + zero.num_qubits - n)
    )
    diffusion = QuantumCircuit(preparation.num_qubits + len(z_scratch))
    diffusion.compose(
        _resolved_qpy_circuit(preparation.inverse())[0],
        [*range(n), *a_scratch],
        inplace=True,
    )
    diffusion.compose(zero, [*range(n), *z_scratch], inplace=True)
    diffusion.compose(preparation, [*range(n), *a_scratch], inplace=True)

    # These are MCX-owned allocations, never data, flags, outputs, kickback or
    # unknown backend wires. The raw, A and S0 pools are pairwise disjoint.
    raw_scratch = list(range(physical, raw.num_qubits))
    search_a = list(range(raw.num_qubits, raw.num_qubits + len(a_scratch)))
    search_z = list(
        range(
            raw.num_qubits + len(a_scratch),
            raw.num_qubits + len(a_scratch) + len(z_scratch),
        )
    )
    search = QuantumCircuit(raw.num_qubits + len(search_a) + len(search_z))
    search.compose(preparation, [*data, *search_a], inplace=True)
    for _ in range(md["iteration"]):
        search.compose(oracle, range(oracle.num_qubits), inplace=True)
        search.compose(diffusion, [*data, *search_a, *search_z], inplace=True)
    case.raw, case.preparation, case.oracle = raw, preparation, oracle
    case.diffusion, case.search = diffusion, search

    scratch = {
        "raw": raw_scratch,
        "oracle": raw_scratch,
        "preparation": a_scratch,
        "diffusion": [*a_scratch, *z_scratch],
        "search": [*raw_scratch, *search_a, *search_z],
    }
    raw_peak = max(
        (
            b["appended_ancillas"]
            for k, b in blocks.items()
            if k not in ("preparation", "zero_reflection")
        ),
        default=0,
    )
    a_peak = len(a_scratch)
    z_peak = len(z_scratch)
    peaks = {
        "raw": raw_peak,
        "oracle": raw_peak,
        "preparation": a_peak,
        "diffusion": max(a_peak, z_peak),
        "search": max(a_peak, raw_peak, z_peak) if md["iteration"] else a_peak,
    }
    for component, circuit in case.circuits.items():
        workspace = md["component_workspace"][component]
        roles = workspace["roles"]
        # Preserve backend unknowns; add only newly allocated MCX wires.
        roles["mcx_ancilla"] = scratch[component]
        assigned = [q for group in roles.values() for q in group]
        if sorted(assigned) != list(range(circuit.num_qubits)):
            raise AssertionError("Restoring workspace roles overlap or omit wires")
        workspace.update(
            role_counts={r: len(q) for r, q in roles.items()},
            policy="fresh_zero_restoring_mcx; dedicated_role_pools; no borrowing",
            mcx_scope="all recursive emitted MCX with >=3 controls lowered; CCX retained",
            peak_reserved_qubits=circuit.num_qubits,
            peak_reserved_nondata_qubits=circuit.num_qubits - n,
            mcx_reserved_qubits=len(scratch[component]),
            mcx_live_peak_upper_bound=peaks[component],
            mcx_live_peak_source="construction capacity and sequential composition proof; not measured liveness",
        )
        workspace["role_sources"][
            "mcx_ancilla"
        ] = "explicit fresh zero allocation, disjoint from every backend wire"
    md["qubit_roles"]["mcx_ancilla"] = raw_scratch
    md["role_counts"] = {r: len(q) for r, q in md["qubit_roles"].items()}
    md["role_notes"] = (
        "Explicit fresh restoring MCX scratch; backend residual roles unchanged; no cross-role borrowing"
    )
    md["component_registers"].update(
        preparation="ordered_data_then_A_scratch",
        diffusion="ordered_data_then_A_scratch_then_S0_scratch",
        search="physical_then_raw_scratch_then_A_scratch_then_S0_scratch",
    )
    md["mcx_lowering"] = {
        "selected_policy": "clean_tree",
        "workspace_policy": "fresh_zero",
        "supported_policies": list(RESTORING_MCX_POLICIES),
        "unsupported_policies": sorted(
            set(MCX_DECOMPOSITIONS) - set(RESTORING_MCX_POLICIES)
        ),
        "controls_range": [3, 20],
        "blocks": blocks,
        "search_scratch_ownership": {
            "raw": raw_scratch,
            "preparation": search_a,
            "zero_reflection": search_z,
        },
        "search_embeddings": {
            "oracle": list(range(oracle.num_qubits)),
            "preparation": [*data, *search_a],
            "diffusion": [*data, *search_a, *search_z],
        },
        "restoration_scope": "scratch initially zero; every lowered gate restores its scratch for arbitrary data/reference; each saved block boundary and complete search restore MCX scratch; raw backend workspace retains its original contract",
        "representation": "restoring_mcx_resolved_standard_gates",
        "emitted_max_controls": {
            name: max(
                (getattr(i.operation, "num_ctrl_qubits", 0) for i in q.data), default=0
            )
            for name, q in case.circuits.items()
        },
    }
    md["timings"]["mcx_decomposition_seconds"] = time.perf_counter() - started
    md["stage_timings"] = _stage_timings(md["timings"], result.metadata)
    return case


def assemble_case(
    problem: ColoringProblem,
    method: str,
    regime: str,
    *,
    iterations: int = 1,
    seed: int = 7,
    validation: str = "auto",
    samples: int = 256,
    verification_assignments: list[int] | None = None,
    remove_precolors: bool = False,
    mcx_decomposition: str | None = None,
    mcx_workspace: str | None = None,
    executable=None,
) -> ColoringStudyCase:
    """Assemble and validate one controlled case without saving or simulating it.

    Native R3 compiles the complete predicate at 2**bits colors, preserving every
    vertex/input. All preparations retain the original k. Baselines use their
    clean XOR kickback wrapper. Native methods use direct kickback when both
    target sectors verify, otherwise compute-Z-inverse-compute.
    """
    # Reuse control validation even for direct callers, before importing Qiskit.
    validate_study_config(
        {
            "inputs": ["case.col"],
            "methods": [method],
            "regimes": [regime],
            "iterations": [iterations],
            "seeds": [seed],
            "validation": validation,
            "samples": samples,
            "remove_precolors": remove_precolors,
            **(
                {"mcx_decomposition": mcx_decomposition, "mcx_workspace": mcx_workspace}
                if mcx_decomposition is not None or mcx_workspace is not None
                else {}
            ),
        }
    )
    problem, transformations = _problem_without_precolors(problem, remove_precolors)
    if not problem.vertices or problem.colors < 2:
        raise ValueError("Study cases require vertices and at least two colors")
    if mcx_decomposition:
        _validate_restoring_problem(problem)
    start = time.perf_counter()
    encoding = encode_coloring(problem)
    timings = {"encoding_seconds": time.perf_counter() - start}
    if validation == "exhaustive" and encoding.input_count > 12:
        raise ValueError("Exhaustive validation is limited to 12 data bits")
    if verification_assignments is not None and (
        not isinstance(verification_assignments, list)
        or any(
            type(v) is not int or not 0 <= v < 1 << encoding.input_count
            for v in verification_assignments
        )
    ):
        raise ValueError("verification assignment is outside the input register")
    from qiskit import QuantumCircuit
    from logique.circuits.grover import coloring_preparation, _reflection
    from logique.synthesis import synthesize, baseline_components
    from logique.verification import (
        validate,
        verify_phase_oracle,
        verify_kickback_oracle,
    )

    start = time.perf_counter()
    effective = ColoringProblem(
        problem.vertices,
        problem.edges,
        (1 << encoding.bits_per_color) if regime == "R3" else problem.colors,
    )
    effective_encoding = encode_coloring(effective)
    timings["effective_encoding_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    if method.startswith("sb_"):
        try:
            result = baseline_components(
                problem,
                method[3:],
                domain_policy=("domain_free" if regime == "R3" else "complete"),
            )
        except ValueError as error:
            if method == "sb_original" and "multiple higher-index neighbors" in str(
                error
            ):
                raise ExcludedCase(str(error)) from error
            raise
        construction = "clean_xor_kickback"
    else:
        result = synthesize(effective_encoding, method, executable=executable)
        construction = "compute_Z_inverse_compute"
    timings["synthesis_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    oracle = result.phase_oracle()
    timings["oracle_wrapper_seconds"] = time.perf_counter() - start
    data = result.metadata["input_qubits"]
    if len(data) != encoding.input_count:
        raise AssertionError("Synthesis changed the coloring input register")
    start = time.perf_counter()
    options = dict(
        sampled=validation == "sampled" or (validation == "auto" and len(data) > 12),
        samples=samples,
        seed=seed,
        assignments=verification_assignments,
    )
    if method.startswith("sb_"):
        report = verify_kickback_oracle(result, encoding=effective_encoding, **options)
        report.update(
            reference="effective independent coloring predicate",
            phase_construction="X H; clean XOR; H X on target",
            phase_evidence="on checked assignments both target sectors have exact XOR and unit phase; kickback by linearity",
        )
    else:
        raw_report = validate(result, **options)
        try:
            report = verify_kickback_oracle(
                result, encoding=effective_encoding, **options
            )
        except AssertionError as error:
            report = verify_phase_oracle(
                result, encoding=effective_encoding, circuit=oracle, **options
            )
            report["direct_kickback_rejection"] = str(error)
        else:
            target = result.metadata["output_qubits"][0]
            oracle = QuantumCircuit(result.circuit.num_qubits, name="native_phase")
            oracle.x(target)
            oracle.h(target)
            oracle.compose(result.circuit, inplace=True)
            oracle.h(target)
            oracle.x(target)
            construction = "verified_clean_xor_kickback"
            report.update(
                reference="effective independent coloring predicate",
                phase_construction="X H; verified clean XOR; H X on target",
                phase_evidence="exact XOR and unit phase in both checked target sectors; kickback by linearity",
            )
        report["raw_validation"] = raw_report
    timings["validation_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    if regime == "R1":
        preparation = QuantumCircuit(len(data), name="hadamard_preparation")
        preparation.h(range(len(data)))
        preparation_label = "Hadamard_all_binary_codes"
    else:
        preparation = coloring_preparation(encoding)
        preparation_label = "unitary_StatePreparation_uniform_original_k_per_vertex"
    diffusion = _reflection(preparation)
    # _reflection implements A(I-2|0><0|)A†; correct its global sign.
    diffusion.global_phase += math.pi
    search = QuantumCircuit(oracle.num_qubits, name="coloring_search")
    search.compose(preparation, data, inplace=True)
    for _ in range(iterations):
        search.compose(oracle, inplace=True)
        search.compose(diffusion, data, inplace=True)
    timings["preparation_diffusion_search_seconds"] = time.perf_counter() - start
    if method.startswith("sb_"):
        roles = {**result.metadata["qubit_roles"], "mcx_ancilla": []}
    else:
        outputs = result.metadata["output_qubits"]
        roles = {
            "data": data,
            "output": [] if construction == "verified_clean_xor_kickback" else outputs,
            "synthesis_workspace": sorted(
                set(range(oracle.num_qubits)) - set(data) - set(outputs)
            ),
            "constraint": [],
            "kickback": (
                outputs if construction == "verified_clean_xor_kickback" else []
            ),
            "mcx_ancilla": [],
        }
    mapping = {
        v: [data[q] for q in wires] for v, wires in encoding.input_mapping.items()
    }
    component_workspace = {}
    for component in ("raw", "preparation", "oracle", "diffusion", "search"):
        data_only = component in ("preparation", "diffusion")
        component_workspace[component] = _workspace_provenance(
            len(data) if data_only else oracle.num_qubits,
            list(range(len(data))) if data_only else data,
            [] if data_only else result.metadata["output_qubits"],
            [] if data_only else result.metadata.get("constraint_qubits", []),
            kickback=component != "raw" and "kickback" in construction,
            source=(
                "ordered preparation data register"
                if data_only
                else "backend input/output/constraint indices and selected oracle construction"
            ),
        )
    metadata = {
        "metadata_version": 2,
        "method": method,
        "regime": regime,
        "iteration": iterations,
        "seed": seed,
        "colors": problem.colors,
        "effective_predicate_colors": effective.colors,
        "vertices": list(problem.vertices),
        "edges": list(problem.edges),
        "transformations": transformations,
        "input_mapping": mapping,
        "input_bit_order": "lsb_first",
        "data_qubits": data,
        "preparation_construction": preparation_label,
        "oracle_construction": construction,
        "diffusion_construction": "A(2|0><0|-I)A_dagger_from_actual_preparation",
        "search_construction": "A_then_(oracle_then_matching_diffusion)^iteration",
        "predicate": "edge_only_all_binary_codes" if regime == "R3" else "complete",
        "qubit_roles": roles,
        "role_counts": {r: len(q) for r, q in roles.items()},
        "role_notes": "Native synthesis workspace is not classified as AND-only; MCX has no explicit added ancillas",
        "validation": report,
        "composition_evidence": {
            "preparation": (
                "H tensor product gives uniform binary codes"
                if regime == "R1"
                else "per-vertex unitary StatePreparation has amplitudes 1/sqrt(k) on codes 0..k-1 and zero elsewhere"
            ),
            "reflection": "inverse of the actual preparation, zero-state reflection, actual preparation; positive Grover global sign",
            "R3_restriction": (
                "edge-only equals complete predicate on the valid-color preparation support; diffusion preserves that support"
                if regime == "R3"
                else None
            ),
            "search": "composition of validated oracle action and matching reflection; no large search statevector simulation",
        },
        "timings": timings,
        "stage_timings": _stage_timings(timings, result.metadata),
        "timing_policy": "Overlapping scopes; do not sum native_combined with synthesis or case total",
        "structural_statistics": {
            key: _network_statistics(
                result.metadata.get(key), f"backend_metadata.{key}"
            )
            for key in ("source_network", "network")
        },
        "peak_memory": {"status": "unavailable", "bytes": None},
        "component_workspace": component_workspace,
        "backend_metadata": result.metadata,
        "component_registers": {
            name: "ordered_data" if name in ("preparation", "diffusion") else "physical"
            for name in ("raw", "preparation", "oracle", "diffusion", "search")
        },
    }
    case = ColoringStudyCase(
        result.circuit, preparation, oracle, diffusion, search, metadata
    )
    return _apply_restoring_mcx(case, result) if mcx_decomposition else case


def run_coloring_study(config: dict, *, executable=None) -> Path:
    """Run cases sequentially, preserving excluded/failed cases without cost rows.

    All controls and input-specific assignments are checked before numerical work.
    QPY artifacts are the source for every metric row; common-basis artifacts are
    saved too. No routing, FT precision, memory/timeout controls or profiles exist.
    """
    config = validate_study_config(config)
    prepared = []
    for filename in config["inputs"]:
        path = Path(filename)
        problem = read_dimacs(path, colors=config.get("colors"))
        clean, _ = _problem_without_precolors(problem, config["remove_precolors"])
        if "mcx_decomposition" in config:
            _validate_restoring_problem(clean)
        n = encode_coloring(clean).input_count
        if not clean.vertices or clean.colors < 2:
            raise ValueError("Study inputs require vertices and at least two colors")
        if config["validation"] == "exhaustive" and n > 12:
            raise ValueError("Exhaustive validation is limited to 12 data bits")
        if any(
            v >= 1 << n
            for v in config.get("verification_assignments", {}).get(filename, [])
        ):
            raise ValueError(
                f"verification assignment outside input register: {filename}"
            )
        prepared.append((path, problem, hashlib.sha256(path.read_bytes()).hexdigest()))
    from qiskit import qpy
    import pandas as pd
    from .metrics import circuit_metrics, lower_circuit
    from .provenance import environment, checkout_revision, native_provenance
    from .runner import new_run_directory

    native = (
        native_provenance(executable)
        if any(m in METHODS for m in config["methods"])
        else None
    )
    output = new_run_directory(config.get("output"), description="coloring-study")
    manifest = {
        "schema_version": 1,
        "metadata_version": 2,
        "metadata_contract": "Additive v2 fields; legacy timings, roles and CSV columns retained; resolved QPY representation recorded per artifact",
        "config": config,
        "status": "running",
        "cases": [],
        "versions": environment(executable=executable),
        "native": native,
        "checkout": checkout_revision(Path.cwd()),
        "source_hashes": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in (Path(__file__), Path(__file__).with_name("runner.py"))
        },
        "implemented_metric_levels": ["logical"]
        + (["common_basis"] if config["common_basis"] else []),
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (output / "provenance.json").write_text(
        json.dumps(
            {
                key: manifest[key]
                for key in ("versions", "native", "checkout", "source_hashes")
            },
            indent=2,
        )
        + "\n"
    )
    rows = []

    def save():
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if rows:
            pd.DataFrame(rows).to_csv(output / "summary.csv", index=False)

    save()
    try:
        for index, (path, problem, digest) in enumerate(prepared):
            for regime in config["regimes"]:
                for method in config["methods"]:
                    for iteration in config["iterations"]:
                        for seed in config["seeds"]:
                            name = f"{index:03d}_{regime}_{method}_j{iteration}_s{seed}"
                            case = {
                                "name": name,
                                "input": str(path),
                                "sha256": digest,
                                "benchmark": path.stem,
                                "regime": regime,
                                "method": method,
                                "iteration": iteration,
                                "seed": seed,
                                "status": "running",
                            }
                            manifest["cases"].append(case)
                            save()
                            started = time.perf_counter()
                            case_rows = []
                            try:
                                assembled = assemble_case(
                                    problem,
                                    method,
                                    regime,
                                    iterations=iteration,
                                    seed=seed,
                                    validation=config["validation"],
                                    samples=config["samples"],
                                    verification_assignments=config.get(
                                        "verification_assignments", {}
                                    ).get(str(path)),
                                    remove_precolors=config["remove_precolors"],
                                    **(
                                        {
                                            key: config[key]
                                            for key in (
                                                "mcx_decomposition",
                                                "mcx_workspace",
                                            )
                                        }
                                        if "mcx_decomposition" in config
                                        else {}
                                    ),
                                    executable=executable,
                                )
                                case.update(assembled.metadata)
                                artifacts = {}
                                case["artifacts"] = artifacts
                                case["artifact_statistics"] = {}
                                for component, circuit in assembled.circuits.items():
                                    for level in ["logical"] + (
                                        ["common_basis"]
                                        if config["common_basis"]
                                        else []
                                    ):
                                        lower_start = time.perf_counter()
                                        measured = (
                                            circuit
                                            if level == "logical"
                                            else lower_circuit(
                                                circuit,
                                                basis_gates=["u", "cx"],
                                                seed=seed,
                                                optimization_level=config.get(
                                                    "optimization_level", 1
                                                ),
                                            )
                                        )
                                        if level == "common_basis" and not set(
                                            measured.count_ops()
                                        ) <= {"u", "cx"}:
                                            raise AssertionError(
                                                "Common basis contains non U/CX gates"
                                            )
                                        elapsed = time.perf_counter() - lower_start
                                        if measured.num_qubits != circuit.num_qubits:
                                            raise AssertionError(
                                                "Lowering changed the workspace register"
                                            )
                                        artifact = f"{name}_{component}_{level}.qpy"
                                        record = {
                                            "metric_level": level,
                                            "status": "resolving",
                                            "emitted_metrics": circuit_metrics(
                                                measured
                                            ),
                                            "metric_level_detail": (
                                                "logical circuit with recursive definitions resolved to standard gates; mixed granularity, not historical opaque-operation counts"
                                                if level == "logical"
                                                else "unrouted U/CX basis, followed by serialization resolution"
                                            ),
                                            "component_register": assembled.metadata[
                                                "component_registers"
                                            ][component],
                                        }
                                        case["artifact_statistics"][artifact] = record
                                        resolve_start = time.perf_counter()
                                        resolved, representation = (
                                            _resolved_qpy_circuit(measured)
                                        )
                                        expected = _qpy_semantic_signature(resolved)
                                        resolve_seconds = (
                                            time.perf_counter() - resolve_start
                                        )
                                        record.update(
                                            status="resolved",
                                            serialization=representation,
                                        )
                                        artifact_start = time.perf_counter()
                                        with (output / artifact).open("wb") as stream:
                                            qpy.dump(resolved, stream)
                                        artifacts[f"{component}_{level}"] = artifact
                                        record.update(
                                            status="written_unverified",
                                            sha256=hashlib.sha256(
                                                (output / artifact).read_bytes()
                                            ).hexdigest(),
                                        )
                                        with (output / artifact).open("rb") as stream:
                                            saved_circuit = qpy.load(stream)[0]
                                        actual = _qpy_semantic_signature(saved_circuit)
                                        record["readback_signatures"] = {
                                            label: hashlib.sha256(
                                                json.dumps(
                                                    value, sort_keys=True
                                                ).encode()
                                            ).hexdigest()
                                            for label, value in (
                                                ("expected", expected),
                                                ("actual", actual),
                                            )
                                        }
                                        if actual != expected:
                                            raise ValueError(
                                                "QPY semantic signature changed on readback"
                                            )
                                        artifact_seconds = (
                                            time.perf_counter() - artifact_start
                                        )
                                        representation["readback_check"] = {
                                            "status": "exact_standard_gate_signature_match",
                                            "signature_sha256": hashlib.sha256(
                                                json.dumps(
                                                    expected, sort_keys=True
                                                ).encode()
                                            ).hexdigest(),
                                            "scope": "gate classes, ordered wires, numeric parameters, controls and scalar phase; no dense simulation",
                                        }
                                        metric_start = time.perf_counter()
                                        metrics = circuit_metrics(saved_circuit)
                                        metric_seconds = (
                                            time.perf_counter() - metric_start
                                        )
                                        workspace = assembled.metadata[
                                            "component_workspace"
                                        ][component]
                                        record.update(
                                            {
                                                "status": "verified",
                                                "metric_level": level,
                                                "metrics": {
                                                    **metrics,
                                                    "metric_level": level,
                                                },
                                                "sha256": hashlib.sha256(
                                                    (output / artifact).read_bytes()
                                                ).hexdigest(),
                                                "workspace": workspace,
                                                "stage_timings": {
                                                    "serialization_resolution": {
                                                        "status": "measured",
                                                        "seconds": resolve_seconds,
                                                        "scope": "resolve emitted recursive definitions and compute expected signature",
                                                    },
                                                    "lowering": {
                                                        "status": (
                                                            "measured"
                                                            if level == "common_basis"
                                                            else "not_requested"
                                                        ),
                                                        "seconds": (
                                                            elapsed
                                                            if level == "common_basis"
                                                            else None
                                                        ),
                                                    },
                                                    "qpy_write_read": {
                                                        "status": "measured",
                                                        "seconds": artifact_seconds,
                                                    },
                                                    "metrics_from_saved_qpy": {
                                                        "status": "measured",
                                                        "seconds": metric_seconds,
                                                    },
                                                },
                                                "clock": "time.perf_counter",
                                                "included_in": "case.total_seconds",
                                            }
                                        )
                                        case_rows.append(
                                            {
                                                "benchmark": path.stem,
                                                "regime": regime,
                                                "component": component,
                                                "method": method,
                                                "iteration": iteration,
                                                "seed": seed,
                                                **metrics,
                                                "metric_level": level,
                                                "representation": representation[
                                                    "representation"
                                                ],
                                                "artifact": artifact,
                                                "input_sha256": digest,
                                                "validation": assembled.metadata[
                                                    "validation"
                                                ]["status"],
                                                "role_counts": (
                                                    {"data": circuit.num_qubits}
                                                    if component
                                                    in ("preparation", "diffusion")
                                                    else assembled.metadata[
                                                        "role_counts"
                                                    ]
                                                ),
                                                "workspace_role_counts": workspace[
                                                    "role_counts"
                                                ],
                                                "workspace_policy": workspace["policy"],
                                                "peak_reserved_nondata_qubits": workspace[
                                                    "peak_reserved_nondata_qubits"
                                                ],
                                                "peak_live_workspace_qubits": None,
                                                "lowering_seconds": (
                                                    elapsed
                                                    if level == "common_basis"
                                                    else None
                                                ),
                                                "optimization_level": (
                                                    config.get("optimization_level", 1)
                                                    if level == "common_basis"
                                                    else None
                                                ),
                                            }
                                        )
                                case.update(status="complete", artifacts=artifacts)
                                rows.extend(case_rows)
                            except ExcludedCase as error:
                                case.update(status="excluded", reason=str(error))
                            except Exception as error:
                                case.update(
                                    status="failed",
                                    reason=f"{type(error).__name__}: {error}",
                                )
                            finally:
                                case["total_seconds"] = time.perf_counter() - started
                                case.setdefault("stage_timings", {})["case_total"] = {
                                    "status": "measured",
                                    "seconds": case["total_seconds"],
                                    "clock": "time.perf_counter",
                                    "scope": "assembly/validation/artifacts/metrics; excludes final case/manifest save",
                                }
                                (output / f"{name}.json").write_text(
                                    json.dumps(case, indent=2) + "\n"
                                )
                                save()
        manifest["status"] = (
            "complete_with_failures"
            if any(c["status"] == "failed" for c in manifest["cases"])
            else "complete"
        )
    except BaseException:
        manifest["status"] = "interrupted"
        raise
    finally:
        save()
    return output
