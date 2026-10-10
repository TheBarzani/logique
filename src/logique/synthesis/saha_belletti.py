"""Optional adapter for the unchanged Saha-Belletti comparison dependency."""

from logique.coloring import ColoringProblem

VARIANTS = ("original", "simple", "minimal", "balanced")


def comparison_circuit(
    problem: ColoringProblem,
    variant: str = "balanced",
    *,
    iterations: int = 1,
    preserve_labels: bool = False,
    measure: bool = False,
):
    """Build a Grover circuit; optionally preserve labels for historical replay.

    Defaults normalize vertex labels and omit measurements. Historical replay
    can retain the original indexing and measured dependency output explicitly.
    This backend does not implement precolors.
    """
    if problem.precolored:
        raise ValueError(
            "Saha-Belletti does not support precolored vertices; use an unprecolored comparison input"
        )
    if variant not in VARIANTS or problem.colors < 2 or not problem.vertices:
        raise ValueError(
            "Saha-Belletti requires a known variant, vertices, and at least two colors"
        )
    if type(iterations) is not int or iterations < 0:
        raise ValueError("iterations must be nonnegative")
    import networkx as nx
    from saha_belletti.core import generate_circuit

    graph = problem.to_networkx()
    if not preserve_labels:
        graph = nx.relabel_nodes(graph, {v: i for i, v in enumerate(problem.vertices)})
    circuit = generate_circuit(
        graph, problem.colors, oracle_type=variant, grover_iterations=iterations
    )
    return circuit if measure else circuit.remove_final_measurements(inplace=False)
