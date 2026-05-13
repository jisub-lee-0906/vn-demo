# 01 — 캐릭터 기준 앵커 생성

Category: `character`

## Purpose

새 캐릭터의 재사용 가능한 기준 source 이미지를 만든다.

이 workflow의 목적은 “가장 화려한 일러스트”가 아니라 후속 workflow에서 안정적으로 재사용하기 쉬운 `front_view + neutral/expressionless + closed_mouth` character anchor 생성이다.

01에서 만든 source PNG는 다음 단계의 기준 이미지가 된다.

```text
01 source anchor
→ 02 transparent alpha sprite
→ 03 expression variations
→ 04 pose variations
→ 10 outfit/costume variations
```

## Output

- 출력물: 회색 배경의 character source PNG
- 용도: 02/03/04/10에서 얼굴, 헤어, 의상, 기본 체형을 참조하는 기준 이미지
- 아직 Ren'Py 투입용 투명 PNG가 아니다. 투명 PNG가 필요하면 02 workflow로 후처리한다.

## API template

- `workflow_api/01_character_anchor_apose_neutral_api.json`
  - checkpoint: `novaAnimeXL_ilV190.safetensors`
  - model family: Nova Anime XL — IL v19.0
  - prompt style: Danbooru tag only
  - role: canonical front/neutral character anchor
  - ComfyUI endpoint when running from WSL: usually `http://172.28.224.1:8000`
  - status: v19 Danbooru-only candidate accepted by agent visual QA and cross-character smoke test

## Fixed settings

특별한 이유가 없으면 아래는 유지한다.

- checkpoint: `novaAnimeXL_ilV190.safetensors`
- image size: `1152 x 1536`
- sampler/settings: `steps 28`, `cfg 5.0`, `euler_ancestral`, `normal`, `denoise 1.0`
- clip skip: 1 equivalent, direct checkpoint CLIP; no `CLIPSetLastLayer`
- rating tag: `rating_questionable` for 15세 target tone
- background: `simple_background, grey_background`

## Editable nodes

보통 아래 3가지만 바꾼다.

| Node | Field | What to edit |
| --- | --- | --- |
| `3` CLIPTextEncode positive | `inputs.text` | character identity tags만 교체 |
| `6` KSampler | `inputs.seed` | 새 후보/새 캐릭터 seed |
| `8` SaveImage | `inputs.filename_prefix` | 출력 prefix |

## Positive prompt structure

반드시 Danbooru-style comma-separated tags만 쓴다. 자연어 문장 금지.

```text
[quality block], [fixed composition/expression block], [character identity tags], [fixed outfit/background tags], BREAK depth_of_field, volumetric_lighting
```

### 1. Fixed quality block

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest
```

주의:
- IL v19에서는 Pony score tags 금지: `score_9`, `score_8_up` 등을 넣지 않는다.
- plain gray background 목적에서는 `scenery`를 넣지 않는다.

### 2. Fixed composition/expression block

```text
rating_questionable, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, straight_posture
```

목표:
- 정면
- 무표정 / 닫힌 입
- 후속 표정/포즈 변형에 방해되지 않는 기준 자세
- 손이 화면 밖으로 잘리지 않는 상반신~허벅지 구도
- full body가 아니라 `cowboy_shot` 기준

### 3. Character identity tags

새 캐릭터를 만들 때는 이 구간만 교체한다.

현재 canonical silver-bob 예시:

```text
short_hair, bob_cut, silver_hair, blue_eyes
```

다른 캐릭터 예시:

```text
long_hair, twintails, pink_hair, green_eyes
```

```text
medium_hair, green_hair, brown_eyes, glasses
```

규칙:
- Danbooru tags only.
- tag가 결과를 바꾸지 않거나 drift만 만들면 제거한다.
- 01에서는 표정을 바꾸지 않는다. smile/happy/sad/angry/surprised/fearful은 03에서 만든다.
- 01에서는 포즈를 바꾸지 않는다. crossed_arms/hand_on_hip/pointing 등은 04에서 만든다.
- 의상 variation은 10에서 만든다. 01에서는 기준 의상만 정한다.

### 4. Fixed outfit/background tags

현재 accepted baseline:

```text
beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, simple_background, grey_background
```

QA 결과:
- `black_pantyhose`는 15세 게임 톤 안정화에 유효했다.
- `long_skirt`는 skirt 색/형태 drift가 커서 제외했다.
- `loose_clothes`는 변화가 작거나 얼굴/몸 비율 drift가 있어 제외했다.
- `medium_breasts`는 15세 톤에 불필요해서 제외했다.
- `school_uniform`은 결과 변화가 크지 않아 baseline에서는 더 구체적인 outfit tags만 유지한다.
- `badge`, `emblem`, `logo`는 작은 마크 drift를 만들 수 있어 negative에 둔다.

### Full canonical positive prompt

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_questionable, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, straight_posture, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, simple_background, grey_background, BREAK depth_of_field, volumetric_lighting
```

## Negative prompt rules

현재 accepted baseline:

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, smile, open_mouth, dynamic_pose, crossed_arms, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, (worst quality, bad quality:1.2)
```

주의:
- positive에 `simple_background`를 쓰므로 negative에는 `simple_background`를 넣지 않는다.
- 색상별 금지어는 넣지 않는다. 다른 캐릭터를 막을 수 있다.
- `badge`, `emblem`, `logo`는 기준 cardigan의 작은 마크 drift 방지용이다. 특정 캐릭터가 badge를 반드시 가져야 한다면 이 세 태그를 제거하고 별도 실험한다.

## Accepted visual QA

Silver-bob canonical candidate:

- seed: `719251035`
- output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_character_anchor/iter5_pantyhose_anchor_seed719251035_00001_.png`
- contact sheet: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_character_anchor/contact_iter5_pantyhose_6seeds.png`

Agent visual QA summary:
- 고퀄리티 얼굴/머리/의상 렌더링.
- 정면, 닫힌 입, 무표정 기준에 적합.
- 회색 배경이 단순하고 02 alpha 전처리에 적합.
- 손/팔이 보이고 후속 03/04에 방해되는 과한 포즈가 없음.
- `black_pantyhose` 적용 후 15세 게임 톤이 더 안정적.

Cross-character smoke test:

- contact sheet: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_character_anchor/contact_generalize_2chars_3seeds_each.png`
- `pink_twinbraids`: best seed `719251102`
- `green_glasses`: best seed `719251104`

둘 다 정면/무표정/회색배경/단순 의상/15세 톤 기준에 합격했다. 따라서 prompt 구조는 다른 캐릭터에도 사용 가능하다.

## Output naming

권장 prefix:

```text
hermes_vn_toonout_other_character/source_{character_slug}_v190_danbooru_anchor_seed{seed}
```

실험/ablation이면 별도 run folder를 쓴다.

```text
hermes_vn_experiments/nova_t2i_il_v190_character_anchor/{test_id}_{character_slug}_seed{seed}
```

## Agent recipe

1. ComfyUI가 켜져 있는지 확인한다.
2. Queue가 비어 있는지 확인한다.
3. `workflow_api/01_character_anchor_apose_neutral_api.json`를 load한다.
4. 새 캐릭터면 positive의 identity tags만 교체한다.
5. seed 후보 3~6개를 생성한다.
6. contact sheet를 만들고 vision QA한다.
7. 태그를 하나씩만 추가/삭제한다.
8. 추가한 태그가 결과를 바꾸지 않거나 drift만 만들면 제거한다.
9. 합격 후보가 나오면 다른 캐릭터 1~2개로 smoke test한다.
10. 둘 다 합격하면 01 canonical template에만 반영한다.

## V190 Danbooru edge/background tuning note

2026-05-13 tuning for 01→02 alpha:

- Keep `thick_outline`: it slightly improves hair/body edge readability without visible identity drift.
- Use `simple_background, grey_background, dark_background` for the current silver-hair anchor when a darker gray source background is needed.
- Add `gradient_background, patterned_background` to negative for this darker-background variant; it reduced background texture without reintroducing badge drift in the accepted smoke.
- Do not use `solid_background` here: in the v19 silver-bob test it reintroduced badge/emblem drift despite the negative prompt.
- Do not use `black_background` for this anchor: it becomes too black/blue and is less suitable as a neutral source background.
