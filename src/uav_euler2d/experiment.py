"""Leakage-safe S3 experiment protocol and conventional baselines.

The experiment unit is one case, never one surface node.  Inputs are limited
to parameters known before the solver run; Fluent observables are targets only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Mapping

from .loader import Euler2DDataset

PRE_SOLVER_FEATURES = ("m", "p", "t", "mach_inf", "alpha_deg", "chord_ref_m")
REFERENCE_TARGETS = ("CL", "CD")
FORBIDDEN_INPUTS = frozenset({"Cp", "pressure_abs_Pa", "CL", "CD", "CL_final", "CD_final"})


@dataclass(frozen=True)
class FeatureSpec:
    names: tuple[str, ...] = PRE_SOLVER_FEATURES
    targets: tuple[str, ...] = REFERENCE_TARGETS

    def validate(self) -> None:
        unknown = set(self.names) - set(PRE_SOLVER_FEATURES)
        if unknown:
            raise ValueError(f"unsupported or post-solver input features: {sorted(unknown)}")
        leakage = set(self.names) & FORBIDDEN_INPUTS
        if leakage:
            raise ValueError(f"target/observable leakage in inputs: {sorted(leakage)}")
        if not self.targets:
            raise ValueError("at least one target is required")


@dataclass(frozen=True)
class MetricReport:
    split: str
    count: int
    mae: Mapping[str, float]
    rmse: Mapping[str, float]


def case_features(case: Mapping[str, str], spec: FeatureSpec) -> tuple[float, ...]:
    spec.validate()
    values = tuple(float(case[name]) for name in spec.names)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"non-finite pre-solver feature for {case['case_id']}")
    return values


def case_targets(case: Mapping[str, str], spec: FeatureSpec) -> tuple[float, ...]:
    spec.validate()
    values = tuple(float(case[name]) for name in spec.targets)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"non-finite target for {case['case_id']}")
    return values


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Small deterministic Gaussian elimination fallback (no sklearn needed)."""
    n = len(vector)
    aug = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            aug[col][col] += 1e-8
            pivot = col
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col])]
    return [aug[row][-1] for row in range(n)]


class MeanPredictor:
    name = "train_mean"

    def fit(self, rows: list[Mapping[str, str]], spec: FeatureSpec) -> "MeanPredictor":
        targets = [case_targets(row, spec) for row in rows]
        self.mean = tuple(sum(values[j] for values in targets) / len(targets) for j in range(len(spec.targets)))
        return self

    def predict(self, row: Mapping[str, str], spec: FeatureSpec) -> tuple[float, ...]:
        return self.mean


class RidgePredictor:
    name = "ridge_geometry"

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, rows: list[Mapping[str, str]], spec: FeatureSpec) -> "RidgePredictor":
        x = [case_features(row, spec) for row in rows]
        y = [case_targets(row, spec) for row in rows]
        self.mean = [sum(row[j] for row in x) / len(x) for j in range(len(spec.names))]
        self.scale = [max(math.sqrt(sum((row[j] - self.mean[j]) ** 2 for row in x) / len(x)), 1e-12) for j in range(len(spec.names))]
        design = [[1.0] + [(row[j] - self.mean[j]) / self.scale[j] for j in range(len(spec.names))] for row in x]
        gram = [[sum(row[i] * row[j] for row in design) for j in range(len(design[0]))] for i in range(len(design[0]))]
        for i in range(1, len(gram)):
            gram[i][i] += self.alpha
        self.weights = []
        for target in range(len(spec.targets)):
            rhs = [sum(design[row][i] * y[row][target] for row in range(len(rows))) for i in range(len(design[0]))]
            self.weights.append(_solve(gram, rhs))
        return self

    def predict(self, row: Mapping[str, str], spec: FeatureSpec) -> tuple[float, ...]:
        values = case_features(row, spec)
        design = [1.0] + [(values[j] - self.mean[j]) / self.scale[j] for j in range(len(values))]
        return tuple(sum(weight[i] * design[i] for i in range(len(design))) for weight in self.weights)


def metrics(split: str, actual: list[tuple[float, ...]], predicted: list[tuple[float, ...]], spec: FeatureSpec) -> MetricReport:
    if not actual:
        raise ValueError(f"cannot score empty split: {split}")
    mae, rmse = {}, {}
    for index, name in enumerate(spec.targets):
        errors = [predicted[i][index] - actual[i][index] for i in range(len(actual))]
        mae[name] = sum(abs(error) for error in errors) / len(errors)
        rmse[name] = math.sqrt(sum(error * error for error in errors) / len(errors))
    return MetricReport(split, len(actual), mae, rmse)


def evaluate_predictor(dataset: Euler2DDataset, predictor, spec: FeatureSpec) -> tuple[MetricReport, ...]:
    spec.validate()
    train = list(dataset.cases_for_split("train", ("success",)))
    if not train:
        raise ValueError("training split has no converged cases")
    predictor.fit(train, spec)
    reports = []
    for split in ("train", "val", "test"):
        rows = list(dataset.cases_for_split(split, ("success",)))
        actual = [case_targets(row, spec) for row in rows]
        predicted = [predictor.predict(row, spec) for row in rows]
        reports.append(metrics(split, actual, predicted, spec))
    return tuple(reports)


def report_dict(report: MetricReport) -> dict:
    return {"split": report.split, "count": report.count, "MAE": dict(report.mae), "RMSE": dict(report.rmse)}
