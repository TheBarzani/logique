from saha_belletti.core import *
from vcgc import *
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def main():
    """
    This will be a walk through on how to use the saha_belletti package.
    
    I am currently thinking as follows:
        1. Read a dimacs file 
        2. Generate a NetworkX graph
        3. Pass the generated graph to the saha_belleti package
        4. Generate oracle circuits from simple, minimal, balanced, and original
        5. Save the circuits in qasm3 netlist format

    INPUT:
        - Dimacs File
    
    OUTPUT:
        - QASM3 Netlist
    """
    print('\n')
    # 1. Create a wrapper VCPNetwork
    network = VCPNetwork()
    network.read_dimacs("data/benchmarks/K5.col")

    # 2. Generate Saha-Belleti Circuits
    qc: QuantumCircuit = generate_circuit(graph=network.graph, colors=network.available_colors, oracle_type='original', grover_iterations=1) # grover_iterations
    print(f"Saha-Belletti circuit depth: {qc.depth()}")
    # qc.draw(output="mpl")

    # 3. Create a Boolean Function
    bf = BooleanFunction() 
    # For multi-bit representation (each vertex uses multiple bits)
    tweedledum_func_multibit = bf.create_multi_bit_function(network)

    # 4. Create a Synthesizer and VCGC circuits
    synthesizer = Synthesizer(tweedledum_func_multibit)
    synthesizer.synthesize_with_xag()
    print(f"VCGC circuit depth: {synthesizer.qiskit_circuit.depth()}")
    # synthesizer.qiskit_circuit.draw(output="mpl")

if __name__ == "__main__":
    main()