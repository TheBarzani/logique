#!/usr/bin/env python3
"""
Script to analyze and visualize results from execution comparison CSV files.
Useful for re-plotting results or analyzing data from previous runs.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
from typing import List, Optional
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


# Optional import for seaborn
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Warning: seaborn not available. Some plots will use matplotlib only.")

class ResultsAnalyzer:
    """Class to analyze execution comparison results."""
    
    def __init__(self, data_dir: str = "../data/execution/"):
        """Initialize the analyzer."""
        self.data_dir = data_dir
        self.df = None
        
    def load_latest_results(self) -> bool:
        """Load the most recent results CSV file."""
        pattern = os.path.join(self.data_dir, "*_*/execution_comparison.csv")
        csv_files = glob.glob(pattern)
        
        if not csv_files:
            print("No execution comparison CSV files found.")
            return False
            
        # Get the most recent file
        latest_file = max(csv_files, key=os.path.getctime)
        return self.load_results(latest_file)
    
    def load_results(self, csv_file: str) -> bool:
        """Load results from a specific CSV file."""
        try:
            self.df = pd.read_csv(csv_file)
            print(f"Loaded results from: {csv_file}")
            print(f"Data shape: {self.df.shape}")
            return True
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
            return False
    
    def show_summary(self):
        """Display a summary of the results."""
        if self.df is None:
            print("No data loaded.")
            return
            
        print("\n" + "="*50)
        print("EXECUTION COMPARISON RESULTS SUMMARY")
        print("="*50)
        
        # Basic info
        print(f"Total experiments: {len(self.df)}")
        print(f"Methods tested: {list(self.df['method'].unique())}")
        print(f"Graph sizes: {sorted(self.df['num_vertices'].unique())}")
        print(f"Backend used: {self.df['backend_name'].iloc[0] if 'backend_name' in self.df.columns else 'Unknown'}")
        
        # Success probabilities
        print(f"\nSuccess Probability Statistics:")
        success_stats = self.df.groupby('method')['success_probability'].agg(['mean', 'std', 'min', 'max'])
        print(success_stats.round(4))
        
        # Circuit metrics
        print(f"\nCircuit Metrics by Method:")
        circuit_stats = self.df.groupby('method')[['original_qubits', 'original_depth', 'original_gates']].mean()
        print(circuit_stats.round(2))
    
    def plot_success_probability(self, save_plot: bool = True):
        """Plot success probability vs number of vertices."""
        if self.df is None:
            print("No data loaded.")
            return
            
        # Smaller figure size for 2-column format
        plt.figure(figsize=(8, 6))
        
        methods = self.df['method'].unique()
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for method, color in zip(methods, colors):
            method_data = self.df[self.df['method'] == method]
            plt.plot(method_data['num_vertices'], method_data['success_probability'], 
                    marker='o', label=method, color=color, linewidth=2.5, markersize=6, linestyle='--')
        
        # Larger font sizes
        plt.xlabel('Number of Vertices', fontsize=16)
        plt.ylabel('Total Probability of the Desired States', fontsize=16)
        plt.title('Success Probability vs Graph Size', fontsize=18, pad=20)
        
        # Adjust legend
        plt.legend(fontsize=12, loc='upper right', frameon=True, fancybox=True, shadow=True)
        
        # Grid and ticks
        plt.grid(True, alpha=0.3, linewidth=0.5)
        plt.xticks(sorted(self.df['num_vertices'].unique()), fontsize=14)
        plt.yticks(fontsize=14)
        
        # Tighter layout
        plt.tight_layout()
        
        # Adjust margins
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.95, top=0.90)
        
        if save_plot:
            plt.savefig(f"{self.data_dir}replotted_success_probability.png", 
                    dpi=300, bbox_inches='tight', facecolor='white')
            # Also save as PDF for better quality in papers
            plt.savefig(f"{self.data_dir}replotted_success_probability.pdf", 
                    bbox_inches='tight', facecolor='white')
            print(f"Plot saved to: {self.data_dir}replotted_success_probability.png/.pdf")
        
        plt.show()

    def plot_success_probability_ieee(self, save_plot: bool = True):
        """Plot optimized for IEEE 2-column format with zoom inset."""
        if self.df is None:
            print("No data loaded.")
            return
            
        # IEEE 2-column optimal size (approximately 3.5 inches wide)
        plt.figure(figsize=(7, 5))
        
        methods = self.df['method'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Better colors
        markers = ['o', 's', '^', 'D', 'v']  # Different markers for each method
        
        # Main plot
        for method, color, marker in zip(methods, colors, markers):
            method_data = self.df[self.df['method'] == method]
            plt.plot(method_data['num_vertices'], method_data['success_probability'], 
                    marker=marker, label=method, color=color, linewidth=2, 
                    markersize=7, linestyle='--', markerfacecolor='white', 
                    markeredgewidth=2, markeredgecolor=color)
        
        plt.xlabel('Number of Vertices', fontsize=10, weight='bold')
        plt.ylabel('Total Probability of the Desired Solution States', fontsize=10, weight='bold')
        
        # Smaller legend with abbreviated names
        method_abbrev = {
            'Proposed': 'Proposed',
            'Saha et al.': 'Saha et al.',
            'Belletti Simple': 'Belletti-Simple',
            'Belletti Minimal': 'Belletti-Minimal',
            'Belletti Balanced': 'Belletti-Balanced'
        }
        
        handles, labels = plt.gca().get_legend_handles_labels()
        new_labels = [method_abbrev.get(label, label) for label in labels]
        plt.legend(handles, new_labels, fontsize=11, loc='upper right', 
                frameon=True, fancybox=False, edgecolor='black')
        
        plt.grid(True, alpha=0.3, linewidth=0.5)
        plt.xticks(sorted(self.df['num_vertices'].unique()), fontsize=12)
        plt.yticks(fontsize=12)
        
        # Create inset for zoom on vertices 6-8
        axins = inset_axes(plt.gca(), width="100%", height="100%", loc='lower left', 
                       bbox_to_anchor=(0.6, 0.15, 0.35, 0.35), bbox_transform=plt.gca().transAxes)
        
        # Plot same data on inset
        for method, color, marker in zip(methods, colors, markers):
            method_data = self.df[self.df['method'] == method]
            # Filter for vertices 6-8
            zoom_data = method_data[method_data['num_vertices'] >= 6]
            axins.plot(zoom_data['num_vertices'], zoom_data['success_probability'], 
                    marker=marker, color=color, linewidth=1.5, 
                    markersize=5, linestyle='--', markerfacecolor='white', 
                    markeredgewidth=1.5, markeredgecolor=color)
        
        # Set zoom limits
        axins.set_xlim(5.8, 8.2)
        max_val = self.df[self.df['num_vertices'] >= 6]['success_probability'].max()
        axins.set_ylim(-0.01, max_val * 1.1)
        
        # Style the inset
        axins.grid(True, alpha=0.3, linewidth=0.5)
        axins.tick_params(labelsize=9)
        axins.set_xticks([6, 7, 8])
        
        # Add border around inset
        axins.spines['bottom'].set_linewidth(1.5)
        axins.spines['top'].set_linewidth(1.5)
        axins.spines['left'].set_linewidth(1.5)
        axins.spines['right'].set_linewidth(1.5)
        
        # Optional: Add lines connecting inset to main plot
        # This requires the indicate_inset_zoom function
        try:
            plt.gca().indicate_inset_zoom(axins, edgecolor="gray", alpha=0.7, linewidth=1)
        except AttributeError:
            # Fallback for older matplotlib versions
            pass
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig(f"{self.data_dir}ieee_success_probability.pdf", 
                    bbox_inches='tight', facecolor='white', dpi=800)
            plt.savefig(f"{self.data_dir}ieee_success_probability.png", 
                    bbox_inches='tight', facecolor='white', dpi=500)
            plt.savefig(f"{self.data_dir}ieee_success_probability.eps", 
                    bbox_inches='tight', facecolor='white', dpi=300)
            print(f"IEEE format plot with zoom inset saved")
        
        plt.show()
    
    def plot_circuit_metrics(self, save_plot: bool = True):
        """Plot various circuit metrics."""
        if self.df is None:
            print("No data loaded.")
            return
            
        metrics = ['original_qubits', 'original_depth', 'original_gates', 'transpiled_depth']
        available_metrics = [m for m in metrics if m in self.df.columns]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Circuit Metrics Comparison', fontsize=16)
        
        methods = self.df['method'].unique()
        colors = plt.cm.Set1(np.linspace(0, 1, len(methods)))
        
        for idx, metric in enumerate(available_metrics[:4]):
            ax = axes[idx // 2, idx % 2]
            
            for method, color in zip(methods, colors):
                method_data = self.df[self.df['method'] == method]
                ax.plot(method_data['num_vertices'], method_data[metric], 
                       marker='o', label=method, color=color, linewidth=2)
            
            ax.set_xlabel('Number of Vertices')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.set_title(metric.replace('_', ' ').title())
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(sorted(self.df['num_vertices'].unique()))
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig(f"{self.data_dir}replotted_circuit_metrics.png", 
                       dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {self.data_dir}replotted_circuit_metrics.png")
        
        plt.show()
    
    def plot_heatmap(self, metric: str = 'success_probability', save_plot: bool = True):
        """Create a heatmap of the specified metric."""
        if self.df is None or metric not in self.df.columns:
            print(f"No data loaded or metric '{metric}' not found.")
            return
            
        # Pivot the data for heatmap
        pivot_data = self.df.pivot(index='method', columns='num_vertices', values=metric)
        
        plt.figure(figsize=(10, 6))
        
        if HAS_SEABORN:
            import seaborn as sns
            sns.heatmap(pivot_data, annot=True, cmap='YlOrRd', fmt='.3f', 
                       cbar_kws={'label': metric.replace('_', ' ').title()})
        else:
            # Fallback to matplotlib
            im = plt.imshow(pivot_data.values, cmap='YlOrRd', aspect='auto')
            plt.colorbar(im, label=metric.replace('_', ' ').title())
            
            # Add text annotations
            for i in range(len(pivot_data.index)):
                for j in range(len(pivot_data.columns)):
                    plt.text(j, i, f'{pivot_data.iloc[i, j]:.3f}', 
                           ha='center', va='center')
            
            plt.xticks(range(len(pivot_data.columns)), pivot_data.columns)
            plt.yticks(range(len(pivot_data.index)), pivot_data.index)
        
        plt.title(f'{metric.replace("_", " ").title()} Heatmap')
        plt.xlabel('Number of Vertices')
        plt.ylabel('Method')
        
        if save_plot:
            plt.savefig(f"{self.data_dir}heatmap_{metric}.png", 
                       dpi=300, bbox_inches='tight')
            print(f"Heatmap saved to: {self.data_dir}heatmap_{metric}.png")
        
        plt.show()
    
    def compare_methods(self, vertices: int = None):
        """Compare methods for a specific number of vertices or overall."""
        if self.df is None:
            print("No data loaded.")
            return
            
        if vertices:
            data = self.df[self.df['num_vertices'] == vertices]
            title = f"Method Comparison for {vertices} Vertices"
        else:
            data = self.df.groupby('method').mean()
            title = "Average Method Comparison"
        
        print(f"\n{title}")
        print("="*50)
        
        if vertices:
            comparison = data[['method', 'success_probability', 'original_qubits', 
                             'original_depth', 'original_gates']].set_index('method')
        else:
            comparison = data[['success_probability', 'original_qubits', 
                              'original_depth', 'original_gates']]
        
        print(comparison.round(3))
        
        # Ranking by success probability
        if vertices:
            ranking = data.sort_values('success_probability', ascending=False)
            print(f"\nRanking by Success Probability:")
            for i, (_, row) in enumerate(ranking.iterrows(), 1):
                print(f"{i}. {row['method']}: {row['success_probability']:.4f}")
        else:
            ranking = data.sort_values('success_probability', ascending=False)
            print(f"\nRanking by Average Success Probability:")
            for i, (method, row) in enumerate(ranking.iterrows(), 1):
                print(f"{i}. {method}: {row['success_probability']:.4f}")
    
    def export_summary_table(self, filename: str = None):
        """Export a summary table to CSV."""
        if self.df is None:
            print("No data loaded.")
            return
            
        if not filename:
            filename = f"{self.data_dir}summary_table.csv"
        
        # Create summary by method and vertices
        summary = self.df.groupby(['method', 'num_vertices']).agg({
            'success_probability': 'mean',
            'original_qubits': 'mean',
            'original_depth': 'mean',
            'original_gates': 'mean',
            'transpiled_depth': 'mean' if 'transpiled_depth' in self.df.columns else lambda x: None
        }).round(4)
        
        summary.to_csv(filename)
        print(f"Summary table exported to: {filename}")

def main():
    """Main function for interactive analysis."""
    analyzer = ResultsAnalyzer()
    
    print("Execution Comparison Results Analyzer")
    print("="*40)
    
    # Try to load latest results
    if not analyzer.load_latest_results():
        print("Please ensure you have execution comparison CSV files in the data directory.")
        return
    
    # Show summary
    analyzer.show_summary()
    
    # Generate plots
    print("\nGenerating plots...")
    analyzer.plot_success_probability()
    analyzer.plot_success_probability_ieee()
    analyzer.plot_circuit_metrics()
    analyzer.plot_heatmap('success_probability')
    
    # Show comparisons
    analyzer.compare_methods()
    
    # Export summary
    analyzer.export_summary_table()
    
    print("\n✅ Analysis completed!")

if __name__ == "__main__":
    main()
