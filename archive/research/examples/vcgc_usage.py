#!/usr/bin/env python3
"""
Example demonstrating how to use the vcgc package
"""

import vcgc
from qiskit.qasm3 import dump

def main():
    print("=== VCGC Package Demo ===")
    print(f"Package version: {vcgc.__version__}")
    print(f"Available modules: {vcgc.__all__}")
    print()

    # 1. Create a VCP Network
    print("1. Creating a VCP Network...")
    network = vcgc.VCPNetwork()
    network.read_dimacs("data/benchmarks/K5.col") # Read Dimacs file
    network.draw_graph(name="data/output/graph.png", node_size=500) # Draw nice graph using NetworkX
    
    # 2. Create a Boolean Function
    print("\n2. Creating a Boolean Function...")
    bf = vcgc.BooleanFunction() 
    bf.print_vertex_constraints(network)
    # For multi-bit representation (each vertex uses multiple bits)
    tweedledum_func_multibit = bf.create_multi_bit_function(network)

    # 3. Create a Synthesizer
    print("\n3. Creating a Synthesizer...")
    synthesizer = vcgc.Synthesizer(tweedledum_func_multibit)
    synthesizer.synthesize_with_xag()
    synthesizer.print_circuit_info()
    with open("data/output/example.qasm","w") as f:
        dump(circuit=synthesizer.qiskit_circuit, stream=f)
    synthesizer.draw_circuit(filename='data/output/grover_oracle.png')
    print(f"The circuit depth: {synthesizer.qiskit_circuit.depth()}")

    print("\n=== Demo completed successfully! ===")
    print("\nThe vcgc package is now ready to use!")
    print("You can import it in any Python script with: import vcgc")

    # Testing with verilog
    # bf.create_manual_verilog(network, "data/output/manual_coloring.v")
    # bf.write_verilog_with_custom_mapping(network, "data/output/manual_coloring_custom.v")
    # synthesizer.from_verilog_file("data/output/manual_coloring.v")
    # synthesizer.synthesize_with_xag()
    # synthesizer.print_circuit_info()
    # synthesizer.draw_circuit(filename='data/output/grover_oracle_verilog.png')

if __name__ == "__main__":
    main()
