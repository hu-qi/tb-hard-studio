# Harbor Rollout and Trajectory Evidence Protocol

This repository uses Harbor jobs, trials, verifier logs, and Agent Trajectory Interchange Format (ATIF) compatible records where available. Refer to `docs/policies/calibration-protocol.md` and `tooling/calibration-protocol.v1.yaml` for the current execution protocol.

## Evidence tree

```text
evidence/<case_id>/
├── oracle/<run_id>/
├── redteam/
├── calibration/
│   ├── aggregate.csv
│   ├── report.md
│   └── runs/<run_id>/
└── release/
```

For each run record: case ID, immutable task revision, Harbor version, provider, agent and model/version, command, timeout, network policy, start/end time, wall-clock duration, reward, job/trial reference, artifact/log locations, and a one-sentence outcome label.

Raw trajectories may contain proprietary prompts or model output. Keep them private. Export only scrubbed summaries unless the purchaser explicitly requires raw traces.
