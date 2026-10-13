"""Build and inspect one documented Euler 2D boundary graph.

Usage:
    python scripts/inspect_surface_graph.py DATASET_ROOT CASE_ID
"""

from __future__ import annotations

import argparse
import json

from uav_euler2d.graph import build_surface_graph
from uav_euler2d.loader import Euler2DDataset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", help="path to dataset_euler_2d")
    parser.add_argument("case_id", help="case identifier, e.g. c0015")
    args = parser.parse_args()
    graph = build_surface_graph(Euler2DDataset(args.dataset), args.case_id)
    print(json.dumps(graph.summary(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
