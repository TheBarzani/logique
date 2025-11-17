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
            'vcgc': '#FF1744',           # Vibrant Red (attention-grabbing)
            'sb_original': '#5E35B1',    # Deep Purple
            'sb_minimal': '#1E88E5',     # Blue
            'sb_simple': '#00897B',      # Teal
            'sb_balanced': '#FFA726'     # Orange
        }
        
        # Define approach labels
        self.labels = {
            'vcgc': 'Proposed',
            'sb_original': 'Saha et al.',
            'sb_minimal': 'Belletti-Minimal',
            'sb_simple': 'Belletti-Simple',
            'sb_balanced': 'Belletti-Balanced'
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
                'vcgc_width': data['vcgc']['width'],
                'vcgc_depth': data['vcgc']['depth'],
                'vcgc_gates': data['vcgc']['gates']
            }
            
            # Add Saha-Belletti metrics
            for oracle_type, metrics in data['saha_belletti'].items():
                row[f'sb_{oracle_type}_width'] = metrics['width']
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
            metric: The metric to plot ('width', 'depth', or 'gates')
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
        
        # Sort data by VCGC metric values (lowest to highest)
        vcgc_metric_col = f'vcgc_{metric}'
        sorted_data = self.data.sort_values(by=vcgc_metric_col).reset_index(drop=True)
        
        # Prepare data
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        graph_labels = [f"{row['benchmark']}\n({row['nodes']}n, {row['edges']}e, {row['colors']}c)" 
                       for _, row in sorted_data.iterrows()]
        
        # Extract metric data for each approach
        metric_data = {}
        for approach in approaches:
            col_name = f'{approach}_{metric}'
            if col_name in sorted_data.columns:
                metric_data[approach] = sorted_data[col_name].values
            else:
                print(f"Warning: Column {col_name} not found in data")
                metric_data[approach] = np.zeros(len(sorted_data))
        
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
                        outlier_benchmarks = [sorted_data.iloc[j]['benchmark'] for j in range(len(outliers)) if outliers[j]]
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
        n_benchmarks = len(sorted_data)
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
                        fontsize = 10
                    else:
                        label_y = height + max(height * 0.01, 1)
                        fontsize = 10
                    
                    ax.annotate(f'{int(height)}',
                              xy=(bar.get_x() + bar.get_width()/2, label_y),
                              ha='center', va='bottom',
                              fontsize=fontsize, rotation=90)
        
        # Adjust y-axis limits to prevent label cutoff
        if log_scale:
            # For log scale, extend the upper limit by a multiplicative factor
            ax.set_ylim(bottom=ax.get_ylim()[0], top=ax.get_ylim()[1] * 1.6)
        else:
            # For linear scale, add some padding at the top
            y_max = ax.get_ylim()[1]
            ax.set_ylim(bottom=0, top=y_max * 1.1)
        
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
        """Create all metric charts with optional normalization"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        # Chart 1: Width (with normalization options)
        if normalize_all:
            # Create both log scale and outlier-excluded versions
            self.create_grouped_bar_chart(
                metric='width',
                title='Circuit Width Comparison (Log Scale)',
                ylabel='Circuit Width',
                filename='width_comparison_log.png' if save_charts else None,
                log_scale=True
            )
            
            self.create_grouped_bar_chart(
                metric='width',
                title='Quantum Circuit Comparison: Circuit Width (Outliers Capped)\nVCGC vs Saha-Belletti Approaches',
                ylabel='Circuit Width',
                filename='width_comparison_normalized.png' if save_charts else None,
                exclude_outliers=True,
                outlier_threshold=2.0
            )
        else:
            # Original chart
            self.create_grouped_bar_chart(
                metric='width',
                title='Quantum Circuit Comparison: Circuit Width\nVCGC vs Saha-Belletti Approaches',
                ylabel='Circuit Width',
                filename='width_comparison.png' if save_charts else None
            )
        
        # Chart 2: Depth (with normalization options)
        if normalize_all:
            # Create both log scale and outlier-excluded versions
            self.create_grouped_bar_chart(
                metric='depth',
                title='Circuit Depth Comparison (Log Scale)',
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
                outlier_threshold=2.0
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
                title='Number of Gates Comparsion (Log Scale)',
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
        
        metrics = ['width', 'depth', 'gates']
        
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
        
        # Create subset data and sort by VCGC metric values
        outlier_data = self.data[outlier_mask].copy()
        vcgc_metric_col = f'vcgc_{metric}'
        outlier_data = outlier_data.sort_values(by=vcgc_metric_col).reset_index(drop=True)
        
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
        metrics = ['width', 'depth', 'gates']
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
        axes = axes.flatten()  # Flatten for easy indexing
        metrics = ['width', 'depth', 'gates']
        sb_approaches = ['sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for i, metric in enumerate(metrics):
            if i >= len(axes):  # Safety check
                break
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
        
        # Hide unused subplot
        if len(metrics) < len(axes):
            axes[-1].set_visible(False)
        
        plt.tight_layout()
        
        # Save the improvement analysis
        save_path = self.results_dir / 'improvement_analysis.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Improvement analysis saved to: {save_path}")
        
        plt.show()
    
    def create_pareto_frontier_plot(self, save_chart: bool = True, figsize: tuple = (14, 10)):
        """
        Create a scatter plot showing the trade-off between circuit depth and total qubits
        with Pareto frontier visualization.
        
        Args:
            save_chart: Whether to save the chart to a file
            figsize: Figure size as (width, height)
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() or load_json_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        # Collect all points for each approach
        all_points = []
        
        for approach in approaches:
            depth_col = f'{approach}_depth'
            width_col = f'{approach}_width'
            gates_col = f'{approach}_gates'
            
            if depth_col not in self.data.columns or width_col not in self.data.columns:
                continue
            
            for idx, row in self.data.iterrows():
                depth = row[depth_col]
                width = row[width_col]
                gates = row[gates_col] if gates_col in self.data.columns else 100
                benchmark = row['benchmark']
                
                all_points.append({
                    'approach': approach,
                    'depth': depth,
                    'width': width,
                    'gates': gates,
                    'benchmark': benchmark
                })
        
        # Plot points for each approach
        for approach in approaches:
            approach_points = [p for p in all_points if p['approach'] == approach]
            
            if not approach_points:
                continue
            
            depths = [p['depth'] for p in approach_points]
            widths = [p['width'] for p in approach_points]
            gates = [p['gates'] for p in approach_points]
            
            # Normalize gate counts for bubble size (scale between 50 and 500)
            max_gates = max(gates) if gates else 1
            min_gates = min(gates) if gates else 0
            gate_range = max_gates - min_gates if max_gates != min_gates else 1
            sizes = [50 + 450 * (g - min_gates) / gate_range for g in gates]
            
            # Plot with semi-transparent bubbles
            scatter = ax.scatter(
                depths, 
                widths, 
                s=sizes,
                c=self.colors[approach],
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5,
                label=self.labels[approach]
            )
        
        # Calculate and plot Pareto frontier
        # A point is on the Pareto frontier if no other point is better in both dimensions
        pareto_points = []
        for point in all_points:
            is_dominated = False
            for other in all_points:
                # A point is dominated if another point has both lower depth AND lower width
                if other['depth'] < point['depth'] and other['width'] < point['width']:
                    is_dominated = True
                    break
            if not is_dominated:
                pareto_points.append(point)
        
        # Sort Pareto points by depth for drawing the frontier line
        pareto_points.sort(key=lambda p: p['depth'])
        
        if pareto_points:
            pareto_depths = [p['depth'] for p in pareto_points]
            pareto_widths = [p['width'] for p in pareto_points]
            
            # Draw Pareto frontier as a stepped line
            ax.plot(pareto_depths, pareto_widths, 
                   'k--', linewidth=2, alpha=0.5, 
                   label='Pareto Frontier', zorder=1)
            
            # Highlight Pareto optimal points
            ax.scatter(pareto_depths, pareto_widths,
                      s=100, facecolors='none', edgecolors='black',
                      linewidth=2, zorder=10)
        
        # Customize the plot
        ax.set_xlabel('Circuit Depth (log scale)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Circuit Width', fontsize=12, fontweight='bold')
        ax.set_title('Depth-Width Trade-Off Space\nVCGC vs Saha-Belletti Approaches\n(Bubble size = Gate Count)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Use log scale for depth
        ax.set_xscale('log')
        
        # Add legend
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3, which='both')
        ax.set_axisbelow(True)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if requested
        if save_chart:
            save_path = self.results_dir / 'pareto_frontier_trade_off.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Pareto frontier plot saved to: {save_path}")
        
        plt.show()
        
        # Print Pareto optimal points summary
        print("\n" + "="*80)
        print("PARETO OPTIMAL POINTS")
        print("="*80)
        print(f"\nFound {len(pareto_points)} Pareto optimal (Method, Benchmark) combinations:\n")
        for p in pareto_points:
            print(f"  {self.labels[p['approach']]:15} | {p['benchmark']:20} | "
                  f"Depth: {p['depth']:6.0f} | Width: {p['width']:4.0f} | Gates: {p['gates']:6.0f}")
        print("="*80)


def main():
    """Main function to run the visualization"""
    parser = argparse.ArgumentParser(description="Visualize VCGC vs Saha-Belletti benchmark results")
    parser.add_argument("--results-dir", "-r", default="../data/output",
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
    parser.add_argument("--metric", "-m", choices=['width', 'depth', 'gates'],
                       help="Create chart for a specific metric only")
    parser.add_argument("--pareto-frontier", action="store_true",
                       help="Create Pareto frontier trade-off plot")
    
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
        if args.metric:
            # Create chart for specific metric
            visualizer.create_grouped_bar_chart(
                metric=args.metric,
                title=f'Quantum Circuit Comparison: {args.metric.replace("_", " ").title()}\nVCGC vs Saha-Belletti Approaches',
                ylabel=args.metric.replace("_", " ").title(),
                filename=f'{args.metric}_comparison.png' if not args.no_save else None
            )
        elif args.pareto_frontier:
            # Create Pareto frontier trade-off plot
            visualizer.create_pareto_frontier_plot(save_chart=not args.no_save)
        elif args.all_alternatives:
            # Create alternative visualizations for all metrics
            visualizer.create_all_comparison_alternatives()
        elif args.depth_alternatives:
            # Create alternative depth visualizations
            visualizer.create_depth_comparison_alternatives()
        else:
            # Create all charts with normalization
            visualizer.create_all_charts(save_charts=not args.no_save, normalize_all=True)
            
            # Create Pareto frontier plot
            print("\nCreating Pareto frontier trade-off plot...")
            visualizer.create_pareto_frontier_plot(save_chart=not args.no_save)
        
        # Create improvement analysis
        visualizer.create_improvement_analysis()


def example_usage():
    """Example of how to use the visualizer"""
    # Create visualizer
    visualizer = BenchmarkVisualizer("../data/output")
    
    # Load data (try CSV first, then JSON)
    try:
        visualizer.load_csv_data()
    except FileNotFoundError:
        try:
            visualizer.load_json_data()
        except FileNotFoundError:
            print("No benchmark data found. Run generate_benchmarks.py first.")
            return
    
    # Create width comparison
    print("Creating width comparison...")
    visualizer.create_grouped_bar_chart(
        metric='width',
        title='Circuit Width Comparison: VCGC vs Saha-Belletti',
        ylabel='Circuit Width',
        filename='width_comparison.png'
    )
    
    # Create Pareto frontier plot
    print("Creating Pareto frontier plot...")
    visualizer.create_pareto_frontier_plot()


if __name__ == "__main__":
    main()