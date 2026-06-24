# Purchaser v1 Adapter

The procurement format expects a case root with `Dockerfile`, `instruction.md`, `test/`, and `tag.txt`. Harbor uses `environment/` and `tests/` inside its canonical task directory.

Run:

```bash
make export CASE=<case_id>
```

The export script performs the mapping in `mapping.yaml`, excludes private authoring and Oracle assets, writes a deterministic zip to `delivery/final/`, and stores the manifest in `cases/<case_id>/exports/purchaser-v1/`.

Do not edit either output by hand.
