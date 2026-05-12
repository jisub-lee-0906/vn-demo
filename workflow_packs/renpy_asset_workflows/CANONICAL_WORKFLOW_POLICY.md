# Canonical workflow policy

Updated: 2026-05-12

The backup should keep only the best successful workflow template for each completed production step, not every exploratory sweep.

## Canonical completed chain kept

01. Character anchor:
- `01_character_anchor_seed719238043_api.json`

02. Transparent alpha:
- `02_alpha_toonout_o0_b0_ref0_api.json`

03. Expressions:
- smile: `03_expression_source_smile_keep_d0p42_w0p6_api.json` + alpha
- surprised: `03_expression_source_surprised_move_d0p54_w0p48_api.json` + alpha
- sad: `03_expression_source_sad_strong_move_d0p56_w0p45_api.json` + alpha
- angry: `03_expression_source_angry_move_d0p54_w0p48_api.json` + alpha

04. Pose donors:
- hand-to-chest: `04_pose_textonly_source_hand_chest_txt_s1_api.json` + alpha
- one-hand-on-hip: `04_pose_textonly_source_hip_txt_s0_api.json` + alpha
- arms-crossed: `04_pose_textonly_source_cross_txt_s0_api.json` + alpha

Pointing was weak, so its API templates are removed from the canonical pack.

05. Pose ref-generation:
- arms-crossed: `05_pose_refregen_arms_crossed_d0p42_w0p60_api.json`
- one-hand-on-hip: `05_pose_refregen_one_hand_hip_d0p42_w0p60_api.json`
- `05_alpha_toonout_example_api.json` as the reusable alpha step for ref-generated outputs

## Non-canonical removed

Alternate seeds, alternate alpha sweeps, keep/move comparison variants, stronger/weaker pose-ref alternatives, weak pointing, and replay-generated artifacts were removed.

## 06-08 background/CG status

`06_background_generation_no_text` is smoke-passed as the minimal no-text classroom background baseline. It is also the fixed route for separate day/night base backgrounds.

`07_background_variation_img2img_layout_lock` is smoke-passed and closed as a same-location rain/weather variation workflow. It is not a day/night conversion workflow; do not reopen 07 for bright-day-to-night swaps unless a new dedicated `07-night-extension` is explicitly created.

`08_event_cg_no_text_story_beat` is smoke-passed as a no-text sealed-envelope hallway hook CG candidate; RenPy screenshot QA is still required before game promotion.

06, 07, and 08 are API/template-smoke passed, not game-promotion-ready. Ren'Py screenshot QA is still required before semantic asset promotion.

## Prompting documentation rule

Canonical workflow template만 남기는 것으로는 부족합니다. 각 canonical template에는 실제 제작자가 무엇을 어떻게 바꾸면 되는지 알 수 있도록 `CANONICAL_PROMPTING_GUIDE.md`에 prompt block, negative block, parameter rule, PASS/FAIL gate를 함께 남깁니다.
