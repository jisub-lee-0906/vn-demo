# 06 — 의상/코스튬 변형

Category: `character`

## Purpose

기존 캐릭터 source PNG를 입력으로 받아 얼굴/헤어/배경은 최대한 보존하고, 캐릭터 실루엣 안의 의상/몸 영역을 masked inpaint로 바꾼다. 06은 범용 의상 변경 workflow이며 hoodie 전용 workflow가 아니다.

```text
01 character source or approved opaque sprite source
→ 06 outfit/costume source PNG, final original-head + fail-closed cleanup composite
→ 02 expression if needed, or 03 alpha for transparent sprite
```

06은 투명 PNG를 직접 만들지 않는다. Ren'Py sprite용 alpha가 필요하면 06의 final output을 `03_toonout_transparency_alpha` workflow로 후처리한다.

## Active API template

Active `workflow_api/`에는 하나의 canonical JSON만 둔다.

- `workflow_api/06_outfit_pulid_i2i_canonical_api.json`
  - route: source image → BiRefNet character mask → Florence-2 face/hair/neck/hand masks → bilateral hand fallback → lower-side silhouette protection → hand/silhouette-safe full-body edit mask → masked inpaint → original head/hands composite → fail-closed auto collar/bow cleanup branch
  - edit mask: `character_alpha - protected_face_hair_neckdiff - protected_hands - lower_side_silhouette_protect`, constrained by character alpha
  - protection mask: Florence-2-large `face and hair` minus `the neck of the person`, union with `hair`, `face`, generic `hand`, `both hands`, `fingers`, deterministic bilateral hand fallback, and deterministic lower-side silhouette/rim protection
  - identity: PuLID uses the source image face as weak identity bias during outfit inpaint
  - preservation: final output composites the original face/hair and detected hands back over the outfit candidate
  - cleanup: deterministic `VN_AutoCollarCleanupMask` searches only a dynamic neck/chest ROI based on the head/face/hair protection bbox; if no reliable old collar/bow remnant is found, the cleanup mask is empty and the branch is effectively a no-op
  - checkpoint: `novaAnimeXL_ilV190.safetensors`
  - identity adapter: `ip-adapter_pulid_sdxl_fp16.safetensors`
  - Florence model: `Florence-2-large`
  - alpha/matting mask: `BiRefNet_toonout`
  - custom node dependency: `VN_AutoCollarCleanupMask`, `VN_AutoHandFallbackProtectionMask`, and `VN_AutoOutfitSilhouetteProtectMask` from `ComfyUI-VN-AutoMasks`
  - last smoke: 2026-05-14 v4c2 passed t5 green-glasses opaque QA, newly generated 01 pink-twinbraids cross-character 06 QA, and 03 alpha light/dark composite gate

Archived routes:

```text
workflow_packs/workflow_backup/06_outfit_costume_variation_legacy_full_i2i/06_outfit_pulid_full_image_i2i_legacy_api.json
workflow_packs/workflow_backup/06_outfit_costume_variation_optional_cleanup_manual/06_outfit_collar_cleanup_optional_api.json
```

## Output

The canonical workflow saves ten outputs per run.

| Output prefix | Node | Meaning | Use |
| --- | ---: | --- | --- |
| `protect_*_facehair_neckdiff_*` | `33` | face/hair protection mask preview | check that face/hair are protected and neck/collar can be edited |
| `protecthands_*` | `56` | Florence hand protection mask preview | check hands/fingers are protected without thigh/skirt false positives |
| `handfallback_roi_*` / `handfallback_added_*` / `handfallback_debug_*` | `63`-`65` | deterministic bilateral hand fallback previews | check missed lower-side hand is added and cardigan/skirt false positives stay out |
| `silhouette_protect_*` / `silhouette_debug_*` | `71` / `70` | lower-side rim/thigh protection previews | check old exterior contour and lower-body shrink are blocked before inpaint |
| `protectfull_*` | `57` | full protection mask preview | check face/hair/hands are protected |
| `mask_*_edit_nohands_*` | `34` | final hand-safe edit mask preview | check body/clothes/skirt/legs are editable, hands are black/protected, and background is not |
| `raw_*_inpaint_*` | `35` | raw outfit inpaint image | debugging only; do not use as final |
| `bodycomp_*` | `36` | raw outfit inpaint composited into original by edit mask | intermediate candidate |
| `final_*_original_head_hands_*` | `37` | pre-cleanup original-head-and-hands composite | checkpoint/debug candidate |
| `cleanup_debug_*` | `44` | auto-cleanup ROI/candidate/final mask overlay | verify cleanup did not target hoodie pocket/hem/details |
| `cleanup_mask_*` | `45` | auto-cleanup mask preview | should be local near old collar/bow or empty on clean outputs |
| `final_*_autoclean_*` | `46` | original-head composite plus fail-closed cleanup branch | actual 06 candidate output |

Important: the actual candidate is node `46`. Node `37` is a pre-cleanup checkpoint. Node `35` is raw inpaint and should not be used as the final asset.

## Editable nodes

Normally edit only these nodes at runtime.

| Node | Class | Field | What to edit |
| ---: | --- | --- | --- |
| `3` | `LoadImage` | `inputs.image` | ComfyUI input-relative source PNG path |
| `6` | `Florence2Run` | `text_input` | usually keep `face and hair`; tune only if mask misses hair/face |
| `7` | `Florence2Run` | `text_input` | usually keep `hair`; improves side/back hair protection |
| `8` | `Florence2Run` | `text_input` | usually keep `face`; improves face protection |
| `9` | `Florence2Run` | `text_input` | usually keep `the neck of the person`; subtracts neck from protected mask so collar/hood can regenerate |
| `47`/`48`/`58` | `Florence2Run` | `text_input` | hand protection prompts; normally keep `hand` / `both hands` / `fingers` because `left hand` and `right hand` can miss one side on front-facing sprites |
| `13` | `GrowMask` | `expand` | protected head/hair dilation; increase if hair is edited, decrease if collar cannot change |
| `50` | `GrowMask` | `expand` | hand protection dilation; increase only if finger/wrist edges are edited, decrease if cuffs fail to change |
| `16` | `GrowMask` | `expand` | edit mask dilation; increase if old outfit rims remain |
| `22` | `ApplyPulidAdvanced` | `weight`, `end_at` | identity bias; default is conservative |
| `23` | `CLIPTextEncode` positive | `text` | Danbooru-style character + target outfit prompt |
| `24` | `CLIPTextEncode` negative | `text` | common negative + old outfit conflict terms |
| `27` | `KSampler` | `seed`, `denoise`, `cfg` | main outfit candidate seed/strength |
| `38` | `VN_AutoCollarCleanupMask` | `mode`, ROI, coverage, grow/blur | normally keep default fail-closed settings; tune only if cleanup misses/removes too much |
| `41` | `KSampler` | `seed`, `denoise`, `cfg` | local cleanup seed/strength; normally keep default |
| `33`-`37`, `44`-`46` | `SaveImage` | `filename_prefix` | output folder/slug/seed labels |

Do not change unless debugging:

- BiRefNet character-mask route (`4`)
- Florence mask arithmetic (`10`-`18`)
- main/final composite route (`29`, `30`, `43`)
- checkpoint / PuLID model / inpaint conditioning route

## Fixed canonical settings

```text
checkpoint: novaAnimeXL_ilV190.safetensors
clip last layer: -2
character mask: BiRefNetRMBG(model=BiRefNet_toonout, mask_blur=1, refine_foreground=true)
Florence model: Florence-2-large fp16
protection prompts: face and hair / hair / face / the neck of the person / hand / both hands / fingers
protected head/hair mask dilation: GrowMask expand 8, blur kernel 7 sigma 3.0
protected hand mask dilation: GrowMask expand 2, blur kernel 5 sigma 2.0, then deterministic bilateral fallback via VN_AutoHandFallbackProtectionMask
silhouette protection: VN_AutoOutfitSilhouetteProtectMask(lower_start_y_ratio=0.50, side_width_ratio=0.25, rim_radius=8, thigh_start_y_ratio=0.80, thigh_width_ratio=0.34, blur=3)
edit mask: character mask - protected head/hair, then GrowMask expand 5, blur kernel 7 sigma 3.0, multiplied by character mask, then subtract protected hands and lower-side silhouette protection
PuLID weight: 0.72
PuLID start/end: 0.0 / 0.75
main sampler: euler_ancestral, normal, steps 28, cfg 5.0, denoise 0.80
pre-cleanup final: ImageCompositeMasked(destination=bodycomp, source=original, mask=protected_facehair_plus_hands)
auto-cleanup mask: VN_AutoCollarCleanupMask(mode=hoodie_collar_bow, roi_top_pad=28, roi_height=190, roi_width_scale=0.46, max_coverage=0.055, min_coverage=0.001, grow=12, blur=9); protect_mask input must be head/face/hair node 14, not the full hand/silhouette protection mask
cleanup sampler: euler_ancestral, normal, steps 28, cfg 4.8, denoise 0.86
final: ImageCompositeMasked(destination=precleanup_final, source=cleanup_raw, mask=cleanup_mask)
```

## Mask source contract

06 must regenerate masks for every source image. Do not reuse mask PNGs from another character/run.

In the active canonical JSON:

- the only `LoadImage` node is node `3`, the source character PNG
- there is no active `LoadImageMask` node
- head/hair protection mask nodes `6`-`14` are computed from node `3` via Florence-2 every run
- hand protection mask nodes `47`-`58` are computed from node `3` via Florence-2 every run; the canonical route uses generic `hand` + `both hands` + `fingers` union because side-specific `left hand` / `right hand` prompts can miss one visible hand on front-facing sprites; this is intentionally preferred over broad BodySegment arm masks because BodySegment can false-positive on thighs/skirt highlights
- character/edit mask nodes `4`, `15`-`18`, and `53` are computed from node `3` via BiRefNet + mask arithmetic every run
- auto-cleanup mask node `38` is computed from the current node `30` candidate plus the current run's node `4` and node `14` head/face/hair protection bbox; do not feed node `52`/`67` into cleanup ROI, because hand/silhouette masks extend the bbox downward and move cleanup to the torso/hem

If a contact sheet appears to show an old mask, first check the output prefix and prompt id. Similar front-facing sprites can produce similar white silhouette masks, but the mask must still have that character's own hair/pose silhouette. Never copy node `33`, `34`, or `45` mask previews into `input/` as runtime masks for this canonical workflow.

## Input rules

ComfyUI `LoadImage` uses paths relative to the Windows ComfyUI `input` folder.

WSL path:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

Recommended input location:

```text
ComfyUI/input/hermes_vn_outfit/{source_character}.png
```

JSON node `3` example:

```text
LoadImage.image = hermes_vn_outfit/source_silver_bob_neutral.png
```

If the source PNG exists only under ComfyUI `output`, copy it to `input` first.

```bash
mkdir -p /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_outfit
cp /mnt/c/Users/Desktop/Documents/ComfyUI/output/{run_folder}/{source_png}.png \
  /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_outfit/
```

## Prompt structure

Positive prompt should be Danbooru-style comma-separated tags.

```text
[quality block], [source character tags], [target outfit tags], [lower-body outfit tags if full outfit change], grey_background
```

Recommended quality block:

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest
```

Example source character tags:

```text
rating_questionable, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, small_breasts
```

Example target outfit tags:

```text
lavender_hoodie, light_purple_hoodie, hoodie, pullover_hoodie, long_sleeves, casual_clothes, hood_down, front_pocket, loose_hoodie, ribbed_cuffs, ribbed_hem, black_pleated_skirt, pleated_skirt, black_pantyhose
```

Background:

```text
grey_background
```

Notes:

- Face/hair preservation is handled by mask/composite, not by natural-language locks.
- Avoid natural language like `same face`, `same hair`, `casual weekend outfit` in the canonical prompt.
- If replacing the whole outfit, include both upper and lower outfit tags. Do not clip the mask to the upper body unless the user explicitly wants the lower body preserved.
- Add old outfit conflict tags to the negative prompt.

## Common negative prompt base

```text
modern, recent, old, oldest, text, signature, watermark, username, logo, emblem, badge, multiple_girls, duplicate_character, cropped_head, cut_off_hair, headwear, hat, different_face, different_hair, different_hairstyle, different_eye_color, changed_face, deformed, bad_anatomy, bad_hands, extra_arms, extra_hands, missing_fingers, extra_digits, fewer_digits, open_clothes, cleavage, nude, nsfw, white_background, black_background, gradient_background, patterned_background, vignette, (worst quality, bad quality:1.2)
```

For a hoodie replacing a school/cardigan outfit, append:

```text
school_uniform, cardigan, beige_cardigan, cream_cardigan, white_shirt, collared_shirt, bowtie, necktie, ribbon, blouse, blazer, jacket, old_clothes, previous_outfit, visible_old_clothing, leftover_clothing, shirt_collar, visible_collar, buttoned_shirt, buttons, waistband, exposed_midriff, belly_cutout
```

## Outfit presets

Use one JSON. Change prompts, seed, denoise, PuLID weight, and output prefixes at runtime.

| slug | positive outfit tags | negative additions | main denoise | PuLID weight | mask notes | seed examples |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `lavender_hoodie_black_skirt` | `lavender_hoodie, light_purple_hoodie, hoodie, pullover_hoodie, long_sleeves, casual_clothes, hood_down, front_pocket, loose_hoodie, ribbed_cuffs, ribbed_hem, black_pleated_skirt, pleated_skirt, black_pantyhose` | school/cardigan/old clothing conflicts | 0.80 | 0.72 | active full-body mask; node `46` is final autoclean output | `62018571` |
| `blue_denim_jacket` | `blue_denim_jacket, denim_jacket, open_jacket, unbuttoned_jacket, plain_white_t-shirt, white_t-shirt, blank_shirt, casual_clothes, long_sleeves, black_pleated_skirt, pleated_skirt, black_pantyhose` | cardigan/school/sailor/bow/hoodie conflicts plus `print_shirt, shirt_logo, clothes_writing, english_text, letters, brand_name` | 0.82 | 0.72 | plain-shirt anti-text prompt passed pink twin-braids smoke better than the earlier logo-prone denim prompt | `62018641` |
| `red_track_jacket` | `red_track_jacket, track_jacket, zip-up_jacket, white_stripes, athletic_clothes, long_sleeves, black_skirt, black_pantyhose` | cardigan/school/blouse/hoodie conflicts | 0.74 | 0.72 | saturated colors can drift linework; QA required | choose new seed |
| `yellow_summer_dress` | `yellow_dress, summer_dress, short_sleeves, casual_clothes` | cardigan/hoodie/jacket/school conflicts | 0.76 | 0.70 | full-body mask is appropriate; expect more body/silhouette change | choose new seed |

## Agent recipe: single outfit

1. Read root `AGENTS.md` and `WORKFLOW_INDEX.json`.
2. Pick an approved 01/source PNG. Prefer the opaque source over a transparent alpha PNG.
3. Copy the source into Windows ComfyUI `input` if needed.
4. Load `workflow_api/06_outfit_pulid_i2i_canonical_api.json`.
5. Replace node `3` `LoadImage.image` with the input-relative source path.
6. Set node `23` positive prompt: quality block + character tags + target outfit tags + `grey_background`.
7. Set node `24` negative prompt: common negative + old outfit conflict tags.
8. Set node `27` seed/denoise and node `22` PuLID weight if using a preset.
9. Keep node `38` cleanup default unless a smoke test shows false positives/false negatives.
10. Set node `33`-`37`, `44`-`46`, and `56`-`57` prefixes with character slug, outfit slug, and seed.
11. Check `/queue`; do not interrupt or clear shared Windows ComfyUI without approval.
12. Submit via `POST /prompt` and poll `/history/{prompt_id}`.
13. Review node `56` hand mask, node `34` edit mask preview, node `45` cleanup mask, and node `46` final output.
14. If the final output is accepted, run it through `03_toonout_transparency_alpha` and check light/dark edge QA.

## QA checklist

Required before claiming production-ready:

- protection mask covers face/hair and does not over-protect collar/hood/neck
- hand protection mask covers visible hands/fingers and does not false-positive on thighs/skirt
- edit mask covers full outfit/lower body when whole outfit changes are desired while excluding protected hands
- edit mask does not expose/change the background
- final candidate is node `46`, not raw node `35`
- face/eyes/hair silhouette match the original after original-head composite
- neck/hood/collar seam is acceptable
- hoodie hem/skirt/lower-body outfit reads as one coherent outfit
- cleanup mask is local near old collar/bow or empty on clean outputs; it must not target hoodie pockets/hem/details
- hands/wrists/sleeves are not broken
- old cardigan/shirt/bow remnants are not obvious
- 03 alpha light/dark composite has no severe halo/rim
- Ren'Py placement/readability passes if promoting to game asset

## Known limitations

- Florence masks can miss back/side hair on some characters. If hair is edited, increase node `13` expand or adjust prompts, then rerun mask preview.
- If node `9` over-subtracts neck/low hair, collar improves but hair tips may be less protected. QA the protection mask.
- The full-body mask can change skirt/legs. This is intended for whole-outfit changes; use an upper-body-clipped sandbox route only if the lower body must stay fixed.
- Florence hand prompts can miss a hand on some poses. Always inspect node `56`; if a hand is missed, try one-variable prompt alternatives (`hands`, `both hands`, `visible hands`) in sandbox before promotion. Avoid broad BodySegment arm masks unless gated/QA'd because they can false-positive on thigh/skirt highlights.
- `denoise=0.80` changes outfit more strongly but can alter body/skirt more than `0.74`; hands are now composited back from the source when detected.
- Auto cleanup is fail-closed and tuned for collar/bow remnants. If it misses a new type of artifact, do not broaden it blindly; add a controlled smoke or use a local/manual cleanup route in sandbox.
- This workflow outputs an opaque source image. Transparent sprites still require workflow 03.

## Notes for agents

- Do not add one JSON per outfit. Keep one canonical JSON and patch editable nodes at runtime.
- Do not store generated PNG/contact sheets inside this reusable pack.
- Treat `TEMPLATE_identity_source.png` and `{character_slug}`/`{preset_slug}`/`{seed}` in prefixes as placeholders to patch before live execution.
- The current active route is full-body face/hair/neck/hand-protected inpaint with integrated fail-closed cleanup, not the old full-image i2i or FashionSegment garment-local route.
