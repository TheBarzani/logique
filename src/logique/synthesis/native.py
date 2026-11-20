"""Explicit build and JSON process boundary for the pinned native bridge."""

import json
from pathlib import Path
import subprocess
from logique.paths import native_executable

REFERENCE_REVISION = "4c6f766cd0ffc62d37ab45edfe80c9f1eae44764"
METHODS = ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")


def build_native(
    source: str | Path, *, build: str | Path | None = None, jobs: int = 2
) -> Path:
    """Build explicitly using local C++ sources or the pinned download fallback."""
    source = Path(source).resolve()
    build = Path(build).resolve() if build else source / "build"
    if jobs < 1:
        raise ValueError("jobs must be positive")
    subprocess.run(
        ["cmake", "-S", str(source), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(build), "-j", str(jobs)], check=True)
    return build / "boolean_synthesis"


def run_native(path: str | Path, method: str, *, executable=None, **parameters) -> dict:
    """Read one response; surface native diagnostics without losing context."""
    timeout = 180
    if parameters.get("strategy") == "sat_pebbling":
        _sat_controls(parameters)
        # The pinned solver ignores its timeout argument. Enforce a process
        # boundary too, including parsing/output work, with one second grace.
        timeout = parameters["sat_time_seconds"] + 1
    elif any(key in parameters for key in SAT_LIMITS):
        raise ValueError("SAT budgets require strategy='sat_pebbling'")
    request = {"path": str(Path(path).resolve()), "method": method, **parameters}
    proc = subprocess.run(
        [str(native_executable(executable))],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(f"Native synthesis failed ({method}): {proc.stderr.strip()}")
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Native synthesis returned invalid JSON") from error
    if not isinstance(response, dict) or "network" not in response:
        raise RuntimeError("Native synthesis returned an invalid response")
    if "preprocessing" in parameters:
        evidence = response.get("preprocessing")
        if (
            not isinstance(evidence, dict)
            or evidence.get("common") is not True
            or evidence.get("policy") != parameters["preprocessing"]
            or not isinstance(evidence.get("before_network"), dict)
            or not isinstance(evidence.get("after_network"), dict)
        ):
            raise RuntimeError(
                "Native bridge did not confirm the requested common preprocessing"
            )
    if "strategy" in parameters:
        evidence = response.get("mapping_strategy")
        implementations = {
            "bennett": "caterpillar::bennett_mapping_strategy",
            "bennett_inplace": "caterpillar::bennett_inplace_mapping_strategy",
            "eager": "caterpillar::eager_mapping_strategy",
            "sat_pebbling": "logique::bounded_sat_pebbling",
            "xag_low_t": "caterpillar::xag_mapping_strategy",
        }
        if (
            not isinstance(evidence, dict)
            or evidence.get("explicit") is not True
            or evidence.get("name") != parameters["strategy"]
            or evidence.get("implementation")
            != implementations.get(parameters["strategy"])
            or not isinstance(response.get("steps"), list)
        ):
            raise RuntimeError("Native bridge did not confirm the requested strategy")
    if parameters.get("strategy") == "xag_low_t":
        audit = response.get("xag_schedule_audit")
        if (
            not isinstance(response.get("physical_control_normalization"), list)
            or not isinstance(audit, dict)
            or audit.get("policy") != "pinned_lhrs_live_stacks_explicit_leaf_targets"
            or not isinstance(audit.get("actions"), list)
        ):
            raise RuntimeError("Native bridge did not confirm xag_low_t alias handling")
        _validate_xag_value_response(response)
    if parameters.get("strategy") == "sat_pebbling":
        audit = response.get("sat_validation", {})
        search = response.get("sat_search", {})
        width = response.get("num_qubits")
        if (
            not isinstance(audit, dict)
            or not isinstance(search, dict)
            or type(width) is not int
            or not 0 <= width <= parameters["qubit_budget"]
            or audit.get("qubit_budget") != parameters["qubit_budget"]
            or search.get("max_steps") != parameters["sat_max_steps"]
            or search.get("conflict_limit_per_solve")
            != parameters["sat_conflict_limit"]
            or search.get("search_seconds_between_calls")
            != parameters["sat_time_seconds"]
            or search.get("solver_wall_timeout_supported") is not False
        ):
            raise RuntimeError(
                "Native bridge did not confirm the requested SAT budgets"
            )
    return response


SAT_LIMITS = {
    "qubit_budget": 64,
    "sat_max_steps": 128,
    "sat_conflict_limit": 100000,
    "sat_time_seconds": 30,
}


def _sat_controls(parameters: dict) -> None:
    """Require explicit bounded SAT controls before launching a native process."""
    for name, cap in SAT_LIMITS.items():
        value = parameters.get(name)
        if type(value) is not int or not 1 <= value <= cap:
            raise ValueError(f"SAT requires integer {name} between 1 and {cap}")


XAG_VALUE_CAPS = {"inputs": 6, "nodes": 256, "width": 256, "steps": 4096}
XAG_VALUE_POLICY = "canonical_sequential_two_cone_truth_tables_v1"


def _validate_xag_value_response(response: dict) -> None:
    """Require the capped sequential value protocol before constructing a circuit.

    This checks the native certificate's structure and response consistency, not
    an unrestricted proof for arbitrary schedules. Internal stack aliases are
    addresses, never persistent Boolean values. All tables have <=64 bits.
    """

    def require(condition, message):
        if not condition:
            raise RuntimeError(f"Native xag_low_t value certificate: {message}")

    def integer(value, lower, upper):
        require(type(value) is int and lower <= value <= upper, "invalid integer")
        return value

    def array(value, cap):
        require(type(value) is list and len(value) <= cap, "invalid array/count")
        return value

    def row(value):
        require(type(value) is dict, "invalid object")
        return value

    cert = row(response.get("xag_value_validation"))
    require(cert.get("policy") == XAG_VALUE_POLICY, "unsupported policy")
    caps = row(cert.get("caps"))
    require(set(caps) == set(XAG_VALUE_CAPS), "unsupported caps")
    for name, cap in XAG_VALUE_CAPS.items():
        require(integer(caps[name], 0, cap) == cap, "unsupported caps")
    n, count, width, steps_count = (
        integer(cert.get(name), 0, cap) for name, cap in XAG_VALUE_CAPS.items()
    )
    require(count > n and width > 0, "invalid node/width counts")
    assignments = integer(cert.get("assignments"), 1, 64)
    require(assignments == 1 << n, "assignment count disagrees with inputs")
    require(integer(response.get("num_qubits"), 1, 256) == width, "width mismatch")
    network = row(response.get("network"))
    nodes = array(network.get("nodes"), 256)
    inputs = array(network.get("inputs"), 6)
    outputs = array(network.get("outputs"), 256)
    steps = array(response.get("steps"), 4096)
    require(len(nodes) == count and len(inputs) == n, "network counts mismatch")
    require(len(steps) == steps_count and outputs, "step/output counts mismatch")

    def node_id(value):
        return integer(value, 0, count - 1)

    def wire(value):
        return integer(value, 0, width - 1)

    def addresses(value, cap, validate, unique=False):
        result = [validate(v) for v in array(value, cap)]
        require(not unique or len(set(result)) == len(result), "duplicate address")
        return result

    require(
        addresses(inputs, 6, node_id, True) == list(range(1, n + 1)),
        "noncanonical input order",
    )
    iq = addresses(response.get("input_qubits"), 6, wire, True)
    oq = addresses(response.get("output_qubits"), 256, wire, True)
    require(iq == list(range(n)) and len(oq) == len(outputs), "I/O mismatch")
    by_id = {}
    for item in nodes:
        item = row(item)
        index = node_id(item.get("id"))
        require(index not in by_id, "duplicate node")
        by_id[index] = item
    require(set(by_id) == set(range(count)), "stored node IDs mismatch")
    mask = (1 << assignments) - 1

    def table(value):
        return integer(value, 0, mask)

    values = [table(v) for v in array(cert.get("node_values"), 256)]
    require(len(values) == count, "node table count mismatch")
    expected = [0] * count
    for i, index in enumerate(inputs):
        expected[index] = sum(((x >> i) & 1) << x for x in range(assignments))
    for index in range(count):
        item = by_id[index]
        kind = item.get("kind")
        fanins = array(item.get("fanins"), 2)
        if index == 0:
            require(kind == "constant" and item.get("value") is False, "constant")
            require(not fanins, "constant fanins")
        elif index <= n:
            require(kind == "input" and not fanins, "input node")
        else:
            require(kind in ("and", "xor") and len(fanins) == 2, "binary XAG")
            operands, children = [], []
            for f in fanins:
                f = row(f)
                child = integer(f.get("node"), 1, index - 1)
                sign = f.get("inverted")
                require(type(sign) is bool, "fanin polarity")
                require(kind != "xor" or not sign, "noncanonical XOR")
                children.append(child)
                operands.append(expected[child] ^ (mask if sign else 0))
            require(children[0] != children[1], "unsimplified fanins")
            require(
                item.get("truth") == ("1000" if kind == "and" else "0110"), "node truth"
            )
            a, b = operands
            expected[index] = a & b if kind == "and" else a ^ b
    require(values == expected, "node truth tables mismatch")
    drivers = set()
    for output in outputs:
        output = row(output)
        drivers.add(node_id(output.get("node")))
        require(type(output.get("inverted")) is bool, "output polarity")
    reachable = set(drivers)
    for index in reversed(range(count)):
        if index in reachable:
            reachable.update(f["node"] for f in by_id[index]["fanins"])
    require(all(index <= n or index in reachable for index in by_id), "unclean graph")

    audit = row(response.get("xag_schedule_audit"))
    require(
        audit.get("policy") == "pinned_lhrs_live_stacks_explicit_leaf_targets",
        "alias handling policy",
    )
    actions = array(audit.get("actions"), 4096)
    require(len(actions) == steps_count, "action count mismatch")
    stacks = array(audit.get("node_stacks"), 256)
    require(len(stacks) == count, "stack count mismatch")
    for stack in stacks:
        # Stale-but-unread aliases deliberately retain their addresses here.
        addresses(stack, 4097, wire)
    action_reads = 0
    central = []
    central_positions = []
    for position, (step, action) in enumerate(zip(steps, actions)):
        step, action = row(step), row(action)
        index = node_id(step.get("node"))
        label = step.get("action")
        require(
            label in ("compute", "uncompute", "compute_inplace", "buffer"),
            "action type",
        )
        require(
            all(key in action for key in step)
            and json.dumps({key: action[key] for key in step}, sort_keys=True)
            == json.dumps(step, sort_keys=True),
            "action/step mismatch",
        )
        target = wire(action.get("physical_target"))
        if label == "buffer":
            require(set(step) == {"node", "action", "target", "leaf"}, "buffer payload")
            require(
                set(action) == set(step) | {"physical_target"}, "buffer audit payload"
            )
            node_id(step.get("target"))
            node_id(step.get("leaf"))
            action_reads += 1
            continue
        require(step.get("cell_override") is None, "cell override")
        leaves = step.get("explicit_leaves")
        payload = {"node", "action", "explicit_leaves"}
        payload |= {"target_index"} if label == "compute_inplace" else {"cell_override"}
        if leaves is not None:
            payload.add("leaves")
        require(set(step) == payload, "action payload")
        physical_key = "physical_controls" if leaves is None else "physical_leaves"
        require(
            set(action) == payload | {"physical_target", physical_key},
            "action audit payload",
        )
        if leaves is None:
            require(label in ("compute", "uncompute"), "missing explicit leaves")
            controls = addresses(action.get("physical_controls"), 2, wire)
            require(len(controls) == 2 and target not in controls, "central controls")
            central.append((index, label == "uncompute"))
            central_positions.append(position)
            action_reads += 2 + (label == "uncompute")
        else:
            leaves = addresses(leaves, 256, node_id, True)
            # Redundant serialized indices need their own type checks: Python
            # equality alone admits True and 1.0 as aliases for node ID 1.
            serialized_leaves = addresses(step.get("leaves"), 256, node_id, True)
            require(serialized_leaves == leaves, "explicit leaves mismatch")
            physical = addresses(action.get("physical_leaves"), 256, wire)
            require(len(physical) == len(leaves), "physical leaves mismatch")
            require(
                physical.count(target) == (label == "compute_inplace"), "parity target"
            )
            if label == "compute_inplace":
                node_id(step.get("target_index"))
            action_reads += len(leaves) - (label == "compute_inplace")
    zero_releases = integer(cert.get("zero_releases"), 0, steps_count)
    require(
        zero_releases == sum(s["action"] == "uncompute" for s in steps),
        "release count mismatch",
    )
    blocks = array(cert.get("block_checks"), 4096)
    require(
        integer(cert.get("blocks"), 0, 4096) == len(blocks) == len(central),
        "block count mismatch",
    )
    expected_central = [
        (i, False)
        for i in range(n + 1, count)
        if by_id[i]["kind"] == "and" or i in drivers
    ]
    expected_central += [
        (i, True) for i, _ in reversed(expected_central) if i not in drivers
    ]
    require(central == expected_central, "noncanonical block order")
    active = set(inputs) | ({0} if 0 in drivers else set())
    boundary_reads = 0
    previous = None

    def boundary(entries, active_nodes):
        entries = array(entries, 256)
        seen, held, result = set(), set(), {}
        for entry in entries:
            entry = row(entry)
            index = node_id(entry.get("node"))
            q = wire(entry.get("wire"))
            require(index not in seen and q not in held, "boundary alias")
            seen.add(index)
            held.add(q)
            require(table(entry.get("value")) == values[index], "boundary value")
            generation = integer(entry.get("generation"), 0, steps_count)
            result[index] = (q, generation)
        require(seen == active_nodes, "boundary node count mismatch")
        return result

    cursor = 0
    for block, (index, undo), position in zip(blocks, central, central_positions):
        start = cursor
        cone_actions = steps[start:position]
        require(len(cone_actions) <= 2, "cone action count")
        cursor = position + 1 + len(cone_actions)
        require(cursor <= len(steps), "missing restoring actions")
        forward_roots = {s["node"]: s for s in cone_actions}
        prepared_addresses = {
            s["node"]: a["physical_target"]
            for s, a in zip(cone_actions, actions[start:position])
        }
        restored_addresses = {
            s["node"]: a["physical_target"]
            for s, a in zip(
                steps[position + 1 : cursor], actions[position + 1 : cursor]
            )
        }
        require(
            set(restored_addresses) == set(prepared_addresses),
            "restoring cone identity",
        )
        require(len(forward_roots) == len(cone_actions), "duplicate cone action")
        block = row(block)
        require(
            node_id(block.get("node")) == index
            and type(block.get("undo")) is bool
            and block["undo"] == undo,
            "block identity",
        )
        entry = boundary(block.get("entry"), active)
        require(previous is None or previous == entry, "discontinuous boundary")
        frames = array(block.get("frames"), 2)
        require(len(frames) == 2, "cone frame count")
        for frame in frames:
            frame = row(frame)
            root = node_id(frame.get("root"))
            q = wire(frame.get("wire"))
            expected_address = prepared_addresses.get(root)
            if root not in prepared_addresses:
                require(root in entry, "unprepared cone root")
                expected_address = entry[root][0]
            require(q == expected_address, "cone frame address mismatch")
            saved = table(frame.get("saved"))
            require(table(frame.get("prepared")) == values[root], "prepared cone value")
            require(
                ("restored_wire" in frame) == (root in forward_roots)
                and ("restored_value" in frame) == (root in forward_roots),
                "missing/unexpected restoration frame",
            )
            if "restored_wire" in frame or "restored_value" in frame:
                require(
                    wire(frame.get("restored_wire")) == restored_addresses[root],
                    "restored frame address mismatch",
                )
                require(table(frame.get("restored_value")) == saved, "cone restoration")
        require(
            [f["root"] for f in frames]
            and set(f["root"] for f in frames)
            == set(f["node"] for f in by_id[index]["fanins"]),
            "cone roots mismatch",
        )
        if undo:
            active.remove(index)
        else:
            active.add(index)
        previous = boundary(block.get("exit"), active)
        require(
            all(previous[k] == v for k, v in entry.items() if k != index),
            "boundary restoration",
        )
        boundary_reads += len(entry) + len(previous)
    require(cursor == len(steps), "unconsumed cone actions")
    # Each forward cone root is checked; an unchanged cone is also read to save
    # its frame. Cone actions occur symmetrically around each central action.
    require((steps_count - len(blocks)) % 2 == 0, "cone action count")
    null_cones = 2 * len(blocks) - (steps_count - len(blocks)) // 2
    require(null_cones >= 0, "cone count")
    reads = (
        action_reads
        + boundary_reads
        + 2 * len(blocks)
        + null_cones
        + len(active)
        + len(outputs)
    )
    require(
        integer(cert.get("operand_reads"), 0, 3000000) == reads,
        "operand read count mismatch",
    )

    gates = array(response.get("gates"), steps_count * 256 + 2 * len(outputs))
    wires = [0] * width
    for q, index in zip(iq, inputs):
        wires[q] = values[index]
    for gate in gates:
        gate = row(gate)
        require(gate.get("kind") == "x", "nonstatic gate")
        target = wire(gate.get("target"))
        controls = addresses(gate.get("controls"), 2, wire, True)
        signs = array(gate.get("polarity"), 2)
        require(
            len(signs) == len(controls) and all(type(s) is bool for s in signs),
            "gate polarity",
        )
        require(target not in controls, "gate target/control alias")
        condition = mask
        for q, sign in zip(controls, signs):
            condition &= wires[q] ^ (0 if sign else mask)
        wires[target] ^= condition
    for output, q in zip(outputs, oq):
        require(
            wires[q] == values[output["node"]] ^ (mask if output["inverted"] else 0),
            "emitted output value",
        )
    expected_wires = dict(zip(iq, (values[i] for i in inputs)))
    expected_wires.update(
        (q, values[o["node"]] ^ (mask if o["inverted"] else 0))
        for o, q in zip(outputs, oq)
    )
    require(
        all(value == expected_wires.get(q, 0) for q, value in enumerate(wires)),
        "emitted input/workspace restoration",
    )
    normalizations = array(response.get("physical_control_normalization"), steps_count)
    for event in normalizations:
        event = row(event)
        controls = addresses(event.get("controls"), 2, wire)
        signs = array(event.get("polarity"), 2)
        require(
            len(controls) == len(signs) == 2 and all(type(s) is bool for s in signs),
            "normalization polarity",
        )
        target = wire(event.get("target"))
        require(
            controls[0] == controls[1] and target not in controls, "normalization alias"
        )
        zero = signs[0] != signs[1]
        offset = integer(event.get("gate_offset"), 0, len(gates))
        require(
            event.get("rule")
            == ("zero_conjunction" if zero else "idempotent_literals"),
            "normalization rule",
        )
        require(
            integer(event.get("emitted_gate_count"), 0, 1) == (0 if zero else 1),
            "normalization count",
        )
        emitted = addresses(event.get("emitted_controls"), 1, wire)
        polarity = array(event.get("emitted_polarity"), 1)
        require(
            all(type(s) is bool for s in polarity), "normalization emitted polarity"
        )
        require(
            emitted == ([] if zero else controls[:1])
            and polarity == ([] if zero else signs[:1]),
            "normalization emission",
        )
        if not zero:
            require(
                offset < len(gates)
                and gates[offset]
                == dict(kind="x", controls=emitted, polarity=polarity, target=target),
                "normalization gate mismatch",
            )
