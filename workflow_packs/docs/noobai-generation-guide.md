---
title: "Crody Illustrious / NoobAI Image Generation Tips - AI Agent Knowledge Guide"
source_main_url: "https://civitai.red/articles/19107/crodys-illustrious-noobai-image-generation-tips"
source_title: "Crody's Illustrious / NoobAI Image Generation Tips"
source_author: "Crody / Team-C"
source_created_at: "2025-09-06T10:18:32.372Z"
source_updated_at: "2026-04-16T22:52:36.268Z"
local_created_at: "2026-05-15T00:22:29+09:00"
document_purpose: "향후 AI 에이전트가 Illustrious / NoobAI / Nova 계열 이미지 생성 설정과 프롬프트 구조를 빠르게 재사용하도록 구조화한 지식 문서"
tags:
  - Illustrious
  - NoobAI
  - Nova Anime XL
  - Nova Series
  - SDXL
  - ComfyUI
  - ADV_CLIP
  - sd_embed
  - Danbooru tags
  - prompt engineering
  - hires fix
  - VN asset workflow
  - anime image generation
---

# Crody Illustrious / NoobAI 이미지 생성 가이드

## Summary / 요약

이 문서는 Crody의 `Illustrious / NoobAI Image Generation Tips`와 문서 내부 참조 링크를 탐색해, AI 에이전트가 바로 검색·파싱·재사용할 수 있도록 재구성한 지식 문서다.

핵심 결론:

- 대상 모델: Illustrious / NoobAI 기반 모델, 특히 Nova Series 계열에 일반적으로 적용 가능한 팁.
- 기본 샘플러: `Euler A` 권장. Crody는 DPM++ 계열이 노이즈를 남기는 경향이 있어 비추천한다고 설명한다.
- 기본 CFG: `3.0 - 5.0`, 실사용 균형점은 `4.5`.
- 기본 steps: `20`.
- 기본 해상도: SDXL 계열 기준 100만 픽셀 안팎, 8의 배수. Crody 예시는 `768x1344`, `832x1216`, `1024x1024`, `1024x1536` 계열.
- Hires.fix: denoise `0.4 - 0.5`, scale `x1.5`, hires steps는 ComfyUI 등 현대 시스템 `16`, Diffusers `40` 예시.
- 긴 프롬프트/가중치 프롬프트: vanilla ComfyUI / vanilla Diffusers / Civitai onsite generator는 75 token 장벽과 weighting 제한이 있으므로, ComfyUI는 `ComfyUI_ADV_CLIP_emb`, Diffusers는 `sd_embed` 같은 고급 임베딩 방식을 사용.
- 프롬프트는 Danbooru 태그 기반으로, 소문자와 쉼표 구분을 지키고, 섹션 단위로 질서 있게 배열한다.
- 복잡한 프롬프트 구조: `품질/스타일/등급 -> 인원/상호작용 -> 캐릭터/신체/의상 -> 포즈 -> 카메라/배경 -> BREAK -> 조명/심도/후처리 -> 네거티브`.
- 연결 문서 `Illustrious Prompt Guide`는 Danbooru 기반 모델의 태그 순서, 문법, token limit, rare/unsupported tag 주의점을 보강한다.

## Keywords / Tags

`Illustrious`, `NoobAI`, `Nova Anime XL`, `Nova Series`, `SDXL`, `Euler A`, `CFG 4.5`, `20 steps`, `Hires.fix`, `denoise 0.4`, `x1.5 upscale`, `Danbooru tags`, `ADV_CLIP`, `sd_embed`, `long prompt weighted embedding`, `ComfyUI`, `Diffusers`, `anime prompt`, `VN sprite`, `character prompt`, `negative prompt`, `BREAK`, `tag order`, `quality tags`, `camera composition`, `lighting tags`

## 1. Source Map / 탐색한 문서와 참조 링크

### 1.1 메인 문서

| 항목 | 값 |
|---|---|
| 제목 | Crody's Illustrious / NoobAI Image Generation Tips |
| URL | https://civitai.red/articles/19107/crodys-illustrious-noobai-image-generation-tips |
| 작성자 | Crody / Team-C |
| 생성일 | 2025-09-06T10:18:32.372Z |
| 최종 수정 | 2026-04-16T22:52:36.268Z |
| 범위 | Illustrious / NoobAI / Nova Series 이미지 생성 설정, 프롬프트 구조, 예시 |

### 1.2 내부 참조 문서 / 도구

| 분류 | 링크 | AI 에이전트용 용도 |
|---|---|---|
| SDXL 해상도 | https://civitai.com/articles/2246/sdxl-image-size-cheat-sheet | 100만 픽셀 안팎, 8의 배수 해상도 선택 |
| Illustrious 프롬프트 | https://civitai.com/articles/16016/illustrious-prompt-guide-optimized-and-complete | Danbooru 기반 태그 순서, 문법, 금지/비권장 태그 확인 |
| ComfyUI 긴 프롬프트/가중치 | https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb | ComfyUI에서 긴 prompt weighting / token normalization 처리 |
| Diffusers 긴 프롬프트/가중치 | https://github.com/xhinker/sd_embed | Diffusers에서 77-token 제한을 넘어 weighted embedding 생성 |
| Danbooru Wiki | https://danbooru.donmai.us/wiki_pages | 태그 의미 확인 |
| Danbooru tag groups | https://danbooru.donmai.us/wiki_pages/tag_groups | 태그 그룹 색인 |
| Danbooru artists | https://danbooru.donmai.us/artists | artist tag 검색 |
| Danbooru character tags | https://danbooru.donmai.us/tags?commit=Search&search%5Bcategory%5D=4&search%5Bhide_empty%5D=yes&search%5Border%5D=date | character tag 검색 |

## 2. 권장 기본 설정값

### 2.1 Crody 기본 설정 테이블

| 설정 | 권장값 | 설명 / 주의 |
|---|---:|---|
| Model family | Illustrious / NoobAI / Nova Series | Crody 문서 기준. Nova Series에 일반 적용된다고 명시됨 |
| Sampler | `Euler A` / Euler Ancestral | Crody는 사실상 이것만 사용한다고 설명. DPM++ 계열은 노이즈 경향으로 비추천 |
| CFG scale | `3.0 - 5.0` | 6 이상은 Pony/Animagine식으로 너무 vivid해질 수 있음 |
| CFG practical default | `4.5` | controllability와 contrast 균형점으로 제시 |
| LCM CFG | `4.0 - 8.0`, 균형점 `6.0` | LCM 사용 시 예외 범위 |
| Steps | `20` | lighting LoRA 등은 해당 모델 권장 steps 우선 |
| Base size | `1024x1024` 또는 `1024x1536` 규칙 | SDXL/Illustrious 계열 기준 |
| Portrait examples | `768x1344`, `832x1216` | Crody가 portrait에 자주 쓰는 예시 |
| Hires denoise | `0.4 - 0.5` | 초기 이미지 보존과 디테일 강화의 균형 |
| Hires scale | `x1.5` | `x2.0` 이상은 오류/깨짐 가능성 증가 |
| Hires steps - ComfyUI | `16` | modern systems 예시 |
| Hires steps - Diffusers | `40` | Crody의 Diffusers 예시 |
| Upscaler example | `Nearest-exact` | 예시 설정에서 사용 |

### 2.2 ComfyUI용 시작 preset

```yaml
model_family: Illustrious/NoobAI/Nova
sampler: Euler A
scheduler: normal  # 문서에서 scheduler는 세부 지정 없음. ComfyUI 워크플로 기본값과 모델 권장값 우선.
steps: 20
cfg: 4.5
base_resolution:
  portrait_recommended:
    - 768x1344
    - 832x1216
  square_reference:
    - 1024x1024
hires_fix:
  enabled: true
  scale: 1.5
  denoise: 0.4-0.5
  hires_steps: 16
  hires_sampler: Euler A
  upscaler: Nearest-exact
prompt_embedding:
  vanilla_clip_warning: "긴 weighted prompt는 75/77 token 제한으로 품질 저하 가능"
  comfyui_recommended_extension: "ComfyUI_ADV_CLIP_emb"
```

## 3. SDXL 해상도 가이드

참조: https://civitai.com/articles/2246/sdxl-image-size-cheat-sheet

해당 문서는 SDXL에서 `1024 x 1024 = 1,048,576` 정도의 약 100만 픽셀을 목표로 하고, width/height를 8의 배수로 맞추라고 설명한다.

| 비율/용도 | 권장 예시 |
|---|---:|
| Portrait 2:3 | `832x1248` |
| Standard 3:4 | `880x1176` |
| Large Format 4:5 | `912x1144` |
| Square 1:1 | `1024x1024` |
| Widescreen 16:9 | `1360x768` |
| Golden Ratio | `1296x800` |
| Crody portrait 예시 | `768x1344`, `832x1216` |
| Crody cover/thumbnail 예시 | `1488x696` |

AI 에이전트 판단 규칙:

```text
IF generating SDXL/Illustrious image:
  prefer total_pixels ~= 1,048,576
  require width % 8 == 0 and height % 8 == 0
  for portrait character/VN sprite concept:
    try 832x1216 or 768x1344
  for square testing:
    try 1024x1024
  avoid jumping directly to x2 hires unless artifact QA passes
```

## 4. 긴 프롬프트 / 가중치 프롬프트 처리

Crody 문서의 중요 경고:

```text
이 prompting 방식은 vanilla ComfyUI, vanilla Diffusers, Civitai onsite generator에서 그대로 동작하지 않을 수 있다.
이유: weighting prompt 지원 부족 및 75-token barrier.
```

### 4.1 ComfyUI: ADV_CLIP

참조: https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb

README 핵심:

- `BNK_CLIPTextEncodeAdvanced` 노드 제공.
- prompt weighting 해석 방식을 더 세밀하게 제어한다.
- 주요 옵션:
  - `token_normalization`: `none`, `mean`, `length`, `length+mean`
  - `weight_interpretation`: prompt weight 해석 방식 제어

AI 에이전트 적용 메모:

```text
ComfyUI에서 Crody식 긴 프롬프트를 재현하려면 일반 CLIPTextEncode만으로는 부족할 수 있다.
워크플로에 ADV_CLIP 노드가 있는지 확인하고, 없으면 prompt 길이/가중치 재현성을 낮게 판단한다.
```

### 4.2 Diffusers: sd_embed

참조: https://github.com/xhinker/sd_embed

README 핵심:

- Stable Diffusion의 77-token prompt limitation을 넘기 위한 long prompt weighted embedding 생성 도구.
- SDXL, SD 1.5, SD3, Stable Cascade, Flux.1 등 여러 계열 예제가 포함됨.
- Crody는 Diffusers + `sd_embed` custom notebook으로 예시 이미지를 생성했다고 명시한다.

## 5. Prompt 구조: AI 파싱용 템플릿

Crody의 프롬프트 사고 방식은 “무엇을 그리지 말아야 하는가”를 먼저 생각한 뒤, 그림을 그리는 순서대로 요소를 정의하는 방식이다.

### 5.1 전체 구조

실제 prompt에 대괄호 설명문은 넣지 않는다. 아래는 구조 표시용이다.

```text
[1. Quality tags, styles and ratings]
[2. Person count and interaction]
{
  [3. Character name if needed + body modifiers from top to bottom including clothes]
  [4. Posing excluding interaction]
}  # multiple characters: repeat this block and separate each by BREAK
[5. Camera position and background]
BREAK
[6. Lighting, depth and after details]
...
[All. Negative prompts]
```

### 5.2 AI용 프롬프트 생성 알고리즘

```pseudo
build_prompt(scene_request):
  negative = default_negative_prompt + request_specific_unwanted_items

  positive = []
  positive += quality_style_rating_tags
  positive += person_count_and_interaction_tags

  for subject in subjects:
    positive += character_name_optional
    positive += body_description_top_to_bottom
    positive += clothing_top_to_bottom
    positive += pose_tags_excluding_interactions
    if multiple_subjects:
      positive += BREAK_between_subjects

  positive += camera_angle_view_focus_tags
  positive += background_tags
  positive += BREAK
  positive += lighting_depth_after_detail_tags

  enforce:
    lowercase_tags_unless_tag_requires_caps
    comma_separated_tags
    no_repeated_tags_for_strength; use weight or reorder instead
    escape_special_symbols_when needed: (), [], :
```

## 6. Prompt 문법 규칙

| 규칙 | 권장 | 비권장 / 주의 |
|---|---|---|
| 대소문자 | `masterpiece`, `best quality` | `Best Quality`처럼 임의 대문자 사용 금지. 단 태그 자체가 대문자를 포함하면 예외 |
| 구분자 | 쉼표로 태그 분리: `sleeveless, striped shirt, collared shirt` | 쉼표 없이 붙이면 태그 오인식 가능 |
| underscore | 강한 하위 태그 충돌 방지 시 사용: `fake_rabbit_ears` | `fake rabbit ears`가 `rabbit ears`로 과하게 먹힐 수 있음 |
| 특수문자 escape | A1111 등에서 `\:p`, `\:)` | `()[]:` 등은 시스템별 parser 혼동 가능 |
| 강조 방식 | weight 또는 tag 재배치 | 같은 태그 반복으로 강조하지 않기 |
| 이름 순서 | Danbooru 표기 순서: `kinoshita hideyoshi` | 역순 사용 지양 |
| token limit | 긴 프롬프트는 ADV_CLIP/sd_embed 사용 | vanilla 75/77 token 제한 무시 금지 |

## 7. Segment별 작성 규칙과 유용한 Danbooru 링크

### 7.1 Negative Prompt

Crody 기본 negative prompt:

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra fingers, extra digits, fewer digits, cropped, very displeasing, (worst quality, bad quality:1.2), sketch, jpeg artifacts, signature, watermark, username, (censored, bar_censor, mosaic_censor:1.2), simple background, conjoined, bad ai-generated
```

추가 원칙:

- 특정 undesired object나 artifact가 있으면 negative prompt 맨 앞에 추가.
- 참조 문서 `Illustrious Prompt Guide`는 negative prompt 30개 이상 과부하를 피하고, 정확한 positive prompt를 쓰라고 조언한다.
- 비교적 안정적인 negative tags 예시:

```text
monochrome, greyscale, multiple views, text, watermark, signature, translation request, comic, 4koma, 2koma
```

유용 링크:

- Flaws: https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition#dtext-flaws
- Metatags: https://danbooru.donmai.us/wiki_pages/tag_group%3Ametatags

### 7.2 Quality / Style / Rating

Crody 예시 quality tags:

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres
```

주의:

- Crody는 Pony식 score tags를 쓰지 말라고 조언한다. `score` 관련 글자가 이미지에 나타나는 문제가 있다고 언급.
- 참조 문서 `Illustrious Prompt Guide`는 `8k`, `4k`, `hdr`, `high quality`, `detailed`, `score_9` 등이 Danbooru에 없는 태그라 보통 비효과적이라고 설명한다.
- 두 문서 간 차이가 있으므로, workflow에서는 실제 모델별 artifact QA로 선택해야 한다.

AI 판단 메모:

```text
Crody/Nova 예시를 그대로 재현할 때는 Crody quality block 사용 가능.
정통 Danbooru tag fidelity를 우선할 때는 unsupported resolution/quality tags를 줄이고, 모델/LoRA 권장 프롬프트를 우선한다.
```

Style / era tags:

```text
newest, recent, mid, modern, early, old, oldest
1980s_\(style\), 2000s_\(style\)
```

Rating tags:

```text
general, sensitive, questionable, explicit
```

참조:

- Style parodies: https://danbooru.donmai.us/wiki_pages/list_of_style_parodies
- Visual aesthetic: https://danbooru.donmai.us/wiki_pages/tag_group%3Avisual_aesthetic
- Artists: https://danbooru.donmai.us/artists

### 7.3 Person Count / Interaction

예시:

```text
1girl, solo
2girls, back-to-back
```

참조:

- Groups: https://danbooru.donmai.us/wiki_pages/tag_group%3Agroups
- Family relationships: https://danbooru.donmai.us/wiki_pages/tag_group%3Afamily_relationships
- Two-person posture/interactions: https://danbooru.donmai.us/wiki_pages/tag_group%3Aposture#dtext-two

### 7.4 Character / Body / Clothes: top-to-bottom 방식

Crody는 신체와 의상을 위에서 아래로 작성하는 방식을 권장한다.

| 순서 | 태그 범주 | 참조 링크 |
|---:|---|---|
| 1 | character name | https://danbooru.donmai.us/tags?commit=Search&search%5Bcategory%5D=4&search%5Bhide_empty%5D=yes&search%5Border%5D=date |
| 2 | skin / head / ears / hair color / hair style | https://danbooru.donmai.us/wiki_pages/tag_group%3Askin_color, https://danbooru.donmai.us/wiki_pages/tag_group%3Aears_tags, https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-head, https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair_color, https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair_styles |
| 3 | headwear / eyewear / hair objects | https://danbooru.donmai.us/wiki_pages/tag_group%3Aheadwear, https://danbooru.donmai.us/wiki_pages/tag_group%3Aeyewear, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-headwear, https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair#dtext-objects |
| 4 | eyes | https://danbooru.donmai.us/wiki_pages/tag_group%3Aeyes_tags |
| 5 | face / expression | https://danbooru.donmai.us/wiki_pages/tag_group%3Aface_tags |
| 6 | neck / neckwear | https://danbooru.donmai.us/wiki_pages/tag_group%3Aneck_and_neckwear |
| 7 | shoulders / upper body / shirts | https://danbooru.donmai.us/wiki_pages/tag_group%3Ashoulders, https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-upper, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-shirts |
| 8 | lower body / pants | https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-lower, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-pants |
| 9 | legs / feet / shoes | https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-appendages, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-legs, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-shoes |
| 10 | style / fashion / patterns / prints | https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-styles, https://danbooru.donmai.us/wiki_pages/tag_group%3Afashion_style, https://danbooru.donmai.us/wiki_pages/tag_group%3Apatterns, https://danbooru.donmai.us/wiki_pages/tag_group%3Aprints |
| 11 | jewelry / accessories / body attire | https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-jewelry, https://danbooru.donmai.us/wiki_pages/tag_group%3Aaccessories, https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire |
| 12 | tail / wings | https://danbooru.donmai.us/wiki_pages/tag_group%3Atail, https://danbooru.donmai.us/wiki_pages/tag_group%3Awings |

### 7.5 Posing

참조:

- Gestures: https://danbooru.donmai.us/wiki_pages/tag_group%3Agestures
- Posture: https://danbooru.donmai.us/wiki_pages/tag_group%3Aposture
- On object: https://danbooru.donmai.us/wiki_pages/on

예시 태그:

```text
sitting, standing, jumping, kneeling, on back, on side, knee up, leg up, standing on one leg, arms up, arms behind head, arms behind back, hand on own hip, thumbs up, clenched hand, head tilt
```

### 7.6 Camera / Composition / Background

Crody 예시:

```text
dutch angle, wide shot, fisheye, from below, portrait, upper body, close-up, foreshortening
```

참조:

- Image composition: https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition
- Focus tags: https://danbooru.donmai.us/wiki_pages/tag_group%3Afocus_tags
- Backgrounds: https://danbooru.donmai.us/wiki_pages/tag_group%3Abackgrounds
- All tag groups: https://danbooru.donmai.us/wiki_pages/tag_groups

### 7.7 Lighting / Depth / After Details

참조:

- Lighting: https://danbooru.donmai.us/wiki_pages/tag_group%3Alighting
- Depth: https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition#dtext-depth

예시:

```text
rim light, backlit, colorful light particles, blurry foreground, bokeh, depth of field, volumetric lighting, detailed eyes
```

After details 작성법:

```text
detailed + target
# examples
detailed eyes
detailed background
detailed fluffy fur
```

## 8. Illustrious Prompt Guide 보강 요약

참조: https://civitai.com/articles/16016/illustrious-prompt-guide-optimized-and-complete

### 8.1 Dataset 전제

- Illustrious v0.1은 Danbooru2023 기반, 1024x1024 resolution, comma-separated Danbooru tags 및 일부 custom tags로 학습되었다고 설명된다.
- e621이나 PonyXL-style dataset이 아니라 Danbooru 중심이라는 점이 중요하다.
- 태그 의미를 모르면 Danbooru Wiki에서 확인한다.

### 8.2 권장 tag order

```text
person count, character name, rating, general tags, artist, score, year modifier
```

예시:

```text
1boy, kinoshita hideyoshi, general, building, itomugi-kun, masterpiece, newest
```

해석:

| 위치 | 예시 | 의미 |
|---|---|---|
| person count | `1boy` | 인물 수/성별 |
| character name | `kinoshita hideyoshi` | 캐릭터명 |
| rating | `general` | rating tag |
| general tags | `building` | 일반 내용 태그 |
| artist | `itomugi-kun` | artist/style source |
| score | `masterpiece` | 품질/score 성격 |
| year | `newest` | 연도/시대 modifier |

### 8.3 Token limit / Inpainting

```text
SDXL handles max 75 tokens.
Longer prompts are split and may reduce quality.
For complex scenes, use inpainting.
In inpainting, prompt only for the edited region, e.g. eye color or expression.
```

AI 에이전트 적용:

- 복잡한 VN 캐릭터 전체를 한 번에 바꾸려 하지 말고, 표정/눈색/의상 세부는 mask inpaint 또는 후속 workflow로 분리.
- prompt가 길어질 경우 ADV_CLIP/sd_embed 사용 여부를 QA 항목으로 넣는다.

### 8.4 비권장/주의 태그

| 유형 | 예시 | 이유 |
|---|---|---|
| unsupported tags | `8k`, `4k`, `hdr`, `high quality`, `detailed`, `score_9` | Danbooru에 없는 태그라 보통 ineffective라고 설명 |
| rare tags | Danbooru 이미지 수 100개 미만 | 모델이 안정적으로 학습하지 않았을 가능성 |
| ambiguous tags | `contortion`, `halo` 등 | 용례가 애매해 예측 불가 |
| redesign issue | `bridget (guilty gear)` 같은 특정 캐릭터 디자인 편중 | 구버전 디자인이 데이터에 적으면 LoRA 필요 |

## 9. 재사용 가능한 Prompt 템플릿

### 9.1 일반 portrait 템플릿

```text
masterpiece, best quality, amazing quality, very aesthetic, high resolution, ultra-detailed, absurdres, newest, scenery,
1girl, solo,
[character/body/hair/eyes/expression/clothes from top to bottom],
[pose/gesture],
[from below/from side/straight-on], [portrait/upper body/full body], [camera effect], [background],
BREAK,
detailed background, detailed eyes, blurry foreground, bokeh, depth of field, volumetric lighting
```

Negative:

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra fingers, extra digits, fewer digits, cropped, very displeasing, (worst quality, bad quality:1.2), sketch, jpeg artifacts, signature, watermark, username, simple background, conjoined, bad ai-generated
```

### 9.2 VN character sprite 응용 템플릿

현재 VN/ComfyUI pack에서 사용할 때는 Crody 구조를 유지하되, sprite 안정성을 위해 아래 제약을 추가한다.

```text
masterpiece, best quality, amazing quality, very aesthetic, high resolution, ultra-detailed, newest,
1girl, solo, single girl only, one character only, isolated standing character portrait,
[character identity], [hair/color/eyes/expression], [outfit from top to bottom],
standing, relaxed pose, looking at viewer,
straight-on, full body, centered composition, plain pure white background,
BREAK,
detailed eyes, clean outline, consistent character design
```

VN sprite negative 추가:

```text
character sheet, reference sheet, sprite sheet, expression sheet, multiple views, small inset, mini character, chibi, duplicate character, extra character, text, watermark, logo, ui, dialogue box, cropped feet, cropped head
```

### 9.3 VN background 응용 템플릿

```text
masterpiece, best quality, amazing quality, very aesthetic, high resolution, ultra-detailed, newest,
empty anime background art, architectural environment only,
[location], [time of day], [mood],
wide shot, straight-on, clean lower third for dialogue box,
BREAK,
detailed background, depth of field, volumetric lighting
```

VN background negative 추가:

```text
character, person, people, visual novel screenshot, game screenshot, dialogue box, textbox, nameplate, subtitles, captions, text, letters, words, ui, interface, overlay, watermark, logo
```

## 10. Crody 예시 설정과 프롬프트

### 10.1 Nova Anime XL IL v11.0 예시

설정:

```text
Initial image size: 768 x 1344
Steps: 20
CFG Scale: 4.5
Sampler: Euler A
Hires Factor: x1.5
Hires Steps: 16
Hires denoise: 0.4
Upscaler: Nearest-exact
Hires Sampler: Euler A
```

Prompt:

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, scenery, 1girl, solo, cute, pink hair, long hair, choppy bangs, long sidelocks, nebulae cosmic purple eyes, rimlit eyes, facing to the side, looking at viewer, downturned eyes, light smile, red annular solar eclipse halo, red choker, detailed purple serafuku, big red neckerchief, fingers, glowing stars in hand, arched back, from below, dutch angle, portrait, upper body, head tilt, colorful, rim light, backlit, (colorful light particles:1.2), cosmic sky, aurora, chaos, perfect night, fantasy background, BREAK, detailed background, blurry foreground, bokeh, depth of field, volumetric lighting
```

Segmented:

```text
[masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, scenery]
[1girl, solo]
[cute, pink hair, long hair, choppy bangs, long sidelocks, nebulae cosmic purple eyes, rimlit eyes, facing to the side, looking at viewer, downturned eyes, light smile, red annular solar eclipse halo, red choker, detailed purple serafuku, big red neckerchief]
[fingers, glowing stars in hand, arched back]
[from below, dutch angle, portrait, upper body, head tilt, colorful, rim light, backlit, (colorful light particles:1.2), cosmic sky, aurora, chaos, perfect night, fantasy background]
BREAK
[detailed background, blurry foreground, bokeh, depth of field, volumetric lighting]
```

### 10.2 Nova Furry XL Illustrious v11.0 fixed prompt 예시

```text
masterpiece, best quality, amazing quality, very aesthetic, 4k, high resolution, ultra-detailed, absurdres, newest, scenery, 1girl, furry, anthro, solo, phoenix fox girl, orange fur, long hair, multicolored glowing hair, gradient hair, flame hair, glowing orange hair, floating hair, hair between eyes, black headband with fire pattern, gradient orange yellow eyes, very large eyes, uneven eyes, facing to the side, looking at viewer, upturned eyes, intimidating, smirk, smug, grin, crazy smile, long snout, sharp teeth, black collar with white spikes, medium breasts, cropped leather flaming red jacket over collared impossible white shirt, underbust belt, portrait, upper body, close-up, foreshortening, dutch angle, (detailed fire forest background, fiery background:1.2), (blue fire:1.2) AND red fire, dark ambient, glow, BREAK, detailed eyes, detailed fluffy fur, depth of field, volumetric lighting
```

Segmented:

```text
[masterpiece, best quality, amazing quality, very aesthetic, 4k, high resolution, ultra-detailed, absurdres, newest, scenery]
[1girl, furry, anthro, solo]
[phoenix fox girl, orange fur, long hair, multicolored glowing hair, gradient hair, flame hair, glowing orange hair, floating hair, hair between eyes, black headband with fire pattern, gradient orange yellow eyes, very large eyes, uneven eyes, facing to the side, looking at viewer, upturned eyes, intimidating, smirk, smug, grin, crazy smile, long snout, sharp teeth, black collar with white spikes, medium breasts, cropped leather flaming red jacket over collared impossible white shirt, underbust belt]
[portrait, upper body, close-up, foreshortening]
[dutch angle, (detailed fire forest background, fiery background:1.2), (blue fire:1.2) AND red fire, dark ambient, glow]
BREAK
[detailed eyes, detailed fluffy fur, depth of field, volumetric lighting]
```

Negative:

```text
particles, 3d, rendered, human, multiple tails, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digits, fewer digits, very displeasing, (worst quality, bad quality:1.2), bad anatomy, sketch, jpeg artifacts, signature, watermark, username, simple background, conjoined, bad ai-generated
```

Crody의 설명상 fixed prompt는 clothing이 더 좋아지고, fur marks가 줄고, 일부 details가 더 제어되었다.

## 11. AI Agent Quick Decision Checklist

이미지 생성 전:

```text
[ ] 모델이 Illustrious/NoobAI/Nova 계열인가?
[ ] Sampler는 Euler A인가?
[ ] CFG는 3.0-5.0 범위인가? 기본값 4.5인가?
[ ] Steps는 20에서 시작하는가?
[ ] 해상도는 약 100만 픽셀이고 width/height가 8의 배수인가?
[ ] Hires scale은 x1.5 이하인가?
[ ] Hires denoise는 0.4-0.5인가?
[ ] 긴 prompt/weight가 있다면 ADV_CLIP 또는 sd_embed 같은 방식이 있는가?
[ ] prompt가 소문자, 쉼표 구분, Danbooru 태그 중심인가?
[ ] top-to-bottom character/body/clothes 순서인가?
[ ] `BREAK` 전후가 의도대로 분리되는 워크플로인가?
[ ] negative prompt가 과도하게 길거나 positive prompt와 충돌하지 않는가?
[ ] VN sprite/background 목적이면 text/UI/duplicate/character sheet 관련 negative를 추가했는가?
[ ] 생성 후 artifact QA로 얼굴/손/의상/텍스트/중복 인물/배경 UI 오염을 확인하는가?
```

## 12. Conflict / Caveat Notes

1. Crody 문서와 `Illustrious Prompt Guide`는 quality/resolution tag에 대한 태도가 일부 다르다.
   - Crody 예시: `4k`, `high resolution`, `ultra-detailed`, `absurdres` 사용.
   - Illustrious Prompt Guide: `8k`, `4k`, `hdr`, `high quality`, `detailed`, `score_9` 등은 Danbooru 태그가 아니라 대체로 비효과적이라고 설명.
   - AI 에이전트는 “문서 재현”과 “Danbooru fidelity” 중 목적을 구분하고, 최종 판단은 artifact QA로 한다.

2. `general` rating tag는 SFW 유도에 유용하지만, 참조 문서는 늦게 도입되어 content를 과하게 필터링할 수 있다고 설명한다.

3. character redesign 이슈가 있는 캐릭터는 prompt만으로 구버전/특정 디자인을 안정 재현하기 어렵다. 이 경우 LoRA나 reference-based workflow가 필요하다.

4. 복잡한 장면은 한 번에 긴 prompt로 해결하려 하기보다, inpainting / regional prompt / character reference / 후처리 compositing으로 분할한다.

## 13. Raw Source URLs

```text
Main:
https://civitai.red/articles/19107/crodys-illustrious-noobai-image-generation-tips

Civitai referenced articles:
https://civitai.com/articles/2246/sdxl-image-size-cheat-sheet
https://civitai.com/articles/16016/illustrious-prompt-guide-optimized-and-complete

Prompt embedding tools:
https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb
https://github.com/xhinker/sd_embed

Danbooru resources:
https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition#dtext-flaws
https://danbooru.donmai.us/wiki_pages/tag_group%3Ametatags
https://danbooru.donmai.us/wiki_pages/list_of_style_parodies
https://danbooru.donmai.us/wiki_pages/tag_group%3Avisual_aesthetic
https://danbooru.donmai.us/artists
https://danbooru.donmai.us/wiki_pages/tag_group%3Agroups
https://danbooru.donmai.us/wiki_pages/tag_group%3Afamily_relationships
https://danbooru.donmai.us/wiki_pages/tag_group%3Aposture#dtext-two
https://danbooru.donmai.us/tags?commit=Search&search%5Bcategory%5D=4&search%5Bhide_empty%5D=yes&search%5Border%5D=date
https://danbooru.donmai.us/wiki_pages/tag_group%3Askin_color
https://danbooru.donmai.us/wiki_pages/tag_group%3Aears_tags
https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-head
https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair_color
https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair_styles
https://danbooru.donmai.us/wiki_pages/tag_group%3Aheadwear
https://danbooru.donmai.us/wiki_pages/tag_group%3Aeyewear
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-headwear
https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair#dtext-objects
https://danbooru.donmai.us/wiki_pages/tag_group%3Aeyes_tags
https://danbooru.donmai.us/wiki_pages/tag_group%3Aface_tags
https://danbooru.donmai.us/wiki_pages/tag_group%3Aneck_and_neckwear
https://danbooru.donmai.us/wiki_pages/tag_group%3Ashoulders
https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-upper
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-shirts
https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-lower
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-pants
https://danbooru.donmai.us/wiki_pages/tag_group%3Abody_parts#dtext-appendages
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-legs
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-shoes
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-styles
https://danbooru.donmai.us/wiki_pages/tag_group%3Afashion_style
https://danbooru.donmai.us/wiki_pages/tag_group%3Apatterns
https://danbooru.donmai.us/wiki_pages/tag_group%3Aprints
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire#dtext-jewelry
https://danbooru.donmai.us/wiki_pages/tag_group%3Aaccessories
https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire
https://danbooru.donmai.us/wiki_pages/tag_group%3Atail
https://danbooru.donmai.us/wiki_pages/tag_group%3Awings
https://danbooru.donmai.us/wiki_pages/tag_group%3Agestures
https://danbooru.donmai.us/wiki_pages/tag_group%3Aposture
https://danbooru.donmai.us/wiki_pages/on
https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition
https://danbooru.donmai.us/wiki_pages/tag_group%3Afocus_tags
https://danbooru.donmai.us/wiki_pages/tag_group%3Abackgrounds
https://danbooru.donmai.us/wiki_pages/tag_groups
https://danbooru.donmai.us/wiki_pages/tag_group%3Alighting
https://danbooru.donmai.us/wiki_pages/tag_group%3Aimage_composition#dtext-depth
```
