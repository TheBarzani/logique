# A module that utilizes the Tweedledum library to synthesize quantum circuits

from tweedledum.synthesis import xag_synth
from tweedledum.qiskit import to_qiskit
from tweedledum.bool_function_compiler.bool_function import BoolFunction

class Synthesizer:
    """A class to handle synthesis of quantum circuits using Tweedledum."""

    def __init__(self, cf = None):
        if (cf != None):
            self.logic_network = cf._logic_network
        else:
            self.logic_network = None
        self.tweedledum_circuit = None
        self.qiskit_circuit = None

    @staticmethod
    def xag_synthesis_preview(cf):
        """Custom synthesizer using XAG synthesis instead of PKRM."""
        
        # Get the LogicNetwork object from cf.network
        logic_network = cf._logic_network
        
        # Perform XAG synthesis ONCE and store the result
        tweedledum_circuit = xag_synth(logic_network)
        print(f"Number of qubits in Tweedledum circuit: {tweedledum_circuit.num_qubits()}")
        print(tweedledum_circuit)
        qc_qiskit = to_qiskit(tweedledum_circuit, circuit_type="gatelist")

        return qc_qiskit
    
    def synthesize_with_xag(self):
        """Synthesize the logic network using XAG synthesis."""
        self.tweedledum_circuit = xag_synth(self.logic_network)
        self.qiskit_circuit = to_qiskit(self.tweedledum_circuit, circuit_type="gatelist")
        return self.qiskit_circuit
    
    def print_circuit_info(self):
        """Print information about the synthesized circuit."""
        if self.tweedledum_circuit:
            print(f"Number of qubits: {self.tweedledum_circuit.num_qubits()}")
            print(self.tweedledum_circuit)
        else:
            print("No circuit synthesized yet.")

    def draw_circuit(self, output='mpl', filename='synthesized_circuit.png'):
        """Draw the synthesized circuit and save it to a file."""
        if self.qiskit_circuit:
            self.qiskit_circuit.draw(output=output, filename=filename)
        else:
            print("No Qiskit circuit available to draw.")

    def from_verilog_file(self, path: str):
        """Get classical function from a verilog file."""
        cf = BoolFunction.from_verilog_file(path)
        self.logic_network = cf._logic_network
    
    def synthesize_saha():
        # TODO: Implement the synthesis method described in the paper:
        #       Circuit Design for K-coloring Problem and its Implementation on Near-term Quantum Devices
        None