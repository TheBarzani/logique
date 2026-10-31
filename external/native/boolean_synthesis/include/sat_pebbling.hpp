#pragma once
#include "actions.hpp"
#include "serialization.hpp"
#include <unordered_set>
#include <abc/satSolver.h>
#include <caterpillar/solvers/bsat_solver.hpp>

// Deliberately separate from the sequential cone/alias validator. Only ordinary
// compute/uncompute, with one physical value per active node, is supported.
struct SatBudget {
    uint32_t qubits, horizons, conflicts, seconds;
};

inline uint32_t sat_integer(json const& request, char const* key, uint32_t cap) {
    auto it = request.find(key);
    if (it == request.end() || !it->is_number_integer() || it->is_boolean())
        throw std::runtime_error(std::string("SAT requires integer ") + key);
    const auto value = it->get<int64_t>();
    if (value < 1 || value > cap)
        throw std::runtime_error(std::string("SAT budget out of range: ") + key);
    return static_cast<uint32_t>(value);
}

inline SatBudget sat_budget(json const& request) {
    return {sat_integer(request, "qubit_budget", 64),
            sat_integer(request, "sat_max_steps", 128),
            sat_integer(request, "sat_conflict_limit", 100000),
            sat_integer(request, "sat_time_seconds", 30)};
}

template<class Ntk> class SatEmitter {
    Ntk const& ntk;
    SatBudget budget;
    uint64_t mask;
    std::vector<uint64_t> values, wires;
    std::vector<int> address;
    std::vector<uint32_t> free;
    json gates = json::array(), steps = json::array();
    json inputs = json::array(), outputs = json::array();
    uint32_t releases = 0, reads = 0, peak = 0, active = 0;

    uint32_t index(typename Ntk::node n) const { return ntk.node_to_index(n); }
    uint32_t allocate() {
        if (!free.empty()) {
            const auto q = free.back(); free.pop_back();
            if (wires[q] != 0) throw std::runtime_error("SAT reuse is not zero");
            return q;
        }
        if (wires.size() >= budget.qubits)
            throw std::runtime_error("SAT emitted width exceeds qubit_budget");
        wires.push_back(0);
        return wires.size() - 1;
    }
    uint32_t read(typename Ntk::node n) {
        const auto i = index(n);
        if (address.at(i) < 0 || wires.at(address[i]) != values[i])
            throw std::runtime_error("SAT inactive or wrong-value operand node=" + std::to_string(i) + " address=" + std::to_string(address.at(i)) + " after=" + steps.dump());
        ++reads;
        return address[i];
    }
    void gate(std::vector<uint32_t> const& controls,
              std::vector<bool> const& polarity, uint32_t target) {
        std::set<uint32_t> distinct(controls.begin(), controls.end());
        if (controls.size() != polarity.size() || distinct.size() != controls.size()
            || distinct.count(target))
            throw std::runtime_error("SAT invalid physical wiring");
        uint64_t toggle = mask;
        for (size_t i = 0; i < controls.size(); ++i)
            toggle &= polarity[i] ? wires.at(controls[i]) : (wires.at(controls[i]) ^ mask);
        wires.at(target) ^= toggle;
        gates.push_back({{"kind", "x"}, {"controls", controls},
                         {"polarity", polarity}, {"target", target}});
    }
    void toggle(typename Ntk::node n, uint32_t target) {
        std::vector<uint32_t> controls;
        std::vector<bool> polarity;
        ntk.foreach_fanin(n, [&](auto f) {
            controls.push_back(read(ntk.get_node(f)));
            polarity.push_back(!ntk.is_complemented(f));
        });
        if (controls.size() != 2) throw std::runtime_error("SAT requires binary gates");
        if (ntk.is_and(n)) gate(controls, polarity, target);
        else if (ntk.is_xor(n)) {
            for (size_t i = 0; i < controls.size(); ++i) {
                gate({controls[i]}, {true}, target);
                if (!polarity[i]) gate({}, {}, target);
            }
        } else throw std::runtime_error("SAT unsupported node kind");
    }
public:
    SatEmitter(Ntk const& net, SatBudget limits) : ntk(net), budget(limits) {
        // Check before truth tables, node maps, or SAT allocations.
        if (ntk.num_pis() > 6 || ntk.num_gates() > 32 || ntk.size() > 64 || ntk.num_pos() > 16)
            throw std::runtime_error("SAT unsupported domain: inputs<=6 gates<=32 nodes<=64 outputs<=16");
        const uint32_t columns = 1u << ntk.num_pis();
        mask = columns == 64 ? ~uint64_t{0} : (uint64_t{1} << columns) - 1;
        values.resize(ntk.size()); address.assign(ntk.size(), -1);
        std::vector<bool> known(ntk.size(), false);
        ntk.foreach_node([&](auto n) {
            if (ntk.is_constant(n)) {
                values[index(n)] = ntk.constant_value(n) ? mask : 0;
                known[index(n)] = true;
            }
        });
        ntk.foreach_pi([&](auto n, auto i) {
            uint64_t table = 0;
            for (uint32_t x = 0; x < columns; ++x)
                if ((x >> i) & 1u) table |= uint64_t{1} << x;
            values[index(n)] = table; known[index(n)] = true;
            auto q = allocate(); address[index(n)] = q;
            wires[q] = table; inputs.push_back(q);
        });
        ntk.foreach_gate([&](auto n) {
            std::vector<uint64_t> operands;
            ntk.foreach_fanin(n, [&](auto f) {
                const auto i = index(ntk.get_node(f));
                if (!known.at(i)) throw std::runtime_error("SAT requires topological network");
                operands.push_back(values[i] ^ (ntk.is_complemented(f) ? mask : 0));
            });
            if (operands.size() != 2 || (!ntk.is_and(n) && !ntk.is_xor(n)))
                throw std::runtime_error("SAT requires binary AIG/XAG");
            values[index(n)] = ntk.is_and(n) ? operands[0] & operands[1] : operands[0] ^ operands[1];
            known[index(n)] = true;
        });
        ntk.foreach_node([&](auto n) {
            if (ntk.is_constant(n) && ntk.fanout_size(n)) {
                auto q = allocate(); address[index(n)] = q;
                if (ntk.constant_value(n)) gate({}, {}, q);
            }
        });
    }
    uint32_t fixed_width() const { return wires.size(); }
    void action(typename Ntk::node n, cp::mapping_strategy_action const& action) {
        const auto i = index(n);
        if (ntk.is_pi(n) || ntk.is_constant(n))
            throw std::runtime_error("SAT action on non-gate");
        bool computing;
        if (auto a = std::get_if<cp::compute_action>(&action)) {
            if (a->leaves || a->cell_override) throw std::runtime_error("SAT unsupported compute payload");
            computing = true;
        } else if (auto a = std::get_if<cp::uncompute_action>(&action)) {
            if (a->leaves || a->cell_override) throw std::runtime_error("SAT unsupported uncompute payload");
            computing = false;
        } else throw std::runtime_error("SAT unsupported action");
        if (steps.size() >= 4096) throw std::runtime_error("SAT action cap exceeded");
        if (computing) {
            if (address.at(i) >= 0) throw std::runtime_error("SAT duplicate live compute");
            auto q = allocate(); address[i] = q;
            toggle(n, q);
            if (wires[q] != values[i]) throw std::runtime_error("SAT wrong computed value");
            peak = std::max(peak, ++active);
        } else {
            auto q = read(n); toggle(n, q);
            if (wires[q] != 0) throw std::runtime_error("SAT nonzero release");
            free.push_back(q); address[i] = -1; --active; ++releases;
        }
        steps.push_back(action_json(i, action));
    }
    json finish() {
        std::set<uint32_t> drivers;
        ntk.foreach_po([&](auto f) { drivers.insert(index(ntk.get_node(f))); });
        ntk.foreach_node([&](auto n) {
            const auto i = index(n);
            if ((!ntk.is_constant(n) && ntk.is_pi(n)) || (ntk.is_constant(n) && address[i] >= 0) || drivers.count(i)) read(n);
            else if (!ntk.is_constant(n) && address[i] >= 0)
                throw std::runtime_error("SAT dirty non-output workspace");
        });
        // Before this boundary PIs are unchanged and every non-output gate is
        // absent/zero. Output preparation may complement a PI, just as LHRS does.
        std::map<uint32_t, bool> first;
        ntk.foreach_po([&](auto f) {
            const auto i = index(ntk.get_node(f));
            if (address.at(i) < 0) throw std::runtime_error("SAT absent output");
            uint32_t q = address[i];
            auto it = first.find(i);
            if (it == first.end()) {
                if (ntk.is_complemented(f)) gate({}, {}, q);
                first[i] = ntk.is_complemented(f);
            } else {
                const auto copy = allocate(); gate({q}, {true}, copy);
                if (it->second != ntk.is_complemented(f)) gate({}, {}, copy);
                q = copy;
            }
            if (wires[q] != (values[i] ^ (ntk.is_complemented(f) ? mask : 0)))
                throw std::runtime_error("SAT wrong prepared output");
            outputs.push_back(q);
        });
        return {{"num_qubits", wires.size()}, {"gates", gates}, {"steps", steps},
                {"input_qubits", inputs}, {"output_qubits", outputs}, {"network", graph_json(ntk)},
                {"sat_validation", {{"truth_table_inputs", ntk.num_pis()}, {"operand_reads", reads},
                    {"zero_releases", releases}, {"peak_gate_values", peak},
                    {"qubit_budget", budget.qubits}, {"cec", "not_performed"},
                    {"domain", "ordinary binary AIG/XAG; clean initial workspace"}}}};
    }
};

template<class Ntk> json compile_sat(Ntk const& ntk, SatBudget const& budget) {
    SatEmitter<Ntk> emitter(ntk, budget);
    json search = json::array();
    if (ntk.num_gates()) {
        if (budget.qubits <= emitter.fixed_width())
            throw std::runtime_error("SAT qubit_budget leaves no gate pebble");
        // Includes all declared inputs and used constants. Output aliases are
        // checked against the same physical width cap during final preparation.
        const auto pebbles = budget.qubits - emitter.fixed_width();
        cp::bsat_pebble_solver<Ntk> solver(ntk, pebbles, budget.conflicts);
        const auto start = std::chrono::steady_clock::now();
        solver.init(); bool solved = false;
        for (uint32_t h = 1; h <= budget.horizons; ++h) {
            if (std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count() >= budget.seconds)
                throw std::runtime_error("SAT search time budget exhausted (no infeasibility proof)");
            solver.add_step(); auto status = solver.solve();
            if (std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count() >= budget.seconds)
                throw std::runtime_error("SAT search time budget exhausted after solver call (unknown)");
            search.push_back({{"horizon", h}, {"status", status == solver.sat() ? "sat" :
                status == solver.unsat() ? "unsat_at_horizon" : "conflict_limit_unknown"}});
            if (status == solver.unknown())
                throw std::runtime_error("SAT conflict budget exhausted (unknown)");
            if (status == solver.sat()) {
                solver.save_model();
                auto steps = solver.extract_result();
                for (auto const& [node, action] : steps) emitter.action(node, action);
                solved = true; break;
            }
        }
        if (!solved) throw std::runtime_error("SAT horizon budget exhausted (no unbounded infeasibility proof)");
    }
    auto result = emitter.finish();
    result["sat_search"] = {{"solver", "caterpillar::bsat_pebble_solver/percy::bsat_wrapper/ABC bsat2"},
        {"horizons", search}, {"max_steps", budget.horizons}, {"conflict_limit_per_solve", budget.conflicts},
        {"search_seconds_between_calls", budget.seconds}, {"solver_wall_timeout_supported", false}};
    return result;
}
