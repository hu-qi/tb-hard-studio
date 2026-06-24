#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
warn=0

ok() { printf 'PASS: %s\n' "$*"; }
warning() { printf 'WARN: %s\n' "$*"; warn=$((warn + 1)); }
error() { printf 'ERROR: %s\n' "$*"; fail=$((fail + 1)); }

if command -v python3 >/dev/null 2>&1; then
  version="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
  python3 - <<'PY' || exit_code=$?
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
  if [[ "${exit_code:-0}" -eq 0 ]]; then ok "python3 $version"; else error "Python >= 3.11 required"; fi
else
  error "python3 not found"
fi

for command in git make; do
  if command -v "$command" >/dev/null 2>&1; then ok "$command available"; else error "$command not found"; fi
done

if command -v harbor >/dev/null 2>&1; then
  ok "harbor $(harbor --version 2>/dev/null || true)"
else
  warning "harbor not installed; install with: uv tool install harbor"
fi

if command -v docker >/dev/null 2>&1; then
  ok "docker available"
else
  warning "docker not found; local Harbor Docker runs will not work"
fi

if python3 scripts/sync_skills.py --check; then
  ok "skill projections synchronized"
else
  error "skill projections out of sync; run python3 scripts/sync_skills.py"
fi

if python3 scripts/validate_case.py --all --deep; then
  ok "case structural checks completed"
else
  error "case structural checks failed"
fi

printf 'SUMMARY: errors=%s warnings=%s\n' "$fail" "$warn"
[[ "$fail" -eq 0 ]]
