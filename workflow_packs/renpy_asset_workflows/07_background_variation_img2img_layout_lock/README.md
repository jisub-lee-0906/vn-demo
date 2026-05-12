# 07 — 레이아웃 고정 배경 변형

Category: `background`

## Purpose

기존 배경 구도를 유지하며 시간/날씨/분위기만 바꾼다.

## Output

layout-locked variation

## API templates

- `workflow_api/07_background_variation_img2img_layout_lock_api.json` — same-location rainy/weather variation with Canny ControlNet layout lock; day/night conversion excluded | inputs: TEMPLATE_bg_base_location.png | status: SMOKE PASS for rainy weather variation; day/night swaps fixed to separate 06 base generations

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

원본과 주요 오브젝트 위치/소실점 비교

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
