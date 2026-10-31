#pragma once
#include "serialization.hpp"
#include "actions.hpp"
#include "sat_pebbling.hpp"
template<class Ntk, class Strategy> json compile(Ntk const& ntk, Strategy& strategy) {
    RecordingCircuit circ;
    cp::logic_network_synthesis_stats stats;
    if (!cp::logic_network_synthesis(circ, ntk, strategy, RecordLut{}, {}, &stats))
        throw std::runtime_error("Mapping strategy failed");
    json steps = json::array();
    strategy.foreach_step([&](auto n, auto const& a) {
        steps.push_back(action_json(ntk.node_to_index(n), a));
    });
    return {{"num_qubits", circ.width}, {"gates", circ.gates}, {"input_qubits", stats.i_indexes},
            {"output_qubits", stats.o_indexes}, {"steps", steps}, {"network", graph_json(ntk)}};
}

// Instantiate the pinned classes, rather than relabeling Bennett schedules.
template<class Ntk> json compile_bennett(Ntk const& ntk, std::string const& name) {
    if (name == "bennett_inplace") {
        cp::bennett_inplace_mapping_strategy<Ntk> strategy;
        return compile(ntk, strategy);
    }
    if (name == "eager") {
        cp::eager_mapping_strategy<Ntk> strategy;
        return compile(ntk, strategy);
    }
    cp::bennett_mapping_strategy<Ntk> strategy;
    return compile(ntk, strategy);
}

inline json map_network(mt::xag_network const& selected, json const& request) {
        const auto method = request.value("method", std::string("xag"));
        const bool explicit_strategy = request.find("strategy") != request.end();
        const auto strategy = explicit_strategy ? request.at("strategy").get<std::string>() : "bennett";
        if (explicit_strategy && method != "aig_bennett" && method != "xag_bennett")
            throw std::runtime_error("strategy is supported only for AIG/XAG Bennett methods");
        if (strategy != "bennett" && strategy != "bennett_inplace" && strategy != "eager" && strategy != "sat_pebbling")
            throw std::runtime_error("strategy must be bennett, bennett_inplace, eager or sat_pebbling");
        const bool common = request.find("preprocessing") != request.end();
        const auto policy = common ? request.at("preprocessing").get<std::string>()
                                   : (method == "aig_bennett" ? "none" : "refactoring");
        if (policy != "none" && policy != "refactoring")
            throw std::runtime_error("preprocessing must be none or refactoring");
        for (auto it = request.begin(); it != request.end(); ++it) {
            const auto& key = it.key();
            if (key == "path" || key == "method" || key == "outputs" || key == "preprocessing" || key == "strategy") continue;
            if (strategy == "sat_pebbling" && (key == "qubit_budget" || key == "sat_max_steps" || key == "sat_conflict_limit" || key == "sat_time_seconds")) continue;
            if (key == "k" && method == "klut_bennett") continue;
            if ((key == "inner_cut" || key == "outer_cut") && method == "best_fit") continue;
            throw std::runtime_error("Unsupported synthesis control: " + key);
        }
        auto xag = mt::cleanup_dangling(selected);
        if (policy == "refactoring") {
            mt::bidecomposition_resynthesis<mt::xag_network> resyn;
            mt::refactoring(xag, resyn);
            xag = mt::cleanup_dangling(xag);
        }
        json result;
        if (method == "xag") result = {{"network", graph_json(xag)}};
        else if (method == "aig_bennett") {
            Network<mt::aig_network> ntk(mt::cleanup_dangling<mt::xag_network, mt::aig_network>(xag));
            result = strategy == "sat_pebbling" ? compile_sat(ntk, sat_budget(request)) : compile_bennett(ntk, strategy);
        } else if (method == "xag_bennett") {
            Network<mt::xag_network> ntk(xag);
            result = strategy == "sat_pebbling" ? compile_sat(ntk, sat_budget(request)) : compile_bennett(ntk, strategy);
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
        const std::string name = method == "xag" ? "xag_synth" :
                                 method == "best_fit" ? "best_fit" : strategy;
        result["mapping_strategy"] = {{"name", name}, {"explicit", explicit_strategy},
            {"implementation", method == "xag" ? "tweedledum::xag_synth" :
                name == "sat_pebbling" ? "logique::bounded_sat_pebbling" :
                "caterpillar::" + name + "_mapping_strategy"}};
        result["preprocessing"] = {{"policy", policy}, {"common", common},
                                   {"before_network", graph_json(selected)},
                                   {"after_network", graph_json(xag)}};
        return result;
}
