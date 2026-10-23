"""Small, read-only loader for ``dataset_euler_2d``.

The loader deliberately does not infer missing topology or rewrite the source
dataset.  Surface adjacency is the documented contour order only.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

StatusFilter = frozenset[str]
VALID_STATUSES = frozenset({"success", "non_converged", "failed"})
VALID_SPLITS = frozenset({"train", "val", "test"})


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _as_float(value: object) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


class Euler2DDataset:
    """Read a dataset directory without mutating it."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.cases_path = self.root / "cases.csv"
        self.surface_dir = self.root / "surface"
        self.manifest = _read_json(self.root / "dataset_manifest.json")
        self.split_manifest = _read_json(self.root / "split_manifest.json")
        self.mesh_metadata = _read_json(self.root / "meshes" / "mesh_metadata.json")
        with self.cases_path.open(encoding="utf-8-sig", newline="") as stream:
            self._cases = tuple(dict(row) for row in csv.DictReader(stream))
        self._by_case = {row["case_id"]: row for row in self._cases}

    @property
    def cases(self) -> tuple[Mapping[str, str], ...]:
        return self._cases

    @property
    def statuses(self) -> frozenset[str]:
        return frozenset(row["status"] for row in self._cases)

    def iter_cases(
        self,
        statuses: Iterable[str] | None = None,
        split: str | None = None,
    ) -> Iterator[Mapping[str, str]]:
        selected = None if statuses is None else frozenset(statuses)
        if selected is not None and not selected <= VALID_STATUSES:
            raise ValueError(f"unknown status: {sorted(selected - VALID_STATUSES)}")
        if split is not None and split not in VALID_SPLITS:
            raise ValueError(f"unknown split: {split}")
        ids = None if split is None else set(self.split_manifest[split])
        for row in self._cases:
            if selected is not None and row["status"] not in selected:
                continue
            if ids is not None and row["geometry_id"] not in ids:
                continue
            yield row

    def cases_for_split(
        self, split: str, statuses: Iterable[str] = ("success",)
    ) -> tuple[Mapping[str, str], ...]:
        if split not in VALID_SPLITS:
            raise ValueError(f"unknown split: {split}")
        return tuple(self.iter_cases(statuses=statuses, split=split))

    def cases_for_geometry(self, geometry_id: str) -> tuple[Mapping[str, str], ...]:
        """Return all runs/cases belonging to one geometry identifier."""
        return tuple(row for row in self._cases if row["geometry_id"] == geometry_id)

    def case(self, case_id: str) -> Mapping[str, str]:
        try:
            return self._by_case[case_id]
        except KeyError as exc:
            raise KeyError(f"unknown case_id: {case_id}") from exc

    def surface_path(self, case_id: str) -> Path:
        row = self.case(case_id)
        expected = self.root / row["surface_file"]
        if expected != self.surface_dir / f"case_{case_id}.parquet":
            raise ValueError(f"unexpected surface path for {case_id}: {expected}")
        return expected

    def surface_rows(self, case_id: str) -> tuple[dict, ...]:
        """Return Parquet rows as dictionaries; no Parquet dependency is hidden."""
        path = self.surface_path(case_id)
        try:
            import pyarrow.parquet as parquet
        except ImportError as exc:
            raise RuntimeError(
                "reading surface Parquet requires the optional 'pyarrow' dependency"
            ) from exc
        return tuple(parquet.read_table(path).to_pylist())

    def physical_constants(self) -> dict[str, float]:
        conditions = self.manifest["conditions"]
        return {key: _as_float(conditions[key]) for key in (
            "p_inf_Pa", "q_inf_Pa", "rho_inf_kg_m3", "V_inf_m_s", "chord_ref_m", "gamma"
        )}
