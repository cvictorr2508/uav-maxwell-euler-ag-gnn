"""Minimal, provenance-preserving graph for an Euler 2D surface export.

Only the ordered boundary contour is represented.  The Parquet export does
not contain volume-cell adjacency, so this module intentionally creates no
volumetric edges and does not infer them from coordinates or distances.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .loader import Euler2DDataset


@dataclass(frozen=True)
class SurfaceNode:
    """One exported surface face, retaining identifiers and physical fields."""

    node_id: str
    case_id: str
    geometry_id: str
    entity_id: str
    contour_index: int
    x_m: float
    y_m: float
    normal_x: float
    normal_y: float
    segment_length_m: float
    attributes: Mapping[str, Any]


@dataclass(frozen=True)
class SurfaceEdge:
    """A directed edge justified by consecutive documented contour order."""

    source: str
    target: str
    contour_index: int
    connectivity: str = "boundary_contour"


@dataclass(frozen=True)
class SurfaceGraph:
    """Graph with boundary connectivity only and explicit Parquet provenance."""

    case_id: str
    geometry_id: str
    source_parquet: str
    nodes: tuple[SurfaceNode, ...]
    contour_edges: tuple[SurfaceEdge, ...]
    volumetric_edges: tuple[SurfaceEdge, ...] = ()

    @property
    def connectivity_kinds(self) -> tuple[str, ...]:
        return ("boundary_contour",) if self.contour_edges else ()

    def summary(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "geometry_id": self.geometry_id,
            "source_parquet": self.source_parquet,
            "node_count": len(self.nodes),
            "boundary_edge_count": len(self.contour_edges),
            "volumetric_edge_count": len(self.volumetric_edges),
            "connectivity": list(self.connectivity_kinds),
            "first_nodes": [
                {
                    "node_id": node.node_id,
                    "entity_id": node.entity_id,
                    "contour_index": node.contour_index,
                    "x_m": node.x_m,
                    "y_m": node.y_m,
                    "Cp": node.attributes.get("Cp"),
                }
                for node in self.nodes[:3]
            ],
        }


def build_surface_graph(dataset: Euler2DDataset, case_id: str) -> SurfaceGraph:
    """Build only the contour graph explicitly supported by the source data."""
    case = dataset.case(case_id)
    if case["status"] == "failed":
        raise ValueError(f"cannot build a surface graph for failed case {case_id}")
    rows = dataset.surface_rows(case_id)
    if not rows:
        raise ValueError(f"cannot build a surface graph with no rows: {case_id}")
    indices = [int(row["contour_index"]) for row in rows]
    if indices != list(range(len(rows))):
        raise ValueError(f"{case_id}: contour_index must be contiguous and ordered")

    nodes: list[SurfaceNode] = []
    for row in rows:
        contour_index = int(row["contour_index"])
        node_id = f"{case_id}:face:{contour_index}"
        nodes.append(
            SurfaceNode(
                node_id=node_id,
                case_id=case_id,
                geometry_id=case["geometry_id"],
                entity_id=str(row["entity_id"]),
                contour_index=contour_index,
                x_m=float(row["x_m"]),
                y_m=float(row["y_m"]),
                normal_x=float(row["normal_x"]),
                normal_y=float(row["normal_y"]),
                segment_length_m=float(row["segment_length_m"]),
                attributes=dict(row),
            )
        )

    edges = tuple(
        SurfaceEdge(
            source=nodes[index].node_id,
            target=nodes[(index + 1) % len(nodes)].node_id,
            contour_index=nodes[index].contour_index,
        )
        for index in range(len(nodes))
    )
    source = Path(dataset.surface_path(case_id))
    try:
        source_name = source.relative_to(dataset.root).as_posix()
    except ValueError:
        source_name = source.as_posix()
    return SurfaceGraph(
        case_id=case_id,
        geometry_id=case["geometry_id"],
        source_parquet=source_name,
        nodes=tuple(nodes),
        contour_edges=edges,
    )
