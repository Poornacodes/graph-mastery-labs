"""Listing 10.3 — A GCN for node classification (PyTorch Geometric).

Optional and heavy: pip install -r requirements-gnn.txt (see PyG's install
notes if that fails). Downloads the Cora citation dataset (~a few MB)."""
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.datasets import Planetoid

data = Planetoid(root='/tmp/Cora', name='Cora')[0]

class GCN(torch.nn.Module):
    def __init__(self, in_dim, hidden, out_dim):
        super().__init__()
        self.c1 = GCNConv(in_dim, hidden)
        self.c2 = GCNConv(hidden, out_dim)
    def forward(self, x, edge_index):
        x = F.relu(self.c1(x, edge_index))
        x = F.dropout(x, training=self.training)
        return self.c2(x, edge_index)

model = GCN(data.num_features, 16, int(data.y.max()) + 1)
opt = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

for _ in range(100):
    model.train()
    opt.zero_grad()
    out = model(data.x, data.edge_index)
    F.nll_loss(F.log_softmax(out, 1)[data.train_mask],
               data.y[data.train_mask]).backward()
    opt.step()

model.eval()
pred = model(data.x, data.edge_index).argmax(1)
acc = (pred[data.test_mask] == data.y[data.test_mask]).float().mean().item()
print(f"Test accuracy: {acc:.3f}")   # ~0.80 on Cora
