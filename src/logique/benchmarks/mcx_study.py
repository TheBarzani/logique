"""Bounded, opt-in whole-circuit MCX comparisons.

This module does not widen coloring_study's admitted clean-tree configuration.
It preserves actual emitted inverses and distinguishes held throwaway garbage
from restoring scratch. Metrics are observations pending independent review.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from . import costs
from .coloring_study import _resolved_qpy_circuit, assemble_case

if TYPE_CHECKING:
    from qiskit import QuantumCircuit
    from logique.coloring import ColoringProblem

GRAY_OPERATION_CAP = 50_000
MAX_CONTROLS = 20
MAX_SOURCE_OPERATIONS = 10_000
MAX_EMITTED_OPERATIONS = 100_000


class StudyExclusion(ValueError):
    """A preallocation or scientific-domain exclusion, never a measured cost."""


def construction_estimate(method: str, controls: int) -> dict:
    """Plan construction before Qiskit, including exponential Gray expansion.

    The installed Gray chain visits 2**n strings of n bits. Each nonzero
    string emits at most n-1 CX and one CU1. Each CU1 expands into three
    phases and two CX. Thus (n+4)*2**n+2 bounds a phase/CX expansion.
    Memory and throughput figures are conservative planning assumptions, not
    allocator limits or predictions with measured confidence intervals.
    """
    if method not in costs.MCX_DECOMPOSITIONS:
        raise ValueError(f"Unknown MCX policy: {method}")
    if type(controls) is not int or not 3 <= controls <= MAX_CONTROLS:
        raise StudyExclusion("MCX study requires 3..20 controls")
    gray = method == "gray_code"
    operations = (controls + 4) * (1 << controls) + 2 if gray else None
    return {
        "method": method,
        "controls": controls,
        "gray_strings": (1 << controls) if gray else None,
        "gray_string_characters": controls * (1 << controls) if gray else None,
        "phase_cx_operations_upper_bound": operations,
        "estimated_bytes": operations * 2048 if gray else None,
        "planning_seconds": operations / 10_000 if gray else None,
        "operation_cap": GRAY_OPERATION_CAP,
        "status": "excluded" if gray and operations > GRAY_OPERATION_CAP else "safe",
        "scope": "Gray bound before construction; non-Gray polynomial templates at n<=20; no hard internal-allocation guarantee",
    }


def _preflight(circuit: QuantumCircuit, method: str) -> QuantumCircuit:
    if method not in costs.MCX_DECOMPOSITIONS:
        raise ValueError(f"Unknown MCX policy: {method}")
    if circuit.num_qubits > 96 or len(circuit.data) > MAX_SOURCE_OPERATIONS:
        raise StudyExclusion("source exceeds 96 wires or 10000 instructions")
    if circuit.num_clbits or circuit.parameters:
        raise StudyExclusion("bound quantum-only source required")
    flat, _ = _resolved_qpy_circuit(circuit, expand_wide=True)
    if any(i.operation.name in ("measure", "reset", "delay") for i in flat.data):
        raise StudyExclusion("dynamic or timed instructions unsupported")
    estimates = [
        construction_estimate(method, i.operation.num_ctrl_qubits)
        for i in flat.data
        if costs.is_mcx(i.operation, 3)
    ]
    if any(e["status"] == "excluded" for e in estimates):
        raise StudyExclusion("Gray preallocation operation cap exceeded")
    if (
        method == "gray_code"
        and sum(e["phase_cx_operations_upper_bound"] for e in estimates)
        + len(flat.data)
        > GRAY_OPERATION_CAP
    ):
        raise StudyExclusion("aggregate Gray block operation cap exceeded")
    return flat


def lower_block(
    circuit: QuantumCircuit, method: str, *, mirrored: bool = False
) -> tuple[QuantumCircuit, dict]:
    """Lower a restoring block, or a monomial prefix with a required mirror.

    Dirty templates may borrow arbitrary noninvolved wires and must restore
    them, even when entangled. Clean templates append zero scratch; they never
    assume backend workspace is clean. Throwaway prefixes allocate distinct
    scratch per gate and hold it until their actual expanded inverse executes.
    The caller must actually assemble that inverse, not replay the source.
    """
    from qiskit import QuantumCircuit
    from logique.circuits.records import _qiskit_records

    flat = _preflight(circuit, method)
    if method == "throwaway_tree":
        if not mirrored:
            raise StudyExclusion("throwaway requires an actual mirrored prefix")
        records = _qiskit_records(circuit)
        if any(
            r["kind"] == "rx" and r["angle"] not in (-math.pi, math.pi) for r in records
        ):
            raise StudyExclusion("throwaway prefix must be monomial")
    # Preserve monomial source instruction boundaries for throwaway replacement.
    # A controlled-Rx(pi) definition can contain nonmonomial intermediate gates;
    # garbage must never be inserted inside that definition.
    substitution_source = circuit if method == "throwaway_tree" else flat
    result, info = costs.decompose_mcx(substitution_source, method)
    result, _ = _resolved_qpy_circuit(result, expand_wide=True)
    if len(result.data) > MAX_EMITTED_OPERATIONS:
        raise StudyExclusion("emitted instructions exceed 100000")
    if any(costs.is_mcx(i.operation, 3) for i in result.data):
        raise StudyExclusion("recursive MCX remains after selected construction")
    # Preserve ordered wire identity while avoiding mixed-register QPY bugs.
    result = QuantumCircuit(result.num_qubits).compose(result)
    return result, {
        **info,
        "scratch_qubits": list(range(circuit.num_qubits, result.num_qubits)),
        "scratch_capacity": info["appended_ancillas"] + info["borrowed_dirty_wires"],
        "held_scratch": info["garbage_ancillas"],
        "boundary_restored": method != "throwaway_tree",
        "source_instructions": len(flat.data),
        "emitted_instructions": len(result.data),
        "workspace_scope": "construction capacity, not optimized liveness or process memory",
    }


def _inverse(circuit: QuantumCircuit) -> QuantumCircuit:
    return _resolved_qpy_circuit(circuit.inverse(), expand_wide=True)[0]


@dataclass
class MCXStudyCase:
    """Saved components and explicit embeddings of disjoint scratch pools."""

    circuits: dict[str, QuantumCircuit]
    metadata: dict


def assemble_mcx_case(
    problem: ColoringProblem,
    method: str,
    regime: str,
    policy: str,
    *,
    iterations: int = 1,
    seed: int = 7,
    executable=None,
) -> MCXStudyCase:
    """Apply a matched policy to a validated small coloring service.

    Baseline/structure comparators and domains form a prefix; the final
    conjunction restores scratch and the actual expanded prefix is inverted.
    Native raw computations use compute-Z-actual-inverse for every policy,
    including k-LUT and best-fit. For throwaway, final conjunction, A and S0
    explicitly use clean_tree because they need restoring gates. Raw native
    garbage is held across Z. This is a matched wrapper, not direct kickback
    performance. Complete predicates in R1/R2 and edge-only R3 follow the source
    service. R3 is valid as complete coloring only on valid-color A's support.
    """
    from qiskit import QuantumCircuit
    from logique.synthesis import baseline_components
    from logique.circuits.structure import structure_oracle

    if policy not in costs.MCX_DECOMPOSITIONS:
        raise ValueError(f"Unknown MCX policy: {policy}")
    n = len(problem.vertices) * (problem.colors - 1).bit_length()
    if problem.precolored or not 1 <= n <= 8 or not 2 <= problem.colors <= 8:
        raise StudyExclusion("whole fixtures require no precolors, k2..8, data1..8")
    if type(iterations) is not int or not 0 <= iterations <= 2:
        raise StudyExclusion("whole fixtures require j0..2")
    source = assemble_case(
        problem, method, regime, iterations=iterations, seed=seed, executable=executable
    )
    restoring = "clean_tree" if policy == "throwaway_tree" else policy
    blocks = {}
    target = source.metadata["backend_metadata"]["output_qubits"][0]
    if method.startswith("sb_") or method.startswith("structure_"):
        domain = "domain_free" if regime == "R3" else "complete"
        if method.startswith("sb_"):
            backend = baseline_components(problem, method[3:], domain_policy=domain)
            prefix_source = backend.initializer.compose(backend.compute)
        else:
            backend = structure_oracle(
                problem,
                domain_policy=domain,
                emission=method.removeprefix("structure_"),
            )
            prefix_source = backend.compute
        physical = backend.circuit.num_qubits
        flags = backend.metadata["constraint_qubits"]
        if not flags:
            # Constant adapters' raw action, including false, is authoritative.
            raw, blocks["raw"] = lower_block(backend.circuit, restoring)
            peak = blocks["raw"]["scratch_capacity"]
        else:
            prefix, blocks["prefix"] = lower_block(prefix_source, policy, mirrored=True)
            mark_source = QuantumCircuit(physical)
            mark_source.mcx(flags, target)
            mark, blocks["conjunction"] = lower_block(mark_source, restoring)
            ps = list(range(physical, prefix.num_qubits))
            ms = list(
                range(prefix.num_qubits, prefix.num_qubits + mark.num_qubits - physical)
            )
            raw = QuantumCircuit(prefix.num_qubits + len(ms))
            raw.compose(prefix, [*range(physical), *ps], inplace=True)
            raw.compose(mark, [*range(physical), *ms], inplace=True)
            raw.compose(_inverse(prefix), [*range(physical), *ps], inplace=True)
            blocks["prefix"]["scratch_qubits"] = ps
            blocks["conjunction"]["scratch_qubits"] = ms
            peak = max(
                blocks["prefix"]["scratch_capacity"],
                blocks["prefix"]["held_scratch"]
                + blocks["conjunction"]["scratch_capacity"],
            )
        oracle = QuantumCircuit(raw.num_qubits)
        oracle.x(target)
        oracle.h(target)
        oracle.compose(raw, inplace=True)
        oracle.h(target)
        oracle.x(target)
        wrapper = "lowered_prefix_restoring_conjunction_actual_prefix_inverse_kickback"
    else:
        physical = source.raw.num_qubits
        raw, blocks["raw"] = lower_block(source.raw, policy, mirrored=True)
        oracle = raw.copy()
        oracle.z(target)
        oracle.compose(_inverse(raw), inplace=True)
        peak = blocks["raw"]["scratch_capacity"]
        wrapper = "lowered_monomial_raw_Z_actual_expanded_inverse"
    a, blocks["preparation"] = lower_block(source.preparation, restoring)
    zero = QuantumCircuit(n, global_phase=math.pi)
    zero.x(range(n))
    if n == 1:
        zero.z(0)
    else:
        zero.h(n - 1)
        zero.mcx(list(range(n - 1)), n - 1)
        zero.h(n - 1)
    zero.x(range(n))
    z, blocks["zero_reflection"] = lower_block(zero, restoring)
    a_count, z_count = a.num_qubits - n, z.num_qubits - n
    diffusion = QuantumCircuit(n + a_count + z_count)
    diffusion.compose(_inverse(a), range(a.num_qubits), inplace=True)
    diffusion.compose(
        z, [*range(n), *range(a.num_qubits, diffusion.num_qubits)], inplace=True
    )
    diffusion.compose(a, range(a.num_qubits), inplace=True)
    data = source.metadata["data_qubits"]
    a_pool = list(range(raw.num_qubits, raw.num_qubits + a_count))
    z_pool = list(range(raw.num_qubits + a_count, raw.num_qubits + a_count + z_count))
    search = QuantumCircuit(raw.num_qubits + a_count + z_count)
    search.compose(a, [*data, *a_pool], inplace=True)
    for _ in range(iterations):
        search.compose(oracle, range(oracle.num_qubits), inplace=True)
        search.compose(diffusion, [*data, *a_pool, *z_pool], inplace=True)
    peaks = {
        "raw": peak,
        "oracle": peak,
        "preparation": blocks["preparation"]["scratch_capacity"],
        "zero_reflection": blocks["zero_reflection"]["scratch_capacity"],
    }
    peaks["diffusion"] = max(peaks["preparation"], peaks["zero_reflection"])
    peaks["search"] = (
        max(peaks["oracle"], peaks["diffusion"], peaks["preparation"])
        if iterations
        else peaks["preparation"]
    )
    return MCXStudyCase(
        {
            "raw": raw,
            "preparation": a,
            "zero_reflection": z,
            "oracle": oracle,
            "diffusion": diffusion,
            "search": search,
        },
        {
            "method": method,
            "regime": regime,
            "policy": policy,
            "seed": seed,
            "iterations": iterations,
            "data_qubits": data,
            "backend_width": physical,
            "source_validation": source.metadata["validation"],
            "wrapper": wrapper,
            "restoring_policy": restoring,
            "blocks": blocks,
            "peak_mcx_scratch_capacity": peaks,
            "scratch_ownership": {
                "oracle": list(range(physical, raw.num_qubits)),
                "preparation": a_pool,
                "zero_reflection": z_pool,
            },
            "search_embeddings": {
                "oracle": list(range(oracle.num_qubits)),
                "preparation": [*data, *a_pool],
                "diffusion": [*data, *a_pool, *z_pool],
            },
            "scratch_scope": "MCX construction capacity including borrowed wires; held prefix plus marking; sequential components use maximum, not sum; backend live workspace unavailable",
            "raw_contract": "native throwaway raw may retain garbage; only oracle/search restores it; backend raw retains original contract",
            "restoration": "zero initial clean/throwaway pools; arbitrary borrowed dirty states; actual expanded inverses; requires independent template and service validation",
            "metric_level": "explicit_mcx_resolved_standard_gates",
            "unsupported": {
                "routed": "not executed; no target/calibration identity",
                "full_ft": "arbitrary rotations unsynthesized; no precision certificate",
                "optimized_live_workspace": "unavailable",
            },
        },
    )


def component_costs(circuit: QuantumCircuit, *, seed: int = 7) -> tuple[dict, dict]:
    """Return explicit/common/partial-FT metrics and their actual circuits.

    T-depth follows dependencies of emitted gates. Residual rotations are
    unpriced; measurements and free AND uncomputation never enter this model.
    """
    from .metrics import circuit_metrics, lower_circuit

    common = lower_circuit(
        circuit, basis_gates=["u", "cx"], seed=seed, optimization_level=0
    )
    ft = costs.clifford_t(circuit)
    ft_row = costs.ft_metrics(ft)
    ft_row.update(
        metric_level="clifford_t_plus_unsynthesized_rz",
        total_t_count=None,
        total_t_depth=None,
        precision=None,
    )
    return {
        "explicit": {
            **circuit_metrics(circuit),
            "metric_level": "explicit_mcx_resolved_standard_gates",
        },
        "common": {
            **circuit_metrics(common),
            "metric_level": "unrouted_u_cx_optimization0",
            "seed": seed,
        },
        "partial_ft": ft_row,
        "routed": {"status": "not_executed", "cost": None},
    }, {"explicit": circuit, "common": common, "partial_ft": ft}


def analytical_dutta_rows() -> list[dict]:
    """Separate theorem-only tradeoffs; no circuit/static measurement claim."""
    rows = []
    for n in range(3, 21):
        for m1 in (2, 3, 4):
            try:
                row = costs.dutta_mcx_costs(n, m1)
            except ValueError as error:
                row = {
                    "controls": n,
                    "m1": m1,
                    "status": "excluded",
                    "reason": str(error),
                }
            else:
                row.update(
                    status="analytical_only",
                    m1=m1,
                    published_t_count=row.pop("t_count"),
                    published_t_depth=row.pop("t_depth"),
                    static_unitary_t_count=None,
                    static_unitary_t_depth=None,
                    scope="Theorem 1 Toffoli tradeoff only; no emitted circuit, phase/restoration test or static measurement-free T certificate; published depth discrepancy retained in costs.py",
                )
            rows.append(row)
    return rows
