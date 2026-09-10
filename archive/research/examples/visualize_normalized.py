#!/usr/bin/env python3
"""
Example script to create normalized visualizations for all metrics
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.visualize_benchmarks import BenchmarkVisualizer


def main():
    """Create normalized visualizations for all metrics"""
    
    results_dir = "../data/vcgc_vs_saha_belletti"
    visualizer = BenchmarkVisualizer(results_dir)
    
    try:
        # Load data (try CSV first, then JSON)
        try:
            visualizer.load_csv_data()
        except FileNotFoundError:
            print("CSV not found, trying JSON...")
            visualizer.load_json_data()
        
        # Print summary
        visualizer.print_summary_statistics()
        
        # Create all alternative visualizations for all metrics
        print("\nCreating normalized visualizations for all metrics...")
        visualizer.create_all_comparison_alternatives()
        
        print("\n✅ All normalized visualizations completed!")
        print("Generated files:")
        print("  Qubits:")
        print("    - qubits_comparison_log.png (logarithmic scale)")
        print("    - qubits_comparison_capped.png (outliers capped)")
        print("    - qubits_outliers_focus.png (focus on problematic benchmarks)")
        print("  Depth:")
        print("    - depth_comparison_log.png (logarithmic scale)")
        print("    - depth_comparison_capped.png (outliers capped)")
        print("    - depth_outliers_focus.png (focus on problematic benchmarks)")
        print("  Gates:")
        print("    - gates_comparison_log.png (logarithmic scale)")
        print("    - gates_comparison_capped.png (outliers capped)")
        print("    - gates_outliers_focus.png (focus on problematic benchmarks)")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have run the benchmark generation script first.")


def create_depth_only():
    """Create only depth normalizations (original functionality)"""
    
    results_dir = "../data/vcgc_vs_saha_belletti"
    visualizer = BenchmarkVisualizer(results_dir)
    
    try:
        visualizer.load_csv_data()
        print("Creating depth-only normalized visualizations...")
        visualizer.create_depth_comparison_alternatives()
        print("✅ Depth visualizations completed!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create normalized benchmark visualizations")
    parser.add_argument("--depth-only", action="store_true", 
                       help="Create only depth normalizations")
    
    args = parser.parse_args()
    
    if args.depth_only:
        create_depth_only()
    else:
        main()
