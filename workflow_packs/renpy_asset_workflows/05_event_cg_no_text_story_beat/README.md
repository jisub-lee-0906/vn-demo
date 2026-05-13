# 08 — 스토리 이벤트 CG

Category: `cg`

## Purpose

루트/이벤트용 한 장면 CG를 만든다.

## Output

텍스트 없는 event CG

## API templates

- `workflow_api/08_event_cg_no_text_story_beat_api.json` — smoke-passed no-text sealed-envelope / hallway hook event CG template | inputs: - | status: SMOKE PASS candidate: selected uppermid_s2 seed 812347402; RenPy route screenshot QA still required

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

손/얼굴/fake UI/fake text/RenPy 화면 focal point 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
