# Harbor and Terminal-Bench 2 Alignment

## Canonical runtime contract

The canonical runnable source for every tb-hard case is `cases/<case_id>/task/`.

```text
instruction.md
task.toml
environment/
solution/
tests/
```

Harbor initializes this shape with `harbor init --task "<org>/<name>"` and runs a local task with `harbor run -p "<path/to/task>" -a "<agent>" -m "<model>"`.

Harbor treats `solution/` as optional, but tb-hard makes it mandatory because each task must carry a reproducible Oracle proof of solvability. Harbor copies `solution/` to `/solution/` only when the Oracle agent runs, and copies `tests/` to `/tests/` for verification. The solver-facing environment must not contain either folder.

## task.toml baseline

Use a Harbor-supported schema version. The repository baseline is `1.3`; change `tooling/versions.env` only after checking the installed Harbor release notes and official task documentation.

Every task must explicitly set:

- `[task]`: name, description, authors, keywords;
- `[metadata]`: category, difficulty explanation, tags, and human time estimates;
- `[agent].timeout_sec` and `[verifier].timeout_sec`;
- `[environment].network_mode`, build timeout, and measured resource limits;
- `artifacts` when a separate verifier must receive solver outputs.

Default task network policy is `no-network`. Do not use `public` simply to make package installation convenient; prebuild required dependencies or use a constrained allowlist when external access is part of the evaluated capability.

## Reward contract

`tests/test.sh` is the verifier entrypoint. It must write one of:

- `/logs/verifier/reward.txt` with one numeric reward; or
- `/logs/verifier/reward.json` with numeric metrics.

The test script must create a reward file on both success and failure paths. Tests should use absolute paths, validate behavior rather than source layout, and remain deterministic under the declared resource and network policy.

## Shared vs separate verifier

Harbor defaults to a shared verifier, which runs in the same container state the solver controlled. Use a separate verifier when the grading code must remain hidden, grading needs a clean image, task artifacts are untrusted, or sidecar evidence is needed.

For a separate verifier:

```toml
[verifier]
environment_mode = "separate"

[verifier.environment]
network_mode = "no-network"
```

Only `/logs/artifacts/` and explicitly declared `artifacts` move from the agent environment to the verifier. Treat transferred solver files as untrusted. For multi-service tasks, use sidecar artifact entries and `[[verifier.collect]]` hooks to snapshot trusted service evidence before verification.

## TB2 alignment

Use Terminal-Bench 2 as a pattern library for realistic task shape, multi-step verification, container boundaries, and Hard-level reasoning composition. Do not copy task text, tests, solutions, hidden fixtures, or proprietary assets.

A task qualifies as tb-hard only when it combines at least three substantive difficulty dimensions and produces authentic exploration/debugging behavior under the agreed calibration protocol.

## Purchaser export

The purchaser-facing directory is generated from the canonical Harbor task by `scripts/export_purchaser.py`. It maps:

| Canonical Harbor source | Purchaser v1 export |
|---|---|
| `task/environment/Dockerfile` | `Dockerfile` |
| `task/instruction.md` | `instruction.md` |
| `task/tests/` | `test/` |
| `case.yaml.purchaser_tag` | `tag.txt` |
| `task/solution/` | excluded by default |

Do not manually maintain two task implementations.
