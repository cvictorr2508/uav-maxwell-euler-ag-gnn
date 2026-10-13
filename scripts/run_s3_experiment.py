"""Run the leakage-safe S3 baselines and graph continuity protocol."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uav_euler2d.experiment import FeatureSpec, MeanPredictor, RidgePredictor, evaluate_predictor, report_dict
from uav_euler2d.geometry import check_contour_continuity
from uav_euler2d.graph import build_surface_graph
from uav_euler2d.gnn import availability
from uav_euler2d.loader import Euler2DDataset
from uav_euler2d.validation import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=202604)
    parser.add_argument("--run-gnn", action="store_true", help="run the optional PyTorch model when installed")
    args = parser.parse_args()
    started = time.perf_counter()
    dataset = Euler2DDataset(args.dataset_root)
    spec = FeatureSpec()
    spec.validate()
    validation = validate_dataset(dataset)
    continuity = {}
    for row in dataset.cases_for_split("test", ("success",)):
        graph = build_surface_graph(dataset, row["case_id"])
        report = check_contour_continuity(graph)
        continuity[row["case_id"]] = {
            "passed": report.passed,
            "edge_count": report.edge_count,
            "max_center_gap_m": report.max_center_gap_m,
            "median_segment_length_m": report.median_segment_length_m,
            "max_gap_to_segment_ratio": report.max_gap_to_segment_ratio,
            "signed_center_area_m2": report.signed_center_area_m2,
            "orientation_semantics": report.orientation_semantics,
            "warnings": list(report.warnings),
        }
    result = {
        "protocol": {
            "seed": args.seed,
            "unit_of_observation": "case; surface nodes are never independent observations",
            "features": list(spec.names),
            "targets": list(spec.targets),
            "forbidden_inputs": sorted(__import__("uav_euler2d.experiment", fromlist=["FORBIDDEN_INPUTS"]).FORBIDDEN_INPUTS),
            "partitions": {name: len(dataset.cases_for_split(name, ("success",))) for name in ("train", "val", "test")},
            "test_case_c0015_preserved": any(row["case_id"] == "c0015" for row in dataset.cases_for_split("test", ("success",))),
        },
        "dataset_validation": {"passed": validation.passed, "errors": validation.errors, "warnings": validation.warnings, "metrics": validation.metrics},
        "geometry_continuity": continuity,
        "baselines": {
            "train_mean": [report_dict(report) for report in evaluate_predictor(dataset, MeanPredictor(), spec)],
            "ridge_geometry": [report_dict(report) for report in evaluate_predictor(dataset, RidgePredictor(alpha=1.0), spec)],
        },
        "gnn": {"status": "requested" if args.run_gnn else "not_requested", **availability()},
        "elapsed_s": time.perf_counter() - started,
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)


if __name__ == "__main__":
    main()
