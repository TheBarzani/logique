"""Complete-search costs under alternative preparations and rotation synthesis.

The oracle does not depend on how the valid colors are prepared, so these
helpers rebuild only the preparation A and the diffusion operator
A(2|0><0| - I)A^dagger of a search instance with another construction, price
them, and combine them with an oracle cost and an iteration count:

    T = T_A + j (T_oracle + T_diffusion) + R · t(epsilon),

where R counts the approximated rotations of the whole search, which share the
error budget (epsilon = budget / R), and t is the T-count of one rotation under
the chosen synthesis model. Exact repeat-until-success rotations take no share
of the budget and add their expected T-count.
"""

from qiskit import QuantumCircuit


def prepared_components(problem, instance, method: str):
    """Preparation and diffusion operator of ``instance`` built with ``method``.

    ``problem`` supplies the true number of colors (the R3 encoding uses 2^c).
    The method's ancillas take the instance's clean workspace first, then new
    wires. Returns the two circuits, the ancillas used, and the wires that stay
    clean while multi-controlled gates of these circuits act.
    """
    from logique.circuits.preparation import search_preparation

    bits = max(1, (problem.colors - 1).bit_length())
    groups = [
        list(range(i * bits, (i + 1) * bits)) for i in range(len(problem.vertices))
    ]
    local = search_preparation(problem, groups, method)
    data = list(instance.data)
    extra = local.num_qubits - len(data)
    width = instance.oracle.num_qubits
    spare = list(instance.clean)
    appended = list(range(width, width + max(0, extra - len(spare))))
    ancillas = [*spare[:extra], *appended]
    wires = [*data, *ancillas]
    total = width + len(appended)
    preparation = QuantumCircuit(total)
    preparation.compose(local, wires, inplace=True)
    if instance.form == "kick-back":
        target = instance.roles["output"][0]
        preparation.x(target)
        preparation.h(target)
    # The reflection acts on every wire that A^dagger may leave in a state
    # other than |0>: the amplified preparation entangles its extra wires with
    # the data unless the data hold a good state, whereas the other methods
    # return their ancillas clean for any input.
    reflected = [*data, *ancillas] if method == "amplitude_amplified" else data
    diffusion = QuantumCircuit(total)
    diffusion.compose(local.inverse(), wires, inplace=True)
    diffusion.x(reflected)
    diffusion.h(reflected[-1])
    diffusion.mcx(reflected[:-1], reflected[-1])
    diffusion.h(reflected[-1])
    diffusion.x(reflected)
    diffusion.compose(local, wires, inplace=True)
    clean = [w for w in [*instance.clean, *appended] if w not in ancillas]
    return preparation, diffusion, ancillas, clean


def component_counts(circuit, policy: str, clean) -> dict:
    """Exact Clifford+T counts after the study's MCX policy and relative phases.

    The throwaway tree is not valid outside a mirrored block, so it falls back
    to the restoring tree, as in the study.
    """
    from .costs import decompose_mcx, ft_counts, paired_relative_phase_toffolis

    restoring = "clean_tree" if policy == "throwaway_tree" else policy
    expanded, _ = decompose_mcx(circuit, restoring, clean_wires=clean)
    return ft_counts(paired_relative_phase_toffolis(expanded))


def search_total(
    preparation: dict,
    diffusion: dict,
    oracle_t: float,
    iterations: int,
    *,
    model: str = "ross_selinger",
    budget: float = 1e-3,
) -> dict:
    """Combine component counts into the T-count of a complete search."""
    from .costs import rotation_t_count

    j = iterations
    rotations = preparation["rotation_count"] + j * diffusion["rotation_count"]
    per_rotation = rotation_t_count(budget / rotations, model) if rotations else 0
    exact = preparation["t_count"] + j * (oracle_t + diffusion["t_count"])
    expected = preparation["rus_expected_t"] + j * diffusion["rus_expected_t"]
    return {
        "iterations": j,
        "t_exact": exact,
        "rotations": rotations,
        "t_per_rotation": per_rotation,
        "t_rotations": rotations * per_rotation,
        "t_exact_rotations": expected,
        "t_total": exact + rotations * per_rotation + expected,
    }
