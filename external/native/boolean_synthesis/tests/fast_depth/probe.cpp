// Diagnostic only: expose actual pinned level actions and unmodified LHRS gates.
// A successful exit is emission, never a value/restoration certificate.
#include "../../include/actions.hpp"
#include "../../include/serialization.hpp"
#include "../../include/input.hpp"
#include <caterpillar/synthesis/strategies/xag_mapping_strategy.hpp>

struct BoundedRecordingCircuit : RecordingCircuit {
    uint32_t budget = 128;
    void add_qubit() {
        if (width >= budget) throw std::runtime_error("diagnostic width budget exceeded");
        RecordingCircuit::add_qubit();
    }
};

mt::xag_network fixture(std::string const& name, json& program) {
    mt::xag_network n;
    // Deliberately asymmetric positions, and one unused declared input.
    auto b = n.create_pi(), a = n.create_pi(), c = n.create_pi();
    auto unused = n.create_pi();
    if (name == "asymmetric") n.create_po(n.create_and(a, !b));
    else if (name == "equal" || name == "opposite") {
        auto p = n.create_xor(a, b), q = n.create_xor(b, c);
        auto l = n.create_xor(p, c), r = n.create_xor(a, q);
        n.create_po(n.create_and(l, name == "equal" ? r : !r));
    } else if (name == "shared") {
        auto p = n.create_and(a, b);
        n.create_po(n.create_and(p, c));
        n.create_po(n.create_and(p, !c));
    } else if (name == "overlap") {
        auto p = n.create_xor(a, b), q = n.create_xor(b, c);
        n.create_po(n.create_and(p, c));
        n.create_po(n.create_and(q, a));
    } else if (name == "alias") {
        n.create_po(!b); n.create_po(b); n.create_po(n.get_constant(false));
        n.create_po(n.get_constant(true));
    } else if (name == "zero_output") {
        // No selected outputs: cleanup retains PIs and removes all gates.
    } else if (name == "zero") n.create_po(n.get_constant(false));
    else if (name == "xor") n.create_po(n.create_xor(a, c));
    else if (name == "above_cap") {
        for (unsigned i = 0; i < 3; ++i) n.create_pi();
        n.create_po(a);
    } else if (name.rfind("generated-", 0) == 0) {
        const auto index = std::stoul(name.substr(10));
        if (index >= 8) throw std::runtime_error("generated fixture index0..7");
        uint64_t state = 1101052342 + index;
        auto random = [&]() {
            state ^= state << 13; state ^= state >> 7; state ^= state << 17;
            return state;
        };
        std::vector<mt::xag_network::signal> signals{b, a, c, unused};
        program = {{"seed", 1101052342 + index}, {"operations", json::array()}};
        for (unsigned i = 0; i < 12; ++i) {
            const auto left = random() % signals.size();
            const auto right = random() % signals.size();
            const bool conjunction = random() & 1;
            const bool negate = conjunction && (random() & 1);
            signals.push_back(conjunction ? n.create_and(signals[left], negate ? !signals[right] : signals[right])
                                          : n.create_xor(signals[left], signals[right]));
            program["operations"].push_back({{"lhs", left}, {"rhs", right},
                {"kind", conjunction ? "and" : "xor"}, {"negate_rhs", negate}});
        }
        n.create_po(signals.back()); n.create_po(!signals[signals.size() - 2]); n.create_po(b);
        program["outputs"] = {{15, false}, {14, true}, {0, false}};
    } else throw std::runtime_error("unknown fixture");
    return mt::cleanup_dangling(n);
}

template<class Strategy> json run(mt::xag_network const& n, Strategy& strategy,
                                  uint32_t budget) {
    // No global truth-table or LHRS/strategy containers before these caps.
    if (n.num_pis() > 6 || n.size() > 64 || n.num_pos() > 16)
        throw std::runtime_error("diagnostic domain cap inputs6/nodes64/outputs16");
    if (!strategy.compute_steps(n)) throw std::runtime_error("strategy failed");
    json scheduled = json::array();
    strategy.foreach_step([&](auto node, auto const& action) {
        if (scheduled.size() >= 128) throw std::runtime_error("diagnostic action cap128");
        scheduled.push_back(action_json(node, action));
    });
    // LHRS recomputes the schedule: use a fresh strategy to avoid appending it.
    Strategy emitted_strategy;
    BoundedRecordingCircuit circ;
    circ.budget = budget;
    cp::logic_network_synthesis_stats stats;
    if (!cp::logic_network_synthesis(circ, n, emitted_strategy, RecordLut{}, {}, &stats))
        throw std::runtime_error("LHRS failed");
    json emitted = json::array();
    emitted_strategy.foreach_step([&](auto node, auto const& action) {
        emitted.push_back(action_json(node, action));
    });
    if (emitted != scheduled) throw std::runtime_error("schedule changed");
    return {{"network", graph_json(n)}, {"steps", scheduled}, {"gates", circ.gates},
            {"input_qubits", stats.i_indexes}, {"output_qubits", stats.o_indexes},
            {"num_qubits", circ.width}, {"diagnostic_only", true}};
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--json") {
            json request;
            std::cin >> request;
            if (!request.is_object()) throw std::runtime_error("request object required");
            for (auto it = request.begin(); it != request.end(); ++it)
                if (it.key() != "path" && it.key() != "strategy" && it.key() != "qubit_budget" && it.key() != "preprocessing" && it.key() != "outputs")
                    throw std::runtime_error("unsupported private control: " + it.key());
            auto const& value = request.at("qubit_budget");
            if (!value.is_number_integer() || value.is_boolean() || value.get<int64_t>() < 1 || value.get<int64_t>() > 128)
                throw std::runtime_error("wire budget requires integer1..128");
            const auto budget = value.get<uint32_t>();
            const auto policy = request.at("preprocessing").get<std::string>();
            if (policy != "none" && policy != "refactoring") throw std::runtime_error("unknown preprocessing");
            auto source = read_source(request);
            const bool selected_outputs = request.find("outputs") != request.end();
            if (selected_outputs) {
                if (!request.at("outputs").is_array() || request.at("outputs").size() > 16)
                    throw std::runtime_error("selected output cap16");
                for (auto const& output : request.at("outputs"))
                    if (!output.is_number_integer() || output.is_boolean() || output.get<int64_t>() < 0 || output.get<int64_t>() >= source.num_pos())
                        throw std::runtime_error("selected output integer/range");
            }
            mt::xag_network n;
            if (selected_outputs && request.at("outputs").empty())
                source.foreach_pi([&](auto) { n.create_pi(); });
            else n = select_outputs(source, request);
            n = mt::cleanup_dangling(n);
            if (policy == "refactoring") {
                mt::bidecomposition_resynthesis<mt::xag_network> resyn;
                mt::refactoring(n, resyn);
                n = mt::cleanup_dangling(n);
            }
            const auto name = request.at("strategy").get<std::string>();
            json result;
            if (name == "fast") {
                cp::xag_fast_lowt_mapping_strategy strategy;
                result = run(n, strategy, budget);
                result["implementation"] = "caterpillar::xag_fast_lowt_mapping_strategy";
            } else if (name == "depth") {
                cp::xag_low_depth_mapping_strategy strategy;
                result = run(n, strategy, budget);
                result["implementation"] = "caterpillar::xag_low_depth_mapping_strategy";
            } else throw std::runtime_error("unknown strategy");
            result["private_request"] = {{"strategy", name}, {"qubit_budget", budget}, {"preprocessing", policy}};
            if (selected_outputs) result["private_request"]["outputs"] = request.at("outputs");
            std::cout << result.dump() << '\n';
            return 0;
        }
        if (argc != 3 && argc != 4)
            throw std::runtime_error("usage: probe fast|depth fixture [wire-budget]");
        uint32_t budget = 128;
        if (argc == 4) {
            const std::string text(argv[3]);
            if (text.empty() || text.find_first_not_of("0123456789") != std::string::npos)
                throw std::runtime_error("wire budget requires integer1..128");
            const auto value = std::stoul(text);
            if (value < 1 || value > 128)
                throw std::runtime_error("wire budget requires integer1..128");
            budget = value;
        }
        json program;
        const auto n = fixture(argv[2], program);
        json result;
        if (std::string(argv[1]) == "fast") {
            cp::xag_fast_lowt_mapping_strategy strategy;
            result = run(n, strategy, budget);
            result["implementation"] = "caterpillar::xag_fast_lowt_mapping_strategy";
        } else if (std::string(argv[1]) == "depth") {
            cp::xag_low_depth_mapping_strategy strategy;
            result = run(n, strategy, budget);
            result["implementation"] = "caterpillar::xag_low_depth_mapping_strategy";
        } else throw std::runtime_error("unknown strategy");
        if (!program.is_null()) result["source_program"] = program;
        std::cout << result.dump() << '\n';
    } catch (std::exception const& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
