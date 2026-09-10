// One JSON request on stdin; machine-readable response on stdout.
#include "include/input.hpp"
#include "include/mapping.hpp"

int main() {
    try {
        json request;
        std::cin >> request;
        const auto start = std::chrono::steady_clock::now();
        auto selected = select_outputs(read_source(request), request);
        auto result = map_network(selected, request);
        result["source_network"] = graph_json(selected);
        result["method"] = request.value("method", std::string("xag"));
        result["native_seconds"] = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        std::cout << result.dump() << '\n';
    } catch (std::exception const& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
