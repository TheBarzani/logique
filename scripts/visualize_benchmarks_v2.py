#!/usr/bin/env python3
"""
Advanced Benchmark Visualization Script (Version 2)

This script provides enhanced visualizations for comparing VCGC vs Saha-Belletti
approaches with scalability analysis, heatmaps, win/loss matrices, and comprehensive dashboards.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import argparse
from matplotlib.gridspec import GridSpec


class AdvancedBenchmarkVisualizer:
    """Class for advanced benchmark visualization and analysis"""
    
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
        
        # Add computed columns
        self.data['density'] = self.data['edges'] / self.data['nodes']
        
        # Size categories
        self.data['size_category'] = pd.cut(
            self.data['nodes'], 
            bins=[0, 10, 25, 50, 100],
            labels=['Small (≤10)', 'Medium (11-25)', 'Large (26-50)', 'Very Large (>50)']
        )
        
        # Density categories
        self.data['density_category'] = pd.cut(
            self.data['density'],
            bins=[0, 2, 4, 6, 100],
            labels=['Sparse', 'Medium', 'Dense', 'Very Dense']
        )
        
        print(f"Loaded data for {len(self.data)} benchmarks from CSV")
        return self.data
    
    def categorize_benchmarks(self):
        """Analyze and categorize benchmarks"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv_data() first.")
        
        print("\n" + "="*80)
        print("BENCHMARK CATEGORIZATION ANALYSIS")
        print("="*80)
        
        print("\n📊 By Size:")
        size_summary = self.data.groupby('size_category').agg({
            'benchmark': 'count',
            'nodes': ['min', 'max', 'mean'],
            'edges': ['min', 'max', 'mean']
        })
        print(size_summary)
        
        print("\n📊 By Density:")
        density_summary = self.data.groupby('density_category').agg({
            'benchmark': 'count',
            'density': ['min', 'max', 'mean']
        })
        print(density_summary)
        
        # Identify problematic benchmarks
        print("\n⚠️  Problematic Benchmarks (with extreme outliers):")
        for metric in ['width', 'depth', 'gates']:
            sb_minimal_col = f'sb_minimal_{metric}'
            if sb_minimal_col in self.data.columns:
                mean_val = self.data[sb_minimal_col].mean()
                std_val = self.data[sb_minimal_col].std()
                outliers = self.data[self.data[sb_minimal_col] > mean_val + 2*std_val]
                if len(outliers) > 0:
                    print(f"\n  {metric.upper()}:")
                    for _, row in outliers.iterrows():
                        print(f"    - {row['benchmark']}: {row[sb_minimal_col]:.0f} "
                              f"({row['nodes']}n, {row['edges']}e, {row['colors']}c)")
    
    def create_scalability_plot(self, save_chart: bool = True, figsize: tuple = (18, 5)):
        """
        Create scatter plots showing how metrics scale with graph size
        """
        if self.data is None:
            raise ValueError("No data loaded.")
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        metrics = ['width', 'depth', 'gates']
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            for approach in approaches:
                col_name = f'{approach}_{metric}'
                if col_name in self.data.columns:
                    # Plot against number of nodes
                    ax.scatter(
                        self.data['nodes'],
                        self.data[col_name],
                        label=self.labels[approach],
                        color=self.colors[approach],
                        s=100,
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=0.5
                    )
                    
                    # Add trend line (polynomial fit)
                    valid_mask = self.data[col_name] > 0
                    if valid_mask.sum() >= 3:  # Need at least 3 points
                        z = np.polyfit(self.data.loc[valid_mask, 'nodes'], 
                                      self.data.loc[valid_mask, col_name], 2)
                        p = np.poly1d(z)
                        x_trend = np.linspace(self.data['nodes'].min(), 
                                            self.data['nodes'].max(), 100)
                        ax.plot(x_trend, p(x_trend), 
                               color=self.colors[approach], 
                               linestyle='--', 
                               alpha=0.3,
                               linewidth=1.5)
            
            ax.set_xlabel('Graph Size (nodes)', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'{metric.capitalize()}', fontsize=11, fontweight='bold')
            ax.set_title(f'Scalability: {metric.capitalize()} vs Graph Size', fontweight='bold')
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8, loc='upper left')
        
        plt.tight_layout()
        
        if save_chart:
            save_path = self.results_dir / 'scalability_analysis.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Scalability plot saved to: {save_path}")
        
        plt.show()
    
    def create_heatmap_comparison(self, save_chart: bool = True, figsize: tuple = (18, 8)):
        """
        Create heatmap showing relative performance across all benchmarks
        """
        if self.data is None:
            raise ValueError("No data loaded.")
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        metrics = ['width', 'depth', 'gates']
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            # Create matrix: benchmarks x approaches
            matrix = []
            for _, row in self.data.iterrows():
                row_data = [row[f'{approach}_{metric}'] for approach in approaches]
                # Normalize by minimum value in row (1.0 = best, higher = worse)
                min_val = min(row_data)
                if min_val > 0:
                    row_data = [val / min_val for val in row_data]
                else:
                    row_data = [1.0] * len(row_data)
                matrix.append(row_data)
            
            matrix = np.array(matrix)
            
            # Create heatmap
            im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=1.0)
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(approaches)))
            ax.set_yticks(np.arange(len(self.data)))
            ax.set_xticklabels([self.labels[a] for a in approaches], 
                              rotation=45, ha='right', fontsize=9)
            ax.set_yticklabels(self.data['benchmark'], fontsize=8)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Relative Performance\n(1.0 = best)', rotation=270, labelpad=20)
            
            # Add value annotations (only for small matrices)
            if len(self.data) <= 15:
                for i in range(len(self.data)):
                    for j in range(len(approaches)):
                        text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                                     ha="center", va="center", 
                                     color="black" if matrix[i, j] < 5 else "white", 
                                     fontsize=7)
            
            ax.set_title(f'{metric.capitalize()} Relative Performance', fontweight='bold')
        
        plt.tight_layout()
        
        if save_chart:
            save_path = self.results_dir / 'heatmap_comparison.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Heatmap saved to: {save_path}")
        
        plt.show()
    
    def create_win_loss_matrix(self, save_chart: bool = True, figsize: tuple = (18, 6)):
        """
        Create a matrix showing head-to-head comparisons between methods
        """
        if self.data is None:
            raise ValueError("No data loaded.")
        
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        metrics = ['width', 'depth', 'gates']
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            # Create win matrix: approach A vs approach B
            n = len(approaches)
            win_matrix = np.zeros((n, n))
            
            for i, approach_a in enumerate(approaches):
                for j, approach_b in enumerate(approaches):
                    if i == j:
                        continue
                    
                    # Count how many times A beats B
                    wins = (self.data[f'{approach_a}_{metric}'] < 
                           self.data[f'{approach_b}_{metric}']).sum()
                    win_matrix[i, j] = wins
            
            # Create heatmap
            im = ax.imshow(win_matrix, cmap='Blues', aspect='auto', 
                          vmin=0, vmax=len(self.data))
            
            # Set ticks and labels
            ax.set_xticks(np.arange(n))
            ax.set_yticks(np.arange(n))
            ax.set_xticklabels([self.labels[a] for a in approaches], 
                              rotation=45, ha='right', fontsize=9)
            ax.set_yticklabels([self.labels[a] for a in approaches], fontsize=9)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Wins', rotation=270, labelpad=20)
            
            # Add value annotations
            for i in range(n):
                for j in range(n):
                    if i != j:
                        text = ax.text(j, i, f'{int(win_matrix[i, j])}',
                                     ha="center", va="center", 
                                     color="white" if win_matrix[i, j] > len(self.data)/2 else "black",
                                     fontsize=10, fontweight='bold')
            
            ax.set_title(f'{metric.capitalize()} Head-to-Head Wins\n(out of {len(self.data)} benchmarks)', 
                        fontweight='bold', fontsize=11)
            ax.set_ylabel('Method A', fontweight='bold')
            ax.set_xlabel('Method B', fontweight='bold')
        
        plt.tight_layout()
        
        if save_chart:
            save_path = self.results_dir / 'win_loss_matrix.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Win/loss matrix saved to: {save_path}")
        
        plt.show()
    
    def create_best_method_distribution(self, ax=None, save_chart: bool = True):
        """
        Create a bar chart showing which method wins most often
        """
        if self.data is None:
            raise ValueError("No data loaded.")
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            standalone = True
        else:
            standalone = False
        
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        metrics = ['width', 'depth', 'gates']
        
        wins_by_approach = {approach: 0 for approach in approaches}
        
        # Count wins for each approach across all metrics
        for metric in metrics:
            for _, row in self.data.iterrows():
                values = {approach: row[f'{approach}_{metric}'] for approach in approaches}
                winner = min(values, key=values.get)
                wins_by_approach[winner] += 1
        
        # Create bar chart
        labels = [self.labels[a] for a in approaches]
        values = [wins_by_approach[a] for a in approaches]
        colors_list = [self.colors[a] for a in approaches]
        
        bars = ax.bar(labels, values, color=colors_list, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Customize chart
        ax.set_title('Best Method Distribution\n(Total wins across all benchmarks & metrics)', 
                    fontweight='bold', fontsize=12)
        ax.set_ylabel('Number of Wins', fontweight='bold')
        ax.set_xlabel('Method', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{int(value)}',
                      xy=(bar.get_x() + bar.get_width()/2, height),
                      xytext=(0, 3),
                      textcoords="offset points",
                      ha='center', va='bottom',
                      fontweight='bold', fontsize=11)
        
        if standalone:
            plt.tight_layout()
            
            if save_chart:
                save_path = self.results_dir / 'best_method_distribution.png'
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Best method distribution saved to: {save_path}")
            
            plt.show()
    
    def create_summary_dashboard(self, save_chart: bool = True):
        """
        Create a comprehensive dashboard showing all key insights
        """
        if self.data is None:
            raise ValueError("No data loaded.")
        
        fig = plt.figure(figsize=(20, 14))
        gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
        
        # Row 1: Win/loss matrices for each metric
        metrics = ['width', 'depth', 'gates']
        approaches = ['vcgc', 'sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        
        for idx, metric in enumerate(metrics):
            ax = fig.add_subplot(gs[0, idx])
            
            # Create mini win matrix
            n = len(approaches)
            win_matrix = np.zeros((n, n))
            
            for i, approach_a in enumerate(approaches):
                for j, approach_b in enumerate(approaches):
                    if i != j:
                        wins = (self.data[f'{approach_a}_{metric}'] < 
                               self.data[f'{approach_b}_{metric}']).sum()
                        win_matrix[i, j] = wins
            
            im = ax.imshow(win_matrix, cmap='Blues', aspect='auto', 
                          vmin=0, vmax=len(self.data))
            ax.set_xticks(np.arange(n))
            ax.set_yticks(np.arange(n))
            ax.set_xticklabels([self.labels[a][:8] for a in approaches], 
                              rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels([self.labels[a][:8] for a in approaches], fontsize=8)
            ax.set_title(f'{metric.capitalize()} Wins', fontweight='bold', fontsize=10)
            
            # Add annotations
            for i in range(n):
                for j in range(n):
                    if i != j:
                        ax.text(j, i, f'{int(win_matrix[i, j])}',
                               ha="center", va="center", 
                               color="white" if win_matrix[i, j] > len(self.data)/2 else "black",
                               fontsize=7, fontweight='bold')
        
        # Row 2: Scalability plots
        for idx, metric in enumerate(metrics):
            ax = fig.add_subplot(gs[1, idx])
            
            for approach in approaches:
                col_name = f'{approach}_{metric}'
                if col_name in self.data.columns:
                    ax.scatter(
                        self.data['nodes'],
                        self.data[col_name],
                        label=self.labels[approach],
                        color=self.colors[approach],
                        s=60,
                        alpha=0.6,
                        edgecolors='black',
                        linewidth=0.5
                    )
            
            ax.set_xlabel('Nodes', fontsize=9, fontweight='bold')
            ax.set_ylabel(f'{metric.capitalize()}', fontsize=9, fontweight='bold')
            ax.set_title(f'{metric.capitalize()} Scalability', fontweight='bold', fontsize=10)
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=6, loc='upper left')
        
        # Row 3, Left: Best method distribution
        ax = fig.add_subplot(gs[2, 0])
        self.create_best_method_distribution(ax=ax, save_chart=False)
        
        # Row 3, Middle: Average improvement
        ax = fig.add_subplot(gs[2, 1])
        sb_approaches = ['sb_original', 'sb_minimal', 'sb_simple', 'sb_balanced']
        avg_improvements = []
        
        for approach in sb_approaches:
            improvements = []
            for metric in metrics:
                vcgc_values = self.data[f'vcgc_{metric}']
                sb_values = self.data[f'{approach}_{metric}']
                improvement = ((sb_values - vcgc_values) / sb_values * 100).fillna(0)
                improvements.append(improvement.mean())
            avg_improvements.append(np.mean(improvements))
        
        colors_list = [self.colors[a] for a in sb_approaches]
        labels_list = [self.labels[a] for a in sb_approaches]
        bars = ax.bar(labels_list, avg_improvements, color=colors_list, 
                     alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax.set_title('Average VCGC Improvement\n(across all metrics)', 
                    fontweight='bold', fontsize=10)
        ax.set_ylabel('% Improvement', fontweight='bold', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        ax.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, avg_improvements):
            height = bar.get_height()
            ax.annotate(f'{value:.1f}%',
                      xy=(bar.get_x() + bar.get_width()/2, height),
                      xytext=(0, 3),
                      textcoords="offset points",
                      ha='center', va='bottom',
                      fontweight='bold', fontsize=9)
        
        # Row 3, Right: Benchmark coverage
        ax = fig.add_subplot(gs[2, 2])
        size_counts = self.data['size_category'].value_counts()
        colors_pie = ['#2E86AB', '#F18F01', '#C73E1D', '#6A994E']
        ax.pie(size_counts.values, labels=size_counts.index, autopct='%1.1f%%',
               colors=colors_pie, startangle=90)
        ax.set_title('Benchmark Size Distribution', fontweight='bold', fontsize=10)
        
        plt.suptitle('VCGC vs Saha-Belletti: Comprehensive Comparison Dashboard', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        if save_chart:
            save_path = self.results_dir / 'summary_dashboard.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Dashboard saved to: {save_path}")
        
        plt.show()
    
    def suggest_benchmarks(self):
        """Suggest additional benchmarks to fill gaps"""
        if self.data is None:
            raise ValueError("No data loaded.")
        
        print("\n" + "="*80)
        print("BENCHMARK SUGGESTIONS")
        print("="*80)
        
        # Check coverage
        size_coverage = self.data.groupby('size_category').size()
        density_coverage = self.data.groupby('density_category').size()
        
        print("\n📈 Current Coverage:")
        print(f"\n  By Size:\n{size_coverage}")
        print(f"\n  By Density:\n{density_coverage}")
        
        print("\n💡 Suggestions to Improve Coverage:")
        
        # Suggest based on gaps
        suggestions = []
        
        if size_coverage.get('Small (≤10)', 0) < 5:
            suggestions.append("  ✓ Add more SMALL graphs (≤10 nodes):")
            suggestions.append("    - K4, wheel_4, petersen, diamond")
        
        if size_coverage.get('Medium (11-25)', 0) < 5:
            suggestions.append("  ✓ Add more MEDIUM graphs (11-25 nodes):")
            suggestions.append("    - queen5_5, dodecahedron, desargues, huck, jean")
        
        if size_coverage.get('Large (26-50)', 0) < 3:
            suggestions.append("  ✓ Add more LARGE graphs (26-50 nodes):")
            suggestions.append("    - queen6_6, queen7_7, games120, anna, david")
        
        if density_coverage.get('Sparse', 0) < 3:
            suggestions.append("  ✓ Add more SPARSE graphs (low edge density):")
            suggestions.append("    - tree structures, path graphs, star graphs")
        
        if density_coverage.get('Dense', 0) < 3:
            suggestions.append("  ✓ Add more DENSE graphs (high connectivity):")
            suggestions.append("    - hamming6-2, hamming6-4, complete graphs")
        
        if suggestions:
            for s in suggestions:
                print(s)
        else:
            print("  ✓ Good coverage across all categories!")
        
        print("\n📚 Recommended Real-World Benchmarks:")
        print("  - Register allocation: fpsol2.i.1, fpsol2.i.2, fpsol2.i.3")
        print("  - Graph coloring competitions: le450_5a, le450_5b, le450_5c")
        print("  - Stanford benchmarks: stanford, games120")
        print("  - DIMACS benchmarks: DSJC125.1, DSJC250.5")


def main():
    """Main function to run advanced visualizations"""
    parser = argparse.ArgumentParser(
        description="Advanced visualization for VCGC vs Saha-Belletti benchmark results"
    )
    parser.add_argument("--results-dir", "-r", default="../data/output",
                       help="Directory containing benchmark results")
    parser.add_argument("--no-save", action="store_true",
                       help="Don't save charts to files")
    parser.add_argument("--analysis", "-a", 
                       choices=['all', 'scalability', 'heatmap', 'winloss', 
                               'dashboard', 'categorize', 'suggest'],
                       default='all',
                       help="Type of analysis to perform")
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = AdvancedBenchmarkVisualizer(args.results_dir)
    
    # Load data
    try:
        visualizer.load_csv_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Run requested analysis
    if args.analysis in ['all', 'categorize']:
        visualizer.categorize_benchmarks()
    
    if args.analysis in ['all', 'suggest']:
        visualizer.suggest_benchmarks()
    
    if args.analysis in ['all', 'scalability']:
        print("\n📊 Creating scalability analysis...")
        visualizer.create_scalability_plot(save_chart=not args.no_save)
    
    if args.analysis in ['all', 'heatmap']:
        print("\n🔥 Creating heatmap comparison...")
        visualizer.create_heatmap_comparison(save_chart=not args.no_save)
    
    if args.analysis in ['all', 'winloss']:
        print("\n🎯 Creating win/loss matrix...")
        visualizer.create_win_loss_matrix(save_chart=not args.no_save)
    
    if args.analysis in ['all', 'dashboard']:
        print("\n📈 Creating comprehensive dashboard...")
        visualizer.create_summary_dashboard(save_chart=not args.no_save)
    
    print("\n✅ Visualization complete!")


if __name__ == "__main__":
    main()
