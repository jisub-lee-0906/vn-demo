# 04 quality/style sweep for direct expression

Date: 2026-05-13
Status: executed; sandbox evidence. Recommended candidate: `q01_crisp_ip065` for 04 direct expression presets.

## Question

The 04 direct pose+expression route works, but the output differs from 01 in color/detail/line feel. Is this mostly unavoidable from 04 regeneration, or can prompt/IPAdapter tuning reduce the drift?

## Setup

Source 01:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png`

Pose reference:
`/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png`

Base workflow:
`04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json`

Run folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513`

Manifest:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/manifest_04_quality_style_sweep.json`

Script:
`/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows/00_experiment_sandbox/scripts/run_04_quality_style_sweep.py`

Common pose/expression:
`arms_crossed, crossed_arms, folded_arms, smile, happy, open_mouth, cheerful`

Common expression negatives:
`frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised`

## Variants

### A. `baseline_openmouth_ip065`

Output:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/04_baseline_openmouth_ip065_seed719252501_00001_.png`

Positive style:
`masterpiece, best_quality, very_aesthetic, newest, ... clean_lineart, anime_coloring, grey_background`

IPAdapter weight: `0.65`

QA:
- Pose and expression pass.
- Open-mouth happy is clear.
- Color/detail still feels simpler than 01.
- No obvious severe rim on grey source.

### B. `q01_crisp_ip065` — recommended

Output:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/04_q01_crisp_ip065_seed719252501_00001_.png`

02 alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/02_alpha_after_04_q01_crisp_ip065_b1_ref1_00001_.png`

Positive style:
`masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, ... clean_lineart, crisp_lineart, clean_outline, anime_coloring, detailed_anime_coloring, grey_background`

IPAdapter weight: `0.65`

QA:
- Pose and expression pass.
- Open-mouth happy is clear.
- Hair/eyes/face have more bright anime polish than baseline.
- Lines are crisp enough without reintroducing `thick_outline`.
- Still not pixel-identical to 01, but prompt tuning improved perceived finish.
- 02 alpha is PNG 1152x1536 RGBA color type 6.
- Dark preview shows no severe old white sticker rim; only minor dark antialias/outline.

### C. `q01_crisp_ip075`

Output:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/04_q01_crisp_ip075_seed719252501_00001_.png`

02 alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/02_alpha_after_04_q01_crisp_ip075_b1_ref1_00001_.png`

IPAdapter weight: `0.75`

QA:
- Pose/expression still pass.
- Slightly more source/style pull than `0.65`, but cardigan becomes more flat/yellow and body/clothing simplification is more noticeable.
- Not clearly better than `q01_crisp_ip065`.
- 02 alpha is PNG 1152x1536 RGBA color type 6.
- Dark preview has no severe white sticker rim, but exterior dark outline/antialias remains visible.

### D. `q01_crisp_ip085`

Output:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/04_q01_crisp_ip085_seed719252501_00001_.png`

IPAdapter weight: `0.85`

QA:
- Pose/expression still readable.
- Stronger drift/flattening: cardigan is more saturated/yellow, lower body/pose crop/shape less desirable.
- Not recommended.

## Conclusion

The 04 quality/color difference is both structural and prompt-related:

- Structural: 04 regenerates the whole image with OpenPose + IPAdapter at denoise 1.0, so exact 01 color/detail preservation is not expected.
- Prompt-related: adding 01-like quality tags and crisp-line tags improves perceived finish without using `thick_outline`.

Best current setting for happy arms_crossed direct 04:

```text
quality/style positive:
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution,
ultra-detailed, absurdres, newest, rating_explicit,
...
clean_lineart, crisp_lineart, clean_outline, anime_coloring,
detailed_anime_coloring, grey_background

IPAdapter weight: 0.65
```

Avoid for now:

- `thick_outline`: earlier 04→02 tests showed sticker-like white rim contamination.
- IPAdapter `0.85`: more flattening/saturation drift.

Next suggested test if more 01 preservation is needed:

- Keep `q01_crisp_ip065` prompt.
- Try `IPAdapter weight_type` alternatives or `0.70` only if there is a specific identity/color complaint.
- Consider a same-seed style block sweep without changing IPAdapter first; prompt has a cleaner effect than high IPAdapter weight.
