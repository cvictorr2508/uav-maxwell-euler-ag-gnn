"""Read-only loading and validation helpers for the Euler 2D dataset."""

from .loader import Euler2DDataset, StatusFilter
from .graph import SurfaceEdge, SurfaceGraph, SurfaceNode, build_surface_graph
from .validation import ValidationConfig, ValidationReport, validate_dataset
from .experiment import FeatureSpec, MeanPredictor, RidgePredictor, evaluate_predictor
from .geometry import ContinuityReport, check_contour_continuity

__all__ = [
    "Euler2DDataset",
    "StatusFilter",
    "SurfaceEdge",
    "SurfaceGraph",
    "SurfaceNode",
    "build_surface_graph",
    "ValidationConfig",
    "ValidationReport",
    "validate_dataset",
    "FeatureSpec",
    "MeanPredictor",
    "RidgePredictor",
    "evaluate_predictor",
    "ContinuityReport",
    "check_contour_continuity",
]
