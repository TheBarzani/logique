#!/usr/bin/env python3
"""
Utility script to generate linear graph DIMACS files for the comparison study.
A linear graph (path graph) has vertices connected in a line: 1-2-3-4-...
"""

import os
import networkx as nx
from typing import List

def create_linear_graph(n: int) -> nx.Graph:
    """Create a linear graph (path graph) with n vertices."""
    return nx.path_graph(n)

def graph_to_dimacs_col(graph: nx.Graph, filename: str, colors: int = 3):
    """
    Convert NetworkX graph to DIMACS .col format.
    
    Args:
        graph: NetworkX graph
        filename: Output filename
        colors: Number of colors (chromatic number)
    """
    
    with open(filename, 'w') as f:
        # Header comments
        f.write(f"c Linear graph with {graph.number_of_nodes()} vertices\n")
        f.write(f"c Generated for VCGC vs Saha-Belletti comparison\n")
        f.write(f"c\n")
        
        # Problem line: p edge <vertices> <edges>
        f.write(f"p edge {graph.number_of_nodes()} {graph.number_of_edges()}\n")
        
        # Edge lines: e <vertex1> <vertex2>
        # Note: DIMACS format uses 1-based indexing
        for edge in graph.edges():
            v1, v2 = edge
            f.write(f"e {v1 + 1} {v2 + 1}\n")

def generate_linear_graphs(output_dir: str = "../data/execution/", max_vertices: int = 7):
    """Generate linear graphs from 1 to max_vertices."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    for n in range(1, max_vertices + 1):
        filename = os.path.join(output_dir, f"linear{n}.col")
        
        if os.path.exists(filename):
            print(f"✓ {filename} already exists")
            continue
            
        # Create linear graph
        if n == 1:
            # Single vertex, no edges
            graph = nx.Graph()
            graph.add_node(0)
        else:
            graph = create_linear_graph(n)
        
        # Save to DIMACS format
        graph_to_dimacs_col(graph, filename)
        print(f"📝 Created {filename}")
        
        # Verify the graph
        verify_linear_graph(filename, n)

def verify_linear_graph(filename: str, expected_vertices: int):
    """Verify that the generated graph is correct."""
    try:
        from vcgc.network import VCPNetwork
        network = VCPNetwork(file_path=filename)
        
        assert network.num_vertices == expected_vertices, f"Expected {expected_vertices} vertices, got {network.num_vertices}"
        
        if expected_vertices > 1:
            assert network.num_edges == expected_vertices - 1, f"Expected {expected_vertices - 1} edges, got {network.num_edges}"
        else:
            assert network.num_edges == 0, f"Expected 0 edges for single vertex, got {network.num_edges}"
        
        print(f"  ✅ Verified: {network.num_vertices} vertices, {network.num_edges} edges")
        
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")

def show_graph_properties(output_dir: str = "../data/execution/"):
    """Display properties of all linear graphs."""
    print("\nLinear Graph Properties:")
    print("=" * 40)
    print("Graph    | Vertices | Edges | Chromatic Number")
    print("-" * 40)
    
    for i in range(1, 8):
        filename = os.path.join(output_dir, f"linear{i}.col")
        if os.path.exists(filename):
            try:
                from vcgc.network import VCPNetwork
                network = VCPNetwork(file_path=filename)
                
                # Linear graphs have chromatic number of min(vertices, 2)
                # except for single vertex which is 1
                chromatic_number = 1 if i == 1 else 2
                
                print(f"linear{i:<2} | {network.num_vertices:>8} | {network.num_edges:>5} | {chromatic_number:>15}")
                
            except Exception as e:
                print(f"linear{i:<2} | Error loading: {e}")
        else:
            print(f"linear{i:<2} | File not found")

def main():
    """Main function."""
    print("Linear Graph Generator for VCGC vs Saha-Belletti Comparison")
    print("=" * 60)
    
    # Generate graphs
    generate_linear_graphs()
    
    # Show properties
    show_graph_properties()
    
    print("\n✅ Linear graph generation completed!")
    print("\nYou can now run:")
    print("  python test_exec_comparison.py  # Test the setup")
    print("  python generate_exec_comparison.py  # Run full comparison")

if __name__ == "__main__":
    main()
