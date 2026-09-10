# Vertex Coloring Instances Benchmarks
- Link: [sites.google.com/site/graphcoloring/vertex-coloring](https://sites.google.com/site/graphcoloring/vertex-coloring)

# Chosen Benchmarks
- K3
- K5
- myciel3
- myciel4
- myciel5
- 2-Insertions_3
- 1-FullIns_3
- linear_2_colored
- grid6_2_colored
- zed-city_2019

# VCGC vs Saha-Belletti Benchmark Generator

This directory contains scripts to automate the benchmark comparison between VCGC and Saha-Belletti approaches for quantum vertex coloring problems.

## Files

- `generate_benchmarks.py` - Main benchmark generation script with comprehensive functionality
- `run_benchmarks.py` - Simple example script showing how to use the benchmark generator (located in examples/)

## Usage

### Quick Start

To run all benchmarks with default settings:

```bash
cd examples
python run_benchmarks.py
```

To test a single benchmark:

```bash
cd examples
python run_benchmarks.py K3
```

### Advanced Usage

For more control over the benchmark generation process:

```bash
cd data
python generate_benchmarks.py --help
```

Options:
- `--benchmarks-dir` or `-b`: Directory containing .col benchmark files (default: ../data/benchmarks)
- `--output-dir` or `-o`: Output directory for results (default: ../data/vcgc_vs_saha_belletti)
- `--draw-circuits` or `-d`: Generate circuit visualizations (default: False)

Example with custom settings:

```bash
python generate_benchmarks.py -b ./benchmarks -o ./results -d
```

## Output Files

The benchmark generator creates several types of output files:

### For each benchmark:
- `{benchmark}_vcgc.v` - Verilog representation of the VCGC logic network
- `{benchmark}_vcgc.dot` - DOT file for logic network visualization
- `{benchmark}_vcgc.qasm` - QASM file for the VCGC quantum circuit
- `{benchmark}_sb_{oracle_type}.qasm` - QASM files for each Saha-Belletti oracle type
- `{benchmark}_graph.png` - Graph visualization (if `draw_circuits=True`)

### Summary files:
- `benchmark_results.csv` - Comprehensive results in CSV format
- `benchmark_results.json` - Detailed results in JSON format

## CSV Output Format

The CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| benchmark | Name of the benchmark file |
| nodes | Number of graph vertices |
| edges | Number of graph edges |
| colors | Number of available colors |
| vcgc_qubits | Number of qubits in VCGC circuit |
| vcgc_depth | Circuit depth of VCGC circuit |
| vcgc_gates | Number of gates in VCGC circuit |
| sb_{oracle}_qubits | Number of qubits for each Saha-Belletti oracle type |
| sb_{oracle}_depth | Circuit depth for each Saha-Belletti oracle type |
| sb_{oracle}_gates | Number of gates for each Saha-Belletti oracle type |

Oracle types tested: `original`, `minimal`, `simple`, `balanced` 