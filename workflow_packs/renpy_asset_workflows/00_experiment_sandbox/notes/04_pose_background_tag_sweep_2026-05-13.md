# 00 experiment — 04 pose background tag sweep

Date: 2026-05-13
Status: executed; canonical 04 should use `grey_background` only for the positive background tag.

## Why

User noticed that background-related tags such as:

```text
simple_background, grey_background, dark_background
```

can fight each other. In particular, `dark_background` clearly competes with the desired neutral gray source background and worsens alpha/source QA risk.

## Scope

Tested the promoted 04 OpenPose + masked IPAdapter route on silver-bob `arms_crossed`.

Fixed settings:

```text
04_pose_refregen_openpose_ipadapter_masked_canonical_api.json
character: silver_bob
pose: arms_crossed
OpenPose + masked IPAdapter
IPAdapter weight 0.65
ControlNet strength 1.0
```

## Batch 1 — varied seeds

Outputs/contact:

```text
ComfyUI/output/hermes_vn_pose_bg_tag_sweep/contact_batch1_bg_tag_sweep.png
ComfyUI/output/hermes_vn_pose_bg_tag_sweep/batch1_manifest.json
```

Variants:

```text
A_current_simple_grey_flat: simple_background, grey_background, flat_background
B_grey_only: grey_background
C_grey_flat: grey_background, flat_background
D_plain_grey: plain_background, grey_background
E_old_simple_grey_dark: simple_background, grey_background, dark_background
```

Result: `dark_background` made the source visibly dark gray. Other variants were lighter, but varied seeds made fine ranking unreliable.

## Batch 2 — same seed controlled comparison

Outputs/contact:

```text
ComfyUI/output/hermes_vn_pose_bg_tag_sweep/contact_batch2_bg_tag_same_seed.png
ComfyUI/output/hermes_vn_pose_bg_tag_sweep/batch2_same_seed_manifest.json
```

Seed:

```text
719252851
```

Variants:

```text
F_same_simple_grey: simple_background, grey_background
G_same_grey_only: grey_background
H_same_grey_flat: grey_background, flat_background
I_same_simple_grey_flat: simple_background, grey_background, flat_background
J_same_old_simple_grey_dark: simple_background, grey_background, dark_background
```

Prompt IDs:

```text
F_same_simple_grey: 85c0e381-fe98-4717-bb09-24ebb088aa37
G_same_grey_only: 9681b800-391f-4878-ac45-dc927dc298f3
H_same_grey_flat: acf182da-b9aa-482c-bff1-d27ab3a171f3
I_same_simple_grey_flat: a843afda-2d16-4011-ba34-2601927e95a8
J_same_old_simple_grey_dark: 33342c42-99a3-40ac-9b71-86fe47c37ee5
```

## QA

- `J_same_old_simple_grey_dark` is a clear reject: background is much darker and conflicts with the desired neutral gray source.
- `H_same_grey_flat` and `I_same_simple_grey_flat` skew warmer/beige compared with the desired neutral gray.
- `F_same_simple_grey` and `G_same_grey_only` are both acceptable.
- `G_same_grey_only` is preferred because it is the minimal non-conflicting color instruction and avoids redundant background semantics.

## Decision

For 04 canonical positive prompt, use only:

```text
grey_background
```

Do not include these in the 04 positive prompt:

```text
simple_background, flat_background, plain_background, dark_background, black_background,
depth_of_field, volumetric_lighting, spotlight, dramatic_lighting, rim_lighting
```

Keep the negative bans:

```text
white_background, bright_background, gradient_background, patterned_background,
black_background, dark_background, vignette, spotlight, dramatic_lighting, rim_lighting
```

Rationale:

- `grey_background` alone is enough to produce a clean neutral gray source.
- `simple_background` is not a direct color conflict, but it is redundant for 04 source generation.
- `flat_background` can push the background warmer/beige in this route.
- `dark_background` directly conflicts with the desired gray source and should stay negative-only.
