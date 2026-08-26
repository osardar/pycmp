"""Parse Python source -> graph -> GCN -> node embeddings.

Usage:
    python netxnn.py <python-file>
"""
import sys

import networkx
import tree_sitter_python
from tree_sitter import Language, Parser

from gcn_model import GCN, build_node_features, gen_embeddings, graph_to_data, train_gnn


def ts_init():
    """Build a tree-sitter parser for Python."""
    language = Language(tree_sitter_python.language())
    return Parser(language)


def convert_ts_nx(root_node):
    """Convert a tree-sitter root node into a networkx DiGraph.

    Each syntax-tree node becomes a graph node (id = memory address), labeled by
    its syntax ``type`` and source ``text``; parent -> child relations become
    directed edges.
    """
    graph = networkx.DiGraph()

    def traverse(node, parent_id=None):
        node_id = id(node)
        text = node.text.decode("utf-8").strip() if node.text is not None else ""
        graph.add_node(node_id, type=node.type, text=text)
        if parent_id is not None:
            graph.add_edge(parent_id, node_id)
        for child in node.children:
            traverse(child, node_id)

    traverse(root_node)
    return graph


def main(pyfile_bytes: bytes):
    parser = ts_init()
    tree = parser.parse(pyfile_bytes)
    graph = convert_ts_nx(tree.root_node)

    num_features = build_node_features(graph, type_attr="type")
    data = graph_to_data(graph)

    print(f"graph: {graph.number_of_nodes()} nodes, "
          f"{graph.number_of_edges()} edges, {num_features} feature dims")
    print(f"x shape: {tuple(data.x.shape)}")

    model = GCN(input_dim=num_features, hidden_dim=16, output_dim=8)
    print(model)
    train_gnn(model, data)
    embeddings = gen_embeddings(model, data)
    print("Node Embeddings:")
    print(embeddings)


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fd:
        pyfile = fd.read()
    main(pyfile)
