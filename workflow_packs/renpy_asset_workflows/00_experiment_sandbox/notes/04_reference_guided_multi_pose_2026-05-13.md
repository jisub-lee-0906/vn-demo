# 04 reference-guided multi-pose smoke — 2026-05-13

Purpose: test the user's proposal to use image references, and test more than arms-crossed. This route treats the reference image as a pose/arm-structure guide, not as identity/style.

Route:
- source identity/style: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png`
- preserve mask: alpha-minus-head/head-hair-face protected body inpaint.
- reference signals:
  - OpenPose from pose reference at strength 1.0.
  - masked Canny from reference image at arms/torso region only, blacking out head and lower body, strength 0.30-0.35, end 0.55.
- tested poses: `arms_crossed`, `hand_chest`, `pointing`.

Run folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513`

Contact sheet:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513/contact_reference_guided_multi_pose.png`

Manifest:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513/manifest_reference_guided_multi_pose.json`

02 alpha gate folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_02_after_reference_guided_multi_pose_20260513`

02 alpha contact sheet:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_02_after_reference_guided_multi_pose_20260513/contact_02_after_reference_guided_multi_pose.png`

Results:

## arms_crossed

Composite:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_arms_crossed_op100_canny35_d88_seed719255101_00001_.png`

Alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_02_after_reference_guided_multi_pose_20260513/alpha_arms_crossed_00001_.png`

Assessment:
- Promising.
- Face/head preservation is strong because head/hair/face are preserved from source.
- Arms-crossed pose is readable.
- Masked Canny helped sleeve/arm structure lock more clearly than pure OpenPose-only attempts.
- 02 alpha passed first light/dark preview: no severe halo/rim; edges acceptable.
- Still needs user QA against previous best for exact 01-style fidelity and cardigan/body drift.

## hand_chest

Composite:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_hand_chest_op100_canny35_d86_seed719255102_00001_.png`

Alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_02_after_reference_guided_multi_pose_20260513/alpha_hand_chest_00001_.png`

Assessment:
- Promising and arguably the cleanest multi-pose smoke result.
- Hand-on-chest gesture is readable.
- Face/head preserved well.
- Outfit remains coherent; less extreme body reconstruction than pointing.
- 02 alpha passed first light/dark preview without severe halo/rim.

## pointing

Composite:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_pointing_op100_canny30_d86_seed719255103_00001_.png`

Alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_02_after_reference_guided_multi_pose_20260513/alpha_pointing_00001_.png`

Assessment:
- Not a production pass for `pointing`.
- It reads more like a raised fist/hand near shoulder than pointing/outstretched arm.
- Face/head preservation and 02 alpha are acceptable, but the intended pose failed.
- Pointing likely needs either a better reference with stronger outstretched arm geometry, a broader edit mask, higher/longer Canny influence, or a separate arm-overlay/donor route. The current alpha-minus-head mask may be too conservative for large lateral arm extension.

Conclusion:
- Image-reference guidance is worth keeping. It improved multi-pose structure for smaller/contained gestures (`arms_crossed`, `hand_chest`).
- This route generalizes better than arms-crossed-only tuning, but does not solve high-displacement gestures like pointing yet.
- Next useful experiment: classify poses by displacement:
  1. contained poses: `arms_crossed`, `hand_chest` → reference-guided alpha-minus-head route likely viable.
  2. high-displacement poses: `pointing`, maybe `one_hand_hip` → need arm-overlay/donor or broader pose-specific mask.
