# 05 — 이미지 참조 기반 포즈 재생성

Category: `character`

## Purpose

04 donor 또는 외부 포즈 이미지를 기존 캐릭터처럼 재생성한다.

## Output

최종 포즈 variant/alpha 후보

## API templates

- `workflow_api/05_alpha_toonout_example_api.json` — canonical reusable alpha for ref-generated pose outputs | inputs: hermes_refregen_alpha_SOURCE_TO_PROCESS.png | status: PASS canonical alpha step
- `workflow_api/05_pose_refregen_arms_crossed_d0p42_w0p60_api.json` — canonical arms-crossed same-character ref-generation | inputs: hermes_refregen_pose_arms_crossed_source.png, hermes_refregen_identity_auburn_719238043.png | status: PASS production-direction canonical
- `workflow_api/05_pose_refregen_one_hand_hip_d0p42_w0p60_api.json` — canonical one-hand-on-hip same-character ref-generation | inputs: hermes_refregen_pose_one_hand_hip_source.png, hermes_refregen_identity_auburn_719238043.png | status: PASS production-direction canonical

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

anchor와 비교해 얼굴/헤어/의상 유지, 손/edge 문제 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
