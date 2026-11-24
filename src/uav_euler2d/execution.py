"""Shared read-only preparation, preprocessing and artifact contracts.

This module uses only the standard library and never fits a model.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
from typing import Sequence

from .loader import Euler2DDataset
from .validation import ValidationReport, validate_dataset


class DatasetValidationError(ValueError):
    """No model or predictive metric may run after this failure."""


def require_valid_dataset(dataset: Euler2DDataset) -> ValidationReport:
    try:
        report = validate_dataset(dataset)
    except (ArithmeticError, ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        raise DatasetValidationError(f"dataset validation could not complete: {exc}") from exc
    if not report.passed:
        raise DatasetValidationError("dataset validation failed: " + "; ".join(report.errors))
    return report


def prepare_experiment(dataset: Euler2DDataset) -> dict:
    """Preserve the frozen manifest and the canonical success-only policy."""
    report = require_valid_dataset(dataset)
    splits = {s: list(dataset.cases_for_split(s, ("success",))) for s in ("train", "val", "test")}
    if not splits["train"] or not splits["val"]:
        raise DatasetValidationError("training and validation need converged cases")
    return {"status": "prepared", "training_executed": False,
            "status_policy": "success_only; non_converged excluded from predictive fitting",
            "case_ids": {s: [r["case_id"] for r in rows] for s, rows in splits.items()},
            "counts": {s: len(rows) for s, rows in splits.items()},
            "warnings": list(report.warnings), "evaluation": "development_only"}


def require_constant_flow(rows: Sequence[dict]) -> dict[str, float]:
    """Legacy geometry-only models are restricted to one verified flow setting."""
    result = {}
    for name in ("mach_inf", "alpha_deg"):
        values = {float(row[name]) for row in rows}
        if len(values) != 1 or not all(math.isfinite(v) for v in values):
            raise ValueError(f"geometry-only model requires one finite {name}; conditioning is not implemented")
        result[name] = next(iter(values))
    if result["mach_inf"] < 0:
        raise ValueError("mach_inf must be non-negative")
    return result


def source_hashes(dataset: Euler2DDataset) -> dict[str, str]:
    paths = [dataset.root / p for p in ("cases.csv", "dataset_manifest.json", "split_manifest.json", "meshes/mesh_metadata.json")]
    paths.extend(dataset.surface_path(r["case_id"]) for r in dataset.cases if r["status"] != "failed")
    return {p.relative_to(dataset.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def environment() -> dict:
    versions = {}
    for name in ("numpy", "pyarrow", "torch", "torch-geometric", "scikit-learn"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"python": platform.python_version(), "platform": platform.platform(), "packages": versions}


def reserve_output(path: Path, dataset_root: Path) -> Path:
    path, dataset_root = path.resolve(), dataset_root.resolve()
    if path == dataset_root or path.is_relative_to(dataset_root):
        raise ValueError("outputs must stay outside the original dataset")
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


@dataclass(frozen=True)
class Standardizer:
    """Sample statistics fitted on training rows only, with a constant fallback."""
    mean: tuple[float, ...]
    scale: tuple[float, ...]

    @classmethod
    def fit(cls, rows, preserve: tuple[int, ...] = ()) -> "Standardizer":
        rows = [tuple(map(float, row)) for row in rows]
        if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("normalization needs non-empty rectangular rows")
        if not all(math.isfinite(v) for r in rows for v in r):
            raise ValueError("normalization needs finite values")
        means = [sum(r[j] for r in rows) / len(rows) for j in range(len(rows[0]))]
        scales = [max(math.sqrt(sum((r[j] - means[j]) ** 2 for r in rows) / max(len(rows)-1, 1)), 1e-8) for j in range(len(means))]
        for j in preserve:
            means[j], scales[j] = 0.0, 1.0
        return cls(tuple(means), tuple(scales))

    def transform(self, rows) -> list[list[float]]:
        rows = [tuple(map(float, row)) for row in rows]
        if any(len(r) != len(self.mean) or not all(math.isfinite(v) for v in r) for r in rows):
            raise ValueError("normalization feature shape or finiteness mismatch")
        return [[(v-m)/s for v, m, s in zip(row, self.mean, self.scale)] for row in rows]

    def to_dict(self) -> dict:
        return {"mean": list(self.mean), "scale": list(self.scale)}

    @classmethod
    def from_dict(cls, state: dict) -> "Standardizer":
        m, s = tuple(map(float, state["mean"])), tuple(map(float, state["scale"]))
        if not m or len(m) != len(s) or not all(math.isfinite(v) for v in m+s) or any(v <= 0 for v in s):
            raise ValueError("invalid stored normalization")
        return cls(m, s)


@dataclass(frozen=True)
class SurfacePreprocessor:
    nodes: Standardizer
    edges: Standardizer
    cp: Standardizer

    @classmethod
    def fit(cls, graphs) -> "SurfacePreprocessor":
        return cls(Standardizer.fit([r for g in graphs for r in g.x.tolist()], preserve=(6,)),
                   Standardizer.fit([r for g in graphs for r in g.edge_attr.tolist()]),
                   Standardizer.fit([r for g in graphs for r in g.y.tolist()]))

    def to_dict(self) -> dict:
        return {"schema_version": 1, "nodes": self.nodes.to_dict(), "edges": self.edges.to_dict(), "cp": self.cp.to_dict()}

    @classmethod
    def from_dict(cls, state: dict) -> "SurfacePreprocessor":
        if state.get("schema_version") != 1:
            raise ValueError("unsupported preprocessing schema")
        result = cls(*(Standardizer.from_dict(state[k]) for k in ("nodes", "edges", "cp")))
        if tuple(len(s.mean) for s in (result.nodes, result.edges, result.cp)) != (7, 5, 1):
            raise ValueError("preprocessing feature layout mismatch")
        return result
