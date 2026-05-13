# 04 Florence-protected pose inpaint test — 2026-05-13

Purpose: test whether Florence-2 can make the pose-only route viable by protecting the original head/identity while inpainting only the arm/torso region for `arms_crossed`.

## Mask probe

Run:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_mask_probe_20260513
```

Contact sheet:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_mask_probe_20260513/contact_florence_masks.png
```

Observation:

- `face`, `head`, and `hair` masks are useful as protection masks.
- `arms`, `sleeves`, `cardigan`, and `upper body` are too broad/ambiguous for precise pose editing; many collapse to torso/clothing rather than actual arms/hands.
- Therefore Florence-2 is useful here mainly for preserving head/identity, not for generating the inpaint edit mask by itself.

## Inpaint route tested

Structure:

```text
01 original source
+ manual arm/torso inpaint mask
- Florence-2 head mask protection
+ OpenPose arms_crossed pose reference
-> InpaintModelConditioning + DifferentialDiffusion
-> ControlNet Union type=openpose
-> ImageCompositeMasked back onto original
```

Run:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513
```

Scripts/workflows:

```text
00_experiment_sandbox/scripts/run_04_florence_mask_probe.py
00_experiment_sandbox/scripts/run_04_florence_protected_pose_inpaint.py
00_experiment_sandbox/workflow_api/00_04_florence_protected_inpaint_wide_d95_cn100_seed719254195_api.json
00_experiment_sandbox/workflow_api/00_04_florence_protected_inpaint_wide_lower_d95_cn100_seed719254196_api.json
00_experiment_sandbox/workflow_api/00_04_florence_protected_inpaint_wide_lower_d95_negpose_seed719254197_api.json
```

Contact sheets:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/contact_original_vs_florence_protected_inpaint.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/contact_inpaint_highdenoise_retry.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/contact_best_and_lower_retry.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/contact_final_negpose_compare.png
```

Key outputs:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/composite_wide_d95_cn100_seed719254195_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/composite_wide_lower_d95_cn100_seed719254196_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_florence_protected_inpaint_20260513/composite_wide_lower_d95_negpose_seed719254197_00001_.png
```

## Observed result

- Low/mid denoise (`0.55`, `0.70`) did not overcome the original arms-at-sides pose.
- High denoise (`0.95`) plus OpenPose strength `1.0` produced a readable crossed-arms pose while preserving the original head/hair outside the mask.
- This is the first tested route that clearly changes the pose while keeping much of the original 01 image outside the edited region.
- Failure: side/lower original-style hands remain or are regenerated near skirt/hips, causing extra-hand artifacts.
- Adding stronger negative pose tags did not remove the side hands.
- The `wide_lower` mask did not fix the side-hand issue and increased torso/waist redraw area.

## Current conclusion

Florence-2 is useful as a protection-mask helper (`head`/`hair`/`face`) but not sufficient by itself. The route is promising because pose changes finally happen with identity preservation, but it needs a second-stage cleanup or a better mask/control strategy before 02 alpha.

Next candidates:

1. Second-stage inpaint just the stray side hands/old arm remnants after the crossed-arm composite.
2. Test a larger/full-torso mask with stricter crop or regional composition, accepting more outfit redraw but removing side hands.
3. Try pose donor / crossed-arm raw result as the inpaint source only inside the mask, then composite original head/hair back.
4. If exact preservation remains required, combine this with manual/Krita mask cleanup: erase side hands and use SD only for seam repair.
