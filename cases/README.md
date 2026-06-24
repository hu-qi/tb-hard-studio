# Cases

Each case stays at `cases/<case_id>/` for its entire life. Status is recorded in `case.yaml` and `registry/tasks.csv`.

Create a case with:

```bash
make new CASE=<case_id>
```

Do not add authoring notes, evidence, or exports inside `task/`. The task directory is the canonical Harbor source tree.
