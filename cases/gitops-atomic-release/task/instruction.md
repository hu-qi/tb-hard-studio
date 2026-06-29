# Repair the Local GitOps Release Pipeline

You are working in `/app`, which contains a deliberately broken local GitOps deployment sandbox. The sandbox has a bare Git repository at `/app/repo.git`, a post-receive hook, deployment scripts under `/app/bin/`, release state under `/app/state/`, and a static site tree under `/app/site/`.

Your task is to repair the release pipeline so that pushes to the bare repository publish the correct static site atomically and leave durable audit evidence. A successful release is a Git push whose worktree contains a valid `index.html` file with a `<h1>...</h1>` heading and does not contain a `FAIL_RELEASE` marker file. An invalid push must fail without changing the currently served site.

The repaired system must satisfy these observable behaviors:

- a valid push publishes a complete versioned release and updates `/app/site/current` only after validation succeeds;
- an invalid push preserves the last known-good release;
- concurrent pushes are serialized so that `/app/site/current`, `/app/state/current_release`, and the audit log agree on the same final release;
- restart recovery via `/app/bin/gitopsctl restart` does not lose the current site or audit history;
- `/app/state/audit.log` records durable `success` and `failure` events with commit IDs and release paths.

You may modify files under `/app`, including hooks, scripts, service-control helpers, and configuration. Keep the system local; do not depend on network access. Do not bypass Git hooks by serving a canned page, deleting validation, ignoring failed pushes, or replacing the workflow with a sleep-based race workaround. The verifier will interact with the system through Git pushes and filesystem/HTTP-like site observations, not by checking for one preferred implementation.
