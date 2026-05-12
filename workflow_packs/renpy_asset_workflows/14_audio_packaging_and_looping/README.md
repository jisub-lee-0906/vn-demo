# 14 — 오디오 패키징/루프

Category: `audio`

## Purpose

SFX/BGM 파일명, manifest, loop 정보를 RenPy 투입 전 정리한다.

## Output

audio manifest

## API templates

- No ComfyUI API JSON. Use the scripts/templates in this folder.

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

경로/볼륨/loop_start/loop_end 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- `audio_manifest_template.json`
