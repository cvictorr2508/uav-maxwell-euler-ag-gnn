"""Build an offline code/documentation handoff, excluding private scientific data.

Run after committing and pushing the release. GitHub CLI must have read access.
The optional dataset path produces hashes only, never copies dataset contents.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from verify_transfer import sha256


REPO = Path(__file__).resolve().parents[1]
REMOTE = "cvictorr2508/uav-maxwell-euler-ag-gnn"


def command(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True, encoding="utf-8").strip()


def api(endpoint: str):
    return json.loads(command("gh", "api", endpoint))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new directory outside repository")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--evidence", type=Path, required=True, help="verified local evidence JSON")
    parser.add_argument("--publication-evidence", type=Path, help="verified deployment and live-site evidence JSON")
    parser.add_argument("--checkpoint", type=Path, help="final human-readable checkpoint")
    parser.add_argument("--sync-evidence", type=Path, help="verified main-to-develop synchronization JSON")
    args = parser.parse_args()
    root = args.output.resolve()
    if root.is_relative_to(REPO):
        raise ValueError("handoff must be outside the checkout")
    if root.exists():
        raise FileExistsError("choose a new output directory; existing package is preserved")
    if command("git", "status", "--porcelain"):
        raise RuntimeError("commit changes before packaging")
    sha = command("git", "rev-parse", "HEAD")
    branch = command("git", "branch", "--show-current")
    if not branch:
        raise RuntimeError("package a named branch so the offline checkout can be restored")
    pr = api(f"repos/{REMOTE}/pulls/{args.pr}")
    if pr["merged"]:
        command("git", "merge-base", "--is-ancestor", pr["merge_commit_sha"], "HEAD")
    elif pr["head"]["sha"] != sha:
        raise RuntimeError("local HEAD differs from open PR head; fetch/inspect before packaging")
    checks_sha = pr["head"]["sha"]
    checks = api(f"repos/{REMOTE}/commits/{checks_sha}/check-runs?per_page=100")
    pages = api(f"repos/{REMOTE}/pages")
    branches = api(f"repos/{REMOTE}/branches?per_page=100")
    sync = None
    if args.sync_evidence:
        sync = json.loads(args.sync_evidence.read_text(encoding="utf-8"))
        if not sync["passed"] or sync["develop_sha"] != sha:
            raise RuntimeError("sync evidence must verify the packaged develop commit")
    root.mkdir(parents=True)
    shutil.copy2(REPO / "PROJECT_STATE.md", root / "PROJECT_STATE.md")
    shutil.copytree(REPO / "handoff", root / "handoff")
    if args.sync_evidence:
        shutil.copy2(args.sync_evidence, root / "SYNC_VERIFICATION.json")
    (root / "scripts").mkdir()
    shutil.copy2(REPO / "scripts" / "verify_transfer.py", root / "scripts" / "verify_transfer.py")
    shutil.copy2(args.evidence, root / "LOCAL_VERIFICATION.json")
    publication = None
    if args.publication_evidence:
        publication = json.loads(args.publication_evidence.read_text(encoding="utf-8"))
        if not pr["merged"] or not publication["passed"] or publication["source_sha"] != pr["merge_commit_sha"]:
            raise RuntimeError("publication evidence must verify this PR's merge commit")
        shutil.copy2(args.publication_evidence, root / "PUBLICATION_VERIFICATION.json")
        pdf_record = next(row for row in publication["http_files"] if row["path"].lower().endswith(".pdf"))
        published_pdf = args.publication_evidence.parent / "published-book.pdf"
        if sha256(published_pdf) != pdf_record["sha256"]:
            raise RuntimeError("downloaded PDF differs from publication evidence")
        (root / "published-book").mkdir()
        shutil.copy2(published_pdf, root / "published-book" / pdf_record["filename"])
    if args.checkpoint:
        shutil.copy2(args.checkpoint, root / "CHECKPOINT_FINAL.md")
    if (REPO / "_book" / "index.html").exists():
        shutil.copytree(REPO / "_book", root / "rendered-book")
    command("git", "archive", "--format=zip", "--output", str(root / "repository-source.zip"), "HEAD")
    bundle_refs = [f"refs/heads/{branch}"]
    if pr["merged"]:
        bundle_refs += ["refs/remotes/origin/main", "refs/remotes/origin/develop"]
    command("git", "bundle", "create", str(root / "repository.bundle"), *bundle_refs)
    command("git", "bundle", "verify", str(root / "repository.bundle"))
    check_rows = [{key: row.get(key) for key in ("name", "status", "conclusion", "html_url", "head_sha")} for row in checks["check_runs"]]
    receipt = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": f"https://github.com/{REMOTE}",
        "head_sha": sha,
        "branch": branch,
        "package_commit": sha,
        "package_commit_is_local_checkpoint": not any(b["commit"]["sha"] == sha for b in branches),
        "checks_sha": checks_sha,
        "published_source_sha": publication["source_sha"] if publication else None,
        "pr": {"number": pr["number"], "url": pr["html_url"], "state": pr["state"], "merged": pr["merged"], "merged_at": pr["merged_at"], "merge_commit_sha": pr["merge_commit_sha"], "head_sha": pr["head"]["sha"], "base": pr["base"]["ref"], "head": pr["head"]["ref"]},
        "checks": check_rows,
        "all_required_named_checks_passed": all(any(c["name"] == name and c["status"] == "completed" and c["conclusion"] == "success" for c in check_rows) for name in ("test", "render")),
        "remote_branches": {b["name"]: b["commit"]["sha"] for b in branches},
        "pages": {k: pages.get(k) for k in ("status", "html_url", "build_type", "source")},
        "publication_of_this_pr": "verified; see PUBLICATION_VERIFICATION.json" if publication else "not_verified_by_this_package",
        "main_to_develop_sync": sync,
        "packaging_environment": {"python": platform.python_version(), "platform": platform.platform(), "quarto": command("quarto", "--version"), "git": command("git", "--version")},
        "private_data_included": False,
        "private_dataset_hashes_included": args.dataset_root is not None,
    }
    write_json(root / "RELEASE_RECEIPT.json", receipt)
    if args.dataset_root:
        dataset = args.dataset_root.resolve(strict=True)
        write_json(root / "DATASET_SHA256.json", {p.relative_to(dataset).as_posix(): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(dataset.rglob("*")) if p.is_file()})
    write_json(root / "SHA256SUMS.json", {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()})
    command(sys.executable, str(root / "scripts" / "verify_transfer.py"), str(root))
    archive = root.with_name(root.name + ".zip")
    if archive.exists():
        raise FileExistsError(archive)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root.parent))
    write_json(archive.with_name(archive.name + ".sha256.json"), {archive.name: sha256(archive)})
    print(json.dumps({"package": str(root), "zip": str(archive), "head_sha": sha, "files": len(list(root.rglob("*")))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
