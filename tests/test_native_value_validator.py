"""Capped production cone validation, real bridge responses and emitted wrappers.

No dense quantum arrays. Table axes are input/target assignments, not raw width.
"""

import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from logique.synthesis import synthesize
from tests.test_native_mapping_strategies import check_action, write_source


@pytest.mark.integration
def test_compiled_value_and_domain_mutations():
    path = Path(os.environ["LOGIQUE_NATIVE_VALUE_PROBE"])
    result = subprocess.run([str(path)], text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["cones"]["frontier_pairs"] == 1024
    assert report["cones"]["variants"] == 1369
    assert report["cones"]["classes"] == {
        "empty": 63,
        "equal": 31,
        "included": 360,
        "incomparable": 570,
    }
    assert report["cones"]["stale_unread_aliases"] > 0
    assert report["negatives"]["rejections"] == 9
    assert report["domain"]["domain_rejections"] == 8
    assert report["domain"]["emission_mutations"] == 6


CASES = {
    "equal": (
        "wire p,q,l,r; assign p=a^b; assign q=b^c; "
        "assign l=p^c; assign r=a^q; assign y=l&r;",
        lambda a, b, c: [a ^ b ^ c],
    ),
    "opposite": (
        "wire p,q,l,r; assign p=a^b; assign q=b^c; "
        "assign l=p^c; assign r=a^q; assign y=l&~r;",
        lambda a, b, c: [np.zeros(8, dtype=bool)],
    ),
    "included": (
        "wire p,q; assign p=a^b; assign q=p^c; assign y=p&q;",
        lambda a, b, c: [(a ^ b) & (a ^ b ^ c)],
    ),
    "incomparable": (
        "wire p,q; assign p=a^b; assign q=b^c; assign y=p&q;",
        lambda a, b, c: [(a ^ b) & (b ^ c)],
    ),
    "singleton": (
        "wire p; assign p=a^b; assign y=p&a;",
        lambda a, b, c: [(a ^ b) & a],
    ),
    "empty": (
        "wire p,q,r,s,t; assign p=a^b; assign q=b^c; "
        "assign r=p^q; assign s=a^c; assign t=r^s; assign y=t&a;",
        lambda a, b, c: [np.zeros(8, dtype=bool)],
    ),
    "dirty_cleanup": (
        "wire p,q; assign p=a&b; assign q=p^c; assign y=q&a;",
        lambda a, b, c: [((a & b) ^ c) & a],
    ),
    "boundary": (
        "wire p; assign p=a^b; assign y=~p; assign z=p^c; assign w=z&a;",
        lambda a, b, c: [~(a ^ b), a ^ b ^ c, (a ^ b ^ c) & a],
    ),
    "outputs": (
        "assign y=~a; assign z=a; assign w=1'b0; assign v=1'b1;",
        lambda a, b, c: [~a, a, np.zeros(8, dtype=bool), np.ones(8, dtype=bool)],
    ),
}


@pytest.mark.integration
@pytest.mark.parametrize("policy", ["none", "refactoring"])
@pytest.mark.parametrize("case", CASES)
def test_real_capped_mapping_and_wrappers(tmp_path, policy, case):
    # <=3 input bits, <=4 joint target bits: at most 128 scalar columns.
    from logique.verification.classical import input_assignments

    text, evaluate = CASES[case]
    names = "y,z,w,v" if case == "outputs" else "y,z,w" if case == "boundary" else "y"
    path = write_source(tmp_path, "b,a,c", names, text)
    result = synthesize(path, "xag_bennett", strategy="xag_low_t", preprocessing=policy)
    b, a, c = input_assignments(3)
    check_action(result, np.array(evaluate(a, b, c)))
    certificate = result.metadata["xag_value_validation"]
    assert certificate["policy"] == "canonical_sequential_two_cone_truth_tables_v1"
    assert certificate["assignments"] == 8
    assert certificate["caps"] == {
        "inputs": 6,
        "nodes": 256,
        "width": 256,
        "steps": 4096,
    }
    assert certificate["width"] == result.metadata["num_qubits"]
    assert certificate["steps"] == len(result.metadata["steps"])
    if case == "dirty_cleanup" and policy == "none":
        assert certificate["zero_releases"] > 0


@pytest.mark.integration
def test_real_above_input_cap_is_explicitly_unsupported(tmp_path):
    path = write_source(tmp_path, "a,b,c,d,e,f,g", "y", "assign y=a&b;")
    with pytest.raises(RuntimeError, match="unsupported: inputs exceed 6"):
        synthesize(path, "xag_bennett", strategy="xag_low_t", preprocessing="none")
    # The capped validator is exclusive to the explicitly requested mapping.
    result = synthesize(path, "xag_bennett", preprocessing="none")
    assert "xag_value_validation" not in result.metadata
