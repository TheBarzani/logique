#include "../include/actions.hpp"
#include "../include/xag_controls.hpp"

// Full basis action proves the real normalized unitary (all phases are +1),
// including arbitrary target bits and the inverse, independently of LHRS.
void check_physical_boolean_controls() {
    unsigned checked = 0;
    for (unsigned mask = 0; mask < 16; ++mask) {
        for (auto indices : {std::vector<uint32_t>{0, 0, 1, 0},
                             std::vector<uint32_t>{1, 0, 1, 0}}) {
            PhysicalBooleanCircuit circ;
            for (int i = 0; i < 3; ++i) circ.add_qubit();
            std::vector<td::qubit_id> cs;
            for (unsigned i = 0; i < indices.size(); ++i)
                cs.emplace_back(indices[i], bool((mask >> i) & 1));
            circ.add_gate(td::gate::mcx, cs, std::vector<td::qubit_id>{2});
            if (circ.normalizations.size() != 1)
                throw std::runtime_error("Missing physical normalization evidence");
            auto apply = [&](unsigned state, bool inverse) {
                auto gates = circ.gates;
                if (inverse) std::reverse(gates.begin(), gates.end());
                for (auto const& g : gates) {
                    bool enabled = true;
                    std::set<unsigned> unique;
                    for (size_t j = 0; j < g["controls"].size(); ++j) {
                        unsigned c = g["controls"][j];
                        if (!unique.insert(c).second || c == g["target"] || c >= 3)
                            throw std::runtime_error("Invalid normalized gate wiring");
                        enabled &= bool((state >> c) & 1) == g["polarity"][j].get<bool>();
                    }
                    if (enabled) state ^= 1u << g["target"].get<unsigned>();
                }
                return state;
            };
            for (unsigned state = 0; state < 8; ++state) {
                bool conjunction = true;
                for (size_t i = 0; i < indices.size(); ++i)
                    conjunction &= bool((state >> indices[i]) & 1) != bool((mask >> i) & 1);
                unsigned expected = state ^ (unsigned(conjunction) << 2);
                if (apply(state, false) != expected || apply(expected, true) != state)
                    throw std::runtime_error("Incorrect Boolean control unitary/inverse");
                ++checked;
            }
        }
    }
    // A contradiction does not excuse a target alias or an out-of-range wire.
    for (auto cs : {std::vector<td::qubit_id>{0, td::qubit_id(0, true), 2},
                    std::vector<td::qubit_id>{0, td::qubit_id(0, true), 3}}) {
        PhysicalBooleanCircuit circ;
        for (int i = 0; i < 3; ++i) circ.add_qubit();
        bool rejected = false;
        try { circ.add_gate(td::gate::mcx, cs, std::vector<td::qubit_id>{2}); }
        catch (std::runtime_error const&) { rejected = true; }
        if (!rejected || !circ.gates.empty()) throw std::runtime_error("Invalid alias accepted");
    }
    for (auto t : {td::qubit_id(3), td::qubit_id(2, true)}) {
        PhysicalBooleanCircuit circ;
        for (int i = 0; i < 3; ++i) circ.add_qubit();
        bool rejected = false;
        try { circ.add_gate(td::gate::pauli_x, t); }
        catch (std::runtime_error const&) { rejected = true; }
        if (!rejected) throw std::runtime_error("Invalid physical target accepted");
    }
    std::cout << "Passed " << checked << " physical Boolean unitary/inverse columns and 4 rejections\n";
}

// Exercise the pinned variant directly: no mapping algorithm is exposed just
// to make its action type reachable. Compare complete rows, including payloads.
int main() {
    try {
        unsigned checked = 0;
        auto check = [&](cp::mapping_strategy_action const& action, json expected) {
            expected["node"] = 42;
            auto actual = action_json(42, action);
            if (actual != expected)
                throw std::runtime_error("Action mismatch: " + actual.dump() + " != " + expected.dump());
            ++checked;
        };
        kitty::dynamic_truth_table truth(2);
        kitty::create_from_binary_string(truth, "0010");
        for (bool uncompute : {false, true}) {
            const auto label = uncompute ? "uncompute" : "compute";
            auto probe = [&](auto const& action) {
                check(action, {{"action", label}, {"explicit_leaves", nullptr}, {"cell_override", nullptr}});
                auto explicit_empty = action;
                explicit_empty.leaves = std::vector<uint32_t>{};
                check(explicit_empty, {{"action", label}, {"explicit_leaves", json::array()},
                                       {"leaves", json::array()}, {"cell_override", nullptr}});
                auto full = action;
                full.leaves = std::vector<uint32_t>{8, 3};
                full.cell_override = std::make_pair(truth, std::vector<uint32_t>{5, 2});
                check(full, {{"action", label}, {"explicit_leaves", {8, 3}}, {"leaves", {5, 2}},
                             {"lut_inputs", 2}, {"cell_override", {{"truth", "0010"}, {"leaves", {5, 2}}}}});
            };
            if (uncompute) probe(cp::uncompute_action{});
            else probe(cp::compute_action{});
        }
        check(cp::compute_inplace_action{7, std::vector<uint32_t>{9, 1}},
              {{"action", "compute_inplace"}, {"target_index", 7}, {"explicit_leaves", {9, 1}}, {"leaves", {9, 1}}});
        check(cp::uncompute_inplace_action{7, std::nullopt},
              {{"action", "uncompute_inplace"}, {"target_index", 7}, {"explicit_leaves", nullptr}});
        check(cp::buffer_action{6, 4}, {{"action", "buffer"}, {"target", 6}, {"leaf", 4}});
        cp::cone_t cone(11, {2, 5}, true);
        cone.target = {13, 7};
        cone.copies = {17, 19};
        cp::level_info_t info = {{23, {cone, cp::cone_t(3, {3})}}, {29, {}}};
        json cones = json::array({
            {{"root", 11}, {"leaves", {2, 5}}, {"complemented", true}, {"target", {13, 7}}, {"copies", {17, 19}}},
            {{"root", 3}, {"leaves", {3}}, {"complemented", false}, {"target", json::array()}, {"copies", json::array()}}
        });
        json level = json::array({{{"node", 23}, {"cones", cones}}, {{"node", 29}, {"cones", json::array()}}});
        check(cp::compute_level_action{info}, {{"action", "compute_level"}, {"level", level}});
        check(cp::uncompute_level_action{info}, {{"action", "uncompute_level"}, {"level", level}});
        check(cp::compute_level_action{}, {{"action", "compute_level"}, {"level", json::array()}});
        check(cp::uncompute_level_action{}, {{"action", "uncompute_level"}, {"level", json::array()}});
        std::cout << "Passed " << checked << " exact action rows across all 7 pinned variants\n";
        check_physical_boolean_controls();
    } catch (std::exception const& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
