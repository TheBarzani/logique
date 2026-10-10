#pragma once
#include "types.hpp"
template<class Ntk> json graph_json(Ntk const& ntk) {
    json g = {{"nodes", json::array()}, {"inputs", json::array()}, {"outputs", json::array()}};
    ntk.foreach_pi([&](auto n) { g["inputs"].push_back(ntk.node_to_index(n)); });
    mt::topo_view topo{ntk};
    topo.foreach_node([&](auto n) {
        json row = {{"id", ntk.node_to_index(n)}, {"fanins", json::array()}};
        if (ntk.is_constant(n)) { row["kind"] = "constant"; row["value"] = ntk.constant_value(n); }
        else if (ntk.is_pi(n)) row["kind"] = "input";
        else {
            row["kind"] = "lut";
            if constexpr (mt::has_is_and_v<Ntk>) if (ntk.is_and(n)) row["kind"] = "and";
            if constexpr (mt::has_is_xor_v<Ntk>) if (ntk.is_xor(n)) row["kind"] = "xor";
            row["truth"] = kitty::to_binary(ntk.node_function(n));
            ntk.foreach_fanin(n, [&](auto f) {
                row["fanins"].push_back({{"node", ntk.node_to_index(ntk.get_node(f))}, {"inverted", ntk.is_complemented(f)}});
            });
        }
        g["nodes"].push_back(row);
    });
    ntk.foreach_po([&](auto f) {
        g["outputs"].push_back({{"node", ntk.node_to_index(ntk.get_node(f))}, {"inverted", ntk.is_complemented(f)}});
    });
    return g;
}

