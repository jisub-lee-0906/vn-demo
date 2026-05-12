# 01 — 캐릭터 기준 앵커 생성

Category: `character`

## Purpose

새 캐릭터의 기준 이미지와 고정 prompt/seed를 만든다.

## Output

02 alpha, 03 expression, 05 pose, 10 outfit의 기준 참조로 사용

## API templates

- `workflow_api/01_character_anchor_seed719238043_api.json` — canonical selected character anchor, updated to `novaAnimeXL_ilV180.safetensors` | inputs: - | status: PASS canonical / user-approved 01 anchor checkpoint ilV180

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

기준 인물성/헤어/의상 anchor가 안정적인지 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Prompting guide

01은 “나중에 계속 재사용할 캐릭터 기준 이미지”를 만드는 단계입니다. 프롬프트는 길게 쓰기보다, 고정할 핵심 특징만 짧게 바꿉니다.

### 유지할 것

- `anime style`, `cowboy shot`, `upper body character portrait`, `waist-up to upper-thigh visible` 같은 VN 스프라이트 구도 토큰
- `full head visible`, `complete hair visible`, `hands inside canvas` 같은 잘림 방지 토큰
- `1girl`, `solo`, `large centered character` 같은 단일 캐릭터 토큰
- negative의 `text`, `watermark`, `logo`, `cropped head`, `cut off hair`, `out of frame`, `extra hands`, `bad hands` 계열

### 캐릭터를 바꿀 때 주로 수정할 것

positive prompt 안의 캐릭터 정체성 부분만 교체합니다.

권장 교체 단위:

```text
[hair], [eye color], [outfit], [expression], [small accessory]
```

예시:

```text
short silver bob hair, cool blue eyes, navy cardigan, white blouse, calm intelligent expression
```

```text
pink twin braids, teal eyes, cream sailor uniform, cheerful bright smile, small star hairclip
```

```text
short moss green hair, amber eyes, round glasses, beige knit vest over white shirt, shy gentle expression
```

### 피할 것

- 세계관/성격 설명을 길게 넣기
- 한 번에 머리, 옷, 포즈, 배경, 표정, 소품을 모두 바꾸기
- `visual novel`, `game sprite` 같은 단어를 과하게 추가하기
- 배경 설명을 자세히 넣기. 01은 캐릭터 anchor가 목적입니다.
- 손/전신/신발을 강조하기. 01은 상반신 VN 기준 이미지입니다.

### seed/output 규칙

- 새 캐릭터 후보는 seed를 바꾸고 output prefix에 캐릭터 slug를 넣습니다.
- 비교용 모델 테스트는 filename에 checkpoint 이름을 넣습니다. 예: `source_auburn_ilV180_719238043`
- 템플릿의 canonical checkpoint는 현재 `novaAnimeXL_ilV180.safetensors`입니다.

### QA 기준

- 머리/얼굴이 잘리지 않음
- 상반신 VN 구도 유지
- 손/팔이 크게 깨지지 않음
- 배경, 글자, 로고, 워터마크 없음
- 02 alpha, 03 expression, 05 pose, 10 outfit의 기준으로 반복 사용 가능

## Agent recipe

AI agent가 새 캐릭터 anchor를 생성할 때는 아래 순서만 따릅니다.

1. `workflow_api/01_character_anchor_seed719238043_api.json`을 로드합니다.
2. checkpoint는 `novaAnimeXL_ilV180.safetensors`를 유지합니다.
3. positive prompt에서 캐릭터 정체성 구간만 교체합니다.
   - 권장 형식: `[hair], [eye color], [outfit], [expression], [small accessory]`
4. VN 스프라이트 구도 토큰은 유지합니다.
   - 예: `cowboy shot`, `upper body character portrait`, `waist-up to upper-thigh visible`, `full head visible`, `complete hair visible`, `hands inside canvas`
5. negative prompt는 특별한 이유가 없으면 유지합니다.
6. 새 seed를 설정합니다.
7. `filename_prefix`는 아래 형식을 사용합니다.

```text
hermes_vn_toonout_other_character/source_{character_slug}_ilV180_{seed}
```

8. ComfyUI에 제출하기 전 `/queue`가 비어 있는지 확인합니다.
9. 실행 후 사용자에게 `prompt_id`와 output path만 전달합니다.
10. 사용자가 명시적으로 요청하지 않으면 vision QA를 하지 않습니다.
11. 사용자가 통과라고 말하면 README/`WORKFLOW_INDEX.json`에 user-approved 상태를 기록합니다.

## Extra files

- none

## User QA

- 2026-05-13: 01 character anchor workflow approved for use with `novaAnimeXL_ilV180.safetensors`.
