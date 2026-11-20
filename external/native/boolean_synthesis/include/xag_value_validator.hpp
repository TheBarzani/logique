#pragma once
#include "actions.hpp"
#include <cstdint>

// Only the pinned sequential, canonical, cleaned XAG schedule is certified.
// Truth tables have one bit per input assignment, never one bit per qubit state.
namespace xag_value {
inline void require(bool condition, std::string const& message) {
    if (!condition) throw std::runtime_error("xag_low_t value validator: " + message);
}
inline void supported(bool condition, std::string const& message) {
    require(condition, "unsupported: " + message);
}
using Leaves = std::vector<uint32_t>;
inline void caps(size_t inputs, size_t nodes, size_t width, size_t steps) {
    supported(inputs <= 6, "inputs exceed 6");
    supported(nodes <= 256, "nodes exceed 256");
    supported(width <= 256, "width exceeds 256");
    supported(steps <= 4096, "steps exceed 4096");
}
inline Leaves difference(Leaves const& a, Leaves const& b) {
    Leaves out;
    std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out));
    return out;
}
struct Cone { uint32_t root; Leaves leaves, target; };

// Independent transcription of the two-cone construction, not a call to
// Caterpillar's get_cones/gen_steps. Singletons preserve their root distinction.
inline std::vector<Cone> cones(uint32_t a, uint32_t b, std::vector<Leaves> const& fi) {
    std::vector<Cone> cs{{a, fi[a], {}}, {b, fi[b], {}}};
    if ((cs[0].leaves.size() == 1) != (cs[1].leaves.size() == 1)) {
        if (cs[0].leaves.size() == 1) std::reverse(cs.begin(), cs.end());
        cs[0].target = cs[0].leaves;
        auto it = std::find(cs[0].target.begin(), cs[0].target.end(), cs[1].leaves[0]);
        if (it != cs[0].target.end()) {
            cs[0].target.erase(it);
            std::reverse(cs.begin(), cs.end());
        }
    } else {
        if (std::includes(cs[0].leaves.begin(), cs[0].leaves.end(),
                          cs[1].leaves.begin(), cs[1].leaves.end()))
            std::reverse(cs.begin(), cs.end());
        cs[0].target = difference(cs[0].leaves, cs[1].leaves);
        cs[1].target = difference(cs[1].leaves, cs[0].leaves);
        if (cs[0].target.empty()) {
            cs[1].target.push_back(cs[0].root);
            cs[1].leaves = cs[1].target;
            cs[0].target = cs[0].leaves;
        }
    }
    return cs;
}
inline json cone_step(Cone const& c, bool restoring) {
    if (c.leaves.size() == 1) {
        if (c.leaves[0] == c.root) return nullptr;
        return {{"node", c.root}, {"action", "buffer"},
                {"target", restoring ? c.leaves[0] : c.root},
                {"leaf", restoring ? c.root : c.leaves[0]}};
    }
    if (!c.target.empty())
        return {{"node", c.root}, {"action", "compute_inplace"},
                {"target_index", c.target[0]}, {"explicit_leaves", c.leaves}, {"leaves", c.leaves}};
    return {{"node", c.root}, {"action", "compute"},
            {"explicit_leaves", c.leaves}, {"leaves", c.leaves}, {"cell_override", nullptr}};
}
struct Block { uint32_t node; bool undo; std::vector<Cone> cs; };
struct Domain {
    json nodes = json::array(), outputs = json::array(), steps = json::array();
    Leaves inputs;
    std::vector<Leaves> fi;
    std::vector<Block> blocks;
    uint32_t width = 0;

    explicit Domain(mt::xag_network const& ntk) {
        // These checks precede all graph-sized validator containers and tables.
        supported(ntk.num_pis() <= 6, "inputs exceed 6");
        supported(ntk.size() <= 256, "nodes exceed 256");
        supported(ntk.num_pos() <= 256, "outputs exceed width cap 256");
        require(ntk.is_combinational(), "sequential network domain");
        require(ntk.size() > 0 && ntk.num_pos() > 0, "missing constant/output domain");
        ntk.foreach_pi([&](auto n) { inputs.push_back(ntk.node_to_index(n)); });
        for (uint32_t i = 0; i < inputs.size(); ++i)
            require(inputs[i] == i + 1 && inputs[i] < ntk.size() && ntk.is_pi(inputs[i]),
                    "noncanonical PI order/domain");
        ntk.foreach_po([&](auto f) {
            outputs.push_back({{"node", ntk.node_to_index(ntk.get_node(f))},
                               {"inverted", ntk.is_complemented(f)}});
        });
        for (uint32_t i = 0; i < ntk.size(); ++i) {
            auto n = ntk.index_to_node(i);
            require(ntk.node_to_index(n) == i && !ntk.is_dead(n), "nonfinite/dead node domain");
            json row = {{"kind", "input"}, {"fanins", json::array()}};
            if (ntk.is_constant(n)) {
                require(i == 0 && !ntk.constant_value(n), "constant domain");
                row["kind"] = "constant";
            } else if (ntk.is_pi(n)) {
                require(i <= inputs.size(), "unlisted PI domain");
            } else {
                require(ntk.is_and(n) || ntk.is_xor(n), "non-XAG node");
                row["kind"] = ntk.is_and(n) ? "and" : "xor";
                ntk.foreach_fanin(n, [&](auto f) {
                    auto child = ntk.node_to_index(ntk.get_node(f));
                    require(child > 0 && child < i, "unsimplified constant or nontopological fanin");
                    require(!ntk.is_xor(n) || !ntk.is_complemented(f), "noncanonical XOR polarity");
                    row["fanins"].push_back({{"node", child}, {"inverted", ntk.is_complemented(f)}});
                });
                require(row["fanins"].size() == 2, "nonbinary node");
                require(row["fanins"][0]["node"] != row["fanins"][1]["node"], "unsimplified equal fanins");
            }
            nodes.push_back(row);
        }
        std::vector<bool> reachable(nodes.size(), false), driver(nodes.size(), false);
        for (auto const& out : outputs) {
            auto n = out.at("node").get<uint32_t>();
            require(n < nodes.size(), "invalid output driver");
            reachable[n] = driver[n] = true;
        }
        for (size_t i = nodes.size(); i-- > 0;)
            if (reachable[i]) for (auto const& f : nodes[i]["fanins"])
                reachable[f.at("node").get<uint32_t>()] = true;
        fi.resize(nodes.size());
        std::vector<Block> cleanup;
        for (uint32_t n = 0; n < nodes.size(); ++n) {
            auto kind = nodes[n]["kind"].get<std::string>();
            bool gate = kind == "and" || kind == "xor";
            require(!gate || reachable[n], "network is not cleaned");
            if (kind != "xor" || driver[n]) fi[n] = {n};
            else {
                auto a = nodes[n]["fanins"][0]["node"].get<uint32_t>();
                auto b = nodes[n]["fanins"][1]["node"].get<uint32_t>();
                std::set_symmetric_difference(fi[a].begin(), fi[a].end(), fi[b].begin(), fi[b].end(),
                                              std::back_inserter(fi[n]));
            }
            if (kind == "and" || (gate && driver[n])) {
                auto a = nodes[n]["fanins"][0]["node"].get<uint32_t>();
                auto b = nodes[n]["fanins"][1]["node"].get<uint32_t>();
                Block block{n, false, cones(a, b, fi)};
                blocks.push_back(block);
                if (!driver[n]) { block.undo = true; cleanup.push_back(block); }
            }
        }
        for (auto it = cleanup.rbegin(); it != cleanup.rend(); ++it) blocks.push_back(*it);
        auto append = [&](json const& step) {
            if (step.is_null()) return;
            supported(steps.size() < 4096, "steps exceed 4096");
            steps.push_back(step);
        };
        for (auto const& block : blocks) {
            for (auto const& c : block.cs) append(cone_step(c, false));
            append({{"node", block.node}, {"action", block.undo ? "uncompute" : "compute"},
                    {"explicit_leaves", nullptr}, {"cell_override", nullptr}});
            for (auto it = block.cs.rbegin(); it != block.cs.rend(); ++it) append(cone_step(*it, true));
        }
        // Exact allocation high-water from the action counts/free-list cardinality,
        // including repeated output copies. No truth-table/wire arrays yet.
        width = inputs.size() + unsigned(reachable[0]);
        uint32_t free_count = 0;
        auto allocate = [&]() { if (free_count) --free_count; else ++width;
            supported(width <= 256, "width exceeds 256"); };
        for (auto const& s : steps) {
            if (s["action"] == "compute") allocate();
            if (s["action"] == "uncompute") ++free_count;
        }
        std::set<uint32_t> seen;
        for (auto const& out : outputs)
            if (!seen.insert(out["node"].get<uint32_t>()).second) allocate();
        supported(width <= 256, "width exceeds 256");
#ifndef NDEBUG
        // Pinned update_fi asserts on an empty internal XOR frontier.
        for (uint32_t n = 0; n < nodes.size(); ++n)
            supported(!fi[n].empty(), "empty frontier requires Release/NDEBUG pinned strategy");
#endif
    }
};

struct Entry { uint32_t q, generation; };
struct Frame { uint32_t q; uint64_t saved; };
struct Machine {
    uint64_t mask;
    std::vector<uint64_t> values, wires;
    std::vector<std::vector<Entry>> stacks;
    std::vector<uint32_t> generation, free;
    std::vector<bool> live;
    json gates = json::array(), actions = json::array();
    uint32_t reads = 0, releases = 0;
    explicit Machine(std::vector<uint64_t> v, uint64_t m) : mask(m), values(std::move(v)), stacks(values.size()) {}
    uint32_t allocate() {
        if (free.empty()) {
            supported(wires.size() < 256, "width exceeds 256");
            wires.push_back(0); live.push_back(true); generation.push_back(0);
            return wires.size() - 1;
        }
        auto q = free.back();
        require(!live[q] && wires[q] == 0, "dirty allocation");
        free.pop_back(); live[q] = true; ++generation[q];
        return q;
    }
    void push(uint32_t n, uint32_t q) {
        require(n < stacks.size() && q < wires.size() && live[q], "invalid stack push");
        stacks[n].push_back({q, generation[q]});
    }
    uint32_t top(uint32_t n) const {
        require(n < stacks.size() && !stacks[n].empty(), "unresolved stack");
        auto e = stacks[n].back();
        require(e.q < wires.size() && live[e.q] && e.generation == generation[e.q], "stale generation");
        return e.q;
    }
    uint32_t read(uint32_t n) {
        auto q = top(n);
        require(wires[q] == values[n], "wrong live operand value");
        ++reads; return q;
    }
    void release(uint32_t n, uint32_t q) {
        require(top(n) == q && wires[q] == 0, "dirty release");
        // Only ordinary uncompute pops, matching the existing effective overlay.
        stacks[n].pop_back(); live[q] = false; free.push_back(q); ++releases;
    }
    void gate(Leaves const& controls, std::vector<bool> const& polarity, uint32_t target) {
        require(target < wires.size() && live[target] && controls.size() == polarity.size(), "invalid emitted gate");
        Leaves unique; std::vector<bool> signs;
        uint64_t condition = mask;
        bool zero = false;
        for (size_t i = 0; i < controls.size(); ++i) {
            auto q = controls[i];
            require(q < wires.size() && live[q] && q != target, "emitted target/control alias");
            auto it = std::find(unique.begin(), unique.end(), q);
            if (it == unique.end()) { unique.push_back(q); signs.push_back(polarity[i]); }
            else if (signs[it - unique.begin()] != polarity[i]) zero = true;
            condition &= wires[q] ^ (polarity[i] ? 0 : mask);
        }
        if (zero) return;
        wires[target] ^= condition;
        gates.push_back({{"kind", "x"}, {"controls", unique}, {"polarity", signs}, {"target", target}});
    }
    Frame action(json const& s, json const& node, bool restoring) {
        auto n = s.at("node").get<uint32_t>();
        auto action = s.at("action").get<std::string>();
        json row = s;
        if (action == "buffer") {
            auto q = read(s.at("leaf"));
            push(s.at("target"), q);
            row["physical_target"] = q; actions.push_back(row);
            return {q, wires[q]};
        }
        uint32_t q;
        if (action == "compute") { q = allocate(); push(n, q); }
        else if (action == "uncompute") q = read(n);
        else {
            require(action == "compute_inplace", "unsupported action");
            // Resolving this address is NOT a Boolean read, particularly on restore.
            q = top(s.at("target_index")); push(n, q);
        }
        Frame frame{q, wires[q]};
        row["physical_target"] = q;
        if (!s.at("explicit_leaves").is_null()) {
            Leaves physical;
            for (auto const& leaf : s["explicit_leaves"]) physical.push_back(top(leaf));
            require(std::count(physical.begin(), physical.end(), q) == (action == "compute_inplace" ? 1 : 0), "parity target occurrence");
            row["physical_leaves"] = physical;
            for (size_t i = 0; i < physical.size(); ++i)
                if (physical[i] != q) {
                    read(s["explicit_leaves"][i]);
                    gate({physical[i]}, {true}, q);
                }
        } else {
            Leaves controls; std::vector<bool> signs;
            for (auto const& f : node.at("fanins")) {
                controls.push_back(read(f.at("node")));
                signs.push_back(!f.at("inverted").get<bool>());
            }
            row["physical_controls"] = controls;
            require(controls.size() == 2, "nonbinary central gate");
            if (node["kind"] == "and") gate(controls, signs, q);
            else {
                require(node["kind"] == "xor", "invalid central node");
                for (auto c : controls) gate({c}, {true}, q);
                if (signs[0] != signs[1]) gate({}, {}, q);
            }
        }
        if (action == "uncompute") release(n, q);
        else if (!restoring) require(wires[q] == values[n], "wrong computed value");
        actions.push_back(row);
        return frame;
    }
    void restored(Frame const& before, Frame const& after, bool empty) const {
        require((empty || before.q == after.q) && wires[after.q] == before.saved, "missing cone restoration");
    }
    void boundary(std::map<uint32_t, Frame> const& before, std::set<uint32_t> const& active) {
        std::set<uint32_t> held;
        for (auto n : active) {
            auto q = read(n);
            require(held.insert(q).second, "boundary address alias");
            auto it = before.find(n);
            if (it != before.end())
                require(it->second.q == q && it->second.saved == wires[q], "boundary not restored");
        }
        for (uint32_t q = 0; q < wires.size(); ++q)
            if (!held.count(q)) require(wires[q] == 0, "unowned boundary garbage");
    }
};

// Creates the independent expected physical computation, with caps checked before
// tables. The caller must compare it with the actual emitted native response.
inline json expected(Domain const& d) {
    caps(d.inputs.size(), d.nodes.size(), d.width, d.steps.size());
    uint32_t assignments = 1u << d.inputs.size();
    uint64_t mask = assignments == 64 ? ~uint64_t(0) : (uint64_t(1) << assignments) - 1;
    std::vector<uint64_t> values(d.nodes.size(), 0);
    for (size_t i = 0; i < d.inputs.size(); ++i)
        for (uint32_t x = 0; x < assignments; ++x)
            values[d.inputs[i]] |= uint64_t((x >> i) & 1) << x;
    for (uint32_t n = 0; n < d.nodes.size(); ++n) {
        auto const& node = d.nodes[n];
        if (node["fanins"].empty()) continue;
        uint64_t f[2];
        for (unsigned i = 0; i < 2; ++i) {
            auto const& child = node["fanins"][i];
            f[i] = values[child["node"].get<uint32_t>()] ^ (child["inverted"].get<bool>() ? mask : 0);
        }
        values[n] = node["kind"] == "and" ? f[0] & f[1] : f[0] ^ f[1];
        if (node["kind"] == "xor" && !(d.fi[n].size() == 1 && d.fi[n][0] == n)) {
            uint64_t parity = 0;
            for (auto l : d.fi[n]) parity ^= values[l];
            require(parity == values[n], "frontier value identity");
        }
    }
    Machine m(values, mask);
    json block_checks = json::array();
    std::set<uint32_t> active;
    Leaves input_qubits, output_qubits;
    for (auto n : d.inputs) {
        auto q = m.allocate(); m.push(n, q); m.wires[q] = values[n];
        active.insert(n); input_qubits.push_back(q);
    }
    for (auto const& out : d.outputs) if (out["node"] == 0 && !active.count(0)) {
        m.push(0, m.allocate()); active.insert(0);
    }
    size_t cursor = 0;
    for (auto const& block : d.blocks) {
        json trace = {{"node", block.node}, {"undo", block.undo},
                      {"entry", json::array()}, {"frames", json::array()},
                      {"exit", json::array()}};
        std::map<uint32_t, Frame> before;
        for (auto n : active) {
            auto q = m.read(n); before[n] = {q, m.wires[q]};
            trace["entry"].push_back({{"node", n}, {"wire", q},
                {"value", m.wires[q]}, {"generation", m.generation[q]}});
        }
        std::vector<Frame> frames;
        for (auto const& c : block.cs) {
            auto step = cone_step(c, false);
            if (step.is_null()) { auto q = m.read(c.root); frames.push_back({q, m.wires[q]}); }
            else { frames.push_back(m.action(d.steps.at(cursor++), d.nodes[block.node], false)); }
            m.read(c.root);
            trace["frames"].push_back({{"root", c.root}, {"wire", frames.back().q},
                {"saved", frames.back().saved}, {"prepared", m.wires[m.top(c.root)]}});
        }
        m.action(d.steps.at(cursor++), d.nodes[block.node], false);
        for (size_t i = block.cs.size(); i-- > 0;) {
            auto const& c = block.cs[i];
            auto step = cone_step(c, true);
            if (!step.is_null()) {
                auto after = m.action(d.steps.at(cursor++), d.nodes[block.node], true);
                m.restored(frames[i], after, c.leaves.empty());
                trace["frames"][i]["restored_wire"] = after.q;
                trace["frames"][i]["restored_value"] = m.wires[after.q];
            }
        }
        if (block.undo) { active.erase(block.node); before.erase(block.node); }
        else active.insert(block.node);
        m.boundary(before, active);
        for (auto n : active) {
            auto q = m.top(n);
            trace["exit"].push_back({{"node", n}, {"wire", q},
                {"value", m.wires[q]}, {"generation", m.generation[q]}});
        }
        block_checks.push_back(trace);
    }
    require(cursor == d.steps.size(), "unconsumed steps");
    // Pre-output checks precede a complemented first PI/output mutating its wire.
    m.boundary({}, active);
    json stacks = json::array();
    for (auto const& stack : m.stacks) {
        Leaves qs; for (auto const& e : stack) qs.push_back(e.q); stacks.push_back(qs);
    }
    std::map<uint32_t, bool> seen;
    for (auto const& out : d.outputs) {
        auto n = out["node"].get<uint32_t>(); bool sign = out["inverted"];
        uint32_t q;
        auto it = seen.find(n);
        if (it == seen.end()) {
            q = m.read(n); seen[n] = sign;
            if (sign) m.gate({}, {}, q);
        } else {
            q = m.allocate(); auto c = m.top(n);
            require(m.wires[c] == (values[n] ^ (it->second ? mask : 0)), "wrong output copy read");
            ++m.reads; m.gate({c}, {true}, q);
            if (sign != it->second) m.gate({}, {}, q);
        }
        require(m.wires[q] == (values[n] ^ (sign ? mask : 0)), "wrong output polarity");
        output_qubits.push_back(q);
    }
    // Later output polarity/copies must preserve all earlier output values.
    for (size_t i = 0; i < d.outputs.size(); ++i) {
        auto n = d.outputs[i]["node"].get<uint32_t>();
        require(m.wires[output_qubits[i]] == (values[n] ^ (d.outputs[i]["inverted"].get<bool>() ? mask : 0)), "post-output value");
    }
    require(m.wires.size() == d.width, "predicted width mismatch");
    return {{"steps", d.steps}, {"gates", m.gates}, {"num_qubits", d.width},
            {"input_qubits", input_qubits}, {"output_qubits", output_qubits},
            {"actions", m.actions}, {"node_stacks", stacks},
            {"certificate", {{"policy", "canonical_sequential_two_cone_truth_tables_v1"},
              {"inputs", d.inputs.size()}, {"assignments", assignments}, {"nodes", d.nodes.size()},
              {"width", d.width}, {"steps", d.steps.size()}, {"blocks", d.blocks.size()},
              {"operand_reads", m.reads}, {"zero_releases", m.releases},
              {"node_values", values}, {"block_checks", block_checks},
              {"caps", {{"inputs", 6}, {"nodes", 256}, {"width", 256}, {"steps", 4096}}}}}};
}
inline void match(json const& expected, json const& actual) {
    for (auto key : {"steps", "gates", "num_qubits", "input_qubits", "output_qubits"})
        require(expected.at(key) == actual.at(key), std::string("actual emitted ") + key + " mismatch");
}
} // namespace xag_value
