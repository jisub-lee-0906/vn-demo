# Agent instructions for renpy_asset_workflows

This pack has been manually reorganized into flat semantic workflow folders. Do not assume the old numbered `01_*` to `07_*` folder layout exists.

## Required reading order

Before editing or running anything in this pack:

1. Read root `README.md`.
2. Read root `WORKFLOW_INDEX.json`.
3. Read this `AGENTS.md`.
4. Read the target workflow folder's `README.md`.
5. Inspect the target `*_workflow_api.json`.

## Current canonical folders

- `character_anchor_base`
- `expression_variations`
- `transparency_alpha`
- `background_art`
- `prop_closeup_cg`
- `outfit_variations`
- `event_cg`

The canonical API graph is located directly inside each folder as `*_workflow_api.json`.

## Do not edit canonical templates during runtime generation

For normal tests/runs:

1. Copy the canonical JSON to a runtime/sandbox file.
2. Patch the runtime copy only.
3. Submit the runtime copy to ComfyUI.
4. Keep generated images in ComfyUI output folders or explicit sandbox/output locations, not in the canonical pack.

Only modify canonical workflow JSONs or per-folder READMEs when the user explicitly asks for pack maintenance or after user-approved promotion.

## Editable fields

Use `WORKFLOW_INDEX.json` as the authoritative editable-node map. Common editable fields are:

- `CLIPTextEncode.inputs.text`
- `KSampler.inputs.seed`
- `KSampler.inputs.steps/cfg/denoise` only when the workflow notes allow it
- `LoadImage.inputs.image`
- `SaveImage.inputs.filename_prefix`
- `EmptyLatentImage.inputs.width/height` only for no-input txt2img workflows when explicitly desired

## Placeholder rules

Never submit a live ComfyUI prompt with unresolved placeholders unless the workflow explicitly documents that ComfyUI should receive them literally.

Examples that normally require runtime replacement:

- `TEMPLATE_*`
- `{헤어 길이}`
- `{감정표현}`
- `{배경 테마 및 장소}`
- `{아이템 이름 및 형태}`
- `{캐릭터 의상/특징}`

For `LoadImage.inputs.image`, verify the referenced file exists in the active ComfyUI input directory before submission.

## Validation checklist

Before reporting that pack maintenance is complete:

- All files listed in `WORKFLOW_INDEX.json` exist.
- All `*_workflow_api.json` files parse as JSON.
- No old numbered folder paths are required by the new root docs/index.
- Only the intended root files or explicitly requested files changed.
- Existing workflow folders and canonical JSONs were not modified unless the user explicitly allowed it.

Before a live ComfyUI run:

- Verify the target backend and queue status.
- Verify required custom nodes exist via `/object_info` when the graph uses custom nodes.
- Verify every runtime input image exists.
- Save the runtime-patched JSON path and output prefix.

## Reporting style

When the user will do visual QA, report concise evidence only:

- workflow used
- runtime JSON path, if any
- prompt id, if submitted
- seed
- exact output path(s)
- what the user should inspect

Do not claim image quality or production readiness without actual artifact QA.
