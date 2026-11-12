"""Private finite-domain value replay for actual pinned XAG level actions.

This is independent of the withheld sequential certificate implementation.
It accepts only static X/CNOT/Toffoli emission with low_tdepth_AND=False.
"""

from copy import deepcopy
import json


class LevelValueError(ValueError):
    """The private level-action contract could not be established."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LevelValueError(message)


def integer(value: object, maximum: int, minimum: int = 0) -> int:
    require(type(value) is int and minimum <= value <= maximum, "integer domain")
    return value


def array(value: object, maximum: int) -> list:
    require(type(value) is list and len(value) <= maximum, "array domain")
    return value


class LevelReplay:
    """Check every Boolean read, restoration frame, release, gate and output."""

    def __init__(self, response: dict, budget: int = 128):
        require(type(response) is dict, "response object")
        self.budget = integer(budget, 128, 1)
        graph = response.get("network")
        require(type(graph) is dict, "network object")
        rows = array(graph.get("nodes"), 64)
        inputs = array(graph.get("inputs"), 6)
        outputs = array(graph.get("outputs"), 16)
        self.steps = array(response.get("steps"), 128)
        self.actual_gates = array(response.get("gates"), 4096)
        integer(response.get("num_qubits"), self.budget)
        require(
            response.get("implementation")
            in (
                "caterpillar::xag_fast_lowt_mapping_strategy",
                "caterpillar::xag_low_depth_mapping_strategy",
            ),
            "implementation identity",
        )
        for key, maximum in (("input_qubits", 6), ("output_qubits", 16)):
            wires = array(response.get(key), maximum)
            for q in wires:
                integer(q, response["num_qubits"] - 1)
            require(len(wires) == len(set(wires)), "duplicate I/O wire")
        # Validate shape/indices before constructing any truth tables or replay maps.
        require(len(rows) >= len(inputs) + 1, "node count")
        ids = []
        for row in rows:
            require(type(row) is dict, "node object")
            ids.append(integer(row.get("id"), len(rows) - 1))
        require(sorted(ids) == list(range(len(rows))), "canonical node IDs")
        for node in inputs:
            integer(node, len(rows) - 1, 1)
        require(inputs == list(range(1, len(inputs) + 1)), "canonical positional PIs")
        self.rows = {row["id"]: row for row in rows}
        self.inputs = inputs
        self.outputs = outputs
        self.drivers = set()
        for output in outputs:
            require(
                type(output) is dict and set(output) == {"node", "inverted"},
                "output shape",
            )
            self.drivers.add(integer(output["node"], len(rows) - 1))
            require(type(output["inverted"]) is bool, "output polarity")
        for node in range(len(rows)):
            row = self.rows[node]
            fanins = array(row.get("fanins"), 2)
            if node == 0:
                require(
                    row.get("kind") == "constant"
                    and row.get("value") is False
                    and not fanins,
                    "canonical zero",
                )
            elif node in inputs:
                require(row.get("kind") == "input" and not fanins, "PI shape")
            else:
                require(
                    row.get("kind") in ("and", "xor") and len(fanins) == 2, "binary XAG"
                )
                for edge in fanins:
                    require(
                        type(edge) is dict and set(edge) == {"node", "inverted"},
                        "fanin shape",
                    )
                    integer(edge["node"], node - 1, 1)
                    require(type(edge["inverted"]) is bool, "edge polarity")
                require(fanins[0]["node"] != fanins[1]["node"], "simplified fanins")
                require(
                    row.get("truth") == ("1000" if row["kind"] == "and" else "0110"),
                    "node truth",
                )
                if row["kind"] == "xor":
                    require(
                        not any(e["inverted"] for e in fanins), "canonical XOR polarity"
                    )
        reachable = set(self.drivers)
        for node in reversed(range(len(rows))):
            if node in reachable:
                reachable.update(e["node"] for e in self.rows[node]["fanins"])
        require(
            all(node in reachable for node in range(len(inputs) + 1, len(rows))),
            "cleaned graph",
        )
        self.mask = (1 << (1 << len(inputs))) - 1
        self.values = [0] * len(rows)
        for i, node in enumerate(inputs):
            self.values[node] = sum(
                ((x >> i) & 1) << x for x in range(1 << len(inputs))
            )
        for node in range(len(inputs) + 1, len(rows)):
            row = self.rows[node]
            left, right = [
                self.values[e["node"]] ^ (self.mask if e["inverted"] else 0)
                for e in row["fanins"]
            ]
            self.values[node] = left & right if row["kind"] == "and" else left ^ right
        self.stacks = [[] for _ in rows]
        self.wires = []
        self.free = []
        self.active = set()
        self.gates = []
        self.reads = self.frames = self.releases = self.reuses = 0
        self.zeroed_unreleased = 0
        for node in inputs:
            q = self.allocate()
            self.wires[q] = self.values[node]
            self.stacks[node].append(q)
            self.active.add(node)
        if 0 in self.drivers:
            self.stacks[0].append(self.allocate())
            self.active.add(0)
        self.response = response

    def allocate(self) -> int:
        if self.free:
            q = self.free.pop()
            require(self.wires[q] == 0, "nonzero reuse")
            self.reuses += 1
            return q
        require(len(self.wires) < self.budget, "physical width budget")
        self.wires.append(0)
        return len(self.wires) - 1

    def address(self, node: int) -> int:
        integer(node, len(self.values) - 1)
        require(bool(self.stacks[node]), "absent address")
        q = self.stacks[node][-1]
        require(q not in self.free, "released address")
        return q

    def release(self, q: int) -> None:
        """Require zero and no current alias before making an address reusable."""
        require(self.wires[q] == 0 and q not in self.free, "nonzero/double release")
        require(
            all(not stack or stack[-1] != q for stack in self.stacks),
            "release live address",
        )
        self.free.append(q)
        self.releases += 1

    def read(self, node: int) -> int:
        q = self.address(node)
        require(self.wires[q] == self.values[node], f"wrong-value operand {node}")
        self.reads += 1
        return q

    def gate(
        self, controls: list[int], target: int, polarity: list[bool] | None = None
    ) -> None:
        polarity = [True] * len(controls) if polarity is None else polarity
        require(len(self.gates) < 4096, "gate cap")
        require(
            len(controls) == len(set(controls)) and target not in controls,
            "invalid gate wiring",
        )
        require(len(controls) == len(polarity), "gate polarity count")
        toggle = self.mask
        for q, positive in zip(controls, polarity):
            toggle &= self.wires[q] ^ (0 if positive else self.mask)
        self.wires[target] ^= toggle
        self.gates.append(
            dict(kind="x", controls=controls, polarity=polarity, target=target)
        )

    def parity(self, target: int, leaves: list[int]) -> None:
        for node in leaves:
            q = self.address(node)
            if q != target:
                self.gate([self.read(node)], target)
            # Skipped target is an address, not a Boolean operand read.

    def boundary(self) -> None:
        addresses = [self.read(node) for node in sorted(self.active)]
        require(len(addresses) == len(set(addresses)), "active boundary aliases")
        require(
            all(value == 0 for q, value in enumerate(self.wires) if q not in addresses),
            "dirty boundary scratch",
        )

    def cone_ids(self, values: object, node: int) -> list[int]:
        result = array(values, 64)
        for value in result:
            integer(value, node - 1, 1)
            require(value in self.active, "inactive boundary leaf")
        require(result == sorted(set(result)), "noncanonical cone IDs")
        return result

    def check_level(self, action: dict) -> list:
        require(
            type(action) is dict and set(action) == {"node", "action", "level"},
            "level action shape",
        )
        integer(action["node"], len(self.values) - 1, 1)
        require(
            action["action"] in ("compute_level", "uncompute_level"),
            "unsupported action",
        )
        level = array(action["level"], 64)
        seen = set()
        for entry in level:
            require(
                type(entry) is dict and set(entry) == {"node", "cones"},
                "level entry shape",
            )
            node = integer(entry["node"], len(self.values) - 1, len(self.inputs) + 1)
            require(node not in seen, "duplicate level node")
            seen.add(node)
            cones = array(entry["cones"], 2)
            require(len(cones) == 2, "two cones required")
            actual_fanins = []
            for cone in cones:
                require(
                    type(cone) is dict
                    and set(cone)
                    == {"root", "leaves", "target", "copies", "complemented"},
                    "cone shape",
                )
                root = integer(cone["root"], node - 1, 1)
                require(type(cone["complemented"]) is bool, "cone polarity")
                actual_fanins.append((root, cone["complemented"]))
                leaves = self.cone_ids(cone["leaves"], node)
                copies = self.cone_ids(cone["copies"], node)
                targets = self.cone_ids(cone["target"], node)
                require(
                    set(copies) <= set(leaves) and set(targets) <= set(leaves),
                    "copy/target subset",
                )
                parity = 0
                for leaf in leaves:
                    parity ^= self.values[leaf]
                require(parity == self.values[root], "cone value differs from root")
            require(
                sorted(actual_fanins)
                == sorted(
                    (e["node"], e["inverted"]) for e in self.rows[node]["fanins"]
                ),
                "central fanins differ",
            )
        return level

    def central(self, node: int, cones: list, targets: list[int], target: int) -> None:
        for cone, q in zip(cones, targets):
            require(
                self.wires[q] == self.values[cone["root"]], "wrong central cone value"
            )
            self.reads += 1
        if self.rows[node]["kind"] == "and":
            self.gate(targets, target, [not c["complemented"] for c in cones])
        else:
            self.gate([targets[0]], target)
            self.gate([targets[1]], target)
            if cones[0]["complemented"] != cones[1]["complemented"]:
                self.gate([], target)

    def frame(
        self,
        before: list[int],
        stacks: list[list[int]],
        node: int,
        target: int,
        inverse: bool,
    ) -> None:
        require(
            self.wires[target] == (0 if inverse else self.values[node]),
            "central result",
        )
        for q, value in enumerate(self.wires):
            if q != target:
                require(
                    value == (before[q] if q < len(before) else 0), "frame restoration"
                )
        expected = deepcopy(stacks)
        if inverse:
            expected[node].pop()
        else:
            expected[node].append(target)
        require(self.stacks == expected, "frame address restoration")
        self.frames += 1

    def compute(self, level: list) -> None:
        roots = {}
        # Pinned LHRS prepares copies for the entire level before any central node.
        for entry in level:
            targets = []
            for cone in entry["cones"]:
                if cone["copies"]:
                    q = self.allocate()
                    self.parity(q, cone["copies"])
                elif len(cone["leaves"]) == 1:
                    q = self.address(cone["leaves"][0])
                else:
                    q = (
                        self.address(cone["target"][0])
                        if cone["target"]
                        else self.allocate()
                    )
                targets.append(q)
            roots[entry["node"]] = targets
        for entry in level:
            node, cones = entry["node"], entry["cones"]
            require(node not in self.active, "compute active node")
            before, stacks = self.wires.copy(), deepcopy(self.stacks)
            target = self.allocate()
            require(self.wires[target] == 0, "compute target nonzero")
            for cone, q in zip(cones, roots[node]):
                self.parity(q, sorted(set(cone["leaves"]) ^ set(cone["copies"])))
                self.stacks[cone["root"]].append(q)
            self.central(node, cones, roots[node], target)
            self.stacks[node].append(target)
            for cone, q in reversed(list(zip(cones, roots[node]))):
                self.parity(q, sorted(set(cone["leaves"]) ^ set(cone["copies"])))
            for cone in cones:
                self.stacks[cone["root"]].pop()
            self.frame(before, stacks, node, target, False)
            self.active.add(node)
        for entry in level:
            for cone, q in zip(entry["cones"], roots[entry["node"]]):
                if cone["copies"]:
                    for leaf in cone["copies"]:
                        self.gate([self.read(leaf)], q)
                    self.release(q)

    def uncompute(self, level: list) -> None:
        for entry in reversed(level):
            node, cones = entry["node"], entry["cones"]
            require(
                node in self.active and node not in self.drivers,
                "invalid uncompute boundary",
            )
            before, stacks = self.wires.copy(), deepcopy(self.stacks)
            targets = []
            for cone in cones:
                if len(cone["leaves"]) == 1:
                    q = self.address(cone["leaves"][0])
                else:
                    q = (
                        self.address(cone["target"][0])
                        if cone["target"]
                        else self.allocate()
                    )
                    self.parity(q, cone["leaves"])
                    self.stacks[cone["root"]].append(q)
                targets.append(q)
            target = self.read(node)
            self.central(node, cones, targets, target)
            self.stacks[node].pop()
            for cone, q in reversed(list(zip(cones, targets))):
                if len(cone["leaves"]) != 1:
                    self.parity(q, cone["leaves"])
                    self.stacks[cone["root"]].pop()
            self.frame(before, stacks, node, target, True)
            self.active.remove(node)
            # Actual pinned uncompute_level does not release its zero target.
            self.zeroed_unreleased += 1

    def finish(self) -> dict:
        self.boundary()
        for action in self.steps:
            level = self.check_level(action)
            if action["action"] == "compute_level":
                self.compute(level)
            else:
                self.uncompute(level)
            self.boundary()
        require(
            self.active
            == set(self.inputs) | self.drivers | ({0} if 0 in self.drivers else set()),
            "unfinished non-output boundary",
        )
        output_wires, first = [], {}
        for output in self.outputs:
            node, sign = output["node"], output["inverted"]
            if node in first:
                q = self.allocate()
                # The first output may have flipped its raw PI/driver wire.
                source = self.address(node)
                require(
                    self.wires[source]
                    == self.values[node] ^ (self.mask if first[node] else 0),
                    "output copy read",
                )
                self.reads += 1
                self.gate([source], q)
                if sign != first[node]:
                    self.gate([], q)
            else:
                q = self.read(node)
                if sign:
                    self.gate([], q)
                first[node] = sign
            require(
                self.wires[q] == self.values[node] ^ (self.mask if sign else 0),
                "output value",
            )
            output_wires.append(q)
        require(
            self.response.get("input_qubits") == list(range(len(self.inputs))),
            "input wire mismatch",
        )
        require(
            self.response.get("output_qubits") == output_wires, "output wire mismatch"
        )
        # JSON typed equality is deliberate: bool/float cannot alias integer IDs.
        require(
            json.dumps(self.actual_gates, sort_keys=True)
            == json.dumps(self.gates, sort_keys=True),
            "emitted gates differ from value replay",
        )
        require(
            self.response["num_qubits"] == len(self.wires), "physical width mismatch"
        )
        return dict(
            policy="bounded_pinned_level_values_v1",
            inputs=len(self.inputs),
            assignments=1 << len(self.inputs),
            nodes=len(self.values),
            width=len(self.wires),
            steps=len(self.steps),
            operand_reads=self.reads,
            frames=self.frames,
            zero_releases=self.releases,
            zero_reuses=self.reuses,
            zeroed_unreleased=self.zeroed_unreleased,
            clean_workspace_required=True,
        )


def validate_level_response(response: dict, *, qubit_budget: int = 128) -> dict:
    """Return a new private certificate only after complete exact replay succeeds."""
    return LevelReplay(response, qubit_budget).finish()
