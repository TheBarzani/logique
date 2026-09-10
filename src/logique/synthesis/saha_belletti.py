"""Optional adapter for the unchanged Saha-Belletti comparison dependency."""

from logique.coloring import ColoringProblem

VARIANTS = ("original", "simple", "minimal", "balanced")


def comparison_circuit(
    problem: ColoringProblem, variant: str = "balanced", *, iterations: int = 1
):
    """Build a full Grover circuit; this backend does not implement precolors."""
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

    graph = nx.relabel_nodes(
        problem.to_networkx(), {v: i for i, v in enumerate(problem.vertices)}
    )
    return generate_circuit(
        graph, problem.colors, oracle_type=variant, grover_iterations=iterations
    ).remove_final_measurements(inplace=False)
