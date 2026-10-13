"""Optional, small surface GNN for feasibility assessment."""

from __future__ import annotations

from typing import Any


def availability() -> dict[str, Any]:
    try:
        import torch  # noqa: F401
    except ImportError:
        return {
            "available": False,
            "training_executed": False,
            "reason": "PyTorch is not installed; availability was checked only.",
        }
    return {
        "available": True,
        "training_executed": False,
        "reason": "PyTorch available; S3 performs an availability check only.",
    }


def train_surface_gnn(*args, **kwargs):
    """Train a graph-level message-passing model when PyTorch is installed."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("optional GNN requires PyTorch; install it outside the minimal CI path") from exc

    graphs = kwargs["graphs"]
    targets = torch.tensor(kwargs["targets"], dtype=torch.float32)
    seed = int(kwargs.get("seed", 202604))
    epochs = int(kwargs.get("epochs", 100))
    hidden = int(kwargs.get("hidden", 16))
    torch.manual_seed(seed)

    class SurfaceGNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.self_layer = nn.Linear(5, hidden)
            self.neighbor_layer = nn.Linear(5, hidden)
            self.head = nn.Linear(hidden, targets.shape[1])

        def forward(self, graph):
            x = torch.tensor([[n.x_m, n.y_m, n.normal_x, n.normal_y, n.segment_length_m] for n in graph.nodes], dtype=torch.float32)
            neighbors = torch.zeros_like(x)
            counts = torch.zeros((len(graph.nodes), 1), dtype=torch.float32)
            index = {node.node_id: i for i, node in enumerate(graph.nodes)}
            for edge in graph.contour_edges:
                i, j = index[edge.source], index[edge.target]
                neighbors[i] += x[j]
                neighbors[j] += x[i]
                counts[i] += 1
                counts[j] += 1
            neighbors = neighbors / counts.clamp_min(1.0)
            h = torch.relu(self.self_layer(x) + self.neighbor_layer(neighbors))
            return self.head(h.mean(dim=0))

    model = SurfaceGNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=float(kwargs.get("learning_rate", 1e-2)))
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        predictions = torch.stack([model(graph) for graph in graphs])
        loss = ((predictions - targets) ** 2).mean()
        loss.backward()
        optimizer.step()
    return model
