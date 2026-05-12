# 02 — 투명 스프라이트 알파/매팅

Category: `character`

## Purpose

이미 생성된 캐릭터 source 이미지를 Ren'Py용 투명 PNG sprite로 변환한다.

02는 새 캐릭터를 만들지 않는다. 01/03/05/10에서 나온 source 이미지를 alpha PNG로 후처리하는 공통 workflow다.

## Output

투명 배경 alpha PNG sprite.

## API template

- `workflow_api/02_alpha_toonout_o0_b0_ref0_api.json`
  - role: shared toonout alpha/background-removal workflow
  - input node: `LoadImage.image`
  - output node: `SaveImage.filename_prefix`
  - status: user-approved canonical alpha setting

## Role in the pack

```text
01/03/05/10 = 캐릭터 source 이미지 생성
02 = source 이미지를 투명 PNG로 변환
```

다른 폴더에 별도 alpha workflow를 중복해서 만들지 않는다. 표정/포즈/의상 source도 alpha가 필요하면 02로 넘긴다.

## Fixed settings

아래 설정은 기본적으로 유지한다.

```text
model: BiRefNet_toonout
mask_blur: 0
mask_offset: 0
refine_foreground: False
background: Alpha
background_color: #222222
```

hair edge, halo, 손/옷 외곽선 문제가 심할 때만 새 실험 JSON을 별도 파일로 만든다. 기존 canonical JSON을 덮어쓰기 전에 사용자 승인을 받는다.

## What the agent should edit

보통 아래 2가지만 바꾼다.

1. `LoadImage.image`
2. `SaveImage.filename_prefix`

node 구조, model, blur, offset은 바꾸지 않는다.

## Input rules

입력 이미지는 ComfyUI input 폴더에 있어야 한다.

권장 위치:

```text
ComfyUI/input/hermes_vn_toonout_other_character/{source_filename}.png
```

WSL 경로:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/{source_filename}.png
```

예시 input filename:

```text
hermes_vn_toonout_other_character/source_auburn_apose_neutral_ilV180_719238045_00001_.png
```

## Output naming

권장 prefix:

```text
hermes_vn_toonout_other_character/alpha_{character_slug}_{variant}_ilV180_{seed}
```

예시:

```text
hermes_vn_toonout_other_character/alpha_auburn_apose_neutral_ilV180_719238045
hermes_vn_toonout_other_character/alpha_auburn_smile_ilV180_719238045
```

## Agent recipe

1. alpha 처리할 source PNG를 선택한다.
2. source PNG가 ComfyUI input 폴더에 없으면 복사한다.
3. `workflow_api/02_alpha_toonout_o0_b0_ref0_api.json`을 로드한다.
4. `LoadImage.image`를 실제 input filename으로 바꾼다.
5. `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
6. 제출 전 ComfyUI `/queue`가 비어 있는지 확인한다.
7. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
8. 사용자가 요청하지 않으면 vision QA를 하지 않는다.
9. 사용자가 후보를 승인하면 상태 기록은 `WORKFLOW_INDEX.json`에 간단히 반영한다.

## QA checklist

투명 PNG를 밝은 배경과 어두운 배경 위에 올려 확인한다.

- 배경이 실제 alpha로 제거됐는가
- 머리카락 끝이 과하게 잘리지 않았는가
- 밝은 배경에서 어두운 halo가 심하지 않은가
- 어두운 배경에서 밝은 rim/잔여 배경이 심하지 않은가
- 손, 팔, 옷 외곽선이 녹거나 뭉개지지 않았는가
- Ren'Py 대사창/배경 위에서 sprite로 사용할 수 있는가

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
