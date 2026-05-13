# 00 experiment — 04 clean baseline 02 alpha gate

Date: 2026-05-13
Status: passed; 04 clean pose baseline is ready for canonical promotion pending user visual QA/approval.

## Purpose

Run the next gate after clean 04 multi-pose + second-character smoke:

```text
04 pose source PNG
-> 02_toonout_transparency_alpha canonical workflow
-> alpha PNG
-> light/dark composite QA
```

## 02 alpha workflow

Used canonical 02 workflow:

```text
02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json
```

Fixed settings:

```text
model: BiRefNet_toonout
mask_blur: 1
mask_offset: 0
invert_output: false
refine_foreground: true
background: Alpha
```

Only edited:

```text
node 1 LoadImage.image
node 3 SaveImage.filename_prefix
```

## Inputs

Accepted 04 clean pose source outputs:

```text
ComfyUI/output/hermes_vn_pose_clean_multi_pose/arms_crossed_clean_ip065_cn100_seed719252601_00001_.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/hand_chest_clean_ip065_cn100_seed719252603_00001_.png
ComfyUI/output/hermes_vn_pose_clean_second_character/pink_arms_crossed_clean_ip065_cn100_seed719252701_00001_.png
ComfyUI/output/hermes_vn_pose_clean_second_character/pink_hand_chest_clean_ip065_cn100_seed719252703_00001_.png
```

Copied to ComfyUI input for LoadImage:

```text
ComfyUI/input/hermes_vn_pose_alpha_gate/arms_crossed_clean_ip065_cn100_seed719252601_00001_.png
ComfyUI/input/hermes_vn_pose_alpha_gate/hand_chest_clean_ip065_cn100_seed719252603_00001_.png
ComfyUI/input/hermes_vn_pose_alpha_gate/pink_arms_crossed_clean_ip065_cn100_seed719252701_00001_.png
ComfyUI/input/hermes_vn_pose_alpha_gate/pink_hand_chest_clean_ip065_cn100_seed719252703_00001_.png
```

## Outputs

Alpha PNGs:

```text
ComfyUI/output/hermes_vn_pose_alpha_gate/alpha_silver_arms_crossed_b1_ref1_00001_.png
ComfyUI/output/hermes_vn_pose_alpha_gate/alpha_silver_hand_chest_b1_ref1_00001_.png
ComfyUI/output/hermes_vn_pose_alpha_gate/alpha_pink_arms_crossed_b1_ref1_00001_.png
ComfyUI/output/hermes_vn_pose_alpha_gate/alpha_pink_hand_chest_b1_ref1_00001_.png
```

All four alpha PNGs verified as `rgba` with `1152x1536` dimensions.

Light/dark composites and QA sheet:

```text
ComfyUI/output/hermes_vn_pose_alpha_gate/contact_batch1_pose_alpha_light_dark.png
ComfyUI/output/hermes_vn_pose_alpha_gate/batch1_manifest.json
```

Prompt IDs:

```text
silver_arms_crossed: ebc19eaa-fb9d-4380-96da-01417ad1d3c1
silver_hand_chest: 553c3cfb-15e7-4803-8314-51e8fdce761c
pink_arms_crossed: 1bc2d441-6a49-4b4a-8b96-89a060e4c730
pink_hand_chest: 5588a3ac-91ea-4389-9379-988153468bd1
```

## Visual QA

All four alpha outputs pass the gate.

Observed:

- Background is removed and alpha is present.
- Light composites are clean; no obvious dark halo.
- Dark composites are clean; no severe light rim or gray/cream background residue.
- Silver hair tips/edges are preserved well enough.
- Pink braids/hair edges are preserved well enough.
- Hands, arms, sleeves, skirt, and cardigan/shirt edges remain intact.
- No visible catastrophic clipping around crossed arms or hand-chest gestures.

Minor notes:

- There may be tiny normal antialiasing around bright hair/edges on dark background, but it is acceptable and less important than preserving hair detail.
- This confirms the existing 02 canonical alpha workflow works for the 04 clean pose outputs; no 02 retuning is needed.

## Current conclusion

The 04 clean baseline passed the required alpha gate for two poses (`arms_crossed`, `hand_chest`) and two characters (`silver_bob`, `pink_twinbraids`).

04 clean baseline is ready for canonical promotion, pending user visual QA/approval.

Recommended promotion scope:

```text
04_pose_variation_reference_and_regeneration/
```

Promote one generic API workflow with editable nodes for:

```text
identity anchor image
pose reference image
positive prompt
negative prompt
seed
SaveImage prefix
```

README should include preset tables:

Stable presets:

```text
arms_crossed
hand_chest
```

Caution presets:

```text
pointing
one_hand_hip
```

Do not promote the failed/weak sandbox variants:

```text
PuLID combo
Depth-only
Canny-only
dirty-prompt workflows
DWPreprocessor route
```
