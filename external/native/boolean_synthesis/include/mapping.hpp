#pragma once
#include "serialization.hpp"
template<class Ntk, class Strategy> json compile(Ntk const& ntk, Strategy& strategy) {
    RecordingCircuit circ;
    cp::logic_network_synthesis_stats stats;
    if (!cp::logic_network_synthesis(circ, ntk, strategy, RecordLut{}, {}, &stats))
        throw std::runtime_error("Mapping strategy failed");
    json steps = json::array();
    strategy.foreach_step([&](auto n, auto const& a) {
        std::string action = std::holds_alternative<cp::compute_action>(a) ? "compute" : "uncompute";
        json row = {{"node", ntk.node_to_index(n)}, {"action", action}};
        auto add_cell = [&](auto const& step) {
            if (step.cell_override) {
                row["lut_inputs"] = step.cell_override->second.size();
                row["leaves"] = step.cell_override->second;
            }
        };
        if (auto step = std::get_if<cp::compute_action>(&a)) add_cell(*step);
        if (auto step = std::get_if<cp::uncompute_action>(&a)) add_cell(*step);
        steps.push_back(row);
    });
    return {{"num_qubits", circ.width}, {"gates", circ.gates}, {"input_qubits", stats.i_indexes},
            {"output_qubits", stats.o_indexes}, {"steps", steps}, {"network", graph_json(ntk)}};
}


inline json map_network(mt::xag_network const& selected, json const& request) {
        auto xag = mt::cleanup_dangling(selected);
        mt::bidecomposition_resynthesis<mt::xag_network> resyn;
        mt::refactoring(xag, resyn);
        xag = mt::cleanup_dangling(xag);
        const auto method = request.value("method", std::string("xag"));
        json result;
        if (method == "xag") result = {{"network", graph_json(xag)}};
        else if (method == "aig_bennett") {
            Network<mt::aig_network> ntk(mt::cleanup_dangling<mt::xag_network, mt::aig_network>(selected));
            cp::bennett_mapping_strategy<decltype(ntk)> strategy;
            result = compile(ntk, strategy);
        } else if (method == "xag_bennett") {
            Network<mt::xag_network> ntk(xag);
            cp::bennett_mapping_strategy<decltype(ntk)> strategy;
            result = compile(ntk, strategy);
        } else if (method == "klut_bennett") {
            const int k = request.value("k", 4);
            if (k < 2 || k > 6) throw std::runtime_error("k must be between 2 and 6");
            mt::mapping_view<mt::xag_network, true> mapped(xag);
            mt::lut_mapping_params ps; ps.cut_enumeration_ps.cut_size = k;
            mt::lut_mapping<decltype(mapped), true>(mapped, ps);
            auto collapsed = mt::collapse_mapped_network<mt::klut_network>(mapped);
            if (!collapsed) throw std::runtime_error("LUT collapse failed");
            Network<mt::klut_network> ntk(*collapsed);
            cp::bennett_mapping_strategy<decltype(ntk)> strategy;
            result = compile(ntk, strategy);
        } else if (method == "best_fit") {
            Network<mt::xag_network> ntk(xag);
            cp::best_fit_mapping_strategy_params ps;
            ps.cut_size = request.value("outer_cut", 16);
            ps.cut_lower_bound = request.value("inner_cut", 4);
            if (ps.cut_lower_bound < 2 || ps.cut_size > 16 || ps.cut_lower_bound > ps.cut_size)
                throw std::runtime_error("Require 2 <= inner_cut <= outer_cut <= 16");
            cp::best_fit_mapping_strategy<decltype(ntk)> strategy(ps);
            result = compile(ntk, strategy);
        } else throw std::runtime_error("Unknown synthesis method");
        return result;
}
