"""Bounded research preprocessing with independently checked ordered boundaries.

The standalone balancer proves each pass by SAT. This adapter additionally checks
its exported networks exhaustively through ten positional inputs, including every
serialization boundary. Larger CEC/compositional evidence is a separate task.
"""

from collections.abc import Sequence
from copy import deepcopy
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import subprocess
import tempfile
import time

from logique.paths import native_executable
from .balancing import BALANCING_PASSES, optimize_verilog

RESEARCH_PROFILES = ("mc_reduction", "cut_esop_balancing")


class UnsupportedOptimizationProfile(RuntimeError):
    """A requested profile cannot meet the required equivalence contract."""


def retain_profile_failure(
    error: Exception,
    profile: dict,
    boundary: str,
    *,
    request: dict | None = None,
    mapping_metadata: dict | None = None,
) -> None:
    """Attach completed evidence without replacing the original raised exception.

    Nested handlers retain the innermost boundary and every context. Existing
    payloads survive verbatim in a separate snapshot if they conflict with the
    completed profile; additive fields and nested evidence are merged as well.
    """
    previous = getattr(error, "profile_evidence", None)
    evidence = deepcopy(profile)

    def merge(target, extra):
        for key, value in extra.items():
            if key not in target:
                target[key] = deepcopy(value)
            elif isinstance(target[key], dict) and isinstance(value, dict):
                merge(target[key], value)

    if isinstance(previous, dict):
        merge(evidence, previous)
        # Keep completed passes authoritative without discarding richer failures.
        if any(
            key in profile and profile[key] != value for key, value in previous.items()
        ):
            evidence["existing_profile_evidence"] = deepcopy(previous)
    elif previous is not None:
        evidence["existing_profile_evidence"] = deepcopy(previous)
    evidence.update(
        status="failed",
        failure=f"{type(error).__name__}: {error}",
    )
    evidence.setdefault("failed_boundary", boundary)
    evidence.setdefault(
        "original_exception", {"type": type(error).__name__, "reason": str(error)}
    )
    contexts = evidence.setdefault("failure_contexts", [])
    contexts.append({"boundary": boundary, "request": deepcopy(request)})
    if request is not None:
        evidence.setdefault("mapping_request", deepcopy(request))
    if mapping_metadata is not None:
        networks = evidence.setdefault("mapping_networks", {})
        for name in ("source_network", "network"):
            if name in mapping_metadata:
                networks.setdefault(name, deepcopy(mapping_metadata[name]))
    error.profile_evidence = evidence


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _truth_signature(graph: dict, max_inputs: int, max_nodes: int) -> tuple:
    """Evaluate every assignment with scalar integer truth vectors, no simulator."""
    inputs, nodes = graph["inputs"], graph["nodes"]
    if len(inputs) > max_inputs or len(nodes) > max_nodes:
        raise UnsupportedOptimizationProfile(
            f"Independent exhaustive CEC cap: inputs<={max_inputs}, nodes<={max_nodes}"
        )
    count = 1 << len(inputs)
    mask = (1 << count) - 1
    values = {
        node: sum(((assignment >> i) & 1) << assignment for assignment in range(count))
        for i, node in enumerate(inputs)
    }
    for node in nodes:
        kind = node["kind"]
        if kind == "input":
            if node["id"] not in values:
                raise RuntimeError("Network has an unordered primary input")
            continue
        if kind == "constant":
            values[node["id"]] = mask if node["value"] else 0
            continue
        fanins = node["fanins"]
        if len(fanins) > 6:
            raise UnsupportedOptimizationProfile("Independent CEC fanin cap is six")
        signals = [values[f["node"]] ^ (mask if f["inverted"] else 0) for f in fanins]
        truth = int(node["truth"], 2)
        value = 0
        for assignment in range(count):
            index = sum(
                ((signal >> assignment) & 1) << i for i, signal in enumerate(signals)
            )
            value |= ((truth >> index) & 1) << assignment
        values[node["id"]] = value
    return len(inputs), tuple(
        values[out["node"]] ^ (mask if out["inverted"] else 0)
        for out in graph["outputs"]
    )


def preprocess_verilog(
    source: str | Path,
    profile: str,
    *,
    executable: str | Path | None = None,
    balancer_executable: str | Path | None = None,
    timeout: float = 120,
    max_inputs: int = 10,
    max_nodes: int = 4096,
) -> dict:
    """Apply an explicit shared profile before representation conversion.

    Failure, unknown SAT, timeout, changed arity/order/polarity and an input above
    the independent exhaustive cap never produce a successful profile. The MC
    binding is deliberately unsupported: it hides intermediate refactoring and
    cut-rewrite boundaries, so certifying only its final output is insufficient.
    Returned Verilog/networks retain all evidence needed to save a replay artifact.
    """
    if profile not in RESEARCH_PROFILES:
        raise ValueError(f"profile must be one of {RESEARCH_PROFILES}")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or not 0 < timeout <= 120
    ):
        raise ValueError("timeout must be finite, positive and at most 120 seconds")
    if type(max_inputs) is not int or not 0 <= max_inputs <= 10:
        raise ValueError("max_inputs must be an integer in 0..10")
    if type(max_nodes) is not int or not 1 <= max_nodes <= 4096:
        raise ValueError("max_nodes must be an integer in 1..4096")
    source = Path(source).resolve()
    if source.suffix != ".v" or not source.is_file():
        raise ValueError("research profiles require an existing Verilog .v file")
    if profile == "mc_reduction":
        try:
            from tweedledum import classical

            installed_version = version("tweedledum")
        except (ImportError, PackageNotFoundError) as error:
            raise UnsupportedOptimizationProfile(
                f"MC binding unavailable: {type(error).__name__}: {error}"
            ) from error
        binding = getattr(classical, "optimize", None)
        raise UnsupportedOptimizationProfile(
            f"tweedledum {installed_version} classical.optimize available={callable(binding)}: "
            "opaque constant/dont-care/refactoring/cut-rewrite(xag_minmc) flow; "
            "no separately callable intermediate passes for mandatory per-pass CEC. "
            "Refactoring alone is not MC reduction."
        )
    started = time.monotonic()
    tool = native_executable(executable)

    def remaining() -> float:
        seconds = timeout - (time.monotonic() - started)
        if seconds <= 0:
            raise TimeoutError("Research preprocessing cumulative timeout")
        return seconds

    def read_network(path: Path) -> tuple[dict, tuple]:
        proc = subprocess.run(
            [str(tool)],
            input=json.dumps(
                {"path": str(path), "method": "xag", "preprocessing": "none"}
            ),
            capture_output=True,
            text=True,
            timeout=remaining(),
        )
        if proc.returncode:
            raise RuntimeError(f"Profile network export failed: {proc.stderr.strip()}")
        graph = json.loads(proc.stdout)["source_network"]
        # Check caps before allocating truth vectors.
        signature = _truth_signature(graph, max_inputs, max_nodes)
        return graph, signature

    original = source.read_bytes()
    before = None
    passes = []
    current = source
    try:
        before, expected = read_network(source)
        with tempfile.TemporaryDirectory(prefix="logique-profile-") as directory:
            for i, name in enumerate(BALANCING_PASSES):
                result = optimize_verilog(
                    current, [name], executable=balancer_executable, timeout=remaining()
                )
                text = result["verilog"]
                path = Path(directory) / f"pass-{i}.v"
                path.write_text(text)
                stage = {**result, "independent_equivalence": {"status": "pending"}}
                passes.append(stage)
                graph, actual = read_network(path)
                stage["exported_network"] = graph
                if actual != expected:
                    raise RuntimeError(
                        f"Independent ordered equivalence failed after {name}"
                    )
                stage["independent_equivalence"] = {
                    "status": "exhaustive",
                    "inputs": expected[0],
                    "assignments": 1 << expected[0],
                }
                current = path
            # A separate final serialization read is deliberately checked as well.
            final = Path(directory) / "serialized.v"
            final.write_text(passes[-1]["verilog"])
            after, actual = read_network(final)
            if actual != expected:
                raise RuntimeError("Independent final serialization equivalence failed")
        return {
            "profile": profile,
            "status": "applied",
            "implementation": "standalone mockturtle xag_balance; xag_algebraic_depth_rewriting; esop_balancing",
            "passes": passes,
            "verilog": passes[-1]["verilog"],
            "source_verilog": original.decode(),
            "source_sha256": _sha(original),
            "optimized_sha256": _sha(passes[-1]["verilog"].encode()),
            "before_network": before,
            "after_network": after,
            "independent_equivalence": {
                "status": "exhaustive",
                "inputs": expected[0],
                "assignments": 1 << expected[0],
                "serialization": True,
            },
            "native": {"executable": str(tool), "sha256": _sha(tool.read_bytes())},
            "seconds": time.monotonic() - started,
            "caps": {"inputs": max_inputs, "nodes": max_nodes, "seconds": timeout},
        }
    except Exception as error:
        # Preserve serialized intermediates even after TemporaryDirectory cleanup.
        # Study runners save this payload with the failed case, without cost rows.
        evidence = {
            "profile": profile,
            "status": "failed",
            "source_verilog": original.decode(),
            "source_sha256": _sha(original),
            "before_network": before,
            "passes": passes,
            "failure": f"{type(error).__name__}: {error}",
            "seconds": time.monotonic() - started,
        }
        retain_profile_failure(error, evidence, "preprocessing")
        raise


def verify_profile_mapping(
    profile: dict, metadata: dict, outputs: Sequence[int] | None = None
) -> dict:
    """Check final parser serialization and representation conversion independently."""
    boundary = "mapping_reference_signature"
    try:
        caps = profile["caps"]
        n, values = _truth_signature(
            profile["before_network"], caps["inputs"], caps["nodes"]
        )
        boundary = "mapping_output_signature"
        order = list(range(len(values))) if outputs is None else list(outputs)
        expected = n, tuple(values[i] for i in order)
        for name in ("source_network", "network"):
            boundary = f"mapping_signature:{name}"
            actual = _truth_signature(metadata[name], caps["inputs"], caps["nodes"])
            if actual != expected:
                raise RuntimeError(
                    f"Independent profile mapping equivalence failed at {name}"
                )
        return {
            "status": "exhaustive",
            "inputs": n,
            "assignments": 1 << n,
            "output_order": order,
            "boundaries": ["source_network", "network"],
        }
    except Exception as error:
        retain_profile_failure(error, profile, boundary, mapping_metadata=metadata)
        raise
