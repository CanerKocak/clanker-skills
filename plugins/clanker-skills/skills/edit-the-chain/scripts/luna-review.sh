#!/usr/bin/env bash
# Bind three evidence-diverse Codex reviews to one immutable git candidate.
set -euo pipefail

usage() {
  printf '%s\n' \
    'usage: luna-review.sh --brief <brief.md> --base <ref> [--out-dir <dir>]' \
    'environment: EDIT_CHAIN_REPO, EDIT_CHAIN_REVIEW_MODEL, CODEX_BIN'
}

brief=''
base_ref=''
outdir="/tmp/codex-review-edit-the-chain-$$"

while (( $# > 0 )); do
  case "$1" in
    --brief)
      brief="${2:-}"
      shift 2
      ;;
    --base)
      base_ref="${2:-}"
      shift 2
      ;;
    --out-dir)
      outdir="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$brief" || -z "$base_ref" ]]; then
  usage >&2
  exit 2
fi
if [[ ! -f "$brief" ]]; then
  echo "brief not found: $brief" >&2
  exit 1
fi

codex_bin="${CODEX_BIN:-codex}"
model="${EDIT_CHAIN_REVIEW_MODEL:-gpt-5.6-luna}"
repo_hint="${EDIT_CHAIN_REPO:-$PWD}"

for dependency in git jq shasum "$codex_bin"; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    echo "required command not found: $dependency" >&2
    exit 1
  fi
done

repo_root="$(git -C "$repo_hint" rev-parse --show-toplevel)"
base_sha="$(git -C "$repo_root" rev-parse --verify "${base_ref}^{commit}")"
head_sha="$(git -C "$repo_root" rev-parse --verify 'HEAD^{commit}')"
head_tree_sha="$(git -C "$repo_root" rev-parse --verify 'HEAD^{tree}')"
merge_base_sha="$(git -C "$repo_root" merge-base "$base_sha" "$head_sha")"

unavailable_submodules="$(
  git -C "$repo_root" submodule status --recursive \
    | awk 'substr($0, 1, 1) == "-" || substr($0, 1, 1) == "U" { print $2 }'
)"
if [[ -n "$unavailable_submodules" ]]; then
  echo 'uninitialized or conflicted submodules cannot be reviewed:' >&2
  printf '%s\n' "$unavailable_submodules" >&2
  exit 1
fi

dirty_submodules="$(
  git -C "$repo_root" submodule foreach --recursive --quiet '
    state="$(git status --porcelain=v1 --untracked-files=all)"
    if [ -n "$state" ]; then
      printf "%s\n" "$sm_path"
    fi
  '
)"
if [[ -n "$dirty_submodules" ]]; then
  echo 'dirty submodules cannot be bound by the parent candidate manifest:' >&2
  printf '%s\n' "$dirty_submodules" >&2
  echo 'review each dirty nested repository separately before the parent review' >&2
  exit 1
fi

brief="$(cd "$(dirname "$brief")" && pwd -P)/$(basename "$brief")"
case "$brief" in
  "$repo_root"/*)
    echo "brief must be outside the reviewed repository: $brief" >&2
    exit 1
    ;;
esac

outdir_parent="$(dirname "$outdir")"
if [[ ! -d "$outdir_parent" ]]; then
  echo "out-dir parent does not exist: $outdir_parent" >&2
  exit 1
fi
outdir="$(cd "$outdir_parent" && pwd -P)/$(basename "$outdir")"
if [[ -e "$outdir" || -L "$outdir" ]]; then
  if [[ ! -d "$outdir" ]]; then
    echo "out-dir exists and is not a directory: $outdir" >&2
    exit 1
  fi
  outdir="$(cd "$outdir" && pwd -P)"
fi
case "$outdir/" in
  "$repo_root/"*)
    echo "out-dir must be outside the reviewed repository: $outdir" >&2
    exit 1
    ;;
esac
mkdir -p "$outdir"
if [[ -n "$(find "$outdir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "out-dir must be empty: $outdir" >&2
  exit 1
fi

hash_file() {
  shasum -a 256 "$1" | awk '{print $1}'
}

snapshot_candidate() {
  local destination="$1"
  local status_hash committed_hash staged_hash unstaged_hash untracked_hash submodule_hash
  mkdir -p "$destination"

  git -C "$repo_root" status --porcelain=v1 -z --untracked-files=all \
    >"$destination/status.z"
  git -C "$repo_root" diff --binary "$merge_base_sha" HEAD \
    >"$destination/committed.patch"
  git -C "$repo_root" diff --binary --cached HEAD \
    >"$destination/staged.patch"
  git -C "$repo_root" diff --binary \
    >"$destination/unstaged.patch"

  : >"$destination/untracked.tsv"
  while IFS= read -r -d '' path; do
    printf '%s\t%s\n' "$(git -C "$repo_root" hash-object -- "$path")" "$path" \
      >>"$destination/untracked.tsv"
  done < <(git -C "$repo_root" ls-files --others --exclude-standard -z | LC_ALL=C sort -z)
  git -C "$repo_root" submodule status --recursive >"$destination/submodules.txt"

  {
    git -C "$repo_root" diff --name-only "$merge_base_sha" HEAD
    git -C "$repo_root" diff --name-only --cached HEAD
    git -C "$repo_root" diff --name-only
    git -C "$repo_root" ls-files --others --exclude-standard
  } | LC_ALL=C sort -u >"$destination/changed-files.txt"

  status_hash="$(hash_file "$destination/status.z")"
  committed_hash="$(hash_file "$destination/committed.patch")"
  staged_hash="$(hash_file "$destination/staged.patch")"
  unstaged_hash="$(hash_file "$destination/unstaged.patch")"
  untracked_hash="$(hash_file "$destination/untracked.tsv")"
  submodule_hash="$(hash_file "$destination/submodules.txt")"

  printf '%s\n' \
    "$repo_root" "$base_sha" "$merge_base_sha" "$head_sha" "$head_tree_sha" \
    "$status_hash" "$committed_hash" "$staged_hash" "$unstaged_hash" "$untracked_hash" \
    "$submodule_hash" \
    | shasum -a 256 | awk '{print $1}' >"$destination/fingerprint.txt"
}

snapshot_candidate "$outdir/candidate"
candidate_fingerprint="$(<"$outdir/candidate/fingerprint.txt")"
brief_sha256="$(hash_file "$brief")"
changed_files="$(jq -Rsc 'split("\n") | map(select(length > 0))' "$outdir/candidate/changed-files.txt")"
dirty=false
if [[ -s "$outdir/candidate/status.z" ]]; then
  dirty=true
fi

jq -n \
  --arg captured_at "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --arg repo_root "$repo_root" \
  --arg base_ref "$base_ref" \
  --arg base_sha "$base_sha" \
  --arg merge_base_sha "$merge_base_sha" \
  --arg head_sha "$head_sha" \
  --arg head_tree_sha "$head_tree_sha" \
  --arg fingerprint "$candidate_fingerprint" \
  --arg brief_sha256 "$brief_sha256" \
  --arg status_sha256 "$(hash_file "$outdir/candidate/status.z")" \
  --arg committed_diff_sha256 "$(hash_file "$outdir/candidate/committed.patch")" \
  --arg staged_diff_sha256 "$(hash_file "$outdir/candidate/staged.patch")" \
  --arg unstaged_diff_sha256 "$(hash_file "$outdir/candidate/unstaged.patch")" \
  --arg untracked_sha256 "$(hash_file "$outdir/candidate/untracked.tsv")" \
  --arg submodules_sha256 "$(hash_file "$outdir/candidate/submodules.txt")" \
  --argjson dirty "$dirty" \
  --argjson changed_files "$changed_files" \
  '{
    captured_at: $captured_at,
    repo_root: $repo_root,
    base_ref: $base_ref,
    base_sha: $base_sha,
    merge_base_sha: $merge_base_sha,
    head_sha: $head_sha,
    head_tree_sha: $head_tree_sha,
    dirty: $dirty,
    status_sha256: $status_sha256,
    committed_diff_sha256: $committed_diff_sha256,
    staged_diff_sha256: $staged_diff_sha256,
    unstaged_diff_sha256: $unstaged_diff_sha256,
    untracked_sha256: $untracked_sha256,
    submodules_sha256: $submodules_sha256,
    fingerprint: $fingerprint,
    brief_sha256: $brief_sha256,
    changed_files: $changed_files
  }' >"$outdir/manifest.json"

manifest_text="$(<"$outdir/manifest.json")"
brief_text="$(<"$brief")"

roles=(blind-contract runtime-boundary evidence-audit)
role_prompts=(
  'Reconstruct the intended behavior from the user contract and canonical sources. Do not assume prior design decisions are correct. Find reachable counterexamples in the exact candidate.'
  'Falsify code-to-runtime boundaries: database/API behavior, lifecycle states, retries, exact-once identity, units, decimal scaling, valuation time, permissions, and stale or partial data. Separate synthetic logic checks from deployed-boundary evidence.'
  'Audit the acceptance evidence itself. Look for stale or proxy evidence, copied expressions, fixture-only proof, wrong repository/base/database/role, missing candidate binding, or a conclusion broader than the observed artifact.'
)

pids=()
for index in 0 1 2; do
  role="${roles[index]}"
  output="$outdir/$((index + 1))-$role.md"
  log="$outdir/$((index + 1))-$role.log"
  prompt="$brief_text

# Exact candidate manifest
$manifest_text

# Assigned review mode
${role_prompts[index]}

# Output contract
The first line must be exactly: Candidate: $candidate_fingerprint / Brief: $brief_sha256
Report only evidence-backed findings that can change the decision. For each,
name the target deployment and rollout state, the supported producer or
security-relevant untrusted input, source evidence, concrete harm, and whether
this candidate introduced or worsened it. Legacy or migration claims must prove
the old representation shipped to the target and can remain at cutover. Do not
turn every technically constructible custom client input into a product-support
requirement. Propose ACTIONABLE, DECLINED, FOLLOW-UP, or OPEN; this is an
evidence lead, not authorization to edit. State VERIFIED, PARTIAL, or OPEN for
the supporting evidence. Do not mutate files."

  (
    "$codex_bin" exec \
      -C "$repo_root" \
      -m "$model" \
      -c model_reasoning_effort="max" \
      -s read-only \
      --ephemeral \
      --color never \
      -o "$output" \
      - <<<"$prompt"
  ) >"$log" 2>&1 &
  pids+=("$!")
done

failed=0
for index in 0 1 2; do
  role="${roles[index]}"
  output="$outdir/$((index + 1))-$role.md"
  log="$outdir/$((index + 1))-$role.log"
  if ! wait "${pids[index]}"; then
    echo "review $role failed; see $log" >&2
    failed=1
    continue
  fi
  if [[ ! -s "$output" ]]; then
    echo "review $role produced no final response; see $log" >&2
    failed=1
    continue
  fi
  first_line="$(sed -n '1p' "$output")"
  if [[ "$first_line" != "Candidate: $candidate_fingerprint / Brief: $brief_sha256" ]]; then
    echo "review $role did not attest the candidate and brief fingerprints on its first line; see $output" >&2
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi

current_head_sha="$(git -C "$repo_root" rev-parse --verify 'HEAD^{commit}')"
current_head_tree_sha="$(git -C "$repo_root" rev-parse --verify 'HEAD^{tree}')"
if [[ "$current_head_sha" != "$head_sha" || "$current_head_tree_sha" != "$head_tree_sha" ]]; then
  echo 'candidate commit or tree changed during review' >&2
  exit 1
fi

snapshot_candidate "$outdir/post-review-candidate"
post_fingerprint="$(<"$outdir/post-review-candidate/fingerprint.txt")"
if [[ "$post_fingerprint" != "$candidate_fingerprint" ]]; then
  echo 'candidate working state changed during review; outputs are stale' >&2
  exit 1
fi

printf '%s\n' \
  "$outdir/manifest.json" \
  "$outdir/1-blind-contract.md" \
  "$outdir/2-runtime-boundary.md" \
  "$outdir/3-evidence-audit.md"
