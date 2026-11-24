"""Import-safe preparation of Joao Pedro's v4 surface GNN.

The 32-wide, six-layer GINE architecture and optimizer defaults are preserved.
The default command validates/prepares only. --execute is a separate campaign,
not authorized by preparing R1. Scores remain development scores after selection.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import random
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uav_euler2d.execution import (
    SurfacePreprocessor, environment, prepare_experiment, require_constant_flow,
    reserve_output, source_hashes, write_json,
)
from uav_euler2d.graph import EDGE_FEATURE_NAMES, NODE_FEATURE_NAMES, build_surface_graph
from uav_euler2d.loader import Euler2DDataset
from uav_euler2d.validation import integrate_surface

V4_EDGE_FEATURES = ("dx_over_c", "dy_over_c", "length_over_c", "normal_dot", "normal_wedge")


@dataclass(frozen=True)
class NetworkConfig:
    hidden: int = 32
    layers: int = 6
    epochs: int = 1500
    learning_rate: float = 1e-3
    final_rate: float = 1e-5
    weight_decay: float = 0.01
    batch_size: int = 8
    folds: int = 5
    seed: int = 42

    def validate(self):
        if min(self.hidden, self.layers, self.epochs, self.batch_size) < 1 or self.folds < 2:
            raise ValueError("positive architecture/budget and at least two folds required")
        if not all(math.isfinite(x) for x in (self.learning_rate, self.final_rate, self.weight_decay)):
            raise ValueError("non-finite optimizer configuration")
        if not 0 < self.final_rate <= self.learning_rate or self.weight_decay < 0:
            raise ValueError("invalid optimizer configuration")


def RedeGrafos(config: NetworkConfig = NetworkConfig()):
    """Construct the original architecture without fitting; imports are lazy."""
    config.validate()
    import torch
    import torch.nn as nn
    from torch_geometric.nn import GINEConv, global_mean_pool

    def mlp(entra, sai):
        return nn.Sequential(nn.Linear(entra, config.hidden), nn.SiLU(), nn.Linear(config.hidden, sai))

    class SurfaceNetwork(nn.Module):
        def __init__(self):
            super().__init__()
            h = config.hidden
            self.codifica_no = mlp(7, h)
            self.codifica_aresta = mlp(5, h)
            self.vizinhos = nn.ModuleList([GINEConv(mlp(h, h), edge_dim=h) for _ in range(config.layers)])
            self.global_ = nn.ModuleList([mlp(2*h, h) for _ in range(config.layers)])
            self.normas = nn.ModuleList([nn.LayerNorm(h) for _ in range(config.layers)])
            self.decodifica = mlp(h, 1)

        def forward(self, g):
            h, e = self.codifica_no(g.x), self.codifica_aresta(g.edge_attr)
            for viz, glo, norma in zip(self.vizinhos, self.global_, self.normas):
                m = viz(h, g.edge_index, e)
                resumo = global_mean_pool(m, g.batch)[g.batch]
                h = norma(h + glo(torch.cat([m, resumo], dim=1)))
            return self.decodifica(h)

    return SurfaceNetwork()


def graph_to_data(graph, *, require_targets=False):
    arrays = graph.to_arrays(require_targets=require_targets)
    import torch
    from torch_geometric.data import Data
    tensor = lambda value, dtype=torch.float32: torch.tensor(value, dtype=dtype)
    indices = [EDGE_FEATURE_NAMES.index(k) for k in V4_EDGE_FEATURES]
    data = Data(x=tensor(arrays["node_features"]),
                edge_index=tensor(arrays["edge_index"], torch.long),
                edge_attr=tensor(arrays["edge_features"][:, indices]),
                normal=tensor([[n.normal_x, n.normal_y] for n in graph.nodes]),
                ds=tensor([n.segment_length_m for n in graph.nodes]),
                case_id=graph.case_id, geometry_id=graph.geometry_id,
                chord_ref_m=graph.chord_ref_m,
                alpha_deg=graph.graph_inputs["alpha_deg"])
    if arrays["node_targets"] is not None:
        data.y = tensor(arrays["node_targets"])
    for name in ("CL", "CD"):
        if name in graph.graph_targets:
            setattr(data, name, tensor([graph.graph_targets[name]]))
    return data


def normalized_graph(graph, preprocessing: SurfacePreprocessor, *, targets=False):
    import torch
    result = graph.clone()
    result.x = torch.tensor(preprocessing.nodes.transform(graph.x.tolist()), dtype=torch.float32)
    result.edge_attr = torch.tensor(preprocessing.edges.transform(graph.edge_attr.tolist()), dtype=torch.float32)
    if targets:
        result.y_norm = torch.tensor(preprocessing.cp.transform(graph.y.tolist()), dtype=torch.float32)
    return result


def predict_cp(model, preprocessing, graph):
    import torch
    from torch_geometric.loader import DataLoader
    if not hasattr(model, "flow_conditions") or any(
        key not in graph.graph_inputs or not math.isclose(float(graph.graph_inputs[key]), value, abs_tol=1e-9)
        for key, value in model.flow_conditions.items()
    ):
        raise ValueError("flow differs from the geometry-only checkpoint")
    data = normalized_graph(graph_to_data(graph), preprocessing)
    model.eval()
    with torch.no_grad():
        scaled = model(next(iter(DataLoader([data], batch_size=1))))[:, 0]
    return scaled * preprocessing.cp.scale[0] + preprocessing.cp.mean[0]


def load_checkpoint(path):
    import torch
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if payload.get("schema_version") != 1 or payload.get("node_features") != list(NODE_FEATURE_NAMES) or payload.get("edge_features") != list(V4_EDGE_FEATURES):
        raise ValueError("checkpoint schema or feature layout mismatch")
    preprocessing = SurfacePreprocessor.from_dict(payload["preprocessing"])
    model = RedeGrafos(NetworkConfig(**payload["configuration"]))
    model.load_state_dict(payload["state_dict"])
    model.flow_conditions = payload["flow_conditions"]
    return model, preprocessing, payload


def treinar(train, valid, config):
    import numpy as np
    import torch
    from torch_geometric.loader import DataLoader
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    model = RedeGrafos(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs, eta_min=config.final_rate)
    generator = torch.Generator().manual_seed(config.seed)
    batches = DataLoader(train, batch_size=config.batch_size, shuffle=True, generator=generator)
    validation = next(iter(DataLoader(valid, batch_size=len(valid))))
    best, best_state, best_epoch = float("inf"), None, None
    loss_fn = torch.nn.MSELoss()
    for epoch in range(1, config.epochs+1):
        model.train()
        for batch in batches:
            optimizer.zero_grad()
            loss = loss_fn(model(batch), batch.y_norm)
            if not torch.isfinite(loss):
                raise ValueError("non-finite training loss")
            loss.backward()
            optimizer.step()
        scheduler.step()
        model.eval()
        with torch.no_grad():
            loss_val = loss_fn(model(validation), validation.y_norm).item()
        if math.isfinite(loss_val) and loss_val < best:
            best, best_state, best_epoch = loss_val, {k:v.clone() for k,v in model.state_dict().items()}, epoch
    if best_state is None:
        raise ValueError("no finite validation checkpoint")
    model.load_state_dict(best_state)
    return model, best_epoch


def metricas(cl, cl_real, cd, cd_real, erro_cp=None):
    def score(predicted, actual):
        if len(predicted) != len(actual) or not len(actual):
            raise ValueError("metric arrays need equal non-zero lengths")
        rmse = math.sqrt(sum((float(p)-float(y))**2 for p,y in zip(predicted,actual))/len(actual))
        scale = abs(sum(map(float, actual))/len(actual))
        return rmse, 100*rmse/scale if scale > 1e-12 else None
    a, ap = score(cl, cl_real)
    b, bp = score(cd, cd_real)
    return {"Cp": erro_cp, "CL": a, "CL_percent_of_mean": ap, "CD": b, "CD_percent_of_mean": bp}


def avaliar_rede(model, graphs, preprocessing):
    import torch
    from torch_geometric.loader import DataLoader
    cp_errors, cl, cd, real_cl, real_cd = [], [], [], [], []
    model.eval()
    with torch.no_grad():
        for g in graphs:
            cp = (model(next(iter(DataLoader([g], batch_size=1))))[:,0] * preprocessing.cp.scale[0] + preprocessing.cp.mean[0])
            cp_errors.append(torch.sqrt(((cp-g.y[:,0])**2).mean()).item())
            rows = [{"Cp":p, "normal_x":n[0], "normal_y":n[1], "segment_length_m":ds}
                    for p,n,ds in zip(cp.tolist(),g.normal.tolist(),g.ds.tolist())]
            a,b = integrate_surface(rows, float(g.alpha_deg), float(g.chord_ref_m))
            cl.append(a); cd.append(b)
            real_cl.append(g.CL.item()); real_cd.append(g.CD.item())
    return metricas(cl, real_cl, cd, real_cd, sum(cp_errors)/len(cp_errors))


def avaliar_kriging(train, valid, seed):
    import numpy as np
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
    lo, hi = np.array([0.,.2,.08]), np.array([.04,.6,.16])
    x = lambda rows: (np.array([[float(r[k]) for k in ("m","p","t")] for r in rows])-lo)/(hi-lo)
    predicted = {}
    for name in ("CL", "CD"):
        gp = GaussianProcessRegressor(ConstantKernel(1.)*RBF([.5,.5,.5])+WhiteKernel(1e-3),
                                      normalize_y=True, n_restarts_optimizer=10, random_state=seed)
        predicted[name] = gp.fit(x(train), [float(r[name]) for r in train]).predict(x(valid))
    return metricas(predicted["CL"], [float(r["CL"]) for r in valid], predicted["CD"], [float(r["CD"]) for r in valid])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--execute", action="store_true", help="run a separately authorized development campaign")
    parser.add_argument("--output", type=Path, help="new private output directory; required for --execute")
    parser.add_argument("--epochs", type=int, default=1500)
    args = parser.parse_args(argv)
    training_started = False
    try:
        config = NetworkConfig(epochs=args.epochs)
        config.validate()
        if args.execute and args.output is None:
            raise ValueError("--execute requires --output")
        dataset = Euler2DDataset(args.dataset_root)
        summary = prepare_experiment(dataset)
        rows = list(dataset.cases_for_split("train", ("success",))) + list(dataset.cases_for_split("val", ("success",)))
        summary["flow_conditions"] = require_constant_flow(rows)
        graphs = {r["case_id"]: build_surface_graph(dataset, r["case_id"]) for r in rows}
        for graph in graphs.values():
            graph.to_arrays(require_targets=True)
        summary["graph_diagnostics"] = {case_id: graph.validation for case_id, graph in graphs.items()}
        summary["configuration"] = asdict(config)
        if not args.execute:
            print(json.dumps(summary, indent=2, allow_nan=False))
            return 0
        import numpy as np
        import torch
        import sklearn  # fail before allocating output if the comparator is unavailable
        from torch_geometric.data import Data
        from torch_geometric.loader import DataLoader
        geos = sorted({r["geometry_id"] for r in rows})
        if len(geos) < config.folds:
            raise ValueError("fewer training/validation geometries than development folds")
        order = np.random.default_rng(config.seed).permutation(len(geos))
        folds = [[geos[i] for i in order[k::config.folds]] for k in range(config.folds)]
        data = {k:graph_to_data(g, require_targets=True) for k,g in graphs.items()}
        hashes = source_hashes(dataset)
        output = reserve_output(args.output, dataset.root)
        write_json(output/"preparation.json", {**summary, "source_hashes":hashes, "environment":environment()})
        torch.use_deterministic_algorithms(True)
        torch.set_num_threads(1)
        scores = []
        for i, part in enumerate(folds,1):
            tr = [r for r in rows if r["geometry_id"] not in part]
            va = [r for r in rows if r["geometry_id"] in part]
            preprocessing = SurfacePreprocessor.fit([data[r["case_id"]] for r in tr])
            norm = lambda group: [normalized_graph(data[r["case_id"]], preprocessing, targets=True) for r in group]
            train, valid = norm(tr), norm(va)
            training_started = True
            model, epoch = treinar(train, valid, config)
            model.flow_conditions = summary["flow_conditions"]
            scores.append({"fold":i, "evaluation":"development_selected_checkpoint",
                           "gnn":avaliar_rede(model, valid, preprocessing),
                           "gpr":avaliar_kriging(tr, va, config.seed),
                           "train_case_ids":[r["case_id"] for r in tr], "validation_case_ids":[r["case_id"] for r in va]})
            with (output/f"fold-{i}.pt").open("xb") as stream:
                torch.save({"schema_version":1, "state_dict":model.state_dict(),
                            "configuration":asdict(config), "preprocessing":preprocessing.to_dict(),
                            "node_features":list(NODE_FEATURE_NAMES), "edge_features":list(V4_EDGE_FEATURES),
                            "best_epoch":epoch, "source_hashes":hashes, "environment":environment(),
                            "flow_conditions":summary["flow_conditions"],
                            "train_case_ids":scores[-1]["train_case_ids"], "validation_case_ids":scores[-1]["validation_case_ids"]}, stream)
        write_json(output/"development-results.json", {"training_executed":True, "folds":scores,
                    "interpretation":"descriptive development scores, not an equivalence test or independent test estimate"})
        print(json.dumps({"status":"completed", "training_executed":True, "output":str(output)}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError) as exc:
        print(json.dumps({"status":"blocked", "training_executed":training_started, "reason":str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
