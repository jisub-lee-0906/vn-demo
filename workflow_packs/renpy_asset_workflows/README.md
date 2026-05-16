# Ren'Py VN Asset ComfyUI Workflow Pack

This folder is the repo-local source of truth for reusable ComfyUI API workflows used to create visual-novel / dating-sim assets for `vn-demo`.

Windows path:
`\\wsl.localhost\Ubuntu-24.04\home\jisub-lee\workspace\vn-demo\workflow_packs\renpy_asset_workflows`

WSL path:
`/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows`

## Current structure

The current pack uses flat, named workflow folders. It no longer uses the old numbered `01_*`, `02_*`, `03_*` folder contract.

Each workflow folder should contain:

- `README.md` — human/agent operating notes for that workflow.
- `*_workflow_api.json` — the canonical ComfyUI API graph template.

Current canonical folders:

| Folder | Purpose | Main API JSON |
|---|---|---|
| `character_anchor_base` | Generate base character/source images. | `character_anchor_base/character_anchor_base_workflow_api.json` |
| `expression_variations` | Generate expression variants from a character source image using face/mask inpaint/composite. | `expression_variations/expression_variations_workflow_api.json` |
| `transparency_alpha` | Convert a source character image to transparent PNG / alpha output. | `transparency_alpha/transparency_alpha_workflow_api.json` |
| `background_art` | Generate 16:9 VN background art. | `background_art/background_art_workflow_api.json` |
| `prop_closeup_cg` | Generate 16:9 close-up prop / clue / cut-in CG images. | `prop_closeup_cg/prop_closeup_cg_workflow_api.json` |
| `outfit_variations` | Generate outfit/costume variants from a featureless or source character image. | `outfit_variations/outfit_variations_workflow_api.json` |
| `event_cg` | Generate 16:9 character event CG from character and scene references. | `event_cg/event_cg_workflow_api.json` |

## Recommended agent entrypoint

When an AI agent starts work in this pack:

1. Read this `README.md`.
2. Read `WORKFLOW_INDEX.json`.
3. Read `AGENTS.md`.
4. Read the target workflow folder's `README.md`.
5. Load the target `*_workflow_api.json` and runtime-patch only the editable fields listed in the index.

## Workflow role split

A typical asset flow is:

1. `character_anchor_base` — produce an opaque base/source character.
2. `transparency_alpha` — convert an accepted character source to transparent PNG when needed.
3. `expression_variations` — create expression variants from a source character image.
4. `outfit_variations` — create outfit variants, especially from featureless/source character images.
5. `background_art` — create 16:9 scene backgrounds.
6. `prop_closeup_cg` — create separate 16:9 prop/clue cut-ins for Ren'Py staging.
7. `event_cg` — create full 16:9 event CGs using character and scene references.

The folders are reusable tools, not a mandatory linear pipeline. Choose the smallest workflow that matches the asset being created.

## Canonical JSON handling

Do not overwrite canonical API JSONs during normal generation.

Preferred pattern:

1. Deep-copy the canonical `*_workflow_api.json` into a temporary runtime/sandbox path outside the canonical workflow folder.
2. Patch only the intended runtime fields: prompts, seed, input image names, output prefix, and any explicitly approved parameters.
3. Submit the runtime copy to ComfyUI.
4. Save generated outputs under ComfyUI output folders, not inside this reusable pack.
5. Promote changes back into canonical JSON only after explicit user QA/approval.

## Placeholders and input files

Some templates intentionally contain placeholders such as:

- `TEMPLATE_character_anchor_source.png`
- `TEMPLATE_source_image.png`
- `TEMPLATE_featureless_mannequin_source.png`
- `TEMPLATE_character_reference.png`
- `TEMPLATE_event_scene_reference.png`
- `TEMPLATE_*` output prefix fragments
- Korean prompt placeholders such as `{감정표현}` or `{배경 테마 및 장소}`

Before live ComfyUI submission, agents must replace these with real ComfyUI `input/` filenames, prompt text, seeds, and output prefixes.

## Quality and promotion rule

A workflow being runnable is not the same as being production-approved.

Only call an output canonical/approved after the user or agent has checked the actual generated artifact/contact sheet/Ren'Py screenshot. If the user says they will visually QA the image themselves, report only the prompt id, seed, runtime JSON path, and output path; do not invent quality claims.

## Current known caution

- The current folder names are flat semantic names, not numbered names. Old references to `01_*` through `07_*` may be stale.
- `background_art` and `prop_closeup_cg` are 16:9 txt2img-style workflows with no image input.
- `expression_variations`, `transparency_alpha`, `outfit_variations`, and `event_cg` require runtime image inputs.
- Some README prompt text is human-facing and may not exactly match the canonical JSON prompt. Treat `WORKFLOW_INDEX.json` plus the actual JSON as execution source of truth.
