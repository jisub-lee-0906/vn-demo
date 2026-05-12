# 11 — 소품/효과 오버레이

Category: `prop_effect`

## Purpose

VN 화면에 얹을 단일 소품/key item/magic shimmer를 만든다.

## Output

overlay prop/effect

## API templates

- `workflow_api/11_effect_magic_shimmer_black_bg_api.json` — scaffold black-background magical shimmer additive overlay | inputs: - | status: SMOKE PASS candidate as black-background additive effect overlay
- `workflow_api/11_prop_alpha_toonout_api.json` — toonout alpha for selected prop source | inputs: hermes_prop_key_SOURCE_TO_PROCESS.png | status: SMOKE PASS on minimal key candidates seed61124024/61124021; RenPy placement QA still required
- `workflow_api/11_prop_single_object_key_minimal_api.json` — preferred minimal single old brass key prop source | inputs: - | status: SMOKE PASS: single key source seed61124024; alpha candidate passed black/gray/checker QA; RenPy placement QA still required

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

alpha/blend, 좌표 배치, 가독성 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
