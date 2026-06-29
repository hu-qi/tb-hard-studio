#!/usr/bin/env bash
set -euo pipefail

commit="${1:?commit required}"
repo="/app/repo.git"
state="/app/state"
site="/app/site"
release="$site/releases/$commit"
work="/app/tmp/work-$commit"

rm -rf "$work" "$release"
mkdir -p "$work" "$release" "$state"

# Broken behavior: the served release is advanced before validation and before
# all files are copied, making failed and concurrent releases observable.
echo "$commit" > "$state/current_release"
ln -sfn "$release" "$site/current"

git --work-tree="$work" --git-dir="$repo" checkout -f "$commit" >/dev/null
cp -R "$work"/. "$release"/

if [[ -f "$work/FAIL_RELEASE" ]]; then
  echo "failure $commit $release" > "$state/audit.log"
  rm -rf "$work"
  exit 1
fi

if ! grep -qi '<h1>' "$work/index.html" 2>/dev/null; then
  echo "failure $commit $release" > "$state/audit.log"
  rm -rf "$work"
  exit 1
fi

echo "success $commit $release" > "$state/audit.log"
rm -rf "$work"
