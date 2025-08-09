#!/usr/bin/env python3
"""
Benchmark Generation Script for VCGC vs Saha-Belletti Comparison

This script automates the process of generating circuits and metrics for both
VCGC and Saha-Belletti approaches across multiple benchmark files.

Based on the comparative analysis from comparing_vcgc_to_saha_belletti.ipynb
"""

import os
import glob
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import traceback

# Core libraries
from vcgc.network import VCPNetwork
from vcgc.boolean import BooleanFunction
from vcgc.synthesis import Synthesizer
from vcgc.circuit import uniform_superposition_qiskit, generate_grover_diffusion, glue_grover_circuit

# Tweedledum for logic synthesis
from tweedledum.bool_function_compiler.bool_function import BoolFunction
from tweedledum.classical import write_gate_dot, LogicNetwork

# Qiskit for quantum circuits
from qiskit import QuantumCircuit
from qiskit.qasm3 import dump

# Saha-Belletti library
from saha_belletti.core import generate_circuit

# Math utilities
from math import ceil, log2


@dataclass
class CircuitMetrics:
    """Data class to store circuit metrics"""
    name: str
    num_qubits: int
    depth: int
    num_gates: int
    oracle_type: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Data class to store complete benchmark results"""
    filename: str
    graph_nodes: int
    graph_edges: int
    available_colors: int
    vcgc_metrics: CircuitMetrics
    saha_belletti_metrics: Dict[str, CircuitMetrics]


class BenchmarkGenerator:
    """Main class for generating benchmark comparisons between VCGC and Saha-Belletti"""
    
    def __init__(self, benchmarks_dir: str, output_dir: str, draw_circuits: bool = False):
        """
        Initialize the benchmark generator
        
        Args:
            benchmarks_dir: Directory containing .col benchmark files
            output_dir: Directory to save output files
            draw_circuits: Whether to save circuit visualizations
        """
        self.benchmarks_dir = Path(benchmarks_dir)
        self.output_dir = Path(output_dir)
        self.draw_circuits = draw_circuits
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Saha-Belletti oracle types to test
        self.sb_oracle_types = ['original', 'minimal', 'simple', 'balanced']
    
    def get_benchmark_files(self) -> List[str]:
        """Get list of .col benchmark files"""
        col_files = glob.glob(str(self.benchmarks_dir / "*.col"))
        return [Path(f).stem for f in col_files]
    
    def generate_vcgc_circuit(self, network: VCPNetwork, filename: str) -> CircuitMetrics:
        """
        Generate VCGC circuit and return metrics
        
        Args:
            network: VCP network object
            filename: Base filename for outputs
            
        Returns:
            CircuitMetrics object with VCGC circuit metrics
        """
        try:
            # Create benchmark-specific output directory
            benchmark_output_dir = self.output_dir / filename
            benchmark_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Extract graph constraints
            bf = BooleanFunction()
            
            # Step 2: Generate logic network
            tweedledum_bf: BoolFunction = bf.create_multi_bit_function(network=network)
            logic_network: LogicNetwork = tweedledum_bf.logic_network()
            
            # Save Verilog file
            verilog_filename = benchmark_output_dir / f"{filename}_vcgc.v"
            bf.write_verilog_file(network=network, filename=str(verilog_filename))
            
            # Save DOT file for logic network
            dot_filename = benchmark_output_dir / f"{filename}_vcgc.dot"
            write_gate_dot(logic_network, str(dot_filename))
            
            # Step 3: Set up XAG synthesizer
            synthesizer = Synthesizer(cf=tweedledum_bf)
            
            # Step 4: Synthesize oracle with XAG
            oracle_circuit_xag: QuantumCircuit = synthesizer.synthesize_with_xag()
            
            
            # Step 5: Create uniform superposition oracle
            num_superpos_states = network.available_colors
            num_encode_qubits = ceil(log2(num_superpos_states))
            usp_oracle = uniform_superposition_qiskit(num_superpos_states=num_superpos_states).decompose()
            
            # Step 6: Create diffusion operator
            num_data_qubits = network.num_vertices * num_encode_qubits
            diff_oracle = generate_grover_diffusion(num_qubits=num_data_qubits)
            
            # Step 7: Create complete Grover circuit
            vcgc_grover_circuit = glue_grover_circuit(
                usp=usp_oracle,
                oracle=oracle_circuit_xag,
                diffusion=diff_oracle,
                num_data_qubits=num_data_qubits,
                num_encode_qubits=num_encode_qubits
            )
            
            # Save QASM file
            qasm_filename = benchmark_output_dir / f"{filename}_vcgc.qasm"
            with open(qasm_filename, "w") as f:
                dump(circuit=vcgc_grover_circuit, stream=f)
            
            return CircuitMetrics(
                name="VCGC",
                num_qubits=vcgc_grover_circuit.num_qubits,
                depth=vcgc_grover_circuit.depth(),
                num_gates=len(vcgc_grover_circuit)
            )
            
        except Exception as e:
            print(f"Error generating VCGC circuit for {filename}: {str(e)}")
            traceback.print_exc()
            return CircuitMetrics(name="VCGC", num_qubits=0, depth=0, num_gates=0)
    
    def generate_saha_belletti_circuits(self, network: VCPNetwork, filename: str) -> Dict[str, CircuitMetrics]:
        """
        Generate Saha-Belletti circuits for all oracle types
        
        Args:
            network: VCP network object
            filename: Base filename for outputs
            
        Returns:
            Dictionary mapping oracle type to CircuitMetrics
        """
        sb_metrics = {}
        
        # Create benchmark-specific output directory
        benchmark_output_dir = self.output_dir / filename
        benchmark_output_dir.mkdir(parents=True, exist_ok=True)
        
        for oracle_type in self.sb_oracle_types:
            try:
                # Generate Saha-Belletti circuit
                sb_circuit = generate_circuit(
                    graph=network.graph,
                    colors=network.available_colors,
                    oracle_type=oracle_type,
                    grover_iterations=1
                )
                
                sb_metrics[oracle_type] = CircuitMetrics(
                    name=f"Saha-Belletti-{oracle_type}",
                    num_qubits=sb_circuit.num_qubits,
                    depth=sb_circuit.depth(),
                    num_gates=len(sb_circuit),
                    oracle_type=oracle_type
                )
                
                # Save QASM file for this oracle type
                qasm_filename = benchmark_output_dir / f"{filename}_sb_{oracle_type}.qasm"
                with open(qasm_filename, "w") as f:
                    dump(circuit=sb_circuit, stream=f)
                    
            except Exception as e:
                print(f"Error generating Saha-Belletti {oracle_type} circuit for {filename}: {str(e)}")
                sb_metrics[oracle_type] = CircuitMetrics(
                    name=f"Saha-Belletti-{oracle_type}",
                    num_qubits=0,
                    depth=0,
                    num_gates=0,
                    oracle_type=oracle_type
                )
        
        return sb_metrics
    
    def process_benchmark(self, filename: str) -> Optional[BenchmarkResult]:
        """
        Process a single benchmark file
        
        Args:
            filename: Name of the benchmark file (without .col extension)
            
        Returns:
            BenchmarkResult object or None if processing failed
        """
        print(f"Processing benchmark: {filename}")
        
        try:
            # Load network from DIMACS file
            dimacs_path = self.benchmarks_dir / f"{filename}.col"
            network = VCPNetwork(file_path=str(dimacs_path))
            
            # Create benchmark-specific output directory
            benchmark_output_dir = self.output_dir / filename
            benchmark_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save graph visualization
            if self.draw_circuits:
                graph_filename = benchmark_output_dir / f"{filename}_graph.png"
                network.draw_graph(name=str(graph_filename), node_size=1000)
            
            print(f"  Graph: {network.num_vertices} vertices, {network.num_edges} edges, {network.available_colors} colors")
            
            # Generate VCGC circuit
            print("  Generating VCGC circuit...")
            vcgc_metrics = self.generate_vcgc_circuit(network, filename)
            
            # Generate Saha-Belletti circuits
            print("  Generating Saha-Belletti circuits...")
            sb_metrics = self.generate_saha_belletti_circuits(network, filename)
            
            return BenchmarkResult(
                filename=filename,
                graph_nodes=network.num_vertices,
                graph_edges=network.num_edges,
                available_colors=network.available_colors,
                vcgc_metrics=vcgc_metrics,
                saha_belletti_metrics=sb_metrics
            )
            
        except Exception as e:
            print(f"Error processing benchmark {filename}: {str(e)}")
            traceback.print_exc()
            return None
    
    def save_results_csv(self, results: List[BenchmarkResult], filename: str = "benchmark_results.csv"):
        """Save results to CSV file"""
        csv_path = self.output_dir / filename
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = [
                'benchmark', 'nodes', 'edges', 'colors',
                'vcgc_qubits', 'vcgc_depth', 'vcgc_gates',
                'sb_original_qubits', 'sb_original_depth', 'sb_original_gates',
                'sb_minimal_qubits', 'sb_minimal_depth', 'sb_minimal_gates',
                'sb_simple_qubits', 'sb_simple_depth', 'sb_simple_gates',
                'sb_balanced_qubits', 'sb_balanced_depth', 'sb_balanced_gates'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = {
                    'benchmark': result.filename,
                    'nodes': result.graph_nodes,
                    'edges': result.graph_edges,
                    'colors': result.available_colors,
                    'vcgc_qubits': result.vcgc_metrics.num_qubits,
                    'vcgc_depth': result.vcgc_metrics.depth,
                    'vcgc_gates': result.vcgc_metrics.num_gates,
                }
                
                # Add Saha-Belletti metrics
                for oracle_type in self.sb_oracle_types:
                    if oracle_type in result.saha_belletti_metrics:
                        metrics = result.saha_belletti_metrics[oracle_type]
                        row[f'sb_{oracle_type}_qubits'] = metrics.num_qubits
                        row[f'sb_{oracle_type}_depth'] = metrics.depth
                        row[f'sb_{oracle_type}_gates'] = metrics.num_gates
                    else:
                        row[f'sb_{oracle_type}_qubits'] = 0
                        row[f'sb_{oracle_type}_depth'] = 0
                        row[f'sb_{oracle_type}_gates'] = 0
                
                writer.writerow(row)
    
    def save_results_json(self, results: List[BenchmarkResult], filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        json_path = self.output_dir / filename
        
        results_dict = {}
        for result in results:
            results_dict[result.filename] = {
                'graph_info': {
                    'nodes': result.graph_nodes,
                    'edges': result.graph_edges,
                    'colors': result.available_colors
                },
                'vcgc': {
                    'qubits': result.vcgc_metrics.num_qubits,
                    'depth': result.vcgc_metrics.depth,
                    'gates': result.vcgc_metrics.num_gates
                },
                'saha_belletti': {}
            }
            
            for oracle_type, metrics in result.saha_belletti_metrics.items():
                results_dict[result.filename]['saha_belletti'][oracle_type] = {
                    'qubits': metrics.num_qubits,
                    'depth': metrics.depth,
                    'gates': metrics.num_gates
                }
        
        with open(json_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
    
    def print_summary(self, results: List[BenchmarkResult]):
        """Print a summary of the results"""
        print("\n" + "="*80)
        print("BENCHMARK COMPARISON SUMMARY")
        print("="*80)
        
        for result in results:
            print(f"\n📊 {result.filename}")
            print(f"   Graph: {result.graph_nodes} nodes, {result.graph_edges} edges, {result.available_colors} colors")
            print(f"   VCGC: {result.vcgc_metrics.num_qubits} qubits, {result.vcgc_metrics.depth} depth, {result.vcgc_metrics.num_gates} gates")
            
            for oracle_type in self.sb_oracle_types:
                if oracle_type in result.saha_belletti_metrics:
                    metrics = result.saha_belletti_metrics[oracle_type]
                    print(f"   SB-{oracle_type}: {metrics.num_qubits} qubits, {metrics.depth} depth, {metrics.num_gates} gates")
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """
        Run benchmarks on all .col files in the benchmarks directory
        
        Returns:
            List of BenchmarkResult objects
        """
        benchmark_files = self.get_benchmark_files()
        print(f"Found {len(benchmark_files)} benchmark files")
        
        results = []
        for filename in benchmark_files:
            result = self.process_benchmark(filename)
            if result:
                results.append(result)
        
        # Save results
        self.save_results_csv(results)
        self.save_results_json(results)
        
        # Print summary
        self.print_summary(results)
        
        print(f"\n✅ Results saved to {self.output_dir}")
        
        return results


def main():
    """Main function to run the benchmark generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate VCGC vs Saha-Belletti benchmark comparison")
    parser.add_argument("--benchmarks-dir", "-b", default="../data/benchmarks", 
                       help="Directory containing .col benchmark files")
    parser.add_argument("--output-dir", "-o", default="../data/vcgc_vs_saha_belletti", 
                       help="Output directory for results")
    parser.add_argument("--draw-circuits", "-d", action="store_true", 
                       help="Generate circuit visualizations")
    
    args = parser.parse_args()
    
    # Create benchmark generator
    generator = BenchmarkGenerator(
        benchmarks_dir=args.benchmarks_dir,
        output_dir=args.output_dir,
        draw_circuits=args.draw_circuits
    )
    
    # Run all benchmarks
    results = generator.run_all_benchmarks()
    
    return results


if __name__ == "__main__":
    main()
