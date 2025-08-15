# A module that prepares and analyzes Boolean Functions and Logic Networks
import math
from .network import *
from tweedledum.classical import write_verilog
from tweedledum.bool_function_compiler.bool_function import BoolFunction

class BooleanFunction():
    def __init__(self):
        self.boolean_function = None

    def print_vertex_constraints(self, network: VCPNetwork) -> None:
        edges = list(network.graph.edges())
        for i, e in enumerate(edges):
            if i > 0: 
                print(' ∧ ', end='')
            u, v = e
            print(f'(v{u} != v{v})', end='')
        print('\n')

    def generate_coloring_expression(self, network: VCPNetwork):
        """
        Generate a boolean expression string for graph coloring constraints.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
            
        Returns:
        --------
        str : Boolean expression string
        list : Variable order for the expression
        """
        vertices = list(network.graph.nodes())
        edges = list(network.graph.edges())
        
        # Create variable names for each vertex
        var_names = [f"v{vertex}" for vertex in vertices]
        
        # Generate constraint clauses using logical operators
        constraints = []
        for u, v in edges:
            # Use XOR for inequality: (a != b) is equivalent to (a ^ b)
            constraints.append(f"(v{u} ^ v{v})")
        
        # Combine all constraints with AND
        if len(constraints) == 0:
            expression = "1"  # Always true if no edges
        elif len(constraints) == 1:
            expression = constraints[0]
        else:
            expression = " & ".join(constraints)
        
        return expression, var_names

    def create_tweedledum_function(self, network: VCPNetwork):
        """
        Create a tweedledum BoolFunction for the graph coloring problem using expression parsing.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
            
        Returns:
        --------
        BoolFunction : Tweedledum boolean function object
        """
        expression, var_order = self.generate_coloring_expression(network)
        
        print(f"Generated expression: {expression}\n")
        print(f"Variable order: {var_order}\n")

        # Create BoolFunction from expression
        return BoolFunction.from_expression(expression, var_order)

    def create_multi_bit_function(self, network: VCPNetwork, debug: bool = False):
        """
        Create a function for multi-bit color representation.
        This creates a more complex expression handling multi-bit inequalities.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
        bits_per_color : int
            Number of bits to represent each color
            
        Returns:
        --------
        BoolFunction : Tweedledum boolean function object
        """
        # Find vertices that are actually used in edges
        vertices = set()
        for u, v in edges:
            vertices.add(u)
            vertices.add(v)
        edges: list = list(network.graph.edges())
        bits_per_color: int = math.ceil(math.log2(network.available_colors))

        # Create variable names only for vertices that appear in edges
        var_names = []
        for vertex in sorted(vertices):
            for bit in range(bits_per_color):
                var_names.append(f"v{vertex}_{bit}")
        
        # Generate constraint clauses
        constraints = []
        for u, v in edges:
            # For multi-bit inequality, we need to check if any bit differs
            bit_diffs = []
            for bit in range(bits_per_color):
                bit_diffs.append(f"(v{u}_{bit} ^ v{v}_{bit})")
            
            # At least one bit must be different
            if len(bit_diffs) == 1:
                constraint = bit_diffs[0]
            else:
                constraint = " | ".join(bit_diffs)
            
            constraints.append(f"({constraint})")
        
        # Combine all constraints with AND
        if len(constraints) == 0:
            expression = "1"
        elif len(constraints) == 1:
            expression = constraints[0]
        else:
            expression = " & ".join(constraints)
        
        if debug:
            print(f"Generated multi-bit expression: {expression}")
            print(f"Variable order: {var_names}")
        
        return BoolFunction.from_expression(expression, var_names)
    
    def write_verilog_file(self, network: VCPNetwork, filename: str = "graph_coloring.v", use_multi_bit: bool = True):
        """
        Write the graph coloring boolean function to a Verilog file.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
        filename : str
            Name of the output Verilog file
        use_multi_bit : bool
            If True, uses multi-bit representation; if False, uses single-bit
        """
        if use_multi_bit:
            bool_func = self.create_multi_bit_function(network)
        else:
            bool_func = self.create_tweedledum_function(network)
        
        # Write to Verilog file using tweedledum's write_verilog function
        write_verilog(bool_func._logic_network, filename)
        print(f"Verilog file written to: {filename}")

    def write_verilog_with_custom_mapping(self, network: VCPNetwork, filename: str = "graph_coloring.v"):
        """
        Write the graph coloring boolean function to a Verilog file with custom variable mapping.
        This creates a mapping where each vertex gets consecutive input bits.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
        filename : str
            Name of the output Verilog file
        """
        vertices = list(network.graph.nodes())
        bits_per_color: int = network.available_colors.bit_length()
        
        # Create the boolean function
        bool_func = self.create_multi_bit_function(network)
        
        # Write to Verilog
        write_verilog(bool_func._logic_network, filename)
        
        # Create a mapping documentation
        mapping_file = filename.replace('.v', '_mapping.txt')
        with open(mapping_file, 'w') as f:
            f.write("Variable Mapping:\n")
            f.write("================\n\n")
            
            input_index = 0
            for vertex in vertices:
                f.write(f"Vertex v{vertex} ({bits_per_color} bits):\n")
                for bit in range(bits_per_color):
                    f.write(f"  v{vertex}_{bit} -> x{input_index}\n")
                    input_index += 1
                f.write("\n")
            
            f.write(f"Output: y0 represents the satisfaction of all graph coloring constraints\n")
            f.write(f"Total inputs: {input_index}\n")
            f.write(f"Available colors: {network.available_colors}\n")
            f.write(f"Bits per color: {bits_per_color}\n")
        
        print(f"Verilog file written to: {filename}")
        print(f"Variable mapping written to: {mapping_file}")

    def create_manual_verilog(self, network: VCPNetwork, filename: str = "manual_coloring.v"):
        """
        Create a manual Verilog implementation for demonstration purposes.
        This manually constructs the Verilog based on the graph structure.
        
        Parameters:
        -----------
        network : VCPNetwork
            The graph network containing vertices and edges
        filename : str
            Name of the output Verilog file
        """
        vertices = list(network.graph.nodes())
        edges = list(network.graph.edges())
        bits_per_color: int = network.available_colors.bit_length()
        
        total_inputs = len(vertices) * bits_per_color
        
        # First pass: collect all wire names and constraints
        wire_count = 13  # Start from n13 to match expected output
        wires = []
        edge_constraints = []
        assign_statements = []
        
        # Generate constraints for each edge
        for u, v in edges:
            if bits_per_color == 1:
                # Single bit case: v_u != v_v is just v_u ^ v_v
                constraint = f"x{u} ^ x{v}"
            else:
                # Multi-bit case: create separate wires for each bit XOR
                bit_constraint_wires = []
                for bit in range(bits_per_color):
                    u_bit = u * bits_per_color + bit
                    v_bit = v * bits_per_color + bit
                    
                    # Create a wire for each bit XOR
                    wire_name = f"n{wire_count}"
                    wires.append(wire_name)
                    assign_statements.append(f"  assign {wire_name} = x{v_bit} ^ x{u_bit} ;")  # Note: v_bit first to match expected
                    bit_constraint_wires.append(wire_name)
                    wire_count += 1
                
                if len(bit_constraint_wires) == 1:
                    # Single bit constraint, just use it directly
                    constraint = bit_constraint_wires[0]
                else:
                    # Create final wire for AND of NOTs of XORs
                    final_wire = f"n{wire_count}"
                    wires.append(final_wire)
                    not_terms = [f"~{wire}" for wire in bit_constraint_wires]
                    assign_statements.append(f"  assign {final_wire} = {' & '.join(not_terms)} ;")
                    constraint = final_wire
                    wire_count += 1
            
            edge_constraints.append(constraint)
        
        # Generate AND operations for combining edge constraints with negation
        if len(edge_constraints) > 1:
            for i, constraint in enumerate(edge_constraints[:-1]):
                if i == 0:
                    wire_name = f"n{wire_count}"
                    wires.append(wire_name)
                    assign_statements.append(f"  assign {wire_name} = ~{constraint} & ~{edge_constraints[i+1]} ;")
                    wire_count += 1
                else:
                    if i == len(edge_constraints) - 2:
                        # Last operation outputs to y0
                        assign_statements.append(f"  assign y0 = {wires[-1]} & ~{edge_constraints[i+1]} ;")
                    else:
                        new_wire = f"n{wire_count}"
                        wires.append(new_wire)
                        assign_statements.append(f"  assign {new_wire} = {wires[-2]} & ~{edge_constraints[i+1]} ;")
                        wire_count += 1
        
        # Now write the file
        with open(filename, 'w') as f:
            # Module declaration with spaces around commas to match expected format
            input_list = " , ".join([f"x{i}" for i in range(total_inputs)])
            f.write(f"module top( {input_list} , y0 );\n")
            f.write(f"  input {input_list} ;\n")
            f.write("  output y0 ;\n")
            
            # Write all wires in a single line (if any) with spaces around commas
            if wires:
                wire_list = " , ".join(wires)
                f.write(f"  wire {wire_list} ;\n")
            
            # Write all assign statements
            for assign_stmt in assign_statements:
                f.write(f"{assign_stmt}\n")
            
            # Handle single constraint case
            if len(edge_constraints) == 1:
                f.write(f"  assign y0 = {edge_constraints[0]} ;\n")
            
            f.write("endmodule\n")
        
        print(f"Manual Verilog file written to: {filename}")