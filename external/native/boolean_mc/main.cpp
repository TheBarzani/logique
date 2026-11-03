// Private, bounded instrumentation of the pinned tweedledum xag_optimize recipe.
#include <cstdint>
#include <chrono>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include <lorina/verilog.hpp>
#include <mockturtle/io/verilog_reader.hpp>
#include <mockturtle/views/topo_view.hpp>
#include <tweedledum/Utils/Classical/xag_optimize.h>

namespace mt = mockturtle;
using json = nlohmann::json;
using Network = mt::xag_network;
using Clock = std::chrono::steady_clock;
constexpr uint32_t max_inputs = 10, max_nodes = 4096, max_outputs = 16;

void caps(Network const& n) {
    if (!n.is_combinational() || n.num_pis() > max_inputs ||
        n.size() > max_nodes || n.num_pos() == 0 || n.num_pos() > max_outputs)
        throw std::runtime_error("Unsupported network: inputs<=10, nodes<=4096, outputs1..16, combinational only");
}

json signal_json(Network const& n, Network::signal s) {
    return {{"node", n.get_node(s)}, {"complement", n.is_complemented(s)}};
}

// Public active-node/edge representation, including dangling live nodes and
// total storage size (foreach_node omits dead slots in the pinned network).
// No truth table is allocated until caps() has accepted the network.
json graph(Network const& n) {
    json nodes = json::array(), inputs = json::array(), outputs = json::array();
    n.foreach_node([&](auto v) {
        json children = json::array();
        if (!n.is_constant(v) && !n.is_pi(v))
            n.foreach_fanin(v, [&](auto s) { children.push_back(signal_json(n, s)); });
        nodes.push_back({{"id", v}, {"kind", n.is_constant(v) ? "constant" :
            n.is_pi(v) ? "input" : n.is_and(v) ? "and" : n.is_xor(v) ? "xor" : "unsupported"},
            {"fanins", children}});
    });
    n.foreach_pi([&](auto v) { inputs.push_back(v); });
    n.foreach_po([&](auto s) { outputs.push_back(signal_json(n, s)); });
    return {{"size", n.size()}, {"nodes", nodes}, {"inputs", inputs}, {"outputs", outputs}};
}

// A scalar evaluator, independent of mockturtle simulation/truth-table APIs.
// Assignment bit i is primary input i; output strings are in increasing assignment order.
std::vector<std::string> truth(Network const& n) {
    caps(n);
    std::vector<std::string> tables(n.num_pos());
    mt::topo_view topo{n};
    for (uint32_t assignment = 0; assignment < (1u << n.num_pis()); ++assignment) {
        std::vector<uint8_t> values(n.size(), 0);
        n.foreach_pi([&](auto v, auto i) { values[v] = (assignment >> i) & 1u; });
        topo.foreach_node([&](auto v) {
            if (n.is_constant(v) || n.is_pi(v)) return;
            std::vector<uint8_t> fs;
            n.foreach_fanin(v, [&](auto s) { fs.push_back(values[n.get_node(s)] ^ n.is_complemented(s)); });
            if (fs.size() != 2 || (!n.is_and(v) && !n.is_xor(v)))
                throw std::runtime_error("Unsupported XAG node");
            values[v] = n.is_and(v) ? fs[0] & fs[1] : fs[0] ^ fs[1];
        });
        n.foreach_po([&](auto s, auto i) {
            tables[i].push_back('0' + (values[n.get_node(s)] ^ n.is_complemented(s)));
        });
    }
    return tables;
}

// Explicit positional writer also supports zero inputs and repeated/constant outputs.
// All declarations precede assignments for the pinned Lorina parser.
std::string serialize(Network const& n) {
    caps(n);
    std::ostringstream out;
    out << "module top(";
    for (uint32_t i = 0; i < n.num_pis(); ++i) out << (i ? ", " : "") << "x" << i;
    for (uint32_t i = 0; i < n.num_pos(); ++i) out << (i || n.num_pis() ? ", " : "") << "y" << i;
    out << ");\n";
    for (uint32_t i = 0; i < n.num_pis(); ++i) out << "input x" << i << ";\n";
    for (uint32_t i = 0; i < n.num_pos(); ++i) out << "output y" << i << ";\n";
    std::vector<std::string> names(n.size());
    names[0] = "1'b0";
    n.foreach_pi([&](auto v, auto i) { names[v] = "x" + std::to_string(i); });
    mt::topo_view topo{n};
    topo.foreach_gate([&](auto v) {
        names[v] = "n" + std::to_string(v);
        out << "wire " << names[v] << ";\n";
    });
    auto expression = [&](auto s) { return (n.is_complemented(s) ? "~" : "") + names[n.get_node(s)]; };
    topo.foreach_gate([&](auto v) {
        std::vector<std::string> fs;
        n.foreach_fanin(v, [&](auto s) { fs.push_back(expression(s)); });
        if (fs.size() != 2 || (!n.is_and(v) && !n.is_xor(v)))
            throw std::runtime_error("Unsupported serialization node");
        out << "assign " << names[v] << " = " << fs[0] << (n.is_and(v) ? " & " : " ^ ") << fs[1] << ";\n";
    });
    n.foreach_po([&](auto s, auto i) { out << "assign y" << i << " = " << expression(s) << ";\n"; });
    out << "endmodule\n";
    return out.str();
}

json statistics(Network const& n) {
    caps(n);
    uint32_t ands = 0, xors = 0, depth = 0;
    std::vector<uint32_t> levels(n.size(), 0);
    mt::topo_view topo{n};
    topo.foreach_gate([&](auto v) {
        uint32_t d = 0;
        n.foreach_fanin(v, [&](auto s) { d = std::max(d, levels[n.get_node(s)]); });
        ands += n.is_and(v); xors += n.is_xor(v);
        levels[v] = d + n.is_and(v);
    });
    n.foreach_po([&](auto s) { depth = std::max(depth, levels[n.get_node(s)]); });
    return {{"inputs", n.num_pis()}, {"outputs", n.num_pos()}, {"nodes", n.size()},
        {"and_count", ands}, {"xor_count", xors}, {"multiplicative_depth", depth}};
}

int main() {
    // Reserve stdout for flushed JSONL; keep dependency diagnostics on stderr.
    auto* protocol = std::cout.rdbuf();
    std::cout.rdbuf(std::cerr.rdbuf());
    auto emit = [&](json const& event) {
        std::ostream stream(protocol); stream << event.dump() << '\n'; stream.flush();
    };
    std::string boundary = "request";
    try {
        json request;
        std::cin >> request;
        auto source = request.at("verilog").get<std::string>();
        if (source.size() > 1048576) throw std::runtime_error("Source exceeds 1MiB cap");
        boundary = "parse";
        Network network;
        std::istringstream input(source);
        if (lorina::read_verilog(input, mt::verilog_reader(network)) != lorina::return_code::success)
            throw std::runtime_error("Combinational Verilog parse failed");
        boundary = "original";
        emit({{"kind", "snapshot"}, {"boundary", boundary}, {"graph", graph(network)}});
        caps(network);
        auto original = truth(network);
        auto previous = original;
        const auto inputs = network.num_pis(), outputs = network.num_pos();
        auto checkpoint = [&](double seconds) {
            // Preserve the post-transform graph BEFORE proof or serialization can fail.
            emit({{"kind", "snapshot"}, {"boundary", boundary}, {"graph", graph(network)}});
            caps(network);
            auto table = truth(network);
            if (network.num_pis() != inputs || network.num_pos() != outputs ||
                table != previous || table != original)
                throw std::runtime_error("Exhaustive original/previous/pass CEC failed");
            auto verilog = serialize(network);
            emit({{"kind", "serialization"}, {"boundary", boundary}, {"verilog", verilog}});
            Network readback;
            std::istringstream exported(verilog);
            if (lorina::read_verilog(exported, mt::verilog_reader(readback)) != lorina::return_code::success)
                throw std::runtime_error("Serialized Verilog parse failed");
            caps(readback);
            auto roundtrip = truth(readback);
            if (readback.num_pis() != inputs || readback.num_pos() != outputs || roundtrip != table)
                throw std::runtime_error("Exhaustive serialization CEC failed");
            emit({{"kind", "checked"}, {"boundary", boundary}, {"equivalent_original", true},
                {"equivalent_previous", true}, {"serialization_equivalent", true},
                {"truth", table}, {"readback_graph", graph(readback)},
                {"statistics", statistics(network)}, {"transform_seconds", seconds},
                {"assignments", 1u << inputs}, {"cec", "exhaustive_positional"}});
            previous = std::move(table);
        };
        checkpoint(0.0);

        // Exact pinned recipe: xag_optimize.h, with a checkpoint after EACH call.
        // Snapshots/truth strings do not share mutable network storage.
        auto step = [&](std::string const& name, auto operation) {
            boundary = name;
            emit({{"kind", "started"}, {"boundary", name}});
            auto start = Clock::now(); operation();
            checkpoint(std::chrono::duration<double>(Clock::now() - start).count());
        };
        mt::future::xag_minmc_resynthesis resyn;
        mt::cut_rewriting_params cut_cfg;
        cut_cfg.cut_enumeration_ps.cut_size = 5;
        mt::bidecomposition_resynthesis<Network> bi_resyn;
        mt::refactoring_params ref_cfg;
        ref_cfg.allow_zero_gain = true;
        step("constant_fanin_1", [&] { network = mt::xag_constant_fanin_optimization(network); });
        step("cleanup_1", [&] { network = mt::cleanup_dangling(network); });
        step("dont_cares_1", [&] { network = mt::xag_dont_cares_optimization(network); });
        step("cleanup_2", [&] { network = mt::cleanup_dangling(network); });
        step("refactoring", [&] { mt::refactoring(network, bi_resyn, ref_cfg, nullptr, mt::free_xor_cost<Network>()); });
        step("cleanup_3", [&] { network = mt::cleanup_dangling(network); });
        step("xag_minmc_cut_rewriting", [&] { mt::cut_rewriting_with_compatibility_graph(network, resyn, cut_cfg, nullptr, mt::mc_cost<Network>()); });
        step("cleanup_4", [&] { network = mt::cleanup_dangling(network); });
        step("constant_fanin_2", [&] { network = mt::xag_constant_fanin_optimization(network); });
        step("cleanup_5", [&] { network = mt::cleanup_dangling(network); });
        step("dont_cares_2", [&] { network = mt::xag_dont_cares_optimization(network); });
        step("cleanup_6", [&] { network = mt::cleanup_dangling(network); });
        emit({{"kind", "complete"}, {"passes", 12}});
        return 0;
    } catch (std::exception const& e) {
        emit({{"kind", "failure"}, {"boundary", boundary}, {"error", e.what()}});
        return 1;
    }
}
