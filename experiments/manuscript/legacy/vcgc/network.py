# This module is to create and visualize NetworkX graphs

import networkx as nx
from matplotlib import pyplot as plt
from .dimacs import *
import random
from typing import Optional
from networkx import bfs_tree

class VCPNetwork:

    def __init__(self, file_path: str = None):
        self.edges = []
        self.colored_vertices = {}
        self.num_vertices = 0
        self.num_edges = 0
        self.available_colors = 0
        self.graph = nx.Graph()  # Declare a graph object
        self.color_map = []
        if file_path:
            self.read_dimacs(file_path=file_path) 
    
    def read_dimacs(self, file_path: str) -> None:
        self.num_vertices, self.num_edges, self.available_colors, self.edges, self.colored_vertices = read_dimacs(file_path=file_path)
        self.create_colored_graph(self.num_vertices, self.edges, self.colored_vertices, self.available_colors)

    def create_colored_graph(self, num_vertices: int, edges: list, colored_nodes: dict, num_colors: int,
                              color_map: list = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'yellow']) -> nx.Graph:
        """
        Generate a graph with colored nodes.
        
        Parameters:
        -----------
        num_vertices : int
            Number of vertices in the graph
        edges : list of tuples
            List of edges as (source, target) tuples
        colored_nodes : dict
            Dictionary mapping node IDs (as strings) to color indices (as strings)
        num_colors : int
            Number of available colors
            
        Returns:
        --------
        graph : networkx.Graph
                The generated graph with color attributes embedded in nodes
        """
        
        # Ensure we have enough colors
        if num_colors > len(color_map):
            color_map = color_map * (num_colors // len(color_map) + 1)
        color_map = color_map[:num_colors]
        
        # Create vertices with color attributes
        for v in range(1,num_vertices+1):
            # Check if this node has a color assigned
            if str(v) in colored_nodes:
                color_idx = int(colored_nodes[str(v)])
                if 0 <= color_idx < num_colors:
                    # Add node with color attribute directly
                    self.graph.add_node(v, color=color_map[color_idx], color_idx=color_idx)
                else:
                    self.graph.add_node(v, color='lightgray', color_idx=-1)
            else:
                self.graph.add_node(v, color='lightgray', color_idx=-1)
        
        # Add edges
        for e in edges:
            self.graph.add_edge(*e)
        
        return self.graph
    
    def draw_graph(self, pos: Optional[dict] = None, name: Optional[str] = None, figsize: tuple =(5, 5), node_size: int = 2000) -> None:
        """
        Draw a graph with nodes colored according to their color attribute.
        Node labels will display both node number and color index in bra-ket notation.
        
        Parameters:
        -----------
        self : networkx.Graph
            The graph to draw (should have 'color' attributes on nodes)
        pos : dict, optional
            A dictionary with nodes as keys and positions as values (if None, uses spring layout)
        name : str, optional
            Name of the file to save the graph image (default is "graph.png")
        figsize : tuple, optional
            Figure size as (width, height) in inches
        node_size : int, optional
            Size of the nodes in the visualization
        """
        draw_colored_graph(self.graph,name=name or "graph.png", pos=pos, figsize=figsize, node_size=node_size)
    
    def bfs_traversal(self, root: int = 0) -> nx.Graph:
        """
        Generate a BFS tree from the graph starting at the specified root node.
        
        Parameters:
        -----------
        root : int
            The root node to start the BFS traversal
        
        Returns:
        --------
        bfs_tree : networkx.Graph
            The BFS tree generated from the graph
        """
        bfs_traversal = bfs_tree(self.graph, source=root)
        
        # Copy node attributes from the original graph to the BFS tree
        for node in bfs_traversal.nodes():
            if node in self.graph.nodes():
                bfs_traversal.nodes[node].update(self.graph.nodes[node])
        
        return bfs_traversal
    
    def draw_bfs_tree(self, root: int = 0, figsize: tuple = (5, 5), node_size: int = 2000) -> None:
        """
        Draw the BFS tree starting from the specified root node.
        
        Parameters:
        -----------
        root : int
            The root node to start the BFS traversal
        figsize : tuple, optional
            Figure size as (width, height) in inches
        node_size : int, optional
            Size of the nodes in the visualization
        """
        bfs_tree = self.bfs_traversal(root)
        pos = hierarchy_pos(bfs_tree, root=0, width=1.0, vert_gap=0.2, leaf_vs_root_factor=0.5)
        draw_colored_graph(bfs_tree, name = "bfs_tree.png", pos=pos, figsize=figsize, node_size=node_size)

def hierarchy_pos(G: nx.Graph, root: Optional[int] = None, width: float = 1., vert_gap :float = 0.2, vert_loc : int = 0, leaf_vs_root_factor : float = 0.5):

    '''
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    Based on Joel's answer at https://stackoverflow.com/a/29597209/2966723,
    but with some modifications.  

    We include this because it may be useful for plotting transmission trees,
    and there is currently no networkx equivalent (though it may be coming soon).
    
    There are two basic approaches we think of to allocate the horizontal 
    location of a node.  
    
    - Top down: we allocate horizontal space to a node.  Then its ``k`` 
      descendants split up that horizontal space equally.  This tends to result
      in overlapping nodes when some have many descendants.
    - Bottom up: we allocate horizontal space to each leaf node.  A node at a 
      higher level gets the entire space allocated to its descendant leaves.
      Based on this, leaf nodes at higher levels get the same space as leaf
      nodes very deep in the tree.  
      
    We use use both of these approaches simultaneously with ``leaf_vs_root_factor`` 
    determining how much of the horizontal space is based on the bottom up 
    or top down approaches.  ``0`` gives pure bottom up, while 1 gives pure top
    down.   
    
    
    :Arguments: 
    
    **G** the graph (must be a tree)

    **root** the root node of the tree 
    - if the tree is directed and this is not given, the root will be found and used
    - if the tree is directed and this is given, then the positions will be 
      just for the descendants of this node.
    - if the tree is undirected and not given, then a random choice will be used.

    **width** horizontal space allocated for this branch - avoids overlap with other branches

    **vert_gap** gap between levels of hierarchy

    **vert_loc** vertical location of root

    **leaf_vs_root_factor**

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, leftmost, width, leafdx = 0.2, vert_gap = 0.2, vert_loc = 0, 
                    xcenter = 0.5, rootpos = None, 
                    leafpos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if rootpos is None:
            rootpos = {root:(xcenter,vert_loc)}
        else:
            rootpos[root] = (xcenter, vert_loc)
        if leafpos is None:
            leafpos = {}
        children = list(G.neighbors(root))
        leaf_count = 0
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            rootdx = width/len(children)
            nextx = xcenter - width/2 - rootdx/2
            for child in children:
                nextx += rootdx
                rootpos, leafpos, newleaves = _hierarchy_pos(G,child, leftmost+leaf_count*leafdx, 
                                    width=rootdx, leafdx=leafdx,
                                    vert_gap = vert_gap, vert_loc = vert_loc-vert_gap, 
                                    xcenter=nextx, rootpos=rootpos, leafpos=leafpos, parent = root)
                leaf_count += newleaves

            leftmostchild = min((x for x,y in [leafpos[child] for child in children]))
            rightmostchild = max((x for x,y in [leafpos[child] for child in children]))
            leafpos[root] = ((leftmostchild+rightmostchild)/2, vert_loc)
        else:
            leaf_count = 1
            leafpos[root]  = (leftmost, vert_loc)
        return rootpos, leafpos, leaf_count

    xcenter = width/2.
    if isinstance(G, nx.DiGraph):
        leafcount = len([node for node in nx.descendants(G, root) if G.out_degree(node)==0])
    elif isinstance(G, nx.Graph):
        leafcount = len([node for node in nx.node_connected_component(G, root) if G.degree(node)==1 and node != root])
    rootpos, leafpos, leaf_count = _hierarchy_pos(G, root, 0, width, 
                                                    leafdx=width*1./leafcount, 
                                                    vert_gap=vert_gap, 
                                                    vert_loc = vert_loc, 
                                                    xcenter = xcenter)
    pos = {}
    for node in rootpos:
        pos[node] = (leaf_vs_root_factor*leafpos[node][0] + (1-leaf_vs_root_factor)*rootpos[node][0], leafpos[node][1]) 
    xmax = max(x for x,y in pos.values())
    for node in pos:
        pos[node]= (pos[node][0]*width/xmax, pos[node][1])
    return pos

def draw_colored_graph(G: nx.Graph, name: str = "graph.png", pos: Optional[dict] = None, figsize: tuple =(5, 5), node_size: int = 2000) -> None:
    """
    Draw a graph with nodes colored according to their color attribute.
    Node labels will display both node number and color index in bra-ket notation.
    
    Parameters:
    -----------
    G : networkx.Graph
        The graph to draw (should have 'color' attributes on nodes)
    pos : dict, optional
        A dictionary with nodes as keys and positions as values (if None, uses spring layout)
    name : str, optional
        Name of the file to save the graph image (default is "graph.png")
    figsize : tuple, optional
        Figure size as (width, height) in inches
    node_size : int, optional
        Size of the nodes in the visualization
    """
    # Extract node colors for drawing, with fallback for missing color attribute
    node_colors = [G.nodes[node].get('color', 'lightgray') for node in G.nodes()]
    
    # Create custom labels in the format "node:|color⟩"
    custom_labels = {}
    for node in G.nodes():
        # Get the color index, default to 'x' if not found or -1
        color_idx = G.nodes[node].get('color_idx', -1)
        if color_idx == -1:
            label = f"{node}"
        else:
            label = f"{node}:|{color_idx}⟩"
        custom_labels[node] = label
    
    # Draw the graph with node colors and custom labels
    plt.figure(figsize=figsize)
    nx.draw(G, pos = pos, labels=custom_labels, node_color=node_colors, node_size=node_size)
    plt.savefig(name, dpi=500, bbox_inches='tight')