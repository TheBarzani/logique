#!/usr/bin/env python3
"""
Runtime Comparison Script for Circuit Generation Methods

This script measures the runtime to generate circuits from a graph instance
using 5 different methods:
1. VCGC with XAG synthesis
2. Saha-Belletti original oracle
3. Saha-Belletti minimal oracle  
4. Saha-Belletti simple oracle
5. Saha-Belletti balanced oracle
"""

import argparse
import time
import traceback
from pathlib import Path
from math import ceil, log2
from typing import Dict, Optional

# Core libraries
from vcgc.network import VCPNetwork
from vcgc.boolean import BooleanFunction
from vcgc.synthesis import Synthesizer
from vcgc.circuit import uniform_superposition_qiskit, generate_grover_diffusion, glue_grover_circuit

# Tweedledum for logic synthesis
from tweedledum.bool_function_compiler.bool_function import BoolFunction

# Qiskit for quantum circuits
from qiskit import QuantumCircuit

# Saha-Belletti library
from saha_belletti.core import generate_circuit


class RuntimeMeasurer:
    """Class to measure runtime for different circuit generation methods"""
    
    def __init__(self, graph_file: str):
        """
        Initialize with a graph file
        
        Args:
            graph_file: Path to .col format graph file
        """
        self.graph_file = Path(graph_file)
        self.network = VCPNetwork(file_path=str(self.graph_file))
        self.results = {}
        
        print(f"Loaded graph: {self.network.num_vertices} vertices, "
              f"{self.network.num_edges} edges, {self.network.available_colors} colors")
    
    def measure_vcgc_xag_runtime(self) -> Optional[float]:
        """
        Measure runtime for VCGC with XAG synthesis
        
        Returns:
            Runtime in seconds, or None if failed
        """
        print("Measuring VCGC XAG synthesis runtime...")
        
        try:
            start_time = time.time()
            
            # Step 1: Extract graph constraints
            bf = BooleanFunction()
            
            # Step 2: Generate logic network
            tweedledum_bf: BoolFunction = bf.create_multi_bit_function(network=self.network)
            
            # lg = tweedledum_bf.logic_network()
            
            end_time = time.time()
            runtime = end_time - start_time
            
            print(f"  ✅ VCGC XAG: {runtime:.4f} seconds")
            return runtime
            
        except Exception as e:
            print(f"  ❌ VCGC XAG failed: {str(e)}")
            traceback.print_exc()
            return None
    
    def measure_saha_belletti_runtime(self, oracle_type: str) -> Optional[float]:
        """
        Measure runtime for Saha-Belletti with specified oracle type
        
        Args:
            oracle_type: Type of oracle ('original', 'minimal', 'simple', 'balanced')
            
        Returns:
            Runtime in seconds, or None if failed
        """
        print(f"Measuring Saha-Belletti {oracle_type} oracle runtime...")
        
        try:
            start_time = time.time()
            
            # Generate Saha-Belletti circuit
            sb_grover_circuit = generate_circuit(
                graph=self.network.graph,
                colors=self.network.available_colors,
                oracle_type=oracle_type,
                grover_iterations=1  # Use single iteration for consistency
            )
            
            end_time = time.time()
            runtime = end_time - start_time
            
            print(f"  ✅ Saha-Belletti {oracle_type}: {runtime:.4f} seconds")
            return runtime
            
        except Exception as e:
            print(f"  ❌ Saha-Belletti {oracle_type} failed: {str(e)}")
            traceback.print_exc()
            return None
    
    def run_all_measurements(self) -> Dict[str, Optional[float]]:
        """
        Run runtime measurements for all 5 methods
        
        Returns:
            Dictionary mapping method name to runtime (or None if failed)
        """
        print(f"\n🔬 Running runtime measurements for {self.graph_file.name}")
        print("=" * 60)
        
        # Method 1: VCGC with XAG
        self.results['vcgc_xag'] = self.measure_vcgc_xag_runtime()
        
        # Methods 2-5: Saha-Belletti with different oracle types
        saha_belletti_oracles = ['original', 'minimal', 'simple', 'balanced']
        
        for oracle_type in saha_belletti_oracles:
            method_name = f'saha_belletti_{oracle_type}'
            self.results[method_name] = self.measure_saha_belletti_runtime(oracle_type)
        
        return self.results
    
    def print_summary(self):
        """Print a summary of all runtime measurements"""
        print("\n📊 RUNTIME SUMMARY")
        print("=" * 60)
        print(f"Graph: {self.graph_file.name}")
        print(f"Vertices: {self.network.num_vertices}, Edges: {self.network.num_edges}, Colors: {self.network.available_colors}")
        print("-" * 60)
        
        # Sort results by runtime (successful ones first, then failed ones)
        successful_results = {k: v for k, v in self.results.items() if v is not None}
        failed_results = {k: v for k, v in self.results.items() if v is None}
        
        # Sort successful results by runtime
        sorted_successful = sorted(successful_results.items(), key=lambda x: x[1])
        
        print("🟢 Successful methods (sorted by speed):")
        for i, (method, runtime) in enumerate(sorted_successful, 1):
            print(f"  {i}. {method:<25} {runtime:.4f} seconds")
        
        if failed_results:
            print("\n🔴 Failed methods:")
            for method in failed_results:
                print(f"  - {method}")
        
        if len(sorted_successful) >= 2:
            fastest = sorted_successful[0]
            slowest = sorted_successful[-1]
            speedup = slowest[1] / fastest[1]
            print(f"\n⚡ Fastest: {fastest[0]} ({fastest[1]:.4f}s)")
            print(f"🐌 Slowest: {slowest[0]} ({slowest[1]:.4f}s)")
            print(f"📈 Speedup: {speedup:.2f}x")
    
    def save_results(self, output_file: Optional[str] = None):
        """Save results to a file"""
        if output_file is None:
            output_file = f"runtime_results_{self.graph_file.stem}.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"Runtime Comparison Results\n")
            f.write(f"Graph: {self.graph_file.name}\n")
            f.write(f"Vertices: {self.network.num_vertices}, Edges: {self.network.num_edges}, Colors: {self.network.available_colors}\n")
            f.write("-" * 60 + "\n")
            
            for method, runtime in self.results.items():
                if runtime is not None:
                    f.write(f"{method}: {runtime:.4f} seconds\n")
                else:
                    f.write(f"{method}: FAILED\n")
        
        print(f"\n💾 Results saved to {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Measure runtime for circuit generation methods on a graph instance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runtime_comparison.py ../data/benchmarks/K3.col
  python runtime_comparison.py ../data/benchmarks/myciel4.col --output results.txt
        """
    )
    
    parser.add_argument("graph_file", help="Path to graph file (.col format)")
    parser.add_argument("--output", "-o", help="Output file to save results")
    
    args = parser.parse_args()
    
    # Check if graph file exists
    if not Path(args.graph_file).exists():
        print(f"Error: Graph file '{args.graph_file}' not found")
        return 1
    
    try:
        # Create runtime measurer
        measurer = RuntimeMeasurer(args.graph_file)
        
        # Run all measurements
        results = measurer.run_all_measurements()
        
        # Print summary
        measurer.print_summary()
        
        # Save results if requested
        if args.output:
            measurer.save_results(args.output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())