"""Independent structural and physical checks for the Euler 2D dataset."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

from .loader import Euler2DDataset, VALID_STATUSES


@dataclass(frozen=True)
class ValidationConfig:
    """Documented tolerances; percentages are relative where meaningful."""

    cp_abs: float = 1e-4
    closure_abs: float = 1e-9
    normal_abs: float = 1e-9
    coefficient_relative_pct: dict[str, float] = field(
        default_factory=lambda: {"CL": 0.1, "CD": 2.0}
    )
    coefficient_absolute: dict[str, float] = field(
        default_factory=lambda: {"CL": 1e-8, "CD": 1e-8}
    )


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, float | int | dict] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.errors


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _number(row: dict, key: str) -> float:
    return float(row[key])


def _positive(value: object) -> bool:
    return _finite(value) and float(value) > 0.0


def _relative_or_absolute(actual: float, expected: float, rel_pct: float, abs_tol: float) -> bool:
    scale = max(abs(expected), abs_tol)
    return abs(actual - expected) <= max(abs_tol, scale * rel_pct / 100.0)


def integrate_surface(rows: Iterable[dict], alpha_deg: float, chord: float) -> tuple[float, float]:
    """Integrate face pressure using the documented external body normal."""
    alpha = math.radians(alpha_deg)
    cfx = -sum(float(r["Cp"]) * float(r["normal_x"]) * float(r["segment_length_m"]) for r in rows) / chord
    cfy = -sum(float(r["Cp"]) * float(r["normal_y"]) * float(r["segment_length_m"]) for r in rows) / chord
    cd = cfx * math.cos(alpha) + cfy * math.sin(alpha)
    cl = -cfx * math.sin(alpha) + cfy * math.cos(alpha)
    return cl, cd


def _validate_surface(dataset: Euler2DDataset, case: dict, config: ValidationConfig, report: ValidationReport) -> None:
    case_id = case["case_id"]
    rows = dataset.surface_rows(case_id)
    if not rows:
        report.errors.append(f"{case_id}: surface has no faces")
    expected_indices = list(range(len(rows)))
    indices = [int(row["contour_index"]) for row in rows]
    if indices != expected_indices:
        report.errors.append(f"{case_id}: contour_index is not a contiguous sequence")
    seen = set()
    constants = dataset.physical_constants()
    for row in rows:
        if row["case_id"] != case_id:
            report.errors.append(f"{case_id}: row has case_id={row['case_id']}")
        key = (row["entity_id"], row["contour_index"])
        if key in seen:
            report.errors.append(f"{case_id}: duplicate face key {key}")
        seen.add(key)
        for name in ("x_m", "y_m", "normal_x", "normal_y", "segment_length_m", "pressure_abs_Pa", "Cp"):
            if not _finite(row[name]):
                report.errors.append(f"{case_id}: non-finite {name}")
        if not _positive(row["segment_length_m"]):
            report.errors.append(f"{case_id}: segment_length_m must be positive")
        norm = math.hypot(float(row["normal_x"]), float(row["normal_y"]))
        if abs(norm - 1.0) > config.normal_abs:
            report.errors.append(f"{case_id}: non-unit normal")
        cp = (float(row["pressure_abs_Pa"]) - constants["p_inf_Pa"]) / constants["q_inf_Pa"]
        if abs(cp - float(row["Cp"])) > config.cp_abs:
            report.errors.append(f"{case_id}: Cp-pressure mismatch")
    closure_x = sum(float(row["normal_x"]) * float(row["segment_length_m"]) for row in rows)
    closure_y = sum(float(row["normal_y"]) * float(row["segment_length_m"]) for row in rows)
    if max(abs(closure_x), abs(closure_y)) > config.closure_abs:
        report.errors.append(f"{case_id}: contour does not close")
    if case["status"] != "failed":
        cl, cd = integrate_surface(rows, float(case["alpha_deg"]), float(case["chord_ref_m"]))
        report.metrics[f"{case_id}.CL_from_surface"] = cl
        report.metrics[f"{case_id}.CD_from_surface"] = cd
        # A surface export is a snapshot.  For non-converged cases the public
        # CL/CD target is a window mean, while CL_final/CD_final identify the
        # snapshot that is physically comparable to the exported surface.
        comparison = "CL/CD"
        expected_values = (float(case["CL"]), float(case["CD"]))
        if case["status"] == "non_converged":
            comparison = "CL_final/CD_final"
            expected_values = (float(case["CL_final"]), float(case["CD_final"]))
            report.warnings.append(
                f"{case_id}: surface compared with final snapshot; window mean remains the target"
            )
        for name, actual, expected_key in (("CL", cl, "CL"), ("CD", cd, "CD")):
            expected = expected_values[0 if name == "CL" else 1]
            report.metrics[f"{case_id}.{name}_comparison"] = comparison
            report.metrics[f"{case_id}.{name}_relative_pct"] = 100.0 * (actual / expected - 1.0)
            if not _relative_or_absolute(
                actual, expected, config.coefficient_relative_pct[name], config.coefficient_absolute[name]
            ):
                report.errors.append(f"{case_id}: integrated {name} exceeds tolerance against {comparison}")


def validate_dataset(dataset: Euler2DDataset, config: ValidationConfig | None = None) -> ValidationReport:
    config = config or ValidationConfig()
    report = ValidationReport()
    cases = dataset.cases
    ids = [row["case_id"] for row in cases]
    geometries = [row["geometry_id"] for row in cases]
    if len(ids) != len(set(ids)):
        report.errors.append("case_id values are not unique")
    if any(not geometry_id for geometry_id in geometries):
        report.errors.append("geometry_id values must be non-empty")
    unknown = {row["status"] for row in cases} - VALID_STATUSES
    if unknown:
        report.errors.append(f"unknown statuses: {sorted(unknown)}")
    for row in cases:
        if row["status"] == "failed":
            if row["CL"] not in ("", "nan", "NaN") or row["CD"] not in ("", "nan", "NaN"):
                report.errors.append(f"{row['case_id']}: failed case has a numeric target")
        else:
            for key in ("CL", "CD", "alpha_deg", "chord_ref_m"):
                if not _finite(row[key]):
                    report.errors.append(f"{row['case_id']}: invalid {key}")
            if not _positive(row["chord_ref_m"]):
                report.errors.append(f"{row['case_id']}: chord_ref_m must be positive")
            for key in ("rho_inf_kg_m3", "p_inf_Pa", "T_inf_K", "gamma", "V_inf_m_s", "q_inf_Pa"):
                if key in row and not _positive(row[key]):
                    report.errors.append(f"{row['case_id']}: {key} must be positive")
    constants = dataset.physical_constants()
    for key, value in constants.items():
        if key != "gamma" and not _positive(value):
            report.errors.append(f"physical constant {key} must be positive")
    if not _finite(constants.get("gamma")) or constants["gamma"] <= 1.0:
        report.errors.append("physical constant gamma must be greater than one")
    split_sets = {name: set(dataset.split_manifest[name]) for name in ("train", "val", "test")}
    known_geometries = set(geometries)
    for split, split_ids in split_sets.items():
        unknown_ids = split_ids - known_geometries
        if unknown_ids:
            report.errors.append(f"{split} references unknown geometries: {sorted(unknown_ids)}")
    excluded_failed = set(dataset.split_manifest.get("excluded_failed", []))
    unknown_excluded = excluded_failed - known_geometries
    if unknown_excluded:
        report.errors.append(f"excluded_failed references unknown geometries: {sorted(unknown_excluded)}")
    assigned = set.union(*split_sets.values(), excluded_failed)
    unassigned = known_geometries - assigned
    if unassigned:
        report.errors.append(f"geometries are not assigned to a split or excluded_failed: {sorted(unassigned)}")
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = split_sets[left] & split_sets[right]
        if overlap:
            report.errors.append(f"split overlap {left}/{right}: {sorted(overlap)}")
    failed_geometries = {row["geometry_id"] for row in cases if row["status"] == "failed"}
    if failed_geometries & set.union(*split_sets.values()):
        report.errors.append("failed geometries appear in a data split")
    expected_success = {name: sum(row["status"] == "success" and row["geometry_id"] in ids_ for row in cases) for name, ids_ in split_sets.items()}
    report.metrics["success_by_split"] = expected_success
    if expected_success != {"train": 31, "val": 7, "test": 8}:
        report.warnings.append(f"deterministic success counts differ: {expected_success}")
    report.metrics["case_count"] = len(cases)
    report.metrics["surface_case_count"] = sum(row["status"] != "failed" for row in cases)
    for row in cases:
        if row["status"] != "failed":
            _validate_surface(dataset, row, config, report)
    return report
