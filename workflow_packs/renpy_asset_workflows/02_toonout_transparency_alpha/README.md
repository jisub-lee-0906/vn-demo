# 02 — 투명 스프라이트 알파/매팅

Category: `character`

## Purpose

캐릭터 이미지를 RenPy용 투명 PNG로 만든다.

## Output

alpha PNG sprite

## API templates

- `workflow_api/02_alpha_toonout_o0_b0_ref0_api.json` — canonical toonout alpha setting | inputs: hermes_other_auburn_seed719238043.png | status: USER_APPROVED canonical

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

밝은/어두운 배경 위 hair halo, edge 손실 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Alpha workflow guide

02는 새 캐릭터를 생성하는 단계가 아니라, 이미 생성된 캐릭터 이미지를 Ren'Py용 투명 PNG로 변환하는 단계입니다.

### 유지할 설정

`workflow_api/02_alpha_toonout_o0_b0_ref0_api.json`의 핵심 설정은 기본적으로 유지합니다.

```text
model: BiRefNet_toonout
mask_blur: 0
mask_offset: 0
refine_foreground: False
background: Alpha
background_color: #222222
```

이 설정은 01에서 통과한 캐릭터 anchor 7장에 대해 user-approved 된 기본 alpha 설정입니다.

### 주로 수정할 것

- `LoadImage.image`: alpha로 변환할 입력 이미지 경로
- `SaveImage.filename_prefix`: 출력 alpha 파일 prefix

보통 node 구조, model, blur, offset은 바꾸지 않습니다. hair edge가 망가지거나 halo가 심한 경우에만 새 실험 JSON을 별도 파일로 만듭니다.

### 입력 규칙

입력 이미지는 ComfyUI input 폴더에 있어야 합니다.

권장 위치:

```text
ComfyUI/input/hermes_vn_toonout_other_character/{source_filename}.png
```

WSL에서 Windows ComfyUI input으로 복사할 때의 일반 경로:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/{source_filename}.png
```

### 출력 규칙

권장 prefix:

```text
hermes_vn_toonout_other_character/alpha_{character_slug}_ilV180_{seed}
```

예시:

```text
hermes_vn_toonout_other_character/alpha_pink_twinbraids_ilV180_274916358
```

## Agent recipe

AI agent가 02 alpha/background-removal을 실행할 때는 아래 순서만 따릅니다.

1. alpha 처리할 source PNG를 선택합니다.
   - 보통 01, 03, 05, 10에서 생성된 캐릭터 이미지입니다.
2. source PNG가 ComfyUI `input/hermes_vn_toonout_other_character/`에 없으면 복사합니다.
3. `workflow_api/02_alpha_toonout_o0_b0_ref0_api.json`을 로드합니다.
4. node `LoadImage.image`를 입력 파일명으로 바꿉니다.
   - 예: `hermes_vn_toonout_other_character/source_pink_twinbraids_ilV180_274916358_00001_.png`
5. node `SaveImage.filename_prefix`를 alpha prefix로 바꿉니다.
   - 예: `hermes_vn_toonout_other_character/alpha_pink_twinbraids_ilV180_274916358`
6. ComfyUI에 제출하기 전 `/queue`가 비어 있는지 확인합니다.
7. 실행 후 사용자에게 `prompt_id`와 output path만 전달합니다.
8. 사용자가 명시적으로 요청하지 않으면 vision QA를 하지 않습니다.
9. 사용자가 통과라고 말하면 README/`WORKFLOW_INDEX.json`에 user-approved 상태를 기록합니다.

## QA checklist

사용자 또는 QA agent는 실제 PNG를 밝은 배경과 어두운 배경 위에 올려 확인합니다.

- 배경이 실제 alpha로 제거됐는가
- 머리카락 끝이 과하게 잘리지 않았는가
- 밝은 배경에서 어두운 halo가 심하지 않은가
- 어두운 배경에서 밝은 rim/잔여 배경이 심하지 않은가
- 손, 팔, 옷 외곽선이 녹거나 뭉개지지 않았는가
- Ren'Py 대사창/배경 위에서 sprite로 사용할 수 있는가

## Extra files

- none

## Smoke test

- 2026-05-13: ran 02 alpha on 7 generated character anchors. Execution passed; user-approved.

## User QA

- 2026-05-13: 02 alpha/background-removal workflow passed user QA on generated character anchors.
