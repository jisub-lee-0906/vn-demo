# 02 alpha — white edge / halo diagnosis

Date: 2026-05-13
Status: diagnosed; partially improvable, but not fully removable without source-side or postprocess tradeoffs.

## User report

The user noticed transparency looked worse than expected and suspected the background prompt conflict (`simple_background, grey_background, dark_background`). They also observed a white line around the character exterior after alpha.

## Background prompt finding

Background conflicts can make the source background darker/less neutral and can make alpha QA harder, but the visible white/light rim is not mainly caused by the text prompt's background tags.

04 same-seed background sweep selected:

```text
grey_background
```

as the only positive background tag. This was propagated to 01/03/04 canonical prompts.

## Alpha workflow inspected

Canonical 02 workflow:

```text
02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json
```

Key node:

```text
node 2: BiRefNetRMBG
model: BiRefNet_toonout
mask_blur: 1
mask_offset: 0
invert_output: false
refine_foreground: true
background: Alpha
```

The likely source of a visible white/light fringe is the combination of:

1. semi-transparent edge pixels created by `BiRefNetRMBG` mask feathering (`mask_blur=1`), and
2. source-side light pixels at the character boundary: silver hair, white shirt/cardigan highlights, and sometimes a pale anti-aliased edge from the gray background.

This is normal matte/defringe behavior: transparent PNGs can still contain light RGB values on semi-transparent edge pixels. On a dark Ren'Py/background composite those edge pixels become visible as a white rim.

## Evidence

Existing 04 alpha gate output was inspected:

```text
ComfyUI/output/hermes_vn_pose_alpha_gate/contact_batch1_pose_alpha_light_dark.png
```

Pixel scan of semi-transparent edge pixels showed the silver-haired sprites have more light edge pixels than pink-haired sprites:

```text
alpha_silver_arms_crossed: whiteish semi-edge pixels ~9.6%
alpha_silver_hand_chest:   whiteish semi-edge pixels ~6.6%
alpha_pink_arms_crossed:   whiteish semi-edge pixels ~0.4%
alpha_pink_hand_chest:     whiteish semi-edge pixels ~0.5%
```

This points to silver hair / light outfit / light edge colors, not simply unremoved gray background.

## Alpha setting sweep

Tested on the worst-looking silver arms-crossed source:

```text
ComfyUI/output/hermes_vn_alpha_edge_sweep/contact_alpha_edge_sweep_dark.png
ComfyUI/output/hermes_vn_alpha_edge_sweep/batch1_manifest.json
```

Variants:

```text
current_blur1_offset0_refineT
sharp_blur0_offset0_refineT
erode_blur1_offset_minus1_refineT
erode_blur0_offset_minus1_refineT
erode_blur1_offset_minus2_refineT
no_refine_blur1_offset0
```

Metric summary:

```text
current_blur1_offset0_refineT:          whiteish semi-edge ~9.6%
erode_blur1_offset_minus1_refineT:     whiteish semi-edge ~9.1%
erode_blur1_offset_minus2_refineT:     whiteish semi-edge ~11.5%
sharp_blur0_offset0_refineT:           whiteish semi-edge ~17.1%
erode_blur0_offset_minus1_refineT:     whiteish semi-edge ~14.3%
no_refine_blur1_offset0:               whiteish semi-edge ~60.6%
```

Visual result:

- `no_refine` is clearly worse; keep `refine_foreground=true`.
- `mask_blur=0` is sharper but increases harsh/light edge artifacts and can look cut-out.
- `mask_offset=-1` with `mask_blur=1` is only a slight improvement and may start eating fine hair/clothing edges.
- `mask_offset=-2` is not better.

## Direct 01→02 control test

After the initial diagnosis, a direct control test was run exactly as requested: generate a fresh 01 canonical source, then immediately pass that output through canonical 02 alpha.

Artifacts:

```text
ComfyUI/output/hermes_vn_01_02_direct_alpha_test/source_01_current_greyonly_seed719251035_00001_.png
ComfyUI/output/hermes_vn_01_02_direct_alpha_test/alpha_01_current_greyonly_seed719251035_b1_ref1_00001_.png
ComfyUI/output/hermes_vn_01_02_direct_alpha_test/contact_01_to_02_direct_alpha.png
ComfyUI/output/hermes_vn_01_02_direct_alpha_test/manifest_01_to_02_direct_alpha.json
```

Prompt IDs:

```text
01: 4fe99363-70b3-4854-979a-8096c11eef8c
02: 8a3fabaf-1006-4a51-a0fc-53b8415625db
```

Result:

- 01 source → 02 alpha has no severe transparency failure.
- Dark composite shows the expected light hair/outfit edge, but not the problematic strong halo seen in some 04 pose outputs.
- Semi-edge metric was lower than problematic 04 silver pose outputs:

```text
01→02 direct: whiteish semi-edge ~4.5%
04 silver arms_crossed→02: whiteish semi-edge ~9.6%
04 silver hand_chest→02:   whiteish semi-edge ~6.6%
```

Correction after user review: do not treat this as a settled diagnosis. The direct 01→02 control looked cleaner, but the agent may have used or evaluated a different transparency route/composite than the user's expected 02 production method. Before changing 04 based on this note, rerun using the exact known-good 02 transparency workflow/method from the user's previous successful path and compare actual RGBA outputs, not only ffmpeg composites.

## Current recommendation

Keep 02 canonical as-is for now:

```text
mask_blur: 1
mask_offset: 0
refine_foreground: true
background: Alpha
```

Optionally test a caution preset later:

```text
mask_blur: 1
mask_offset: -1
refine_foreground: true
```

but do not promote it without multi-character/hair-tip QA.

## Is it unavoidable?

Partly yes, partly improvable.

Unavoidable part:

- Silver hair and white clothing naturally create light edge pixels.
- A transparent PNG composited over dark backgrounds will reveal those light boundary pixels.
- Removing them aggressively cuts hair tips and makes the sprite look pasted/cropped.

Improvable part:

- Keep source background neutral gray (`grey_background` only) to reduce background-color contamination.
- Keep `refine_foreground=true`; disabling it is much worse.
- Add a post-alpha defringe step that only recolors semi-transparent edge RGB, not alpha, if dark-background compositing is the main target.
- Alternatively generate a dark-background-specific sprite variant, but that is less reusable.

## Best next test if user wants stronger cleanup

Create a postprocess-only variant after 02 alpha:

```text
edge RGB defringe / color decontamination
alpha unchanged
operate only on pixels with 0 < alpha < ~220
replace/lightly blend edge RGB toward nearby fully-opaque foreground color, not toward transparent background
```

This targets the actual white rim without changing the segmentation mask.
