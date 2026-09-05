"""Load pre-built graph(s) -> GCN -> node embeddings.

This variant skips parsing: it reads NetworkX graphs serialized as .graphml
(files that ``pycmp`` could produce) and runs a GCN on each.

Usage:
    python ptg.py <graph.graphml> [more.graphml ...]
"""
import sys

import networkx

from gcn_model import GCN, build_node_features, gen_embeddings, graph_to_data, train_gnn


def main(graphs: list):
    for graph in graphs:
         # Graphs loaded from graphml store the node type under the 'label' key.
        num_features = build_node_features(graph, type_attr="label")
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
    graphs = [networkx.read_graphml(arg) for arg in sys.argv[1:]]
    main(graphs)
