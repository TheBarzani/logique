#pragma once
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

