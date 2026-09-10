# Execution Comparison Scripts

This directory contains scripts to compare the execution performance of VCGC and Saha-Belletti methods on linear graphs of increasing size.

## Files

- `generate_exec_comparison.py` - Main script that runs the full comparison
- `test_exec_comparison.py` - Test script to validate setup before running full comparison  
- `generate_linear_graphs.py` - Utility to generate/verify linear graph DIMACS files
- `README.md` - This file

## Usage

### 1. Setup and Validation

First, verify that all linear graph files exist and test the setup:

```bash
cd scripts/
python generate_linear_graphs.py  # Generate linear graphs if needed
python test_exec_comparison.py    # Test the setup with a small example
```

### 2. Run Full Comparison

Once validation passes, run the full comparison:

```bash
python generate_exec_comparison.py
```

This will:
- Process linear graphs from 1 to 7 vertices
- Generate circuits using 5 methods: VCGC, original, simple, minimal, balanced
- Execute circuits on IBM quantum backend
- Save results to CSV file with timestamp
- Generate comparison plots

### 3. Configuration

You can modify the following parameters in `generate_exec_comparison.py`:

- `shots`: Number of quantum measurements (default: 10000 for production, 1000 for testing)
- `start_vertices`/`end_vertices`: Range of graph sizes to test
- `backend_name`: Specific IBM backend to use (defaults to least busy)

### Output Files

The script generates several output files in `../data/execution/`:

- `execution_comparison_YYYYMMDD_HHMMSS.csv` - Raw results data
- `success_probability_comparison_YYYYMMDD_HHMMSS.png` - Main comparison plot
- `detailed_metrics_comparison_YYYYMMDD_HHMMSS.png` - Detailed metrics plots

### CSV Output Format

The CSV file contains the following columns:

- `method`: Circuit generation method (vcgc, original, simple, minimal, balanced)
- `num_vertices`: Number of vertices in the graph
- `num_edges`: Number of edges in the graph  
- `available_colors`: Number of colors used for coloring
- `original_qubits`: Number of qubits in original circuit
- `original_depth`: Depth of original circuit
- `original_gates`: Number of gates in original circuit
- `transpiled_depth`: Depth after transpilation to target backend
- `transpiled_gates`: Number of gates after transpilation
- `success_probability`: Calculated success probability
- `total_shots`: Number of measurements taken
- `job_id`: IBM job ID for the execution
- `backend_name`: Name of IBM backend used
- `timestamp`: When the experiment was run

## Requirements

Make sure you have:

1. IBM Quantum account set up with `QiskitRuntimeService`
2. All dependencies installed (see main requirements.txt)
3. VCGC and Saha-Belletti libraries properly installed
4. Sufficient IBM Quantum credits for the experiments

## Notes

- The script includes delays between executions to avoid overwhelming the quantum backend
- Success probability calculation for Saha-Belletti methods is simplified and may need refinement
- For testing, reduce the number of shots to avoid using too many credits
- The script is designed to be resumable - you can stop and restart if needed

## Troubleshooting

If you encounter issues:

1. Run `test_exec_comparison.py` first to identify problems
2. Check IBM Quantum service connection
3. Verify all required libraries are installed
4. Ensure linear graph files exist in `../data/execution/`

For backend-related issues, you may need to:
- Check backend availability
- Verify your IBM Quantum account status
- Switch to a different backend if the current one is offline
