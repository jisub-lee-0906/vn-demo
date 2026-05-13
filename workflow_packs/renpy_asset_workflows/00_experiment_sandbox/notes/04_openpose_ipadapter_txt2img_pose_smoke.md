# 00 experiment — 04 OpenPose ControlNet + IPAdapter txt2img pose smoke

Date: 2026-05-13
Status: smoke executed; promising but not canonical.

## Purpose

Test a new 04 pose route that avoids pose-donor identity contamination by using the pose image only as OpenPose/DWPose control, not as img2img latent.

## Workflow

```text
workflow_api/00_04_pose_openpose_ipadapter_txt2img_smoke_api.json
```

Route:

```text
CheckpointLoaderSimple(novaAnimeXL_ilV190)
LoadImage(anchor) -> IPAdapterAdvanced(identity/style)
LoadImage(pose_reference) -> OpenposePreprocessor or DWPreprocessor -> SDXL Union ControlNet(type=openpose)
EmptyLatentImage -> KSampler(denoise=1.0) -> VAEDecode -> SaveImage
```

Important design choice:

- Use `EmptyLatentImage`, not `VAEEncode(pose_reference)`, when `denoise=1.0`.
- The pose image should only feed the pose preprocessor/ControlNet.
- This makes the route closer to txt2img with image controls instead of img2img donor regeneration.

## Inputs used

```text
ComfyUI/input/hermes_identity_silver_bob_anchor_v190.png
ComfyUI/input/hermes_pose_ref_silver_bob_arms_crossed.png
```

## Batch1 variants

| slug | preprocessor | ControlNet strength | IPAdapter weight | seed |
|---|---|---:|---:|---:|
| openpose_cn100_ip065 | OpenposePreprocessor | 1.00 | 0.65 | 719252101 |
| openpose_cn110_ip065 | OpenposePreprocessor | 1.10 | 0.65 | 719252102 |
| openpose_cn100_ip075 | OpenposePreprocessor | 1.00 | 0.75 | 719252103 |
| dwpose_cn100_ip065 | DWPreprocessor | 1.00 | 0.65 | 719252104 |

Shared settings:

```text
checkpoint: novaAnimeXL_ilV190.safetensors
controlnet: xinsir-controlnet-union-sdxl-1.0-promax.safetensors
union type: openpose
latent: EmptyLatentImage 1152x1536
sampler: euler_ancestral / normal
steps: 28
cfg: 5.0
denoise: 1.0
IPAdapter file: ip-adapter-plus_sdxl_vit-h.safetensors
CLIP vision: clip-vision_vit-h.safetensors
IPAdapter weight_type: style transfer
IPAdapter end_at: 0.75
```

## Evidence

```text
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/contact_batch1_openpose_ipadapter_outputs.png
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/contact_batch1_openpose_ipadapter_controls.png
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/batch1_manifest.json
```

Outputs:

```text
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/batch1_openpose_cn100_ip065_seed719252101_00001_.png
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/batch1_openpose_cn110_ip065_seed719252102_00001_.png
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/batch1_openpose_cn100_ip075_seed719252103_00001_.png
ComfyUI/output/hermes_vn_pose_openpose_ipadapter/batch1_dwpose_cn100_ip065_seed719252104_00001_.png
```

## Findings

- The method successfully changed the A-pose anchor into an arms-crossed pose.
- OpenPose control previews detected the torso/arm crossing well enough to guide the pose.
- `openpose_cn100_ip065` and `openpose_cn110_ip065` are the best first candidates.
- `openpose_cn100_ip075` follows pose but IPAdapter weight 0.75 increased color/stylistic drift.
- `DWPreprocessor` produced a blank control preview in this setup, so do not use it for this route without diagnosing the preprocessor/model state first.
- Identity is much better than old donor-img2img contamination in the sense that hair stays silver/short bob, but outfit/background/color still drift from the exact 01 anchor.
- The cardigan becomes yellower/brighter and details are not exact. This is expected because OpenPose does not preserve clothing texture or color.

## Current best baseline

Use OpenPose, not DWPose:

```text
preprocessor: OpenposePreprocessor
controlnet_strength: 1.0 to 1.1
ipadapter_weight: 0.65
ipadapter_weight_type: style transfer
ipadapter_end_at: 0.75
denoise: 1.0
latent: EmptyLatentImage
```

For next tests, try preserving outfit/color with one added image signal, one variable at a time:

1. Anchor lineart/canny/anime_lineart at low strength, plus pose OpenPose.
2. Lower IPAdapter end_at only if pose weakens less than identity improves.
3. Avoid DWPose until blank-control issue is resolved.
4. Do not return to pose image as img2img latent unless intentionally testing donor contamination.

## Promotion gate before touching 04 canonical

Do not promote yet. First verify:

1. At least two poses, not only arms_crossed.
2. One second character to check generalization.
3. 02 alpha smoke on a selected pose output.
4. Outfit color/detail drift is acceptable or fixed with a stable low-strength anchor lineart/canny control.
