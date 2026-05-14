# 04 — 텍스트 없는 배경 생성

Category: `background`

## Purpose

VN 장면 배경을 새로 만든다.

## Output

텍스트/UI/로고 없는 background

## API templates

- `workflow_api/04_background_generation_no_text_api.json` — minimal-smoke no-text classroom background baseline; also day/night base-generation route | inputs: - | status: SMOKE PASS: ilV190 minimal txt2img; use separate 06 generations for day/night; RenPy textbox QA still required

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

RenPy 대사창을 얹어 focal point와 fake text 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
