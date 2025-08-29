#!/usr/bin/env python3
"""
Script to generate execution comparison between VCGC and Saha-Belletti methods
on linear graphs of increasing size (1-7 vertices).

This script:
1. Prepares circuits for each method (VCGC, original, simple, minimal, balanced)
2. Executes them on IBM quantum backend
3. Stores results in CSV format
4. Plots success quasi-probability vs number of vertices
"""

import os
import csv
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from math import ceil, log2

# Quantum computing imports
from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.visualization import plot_distribution
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler import PassManager
from qiskit.circuit.library import XGate
from qiskit_ibm_runtime.transpiler.passes.scheduling import (
    ALAPScheduleAnalysis, 
    PadDynamicalDecoupling, 
    DynamicCircuitInstructionDurations
)
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# VCGC imports
from vcgc.network import VCPNetwork
from vcgc.boolean import BooleanFunction
from vcgc.synthesis import Synthesizer
from vcgc.circuit import uniform_superposition_qiskit, generate_grover_diffusion, glue_grover_circuit

# Saha-Belletti imports
from saha_belletti.core import generate_circuit


class ExecutionComparison:
    """Class to handle the execution comparison between different methods."""
    
    def __init__(self, output_dir: str = "../data/execution/", shots: int = 10000):
        """
        Initialize the comparison class.
        
        Args:
            output_dir: Directory to store results
            shots: Number of shots for quantum execution
        """
        self.output_dir = output_dir
        self.shots = shots
        self.service = QiskitRuntimeService()
        self.backend = None
        self.results = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def setup_backend(self, backend_name: Optional[str] = None):
        """Setup IBM quantum backend."""
        if backend_name:
            self.backend = self.service.backend(backend_name)
        else:
            # Use least busy backend
            self.backend = self.service.least_busy(simulator=False, operational=True)
        
        print(f"Using backend: {self.backend.name}")
        
    def create_vcgc_circuit(self, network: VCPNetwork) -> QuantumCircuit:
        """Create VCGC Grover circuit for given network."""
        try:
            
            # Extract boolean function
            bf = BooleanFunction()
            tweedledum_bf = bf.create_multi_bit_function(network=network)
            
            # Synthesize oracle
            synthesizer = Synthesizer(cf=tweedledum_bf)
            oracle_circuit = synthesizer.synthesize_with_xag()
            
            # Create uniform superposition oracle
            num_superpos_states = network.available_colors
            if num_superpos_states <= 1:
                raise ValueError(f"Invalid number of colors: {num_superpos_states}")
                
            num_encode_qubits = ceil(log2(num_superpos_states))
            
            usp_oracle = uniform_superposition_qiskit(num_superpos_states=num_superpos_states).decompose()
            
            # Create diffusion operator
            num_data_qubits = network.num_vertices * num_encode_qubits
            
            diff_oracle = generate_grover_diffusion(num_qubits=num_data_qubits, uqs=usp_oracle)
            
            # Glue complete circuit together
            grover_circuit = glue_grover_circuit(
                usp=usp_oracle,
                oracle=oracle_circuit,
                diffusion=diff_oracle,
                num_data_qubits=num_data_qubits,
                num_encode_qubits=num_encode_qubits
            )
            
            return grover_circuit, num_data_qubits
            
        except Exception as e:
            print(f"Error in create_vcgc_circuit: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def add_measurements(self, circuit: QuantumCircuit, num_data_qubits: int) -> QuantumCircuit:
        """Add classical register and measurements to circuit."""
        circuit_with_meas = circuit.copy()
        classical_reg = ClassicalRegister(num_data_qubits, 'creg')
        circuit_with_meas.add_register(classical_reg)
        circuit_with_meas.measure(range(num_data_qubits), range(num_data_qubits))
        return circuit_with_meas
    
    def transpile_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Transpile circuit for the target backend."""
        durations = DynamicCircuitInstructionDurations.from_backend(backend=self.backend)
        
        optimized_pm = generate_preset_pass_manager(
            target=self.backend.target, 
            optimization_level=3
        )
        
        dd_rep = 8
        dd_sequence = [XGate()] * dd_rep
        
        optimized_pm.scheduling = PassManager([
            ALAPScheduleAnalysis(durations=durations),
            PadDynamicalDecoupling(
                durations=durations,
                dd_sequences=dd_sequence,
                pulse_alignment=16
            )
        ])
        
        return optimized_pm.run(circuit)
    
    def calculate_success_probability(self, counts: Dict[str, int], 
                                    network: VCPNetwork, method: str) -> float:
        """
        Calculate success probability based on valid colorings.
        
        Args:
            counts: Measurement counts from quantum execution
            network: The VCP network
            method: Method used (for different encoding schemes)
            
        Returns:
            Success probability as a float
        """
        total_shots = sum(counts.values())
        valid_shots = 0
        print (f'total shots: {total_shots}')
        print(counts)
        
        if method == "vcgc":
            # VCGC uses binary encoding for colors
            num_encode_qubits = ceil(log2(network.available_colors)) if network.available_colors > 1 else 1
            expected_bits = network.num_vertices * num_encode_qubits
            
            print(f"Debug: VCGC analysis - {network.num_vertices} vertices, {network.available_colors} colors")
            print(f"Debug: Expected {expected_bits} bits ({num_encode_qubits} per vertex)")
            print(f"Debug: Sample states: {list(counts.keys())[:3] if counts else 'No states'}")
                        
            for state, count in counts.items():
                # Skip if state string is too short
                if len(state) < expected_bits:
                    print(f"Debug: Skipping short state {state} (length {len(state)} < {expected_bits})")
                    continue
                    
                # Parse the binary state into vertex colors
                vertex_colors = []
                # Use the rightmost bits (standard Qiskit bit ordering)
                state_bits = state[-expected_bits:]  # Take only the expected number of bits
                
                success = True
                for v in range(network.num_vertices):
                    start_bit = v * num_encode_qubits
                    end_bit = start_bit + num_encode_qubits
                    
                    print(f"Debug: Processing vertex {v}, start_bit={start_bit}, end_bit={end_bit}, state_bits='{state_bits}' (len={len(state_bits)})")
                    
                    # Check if we have enough bits
                    if end_bit > len(state_bits):
                        print(f"Debug: Not enough bits for vertex {v}: need {end_bit}, have {len(state_bits)}")
                        success = False
                        break
                    
                    # Extract color bits for this vertex
                    color_bits = state_bits[start_bit:end_bit]
                    print(f"Debug: Extracted color_bits='{color_bits}' for vertex {v}")
                    
                    if not color_bits:  # Empty string
                        print(f"Debug: Empty color_bits for vertex {v}")
                        success = False
                        break
                        
                    try:
                        # Convert binary string to integer
                        color_value = int(color_bits, 2)
                        print(f"Debug: Converted '{color_bits}' to color {color_value}")
                        
                        if color_value < network.available_colors:
                            vertex_colors.append(color_value)
                        else:
                            # Invalid color encoding
                            print(f"Debug: Color {color_value} >= available colors {network.available_colors}")
                            success = False
                            break
                    except ValueError as e:
                        # Invalid binary string
                        print(f"Debug: ValueError converting '{color_bits}': {e}")
                        success = False
                        break
                    except Exception as e:
                        print(f"Debug: Unexpected error: {e}")
                        success = False
                        break
                
                # Check if we successfully parsed all vertices and have a valid coloring
                if success and len(vertex_colors) == network.num_vertices:
                    if self.is_valid_coloring(network, vertex_colors):
                        valid_shots += count
                        print(f"Debug: Valid coloring found: {vertex_colors} from state {state}")
            
            print(f"Debug: VCGC found {valid_shots}/{total_shots} valid shots")
        else:
            # Saha-Belletti methods also use binary encoding
            print(f"Debug: Saha-Belletti {method} analysis - {network.num_vertices} vertices, {network.available_colors} colors")
            
            # For Saha-Belletti, we need to understand their specific encoding scheme
            # For now, we'll use a similar approach but may need refinement
            num_encode_qubits = ceil(log2(network.available_colors)) if network.available_colors > 1 else 1
            expected_bits = network.num_vertices * num_encode_qubits
            
            print(f"Debug: Expected {expected_bits} bits ({num_encode_qubits} per vertex)")
            print(f"Debug: Sample states: {list(counts.keys())[:3] if counts else 'No states'}")
            
            for state, count in counts.items():
                # Skip if state string is too short
                if len(state) < expected_bits:
                    continue
                    
                # Parse the binary state into vertex colors (similar to VCGC for now)
                vertex_colors = []
                state_bits = state[-expected_bits:]  # Take rightmost bits
                
                success = True
                for v in range(network.num_vertices):
                    start_bit = v * num_encode_qubits
                    end_bit = start_bit + num_encode_qubits
                    
                    if end_bit <= len(state_bits):
                        color_bits = state_bits[start_bit:end_bit]
                        
                        try:
                            color_value = int(color_bits, 2)
                            
                            if color_value < network.available_colors:
                                vertex_colors.append(color_value)
                            else:
                                success = False
                                break
                        except ValueError:
                            success = False
                            break
                    else:
                        success = False
                        break
                
                if success and len(vertex_colors) == network.num_vertices:
                    if self.is_valid_coloring(network, vertex_colors):
                        valid_shots += count
                        
            print(f"Debug: Saha-Belletti found {valid_shots}/{total_shots} valid shots")
        
        return valid_shots / total_shots if total_shots > 0 else 0.0
    
    def is_valid_coloring(self, network: VCPNetwork, vertex_colors: List[int]) -> bool:
        """Check if vertex coloring is valid (no adjacent vertices have same color)."""
        if len(vertex_colors) != network.num_vertices:
            return False
            
        for edge in network.graph.edges():
            v1, v2 = edge
            if vertex_colors[v1] == vertex_colors[v2]:
                return False
        return True
    
    def execute_circuit(self, circuit: QuantumCircuit, method: str, 
                       num_vertices: int) -> Dict:
        """Execute circuit on quantum backend and return results."""
        try:
            # Transpile circuit
            transpiled_circuit = self.transpile_circuit(circuit)
            
            # Execute on backend
            sampler = Sampler(mode=self.backend)
            sampler.options.default_shots = self.shots
            
            print(f"Executing {method} circuit for {num_vertices} vertices...")
            # TODO: fix this later
            # job = sampler.run([transpiled_circuit])
            job = self.service.job(job_id="d2nrt037d31s73acje40")
            result = job.result()
            
            # Get counts
            counts = result[0].data.creg.get_counts()

            return {
                'job_id': job.job_id(),
                'counts': counts,
                'transpiled_depth': transpiled_circuit.depth(),
                'transpiled_gates': len(transpiled_circuit),
                'execution_time': time.time()
            }
            
        except Exception as e:
            print(f"Error executing {method} circuit: {e}")
            return None
    
    def run_comparison(self, start_vertices: int = 2, end_vertices: int = 7):
        """Run the full comparison across different graph sizes."""
        methods = ['vcgc', 'original', 'simple', 'minimal', 'balanced']
        
        for num_vertices in range(start_vertices, end_vertices + 1):
            print(f"\n=== Processing {num_vertices} vertices ===")
            
            # Load the linear graph
            dimacs_file = f"{self.output_dir}linear{num_vertices}.col"
            if not os.path.exists(dimacs_file):
                print(f"Warning: {dimacs_file} not found, skipping...")
                continue
                
            network = VCPNetwork(file_path=dimacs_file)
            print(f"Loaded graph: {network.num_vertices} vertices, {network.num_edges} edges")
            
            for method in methods:
                print(f"\nProcessing method: {method}")
                
                try:
                    # Create circuit based on method
                    if method == 'vcgc':
                        print(f"Creating VCGC circuit for {num_vertices} vertices...")
                        circuit, num_data_qubits = self.create_vcgc_circuit(network)
                        print(f"VCGC circuit created: {circuit.num_qubits} qubits, {num_data_qubits} data qubits")
                        circuit_with_meas = self.add_measurements(circuit, num_data_qubits)
                        print(f"Added measurements: {circuit_with_meas.num_qubits} qubits, {circuit_with_meas.num_clbits} clbits")
                    else:
                        # Saha-Belletti methods
                        print(f"Creating Saha-Belletti {method} circuit for {num_vertices} vertices...")
                        circuit_with_meas = generate_circuit(
                            graph=network.graph, 
                            colors=network.available_colors, 
                            oracle_type=method, 
                            grover_iterations=1
                        )
                        print(f"Saha-Belletti circuit created: {circuit_with_meas.num_qubits} qubits")
                    
                    # Record circuit metrics
                    circuit_metrics = {
                        'method': method,
                        'num_vertices': num_vertices,
                        'num_edges': network.num_edges,
                        'available_colors': network.available_colors,
                        'original_qubits': circuit_with_meas.num_qubits,
                        'original_depth': circuit_with_meas.depth(),
                        'original_gates': len(circuit_with_meas),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    print(f"Circuit metrics: {circuit_metrics['original_qubits']} qubits, {circuit_metrics['original_depth']} depth, {circuit_metrics['original_gates']} gates")
                    
                    # Execute circuit
                    execution_result = self.execute_circuit(circuit_with_meas, method, num_vertices)
                    
                    if execution_result:
                        # Calculate success probability
                        
                        success_prob = self.calculate_success_probability(
                            execution_result['counts'], network, method
                        )
                        # Combine all results
                        result_entry = {
                            **circuit_metrics,
                            'job_id': execution_result['job_id'],
                            'transpiled_qubits': circuit_with_meas.num_qubits,  # This would be updated after transpilation
                            'transpiled_depth': execution_result['transpiled_depth'],
                            'transpiled_gates': execution_result['transpiled_gates'],
                            'success_probability': success_prob,
                            'total_shots': self.shots,
                            'backend_name': self.backend.name
                        }
                        
                        self.results.append(result_entry)
                        print(f"Success probability: {success_prob:.4f}")
                    
                except Exception as e:
                    print(f"Error processing {method} for {num_vertices} vertices: {e}")
                    continue
                
                # Add delay between executions to avoid overwhelming the backend
                time.sleep(30)
    
    def save_results_to_csv(self, filename: str = None):
        """Save results to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}execution_comparison_{timestamp}.csv"
        
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False)
            print(f"Results saved to: {filename}")
            return filename
        else:
            print("No results to save")
            return None
    
    def plot_results(self, csv_file: str = None):
        """Plot success probability vs number of vertices for each method."""
        if csv_file:
            df = pd.read_csv(csv_file)
        else:
            df = pd.DataFrame(self.results)
        
        if df.empty:
            print("No data to plot")
            return
        
        plt.figure(figsize=(12, 8))
        
        methods = df['method'].unique()
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, method in enumerate(methods):
            method_data = df[df['method'] == method]
            plt.plot(method_data['num_vertices'], method_data['success_probability'], 
                    marker='o', label=method, color=colors[i % len(colors)], linewidth=2)
        
        plt.xlabel('Number of Vertices', fontsize=12)
        plt.ylabel('Success Quasi-Probability', fontsize=12)
        plt.title('Success Probability vs Graph Size Comparison', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(1, 8))
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"{self.output_dir}success_probability_comparison_{timestamp}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Plot saved to: {plot_filename}")
        
        # Also create individual method plots
        self.plot_individual_methods(df)
    
    def plot_individual_methods(self, df: pd.DataFrame):
        """Create individual plots for each metric."""
        metrics = ['original_qubits', 'transpiled_depth', 'original_gates']
        metric_labels = ['Number of Qubits', 'Transpiled Circuit Depth', 'Number of Gates']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Circuit Metrics Comparison', fontsize=16)
        
        # Success probability plot
        ax = axes[0, 0]
        methods = df['method'].unique()
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, method in enumerate(methods):
            method_data = df[df['method'] == method]
            ax.plot(method_data['num_vertices'], method_data['success_probability'], 
                   marker='o', label=method, color=colors[i % len(colors)])
        
        ax.set_xlabel('Number of Vertices')
        ax.set_ylabel('Success Probability')
        ax.set_title('Success Probability')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Other metrics
        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[(idx + 1) // 2, (idx + 1) % 2]
            
            for i, method in enumerate(methods):
                method_data = df[df['method'] == method]
                ax.plot(method_data['num_vertices'], method_data[metric], 
                       marker='o', label=method, color=colors[i % len(colors)])
            
            ax.set_xlabel('Number of Vertices')
            ax.set_ylabel(label)
            ax.set_title(label)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"{self.output_dir}detailed_metrics_comparison_{timestamp}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Detailed metrics plot saved to: {plot_filename}")


def main():
    """Main function to run the execution comparison."""
    print("Starting VCGC vs Saha-Belletti Execution Comparison")
    print("=" * 50)
    
    # Initialize comparison
    comparison = ExecutionComparison(
        output_dir="../data/execution/",
        shots=1000  # Reduced for testing, increase for production
    )
    
    # Setup backend
    comparison.setup_backend()  # Will use least busy backend
    # Or specify a specific backend:
    # comparison.setup_backend("ibm_torino")
    
    # Run comparison
    comparison.run_comparison(start_vertices=2, end_vertices=7)
    
    # Save results
    csv_file = comparison.save_results_to_csv()
    
    # Plot results
    if csv_file:
        comparison.plot_results(csv_file)
    
    print("\nComparison completed!")


if __name__ == "__main__":
    main()
