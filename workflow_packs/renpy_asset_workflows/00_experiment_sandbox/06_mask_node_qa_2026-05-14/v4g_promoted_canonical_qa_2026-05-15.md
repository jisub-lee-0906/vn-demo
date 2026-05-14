# 06 v4g promoted canonical QA — 2026-05-15

## Scope

Candidate: `workflow_packs/renpy_asset_workflows/06_outfit_costume_variation/workflow_api/06_outfit_pulid_i2i_canonical_api.json`

Goal: make the 06 outfit workflow reusable as the canonical full-outfit route, using `novaAnimeXL_ilV190.safetensors`, Danbooru-style prompts, conflict-free base negatives, CFG 4.5, and the v4e29 hand/foreground custom-node fixes.

## Live backend

Endpoint: Windows ComfyUI Desktop `http://127.0.0.1:8000`

Verified before smoke:

- queue empty
- PyTorch `2.10.0+cu130`
- device `cuda:0 NVIDIA GeForce RTX 5070 Ti`

## Promoted canonical deltas

- Positive prompt shortened and kept Danbooru/tag-only.
- Base negative prompt made generic/conflict-free; target outfit tags are not globally negated.
- Added pose/hand guards: `arms_at_sides`, `hands_down`, `relaxed_pose`; negatives for hand-on-chest/holding/clasped/crossed-arm failure modes.
- Main CFG lowered from `6.0` to `4.5` while keeping `denoise=0.92` and 28 Euler ancestral steps.
- Node `80` remains opaque diagnostic fullfit; node `82` is the foreground-cut RGBA candidate after QA.

## Smoke commands

Ran canonical JSON directly, patched only runtime source/prompt/prefix via the existing smoke harness:

```bash
python3 workflow_packs/renpy_asset_workflows/00_experiment_sandbox/06_mask_node_qa_2026-05-14/scripts/run_gpu_canonical_06_smoke.py \
  --endpoint http://127.0.0.1:8000 \
  --template workflow_packs/renpy_asset_workflows/06_outfit_costume_variation/workflow_api/06_outfit_pulid_i2i_canonical_api.json \
  --slug t5 --preset lavender_hoodie_black_skirt --run-slug v4g_promoted_canonical_gpu

python3 workflow_packs/renpy_asset_workflows/00_experiment_sandbox/06_mask_node_qa_2026-05-14/scripts/run_gpu_canonical_06_smoke.py \
  --endpoint http://127.0.0.1:8000 \
  --template workflow_packs/renpy_asset_workflows/06_outfit_costume_variation/workflow_api/06_outfit_pulid_i2i_canonical_api.json \
  --slug pink01 --preset lavender_hoodie_black_skirt --run-slug v4g_promoted_canonical_gpu
```

Prompt IDs:

- t5: `ab367846-c45f-4d50-bd8b-39be0ee09f89`
- pink01: `aca0545c-98ae-4021-86b6-f7bf4a232699`

Both completed with `status_str: success`.

## QA artifacts

All artifacts under:

`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_variation/`

Primary QA sheets:

- `v4g_promoted_canonical_gpu_strict_mask_contact_sheet.png`
- `v4g_promoted_canonical_gpu_alpha_bg_qa_sheet.png`
- `v4g_promoted_canonical_gpu_hand_cuff_closeup_sheet.png`

Representative finals:

- `v4g_promoted_canonical_gpu_final_t5_lavender_hoodie_black_skirt_fullfit_seed_62019146_00001_.png`
- `v4g_promoted_canonical_gpu_final_t5_lavender_hoodie_black_skirt_fullfit_foregroundcut_seed_62019146_00001_.png`
- `v4g_promoted_canonical_gpu_final_pink01_lavender_hoodie_black_skirt_fullfit_seed_62019146_00001_.png`
- `v4g_promoted_canonical_gpu_final_pink01_lavender_hoodie_black_skirt_fullfit_foregroundcut_seed_62019146_00001_.png`

## Vision QA result

Pass for hoodie canonical promotion.

Observed:

- t5 and pink01 both generate coherent lavender hoodie + black pleated skirt outfits.
- Face/hair identity is preserved by the original head/hair composite.
- Hands are present, not duplicated, and not obviously broken.
- Old cream/cardigan cuff sliver from earlier v4e28/v4e29 runs is no longer an obvious blocker in the promoted canonical smoke.
- Foreground-cut node `82` does not punch visible holes through hoodie/skirt on light/dark/gray composites.
- No severe alpha rim/halo or destructive hair/hand overcut was visible.

Caveats:

- Pink01 still has a few tiny hair-side/strand edge specks on light/dark composites; acceptable for node `82` candidate QA, but still check light/dark/gray if using as a production transparent sprite.
- Denim/jacket presets are stress/examples only. v4h denim prompt improved color but still tended to regenerate a neck bow/ribbon; do not claim non-hoodie presets are production-passed without separate visual QA.

## Promotion decision

Promote the v4g canonical JSON/README/WORKFLOW_INDEX state for 06 as the reusable hoodie/full-outfit canonical route.
