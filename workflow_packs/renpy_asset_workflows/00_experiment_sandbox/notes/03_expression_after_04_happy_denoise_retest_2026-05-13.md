# 03 expression after 04 happy denoise retest

Date: 2026-05-13
Status: executed; sandbox evidence, not canonical promotion yet.

## Question

User asked whether the current 03 canonical was based on the earlier good expression outputs and whether expression-change needs retesting.

## Inputs

- Fixed 01 source:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_chain_retest_20260513/01_no_depth_volumetric_source_00001_.png`
- Fixed 04 source, no `thick_outline` rim:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_chain_retest_20260513/no_thick_arms_crossed_src_00001_.png`

## Findings

1. The promoted 03 canonical route is the same Florence-2 face-mask composite route that worked on the earlier 01/silver-bob source tests.
2. That earlier success was source-level 01 expression QA, not a proven 01→04→03 chain gate.
3. On the fixed 01 source, current happy/surprised presets remain visibly distinct.
4. On the fixed 04 arms-crossed source, exact current JSON happy at denoise `0.40` is still too weak: it opens the mouth but does not read as a clear smile.
5. A one-variable denoise sweep on 04 source found:
   - `0.40`: weak / not happy enough
   - `0.50`: weak / not happy enough
   - `0.55`: clear mild smile, usable candidate
   - `0.65`: slightly stronger smile, still plausible; check identity/user preference

## Evidence

- Manifest current 03 smoke:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/manifest_current_03_smoke.json`
- Full contact:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/contact_current_03_full.png`
- Face contact:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/contact_current_03_face.png`
- Exact JSON vs source-compatible happy:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/contact_04_exact_vs_source_compatible_happy_face.png`
- Happy denoise sweep:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/contact_04_happy_denoise_sweep_face.png`
- Denoise sweep manifest:
  `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_expr_retest_20260513/manifest_04_happy_denoise_sweep.json`

## Recommendation

Keep 03 folder canonical route as Florence-2 face-mask composite, but do not claim the existing per-expression preset table is production-safe after 04. For 04 posed sources, retest presets separately. For happy after 04, candidate denoise is `0.55` or `0.65`; user visual QA should choose between mild identity preservation (`0.55`) and stronger smile (`0.65`).
