#include "../include/actions.hpp"

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
    } catch (std::exception const& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
