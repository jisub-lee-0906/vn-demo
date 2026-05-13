# 03 — 표정 변형

Category: `character`

## Purpose

01에서 승인된 캐릭터 anchor/source 이미지를 기준으로 VN 기본 표정 source PNG를 만든다.

03은 표정 source 생성만 담당한다. 투명 PNG가 필요하면 결과 source를 02 alpha workflow로 후처리한다.

기본 표정 세트:

```text
neutral, happy, sad, angry, disgusted, surprised, fearful
```

한국어 기준:

```text
무표정, 행복, 슬픔, 분노, 혐오/역겨움, 놀람, 두려움/공포
```

## Output

표정별 source PNG 후보.

## API templates

- `workflow_api/03_expression_source_canonical_api.json`
  - role: canonical expression source img2img/IPAdapter workflow
  - checkpoint: `novaAnimeXL_ilV180.safetensors`
  - input node: `3 LoadImage.image`
  - positive prompt node: `7 CLIPTextEncode.text`
  - negative prompt node: `8 CLIPTextEncode.text`
  - IPAdapter node: `6 IPAdapterAdvanced.weight`, `6 IPAdapterAdvanced.end_at`
  - sampler node: `10 KSampler.seed`, `10 KSampler.cfg`, `10 KSampler.steps`, `10 KSampler.sampler_name`, `10 KSampler.denoise`
  - output node: `12 SaveImage.filename_prefix`
  - default input placeholder: `TEMPLATE_character_anchor.png`
  - status: canonical source template, defaults set to nova-sensitive v1 identity-safe neutral

## Role in the pack

```text
01 = 캐릭터 기준 anchor 생성
02 = source 이미지를 Ren'Py용 투명 PNG로 변환
03 = 01 anchor/source를 기준으로 표정 source variation 생성
```

이 폴더에는 표정 source 생성 workflow만 둔다. 표정별 alpha workflow는 만들지 않는다.

## What the agent should edit

기본 생성에서는 아래 항목만 수정한다.

1. `3 LoadImage.image`
2. `7 CLIPTextEncode.text`의 expression block
3. `8 CLIPTextEncode.text`의 expression-specific negative additions
4. `6 IPAdapterAdvanced.weight`
5. `6 IPAdapterAdvanced.end_at`
6. `10 KSampler.seed`
7. `10 KSampler.cfg`
8. `10 KSampler.steps`
9. `10 KSampler.sampler_name`
10. `10 KSampler.denoise`
11. `12 SaveImage.filename_prefix`

특별한 이유가 없으면 아래는 바꾸지 않는다.

- checkpoint
- node 구조
- image size/framing prompt
- base style/background prompt
- VAE/checkpoint/CLIP/IPAdapter loader node

## Input rules

기준 캐릭터 이미지는 ComfyUI input 폴더에 있어야 한다.

권장 위치:

```text
ComfyUI/input/hermes_vn_toonout_other_character/{character_anchor_or_source}.png
```

WSL 경로:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_toonout_other_character/{character_anchor_or_source}.png
```

workflow 안의 `TEMPLATE_character_anchor.png`는 실행 전에 실제 input filename으로 교체한다.

예시:

```text
hermes_vn_toonout_other_character/source_navy_short_bob_apose_neutral_ilV180_719239101_00001_.png
```

## Fixed base prompt

Expression block 앞의 base prompt는 기본적으로 유지한다.

```text
masterpiece, best quality, very aesthetic, newest, 1girl, solo, anime style, cowboy shot, upper body character portrait, full head visible, complete hair visible, large centered character, clean face, consistent hair, consistent eyes, consistent outfit, same character, clean sharp anime lineart, flat solid medium gray background, plain uniform gray backdrop
```

## Nova-sensitive v1 identity-safe presets

`novaAnimeXL_ilV180.safetensors`는 표정/색상 prompt에 민감하다. 눈/머리/얼굴 동일성 유지가 우선이면 아래 v1 값을 먼저 사용한다.

규칙:

- 색상 단어를 추가하지 않는다.
- `VERY`, `huge`, `bright`, `beaming`, `happy eyes` 같은 강한 감정/얼굴 변화 단어를 먼저 쓰지 않는다.
- 표정은 입, 눈썹, 눈 뜸 정도의 짧은 mechanics로만 준다.
- 표정이 약해도 한 번에 여러 값을 바꾸지 않는다.
- v2 값보다 v1 값이 더 보수적이며, 현재 기본 권장값이다.

| slug | expression block | denoise | IPAdapter weight | IPAdapter end_at | cfg | steps | sampler | seed example |
|---|---|---:|---:|---:|---:|---:|---|---:|
| neutral | `neutral expression, relaxed closed mouth, calm eyes` | `0.18` | `0.86` | `1.0` | `5.2` | `26` | `euler_ancestral` | `719241000` |
| happy | `small gentle smile, mouth corners up, soft happy expression, relaxed eyes` | `0.24` | `0.84` | `1.0` | `5.3` | `26` | `euler_ancestral` | `719241001` |
| sad | `sad expression, slightly downturned mouth, raised inner eyebrows, worried soft eyes` | `0.28` | `0.82` | `1.0` | `5.4` | `26` | `euler_ancestral` | `719241002` |
| angry | `angry expression, furrowed eyebrows, narrowed eyes, small tense frown` | `0.30` | `0.80` | `1.0` | `5.5` | `26` | `euler_ancestral` | `719241003` |
| disgusted | `disgusted expression, uneasy grimace, displeased eyes, small uneven frown, uncomfortable face` | `0.30` | `0.80` | `1.0` | `5.5` | `26` | `euler_ancestral` | `719241004` |
| surprised | `surprised expression, widened eyes, raised eyebrows, small open mouth` | `0.32` | `0.78` | `1.0` | `5.6` | `26` | `euler_ancestral` | `719241005` |
| fearful | `fearful expression, worried raised eyebrows, anxious eyes, small tense mouth, scared face` | `0.31` | `0.79` | `1.0` | `5.6` | `26` | `euler_ancestral` | `719241006` |

## Negative prompt pattern

Use this common negative base:

```text
text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, cropped arms, out of frame, extra arms, extra hands, bad hands, low quality, worst quality, full body, tiny character, chibi, feet visible, shoes, white background, bright background, gradient background, green background, teal background, headwear, object above head, ribbon on head, bow on head, hair ornament, reference sheet, character sheet, sprite sheet, expression sheet, inset, profile card, changed hair, changed eyes, different face, face shape change, new hairstyle, different outfit
```

Add expression-specific negatives only when useful:

| slug | negative additions |
|---|---|
| neutral | `smile, happy, sad, angry, surprised, disgusted, fearful` |
| happy | `sad, angry, surprised, scared, disgusted` |
| sad | `smile, happy, angry, surprised, disgusted` |
| angry | `smile, happy, sad tears, surprised, disgusted` |
| disgusted | `angry glare, smile, happy, surprised, scared` |
| surprised | `smile, happy, angry, disgusted, sad crying` |
| fearful | `smile, happy, angry, disgusted, simple surprise` |

## Output naming

권장 prefix:

```text
hermes_vn_expression/source_{character_slug}_{expression}
```

Nova-safe batch 권장 prefix:

```text
hermes_vn_expression/source_{character_slug}_{expression}_novasafe_seed{seed}
```

예시:

```text
hermes_vn_expression/source_navy_short_bob_happy_novasafe_seed719241001
```

## Agent recipe: single expression

1. 01에서 통과한 캐릭터 anchor/source 이미지를 선택한다.
2. source 이미지가 ComfyUI input 폴더에 없으면 복사한다.
3. `workflow_api/03_expression_source_canonical_api.json`을 로드한다.
4. `3 LoadImage.image`를 실제 input filename으로 바꾼다.
5. `7 CLIPTextEncode.text`를 `[Fixed base prompt], [preset expression block]`으로 설정한다.
6. `8 CLIPTextEncode.text`를 `[common negative base], [expression-specific negative additions]`로 설정한다.
7. preset 표 기준으로 `6 IPAdapterAdvanced.weight`, `6 IPAdapterAdvanced.end_at`, `10 KSampler.cfg`, `10 KSampler.steps`, `10 KSampler.sampler_name`, `10 KSampler.denoise`, `10 KSampler.seed`를 설정한다.
8. `12 SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
9. 제출 전 ComfyUI `/queue`가 비어 있는지 확인한다.
10. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
11. 사용자가 요청하지 않으면 vision QA를 하지 않는다.
12. 사용자가 후보를 승인하면 상태 기록은 `WORKFLOW_INDEX.json`에 간단히 반영한다.

## Agent recipe: default 7-expression batch

1. 같은 anchor/source를 사용한다.
2. 위 v1 preset 표의 `neutral, happy, sad, angry, disgusted, surprised, fearful`를 순서대로 실행한다.
3. 한 표정당 seed를 다르게 둔다.
4. 출력 prefix에는 slug와 seed를 포함한다.
5. 사용자에게 각 `prompt_id`와 output path를 전달한다.
6. 사용자가 QA를 요청하면 contact sheet를 만든다.
7. 통과한 표정은 다시 만들지 말고, 약한 표정만 재실행한다.

## Tuning rules after user QA

- 얼굴/눈/머리가 바뀌면: denoise를 `0.02` 낮추거나 IPAdapter weight를 `0.02` 올린다.
- 표정이 너무 약하면: 먼저 expression block을 한두 단어만 조정한다.
- 그래도 약하면: denoise를 `0.02` 올리거나 IPAdapter weight를 `0.02` 낮춘다.
- 색상 단어를 추가하는 것은 마지막 수단이다. nova에서는 색상 단어가 얼굴/눈/헤어 drift를 유발할 수 있다.
- `happy`는 특히 민감하다. 강한 smile prompt보다 작은 입꼬리 변화가 안전하다.
- `disgusted`와 `fearful`은 읽힘이 약할 수 있다. 그래도 strong prompt로 바로 가지 말고 한 변수씩만 조정한다.
- `surprised`는 작은 열린 입 때문에 가장 잘 읽히지만 face drift도 확인한다.

## QA checklist

표정 source 후보는 contact sheet 또는 실제 출력 비교로 확인한다.

- anchor와 같은 인물로 보이는가
- 눈 색과 얼굴 인상이 유지되는가
- 헤어 길이/색/실루엣이 유지되는가
- 의상 형태와 주요 색이 유지되는가
- 표정 차이가 작은 썸네일에서도 읽히는가
- 손/팔/머리카락이 새로 망가지지 않았는가
- 배경은 단순한 source 배경으로 유지되는가
- alpha가 필요하면 02 workflow 결과까지 따로 확인했는가

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
