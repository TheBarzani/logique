"""Independent check of the MCX controls study range (3..20) and per-policy costs.

Writes one JSON file. Does not use Codex's run_mcx_study.py (hard-coded paths).
Usage: uv run --no-sync python tools/chia_mcx_controls_check.py OUT.json
"""

import json
import random
import sys

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from logique.benchmarks import costs, mcx_study as s

SEED = 7
CORRECTNESS_CONTROLS = (3, 4, 5)


def range_check() -> dict:
    out = {}
    for n in (0, 1, 2, 3, 20, 21, 25):
        try:
            est = s.construction_estimate("noaux_v24", n)
            out[str(n)] = "accepted:" + est["status"]
        except s.StudyExclusion as error:
            out[str(n)] = f"rejected:{error}"
    for bad in (3.0, True, "4"):
        try:
            s.construction_estimate("noaux_v24", bad)
            out[repr(bad)] = "accepted"
        except s.StudyExclusion:
            out[repr(bad)] = "rejected"
    return out


def basis_index(bits: dict[int, int]) -> int:
    return sum(v << q for q, v in bits.items())


def functional(method: str, n: int) -> dict:
    """Brute-force: lowered circuit acts as MCX on all control/target inputs."""
    rng = random.Random(SEED)
    source = QuantumCircuit(2 * n - 1)
    source.mcx(list(range(n)), n)
    lowered, info = costs.decompose_mcx(source, method)
    width = lowered.num_qubits
    spare = list(range(n + 1, 2 * n - 1))
    fails = 0
    cases = 0
    for pattern in range(1 << (n + 1)):
        for spare_bits in (0, rng.getrandbits(len(spare))):
            bits = {q: (pattern >> q) & 1 for q in range(n + 1)}
            for i, q in enumerate(spare):
                bits[q] = (spare_bits >> i) & 1
            sv = Statevector.from_int(basis_index(bits), 2**width).evolve(lowered)
            probs = np.abs(sv.data) ** 2
            top = int(np.argmax(probs))
            expect = dict(bits)
            if all(bits[q] for q in range(n)):
                expect[n] ^= 1
            if method == "throwaway_tree":
                mask = (1 << (n + 1)) - 1  # only controls+target are specified
                ok = probs[top] > 1 - 1e-9 and (top & mask) == basis_index(
                    {q: expect[q] for q in range(n + 1)}
                )
            else:
                ok = probs[top] > 1 - 1e-9 and top == basis_index(expect)
            fails += not ok
            cases += 1
    return {"method": method, "controls": n, "cases": cases, "failures": fails,
            "width": width}


def main(out_path: str) -> int:
    result = {"range_check": range_check(), "costs": [], "functional": [], "gray": []}
    for method in sorted(costs.MCX_DECOMPOSITIONS):
        for n in range(3, 21):
            est = s.construction_estimate(method, n)
            if est["status"] == "excluded":
                result["gray"].append({"controls": n, "ops_bound": est[
                    "phase_cx_operations_upper_bound"]})
                continue
            try:
                row = costs.isolated_mcx_costs(method, n)
            except Exception as error:  # record, never hide
                row = {"method": method, "controls": n,
                       "error": f"{type(error).__name__}: {error}"}
            result["costs"].append(row)
        for n in CORRECTNESS_CONTROLS:
            result["functional"].append(functional(method, n))
    result["seed"] = SEED
    with open(out_path, "w") as handle:
        json.dump(result, handle, indent=1, default=str)
    bad = [f for f in result["functional"] if f["failures"]]
    errs = [c for c in result["costs"] if "error" in c]
    print(json.dumps({"cost_rows": len(result["costs"]), "cost_errors": len(errs),
                      "functional_rows": len(result["functional"]),
                      "functional_failing": len(bad),
                      "range": result["range_check"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
