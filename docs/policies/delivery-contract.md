# Delivery Contract

## Canonical source

The only editable benchmark source is `cases/<case_id>/task/`. All purchaser deliverables are generated from it.

## Purchaser v1 package

The generated zip contains one root folder `<case_id>/` with:

```text
Dockerfile
instruction.md
tag.txt
test/
```

The package excludes:

- `solution/` and Oracle-private helpers;
- authoring Skills, Subagents, plugin configuration, documentation, and templates;
- design briefs, reviews, trajectories, calibration reports, credentials, caches, and source-control metadata.

A sidecar manifest is retained outside the package and records the canonical task checksum, exported files, excluded paths, build timestamp, and script version.

## Freeze rule

Run `make release-check CASE=<case_id>` only after the case status is `validated`. Do not edit the package after generation. Any task change requires a new Oracle run, targeted calibration rerun, audit, and export.
