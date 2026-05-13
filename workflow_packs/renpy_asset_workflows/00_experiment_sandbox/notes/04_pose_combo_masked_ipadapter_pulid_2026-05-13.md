# 00 experiment — 04 pose combo: masked IPAdapter + PuLID

Date: 2026-05-13
Status: executed; PuLID combo did not beat previous mask-only baseline.

## Purpose

Test the proposed combination of:

```text
OpenPose pose control
+ IPAdapter attention mask from character mask
+ PuLID for face identity
+ lower IPAdapter weight for outfit/style
```

This follows the previous method sweep where:

- Direction 2 (`OpenPose + masked IPAdapter`) was the best drift reducer.
- Direction 3 (`OpenPose + PuLID + low IPAdapter`) improved face identity but did not fully fix outfit/background.

## Inputs

```text
anchor: ComfyUI/input/hermes_identity_silver_bob_anchor_v190.png
pose_ref: ComfyUI/input/hermes_pose_ref_silver_bob_arms_crossed.png
```

## Batch1 variants

| slug | PuLID weight | IPAdapter weight | seed | prompt_id |
|---|---:|---:|---:|---|
| A_pulid065_ip045_mask_openpose | 0.65 | 0.45 | 719252401 | 261bee8f-2aa0-4796-8235-55eea45cb9b8 |
| B_pulid075_ip045_mask_openpose | 0.75 | 0.45 | 719252402 | 9326deb8-69d5-4160-9c5d-159a9a149ed7 |
| C_pulid075_ip055_mask_openpose | 0.75 | 0.55 | 719252403 | ecdf776c-5d23-48c8-a186-59f89fd478dd |

## Evidence

```text
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/contact_batch1_mask_pulid_combo_outputs.png
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/contact_batch1_mask_pulid_combo_controls.png
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/batch1_manifest.json
```

Individual outputs:

```text
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/A_pulid065_ip045_mask_openpose_seed719252401_00001_.png
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/B_pulid075_ip045_mask_openpose_seed719252402_00001_.png
ComfyUI/output/hermes_vn_pose_mask_pulid_combo/C_pulid075_ip055_mask_openpose_seed719252403_00001_.png
```

Compared against previous best:

```text
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction2_ipmask_openpose_seed719252303_00001_.png
```

## Control QA

A/B/C used the same valid OpenPose control preview. The control still captures the arms-crossed skeleton. Differences in output are from PuLID/IPAdapter settings and seed, not from different pose controls.

## Visual QA summary

### A — PuLID 0.65 + masked IPAdapter 0.45

- Arms-crossed pose works.
- Silver bob and outfit remain readable.
- Background is very dark and vignetted.
- Face tilts/changes more than desired.
- Does not beat previous mask-only baseline.

### B — PuLID 0.75 + masked IPAdapter 0.45

- Arms-crossed pose works.
- Cardigan color is relatively stable.
- Face/eyes become more exaggerated and less like the anchor.
- Background remains very dark.
- Also does not beat previous mask-only baseline.

### C — PuLID 0.75 + masked IPAdapter 0.55

- Arms-crossed pose works.
- Strong color/style drift: orange/red linework, oversaturated bow/skirt, heavier shadowing.
- Worst of the three for canonical purposes.
- Increasing masked IPAdapter from 0.45 to 0.55 with PuLID worsened style/color drift in this batch.

## Current conclusion

The PuLID + masked IPAdapter combo did not improve the 04 candidate. The earlier mask-only result remains the best current baseline:

```text
OpenPose + IPAdapterAdvanced(attn_mask=character_mask), IPAdapter weight 0.65
```

PuLID is not automatically beneficial here. It can preserve a face-like identity, but in this setup it also pushed lighting/background/face stylization away from the 01 anchor. For this silver-bob arms-crossed case, PuLID should be disabled or tested at much lower weight only after the mask-only baseline is stabilized.

## Next recommended tests

Do not keep stacking PuLID. Return to mask-only baseline and tune one variable:

1. Fix background drift:

```text
OpenPose + masked IPAdapter 0.65
+ stronger prompt negatives: dark_background, black_background, vignette, spotlight, dramatic_lighting
+ positive: simple_background, grey_background, flat_background
```

2. If outfit/line drift remains after background fix, add very low depth or line control only as secondary support:

```text
OpenPose + masked IPAdapter 0.65
+ Depth from pose_ref strength 0.20~0.30, end 0.40~0.50
```

or

```text
OpenPose + masked IPAdapter 0.65
+ Canny from pose_ref strength 0.10~0.20, end 0.30~0.40
```

3. If face identity becomes weak after background/outfit tuning, retry PuLID only at very low weight:

```text
PuLID 0.25~0.40
IPAdapter mask baseline unchanged
```

Avoid PuLID 0.65+ for now.
