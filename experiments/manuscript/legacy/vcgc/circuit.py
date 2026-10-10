# A module to handle state preparation, oracle attachment, and diffusion circuit generations for grover's circuit

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library.data_preparation.state_preparation import UniformSuperpositionGate
from math import ceil, log2

# Create a quantum subcircuit for grover diffusion operator
def generate_grover_diffusion(num_qubits: int, uqs: QuantumCircuit = None) -> QuantumCircuit:
    # Create a quantum subcircuit for grover diffusion operator
    if uqs == None:
        grover_diff = QuantumCircuit(num_qubits, name="grover_diffusion")
        grover_diff.h(range(num_qubits))
        grover_diff.x(range(num_qubits))
        grover_diff.h(num_qubits - 1)
        grover_diff.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        grover_diff.h(num_qubits - 1)
        grover_diff.x(range(num_qubits))
        grover_diff.h(range(num_qubits))
    else:
        grover_diff = QuantumCircuit(num_qubits, name="grover_diffusion")
        num_encode_qubits = uqs.num_qubits
        for vertex in range(num_qubits // num_encode_qubits):
            start_qubit = vertex * num_encode_qubits
            end_qubit = start_qubit + num_encode_qubits
            grover_diff.compose(uqs.inverse(), qubits=range(start_qubit, end_qubit), inplace=True)
        grover_diff.x(range(num_qubits))
        grover_diff.h(num_qubits - 1)
        grover_diff.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        grover_diff.h(num_qubits - 1)
        grover_diff.x(range(num_qubits))
        for vertex in range(num_qubits // num_encode_qubits):
            start_qubit = vertex * num_encode_qubits
            end_qubit = start_qubit + num_encode_qubits
            grover_diff.compose(uqs, qubits=range(start_qubit, end_qubit), inplace=True)
    return grover_diff


def uniform_superposition(M, n) -> QuantumCircuit:
    """
    Creates a quantum circuit that prepares a uniform superposition state over M basis states.
    This function generates a quantum circuit that creates the uniform superposition state:
    (1/√M) * Σ|j⟩ for j from 0 to M-1, using the minimum number of qubits required 
    ($\frac{1}{\sqrt{M}} \sum_{j=0}^{M-1} \ket{j} $).
    The algorithm uses a recursive approach based on the binary representation of M,
    applying controlled rotations and Hadamard gates to achieve the desired amplitudes.
    Args:
        M (int): A positive integer with 2 < M < 2^n, where M is not equal to 2^r 
                for any natural number r. This represents the number of basis states
                in the uniform superposition.
        n (int): The number of qubits to use. Should be at least ceil(log2(M)) to
                accommodate all M states.
    Returns:
        QuantumCircuit: A quantum circuit that prepares the uniform superposition state
                    when applied to the |0⟩^⊗n initial state.
    Note:
        The function assumes M is not a power of 2, as such cases can be handled
        more simply with just Hadamard gates. The circuit uses controlled Y-rotations
        and controlled Hadamard gates to achieve the precise amplitudes required
        for uniform superposition.
    """
    N = [int(x) for x in list(np.binary_repr(M))][::-1]
    k = len(N)
    L = [index for (index, item) in enumerate(N) if item == 1]  # Locations of '1's
    
    qcircuit = QuantumCircuit(n)
    qcircuit.x(L[1:k])
    Mcurrent = 2**(L[0])
    theta = -2*np.arccos(np.sqrt(Mcurrent/M))
    
    if L[0] > 0:  # if M is even
        qcircuit.h(range(L[0]))
        qcircuit.ry(theta, L[1])
        qcircuit.ch(L[1], range(L[0], L[1]), ctrl_state='0')
    
    for m in range(1, len(L) - 1):
        theta = -2*np.arccos(np.sqrt(2**L[m]/(M - Mcurrent)))
        qcircuit.cry(theta, L[m], L[m+1], ctrl_state='0')
        qcircuit.ch(L[m+1], range(L[m], L[m+1]), ctrl_state='0')
        Mcurrent = Mcurrent + 2**(L[m])
    
    # Note: Removed display() call as it requires IPython/Jupyter
    # display(qcircuit.draw('mpl'))
    return qcircuit

def uniform_superposition_qiskit(num_superpos_states: int, num_qubits: int = None) -> QuantumCircuit:
    """
    Creates a quantum circuit that prepares a uniform superposition state over M basis states.
    
    Args:
        num_superpos_states (int): Number of basis states in the uniform superposition
        num_qubits (int): Number of qubits to use
    
    Returns:
        QuantumCircuit: Circuit that prepares the uniform superposition state
    """
    
    # Create the gate
    usup_gate = UniformSuperpositionGate(num_superpos_states=num_superpos_states, num_qubits=num_qubits)
    
    if not num_qubits:
        num_qubits = ceil(log2(num_superpos_states))
    # Create circuit and add the gate
    qcircuit = QuantumCircuit(num_qubits)
    qcircuit.append(usup_gate, range(num_qubits))
    
    return qcircuit

def glue_grover_circuit(usp: QuantumCircuit, oracle: QuantumCircuit, diffusion: QuantumCircuit, num_data_qubits: int, num_encode_qubits: int) -> QuantumCircuit:
    """
    Glues together the uniform superposition, oracle, and diffusion circuits to create a complete Grover circuit.
    
    Args:
        usp (QuantumCircuit): Uniform superposition preparation circuit
        oracle (QuantumCircuit): Oracle circuit that marks the target states
        diffusion (QuantumCircuit): Grover diffusion operator
        num_data_qubits (int): Total number of data qubits
        num_encode_qubits (int): Number of qubits per vertex encoding
    
    Returns:
        QuantumCircuit: Complete Grover circuit
    """
    # Create the main circuit with enough qubits for all components
    total_qubits = max(usp.num_qubits, oracle.num_qubits, diffusion.num_qubits)
    grover_circuit = QuantumCircuit(total_qubits, name="grover_circuit")
    
    # Step 1: Apply uniform superposition to prepare initial state
    # This prepares each vertex in superposition of valid colors
    for vertex in range(num_data_qubits // num_encode_qubits):
        start_qubit = vertex * num_encode_qubits
        end_qubit = start_qubit + num_encode_qubits
        grover_circuit.compose(usp, qubits=range(start_qubit, end_qubit), inplace=True)
    grover_circuit.x(num_data_qubits)
    grover_circuit.h(num_data_qubits)
    
    # Step 2: Apply oracle (marks invalid colorings)
    grover_circuit.barrier()
    grover_circuit.compose(oracle, inplace=True)
    
    # Step 3: Apply diffusion operator
    grover_circuit.barrier()
    grover_circuit.compose(diffusion, inplace=True)
    
    return grover_circuit

def glue_grover_circuit_with_iterations(usp: QuantumCircuit, oracle: QuantumCircuit, diffusion: QuantumCircuit, 
                                      num_data_qubits: int, num_encode_qubits: int, iterations: int = 1) -> QuantumCircuit:
    """
    Creates a complete Grover circuit with multiple iterations.
    
    Args:
        iterations (int): Number of Grover iterations (oracle + diffusion)
    """
    total_qubits = max(usp.num_qubits, oracle.num_qubits, diffusion.num_qubits)
    grover_circuit = QuantumCircuit(total_qubits, name=f"grover_circuit_{iterations}_iter")
    
    # Step 1: Apply uniform superposition
    for vertex in range(num_data_qubits // num_encode_qubits):
        start_qubit = vertex * num_encode_qubits
        end_qubit = start_qubit + num_encode_qubits
        grover_circuit.compose(usp, qubits=range(start_qubit, end_qubit), inplace=True)
    
    # Step 2: Apply Grover iterations
    for iteration in range(iterations):
        grover_circuit.barrier()
        grover_circuit.compose(oracle, inplace=True)
        grover_circuit.barrier()
        grover_circuit.compose(diffusion, inplace=True)
    
    return grover_circuit