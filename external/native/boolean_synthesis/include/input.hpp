#pragma once
#include "types.hpp"
mt::xag_network select_outputs(mt::xag_network const& src, json const& request) {
    mt::xag_network dest;
    std::map<uint32_t, mt::xag_network::signal> map;
    map[0] = dest.get_constant(false);
    src.foreach_pi([&](auto n) { map[n] = dest.create_pi(); });
    mt::topo_view topo{src};
    topo.foreach_gate([&](auto n) {
        std::vector<mt::xag_network::signal> cs;
        src.foreach_fanin(n, [&](auto f) { cs.push_back(map[src.get_node(f)] ^ src.is_complemented(f)); });
        map[n] = src.is_xor(n) ? dest.create_xor(cs[0], cs[1]) : dest.create_and(cs[0], cs[1]);
    });
    std::vector<uint32_t> outputs;
    if (request.find("outputs") != request.end()) outputs = request.at("outputs").get<std::vector<uint32_t>>();
    else for (uint32_t i = 0; i < src.num_pos(); ++i) outputs.push_back(i);
    if (outputs.empty()) throw std::runtime_error("Select at least one output");
    for (auto i : outputs) {
        if (i >= src.num_pos()) throw std::runtime_error("Output index out of range");
        auto f = src.po_at(i);
        dest.create_po(map[src.get_node(f)] ^ src.is_complemented(f));
    }
    return mt::cleanup_dangling(dest);
}


inline mt::xag_network read_source(json const& request) {
        const auto path = request.at("path").get<std::string>();
        std::ifstream input(path);
        if (!input) throw std::runtime_error("Cannot open benchmark: " + path);
        if (path.size() < 2 || path.substr(path.size()-2) != ".v") {
            std::string header;
            std::getline(input, header);
            std::istringstream fields(header);
            std::string magic; uint32_t m, i, l, o, a;
            if (!(fields >> magic >> m >> i >> l >> o >> a) || (magic != "aig" && magic != "aag") || l != 0)
                throw std::runtime_error("Expected combinational AIGER with zero latches");
        }
        mt::xag_network source;
        auto code = path.size() >= 2 && path.substr(path.size()-2) == ".v"
            ? lorina::read_verilog(path, mt::verilog_reader(source))
            : lorina::read_aiger(path, mt::aiger_reader(source));
        if (code != lorina::return_code::success || source.num_pos() == 0)
            throw std::runtime_error("Benchmark parse failed or has no outputs");
        return source;
}
