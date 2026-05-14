# 03 — 투명 스프라이트 알파/매팅

Category: `character`

## Purpose

이미 생성된 캐릭터 source PNG를 Ren'Py에서 바로 쓸 수 있는 투명 배경 PNG sprite로 변환한다.

03은 새 캐릭터, 새 표정, 새 포즈, 새 의상을 만들지 않는다. 아래 workflow들이 만든 회색/단색 배경 source 이미지를 alpha PNG로 후처리하는 공통 workflow다.

```text
01 character anchor source
02 expression source
06 outfit/costume source
→ 03 transparent alpha sprite
```

다른 폴더에 alpha workflow를 중복해서 만들지 않는다. 표정/포즈/의상 source도 투명 PNG가 필요하면 03으로 넘긴다.

## Output

- 출력물: alpha channel이 있는 transparent PNG sprite
- 용도: Ren'Py `show` 이미지, contact sheet QA, 배경/대사창 위 합성 QA
- 입력 source의 캐릭터 디자인은 바꾸지 않고 배경만 제거하는 것이 목표다.

## API template

- `workflow_api/03_alpha_toonout_b1_ref1_api.json`
  - role: shared ToonOut/BiRefNet alpha/background-removal workflow
  - input node: `1` LoadImage `inputs.image`
  - processing node: `2` BiRefNetRMBG
  - output node: `3` SaveImage `inputs.filename_prefix`
  - status: user-approved canonical alpha setting

Note: 03 should not be used to explain or cover up artifacts that are already visible in 01/02/06 opaque source outputs. If an artifact appears before alpha conversion, fix the upstream source/inpaint/mask workflow first.

## Editable nodes

보통 아래 2가지만 바꾼다.

| Node | Field | What to edit |
| --- | --- | --- |
| `1` LoadImage | `inputs.image` | ComfyUI input 폴더 기준 source image path |
| `3` SaveImage | `inputs.filename_prefix` | output prefix |

특별한 이유가 없으면 canonical workflow에서는 아래는 바꾸지 않는다.

- node 구조
- `BiRefNet_toonout` model
- `mask_blur`
- `mask_offset`
- `invert_output`
- `refine_foreground`
- `background`

`background_color`는 canonical JSON에서 의도적으로 제거되어 있다.

## Fixed canonical settings

현재 합격/유지 상태의 canonical 설정은 아래와 같다.
```text
model: BiRefNet_toonout
mask_blur: 1
mask_offset: 0
invert_output: false
refine_foreground: true
background: Alpha
# background_color intentionally omitted for Alpha output
```

의미:

- `background: Alpha`가 실제 투명 PNG를 만든다.
- `mask_blur: 1`, `mask_offset: 0`은 hair/detail 손실을 줄이는 기준값이다.
- `refine_foreground: true`는 v19 은발 anchor에서 어두운 배경 composite의 edge/rim을 줄인 현재 기준값이다.
- `background_color`는 `background: Alpha` 출력에서는 matte 개선에 도움이 되지 않아 canonical JSON에서 제거했다. 투명 PNG QA는 반드시 별도 밝은/어두운 배경 위에 올려 확인한다.

hair edge, halo, 손/옷 외곽선 문제가 심할 때만 새 실험 JSON 또는 별도 테스트 run을 만든다. canonical JSON을 덮어쓰기 전에는 사용자 승인을 받는다.

## Input rules

ComfyUI `LoadImage`는 Windows ComfyUI의 `input` 폴더 기준 상대 경로를 받는다.

WSL에서 보이는 input root:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

ComfyUI API에 넣는 `LoadImage.image` 값 예:

```text
hermes_vn_toonout_other_character/{source_png_filename}.png
```

실제 WSL 파일 위치 예:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/{source_png_filename}.png
```

source PNG가 ComfyUI `output` 폴더에만 있으면 실행 전에 `input` 폴더로 복사한다. 같은 subfolder 구조를 쓰면 관리가 쉽다.

예:

```bash
mkdir -p /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character
cp /mnt/c/Users/Desktop/Documents/ComfyUI/output/{run_folder}/{source_png_filename}.png \
   /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/
```

그 다음 JSON의 `LoadImage.image`는 아래처럼 쓴다.

```text
hermes_vn_toonout_other_character/{source_png_filename}.png
```

## Output naming

권장 prefix:

```text
hermes_vn_toonout_other_character/alpha_{character_slug}_{variant}_ilV190_{seed}
```

예시:

```text
hermes_vn_toonout_other_character/alpha_silver_bob_apose_neutral_ilV190_719242400
hermes_vn_expression/alpha_silver_bob_happy_ilV190_719242400
hermes_vn_pose/alpha_silver_bob_arms_crossed_ilV190_719242400
hermes_vn_outfit/alpha_silver_bob_lavender_hoodie_ilV190_719242400
```

ComfyUI는 실제 파일명 뒤에 `_00001_.png` 같은 suffix를 붙인다.

## Agent recipe

1. root `AGENTS.md`와 `WORKFLOW_INDEX.json`을 확인한다.
2. alpha 처리할 source PNG를 선택한다.
3. source PNG가 ComfyUI `input` 폴더에 없으면 복사한다.
4. `workflow_api/03_alpha_toonout_b1_ref1_api.json`을 로드한다.
5. node `1` `LoadImage.image`를 실제 input-relative filename으로 바꾼다.
6. node `3` `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
7. ComfyUI `/queue`가 비어 있는지 확인한다. 공유 Windows ComfyUI를 함부로 interrupt/clear하지 않는다.
8. `POST /prompt`로 실행한다.
9. `/history/{prompt_id}`에서 output path를 확인한다.
10. 사용자에게 `prompt_id`, input path, output path를 전달한다.
11. 사용자가 QA를 맡겠다고 했으면 자동 vision QA를 하지 않는다.
12. 사용자가 후보를 승인하면 `WORKFLOW_INDEX.json`에는 대표 상태/output만 짧게 반영한다.

## Batch use

여러 표정/포즈/의상 source를 처리할 때도 workflow JSON을 복제하지 않는다.

- 같은 canonical JSON을 deep-copy한다.
- 각 item마다 `LoadImage.image`와 `SaveImage.filename_prefix`만 바꾼다.
- queue 확인 후 순차 submit하거나, 사용자가 허락한 경우에만 batch submit한다.
- batch 결과는 reusable pack 안이 아니라 ComfyUI output run folder에 저장한다.

## QA checklist

투명 PNG는 최소한 밝은 배경과 어두운 배경 위에 올려 확인한다. 가능하면 Ren'Py 대사창이 있는 실제 화면에서도 확인한다.

필수 확인:

- 배경이 실제 alpha로 제거됐는가
- 머리카락 끝이 과하게 잘리지 않았는가
- 밝은 배경에서 어두운 halo가 심하지 않은가
- 어두운 배경에서 밝은 rim/잔여 배경이 심하지 않은가
- 손, 팔, 옷 외곽선이 녹거나 뭉개지지 않았는가
- 얼굴/머리/의상 색이 source와 비교해 불필요하게 변하지 않았는가
- 투명 영역에 회색/초록/흰색 배경 찌꺼기가 남지 않았는가
- Ren'Py 대사창/배경 위에서 sprite로 사용할 수 있는가

QA용 quick composite는 pack 밖의 임시/output 폴더에서 만든다. generated PNG/contact sheet를 이 reusable pack에 저장하지 않는다.

## When not to use 02

- source 캐릭터 자체가 마음에 들지 않으면 01/02/06에서 다시 생성한다.
- 표정이 틀렸으면 02를 사용한다.
- 의상 변경이 필요하면 06을 사용한다.
- 03은 배경 제거/alpha 처리만 담당한다.

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
- 03은 v19 은발 anchor smoke 이후 `mask_blur: 1`, `refine_foreground: true`, no `background_color` 기준으로 갱신된 canonical이다. 추가 튜닝은 비교 output과 사용자 승인이 있을 때만 반영한다.

## V190 silver-hair alpha tuning note

2026-05-13 canonical update after 01 v19 Danbooru silver-hair smoke:

- Use `mask_blur: 1` instead of `0`.
- Use `refine_foreground: true` instead of `false`.
- Remove `background_color`; with `background: Alpha` it does not improve matte extraction and can confuse docs.
- Keep `mask_offset: 0`, `invert_output: false`, `background: Alpha`, `model: BiRefNet_toonout`.
- Reason: on the accepted silver-bob v19 anchor, this reduced visible edge/rim artifacts on dark composite without noticeable hair/hand/clothing loss.

Accepted smoke artifacts:

- Source: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_background_test/source_grey_dark_neg_gradient_seed719251035_00001_.png`
- Alpha: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_toonout_other_character/alpha_grey_dark_neg_gradient_rftrue_blur1_seed719251035_00001_.png`
- QA sheet: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_background_test/contact_grey_dark_neg_gradient_source_alpha.png`
