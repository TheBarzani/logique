"""Bounded diagnostic of pinned level APIs; no production certificate or simulator."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import time
from collections.abc import Iterable

from qiskit import QuantumCircuit

import logique.circuits.records as records
import logique.synthesis.result as result_module
from level_value import validate_level_response


def expected(case: str, bits: tuple[int, ...]) -> list[int]:
    """Independent functions of deliberately positional b,a,c,unused inputs."""
    b, a, c, _ = bits
    return {
        "asymmetric": [a & (1 - b)],
        "equal": [a ^ b ^ c],
        "opposite": [0],
        "shared": [a & b & c, a & b & (1 - c)],
        "overlap": [(a ^ b) & c, (b ^ c) & a],
        "alias": [1 - b, b, 0, 1],
        "zero_output": [],
        "zero": [0],
        "xor": [a ^ c],
    }[case]


def apply_rows(rows: Iterable[dict], bits: list[int]) -> None:
    for row in rows:
        assert row["kind"] == "x"
        controls, target = row["controls"], row["target"]
        assert len(controls) == len(set(controls))
        assert target not in controls
        assert len(controls) == len(row["polarity"])
        if all(bits[q] == p for q, p in zip(controls, row["polarity"])):
            bits[target] ^= 1


def apply_circuit(circuit: QuantumCircuit, bits: list[int]) -> int:
    """Interpret actual wrapper instructions independently, including Z signs."""
    phase = 1
    for inst in circuit.data:
        op = inst.operation
        qs = [circuit.find_bit(q).index for q in inst.qubits]
        count = getattr(op, "num_ctrl_qubits", 0)
        base = op.base_gate if count else op
        assert base.name in ("x", "z")
        assert len(qs) == len(set(qs))
        state = getattr(op, "ctrl_state", 0)
        if all(bits[q] == ((state >> i) & 1) for i, q in enumerate(qs[:count])):
            if base.name == "x":
                bits[qs[-1]] ^= 1
            elif bits[qs[-1]]:
                phase *= -1
    return phase


def validate(data: dict, case: str) -> dict:
    assert data["diagnostic_only"] is True
    certificate = validate_level_response(data)
    width = data["num_qubits"]
    inputs, outputs = data["input_qubits"], data["output_qubits"]
    # Before scalar arrays or wrapper construction, recheck the diagnostic caps.
    assert len(inputs) == 4 and len(outputs) <= 16 and width <= 128
    assert len(data["network"]["nodes"]) <= 64 and len(data["steps"]) <= 128
    assert len(set(inputs)) == len(inputs) and len(set(outputs)) == len(outputs)
    raw = records.records_to_qiskit(data["gates"], width)
    result = result_module.SynthesisResult(raw, data)
    oracle = result.oracle()
    phases = [result.phase_oracle(output=j) for j in range(len(outputs))]
    columns = 0
    for x in itertools.product((0, 1), repeat=4):
        if "source_program" in data:
            program = data["source_program"]
            signals = list(x)
            for op in program["operations"]:
                left, right = signals[op["lhs"]], signals[op["rhs"]]
                right ^= op["negate_rhs"]
                signals.append(left & right if op["kind"] == "and" else left ^ right)
            values = [signals[i] ^ sign for i, sign in program["outputs"]]
        else:
            values = expected(case, x)
        initial = [0] * width
        for q, bit in zip(inputs, x):
            initial[q] = bit
        raw_bits = initial.copy()
        apply_rows(data["gates"], raw_bits)
        assert [raw_bits[q] for q in outputs] == values
        assert not any(
            raw_bits[q] for q in range(width) if q not in set(inputs + outputs)
        )
        apply_rows(reversed(data["gates"]), raw_bits)
        assert raw_bits == initial
        for targets in itertools.product((0, 1), repeat=len(outputs)):
            bits = initial + list(targets)
            assert apply_circuit(oracle, bits) == 1
            assert bits == initial + [t ^ y for t, y in zip(targets, values)]
            columns += 1
        for j, circuit in enumerate(phases):
            bits = initial.copy()
            assert apply_circuit(circuit, bits) == (-1 if values[j] else 1)
            assert bits == initial
            columns += 1
    return {
        "wrapper_columns": columns,
        "width": width,
        "gates": len(data["gates"]),
        "value_certificate": certificate,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[5] / "src"
    for module in (records, result_module):
        assert Path(module.__file__).resolve().is_relative_to(source)
    args.evidence.mkdir(exist_ok=False)
    observations = []
    cases = (
        "asymmetric",
        "equal",
        "opposite",
        "shared",
        "overlap",
        "alias",
        "zero_output",
        "zero",
        "xor",
    ) + tuple(f"generated-{i}" for i in range(8))
    for strategy in ("fast", "depth"):
        requests = [(case, []) for case in cases]
        requests += [
            ("above_cap", []),
            ("shared", ["4"]),
            ("shared", ["0"]),
            ("shared", ["1.0"]),
        ]
        for index, (case, extra) in enumerate(requests):
            label = f"{strategy}-{index:02d}-{case}"
            command = [str(args.executable.resolve()), strategy, case, *extra]
            start = time.monotonic()
            proc = subprocess.run(command, capture_output=True, timeout=5)
            elapsed = time.monotonic() - start
            (args.evidence / f"{label}.stdout").write_bytes(proc.stdout)
            (args.evidence / f"{label}.stderr").write_bytes(proc.stderr)
            row = dict(
                command=command,
                exit=proc.returncode,
                seconds=elapsed,
                child_rss=None,
                source_case=case,
                strategy=strategy,
            )
            if case == "above_cap" or extra:
                assert proc.returncode == 1 and not proc.stdout
                row["status"] = "expected_rejection"
            else:
                assert proc.returncode == 0, proc.stderr.decode()
                try:
                    row.update(validate(json.loads(proc.stdout), case))
                    row["status"] = "bounded_columns_pass"
                except (AssertionError, ValueError) as error:
                    row["status"] = "semantic_block"
                    row["error"] = repr(error)
            observations.append(row)
            (args.evidence / f"{label}.receipt.json").write_text(
                json.dumps(row, indent=2)
            )
    inventory = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in args.evidence.iterdir()
        if p.is_file()
    }
    summary = {
        "observations": observations,
        "inventory": inventory,
        "scientific_admission": False,
        "seed": None,
    }
    (args.evidence / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if any(row["status"] == "semantic_block" for row in observations):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
