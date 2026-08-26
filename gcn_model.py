"""Shared graph-neural-network helpers for netx_nn.

Both entry points (``netxnn.py`` and ``ptg.py``) turn code into a graph and run a
small Graph Convolutional Network to produce per-node embeddings. The shared
pieces live here so the two entry points stay in sync.
"""
from __future__ import annotations

import torch
import torch.optim
import torch.nn.functional as F
import torch_geometric.utils
import torch_geometric.nn

# Default model / training hyper-parameters.
HIDDEN_DIM = 16
OUTPUT_DIM = 8
EPOCHS = 100
LR = 0.01
WEIGHT_DECAY = 5e-4
# A fixed seed keeps the placeholder training target reproducible across runs.
SEED = 0


class GCN(torch.nn.Module):
    """A two-layer GCN: conv -> ReLU -> conv."""

    def __init__(self, input_dim, hidden_dim=HIDDEN_DIM, output_dim=OUTPUT_DIM):
        super().__init__()
        self.conv1 = torch_geometric.nn.GCNConv(input_dim, hidden_dim)
        self.conv2 = torch_geometric.nn.GCNConv(hidden_dim, output_dim)
        self.output_dim = output_dim

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = self.conv2(x, edge_index)
        return x


def _node_label(node_data, type_attr, default_type):
    """Pick the label string for a node, tolerating different attribute names.

    ``netxnn`` stores the syntax type under ``type``; graphs loaded from
    graphml store it under ``label``.
    """
    if type_attr in node_data:
        return str(node_data[type_attr])
    if "label" in node_data:
        return str(node_data["label"])
    return default_type


def build_node_features(graph, type_attr="type", default_type="unknown"):
    """Attach a fixed-size one-hot feature vector to *every* node.

    The feature is a one-hot over the distinct node-type labels present in the
    graph. A 1-D tensor is attached to each node under the key ``x`` so that
    ``torch_geometric.utils.from_networkx`` can assemble a ``data.x`` that is
    guaranteed to be aligned with ``edge_index`` (same node index mapping).

    Returns the number of feature dimensions (the one-hot size).
    """
    # First pass: assign a stable index to each distinct label.
    label_to_idx = {}
    for data in graph.nodes(data=True):
        label = _node_label(data, type_attr, default_type)
        if label not in label_to_idx:
            label_to_idx[label] = len(label_to_idx)

    num_features = len(label_to_idx)

    # Second pass: attach a 1-D one-hot tensor to every node.
    for data in graph.nodes(data=True):
        label = _node_label(data, type_attr, default_type)
        vec = torch.zeros(num_features, dtype=torch.float32)
        vec[label_to_idx[label]] = 1.0
        data["x"] = vec

    return num_features


def graph_to_data(graph):
    """Convert a networkx graph to a PyG ``Data`` object.

    ``from_networkx`` can trip over non-tensor node attributes (strings, etc.),
    so we feed it a clean copy that carries only the per-node ``x`` tensor. This
    also guarantees ``data.x`` lines up with ``edge_index``.
    """
    import networkx as nx

    clean = nx.DiGraph()
    clean.add_nodes_from(list(graph.nodes()))
    clean.add_edges_from(graph.edges())
    for node, data in graph.nodes(data=True):
        x = data.get("x")
        if isinstance(x, torch.Tensor):
            clean.nodes[node]["x"] = x

    return torch_geometric.utils.from_networkx(clean)


def make_placeholder_target(data, output_dim):
    """Build a *deterministic* placeholder target for the smoke-test loss.

    There is no ground-truth label set yet, so training uses a reproducible
    pseudo-target instead of a fresh random one on every run. Replace this with a
    real target (labels, a reconstruction target, etc.) for meaningful training.
    """
    torch.manual_seed(SEED)
    return torch.randn(data.num_nodes, output_dim)


def train_gnn(model, data, target=None, epochs=EPOCHS, lr=LR,
              weight_decay=WEIGHT_DECAY, verbose=True, print_every=25):
    """Train the model for ``epochs`` and return it.

    If ``target`` is ``None``, a reproducible placeholder target is generated so
    the forward/backward path is exercised deterministically.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    if target is None:
        target = make_placeholder_target(data, model.output_dim)

    model.train()
    last_loss = 0.0
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(data)
        loss = F.mse_loss(out, target)
        loss.backward()
        optimizer.step()
        last_loss = loss.item()
        if verbose and (epoch == 0 or (epoch + 1) % print_every == 0):
            print(f"Epoch {epoch + 1:>3}/{epochs}, Loss: {last_loss:.6f}")
    return model


def gen_embeddings(model, data):
    """Run a forward pass and return the detached node-embedding tensor."""
    model.eval()
    with torch.no_grad():
        return model(data)
