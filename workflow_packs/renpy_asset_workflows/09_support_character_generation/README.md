# 09 — 서포트 캐릭터 생성

Category: `character`

## Purpose

교사/친구/NPC 등 보조 캐릭터 anchor/alpha를 만든다.

## Output

support character anchor/alpha

## API templates

- `workflow_api/09_support_character_alpha_toonout_api.json` — toonout alpha for selected support-character source | inputs: hermes_support_teacher_SOURCE_TO_PROCESS.png | status: SMOKE PASS candidate on v2 teacher source; not game-promotion-ready
- `workflow_api/09_support_character_anchor_teacher_api.json` — scaffold support-character teacher neutral anchor | inputs: - | status: SMOKE PASS candidate after v2 prompt seed91420932; not game-promotion-ready

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

메인 캐릭터와 구분되면서 같은 VN 스타일인지 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
