#pragma once

// This policy is used ONLY by the explicit xag_low_t path. The legacy recorder
// and its callers retain their original behavior.
struct PhysicalBooleanCircuit : RecordingCircuit {
    json normalizations = json::array();

    void add_gate(td::gate_base const& op, std::vector<td::qubit_id> const& controls,
                  std::vector<td::qubit_id> const& targets) {
        if (!op.is_one_of(td::gate_set::pauli_x, td::gate_set::cx, td::gate_set::mcx)
            || targets.size() != 1)
            throw std::runtime_error("xag_low_t: unsupported physical action");
        auto t = targets.front();
        if (t.index() >= width || t.is_complemented())
            throw std::runtime_error("xag_low_t: invalid physical target");
        std::vector<td::qubit_id> unique;
        std::map<uint32_t, bool> seen;
        bool zero = false;
        json original = json::array(), polarity = json::array();
        for (auto c : controls) {
            // Validate BEFORE zero-conjunction simplification: target aliases
            // are never accepted, including in contradictory conjunctions.
            if (c.index() >= width || c.index() == t.index())
                throw std::runtime_error("xag_low_t: target/control alias or out-of-range control");
            original.push_back(c.index());
            polarity.push_back(!c.is_complemented());
            auto [it, fresh] = seen.emplace(c.index(), c.is_complemented());
            if (fresh) unique.push_back(c);
            else if (it->second != c.is_complemented()) zero = true;
        }
        // |x,t> -> |x,t XOR conjunction(x)> has no phases. For distinct t,
        // l*l=l and l*~l=0 give respectively the reduced controlled X and I.
        // Both are exact permutations and self-inverse on the full Hilbert space.
        if (unique.size() != controls.size()) {
            json reduced = json::array(), reduced_polarity = json::array();
            for (auto c : unique) {
                reduced.push_back(c.index());
                reduced_polarity.push_back(!c.is_complemented());
            }
            normalizations.push_back({{"gate_offset", gates.size()},
                {"controls", original}, {"polarity", polarity}, {"target", t.index()},
                {"rule", zero ? "zero_conjunction" : "idempotent_literals"},
                {"emitted_controls", zero ? json::array() : reduced},
                {"emitted_polarity", zero ? json::array() : reduced_polarity},
                {"emitted_gate_count", zero ? 0 : 1}});
        }
        if (!zero) RecordingCircuit::add_gate(td::gate::mcx, unique, targets);
    }
    void add_gate(td::gate_base const& op, td::qubit_id t) {
        add_gate(op, std::vector<td::qubit_id>{}, std::vector<td::qubit_id>{t});
    }
    void add_gate(td::gate_base const& op, td::qubit_id c, td::qubit_id t) {
        add_gate(op, std::vector<td::qubit_id>{c}, std::vector<td::qubit_id>{t});
    }
};

// Replay only the live-stack/allocator part of the pinned LHRS visitor before
// emission. No action is changed. This guards reads before .top(), released
// wires, and the implicit target skip in compute_big_xor. Keep stale entries
// exactly as pinned LHRS does; a buffer push is not an uncompute/pop.
inline json audit_xag_schedule(mt::xag_network const& ntk) {
    cp::xag_mapping_strategy strategy;
    if (!strategy.compute_steps(ntk))
        throw std::runtime_error("xag_low_t: strategy audit failed");
    std::vector<std::vector<uint32_t>> stacks(ntk.size());
    std::vector<std::vector<uint32_t>> stack_generations(ntk.size());
    std::vector<bool> live;
    std::vector<uint32_t> generations;
    std::vector<uint32_t> free;
    json rows = json::array(), steps = json::array();
    auto allocate = [&]() {
        if (free.empty()) {
            live.push_back(true); generations.push_back(0);
            return uint32_t(live.size() - 1);
        }
        auto q = free.back(); free.pop_back(); live[q] = true; ++generations[q]; return q;
    };
    auto push = [&](uint32_t n, uint32_t q) {
        stacks[n].push_back(q); stack_generations[n].push_back(generations[q]);
    };
    auto top = [&](uint32_t n) {
        if (n >= stacks.size() || stacks[n].empty())
            throw std::runtime_error("xag_low_t: unresolved node stack");
        auto q = stacks[n].back();
        if (q >= live.size() || !live[q] || stack_generations[n].back() != generations[q])
            throw std::runtime_error("xag_low_t: read of released physical wire");
        return q;
    };
    ntk.foreach_pi([&](auto n) { push(n, allocate()); });
    auto cn = ntk.get_node(ntk.get_constant(false));
    if (ntk.fanout_size(cn)) push(cn, allocate());
    strategy.foreach_step([&](auto n, auto const& action) {
        if (n >= stacks.size()) throw std::runtime_error("xag_low_t: invalid action node");
        steps.push_back(action_json(n, action));
        auto row = action_json(n, action);
        auto validate_leaves = [&](uint32_t t, auto const& leaves, bool inplace) {
            json qs = json::array();
            unsigned occurrences = 0;
            for (auto l : leaves) { auto q = top(l); qs.push_back(q); occurrences += q == t; }
            // In-place parity is an invertible XOR onto the old target iff its
            // explicit leaves contain that physical target exactly once here.
            // Reject even/multiple aliases rather than silently skip them.
            if (occurrences != (inplace ? 1u : 0u))
                throw std::runtime_error("xag_low_t: unresolved explicit-leaf target alias");
            row["physical_leaves"] = qs;
        };
        auto validate_node = [&](uint32_t t) {
            if (!ntk.is_and(n) && !ntk.is_xor(n))
                throw std::runtime_error("xag_low_t: unsupported node action");
            json qs = json::array();
            ntk.foreach_fanin(n, [&](auto f) {
                auto q = top(ntk.get_node(f));
                if (q == t) throw std::runtime_error("xag_low_t: node target/control alias");
                qs.push_back(q);
            });
            row["physical_controls"] = qs;
        };
        std::visit(cp::detail::overloaded{
            [&](cp::compute_action const& a) {
                if (a.cell_override) throw std::runtime_error("xag_low_t: unexpected cell action");
                auto t = allocate(); push(n, t); row["physical_target"] = t;
                if (a.leaves) validate_leaves(t, *a.leaves, false); else validate_node(t);
            },
            [&](cp::uncompute_action const& a) {
                if (a.cell_override) throw std::runtime_error("xag_low_t: unexpected cell action");
                auto t = top(n); row["physical_target"] = t;
                if (a.leaves) validate_leaves(t, *a.leaves, false); else validate_node(t);
                // Ordinary uncompute uses the existing stack-pop overlay.
                stacks[n].pop_back(); stack_generations[n].pop_back();
                live[t] = false; free.push_back(t);
            },
            [&](cp::compute_inplace_action const& a) {
                if (!a.leaves) throw std::runtime_error("xag_low_t: missing explicit inplace leaves");
                auto t = top(a.target_index); push(n, t);
                row["physical_target"] = t; validate_leaves(t, *a.leaves, true);
            },
            [&](cp::buffer_action const& a) {
                auto q = top(a.leaf);
                if (a.target >= stacks.size()) throw std::runtime_error("xag_low_t: invalid buffer target");
                push(a.target, q); row["physical_target"] = q;
            },
            [&](auto const&) { throw std::runtime_error("xag_low_t: unsupported schedule action"); }
        }, action);
        rows.push_back(row);
    });
    // prepare_outputs reads the same stacks, then allocates copies for repeated
    // POs. Its complemented first-PO X can change a PI; wrappers must undo it.
    ntk.foreach_po([&](auto f) { top(ntk.get_node(f)); });
    return {{"steps", steps}, {"actions", rows}, {"node_stacks", stacks},
            {"policy", "pinned_lhrs_live_stacks_explicit_leaf_targets"}};
}
