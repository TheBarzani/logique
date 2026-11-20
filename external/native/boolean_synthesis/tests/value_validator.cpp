#include "../include/mapping.hpp"

using namespace xag_value;

template<class F> void rejects(F&& f, std::string const& reason) {
    try { f(); }
    catch (std::runtime_error const& e) {
        require(std::string(e.what()).find(reason) != std::string::npos,
                "wrong rejection: " + std::string(e.what()) + ", wanted " + reason);
        return;
    }
    throw std::runtime_error("mutation accepted: " + reason);
}

json check_cones() {
    // Five independent boundary bits, all 1024 frontier pairs and singleton
    // boundary/root aliases. No dense matrices or statevectors.
    std::vector<uint64_t> bits(7, 0);
    for (uint32_t i = 0; i < 5; ++i)
        for (uint32_t x = 0; x < 32; ++x) bits[i] |= uint64_t((x >> i) & 1) << x;
    uint32_t variants = 0, stale = 0;
    std::map<std::string, uint32_t> classes;
    for (unsigned a = 0; a < 32; ++a) for (unsigned b = 0; b < 32; ++b) {
        Leaves left, right;
        for (unsigned i = 0; i < 5; ++i) {
            if ((a >> i) & 1) left.push_back(i);
            if ((b >> i) & 1) right.push_back(i);
        }
        std::string relation = !a || !b ? "empty" : a == b ? "equal" :
            ((a & b) == a || (a & b) == b) ? "included" : "incomparable";
        ++classes[relation];
        Leaves roots_a{5}, roots_b{6};
        if (left.size() == 1) roots_a.push_back(left[0]);
        if (right.size() == 1) roots_b.push_back(right[0]);
        for (auto ra : roots_a) for (auto rb : roots_b) {
            auto values = bits;
            for (auto l : left) values[5] ^= values[l];
            for (auto l : right) values[6] ^= values[l];
            Machine m(values, 0xffffffff);
            std::set<uint32_t> active;
            std::map<uint32_t, Frame> before;
            for (uint32_t i = 0; i < 5; ++i) {
                auto q = m.allocate(); m.push(i, q); m.wires[q] = values[i];
                active.insert(i); before[i] = {q, values[i]};
            }
            std::vector<Leaves> fi(7);
            fi[ra] = left; fi[rb] = right;
            auto cs = cones(ra, rb, fi);
            std::vector<Frame> frames;
            for (auto const& c : cs) {
                auto step = cone_step(c, false);
                if (step.is_null()) { auto q = m.read(c.root); frames.push_back({q, m.wires[q]}); }
                else frames.push_back(m.action(step, nullptr, false));
            }
            m.read(ra); m.read(rb);
            for (size_t i = cs.size(); i-- > 0;) {
                auto step = cone_step(cs[i], true);
                if (!step.is_null()) {
                    auto frame = m.action(step, nullptr, true);
                    m.restored(frames[i], frame, cs[i].leaves.empty());
                }
            }
            m.boundary(before, active);
            for (uint32_t n = 5; n < 7; ++n)
                if (!m.stacks[n].empty() && m.wires[m.top(n)] != values[n]) ++stale;
            ++variants;
        }
    }
    return {{"frontier_pairs", 1024}, {"variants", variants}, {"classes", classes},
            {"stale_unread_aliases", stale}, {"assignments", 32}};
}

json check_negatives() {
    Machine m({0xa, 0xc, 0x6}, 0xf);
    for (uint32_t n = 0; n < 2; ++n) {
        auto q = m.allocate(); m.push(n, q); m.wires[q] = m.values[n];
    }
    m.wires[0] ^= 1;
    rejects([&] { m.read(0); }, "wrong live operand value");
    m.wires[0] ^= 1;
    rejects([&] { m.release(0, 0); }, "dirty release");
    Cone c{2, {0, 1}, {0}};
    auto frame = m.action(cone_step(c, false), nullptr, false);
    // A live alias can hold the correct cone value while its PI anchor is dirty.
    m.read(2);
    rejects([&] { m.restored(frame, frame, false); }, "missing cone restoration");
    auto after = m.action(cone_step(c, true), nullptr, true);
    m.restored(frame, after, false);
    // Restoring parity resolved PI0 only as an address; its value was 0x6.
    // The stale XOR alias is legal until somebody attempts an actual read.
    rejects([&] { m.read(2); }, "wrong live operand value");
    auto q = m.allocate(); m.push(2, q); m.release(2, q);
    m.allocate();
    m.stacks[2].push_back({q, 0});
    rejects([&] { m.top(2); }, "stale generation");
    caps(6, 256, 256, 4096);
    rejects([&] { caps(7, 1, 0, 0); }, "inputs exceed 6");
    rejects([&] { caps(0, 257, 0, 0); }, "nodes exceed 256");
    rejects([&] { caps(0, 1, 257, 0); }, "width exceeds 256");
    rejects([&] { caps(0, 1, 0, 4097); }, "steps exceed 4096");
    return {{"rejections", 9}};
}

json check_domain() {
    mt::xag_network ntk;
    auto a = ntk.create_pi(), b = ntk.create_pi(), c = ntk.create_pi();
    auto p = ntk.create_xor(a, b);
    auto out = ntk.create_and(p, c);
    ntk.create_po(out);
    Domain d(ntk);
    auto reference = expected(d);
    cp::xag_mapping_strategy strategy;
    PhysicalBooleanCircuit circuit;
    auto actual = compile(ntk, strategy, circuit);
    match(reference, actual);
    for (auto key : {"gates", "steps", "output_qubits", "input_qubits", "num_qubits"}) {
        auto changed = actual;
        if (std::string(key) == "num_qubits") changed[key] = 0;
        else changed[key] = json::array();
        rejects([&] { match(reference, changed); }, std::string("actual emitted ") + key);
    }
    auto altered = actual;
    altered["gates"][0]["controls"][0] = 2;
    rejects([&] { match(reference, altered); }, "emitted gates");
    auto dirty = mt::xag_network(std::make_shared<mt::xag_storage>(*ntk._storage));
    dirty.create_and(a, b);
    rejects([&] { Domain bad(dirty); }, "not cleaned");
    auto polarity = mt::xag_network(std::make_shared<mt::xag_storage>(*ntk._storage));
    polarity._storage->nodes[p.index].children[0].weight = 1;
    rejects([&] { Domain bad(polarity); }, "noncanonical XOR polarity");
    auto constant = mt::xag_network(std::make_shared<mt::xag_storage>(*ntk._storage));
    constant._storage->nodes[out.index].children[0].index = 0;
    rejects([&] { Domain bad(constant); }, "unsimplified constant");
    auto order = mt::xag_network(std::make_shared<mt::xag_storage>(*ntk._storage));
    order._storage->nodes[out.index].children[1].index = out.index + 1;
    rejects([&] { Domain bad(order); }, "nontopological fanin");
    auto input_order = mt::xag_network(std::make_shared<mt::xag_storage>(*ntk._storage));
    input_order._storage->inputs[0] = 250;
    rejects([&] { Domain bad(input_order); }, "noncanonical PI");
    mt::xag_network seq;
    auto ro = seq.create_ro(); seq.create_po(ro);
    rejects([&] { Domain bad(seq); }, "sequential network");
    mt::xag_network many;
    for (int i = 0; i < 7; ++i) many.create_pi();
    rejects([&] { Domain bad(many); }, "inputs exceed 6");
    mt::xag_network wide;
    auto x = wide.create_pi(), y = wide.create_pi();
    wide.create_pi();
    auto z = wide.create_and(x, y);
    for (int i = 0; i < 256; ++i) wide.create_po(z);
    rejects([&] { Domain bad(wide); }, "width exceeds 256");
    return {{"domain_rejections", 8}, {"emission_mutations", 6}, {"certificate", reference["certificate"]}};
}
int main() {
    try {
        std::cout << json({{"cones", check_cones()}, {"negatives", check_negatives()},
                          {"domain", check_domain()}}).dump() << '\n';
    } catch (std::exception const& e) { std::cerr << e.what() << '\n'; return 1; }
}
