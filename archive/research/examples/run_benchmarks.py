#!/usr/bin/env python3
"""
Simple example script to demonstrate how to use the benchmark generator
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_benchmarks import BenchmarkGenerator


def run_simple_example():
    """Run a simple example with default settings"""
    
    # Define paths relative to the current script location
    current_dir = Path(__file__).parent
    benchmarks_dir = current_dir / "benchmarks"
    output_dir = current_dir / "vcgc_vs_saha_belletti"
    
    print("🚀 Starting VCGC vs Saha-Belletti Benchmark Generation")
    print(f"📁 Benchmarks directory: {benchmarks_dir}")
    print(f"📂 Output directory: {output_dir}")
    
    # Create the benchmark generator
    generator = BenchmarkGenerator(
        benchmarks_dir=str(benchmarks_dir),
        output_dir=str(output_dir),
        draw_circuits=False  # Set to True if you want circuit visualizations
    )
    
    # Run all benchmarks
    results = generator.run_all_benchmarks()
    
    print(f"\n✅ Successfully processed {len(results)} benchmarks")
    print(f"📊 Results saved to: {output_dir}")
    
    return results


def run_single_benchmark(benchmark_name: str):
    """Run a single benchmark for testing"""
    
    current_dir = Path(__file__).parent
    benchmarks_dir = current_dir / "benchmarks"
    output_dir = current_dir / "test_output"
    
    print(f"🔬 Testing single benchmark: {benchmark_name}")
    
    generator = BenchmarkGenerator(
        benchmarks_dir=str(benchmarks_dir),
        output_dir=str(output_dir),
        draw_circuits=True  # Enable visualizations for single test
    )
    
    # Process single benchmark
    result = generator.process_benchmark(benchmark_name)
    
    if result:
        print(f"\n✅ Successfully processed {benchmark_name}")
        print(f"📊 VCGC: {result.vcgc_metrics.num_qubits} qubits, {result.vcgc_metrics.depth} depth")
        for oracle_type, metrics in result.saha_belletti_metrics.items():
            print(f"📊 SB-{oracle_type}: {metrics.num_qubits} qubits, {metrics.depth} depth")
    else:
        print(f"❌ Failed to process {benchmark_name}")
    
    return result


if __name__ == "__main__":
    # You can choose to run all benchmarks or test a single one
    
    if len(sys.argv) > 1:
        # Run single benchmark for testing
        benchmark_name = sys.argv[1]
        run_single_benchmark(benchmark_name)
    else:
        # Run all benchmarks
        run_simple_example()
