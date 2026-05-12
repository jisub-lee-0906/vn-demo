# Canonical ComfyUI API workflow templates

This folder keeps only the best successful `/prompt` API templates for the completed 01-05 character/sprite chain.

Exploratory alternatives, weaker sweeps, and the weak pointing pose templates were removed. See `../CANONICAL_WORKFLOW_POLICY.md`.

## Completed canonical chain

01 character anchor:
- `01_character_anchor_seed719238043_api.json`

02 alpha:
- `02_alpha_toonout_o0_b0_ref0_api.json`

03 expressions:
- `03_expression_source_smile_keep_d0p42_w0p6_api.json` + `03_expression_alpha_smile_toonout_o0_b0_ref0_api.json`
- `03_expression_source_surprised_move_d0p54_w0p48_api.json` + `03_expression_alpha_surprised_toonout_o0_b0_ref0_api.json`
- `03_expression_source_sad_strong_move_d0p56_w0p45_api.json` + `03_expression_alpha_sad_toonout_o0_b0_ref0_api.json`
- `03_expression_source_angry_move_d0p54_w0p48_api.json` + `03_expression_alpha_angry_toonout_o0_b0_ref0_api.json`

04 pose donors:
- `04_pose_textonly_source_hand_chest_txt_s1_api.json` + `04_pose_alpha_hand_chest_toonout_o0_b0_ref0_api.json`
- `04_pose_textonly_source_hip_txt_s0_api.json` + `04_pose_alpha_one_hand_hip_toonout_o0_b0_ref0_api.json`
- `04_pose_textonly_source_cross_txt_s0_api.json` + `04_pose_alpha_arms_crossed_toonout_o0_b0_ref0_api.json`

05 same-character pose ref-generation:
- `05_pose_refregen_arms_crossed_d0p42_w0p60_api.json`
- `05_pose_refregen_one_hand_hip_d0p42_w0p60_api.json`
- `05_alpha_toonout_example_api.json`

## Background/CG templates

- `06_background_generation_no_text_api.json`: smoke-passed minimal no-text classroom baseline; use this for separate day/night base backgrounds.
- `07_background_variation_img2img_layout_lock_api.json`: smoke-passed rain/weather variation with layout lock; not for day/night conversion.
- `08_event_cg_no_text_story_beat_api.json`: smoke-passed sealed-envelope hallway hook CG candidate; RenPy screenshot QA still required.

## Required input images

Templates with `LoadImage` require generated outputs to be copied into:

```text
C:\Users\Desktop\Documents\ComfyUI\input
```

After cleanup, this backup does not keep PNGs. Recreate required inputs by running earlier canonical templates in order or by using `../run_zero_memory_replay_test.py` for the 01-05 chain.

## Queue example from WSL

```bash
cd /mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows
HOST=http://$(ip route | awk '/default/ {print $3; exit}'):8000
curl -fsS "$HOST/queue"
jq -n --argjson prompt "$(cat api_workflows/01_character_anchor_seed719238043_api.json)"   '{prompt:$prompt, client_id:"manual-replay"}'   | curl -fsS -H 'Content-Type: application/json' -d @- "$HOST/prompt"
```

## QA rule

API replayability is not game promotion readiness. Still require contact/full-size QA, alpha dark/checker QA where applicable, sprite-set consistency QA, and Ren'Py screenshot QA.

## Prompting guide

Do not infer prompting changes from filenames alone. Use `../CANONICAL_PROMPTING_GUIDE.md` for concrete prompt blocks, negative prompts, parameter ranges, and PASS/FAIL criteria for each canonical template.

08 update: `08_event_cg_no_text_story_beat_api.json` is smoke-passed for a no-text sealed-envelope hallway hook CG candidate; RenPy screenshot QA still required.


## Generation expansion API scaffolds

09 support character:
- `09_support_character_anchor_teacher_api.json`
- `09_support_character_alpha_toonout_api.json`

10 outfit/costume variation:
- `10_outfit_casual_img2img_ipadapter_api.json`
- `10_outfit_alpha_toonout_api.json`

11 prop/effect overlay:
- `11_prop_single_object_key_api.json`
- `11_prop_alpha_toonout_api.json`
- `11_effect_magic_shimmer_black_bg_api.json`

These are scaffold templates, not canonical/smoke-passed workflows yet. Run tiny smoke tests and artifact review before promoting them to canonical status. Audio workflows 12-14 are documented outside `api_workflows/` because their backend is not selected yet.
