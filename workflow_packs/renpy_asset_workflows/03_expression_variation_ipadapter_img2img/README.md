# 03 — 표정 변형

Category: `character`

## Purpose

기준 캐릭터 anchor/source 이미지를 유지하면서 VN 기본 표정 source 후보를 만든다.

기본 표정 세트:

```text
neutral, happy, sad, angry, disgusted, surprised, fearful
```

한국어 기준:

```text
무표정, 행복, 슬픔, 분노, 혐오/역겨움, 놀람, 두려움/공포
```

03은 표정 source 생성만 담당한다. 투명 PNG가 필요하면 02 alpha workflow로 후처리한다.

## Output

표정별 source PNG 후보.

## API template

- `workflow_api/03_expression_source_canonical_api.json`
  - role: canonical expression source img2img/IPAdapter workflow
  - input node: `LoadImage.image`
  - output node: `SaveImage.filename_prefix`
  - default input placeholder: `TEMPLATE_character_anchor.png`
  - status: canonical source template

- `workflow_api/03_face_composite_masked_api.json`
  - role: outfit/body-lock postprocess for expression candidates
  - destination node: neutral/approved anchor `LoadImage.image`
  - source node: expression candidate `LoadImage.image`
  - mask node: inverted-alpha face mask `LoadImage.image`
  - output node: `SaveImage.filename_prefix`
  - status: optional refinement template for outfit drift

## Role in the pack

```text
01 = 캐릭터 기준 anchor 생성
02 = source 이미지를 Ren'Py용 투명 PNG로 변환
03 = 01 anchor/source를 기준으로 표정 source variation 생성
```

이 폴더에는 표정 source 생성 workflow만 둔다. 표정별 alpha workflow는 만들지 않는다.

## What the agent should edit

기본 생성에서는 아래 항목만 수정한다.

1. `LoadImage.image`
2. positive prompt의 expression block
3. `KSampler.denoise`
4. `IPAdapterAdvanced.weight`
5. `SaveImage.filename_prefix`
6. seed

사용자 QA 후 표정이 약하면 아래 고급 항목을 한 변수씩 조정할 수 있다.

7. `KSampler.cfg`
8. `KSampler.steps`
9. `KSampler.sampler_name` (`euler_ancestral` → `euler`)
10. `IPAdapterAdvanced.end_at`

node 구조와 checkpoint는 바꾸지 않는다. 구조 변경 실험은 목적을 명확히 기록하고 새 JSON으로 만든다.

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

workflow 안의 `TEMPLATE_character_anchor.png`는 실행 전에 실제 파일명으로 교체한다.

## Expression presets

하나의 canonical workflow를 사용하고, 감정별 차이는 아래 값만 바꾼다.

| Expression slug | Korean label | Positive prompt expression block | Denoise | IPAdapter weight | Use when |
|---|---|---|---:|---:|---|
| neutral | 무표정 | `neutral expression, calm face, relaxed closed mouth, normal eyes, no smile, no frown, no anger, no surprise, no fear, clean simple anime face` | `0.30` | `0.70` | 기본 앵커/source의 색·인물성이 흔들릴 때 기준 무표정 source가 필요할 때 |
| happy | 행복 | `VERY happy expression, warm bright smile, clearly smiling mouth, happy eyes, cheerful friendly face, clearly readable happiness, not subtle expression` | `0.42` | `0.60` | 인물성 보존을 우선하면서 기본 웃는 표정 필요 |
| sad | 슬픔 | `VERY sad expression, tiny anime nose, simple small nose, trembling small frown, downturned eyebrows, glossy teary eyes, about to cry, vulnerable worried face, clearly readable sadness, not subtle expression` | `0.52` | `0.52` | 슬픔이 약하게 나올 때 강한 표정 변화 필요. 코/얼굴 구조가 생기면 denoise를 낮추고 IPAdapter를 올린다. |
| angry | 분노 | `VERY angry expression, furrowed eyebrows, sharp glaring eyes, tense small frown, pouting angry mouth, clearly readable anger, not subtle expression` | `0.54` | `0.46` | 눈썹/눈매/입 모양 변화가 필요할 때 |
| disgusted | 혐오/역겨움 | `VERY disgusted expression, tiny anime nose, simple small nose, uneasy grimace, slightly raised upper lip, narrowed displeased eyes, repulsed face, clearly readable disgust, not subtle expression` | `0.52` | `0.52` | 불쾌함/역겨움/거부감이 읽혀야 할 때. `wrinkled nose`는 코 구조를 만들 수 있어 기본값에서 쓰지 않는다. |
| surprised | 놀람 | `VERY surprised expression, wide open eyes, raised eyebrows, small open mouth, startled face, clearly readable surprise, not subtle expression` | `0.54` | `0.48` | 놀람 표정, 열린 입/커진 눈 필요 |
| fearful | 두려움/공포 | `VERY fearful scared expression, widened anxious eyes, raised inner eyebrows, tense worried mouth, frightened vulnerable face, clearly readable fear, not subtle expression` | `0.56` | `0.46` | 공포/불안/겁먹은 표정이 필요할 때 |

`smile`은 과거 호환용 별칭으로만 사용한다. 새 기본 세트에서는 `happy`를 사용한다.

## Refined expression presets

기본 preset이 약하거나 표정 간 구분이 부족하면 아래 refinement preset을 우선 시도한다. 이 값들은 silver-bob cross-character QA에서 더 잘 읽힌 방향을 일반화한 것이다. 결과 이미지를 README에 고정하지 말고, 새 캐릭터마다 사용자 QA로 선택한다.

| Expression slug | Refinement direction | Positive prompt expression block | Denoise | IPAdapter weight | CFG | Steps | Sampler | IPAdapter end_at | Negative additions |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| happy | 눈웃음/큰 행복 | `VERY cheerful happy expression, huge beaming smile, happy closed crescent eyes, laughing smile, raised cheeks, delighted friendly face, joyful anime smile, mouth clearly smiling, pure happiness, readable from small game sprite, not subtle, not neutral` | `0.58` | `0.40` | `8.2` | `36` | `euler` | `0.55` | `neutral face, expressionless, subtle expression, barely changed expression, tiny smile, sad, worried, angry, disgusted, fearful, surprised, crying, smug grin, sarcastic smile` |
| sad | 코 구조 보존 + 눈물 | `VERY sad crying expression, tiny anime nose, simple small nose, smooth simple anime nose, raised inner eyebrows, downturned eyebrows, trembling open frown, quivering lips, watery glossy eyes, visible small tear drops, tear streaks, hurt vulnerable face, clearly readable sadness from small game sprite, not subtle` | `0.50` | `0.56` | `7.0` | `34` | `euler` | `0.72` | `happy, smile, smiling, angry, disgusted, surprised, fearful, big nose, long nose, pointed nose, nose bridge, nostrils, realistic nose, prominent nose, wrinkled nose, nose shadow` |
| angry | 혐오와 분리된 진지한 분노 | `SERIOUS angry expression, intense furious glare, strongly furrowed eyebrows, sharp narrowed angry eyes, tense straight eyebrows, clenched small frown, tight pressed mouth, stern rage, clearly readable anger from small game sprite, not subtle, no nausea, no disgust` | `0.56` | `0.44` | `7.6` | `36` | `euler` | `0.58` | `disgusted face, nausea, sick face, queasy, raised upper lip, grimace, surprised, fearful, tears` |
| disgusted | 시선 회피 + 역겨움 | `VERY disgusted repulsed expression, looking away to the side with narrowed displeased eyes, raised upper lip, awkward uneven grimace, mouth twisted downward to one side, eyebrows pinched in revulsion, sickened grossed-out reaction, clear "ew" face, visibly uncomfortable and rejecting, clearly readable disgust from small game sprite, not anger, not pout, not sad` | `0.58` | `0.42` | `8.0` | `36` | `euler` | `0.56` | `angry glare, furious, pout, pouting, clenched mouth, clenched teeth, symmetrical angry eyebrows, surprised, fearful, big nose, pointed nose, nose bridge, nostrils, realistic nose, prominent nose, wrinkled nose` |
| surprised | 공포와 분리된 순수 놀람 | `EXTREME surprised shocked expression, huge round wide open eyes, very raised eyebrows, small round open O mouth, startled gasp, sudden shock, bright alert face, clearly readable surprise from small game sprite, not fear, not worried, not sad` | `0.58` | `0.42` | `7.8` | `36` | `euler` | `0.55` | `fearful, scared, anxious, worried eyebrows, trembling mouth, angry, disgusted, smile` |
| fearful | 놀람과 분리된 불안/공포 | `VERY fearful terrified expression, scared anxious eyes, raised inner eyebrows, worried arched brows, trembling uneven mouth, small tense frown, pale frightened vulnerable face, about to cry from fear, shoulders tense, clearly readable fear from small game sprite, not surprise, not simple shocked face` | `0.58` | `0.44` | `7.8` | `36` | `euler` | `0.55` | `simple surprise, round O mouth, excited surprise, cheerful, wide happy eyes` |

Refinement preset은 표정을 더 읽히게 하는 대신 헤어/의상/얼굴 폭 drift 위험이 커진다. drift가 보이면 denoise를 `0.02` 낮추거나 IPAdapter weight를 `0.02` 올린다.

## Expression separation rules

- `happy`가 약하면 generic `smile`보다 `happy closed crescent eyes`, `huge beaming smile`, `raised cheeks`, `laughing smile`을 쓴다. `smug grin`, `sarcastic smile`, `tiny smile`은 negative에 넣는다.
- `disgusted`가 `angry`와 비슷하면 `furious`, `angry glare`, `clenched teeth`, `symmetrical angry eyebrows`를 negative에 넣고, positive는 `looking away`, `raised upper lip`, `uneven grimace`, `mouth twisted downward to one side`, `clear "ew" face`처럼 비대칭/거부감 중심으로 쓴다.
- `surprised`와 `fearful`이 비슷하면 `surprised`는 `round open O mouth`, `startled gasp`, `bright alert face`를 쓰고, `fearful`은 `worried arched brows`, `trembling uneven mouth`, `vulnerable`, `about to cry from fear`를 쓴다.
- `sad` 또는 `disgusted`에서 코가 이상해지면 positive에 `tiny anime nose`, `simple small nose`, `smooth simple anime nose`를 넣고 negative에 `big nose`, `long nose`, `pointed nose`, `nose bridge`, `nostrils`, `realistic nose`, `prominent nose`, `wrinkled nose`, `nose shadow`를 넣는다.
- refined preset도 한 번에 2~4개 후보만 만든다. 사용자가 가장 나은 후보를 고르면 그 방향으로만 추가 생성한다.

## Outfit/body drift fix: face-only composite

강한 표정 후보는 의상, emblem, cardigan fold, skirt, 손 모양이 같이 변할 수 있다. 이 문제는 표정 후보 전체를 쓰지 말고, 승인된 neutral anchor 위에 얼굴 영역만 합성해서 줄인다.

사용 workflow:

```text
workflow_api/03_face_composite_masked_api.json
```

동작:

```text
neutral/approved anchor = destination
expression candidate = source
face mask = mask
ImageCompositeMasked(source -> destination)
```

ComfyUI `LoadImage`의 mask 출력은 alpha를 `1 - alpha`로 읽는다. 따라서 face mask PNG는 아래처럼 만든다.

```text
투명 alpha 0   = 합성할 얼굴 영역
불투명 alpha 255 = 유지할 neutral/body 영역
feathered edge = seam 완화
```

권장 mask:

- 얼굴, 눈썹, 눈, 볼, 입, 턱 일부만 포함한다.
- 교복 collar, emblem, cardigan, skirt는 mask 밖에 둔다.
- 너무 큰 mask는 의상 drift까지 같이 복사한다.
- 너무 작은 mask는 표정이 약하거나 경계 seam이 생긴다.
- 1152x1536 upper-body source에서 silver-bob smoke는 `x=385, y=95, w=385, h=450, feather=45` face-only rectangle이 의상 보존에 더 적합했다. 캐릭터 구도마다 좌표는 다시 잡는다.

Face composite recipe:

1. 통과한 neutral anchor와 표정 candidate를 ComfyUI input 폴더에 둔다.
2. 같은 해상도의 inverted-alpha face mask를 만든다.
3. `03_face_composite_masked_api.json`에서 세 LoadImage 파일명을 교체한다.
4. `SaveImage.filename_prefix`를 아래 형식으로 바꾼다.

```text
hermes_vn_expression/source_{character_slug}_{expression}_face_composite
```

5. 결과를 neutral / whole-image expression / face-composite contact sheet로 비교한다.
6. 의상은 neutral과 같고 표정만 읽히면 face-composite 결과를 후속 02 alpha workflow로 넘긴다.

Face composite 한계:

- 머리카락/턱선이 크게 변한 표정 후보는 face mask 경계가 보일 수 있다.
- 표정 후보의 얼굴 위치가 neutral과 많이 다르면 합성이 어긋난다.
- 이런 경우 먼저 같은 anchor에서 표정 후보를 다시 뽑거나, mask를 조금 키우고 feather를 늘린다.

## Strength tuning rules

- 인물성이 무너지면: `denoise`를 낮추거나 `IPAdapter weight`를 올린다.
- 표정 변화가 약하면: expression block을 더 명확하게 쓰고, 그래도 부족할 때만 `denoise`를 조금 올린다.
- 헤어/의상/눈 색이 바뀌면: 캐릭터 고정 구간을 보강하고 `denoise`를 낮춘다.
- 머리색이 바뀌면: positive에 `same exact hair color`, 캐릭터별 색상 고정 문구를 넣고 negative에 `different hair color`를 넣는다. 필요하면 `denoise`를 `0.52` 근처로 낮추고 `IPAdapter weight`를 `0.52` 이상으로 올린다.
- 슬픔/혐오에서 코가 새로 생기면: `wrinkled nose`, `nose bridge`, `nostrils`, `realistic nose` 계열을 피하고 `tiny anime nose`, `simple small nose`를 쓴다.
- 한 번에 여러 값을 바꾸지 않는다. prompt → denoise → IPAdapter weight 순서로 한 변수씩 조정한다.
- 기본 preset에서 표정이 계속 약하면 refined preset 범위로 이동한다: `steps 34-36`, `cfg 7.0-8.4`, `denoise 0.50-0.62`, `IPAdapter weight 0.38-0.56`, `IPAdapter end_at 0.52-0.72`, `sampler euler`.
- `denoise 0.60+` 또는 `IPAdapter weight 0.40 이하`는 표정은 강해지지만 인물성 drift가 커질 수 있으므로 사용자 QA용 후보에만 사용한다.

## Output naming

권장 prefix:

```text
hermes_vn_expression/source_{character_slug}_{expression}
```

예시:

```text
hermes_vn_expression/source_auburn_neutral
hermes_vn_expression/source_auburn_happy
hermes_vn_expression/source_auburn_sad
hermes_vn_expression/source_auburn_angry
hermes_vn_expression/source_auburn_disgusted
hermes_vn_expression/source_auburn_surprised
hermes_vn_expression/source_auburn_fearful
```

## Agent recipe

1. 01에서 통과한 캐릭터 anchor/source 이미지를 선택한다.
2. source 이미지가 ComfyUI input 폴더에 없으면 복사한다.
3. `workflow_api/03_expression_source_canonical_api.json`을 로드한다.
4. `LoadImage.image`를 실제 기준 캐릭터 파일명으로 바꾼다.
5. 만들 감정에 맞춰 expression block만 교체한다.
6. preset 표 기준으로 `denoise`와 `IPAdapter weight`를 맞춘다.
7. `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
8. 제출 전 ComfyUI `/queue`가 비어 있는지 확인한다.
9. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
10. 의상/body drift가 보이면 `03_face_composite_masked_api.json`으로 face-only composite를 만든다.
11. 투명 PNG가 필요하면 02 alpha workflow로 넘긴다.
12. 사용자가 요청하지 않으면 vision QA를 하지 않는다.
13. 사용자가 후보를 승인하면 상태 기록은 `WORKFLOW_INDEX.json`에 간단히 반영한다.

## Refinement recipe after user QA

1. 사용자가 지적한 표정만 다시 생성한다. 통과한 표정은 다시 만들지 않는다.
2. 피드백을 실패 모드로 분류한다.
   - 표정 약함: refined preset 사용, `cfg/denoise` 소폭 상향
   - 표정 간 유사함: 서로 반대되는 negative additions 추가
   - 코/얼굴 구조 이상: 코 관련 negative 강화, IPAdapter weight 상향
   - 헤어/의상 drift: identity prompt 강화, denoise 하향
3. 한 표정당 2~4개 후보를 만든다.
4. 후보 이름에는 방향을 짧게 넣는다.

```text
hermes_vn_expression/source_{character_slug}_{expression}_{direction}_v{n}
```

예시:

```text
hermes_vn_expression/source_silver_bob_happy_closed_eyes_refine3
hermes_vn_expression/source_silver_bob_disgusted_averted_v4a
```

5. 사용자에게 번호, 방향, prompt_id, output path만 보고한다.
6. 사용자가 고른 후보가 workflow 자체에 유용한 일반 패턴이면 README preset/분리 규칙에 반영한다. 단, 특정 생성 결과 파일을 README에 누적하지 않는다.

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

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.


