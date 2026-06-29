#!/usr/bin/env bash
set -euo pipefail

cat > /app/bin/deploy.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

commit="${1:?commit required}"
repo="/app/repo.git"
state="/app/state"
site="/app/site"
releases="$site/releases"
lock="$state/deploy.lock"
work="/app/tmp/work-$commit"
staged="/app/tmp/release-$commit"
release="$releases/$commit"
audit="$state/audit.log"

mkdir -p "$state" "$releases" /app/tmp

exec 9>"$lock"
flock 9

record() {
  printf '%s %s %s\n' "$1" "$commit" "$2" >> "$audit"
}

rm -rf "$work" "$staged"
mkdir -p "$work" "$staged"

if ! git --work-tree="$work" --git-dir="$repo" checkout -f "$commit" >/dev/null 2>&1; then
  record failure checkout
  rm -rf "$work" "$staged"
  exit 1
fi

if [[ -f "$work/FAIL_RELEASE" ]]; then
  record failure marker
  rm -rf "$work" "$staged"
  exit 1
fi

if [[ ! -f "$work/index.html" ]] || ! grep -qi '<h1>' "$work/index.html"; then
  record failure validation
  rm -rf "$work" "$staged"
  exit 1
fi

cp -R "$work"/. "$staged"/
rm -rf "$release"
mv "$staged" "$release"
ln -sfn "$release" "$site/current.next"
mv -Tf "$site/current.next" "$site/current"
printf '%s\n' "$commit" > "$state/current_release.tmp"
mv -f "$state/current_release.tmp" "$state/current_release"
record success "$release"
rm -rf "$work"
EOF

cat > /app/bin/gitopsctl <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  init)
    mkdir -p /app/site/releases /app/state /app/tmp
    if [[ ! -e /app/site/current ]]; then
      mkdir -p /app/site/releases/bootstrap
      cat > /app/site/releases/bootstrap/index.html <<'HTML'
<html><body><h1>bootstrap</h1></body></html>
HTML
      ln -sfn /app/site/releases/bootstrap /app/site/current
      printf 'bootstrap\n' > /app/state/current_release
      printf 'success bootstrap /app/site/releases/bootstrap\n' >> /app/state/audit.log
    fi
    ;;
  restart)
    mkdir -p /app/site/releases /app/state /app/tmp
    current="$(cat /app/state/current_release 2>/dev/null || true)"
    if [[ -n "$current" && -d "/app/site/releases/$current" ]]; then
      ln -sfn "/app/site/releases/$current" /app/site/current
      printf 'restart %s /app/site/releases/%s\n' "$current" "$current" >> /app/state/audit.log
    else
      printf 'restart failure missing-current\n' >> /app/state/audit.log
      exit 1
    fi
    ;;
  status)
    current_value="$(cat /app/state/current_release 2>/dev/null || printf unknown)"
    printf 'current=%s\n' "$current_value"
    readlink /app/site/current 2>/dev/null || true
    ;;
  *)
    echo "usage: gitopsctl {init|restart|status}" >&2
    exit 2
    ;;
esac
EOF

cat > /app/repo.git/hooks/pre-receive <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

audit="/app/state/audit.log"
mkdir -p /app/state

while read -r old new ref; do
  [[ "$ref" == "refs/heads/main" ]] || continue
  [[ "$new" =~ ^0+$ ]] && continue

  if git --git-dir=/app/repo.git cat-file -e "$new:FAIL_RELEASE" 2>/dev/null; then
    printf 'failure %s marker\n' "$new" >> "$audit"
    exit 1
  fi

  html="$(git --git-dir=/app/repo.git show "$new:index.html" 2>/dev/null || true)"
  if [[ -z "$html" ]] || ! grep -qi '<h1>' <<<"$html"; then
    printf 'failure %s validation\n' "$new" >> "$audit"
    exit 1
  fi
done
EOF

chmod +x /app/bin/deploy.sh /app/bin/gitopsctl /app/repo.git/hooks/pre-receive /app/repo.git/hooks/post-receive
