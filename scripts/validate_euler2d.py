#!/usr/bin/env python3
"""Run the read-only Euler 2D validation report on a local dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uav_euler2d import Euler2DDataset, ValidationConfig, validate_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = validate_dataset(Euler2DDataset(args.dataset), ValidationConfig())
    summary = {
        "passed": report.passed,
        "errors": report.errors,
        "warnings": report.warnings,
        "metrics": {
            key: value
            for key, value in report.metrics.items()
            if not key.endswith(".CL_from_surface") and not key.endswith(".CD_from_surface")
        },
    }
    if args.as_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"passed={summary['passed']}")
        print(f"errors={len(report.errors)} warnings={len(report.warnings)}")
        print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))
        for message in report.errors + report.warnings:
            print(message)
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
