# 13 — BGM 프롬프트 설계

Category: `audio`

## Purpose

장면/루트 분위기에 맞는 BGM 프롬프트를 설계한다.

## Output

BGM prompt template

## API templates

- No ComfyUI API JSON. Use the scripts/templates in this folder.

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

loop 가능성, 대사 가독성 방해 여부 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- `bgm_prompt_templates.md`
