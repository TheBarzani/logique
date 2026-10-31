#include "../include/sat_pebbling.hpp"
#include <functional>

void rejects(std::function<void()> const& fn) {
    try { fn(); } catch (std::runtime_error const&) { return; }
    throw std::runtime_error("expected rejection");
}
int main() {
    Network<mt::xag_network> ntk;
    const auto a = ntk.create_pi(), b = ntk.create_pi(), c = ntk.create_pi();
    const auto p = ntk.create_and(a,b), q = ntk.create_xor(p,c);
    ntk.create_po(q);
    SatBudget budget{5, 16, 1000, 2};
    auto result = compile_sat(ntk, budget);
    if (result["sat_validation"]["zero_releases"] != 1 || result["num_qubits"] != 5)
        throw std::runtime_error("unexpected tiny SAT result");
    auto pn=ntk.get_node(p), qn=ntk.get_node(q);
    SatEmitter<decltype(ntk)> emitter(ntk, budget);
    rejects([&] { emitter.action(qn, cp::compute_action{}); });
    SatEmitter<decltype(ntk)> clean(ntk, budget);
    rejects([&] { clean.action(pn, cp::buffer_action{}); });
    rejects([&] { clean.action(pn, cp::compute_inplace_action{}); });
    rejects([&] { clean.action(pn, cp::uncompute_inplace_action{}); });
    rejects([&] { clean.action(pn, cp::compute_level_action{}); });
    rejects([&] { clean.action(pn, cp::uncompute_level_action{}); });
    rejects([&] { clean.action(pn, cp::compute_action{std::vector<uint32_t>{}}); });
    clean.action(pn, cp::compute_action{});
    rejects([&] { clean.action(pn, cp::compute_action{}); });
    rejects([&] { clean.finish(); });
    clean.action(qn, cp::compute_action{});
    clean.action(pn, cp::uncompute_action{});
    rejects([&] { clean.action(pn, cp::uncompute_action{}); });
    clean.finish();
    rejects([&] { compile_sat(ntk, SatBudget{4, 1, 1000, 2}); });
    Network<mt::xag_network> large;
    std::vector<mt::xag_network::signal> pis;
    for (unsigned i=0; i<6; ++i) pis.push_back(large.create_pi());
    auto last = pis[0];
    for (unsigned i=0; i<33; ++i)
        last = large.create_and(last, pis[(i+1)%6] ^ bool((i/6)%2));
    large.create_po(last);
    if (large.num_gates() != 33) throw std::runtime_error("invalid gate-cap fixture");
    rejects([&] { compile_sat(large, budget); });
    std::cout << "SAT value/release/action guards passed\n";
}
