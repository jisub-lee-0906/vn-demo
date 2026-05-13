# 00 experiment — 04 no `thick_outline` retest

Date: 2026-05-13
Status: executed; `thick_outline` was identified as the main white/sticker rim contaminant in 04 pose source outputs.

## Root cause

The promoted 04 graph itself matched the passed sandbox graph after normalizing editable values. The missing piece was prompt QA:

- Old/passed evidence existed in `00_experiment_sandbox` and ComfyUI output, but the old pass was judged at contact-sheet scale.
- Full-size source inspection showed the old 04 pass already had a generated bright exterior outline/sticker rim.
- 02 alpha preserved/remapped that generated rim; 02 was not the root cause.
- Removing only `thick_outline` from the 04 positive prompt reduced the bright exterior rim while keeping pose and identity usable.

## Current rejected 04 positive style block

```text
thick_outline, clean_lineart, anime_coloring, grey_background
```

Reject reason: `thick_outline` encourages an exterior sticker-like white/bright border, especially around hair/body. This contaminates 02 alpha on dark backgrounds.

## New 04 positive style block

```text
clean_lineart, anime_coloring, grey_background
```

## Workflow chain tested

```text
04 pose source
-> 02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json
-> RGBA alpha PNG
```

ComfyUI endpoint:

```text
http://172.28.224.1:8000
```

## Evidence

Initial current canonical retest with `thick_outline`:

```text
04 prompt_id: 14bf013f-c35f-4fcc-b762-8bdebf2e5e67
02 prompt_id: 87c27d61-9fd9-4dc9-b8fb-95c8cfb5ba3b
04 source: ComfyUI/output/hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_src_00001_.png
02 alpha: ComfyUI/output/hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_alpha_b1_ref1_00001_.png
manifest: ComfyUI/output/hermes_vn_chain_retest_20260513/manifest_current04_to_02.json
```

Single-variable candidate retest without `thick_outline`:

```text
04 prompt_id: 709d31e5-82f6-4f7c-bb24-82f2af4a7c95
02 prompt_id: ac0c86db-2fec-45c1-b18d-98926f42c50c
04 source: ComfyUI/output/hermes_vn_chain_retest_20260513/candidate_no_thick_outline_src_00001_.png
02 alpha: ComfyUI/output/hermes_vn_chain_retest_20260513/candidate_no_thick_outline_alpha_b1_ref1_00001_.png
manifest: ComfyUI/output/hermes_vn_chain_retest_20260513/manifest_candidate_no_thick_outline.json
```

Stable preset batch retest without `thick_outline`:

```text
arms_crossed 04 prompt_id: 317c9a00-6ed0-4f3e-a761-13cd020d606f
arms_crossed 02 prompt_id: fc64204f-1da1-489e-996a-f3736df42cd3
arms_crossed alpha: ComfyUI/output/hermes_vn_chain_retest_20260513/no_thick_arms_crossed_alpha_b1_ref1_00001_.png

hand_chest 04 prompt_id: 1247e805-533b-48a8-9319-880e847cdbdd
hand_chest 02 prompt_id: 8a638894-bddb-45ec-8272-8bf73b4071b3
hand_chest alpha: ComfyUI/output/hermes_vn_chain_retest_20260513/no_thick_hand_chest_alpha_b1_ref1_00001_.png

manifest: ComfyUI/output/hermes_vn_chain_retest_20260513/manifest_no_thick_stable_batch.json
```

PNG verification:

```text
both stable alpha outputs are PNG 1152x1536 8-bit RGBA
```

## QA result

- `arms_crossed`: pass with minor caveat. Pose readable; silver-bob identity retained; no large white sticker rim. Minor dark antialias edge remains on dark background, acceptable compared with previous thick white rim.
- `hand_chest`: pass with minor caveat. Pose readable; identity retained; no large white sticker rim. Minor dark antialias edge remains.

## Decision

Update numbered 04 canonical prompt skeleton and README to remove `thick_outline` from the default positive style block.

Keep 02 unchanged. The alpha workflow is technically correct and was only preserving upstream 04 rim contamination.

Do not declare the separate 03 expression issue solved by this test. 03 still needs its own expression-strength retest after 04 source is fixed.
