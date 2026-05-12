# 03 — 표정 변형

Category: `character`

## Purpose

기준 캐릭터 anchor/source 이미지를 유지하면서 smile/sad/angry/surprised 같은 표정 source 후보를 만든다.

03은 투명 PNG를 만들지 않는다. 표정 source 생성만 담당하고, 배경 투명화/alpha 처리는 02 workflow를 재사용한다.

## Output

표정별 source PNG 후보

## API templates

- `workflow_api/03_expression_source_canonical_api.json` — canonical expression source img2img/IPAdapter workflow | inputs: `TEMPLATE_character_anchor.png` | status: canonical source template

## Role split

```text
01 = 캐릭터 기준 anchor 생성
02 = 캐릭터/source 이미지를 Ren'Py용 투명 PNG로 변환
03 = 기준 캐릭터의 표정 source variation 생성
```

이 폴더에는 03 source 생성 workflow만 둔다. 이전의 표정별 alpha workflow는 02와 중복되므로 제거했다.

## Editable fields

보통 아래 항목만 수정한다.

- `LoadImage.image`: 기준 캐릭터 anchor/source 파일명
- positive prompt의 expression 구간
- 필요 시 `KSampler.denoise`
- 필요 시 `IPAdapterAdvanced.weight`
- `SaveImage.filename_prefix`
- seed

node 구조, checkpoint, sampler 구조는 바꾸지 않는다. 구조를 바꾸는 실험은 새 JSON으로 만들기 전에 먼저 목적을 명확히 기록한다.

## Inputs

기준 캐릭터 이미지는 ComfyUI input 폴더에 있어야 한다.

권장 입력:

```text
ComfyUI/input/hermes_vn_toonout_other_character/{character_anchor_or_source}.png
```

WSL에서 Windows ComfyUI input으로 복사할 때의 일반 경로:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/{character_anchor_or_source}.png
```

workflow 안의 기본 `TEMPLATE_character_anchor.png`는 실제 실행 전에 교체해야 하는 placeholder다.

## Expression prompting presets

기준은 `03_expression_source_canonical_api.json` 하나만 사용한다. 감정별 차이는 prompt와 소수의 strength 값으로만 관리한다.

| Expression | Positive prompt expression block | Denoise | IPAdapter weight | Use when |
|---|---|---:|---:|---|
| smile | `VERY warm gentle smile, clearly smiling mouth, happy eyes, cheerful friendly expression, not subtle expression` | `0.42` | `0.60` | 인물성 보존을 우선하면서 미소 추가 |
| sad | `VERY sad expression, trembling small frown, downturned eyebrows, glossy teary eyes, about to cry, vulnerable worried face, clearly readable sadness, not subtle expression` | `0.56` | `0.46` | 슬픔이 약하게 나올 때 강한 표정 변화 필요 |
| angry | `VERY angry annoyed expression, furrowed eyebrows, sharp glaring eyes, small frown, pouting angry mouth, clearly readable anger, not subtle expression` | `0.54` | `0.46` | 눈썹/눈매/입 모양 변화가 필요할 때 |
| surprised | `VERY surprised expression, wide open eyes, small open mouth, startled face, clearly readable surprise, not subtle expression` | `0.54` | `0.48` | 놀람 표정, 열린 입/커진 눈 필요 |

### Strength tuning rule

- 인물성이 무너지면: `denoise`를 낮추거나 `IPAdapter weight`를 올린다.
- 표정 변화가 약하면: expression block을 더 명확하게 쓰고, 그래도 부족할 때만 `denoise`를 조금 올린다.
- 헤어/의상/눈 색이 바뀌면: prompt의 캐릭터 고정 구간을 보강하고 `denoise`를 낮춘다.
- 한 번에 여러 값을 바꾸지 않는다. prompt → denoise → IPAdapter weight 순서로 한 변수씩 조정한다.

## Output naming

권장 prefix:

```text
hermes_vn_expression/source_{character_slug}_{expression}
```

예시:

```text
hermes_vn_expression/source_auburn_smile
hermes_vn_expression/source_auburn_sad
hermes_vn_expression/source_auburn_angry
hermes_vn_expression/source_auburn_surprised
```

## Agent recipe

AI agent가 03 expression workflow를 실행할 때는 아래 순서만 따른다.

1. 01에서 통과한 캐릭터 anchor 또는 02 전 source 이미지를 선택한다.
2. source 이미지가 ComfyUI input 폴더에 없으면 복사한다.
3. `workflow_api/03_expression_source_canonical_api.json`을 로드한다.
4. `LoadImage.image`를 실제 기준 캐릭터 이미지 파일명으로 바꾼다.
5. 만들 감정에 맞춰 positive prompt의 expression block만 교체한다.
6. README의 preset 표를 기준으로 `denoise`와 `IPAdapter weight`를 맞춘다.
7. `SaveImage.filename_prefix`를 `hermes_vn_expression/source_{character_slug}_{expression}` 형식으로 바꾼다.
8. ComfyUI 제출 전 `/queue`가 비어 있는지 확인한다.
9. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
10. 투명 PNG가 필요하면 03 안에서 처리하지 말고 02 alpha workflow로 넘긴다.
11. 사용자가 명시적으로 요청하지 않으면 vision QA를 하지 않는다.
12. 사용자가 통과라고 말하면 README/`WORKFLOW_INDEX.json`에 user-approved 상태를 기록한다.

## QA checklist

표정 source 후보는 contact sheet 또는 실제 출력 비교로 확인한다.

- anchor와 같은 인물로 보이는가
- 헤어 길이/색/실루엣이 유지되는가
- 눈 색과 얼굴 인상이 유지되는가
- 의상 형태와 주요 색이 유지되는가
- 표정 차이가 작은 썸네일에서도 읽히는가
- 손/팔/머리카락이 새로 망가지지 않았는가
- 배경은 단순한 source 배경으로 유지되는가
- alpha가 필요하면 02 workflow 결과까지 따로 확인했는가

For game-ready promotion, verify actual outputs with contact sheet or Ren'Py screenshot. Do not rely on workflow theory alone.

## Smoke test

- 2026-05-13: ran `03_expression_source_canonical_api.json` with smile preset on `hermes_vn_toonout_other_character/source_auburn_ilV180_719238043_00001_.png`.
- ComfyUI prompt_id: `32bee936-3320-4e28-9724-96853b81a825`
- Output: `ComfyUI/output/hermes_vn_expression/source_auburn_smile_canonical_smoke_00001_.png`
- Result: execution passed. Visual smoke candidate shows a readable smile and single-character portrait; user approval still required before marking 03 user-approved.

## Removed duplicates

2026-05-13 cleanup:

- Removed 4 duplicated alpha workflows from 03 because alpha/background removal belongs to 02.
- Replaced 4 per-expression source workflows with one generic canonical workflow.
- Preserved expression-specific prompting and strength values in this README instead of separate JSON files.

## Extra files

- none
