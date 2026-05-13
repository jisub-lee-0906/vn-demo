# 04 pose prompt audit — Danbooru cleanliness and positive/negative conflicts

Date: 2026-05-13
Status: audit only; do not rewrite past evidence workflows.

## Scope

Audited current 04 pose sandbox workflows under:

```text
00_experiment_sandbox/workflow_api/00_04_pose*.json
04_pose_variation_reference_and_regeneration/workflow_api/*.json
```

## Findings

### 00 sandbox prompts

The active 00 pose sandbox prompt is mostly Danbooru-style underscore tags and has no direct positive/negative conflict for the target arms-crossed pose.

Positive includes:

```text
arms_crossed, crossed_arms, folded_arms
```

Negative does not ban those tags in the 00 sandbox pose tests. This is correct for arms-crossed testing.

However, the 00 pose prompt still has contamination risks:

1. Positive includes lighting/background tags that can explain the dark/vignette drift:

```text
dark_background
BREAK depth_of_field
volumetric_lighting
```

2. Negative does not ban dark/vignette/dramatic lighting in the runs that drifted dark.

3. Positive includes several quality/meta tags that are accepted in the current 01 v19 baseline but are not pure object/pose tags:

```text
amazing_quality
4k
high_resolution
ultra-detailed
absurdres
```

These are not positive/negative conflicts, but they can increase glossy/detail/lighting reinterpretation in pose redraws.

4. Negative includes broad style-era bans:

```text
modern, recent, old, oldest, cartoon, graphic, painting
```

These came from the Nova/Illustrious-style baseline and are not direct conflicts with current positives, but they are broad and may be over-constraining. Keep only if already proven beneficial.

### Canonical 04 old prompts

The current numbered 04 folder still contains older natural-language prompt fragments such as:

```text
anime style
cowboy shot
upper body character portrait
full head visible
complete hair visible
auburn medium-length wavy hair
pink knit cardigan over pale blue blouse
flat solid medium gray background
plain uniform gray backdrop
```

Those are not v19 Danbooru-clean and belong to legacy 04, not the new sandbox route. Do not promote them into the new 04 canonical route.

## Conflict check

For 00 pose sandbox arms-crossed workflows:

- No exact token overlap between positive and negative for pose target.
- Positive arms-crossed tags are not banned in negative.
- Negative bans competing hand poses:

```text
hands_on_hips
hands_in_pockets
hands_near_face
```

This is acceptable for arms-crossed tests.

Potential issue:

```text
negative: dynamic_pose
```

This is not a direct conflict with static `arms_crossed`, but it can fight future dynamic poses such as dancing/running/jumping. Remove it for any dynamic-pose tests.

## Recommended clean 04 prompt baseline

Use this for the next mask-only background-lock test. It keeps Danbooru-style tags and removes the tags most likely to cause dark/vignette drift.

Positive:

```text
masterpiece, best_quality, very_aesthetic, newest, rating_questionable,
1girl, solo, cowboy_shot, standing, looking_at_viewer,
short_hair, bob_cut, silver_hair, blue_eyes,
beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose,
long_sleeves, small_breasts,
arms_crossed, crossed_arms, folded_arms,
thick_outline, clean_lineart, anime_coloring,
simple_background, grey_background, flat_background
```

Negative:

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

Notes:

- Do not include `dark_background` in positive if `dark_background` is in negative.
- Do not include `depth_of_field` or `volumetric_lighting` for sprite pose tests unless intentionally testing lighting.
- Remove `dynamic_pose` from negative when the target pose is dynamic.
- For non-arms-crossed poses, swap pose negatives so the target gesture is not banned.
