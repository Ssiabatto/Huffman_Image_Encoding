import graphviz
import os

def save_huffman_tree_graph(huffman_tree, frequencies, filename, code_map):
    total_pixels = sum(frequencies.values())
    graph = print_huffman_tree_graphviz(huffman_tree, total_pixels, code_map)
    graph.render(filename, format='png')
    os.remove(filename)  # Remove the temporary file created by graphviz

def print_huffman_tree_graphviz(node, total_pixels, code_map=None):
    if code_map is None:
        code_map = {}

    def add_nodes_edges(node, graph, parent=None, edge_label=""):
        if node.symbol is not None:
            label = f"symbol={node.symbol}\\ncode={code_map.get(node.symbol, '')}\\nweight={node.weight}\\nprob={node.weight / total_pixels:.6f}"
            graph.node(str(id(node)), label=label)
        else:
            label = f"weight={node.weight}\\nprob={node.weight / total_pixels:.6f}"
            graph.node(str(id(node)), label=label)
            if node.left:
                add_nodes_edges(node.left, graph, node, "0")
            if node.right:
                add_nodes_edges(node.right, graph, node, "1")
        
        if parent:
            graph.edge(str(id(parent)), str(id(node)), label=edge_label)

    graph = graphviz.Digraph(format='png')
    add_nodes_edges(node, graph)
    return graph