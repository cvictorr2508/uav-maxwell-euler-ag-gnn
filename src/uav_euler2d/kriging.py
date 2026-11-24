"""Prepare the legacy CL/GPR experiment; fitting requires explicit --execute.

R1 preserves the RBF/WhiteKernel model. Protocol/kernel comparisons belong to R2/R3.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uav_euler2d.execution import (
    environment, prepare_experiment, require_constant_flow, reserve_output,
    source_hashes, validate_flow_conditions, write_json,
)
from uav_euler2d.loader import Euler2DDataset

LOWER = (0.0, 0.20, 0.08)
UPPER = (0.04, 0.60, 0.16)


def normalized_inputs(rows, lower=LOWER, upper=UPPER):
    result = []
    for row in rows:
        values = [float(row[k]) for k in ("m", "p", "t")]
        if not all(math.isfinite(v) for v in values):
            raise ValueError("non-finite GPR input")
        result.append([(v-lo)/(hi-lo) for v,lo,hi in zip(values,lower,upper)])
    return result


def predict_cl(artifact, rows):
    if artifact.get("schema_version") != 1 or artifact.get("features") != ["m", "p", "t"]:
        raise ValueError("unsupported GPR artifact layout")
    if require_constant_flow(rows) != validate_flow_conditions(artifact["flow_conditions"]):
        raise ValueError("flow differs from the geometry-only model")
    return artifact["model"].predict(
        normalized_inputs(rows, artifact["lower"], artifact["upper"]), return_std=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--execute", action="store_true", help="fit the model; requires a separately authorized campaign")
    parser.add_argument("--output", type=Path, help="new private output directory, required with --execute")
    args = parser.parse_args(argv)
    training_started = False
    try:
        if args.execute and args.output is None:
            raise ValueError("--execute requires --output")
        dataset = Euler2DDataset(args.dataset_root)
        summary = prepare_experiment(dataset)
        train = list(dataset.cases_for_split("train", ("success",)))
        valid = list(dataset.cases_for_split("val", ("success",)))
        summary["flow_conditions"] = require_constant_flow(train + valid)
        if not args.execute:
            print(json.dumps(summary, indent=2, allow_nan=False))
            return 0
        import numpy as np
        import joblib
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
        x_train, x_valid = normalized_inputs(train), normalized_inputs(valid)
        y_train = np.array([float(r["CL"]) for r in train])
        y_valid = np.array([float(r["CL"]) for r in valid])
        hashes = source_hashes(dataset)
        output = reserve_output(args.output, dataset.root)
        write_json(output / "preparation.json", {**summary, "source_hashes": hashes, "environment": environment()})
        model = GaussianProcessRegressor(
            kernel=ConstantKernel(1.0) * RBF([0.5, 0.5, 0.5]) + WhiteKernel(1e-3),
            normalize_y=True, n_restarts_optimizer=10, random_state=42)
        training_started = True
        model.fit(x_train, y_train)
        prediction, std = model.predict(x_valid, return_std=True)
        artifact = {"schema_version": 1, "model": model, "features": ["m", "p", "t"],
                    "lower": LOWER, "upper": UPPER, "target": "CL",
                    "flow_conditions": summary["flow_conditions"], "source_hashes": hashes}
        joblib.dump(artifact, output / "gpr-cl.joblib")
        write_json(output / "validation.json", {
            "training_executed": True, "evaluation": "development_only",
            "rmse_CL": float(np.sqrt(np.mean((prediction-y_valid)**2))),
            "case_ids": [r["case_id"] for r in valid],
            "predicted_CL": prediction.tolist(), "reference_CL": y_valid.tolist(),
            "predictive_std_CL": std.tolist(), "kernel": str(model.kernel_),
            "uncertainty": "model-conditioned observation standard deviation; not CFD error"})
        print(json.dumps({"status": "completed", "output": str(output), "training_executed": True}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError) as exc:
        print(json.dumps({"status": "blocked", "training_executed": training_started, "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
