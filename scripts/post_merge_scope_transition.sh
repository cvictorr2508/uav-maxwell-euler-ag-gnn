#!/usr/bin/env bash
# ONE-TIME transition after merge of PR #22; preserve historical commit tips.
set -euo pipefail
repo="${GITHUB_REPOSITORY:?}"
[[ "$repo" == "cvictorr2508/uav-maxwell-euler-ag-gnn" ]] || { echo "Wrong repository"; exit 1; }
[[ "${GITHUB_REF:-}" == "refs/heads/develop" ]] || { echo "Wrong branch"; exit 1; }
data="$(gh api "repos/$repo/pulls/22")"
merged="$(jq -r '.merged_at // empty' <<< "$data")"
merge_sha="$(jq -r '.merge_commit_sha // empty' <<< "$data")"
source_sha="$(jq -r '.head.sha // empty' <<< "$data")"
if [[ -z "$merged" || -z "$merge_sha" || -z "$source_sha" ]]; then
  echo "PR #22 is not yet merged; no cleanup."
  exit 0
fi
git merge-base --is-ancestor "$merge_sha" "${GITHUB_SHA:?}" || { echo "PR #22 is not in this develop revision"; exit 0; }
prefix="archive/academic-realignment-2026-10-13"
if gh api "repos/$repo/git/ref/tags/$prefix/completed" >/dev/null 2>&1; then
  echo "Transition already completed."
  exit 0
fi

# Frozen refs from 13 October 2026. Do not touch branches that changed.
mapfile -t refs <<'REFS'
chore/audit-bibliography-ch1-ch3 0e683c23304517007a0f698086efbd0f47ca5188
docs/ch5-theory-methodology 87439ba3ddefd31e782e29c6daec24290588ab66
docs/s0-ga-euler-dataset-contract 74818f0bf0ec7fafe72490fd5ddfe82f3ab4ce7f
feature/ch5-2d-data-ga-pipeline 7e62b86b119bce3d028d933d43c2f3085c123b92
feature/m1-problem-definition 73dd7bf5868ddea3d39521d85a61051daca5758e
feature/m2-geometric-algebra-foundations 3b383d701fabfaa2eb358e60f61f7418e10cb29
feature/m3-maxwell-euler-physics 1cb2eb30c739e4bd2c68fa942709a601b537e09f
refactor/2d-3d-study-architecture dcd2a6a5b0234d27b65bce83a9fbfc2249bd2a06
review/ch5-methodology-parametrization-doe 920bb3d6508d012ca3b7863a61790b968ac00249
REFS
refs+=("refactor/academic-research-scope-2026 $source_sha")

# Preflight: all branch heads must still equal the approved snapshot, or
# must already have an archive tag at that exact revision.
for record in "${refs[@]}"; do
  read -r name expected <<< "$record"
  [[ "$name" != "main" && "$name" != "develop" && "$name" != "gh-pages" ]] || exit 1
  current="$(gh api "repos/$repo/git/ref/heads/$name" --jq '.object.sha' 2>/dev/null || true)"
  saved="$(gh api "repos/$repo/git/ref/tags/$prefix/$name" --jq '.object.sha' 2>/dev/null || true)"
  if [[ ( -n "$current" && "$current" != "$expected" ) || ( -n "$saved" && "$saved" != "$expected" ) || ( -z "$current" && "$saved" != "$expected" ) ]]; then
    echo "::error::$name changed or is not safely archived; refusing any deletion."
    exit 1
  fi
done

# Create lightweight tags, verifying all commits are protected before deletion.
for record in "${refs[@]}"; do
  read -r name expected <<< "$record"
  if ! gh api "repos/$repo/git/ref/tags/$prefix/$name" >/dev/null 2>&1; then
    gh api -X POST "repos/$repo/git/refs" -f "ref=refs/tags/$prefix/$name" -f "sha=$expected" --silent
  fi
  saved="$(gh api "repos/$repo/git/ref/tags/$prefix/$name" --jq '.object.sha')"
  [[ "$saved" == "$expected" ]] || { echo "::error::Archive mismatch: $name"; exit 1; }
done

# PR #16 is an open legacy draft whose head will be retired; its archive tag
# and full PR discussion remain available. Close it only after archiving.
if [[ "$(gh api "repos/$repo/pulls/16" --jq '.state')" == "open" ]]; then
  gh api -X POST "repos/$repo/issues/16/comments" -f "body=Superseded by the academic realignment in PR #22. Historical code is preserved by refs/tags/$prefix/feature/ch5-2d-data-ga-pipeline. The former implementation was not merged." --silent
  gh api -X PATCH "repos/$repo/pulls/16" -f state=closed --silent
fi

for record in "${refs[@]}"; do
  read -r name expected <<< "$record"
  current="$(gh api "repos/$repo/git/ref/heads/$name" --jq '.object.sha' 2>/dev/null || true)"
  [[ -z "$current" ]] && continue
  [[ "$current" == "$expected" ]] || { echo "::error::Ref moved: $name"; exit 1; }
  gh api -X DELETE "repos/$repo/git/refs/heads/$name" --silent
  echo "Archived and retired: $name"
done

# Create a promotion PR from develop to main. This can be disallowed by the
# repository's Actions permission setting; failure is deliberately visible.
existing="$(gh pr list --repo "$repo" --head develop --base main --state open --json number --jq '.[0].number // empty')"
if [[ -z "$existing" ]]; then
  gh api -X POST "repos/$repo/pulls" \
    -f head=develop -f base=main \
    -f title="Publish academic Maxwell–Euler scope realignment" \
    -f body="Promote the academic Q1/Q2/Q3 Maxwell–Euler, Geometric Algebra and GNN research realignment merged in PR #22. Historical development heads were archived as tags before branch retirement. Review Quarto checks and approve separately before merging to main; no automatic publication is authorized." --silent
else
  echo "Existing develop-to-main promotion PR: #$existing"
fi

# Written last: if a step fails, the next push can retry safely.
gh api -X POST "repos/$repo/git/refs" -f "ref=refs/tags/$prefix/completed" -f "sha=$merge_sha" --silent
echo "One-time scope transition finished."
