#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <json.hpp>
#include <mockturtle/networks/aig.hpp>
#include <mockturtle/networks/xag.hpp>
#include <mockturtle/networks/klut.hpp>
#include <mockturtle/io/aiger_reader.hpp>
#include <mockturtle/io/verilog_reader.hpp>
#include <mockturtle/algorithms/cleanup.hpp>
#include <mockturtle/algorithms/refactoring.hpp>
#include <mockturtle/algorithms/node_resynthesis/bidecomposition.hpp>
#include <mockturtle/algorithms/lut_mapping.hpp>
#include <mockturtle/algorithms/collapse_mapped.hpp>
#include <mockturtle/views/mapping_view.hpp>
#include <caterpillar/synthesis/lhrs.hpp>
#include <caterpillar/synthesis/strategies/bennett_mapping_strategy.hpp>
#include <caterpillar/synthesis/strategies/best_fit_mapping_strategy.hpp>

using json = nlohmann::json;
namespace mt = mockturtle;
namespace cp = caterpillar;
namespace td = tweedledum;

// The pinned LHRS visitor instantiates level handlers even for simple strategies.
template<class Base> struct Network : Base {
    Network() = default;
    explicit Network(Base const& b) : Base(b) {}
    bool is_nary_xor(typename Base::node const&) const { return false; }
    bool is_and(typename Base::node const& n) const {
        if constexpr (mt::has_is_and_v<Base>) return Base::is_and(n);
        return false;
    }
    bool is_xor(typename Base::node const& n) const {
        if constexpr (mt::has_is_xor_v<Base>) return Base::is_xor(n);
        return false;
    }
};

struct RecordingCircuit {
    uint32_t width = 0;
    json gates = json::array();
    uint32_t num_qubits() const { return width; }
    void add_qubit() { ++width; }
    void add_gate(td::gate_base const& op, std::vector<td::qubit_id> const& controls,
                  std::vector<td::qubit_id> const& targets) {
        if (!op.is_one_of(td::gate_set::pauli_x, td::gate_set::cx, td::gate_set::mcx))
            throw std::runtime_error("Unexpected gate in reference synthesis");
        json cs = json::array(), polarity = json::array();
        for (auto c : controls) { cs.push_back(c.index()); polarity.push_back(!c.is_complemented()); }
        for (auto t : targets)
            gates.push_back({{"kind", "x"}, {"controls", cs}, {"polarity", polarity}, {"target", t.index()}});
    }
    void add_gate(td::gate_base const& op, td::qubit_id t) {
        add_gate(op, std::vector<td::qubit_id>{}, std::vector<td::qubit_id>{t});
    }
    void add_gate(td::gate_base const& op, td::qubit_id c, td::qubit_id t) {
        add_gate(op, std::vector<td::qubit_id>{c}, std::vector<td::qubit_id>{t});
    }
};

struct RecordLut {
    void operator()(RecordingCircuit& circ, std::vector<td::qubit_id> const& qs,
                    kitty::dynamic_truth_table const& tt) const {
        json controls = json::array(), polarity = json::array();
        for (size_t i = 0; i + 1 < qs.size(); ++i) {
            controls.push_back(qs[i].index()); polarity.push_back(!qs[i].is_complemented());
        }
        circ.gates.push_back({{"kind", "lut"}, {"controls", controls}, {"polarity", polarity},
                              {"target", qs.back().index()}, {"truth", kitty::to_binary(tt)}});
    }
};

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

int main() {
    try {
        json req; std::cin >> req;
        const auto start = std::chrono::steady_clock::now();
        const auto path = req.at("path").get<std::string>();
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
        auto selected = select_outputs(source, req);
        auto xag = mt::cleanup_dangling(selected);
        mt::bidecomposition_resynthesis<mt::xag_network> resyn;
        mt::refactoring(xag, resyn);
        xag = mt::cleanup_dangling(xag);
        const auto method = req.value("method", std::string("xag"));
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
            const int k = req.value("k", 4);
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
            ps.cut_size = req.value("outer_cut", 16);
            ps.cut_lower_bound = req.value("inner_cut", 4);
            if (ps.cut_lower_bound < 2 || ps.cut_size > 16 || ps.cut_lower_bound > ps.cut_size)
                throw std::runtime_error("Require 2 <= inner_cut <= outer_cut <= 16");
            cp::best_fit_mapping_strategy<decltype(ntk)> strategy(ps);
            result = compile(ntk, strategy);
        } else throw std::runtime_error("Unknown synthesis method");
        result["source_network"] = graph_json(selected);
        result["method"] = method;
        result["native_seconds"] = std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout << result.dump() << '\n';
    } catch (std::exception const& e) {
        std::cerr << e.what() << '\n'; return 1;
    }
}
