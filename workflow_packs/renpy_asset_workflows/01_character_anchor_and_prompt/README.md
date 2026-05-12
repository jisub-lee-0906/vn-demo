# 01 — 캐릭터 기준 앵커 생성

Category: `character`

## Purpose

새 캐릭터의 재사용 가능한 기준 source 이미지를 만든다.

01의 기준은 예쁜 완성 포즈가 아니라 후속 workflow에서 다루기 쉬운 `A-pose + neutral expression` anchor다.

## Output

02 alpha, 03 expression, 04 pose, 10 outfit의 기준 참조로 사용할 character source PNG.

## API template

- `workflow_api/01_character_anchor_apose_neutral_api.json`
  - checkpoint: `novaAnimeXL_ilV180.safetensors`
  - role: canonical A-pose neutral character anchor
  - inputs: none
  - status: user-approved canonical

## Role in the pack

```text
01 = 캐릭터 기준 anchor 생성
02 = anchor/source 이미지를 Ren'Py용 투명 PNG로 변환
03 = 01 anchor를 기준으로 표정 variation 생성
04 = 01 anchor + pose reference로 포즈 variation 생성
10 = 01 anchor를 기준으로 의상 variation 생성
```

## What the agent should edit

보통 아래 3가지만 바꾼다.

1. positive prompt의 캐릭터 정체성 구간
2. `KSampler.seed`
3. `SaveImage.filename_prefix`

특별한 이유가 없으면 아래는 유지한다.

- checkpoint
- sampler/node 구조
- A-pose/neutral expression 구간
- negative prompt의 pose/hand/crop/sheet/text 방지 구간

## Canonical pose/expression target

생성 결과가 아래에 가까워야 한다.

```text
front view
standing character reference pose
relaxed A-pose
arms straight down at both sides
arms slightly away from body
visible open hands at sides
palms facing body
straight posture
shoulders level
neutral expression
closed mouth
calm blank face
upper body to mid-thigh visible
full head visible
complete hair visible
plain gray background
```

## Prompt editing pattern

positive prompt는 크게 두 덩어리로 본다.

```text
[fixed composition/pose/expression block], [character identity block], [fixed style/background block]
```

새 캐릭터를 만들 때는 character identity block만 교체한다.

권장 교체 단위:

```text
[hair], [eye color], clean face, [outfit], simple school uniform or outfit descriptor
```

예시:

```text
short silver bob hair, cool blue eyes, clean face, navy cardigan over white blouse, charcoal pleated skirt, simple school uniform
```

```text
pink twin braids, teal eyes, clean face, cream sailor uniform with pale pink ribbon, navy pleated skirt, simple school uniform
```

```text
short moss green hair, amber eyes, round glasses, clean face, beige knit vest over white shirt, brown pleated skirt, simple school uniform
```

01에서는 표정을 바꾸지 않는다. smile/sad/angry/surprised는 03에서 만든다.

## Negative prompt rules

A-pose neutral 기준에서는 아래 계열을 유지한다.

```text
smile, smiling, open mouth,
dynamic pose, tilted body, crossed arms,
hands together, hands near face,
hands on hips, hands on waist, hands in pockets,
akimbo, elbows bent, hidden hands, cropped hands,
clenched fists, fist, dramatic pose, sassy pose, leaning,
three-quarter view,
text, watermark, logo,
reference sheet, character sheet, sprite sheet, inset, profile card
```

## Output naming

권장 prefix:

```text
hermes_vn_toonout_other_character/source_{character_slug}_apose_neutral_ilV180_{seed}
```

예시:

```text
hermes_vn_toonout_other_character/source_auburn_apose_neutral_ilV180_719238045
```

## Agent recipe

1. `workflow_api/01_character_anchor_apose_neutral_api.json`을 로드한다.
2. 캐릭터 정체성 구간만 교체한다.
3. 새 후보라면 seed를 바꾼다.
4. `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
5. 제출 전 ComfyUI `/queue`가 비어 있는지 확인한다.
6. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
7. 사용자가 요청하지 않으면 vision QA를 하지 않는다.
8. 사용자가 후보를 승인하면 상태 기록은 `WORKFLOW_INDEX.json`에 간단히 반영한다.

## QA checklist

- 단일 캐릭터인가
- 무표정/닫힌 입인가
- 정면 기준인가
- A-pose 또는 팔 내림 reference pose인가
- 양손이 보이고 크게 깨지지 않았는가
- 머리/얼굴/손/치마가 잘리지 않았는가
- 상반신~허벅지 구도가 유지되는가
- 배경, 글자, 로고, 워터마크가 없는가
- 02/03/05/10의 기준 이미지로 재사용하기 쉬운가

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
