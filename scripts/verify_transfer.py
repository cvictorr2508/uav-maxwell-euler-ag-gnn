"""Verify a transferred handoff directory against its SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory.resolve()
    manifest = json.loads((root / "SHA256SUMS.json").read_text(encoding="utf-8"))
    failures = []
    for name, expected in manifest.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            failures.append(f"unsafe path: {name}")
        elif not path.is_file() or sha256(path) != expected:
            failures.append(name)
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    extras = actual - set(manifest) - {"SHA256SUMS.json"}
    failures.extend(f"unexpected file: {name}" for name in sorted(extras))
    print(json.dumps({"passed": not failures, "checked": len(manifest), "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
