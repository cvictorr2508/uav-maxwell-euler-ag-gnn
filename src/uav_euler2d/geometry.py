"""Diagnostics for the geometric meaning of contour adjacencies."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .graph import SurfaceGraph


@dataclass(frozen=True)
class ContinuityReport:
    passed: bool
    edge_count: int
    max_center_gap_m: float
    median_segment_length_m: float
    max_gap_to_segment_ratio: float
    signed_center_area_m2: float
    orientation_semantics: str = "diagnostic_only; contour_index order is not a physical orientation"
    warnings: tuple[str, ...] = ()


def check_contour_continuity(graph: SurfaceGraph, gap_ratio_limit: float = 4.0) -> ContinuityReport:
    """Check ordered, finite, geometrically local contour adjacency.

    Surface rows provide face centers and segment lengths, not face endpoints.
    Thus this is a continuity diagnostic, not a proof of shared-face topology.
    """
    if not graph.nodes or not graph.contour_edges:
        return ContinuityReport(False, 0, math.nan, math.nan, math.inf, math.nan, warnings=("empty contour",))
    by_id = {node.node_id: node for node in graph.nodes}
    gaps, ratios = [], []
    for edge in graph.contour_edges:
        source, target = by_id[edge.source], by_id[edge.target]
        gap = math.hypot(source.x_m - target.x_m, source.y_m - target.y_m)
        scale = max(source.segment_length_m, target.segment_length_m, 1e-12)
        gaps.append(gap)
        ratios.append(gap / scale)
    lengths = sorted(node.segment_length_m for node in graph.nodes)
    median = lengths[len(lengths) // 2]
    area = 0.5 * sum(
        left.x_m * right.y_m - right.x_m * left.y_m
        for left, right in zip(graph.nodes, graph.nodes[1:] + graph.nodes[:1])
    )
    warnings = []
    if max(ratios) > gap_ratio_limit:
        warnings.append(f"max center-gap/segment ratio {max(ratios):.3g} exceeds {gap_ratio_limit:g}")
    return ContinuityReport(
        passed=not warnings,
        edge_count=len(graph.contour_edges),
        max_center_gap_m=max(gaps),
        median_segment_length_m=median,
        max_gap_to_segment_ratio=max(ratios),
        signed_center_area_m2=area,
        warnings=tuple(warnings),
    )
