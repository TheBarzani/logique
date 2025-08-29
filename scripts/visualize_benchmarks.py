#!/usr/bin/env python3
"""
Benchmark Visualization Script

This script reads the generated benchmark results and creates group bar charts
comparing VCGC vs Saha-Belletti approaches across different metrics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from typing import List, Optional
import argparse


class BenchmarkVisualizer:
    """Class for visualizing benchmark comparison results"""
    
    def __init__(self, results_dir: str):
        """
        Initialize the visualizer
        
        Args:
            results_dir: Directory containing benchmark results
        """
        self.results_dir = Path(results_dir)
        self.data = None
        
        # Define colors for different approaches
        self.colors = {
            'vcgc': '#2E86AB',           # Blue
            'sb_original': '#A23B72',    # Pink
            'sb_minimal': '#F18F01',     # Orange
            'sb_simple': '#C73E1D',      # Red
            'sb_balanced': '#6A994E'     # Green
        }
        
        # Define approach labels
        self.labels = {
            'vcgc': 'VCGC',
            'sb_original': 'SB-Original',
            'sb_minimal': 'SB-Minimal',
            'sb_simple': 'SB-Simple',
            'sb_balanced': 'SB-Balanced'
        }
    
    def load_csv_data(self, filename: str = "benchmark_results.csv") -> pd.DataFrame:
        """Load data from CSV file"""
        csv_path = self.results_dir / filename
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        self.data = pd.read_csv(csv_path)
        print(f"Loaded data for {len(self.data)} benchmarks from CSV")
        return self.data
    
    def load_json_data(self, filename: str = "benchmark_results.json") -> pd.DataFrame:
        """Load data from JSON file and convert to DataFrame"""
        json_path = self.results_dir / filename
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Convert JSON to DataFrame format
        rows = []
        for benchmark, data in json_data.items():
            row = {
                'benchmark': benchmark,
                'nodes': data['graph_info']['nodes'],
                'edges': data['graph_info']['edges'],
                'colors': data['graph_info']['colors'],
                'vcgc_qubits': data['vcgc']['qubits'],
                'vcgc_depth': data['vcgc']['depth'],
                'vcgc_gates': data['vcgc']['gates']
            }
            
            # Add Saha-Belletti metrics
            for oracle_type, metrics in data['saha_belletti'].items():
                row[f'sb_{oracle_type}_qubits'] = metrics['qubits']
                row[f'sb_{oracle_type}_depth'] = metrics['depth']
                row[f'sb_{oracle_type}_gates'] = metrics['gates']
            
            rows.append(row)
        
        self.data = pd.DataFrame(rows)
        print(f"Loaded data for {len(self.data)} benchmarks from JSON")
        return self.data
    
    def create_graph_labels(self) -> List[str]:
        """Create descriptive labels for graphs including their characteristics"""
        labels = []
        for _, row in self.data.iterrows():
            label = f"{row['benchmark']}\n({row['nodes']}n, {row['edges']}e, {row['colors']}c)"
            labels.append(label)
        return labels
    
    def create_grouped_bar_chart(self, metric: str, title: str, ylabel: str, 
                                filename: Optional[str] = None, figsize: tuple = (14, 8),
                                log_scale: bool = False, exclude_outliers: bool = False,
                                outlier_threshold: float = 3.0):
        """
        Create a grouped bar chart for a specific metric
        
        Args:
            metric: The metric to plot ('qubits', 'depth', or 'gates')
            title: Chart title
            ylabel: Y-axis label
            filename: Optional filename to save the chart
            figsize: Figure size as (width, height)
            log_scale: Use logarithmic scale for y-axis
            exclude_outliers: Exclude extreme outliers from visualization
            outlier_threshold: Standard deviations beyond which to consider outliers
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        # Prepare data
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        graph_labels = self.create_graph_labels()
        
        # Extract metric data for each approach
        metric_data = {}
        for approach in approaches:
            col_name = f'{approach}_{metric}'
            if col_name in self.data.columns:
                metric_data[approach] = self.data[col_name].values
            else:
                print(f"Warning: Column {col_name} not found in data")
                metric_data[approach] = np.zeros(len(self.data))
        
        # Handle outliers if requested
        if exclude_outliers:
            # Calculate outliers based on all non-zero values
            all_values = []
            for approach in approaches:
                non_zero_values = metric_data[approach][metric_data[approach] > 0]
                all_values.extend(non_zero_values)
            
            if len(all_values) > 0:
                mean_val = np.mean(all_values)
                std_val = np.std(all_values)
                threshold = mean_val + outlier_threshold * std_val
                
                print(f"Outlier threshold for {metric}: {threshold:.0f}")
                
                # Create a note about excluded outliers
                outlier_info = []
                for i, approach in enumerate(approaches):
                    outliers = metric_data[approach] > threshold
                    if np.any(outliers):
                        outlier_benchmarks = [self.data.iloc[j]['benchmark'] for j in range(len(outliers)) if outliers[j]]
                        outlier_values = [metric_data[approach][j] for j in range(len(outliers)) if outliers[j]]
                        for bench, val in zip(outlier_benchmarks, outlier_values):
                            outlier_info.append(f"{self.labels[approach]} {bench}: {val:.0f}")
                        
                        # Cap outliers at threshold
                        metric_data[approach] = np.minimum(metric_data[approach], threshold)
                
                if outlier_info:
                    title += f"\n(Values >{threshold:.0f} capped. Outliers: {', '.join(outlier_info[:3])}{'...' if len(outlier_info) > 3 else ''})"
        
        # Set up the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculate bar positions
        n_benchmarks = len(self.data)
        n_approaches = len(approaches)
        bar_width = 0.15
        positions = np.arange(n_benchmarks)
        
        # Create bars for each approach
        bars = []
        for i, approach in enumerate(approaches):
            offset = (i - n_approaches/2 + 0.5) * bar_width
            bars.append(ax.bar(
                positions + offset,
                metric_data[approach],
                bar_width,
                label=self.labels[approach],
                color=self.colors[approach],
                alpha=0.8,
                edgecolor='black',
                linewidth=0.5
            ))
        
        # Apply log scale if requested
        if log_scale:
            ax.set_yscale('log')
            ylabel += " (log scale)"
        
        # Customize the plot
        ax.set_xlabel('Benchmark Graphs\n(nodes, edges, colors)', fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(positions)
        ax.set_xticklabels(graph_labels, rotation=45, ha='right', fontsize=10)
        
        # Add legend
        ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # Add value labels on bars (with better positioning for log scale)
        for bar_group in bars:
            for bar in bar_group:
                height = bar.get_height()
                if height > 0:  # Only label non-zero bars
                    # Adjust label positioning for log scale
                    if log_scale:
                        label_y = height * 1.05
                        fontsize = 7
                    else:
                        label_y = height + max(height * 0.01, 1)
                        fontsize = 8
                    
                    ax.annotate(f'{int(height)}',
                              xy=(bar.get_x() + bar.get_width()/2, label_y),
                              ha='center', va='bottom',
                              fontsize=fontsize, rotation=90 if not log_scale else 0)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save if filename provided
        if filename:
            save_path = self.results_dir / filename
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        
        # Show the plot
        plt.show()
    
    def create_all_charts(self, save_charts: bool = True, normalize_all: bool = True):
        """Create all three metric charts with optional normalization"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        # Chart 1: Qubits (with normalization options)
        if normalize_all:
            # Create both log scale and outlier-excluded versions
            self.create_grouped_bar_chart(
                metric='qubits',
                title='Quantum Circuit Comparison: Number of Qubits (Log Scale)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Qubits',
                filename='qubits_comparison_log.png' if save_charts else None,
                log_scale=True
            )
            
            self.create_grouped_bar_chart(
                metric='qubits',
                title='Quantum Circuit Comparison: Number of Qubits (Outliers Capped)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Qubits',
                filename='qubits_comparison_normalized.png' if save_charts else None,
                exclude_outliers=True,
                outlier_threshold=2.0
            )
        else:
            # Original chart
            self.create_grouped_bar_chart(
                metric='qubits',
                title='Quantum Circuit Comparison: Number of Qubits\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Qubits',
                filename='qubits_comparison.png' if save_charts else None
            )
        
        # Chart 2: Depth (with normalization options)
        if normalize_all:
            # Create both log scale and outlier-excluded versions
            self.create_grouped_bar_chart(
                metric='depth',
                title='Quantum Circuit Comparison: Circuit Depth (Log Scale)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Circuit Depth',
                filename='depth_comparison_log.png' if save_charts else None,
                log_scale=True
            )
            
            self.create_grouped_bar_chart(
                metric='depth',
                title='Quantum Circuit Comparison: Circuit Depth (Outliers Capped)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Circuit Depth',
                filename='depth_comparison_normalized.png' if save_charts else None,
                exclude_outliers=True,
                outlier_threshold=2.0  # 2 standard deviations
            )
        else:
            # Original chart
            self.create_grouped_bar_chart(
                metric='depth',
                title='Quantum Circuit Comparison: Circuit Depth\nVCGC vs Saha-Belletti Approaches',
                ylabel='Circuit Depth',
                filename='depth_comparison.png' if save_charts else None
            )
        
        # Chart 3: Gates (with normalization options)
        if normalize_all:
            # Create both log scale and outlier-excluded versions
            self.create_grouped_bar_chart(
                metric='gates',
                title='Quantum Circuit Comparison: Number of Gates (Log Scale)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Gates',
                filename='gates_comparison_log.png' if save_charts else None,
                log_scale=True
            )
            
            self.create_grouped_bar_chart(
                metric='gates',
                title='Quantum Circuit Comparison: Number of Gates (Outliers Capped)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Gates',
                filename='gates_comparison_normalized.png' if save_charts else None,
                exclude_outliers=True,
                outlier_threshold=2.0
            )
        else:
            # Original chart
            self.create_grouped_bar_chart(
                metric='gates',
                title='Quantum Circuit Comparison: Number of Gates\nVCGC vs Saha-Belletti Approaches',
                ylabel='Number of Gates',
                filename='gates_comparison.png' if save_charts else None
            )
    
    def create_all_comparison_alternatives(self):
        """Create multiple normalized versions for all metrics"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        print("Creating alternative visualizations for all metrics...")
        
        metrics = ['qubits', 'depth', 'gates']
        
        for metric in metrics:
            print(f"\nCreating {metric} visualizations...")
            
            # 1. Log scale version
            self.create_grouped_bar_chart(
                metric=metric,
                title=f'{metric.capitalize()} Comparison (Logarithmic Scale)\nVCGC vs Saha-Belletti Approaches',
                ylabel=f'{metric.capitalize()} (log scale)',
                filename=f'{metric}_comparison_log.png',
                log_scale=True
            )
            
            # 2. Outliers excluded version
            self.create_grouped_bar_chart(
                metric=metric,
                title=f'{metric.capitalize()} Comparison (Extreme Values Capped)\nVCGC vs Saha-Belletti Approaches',
                ylabel=metric.capitalize(),
                filename=f'{metric}_comparison_capped.png',
                exclude_outliers=True,
                outlier_threshold=2.0
            )
            
            # 3. Create a separate chart showing only the problematic benchmarks
            self.create_metric_outlier_focus_chart(metric)
    
    def create_metric_outlier_focus_chart(self, metric: str):
        """Create a focused chart showing only benchmarks with extreme values for a specific metric"""
        if self.data is None:
            return
        
        # Find benchmarks with extreme values across all approaches
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        all_values = []
        
        for approach in approaches:
            col_name = f'{approach}_{metric}'
            if col_name in self.data.columns:
                values = self.data[col_name]
                all_values.extend(values[values > 0])
        
        if not all_values:
            print(f"No data found for {metric} outlier analysis")
            return
        
        mean_val = np.mean(all_values)
        std_val = np.std(all_values)
        threshold = mean_val + 2 * std_val
        
        # Find benchmarks that have at least one approach exceeding the threshold
        outlier_mask = False
        for approach in approaches:
            col_name = f'{approach}_{metric}'
            if col_name in self.data.columns:
                outlier_mask = outlier_mask | (self.data[col_name] > threshold)
        
        if not outlier_mask.any():
            print(f"No outliers found for {metric} focused chart")
            return
        
        # Create subset data
        outlier_data = self.data[outlier_mask].copy()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left plot: Linear scale
        x_pos = np.arange(len(outlier_data))
        width = 0.15
        
        for i, approach in enumerate(approaches):
            col_name = f'{approach}_{metric}'
            if col_name in outlier_data.columns:
                values = outlier_data[col_name]
                offset = (i - len(approaches)/2 + 0.5) * width
                ax1.bar(x_pos + offset, values, width, 
                       label=self.labels[approach], color=self.colors[approach], alpha=0.8)
        
        ax1.set_title(f'Outlier Benchmarks for {metric.capitalize()}: Linear Scale')
        ax1.set_ylabel(metric.capitalize())
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([f"{row['benchmark']}\n({row['nodes']}n,{row['edges']}e,{row['colors']}c)" 
                            for _, row in outlier_data.iterrows()], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Right plot: Log scale
        for i, approach in enumerate(approaches):
            col_name = f'{approach}_{metric}'
            if col_name in outlier_data.columns:
                values = outlier_data[col_name]
                values = np.maximum(values, 1)  # Avoid log(0)
                offset = (i - len(approaches)/2 + 0.5) * width
                ax2.bar(x_pos + offset, values, width, 
                       label=self.labels[approach], color=self.colors[approach], alpha=0.8)
        
        ax2.set_title(f'Outlier Benchmarks for {metric.capitalize()}: Log Scale')
        ax2.set_ylabel(f'{metric.capitalize()} (log scale)')
        ax2.set_yscale('log')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f"{row['benchmark']}\n({row['nodes']}n,{row['edges']}e,{row['colors']}c)" 
                            for _, row in outlier_data.iterrows()], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the focused chart
        save_path = self.results_dir / f'{metric}_outliers_focus.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"{metric.capitalize()} outlier focus chart saved to: {save_path}")
        
        plt.show()
    
    def create_depth_comparison_alternatives(self):
        """Create multiple normalized versions of the depth comparison"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        print("Creating alternative depth visualizations...")
        
        # 1. Log scale version
        self.create_grouped_bar_chart(
            metric='depth',
            title='Circuit Depth Comparison (Logarithmic Scale)\nVCGC vs Saha-Belletti Approaches',
            ylabel='Circuit Depth (log scale)',
            filename='depth_comparison_log.png',
            log_scale=True
        )
        
        # 2. Outliers excluded version
        self.create_grouped_bar_chart(
            metric='depth',
            title='Circuit Depth Comparison (Extreme Values Capped)\nVCGC vs Saha-Belletti Approaches',
            ylabel='Circuit Depth',
            filename='depth_comparison_capped.png',
            exclude_outliers=True,
            outlier_threshold=2.0
        )
        
        # 3. Create a separate chart showing only the problematic benchmarks
        self.create_outlier_focus_chart()
    
    def create_outlier_focus_chart(self):
        """Create a focused chart showing only benchmarks with extreme depth values"""
        if self.data is None:
            return
        
        # Find benchmarks with extreme SB-Minimal values
        sb_minimal_values = self.data['sb_minimal_depth']
        mean_val = sb_minimal_values.mean()
        std_val = sb_minimal_values.std()
        threshold = mean_val + 2 * std_val
        
        outlier_mask = sb_minimal_values > threshold
        
        if not outlier_mask.any():
            print("No outliers found for focused chart")
            return
        
        # Create subset data
        outlier_data = self.data[outlier_mask].copy()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left plot: Linear scale
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        x_pos = np.arange(len(outlier_data))
        width = 0.15
        
        for i, approach in enumerate(approaches):
            values = outlier_data[f'{approach}_depth']
            offset = (i - len(approaches)/2 + 0.5) * width
            ax1.bar(x_pos + offset, values, width, 
                   label=self.labels[approach], color=self.colors[approach], alpha=0.8)
        
        ax1.set_title('Outlier Benchmarks: Linear Scale')
        ax1.set_ylabel('Circuit Depth')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([f"{row['benchmark']}\n({row['nodes']}n,{row['edges']}e,{row['colors']}c)" 
                            for _, row in outlier_data.iterrows()], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Right plot: Log scale
        for i, approach in enumerate(approaches):
            values = outlier_data[f'{approach}_depth']
            values = np.maximum(values, 1)  # Avoid log(0)
            offset = (i - len(approaches)/2 + 0.5) * width
            ax2.bar(x_pos + offset, values, width, 
                   label=self.labels[approach], color=self.colors[approach], alpha=0.8)
        
        ax2.set_title('Outlier Benchmarks: Log Scale')
        ax2.set_ylabel('Circuit Depth (log scale)')
        ax2.set_yscale('log')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f"{row['benchmark']}\n({row['nodes']}n,{row['edges']}e,{row['colors']}c)" 
                            for _, row in outlier_data.iterrows()], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the focused chart
        save_path = self.results_dir / 'depth_outliers_focus.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Outlier focus chart saved to: {save_path}")
        
        plt.show()
    
    def print_summary_statistics(self):
        """Print summary statistics for the data"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY STATISTICS")
        print("="*80)
        
        # Graph characteristics summary
        print(f"\n📊 Graph Characteristics:")
        print(f"   Total benchmarks: {len(self.data)}")
        print(f"   Nodes: {self.data['nodes'].min()}-{self.data['nodes'].max()} (avg: {self.data['nodes'].mean():.1f})")
        print(f"   Edges: {self.data['edges'].min()}-{self.data['edges'].max()} (avg: {self.data['edges'].mean():.1f})")
        print(f"   Colors: {self.data['colors'].min()}-{self.data['colors'].max()} (avg: {self.data['colors'].mean():.1f})")
        
        # Metrics summary
        metrics = ['qubits', 'depth', 'gates']
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for metric in metrics:
            print(f"\n📈 {metric.upper()} Comparison:")
            for approach in approaches:
                col_name = f'{approach}_{metric}'
                if col_name in self.data.columns:
                    values = self.data[col_name]
                    print(f"   {self.labels[approach]}: {values.min()}-{values.max()} (avg: {values.mean():.1f})")
    
    def create_improvement_analysis(self):
        """Analyze and visualize improvements of VCGC over Saha-Belletti approaches"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        metrics = ['qubits', 'depth', 'gates']
        sb_approaches = ['sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            # Calculate improvement percentages
            vcgc_values = self.data[f'vcgc_{metric}']
            improvements = {}
            
            for approach in sb_approaches:
                sb_values = self.data[f'{approach}_{metric}']
                # Calculate percentage improvement: (SB - VCGC) / SB * 100
                improvement = ((sb_values - vcgc_values) / sb_values * 100).fillna(0)
                improvements[approach] = improvement.mean()
            
            # Create bar chart
            approaches = list(improvements.keys())
            values = list(improvements.values())
            colors = [self.colors[app] for app in approaches]
            labels = [self.labels[app] for app in approaches]
            
            bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
            
            # Customize chart
            ax.set_title(f'VCGC Improvement in {metric.upper()}\n(% reduction vs Saha-Belletti)', 
                        fontweight='bold')
            ax.set_ylabel(f'Average % Improvement', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_axisbelow(True)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.annotate(f'{value:.1f}%',
                          xy=(bar.get_x() + bar.get_width()/2, height),
                          xytext=(0, 3),
                          textcoords="offset points",
                          ha='center', va='bottom',
                          fontweight='bold')
            
            # Color-code positive/negative improvements
            for bar, value in zip(bars, values):
                if value < 0:
                    bar.set_color('red')
                    bar.set_alpha(0.5)
        
        plt.tight_layout()
        
        # Save the improvement analysis
        save_path = self.results_dir / 'improvement_analysis.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Improvement analysis saved to: {save_path}")
        
        plt.show()


def main():
    """Main function to run the visualization"""
    parser = argparse.ArgumentParser(description="Visualize VCGC vs Saha-Belletti benchmark results")
    parser.add_argument("--results-dir", "-r", default="../data/vcgc_vs_saha_belletti",
                       help="Directory containing benchmark results")
    parser.add_argument("--format", "-f", choices=['csv', 'json'], default='csv',
                       help="Input file format")
    parser.add_argument("--no-save", action="store_true",
                       help="Don't save charts to files")
    parser.add_argument("--summary-only", action="store_true",
                       help="Only print summary statistics")
    parser.add_argument("--depth-alternatives", action="store_true",
                       help="Create alternative normalized depth charts")
    parser.add_argument("--all-alternatives", action="store_true",
                       help="Create alternative normalized charts for all metrics")
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = BenchmarkVisualizer(args.results_dir)
    
    # Load data
    try:
        if args.format == 'csv':
            visualizer.load_csv_data()
        else:
            visualizer.load_json_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Print summary statistics
    visualizer.print_summary_statistics()
    
    if not args.summary_only:
        if args.all_alternatives:
            # Create alternative visualizations for all metrics
            visualizer.create_all_comparison_alternatives()
        elif args.depth_alternatives:
            # Create alternative depth visualizations
            visualizer.create_depth_comparison_alternatives()
        else:
            # Create all charts with normalization
            visualizer.create_all_charts(save_charts=not args.no_save, normalize_all=True)
        
        # Create improvement analysis
        visualizer.create_improvement_analysis()


if __name__ == "__main__":
    main()