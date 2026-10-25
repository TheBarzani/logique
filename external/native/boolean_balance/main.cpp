// One JSON request on stdin; checked Verilog and per-pass evidence on stdout.
#include <chrono>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <nlohmann/json.hpp>
#include <lorina/verilog.hpp>
#include <mockturtle/networks/xag.hpp>
#include <mockturtle/io/verilog_reader.hpp>
#include <mockturtle/io/write_verilog.hpp>
#include <mockturtle/algorithms/balancing.hpp>
#include <mockturtle/algorithms/cleanup.hpp>
#include <mockturtle/algorithms/equivalence_checking.hpp>
#include <mockturtle/algorithms/miter.hpp>
#include <mockturtle/algorithms/xag_balancing.hpp>
#include <mockturtle/algorithms/xag_algebraic_rewriting.hpp>
#include <mockturtle/views/depth_view.hpp>
#include <mockturtle/views/topo_view.hpp>

namespace mt = mockturtle;
using json = nlohmann::json;
using clock_type = std::chrono::steady_clock;

json statistics(mt::xag_network const& network) {
    uint32_t ands = 0, xors = 0, multiplicative_depth = 0;
    std::vector<uint32_t> levels(network.size(), 0);
    mt::topo_view topo{network};
    topo.foreach_gate([&](auto node) {
        uint32_t depth = 0;
        network.foreach_fanin(node, [&](auto signal) {
            depth = std::max(depth, levels[network.get_node(signal)]);
        });
        if (network.is_and(node)) { ++ands; ++depth; }
        if (network.is_xor(node)) ++xors;
        levels[node] = depth;
    });
    network.foreach_po([&](auto signal) {
        multiplicative_depth = std::max(multiplicative_depth, levels[network.get_node(signal)]);
    });
    mt::depth_view depth{network};
    return {{"inputs", network.num_pis()}, {"outputs", network.num_pos()},
            {"and_count", ands}, {"xor_count", xors}, {"lut_count", 0},
            {"multiplicative_depth", multiplicative_depth}, {"depth", depth.depth()}};
}

void check_equivalence(mt::xag_network const& before, mt::xag_network const& after,
                       uint32_t conflict_limit) {
    auto miter = mt::miter<mt::xag_network>(before, after);
    if (!miter) throw std::runtime_error("Optimization changed input/output arity");
    mt::equivalence_checking_params params;
    params.conflict_limit = conflict_limit;
    auto equivalent = mt::equivalence_checking(*miter, params);
    if (!equivalent) throw std::runtime_error("Boolean equivalence check reached its resource limit");
    if (!*equivalent) throw std::runtime_error("Optimization changed the Boolean function");
}

int main() {
    std::ostringstream diagnostics;
    auto* output = std::cout.rdbuf(diagnostics.rdbuf());
    try {
        json request;
        std::cin >> request;
        const auto path = request.at("path").get<std::string>();
        const auto passes = request.at("passes").get<std::vector<std::string>>();
        const auto conflicts = request.value("cec_conflict_limit", uint32_t{1000000});
        for (auto const& pass : passes)
            if (pass != "xag_balance" && pass != "algebraic" && pass != "esop")
                throw std::runtime_error("Unknown balancing pass: " + pass);
        mt::xag_network network;
        auto start = clock_type::now();
        if (lorina::read_verilog(path, mt::verilog_reader(network)) != lorina::return_code::success
            || network.num_pos() == 0)
            throw std::runtime_error("Expected combinational Verilog with at least one output");
        json result = {{"input_seconds", std::chrono::duration<double>(clock_type::now() - start).count()},
                       {"input_statistics", statistics(network)}, {"passes", json::array()},
                       {"input_order", "preserved by primary-input index"}};
        // Deep clones matter: mockturtle's ordinary copy shares mutable storage.
        auto before_cleanup = network.clone();
        network = mt::cleanup_dangling(network);
        check_equivalence(before_cleanup, network, conflicts);
        result["cleanup_equivalent"] = true;
        for (auto const& pass : passes) {
            auto before = network.clone();
            auto begin = clock_type::now();
            if (pass == "xag_balance") mt::xag_balance(network);
            else if (pass == "algebraic") {
                mt::depth_view depth{network};
                mt::xag_algebraic_depth_rewriting(depth);
            } else network = mt::esop_balancing(network);
            network = mt::cleanup_dangling(network);
            auto elapsed = std::chrono::duration<double>(clock_type::now() - begin).count();
            begin = clock_type::now();
            check_equivalence(before, network, conflicts);
            auto verification = std::chrono::duration<double>(clock_type::now() - begin).count();
            result["passes"].push_back({{"name", pass}, {"equivalent", true},
                {"optimization_seconds", elapsed}, {"equivalence_seconds", verification},
                {"before", statistics(before)}, {"after", statistics(network)}});
        }
        std::ostringstream verilog;
        if (network.num_pis() == 0) {
            // The pinned writer emits an empty input declaration that its own
            // reader rejects. Zero-input Boolean outputs must be constants.
            verilog << "module top(";
            for (uint32_t i = 0; i < network.num_pos(); ++i)
                verilog << (i ? ", " : "") << "y" << i;
            verilog << ");" << std::endl;
            for (uint32_t i = 0; i < network.num_pos(); ++i) {
                auto signal = network.po_at(i);
                auto node = network.get_node(signal);
                if (!network.is_constant(node))
                    throw std::runtime_error("Nonconstant output without primary inputs");
                const bool value = network.constant_value(node) != network.is_complemented(signal);
                verilog << "output y" << i << ";" << std::endl;
                verilog << "assign y" << i << " = 1'b" << int(value) << ";" << std::endl;
            }
            verilog << "endmodule" << std::endl;
        } else mt::write_verilog(network, verilog);
        std::istringstream exported(verilog.str());
        mt::xag_network roundtrip;
        if (lorina::read_verilog(exported, mt::verilog_reader(roundtrip)) != lorina::return_code::success)
            throw std::runtime_error("Exported Verilog cannot be read back");
        check_equivalence(network, roundtrip, conflicts);
        result["serialization_equivalent"] = true;
        result["verilog"] = verilog.str();
        result["output_statistics"] = statistics(network);
        result["cec_conflict_limit"] = conflicts;
        std::cout.rdbuf(output);
        if (!diagnostics.str().empty()) std::cerr << diagnostics.str();
        std::cout << result.dump() << '\n';
        return 0;
    } catch (std::exception const& error) {
        std::cout.rdbuf(output);
        std::cerr << diagnostics.str() << error.what() << '\n';
        return 1;
    }
}
