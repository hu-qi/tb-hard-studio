# Calibration Policy

Follow the machine-readable baseline in `tooling/calibration-protocol.v1.yaml`.

## What calibration must establish

Calibration demonstrates that the task is:

- solvable by a competent expert through the public contract;
- difficult for substantive technical reasons;
- stable under repeated execution;
- not secretly easy through a shortcut or leaked asset;
- within the agreed pass-rate/time/trajectory target for the selected agents.

## Failure taxonomy

Classify every failure as one or more of:

- incorrect technical reasoning;
- partial implementation with a real remaining defect;
- investigation/search failure;
- authentic timeout;
- artificial time sink;
- ambiguous instruction;
- environment/setup failure;
- verifier defect;
- answer leakage or shortcut;
- agent-tool incompatibility unrelated to intended capability.

Only authentic technical failures and authentic timeouts support a hard-difficulty claim. A low pass rate by itself never does.

## Evidence location

Use `evidence/<case_id>/` and retain the exact task revision, Harbor version, agent/model configuration, command, runtime, reward, job/trial reference, and scrubbed trajectory summary. Raw model logs remain private unless the purchaser explicitly requests them.
