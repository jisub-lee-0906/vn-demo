# 12 — SFX 생성

Category: `audio`

## Purpose

짧은 UI/문/마법/알림 효과음을 만든다.

## Output

wav/ogg SFX 후보

## API templates

- No ComfyUI API JSON. Use the scripts/templates in this folder.

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

피크/노이즈/RenPy 재생 지연 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- `sfx_taxonomy.md`
- `scripts/generate_ui_sfx.py`
