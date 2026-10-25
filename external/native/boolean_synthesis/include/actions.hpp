#pragma once
#include "types.hpp"

// No catch-all overload: a new pinned variant must fail compilation until its
// payload has an explicit serialization contract.
struct ActionJsonVisitor {
    template<class Action> json leaves(Action const& action, const char* label) const {
        json row = {{"action", label}};
        row["explicit_leaves"] = action.leaves ? json(*action.leaves) : json(nullptr);
        if (action.leaves) row["leaves"] = *action.leaves;
        return row;
    }

    template<class Action> json cell(Action const& action, const char* label) const {
        auto row = leaves(action, label);
        row["cell_override"] = nullptr;
        if (action.cell_override) {
            auto const& [truth, inputs] = *action.cell_override;
            row["cell_override"] = {{"truth", kitty::to_binary(truth)}, {"leaves", inputs}};
            row["lut_inputs"] = inputs.size();
            // Retain the old cell-leaf column for existing schedule displays.
            row["leaves"] = inputs;
        }
        return row;
    }

    json level(cp::level_info_t const& info, const char* label) const {
        json entries = json::array();
        for (auto const& [node, cones] : info) {
            json data = json::array();
            for (auto const& cone : cones)
                data.push_back({{"root", cone.root}, {"leaves", cone.leaves},
                                {"complemented", cone.complemented},
                                {"target", cone.target}, {"copies", cone.copies}});
            entries.push_back({{"node", node}, {"cones", data}});
        }
        return {{"action", label}, {"level", entries}};
    }

    json operator()(cp::compute_action const& a) const { return cell(a, "compute"); }
    json operator()(cp::uncompute_action const& a) const { return cell(a, "uncompute"); }
    json operator()(cp::compute_inplace_action const& a) const {
        auto row = leaves(a, "compute_inplace");
        row["target_index"] = a.target_index;
        return row;
    }
    json operator()(cp::uncompute_inplace_action const& a) const {
        auto row = leaves(a, "uncompute_inplace");
        row["target_index"] = a.target_index;
        return row;
    }
    json operator()(cp::buffer_action const& a) const {
        return {{"action", "buffer"}, {"target", a.target}, {"leaf", a.leaf}};
    }
    json operator()(cp::compute_level_action const& a) const { return level(a.level, "compute_level"); }
    json operator()(cp::uncompute_level_action const& a) const { return level(a.level, "uncompute_level"); }
};

inline json action_json(uint32_t node, cp::mapping_strategy_action const& action) {
    auto row = std::visit(ActionJsonVisitor{}, action);
    row["node"] = node;
    return row;
}
