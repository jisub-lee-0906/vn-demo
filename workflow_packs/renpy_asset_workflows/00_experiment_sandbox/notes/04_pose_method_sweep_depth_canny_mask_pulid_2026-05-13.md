# 00 experiment — 04 pose method sweep: Depth/Canny, IPAdapter mask, PuLID split

Date: 2026-05-13
Status: executed; best candidate is IPAdapter attention mask + OpenPose, with PuLID split also promising.

## Purpose

Test four proposed approaches for reducing color/style/outfit drift in 04 pose variation.

User proposals:

1. Replace OpenPose with Depth or Canny.
2. Add IPAdapter attention masking so IPAdapter affects only character area.
3. Split identity/style work: PuLID for face identity, low-weight IPAdapter for outfit/style, ControlNet for pose.
4. LoRA training feasibility.

## Runtime availability

Available on the live Windows ComfyUI backend:

```text
DepthAnythingPreprocessor
DepthAnythingV2Preprocessor
Zoe_DepthAnythingPreprocessor
CannyEdgePreprocessor
AnimeLineArtPreprocessor
ColorPreprocessor
IPAdapterAdvanced with optional attn_mask
ApplyPulid / ApplyPulidAdvanced
PulidModelLoader: ip-adapter_pulid_sdxl_fp16.safetensors
PulidInsightFaceLoader
PulidEvaClipLoader
ControlNetLoader: xinsir-controlnet-union-sdxl-1.0-promax.safetensors
SetUnionControlNetType: openpose/depth/canny-lineart/etc.
```

Local WSL LoRA training stack was not present:

```text
onetrainer: missing
torch: missing
diffusers: missing
accelerate: missing
transformers: missing
```

Do not claim local 2-minute LoRA training is ready on this machine without installing/configuring a training stack and approving that side effect.

## Inputs

```text
anchor: ComfyUI/input/hermes_identity_silver_bob_anchor_v190.png
pose_ref: ComfyUI/input/hermes_pose_ref_silver_bob_arms_crossed.png
```

## Batch1 variants

| slug | method | seed | prompt_id |
|---|---|---:|---|
| direction1_depth_ip065 | DepthAnythingV2 pose control + IPAdapter 0.65 | 719252301 | 18acccdb-838c-4b02-a88f-8f7474fc5d13 |
| direction1_canny_ip065 | Canny pose/style control + IPAdapter 0.65 | 719252302 | efbf989d-5940-4f95-9008-b3dcfcccd58d |
| direction2_ipmask_openpose | OpenPose + IPAdapter 0.65 with BiRefNet character attn_mask | 719252303 | 83e95630-a2d4-4654-b98a-55b6281743df |
| direction3_pulid_ip045_openpose | OpenPose + PuLID 0.75 + IPAdapter 0.45 | 719252304 | c225f77c-2ae1-4f7f-a2c9-3fa0492942ad |

## Evidence

```text
ComfyUI/output/hermes_vn_pose_method_sweep/contact_batch1_method_sweep_outputs.png
ComfyUI/output/hermes_vn_pose_method_sweep/contact_batch1_method_sweep_controls.png
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_manifest.json
```

Individual outputs:

```text
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction1_depth_ip065_seed719252301_00001_.png
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction1_canny_ip065_seed719252302_00001_.png
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction2_ipmask_openpose_seed719252303_00001_.png
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction3_pulid_ip045_openpose_seed719252304_00001_.png
```

## Visual QA summary

### Direction 1: Depth instead of OpenPose

- Depth control carried useful body volume and arms-crossed silhouette.
- Output followed arms-crossed pose well.
- However cardigan became very yellow/bright and background shifted warmer.
- Identity is okay, but color/style drift is still strong.
- Not the best answer alone.

### Direction 1: Canny instead of OpenPose

- Canny carried the most detailed silhouette/line information.
- It followed arms-crossed pose and clothing outline strongly.
- However it also imported too much pose-reference structure/style and made the output more donor/reference-like.
- Color/style drift remained high.
- Useful as a low-strength secondary control, but risky as the only pose control.

### Direction 2: IPAdapter attention mask + OpenPose

- Best first result for reducing drift.
- Cardigan color moved closer to anchor beige than the previous OpenPose+IP baseline.
- Outfit details and skirt remained readable.
- Pose remains arms-crossed.
- Background became too dark because the IPAdapter mask restricts anchor influence to the character area; background must be prompt-controlled or handled separately.
- Strong candidate for next 04 route.

### Direction 3: PuLID + low IPAdapter + OpenPose

- Face identity improved; silver bob and facial impression remained strong.
- Pose remains arms-crossed.
- Outfit is somewhat stable, but cardigan/background still drift.
- Good candidate to combine with direction 2, but not a full fix alone.

## Current ranking

1. Direction 2: IPAdapter attention mask + OpenPose — best overall drift reduction.
2. Direction 3: PuLID + low IPAdapter + OpenPose — best face identity split, useful combined with direction 2.
3. Direction 1 Depth — good pose/volume, but color drift remains high.
4. Direction 1 Canny — strong structure but too much style/line leakage when used as sole control.

## Recommended next test

Combine direction 2 and direction 3 with one minimal graph:

```text
OpenposePreprocessor pose_ref
+ IPAdapterAdvanced(anchor, weight=0.45~0.55, attn_mask=BiRefNet character mask)
+ ApplyPulidAdvanced(anchor, weight=0.65~0.75)
+ stronger prompt/background lock
```

Keep OpenPose for pose. Do not replace it with Depth/Canny as the sole pose signal yet.

Optional secondary test:

```text
OpenPose + masked low IPAdapter + PuLID
+ low-strength Depth control from pose_ref, strength 0.25~0.35, end 0.45
```

Do not use Canny at high strength as the sole pose control because it may over-constrain/reference-leak line style.

## LoRA note

Character LoRA may eventually be the highest-control option, but this machine/session does not currently have a ready local training stack. Also, a one-image LoRA can overfit and will not invent unseen back/side outfit data. Treat LoRA as a separate setup/training milestone, not a quick node-only smoke test.
