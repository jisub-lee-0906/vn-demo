# AGENTS.md — RenPy ComfyUI workflow pack

This folder is a reusable workflow kit, not an image/archive dump.

## Read order

1. `WORKFLOW_INDEX.json` for machine-readable workflow/API mapping.
2. The target `NN_*/README.md`.
3. The target `NN_*/workflow_api/*.json` if that workflow has ComfyUI API templates.

## Rules

- Do not invent new ComfyUI graphs before checking the matching numbered folder.
- Executable image workflows keep API JSON in `NN_*/workflow_api/`.
- 04 and 05 are intentionally separate: 04 creates pose donors; 05 regenerates the existing character from an image reference.
- Keep prompts short. Change one variable at a time: expression, pose, outfit, weather, or story beat.
- Do not store generated PNG/contact sheets/audio dumps in this reusable pack. Save test outputs in a project-specific run folder.
- Before claiming an asset is game-ready, run artifact QA: contact sheet or RenPy screenshot, alpha/edge check, fake text/UI check for backgrounds/CG.
- Windows ComfyUI is usually `http://172.28.224.1:8000` from WSL when running. Check `/queue` before submitting and never interrupt/delete other work without user approval.

## Test command

Dry run:

```bash
python scripts/run_workflow_smoke_tests.py --endpoint http://172.28.224.1:8000
```

Execute one template per workflow:

```bash
python scripts/run_workflow_smoke_tests.py --endpoint http://172.28.224.1:8000 --execute --one-per-workflow
```
