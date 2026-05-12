# Cleanup policy: reproducible template pack

Updated: 2026-05-12

This folder is kept as a Ren'Py/ComfyUI asset-production template pack, not an image archive.

## Kept

- Root documentation: `README.md`, `TEMPLATE_INTENT.md`, `CURRENT_STATUS_AND_GAPS.md`, `NEXT_ASSET_WORKFLOWS.md`.
- Per-workflow `USAGE.md`.
- ComfyUI `/prompt` API templates under `api_workflows/`.
- JSON/Markdown manifests and verdict notes that record prompts, seeds, settings, PASS/FAIL criteria, and known rejected directions.
- `run_zero_memory_replay_test.py` as the executable reproducibility harness.

## Removed

- Generated PNG examples and contact sheets.
- Dark/checker/head QA image sheets.
- `test_runs/` replay outputs, history JSON, copied input PNGs, and sheet-input copies.

## Reason

The remaining files are sufficient to recreate assets from ComfyUI using the API templates and recorded settings. Removed files are reproducible outputs or intermediate evidence, not template inputs. If visual examples are needed later, rerun the relevant API templates or the zero-memory replay harness.
