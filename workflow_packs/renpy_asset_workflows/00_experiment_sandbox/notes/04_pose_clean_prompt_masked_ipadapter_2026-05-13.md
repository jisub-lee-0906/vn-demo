# 00 experiment — 04 pose clean Danbooru prompt with masked IPAdapter baseline

Date: 2026-05-13
Status: executed; clean prompt fixed dark/vignette drift and is the new best 04 sandbox baseline.

## Purpose

Test whether the previous dark/vignette/color drift was partly prompt contamination from:

```text
dark_background
BREAK depth_of_field
volumetric_lighting
```

The test keeps the best node baseline from the earlier method sweep:

```text
OpenPose + IPAdapterAdvanced(attn_mask=character_mask), no PuLID
```

and changes only to a cleaner Danbooru-style prompt plus small IPAdapter/ControlNet variations.

## Clean positive

```text
masterpiece, best_quality, very_aesthetic, newest, rating_explicit,
1girl, solo, cowboy_shot, standing, looking_at_viewer,
short_hair, bob_cut, silver_hair, blue_eyes,
beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose,
long_sleeves, small_breasts,
arms_crossed, crossed_arms, folded_arms,
thick_outline, clean_lineart, anime_coloring,
simple_background, grey_background, flat_background
```

## Clean negative

```text
lowres, low_quality, worst_quality, bad_quality, very_displeasing,
bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, fused_fingers,
extra_arms, extra_hands, long_body, deformed, mutated, disfigured, ugly,
cropped, cropped_head, cropped_hair, out_of_frame,
multiple_girls, duplicate_character,
text, signature, watermark, username, logo,
smile, open_mouth,
hands_on_hips, hands_in_pockets, hands_near_face,
large_breasts, huge_breasts, cleavage, nude, nipples,
badge, emblem,
white_background, bright_background, gradient_background, patterned_background,
black_background, dark_background, vignette, spotlight, dramatic_lighting, rim_lighting,
headwear, hair_ornament, object_above_head
```

## Batch1 variants

| slug | IPAdapter weight | OpenPose strength | seed | prompt_id |
|---|---:|---:|---:|---|
| A_clean_ip065_cn100 | 0.65 | 1.00 | 719252501 | 3796e308-6ce2-4f7d-95e8-9248e6fa352c |
| B_clean_ip060_cn100 | 0.60 | 1.00 | 719252502 | 67d05986-a813-42b7-bda4-5e8f6294eb0e |
| C_clean_ip065_cn090 | 0.65 | 0.90 | 719252503 | 4b296581-c2e9-4e5b-88c6-fe2cbb6de062 |

## Evidence

```text
ComfyUI/output/hermes_vn_pose_clean_prompt/contact_batch1_clean_prompt_outputs.png
ComfyUI/output/hermes_vn_pose_clean_prompt/contact_batch1_clean_prompt_controls.png
ComfyUI/output/hermes_vn_pose_clean_prompt/batch1_manifest.json
```

Individual outputs:

```text
ComfyUI/output/hermes_vn_pose_clean_prompt/A_clean_ip065_cn100_seed719252501_00001_.png
ComfyUI/output/hermes_vn_pose_clean_prompt/B_clean_ip060_cn100_seed719252502_00001_.png
ComfyUI/output/hermes_vn_pose_clean_prompt/C_clean_ip065_cn090_seed719252503_00001_.png
```

Compared against previous dirty-prompt mask-only output:

```text
ComfyUI/output/hermes_vn_pose_method_sweep/batch1_direction2_ipmask_openpose_seed719252303_00001_.png
```

## Visual QA summary

The clean prompt clearly fixed the dark/vignette background drift. All three clean variants use a light gray/beige flat background instead of the previous black/dark background.

All three keep the arms-crossed pose and preserve the silver-bob identity better than the PuLID combo tests.

### A — IP 0.65, CN 1.0

- Best overall balance.
- Arms-crossed pose is clear.
- Face/eyes/silver bob remain close enough.
- Outfit is readable and cardigan color is close to the anchor/pose reference family.
- Background is no longer dark.
- Minor drift: cardigan is slightly brighter/cleaner than anchor; expression softer/cuter.

### B — IP 0.60, CN 1.0

- Good but slightly weaker identity/face stability than A.
- Arms-crossed pose works.
- Hair/face feel a little more regenerated.

### C — IP 0.65, CN 0.9

- Pose still works, but outfit/skirt saturation drifts more.
- Not better than A.

## Current conclusion

Prompt contamination was a major contributor to the dark/vignette drift. The current best 04 sandbox baseline is:

```text
OpenPose + IPAdapterAdvanced(attn_mask=character_mask)
IPAdapter weight: 0.65
OpenPose ControlNet strength: 1.0
No PuLID
Clean Danbooru prompt without depth_of_field/volumetric_lighting/dark_background
```

Best candidate output:

```text
ComfyUI/output/hermes_vn_pose_clean_prompt/A_clean_ip065_cn100_seed719252501_00001_.png
```

## Next gates before canonical 04 promotion

1. Run the same clean baseline on at least one more pose.
2. Run it on a second character.
3. Run 02 alpha smoke on accepted pose output.
4. If color/outfit drift remains too high, test only one extra variable:

```text
+ very low Depth control from pose_ref, strength 0.20~0.30, end 0.40~0.50
```

Do not re-add PuLID or heavy Canny unless the clean baseline fails on identity or pose in later tests.
