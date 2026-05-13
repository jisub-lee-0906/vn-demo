# Full chain 01→04→03→02 current retest

Date: 2026-05-13
Status: executed; production gate still fails at 03 expression readability.

## Chain

Run folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current`

Steps:

1. `01_character_anchor_and_prompt` current canonical after removing `depth_of_field`/`volumetric_lighting`.
2. `04_pose_variation_reference_and_regeneration` current canonical OpenPose + masked IPAdapter, with no `thick_outline` in 04 character tags.
3. `03_expression_variation_face_composite` Florence-2 face composite on the 04 source, happy retries at denoise `0.55` and `0.65`.
4. `02_toonout_transparency_alpha` current b1/ref1 alpha.

## Outputs

- Manifest:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/manifest_full_chain_current.json`
- 01 source:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png`
- 04 source:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/04_pose_silver_bob_arms_crossed_seed719252501_00001_.png`
- 03 happy d0.55:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/03_happy_d055_composited_00001_.png`
- 03 happy d0.65:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/03_happy_d065_composited_00001_.png`
- 02 alpha d0.65:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/02_alpha_after_03_happy_d065_b1_ref1_00001_.png`
- Contact sheet:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/contact_full_chain_01_04_03_02_current.png`
- d0.55 vs d0.65 comparison:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/contact_full_chain_happy_d055_d065_compare.png`
- Face comparison:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/contact_full_chain_happy_d055_d065_faces.png`
- Mask overlay:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/03_happy_d065_mask_overlay_on_04.png`

## QA summary

- 01 background: improved and plain enough for this chain smoke.
- 04: arms-crossed pose works; no obvious old sticker-like white rim. Caution: style/linework and facial attitude drift remain from 01.
- 03: source-level 01→03 expression change still works; the known happy 01-source output reads as a smile. The failure is specifically 04→03 on this exact full-chain 04 output. Denoise `0.55` and `0.65` barely change the stern mouth/face; neither reads as a clear happy smile.
- 03 mask: overlay shows the face/mouth region is covered, so this failure is likely not just mask placement. The current 04 source face attitude / pose-regeneration styling appears too locked for happy.
- 02: alpha output on black does not show severe new halo/rim; it preserves upstream 03/04 appearance.

## Next direction

Do not promote this full chain yet. Next 03 work should change the expression mechanism, not just denoise: try stronger face-local prompt/negative, different seed, reduced ControlNet/repaint lock, mask offset/blur variation, or a mouth-specific/manual mask route that can alter the mouth while preserving the rest of the face.
