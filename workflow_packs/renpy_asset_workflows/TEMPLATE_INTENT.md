# Template intent: Ren'Py asset production with ComfyUI

This backup is not primarily an image archive.

The purpose is to preserve reusable, reproducible workflows so that a future session with no memory of this work can still generate Ren'Py game assets with ComfyUI.

## What must be preserved

1. Reproducible usage instructions
   - What the workflow is for
   - When to use it
   - Required input images
   - Required ComfyUI models/nodes
   - Exact positive/negative prompt patterns
   - Canvas size / sampler / scheduler / cfg / steps
   - Recommended parameter ranges
   - PASS/FAIL criteria
   - QA gates before Ren'Py promotion

2. ComfyUI API workflow JSON
   - `/prompt`-ready API JSON when possible
   - Not just screenshots or output manifests
   - Templates should be parameterized or easy to edit:
     - input image names
     - output prefix
     - seed
     - denoise
     - IPAdapter weight
     - prompt text

3. Reproducibility notes
   - Active endpoint pattern from WSL: Windows gateway port 8000
   - Queue safety rules for shared ComfyUI
   - Node/model names that actually worked
   - Known failed directions and why they were rejected

4. QA templates
   - Contact-sheet pattern
   - Dark/checker alpha QA pattern
   - Ren'Py screen-fit QA checklist
   - Sprite set consistency checklist
   - Background + character integration checklist

## What is secondary

Image PNG files are useful as examples and QA references, but they are not the main reason this folder exists.

If space cleanup is needed later, keep:
- `USAGE.md`
- `TEMPLATE_INTENT.md`
- `CURRENT_STATUS_AND_GAPS.md`
- `api_workflows/*.json`
- manifests with prompt/seed/settings
- representative contact/QA sheets only if needed to understand PASS/FAIL

The important deliverable is a reusable Ren'Py asset-production template pack.

## Current template coverage

Completed / documented:
- 01 character anchor/source generation usage
- 02 toonout transparency/alpha usage
- 03 expression IPAdapter img2img usage
- 04 text-only pose donor/source generation usage
- 05 pose image-reference regeneration API templates and usage

API template coverage:
- 01 now has replayable txt2img character-anchor `/prompt` API JSON templates (3 files).
- 02 now has replayable `BiRefNet_toonout` alpha sweep `/prompt` API JSON templates (5 files).
- 03 now has replayable IPAdapter img2img expression-source and selected expression-alpha `/prompt` API JSON templates (12 files).
- 04 now has replayable text-only pose-source and selected pose-alpha `/prompt` API JSON templates (12 files).
- 05 has replayable pose ref-generation and alpha example `/prompt` API JSON templates.

See `api_workflows/README.md` and `api_workflows/API_TEMPLATE_INDEX.json`.

## Next template work

The 01-05 character/sprite workflow chain is now covered by API templates. Remaining template work should move beyond the current character sprite chain:

1. Background production workflow.
2. Ren'Py screen-fit QA workflow.
3. Semantic asset promotion workflow.
4. Sprite-set consistency QA workflow.
5. Character-on-background integration QA workflow.
6. UI/dialogue visual workflow.
7. Event CG workflow.
8. Optional motion workflow: LivePortrait/AnimateDiff/WebM only after runtime readiness and Ren'Py playback tests.

The background and Ren'Py integration workflows are the next required missing templates for VN production.
