# 04 — 텍스트 기반 포즈 donor/source 생성

Category: `character`

## Purpose

참조 포즈가 없을 때 donor/source 포즈 이미지를 만든다. 최종 캐릭터가 아니다.

## Output

05에 넣을 pose donor/source

## API templates

- `workflow_api/04_pose_alpha_arms_crossed_toonout_o0_b0_ref0_api.json` — canonical arms-crossed donor alpha | inputs: hermes_pose_selected_arms_crossed.png | status: PASS canonical
- `workflow_api/04_pose_alpha_hand_chest_toonout_o0_b0_ref0_api.json` — canonical hand-to-chest donor alpha | inputs: hermes_pose_selected_hand_chest.png | status: PASS canonical
- `workflow_api/04_pose_alpha_one_hand_hip_toonout_o0_b0_ref0_api.json` — canonical one-hand-on-hip donor alpha | inputs: hermes_pose_selected_one_hand_hip.png | status: PASS canonical
- `workflow_api/04_pose_textonly_source_cross_txt_s0_api.json` — canonical arms-crossed pose donor | inputs: - | status: PASS pose source canonical
- `workflow_api/04_pose_textonly_source_hand_chest_txt_s1_api.json` — canonical hand-to-chest pose donor | inputs: - | status: PASS pose source canonical
- `workflow_api/04_pose_textonly_source_hip_txt_s0_api.json` — canonical one-hand-on-hip pose donor | inputs: - | status: PASS pose source canonical

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

포즈 형태만 확인. 캐릭터 일관성은 05에서 판정

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
