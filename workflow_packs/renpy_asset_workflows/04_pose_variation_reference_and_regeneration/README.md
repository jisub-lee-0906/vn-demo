# 04 — 포즈 variation: OpenPose + masked IPAdapter

Category: `character`

## Purpose

기준 캐릭터 anchor를 유지하면서 VN sprite용 포즈 variation source PNG를 만든다.

04의 현재 canonical 본체는 아래 경로다.

```text
pose reference image
+ character anchor image
-> OpenPose preprocessor
-> SDXL Union ControlNet type=openpose
-> IPAdapterAdvanced with character attention mask
-> same-character pose source PNG
```

투명 PNG가 필요하면 최종 source PNG를 02 alpha workflow로 후처리한다.

```text
04 pose source PNG
-> ../02_toonout_transparency_alpha/
-> Ren'Py transparent sprite PNG
```

## API template

04 now keeps exactly one active workflow JSON in this numbered folder.

- `workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json`
  - role: same-character pose regeneration from pose reference + character anchor
  - status: promoted 2026-05-13 after multi-pose, second-character, and 02 alpha gate
  - use when: 이미 pose reference가 있고, 기존 캐릭터 anchor로 같은 캐릭터의 새 포즈 source를 만들 때
  - output: source PNG plus OpenPose control preview PNG

Legacy pre-canonical JSONs were moved out of this folder to keep agent selection unambiguous:

```text
00_experiment_sandbox/workflow_api/legacy_04_pose_precanonical_2026-05-13/
```

## Canonical fixed settings

`04_pose_refregen_openpose_ipadapter_masked_canonical_api.json` uses:

```text
checkpoint: novaAnimeXL_ilV190.safetensors
latent: EmptyLatentImage 1152x1536
sampler: euler_ancestral
scheduler: normal
steps: 28
cfg: 5.0
denoise: 1.0

pose control:
OpenposePreprocessor
  detect_body: enable
  detect_hand: enable
  detect_face: disable
  resolution: 1024
  scale_stick_for_xinsr_cn: enable
ControlNet: xinsir-controlnet-union-sdxl-1.0-promax.safetensors
SetUnionControlNetType: openpose
ControlNetApplyAdvanced strength: 1.0
ControlNet start/end: 0.0 / 0.8

identity/style:
IPAdapterModelLoader: ip-adapter-plus_sdxl_vit-h.safetensors
CLIPVisionLoader: clip-vision_vit-h.safetensors
IPAdapterAdvanced weight: 0.65
IPAdapterAdvanced weight_type: style transfer
IPAdapterAdvanced combine_embeds: concat
IPAdapterAdvanced start/end: 0.0 / 0.75
IPAdapterAdvanced embeds_scaling: K+V
attn_mask: BiRefNetRMBG character mask from anchor

character mask:
BiRefNetRMBG model: BiRefNet_toonout
mask_blur: 3
mask_offset: 0
refine_foreground: true
background: Alpha

PuLID: disabled
Depth/Canny: disabled
DWPreprocessor: disabled
```

Do not reintroduce the failed sandbox variants into canonical by default:

```text
PuLID combo
Depth-only
Canny-only
dirty-prompt workflows
DWPreprocessor route
pose-reference VAE img2img latent route
```

## Editable nodes

For normal runs, edit only these fields.

| Node | Field | Meaning |
|---|---|---|
| `2` CLIPTextEncode | `inputs.text` | positive prompt: replace `TEMPLATE_CHARACTER_TAGS`, `TEMPLATE_POSE_TAGS` |
| `3` CLIPTextEncode | `inputs.text` | negative prompt: replace `TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES`, `TEMPLATE_POSE_CONFLICT_NEGATIVES` |
| `4` LoadImage | `inputs.image` | character anchor image, ComfyUI input-relative path |
| `5` LoadImage | `inputs.image` | pose reference image, ComfyUI input-relative path |
| `14` KSampler | `inputs.seed` | seed |
| `16` SaveImage | `inputs.filename_prefix` | final pose source output prefix |
| `17` SaveImage | `inputs.filename_prefix` | OpenPose control preview output prefix |

Only tune node structure, IPAdapter weight, ControlNet strength, denoise, sampler, or resolution in `00_experiment_sandbox/` first.

## Input rules

ComfyUI `LoadImage.image` uses a path relative to the Windows ComfyUI input folder.

WSL input root:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

Example API values:

```text
TEMPLATE_character_anchor.png
TEMPLATE_pose_reference.png
```

Recommended input naming:

```text
hermes_identity_{character_slug}_anchor.png
hermes_pose_ref_{character_slug}_{pose_slug}.png
```

If a source exists only in ComfyUI output, copy it to input first.

## Clean prompt rules

All controllable prompt content should be Danbooru-style comma-separated tags.

Keep this clean background/style block in positive:

```text
thick_outline, clean_lineart, anime_coloring, grey_background
```

Use `grey_background` as the only positive background tag for 04. A same-seed sweep found it is enough for a neutral gray source and avoids redundant/competing background semantics.

Do not add these to positive:

```text
simple_background, flat_background, plain_background, dark_background, black_background,
depth_of_field, volumetric_lighting, spotlight, dramatic_lighting, rim_lighting
```

Keep these in negative unless a specific production case proves otherwise:

```text
black_background, dark_background, vignette, spotlight, dramatic_lighting, rim_lighting,
white_background, bright_background, gradient_background, patterned_background,
text, signature, watermark, username, logo,
badge, emblem, headwear, hair_ornament, object_above_head
```

Target pose tags must never appear in the negative prompt.

## Prompt blocks

### Shared positive skeleton

```text
masterpiece, best_quality, very_aesthetic, newest, rating_questionable,
1girl, solo, cowboy_shot, standing, looking_at_viewer,
{character_tags},
{pose_tags},
thick_outline, clean_lineart, anime_coloring,
grey_background
```

### Shared negative skeleton

```text
lowres, low_quality, worst_quality, bad_quality, very_displeasing,
bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, fused_fingers,
extra_arms, extra_hands, long_body, deformed, mutated, disfigured, ugly,
cropped, cropped_head, cropped_hair, out_of_frame,
multiple_girls, duplicate_character,
text, signature, watermark, username, logo,
{expression_conflict_negatives},
{pose_conflict_negatives},
large_breasts, huge_breasts, cleavage, nude, nipples,
badge, emblem,
white_background, bright_background, gradient_background, patterned_background,
black_background, dark_background, vignette, spotlight, dramatic_lighting, rim_lighting,
headwear, hair_ornament, object_above_head
```

## Character tag examples

Silver bob example:

```text
short_hair, bob_cut, silver_hair, blue_eyes,
beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose,
long_sleeves, small_breasts
```

Pink twin-braids example:

```text
pink_hair, twin_braids, long_hair, blue_eyes,
sailor_collar, white_sailor_shirt, short_sleeves, pink_bowtie, blue_skirt, pleated_skirt,
small_breasts
```

## Pose presets

Use one canonical workflow and swap only prompt blocks, seed, inputs, and prefixes.

| Pose slug | Status | Positive pose block | Negative pose-conflict additions |
|---|---|---|---|
| `arms_crossed` | stable | `arms_crossed, crossed_arms, folded_arms` | `smile, open_mouth, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed` |
| `hand_chest` | stable | `hand_on_chest, hand_to_own_chest, hands_near_chest` | `smile, open_mouth, arms_crossed, crossed_arms, folded_arms, hands_on_hips, hands_in_pockets, hands_near_face` |
| `pointing` | caution | `pointing, pointing_at_viewer, outstretched_arm, index_finger_raised` | `smile, open_mouth, arms_crossed, crossed_arms, folded_arms, hands_on_hips, hands_in_pockets, hands_near_face` |
| `one_hand_hip` | caution | `hand_on_hip, one_hand_on_hip, other_arm_at_side` | `smile, open_mouth, arms_crossed, crossed_arms, folded_arms, hand_on_chest, hands_near_chest` |

Stable presets passed multi-character smoke and 02 alpha gate:

```text
arms_crossed
hand_chest
```

Caution presets were readable but need extra seed/user QA:

```text
pointing        # large/overemphasized hand risk
one_hand_hip    # stronger color/line/style drift risk
```

## Output naming

Recommended source output prefix:

```text
hermes_vn_pose/refgen_{character_slug}_{pose_slug}_openpose_ip065_cn100
```

Recommended control preview prefix:

```text
hermes_vn_pose/control_{character_slug}_{pose_slug}_openpose_preview
```

ComfyUI appends suffixes like `_00001_.png`.

Alpha output is not generated here. Use 02 naming after source QA:

```text
hermes_vn_pose_alpha/alpha_{character_slug}_{pose_slug}_b1_ref1
```

## Agent recipe

1. Pick a target character anchor/source from 01.
2. Pick or create a pose reference image.
3. Copy both images to `/mnt/c/Users/Desktop/Documents/ComfyUI/input` if needed.
4. Load `workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json`.
5. Edit node `4` character anchor and node `5` pose reference.
6. Replace `TEMPLATE_CHARACTER_TAGS` in node `2` with Danbooru character/outfit tags.
7. Replace `TEMPLATE_POSE_TAGS` in node `2` with one pose preset.
8. Replace node `3` template negative placeholders with pose-safe conflict negatives.
9. Set node `14` seed.
10. Set node `16` and `17` filename prefixes.
11. Check ComfyUI `/queue` before submitting.
12. Run via `/prompt`.
13. Review final source and control preview.
14. If source passes, send it to `../02_toonout_transparency_alpha/`.
15. QA alpha on light and dark composites before claiming Ren'Py readiness.

## QA checklist

Source PNG:

- Same character as anchor: hair color/style, eye color, face impression.
- Outfit key colors/items preserved enough for the VN route.
- Target pose is readable at thumbnail size.
- Hands/arms/shoulders are not catastrophically broken.
- Head/hair/crop are intact.
- Background is clean flat grey/neutral, not dark/vignetted.
- No badge/emblem/headwear/text/logo contamination.

Alpha PNG through 02:

- Actual RGBA alpha.
- Hair tips are not aggressively clipped.
- Light background has no severe dark halo.
- Dark background has no severe bright rim or gray residue.
- Hands, sleeves, skirt, and clothing edges stay intact.

## Promotion evidence

Promoted on 2026-05-13 from `00_experiment_sandbox` after:

```text
1. clean prompt mask-only arms_crossed smoke passed
2. multi-pose smoke passed for silver_bob:
   arms_crossed, hand_chest stable
   pointing, one_hand_hip caution
3. second-character smoke passed for pink_twinbraids:
   arms_crossed, hand_chest stable
   pointing caution
4. 02 alpha gate passed for:
   silver arms_crossed
   silver hand_chest
   pink arms_crossed
   pink hand_chest
```

Reference QA artifacts outside reusable pack:

```text
ComfyUI/output/hermes_vn_pose_clean_prompt/contact_batch1_clean_prompt_outputs.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/contact_batch1_clean_multi_pose_outputs.png
ComfyUI/output/hermes_vn_pose_clean_second_character/contact_batch1_second_character_outputs.png
ComfyUI/output/hermes_vn_pose_alpha_gate/contact_batch1_pose_alpha_light_dark.png
ComfyUI/output/hermes_vn_pose_bg_tag_sweep/contact_batch2_bg_tag_same_seed.png
```

Background tag decision:

```text
2026-05-13: same-seed sweep selected positive `grey_background` only. `simple_background` was redundant, `flat_background` skewed warmer/beige, and `dark_background` conflicted with neutral gray.
```

Sandbox notes:

```text
00_experiment_sandbox/notes/04_pose_clean_prompt_masked_ipadapter_2026-05-13.md
00_experiment_sandbox/notes/04_pose_clean_baseline_multipose_secondchar_2026-05-13.md
00_experiment_sandbox/notes/04_pose_alpha_gate_2026-05-13.md
00_experiment_sandbox/notes/04_pose_background_tag_sweep_2026-05-13.md
```
