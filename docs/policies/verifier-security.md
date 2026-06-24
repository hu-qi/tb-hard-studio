# Verifier Security Policy

## Threat model

Assume the solver can read and modify everything in its container, create persistent processes, inspect file names and image layers, alter writable startup wrappers, hardcode visible samples, and exploit shared verification state.

## Required review attempts

The red-team review must attempt to:

1. Delete, bypass, or stub core functionality.
2. Hardcode visible sample outputs or parse public tests.
3. Replace entrypoints, wrappers, PATH tools, or environment variables.
4. Read Docker layers, Git history, comments, shell history, caches, mounted files, and leftover processes.
5. Emit superficially valid artifacts without satisfying the actual requirement.
6. Abuse network access, service accounts, shared volumes, sidecars, or writable verifier state.
7. Tamper with test scripts or grading dependencies in shared verifier mode.

## Grading rules

- Grade observable behavior, protocol/state correctness, output correctness, or measurable performance.
- Do not require one preferred source layout or command sequence.
- Each material acceptance criterion needs direct coverage or a documented composite test.
- Treat solver-produced artifacts as untrusted.
- Use separate verifier mode when a credible shared-mode attack would compromise score integrity.

## Release blocker

Any credible bypass that yields reward without completing the intended task is P0/P1 and blocks release until fixed and retested.
