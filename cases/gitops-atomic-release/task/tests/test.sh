#!/usr/bin/env bash
set -u

mkdir -p /logs/verifier
reward_file=/logs/verifier/reward.txt
echo 0 > "$reward_file"

fail() {
  echo "FAIL: $*" >&2
  echo 0 > "$reward_file"
  exit 1
}

pass() {
  echo 1 > "$reward_file"
  exit 0
}

run() {
  "$@" || fail "command failed: $*"
}

commit_for_push() {
  local repo="$1"
  local title="$2"
  local body="$3"
  local marker="${4:-}"
  rm -f "$repo/FAIL_RELEASE"
  printf '<html><body><h1>%s</h1><p>%s</p></body></html>\n' "$title" "$body" > "$repo/index.html"
  if [[ -n "$marker" ]]; then
    printf '%s\n' "$marker" > "$repo/FAIL_RELEASE"
  fi
  git -C "$repo" add -A >/dev/null
  git -C "$repo" commit -m "$title" >/dev/null
  git -C "$repo" rev-parse HEAD
}

push_expect_success() {
  local repo="$1"
  git -C "$repo" push origin HEAD:main >/tmp/gitops-push.log 2>&1 \
    || fail "expected push success; log: $(cat /tmp/gitops-push.log)"
}

push_expect_failure() {
  local repo="$1"
  if git -C "$repo" push origin HEAD:main >/tmp/gitops-push.log 2>&1; then
    fail "expected push failure"
  fi
}

site_title() {
  sed -n 's/.*<h1>\(.*\)<\/h1>.*/\1/p' /app/site/current/index.html 2>/dev/null
}

assert_current_matches() {
  local expected_commit="$1"
  local expected_title="$2"
  local state_commit
  local link_target
  state_commit="$(cat /app/state/current_release 2>/dev/null || true)"
  link_target="$(readlink /app/site/current 2>/dev/null || true)"
  [[ "$state_commit" == "$expected_commit" ]] || fail "current_release=$state_commit, expected $expected_commit"
  [[ "$link_target" == "/app/site/releases/$expected_commit" ]] || fail "site/current=$link_target, expected /app/site/releases/$expected_commit"
  [[ "$(site_title)" == "$expected_title" ]] || fail "served title '$(site_title)' != '$expected_title'"
}

run /app/bin/gitopsctl init
chmod +x /app/bin/deploy.sh /app/bin/gitopsctl /app/repo.git/hooks/post-receive
if [[ -f /app/repo.git/hooks/pre-receive ]]; then
  chmod +x /app/repo.git/hooks/pre-receive
fi

workroot="$(mktemp -d /tmp/gitops-test.XXXXXX)"
repo="$workroot/client"
run git clone /app/repo.git "$repo"
run git -C "$repo" checkout -B main
run git -C "$repo" config user.email verifier@example.invalid
run git -C "$repo" config user.name "GitOps Verifier"

first_commit="$(commit_for_push "$repo" "release-one" "first valid release")"
push_expect_success "$repo"
assert_current_matches "$first_commit" "release-one"

invalid_commit="$(commit_for_push "$repo" "broken-release" "this must not publish" "invalid")"
push_expect_failure "$repo"
assert_current_matches "$first_commit" "release-one"
grep -q "failure $invalid_commit" /app/state/audit.log || fail "missing failure audit for invalid push"

before_restart_audit_lines="$(wc -l < /app/state/audit.log)"
run /app/bin/gitopsctl restart
assert_current_matches "$first_commit" "release-one"
after_restart_audit_lines="$(wc -l < /app/state/audit.log)"
[[ "$after_restart_audit_lines" -gt "$before_restart_audit_lines" ]] || fail "restart did not append audit history"

repo_a="$workroot/client-a"
repo_b="$workroot/client-b"
run git clone /app/repo.git "$repo_a"
run git clone /app/repo.git "$repo_b"
for r in "$repo_a" "$repo_b"; do
  run git -C "$r" checkout -B main origin/main
  run git -C "$r" config user.email verifier@example.invalid
  run git -C "$r" config user.name "GitOps Verifier"
done

commit_a="$(commit_for_push "$repo_a" "concurrent-a" "parallel release a")"
commit_b="$(commit_for_push "$repo_b" "concurrent-b" "parallel release b")"

git -C "$repo_a" push origin HEAD:main >/tmp/gitops-push-a.log 2>&1 &
pid_a=$!
git -C "$repo_b" push --force origin HEAD:main >/tmp/gitops-push-b.log 2>&1 &
pid_b=$!
wait "$pid_a"
status_a=$?
wait "$pid_b"
status_b=$?
[[ "$status_a" -eq 0 || "$status_b" -eq 0 ]] || fail "both concurrent pushes failed: A=$(cat /tmp/gitops-push-a.log) B=$(cat /tmp/gitops-push-b.log)"

final_commit="$(cat /app/state/current_release)"
case "$final_commit" in
  "$commit_a")
    [[ "$status_a" -eq 0 ]] || fail "final state points at failed concurrent push A"
    expected_title="concurrent-a"
    ;;
  "$commit_b")
    [[ "$status_b" -eq 0 ]] || fail "final state points at failed concurrent push B"
    expected_title="concurrent-b"
    ;;
  *) fail "final commit $final_commit was not one of the concurrent pushes" ;;
esac
assert_current_matches "$final_commit" "$expected_title"
if [[ "$status_a" -eq 0 ]]; then
  grep -q "success $commit_a" /app/state/audit.log || fail "missing success audit for concurrent push A"
fi
if [[ "$status_b" -eq 0 ]]; then
  grep -q "success $commit_b" /app/state/audit.log || fail "missing success audit for concurrent push B"
fi

pass
