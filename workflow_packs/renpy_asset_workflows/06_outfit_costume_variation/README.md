# 06 — 의상/코스튬 변형

Category: `character`

## Purpose

기존 캐릭터 source PNG를 입력으로 받아 같은 얼굴/헤어 인상을 유지하면서 의상만 새 variant로 바꾼다.

현재 06은 여러 의상별 JSON을 두지 않는다. 하나의 PuLID + img2img canonical workflow를 deep-copy해서 prompt/seed/output prefix만 바꿔 실행한다.

```text
01 character source or approved sprite source
→ 06 outfit source PNG
→ 02 expression if needed, or 03 alpha for transparent sprite
```

06은 투명 PNG를 직접 만들지 않는다. 최종 Ren'Py sprite용 alpha가 필요하면 06 결과를 현재 pack의 `03_toonout_transparency_alpha` workflow로 후처리한다.

## Active API template

- `workflow_api/06_outfit_pulid_i2i_canonical_api.json`
  - route: source image VAEEncode img2img + PuLID identity anchoring
  - checkpoint: `novaAnimeXL_ilV190.safetensors`
  - identity adapter: `ip-adapter_pulid_sdxl_fp16.safetensors`
  - status: single canonical workflow consolidated from the accepted lavender-hoodie PuLID+i2i route

Superseded per-outfit JSONs were removed from the active folder. Outfit variation is now represented by README presets, not separate workflow files.

## Editable nodes

보통 아래만 바꾼다.

| Node | Class | Field | What to edit |
| --- | --- | --- | --- |
| `3` | `LoadImage` | `inputs.image` | ComfyUI input 기준 identity/source PNG path |
| `7` | `ApplyPulidAdvanced` | `inputs.weight` | identity retention strength; 보통 `1.00`-`1.05` |
| `8` | `CLIPTextEncode` positive | `inputs.text` | character lock + outfit preset prompt |
| `9` | `CLIPTextEncode` negative | `inputs.text` | common negative + old outfit/new outfit conflict terms |
| `11` | `KSampler` | `inputs.seed` | outfit candidate seed |
| `11` | `KSampler` | `inputs.denoise` | outfit change strength; 보통 `0.80`-`0.87` |
| `13` | `SaveImage` | `inputs.filename_prefix` | output prefix |

특별한 이유가 없으면 아래는 바꾸지 않는다.

- node graph structure
- checkpoint
- PuLID model / projection / fidelity / start_at / end_at
- sampler type, steps, cfg, scheduler
- VAEEncode img2img route

## Fixed canonical settings

```text
checkpoint: novaAnimeXL_ilV190.safetensors
clip last layer: -2
PuLID model: ip-adapter_pulid_sdxl_fp16.safetensors
PuLID provider: CUDA
PuLID projection: ortho_v2
PuLID fidelity: 12
PuLID start/end: 0.0 / 0.85
sampler: euler_ancestral
scheduler: normal
steps: 30
cfg: 5.4
canonical default denoise: 0.82
canonical default PuLID weight: 1.05
```

## Input rules

ComfyUI `LoadImage`는 Windows ComfyUI의 `input` 폴더 기준 상대 경로를 받는다.

WSL에서 보이는 input root:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

권장 input 위치:

```text
ComfyUI/input/hermes_vn_outfit/{source_character}.png
```

JSON node `3` 예:

```text
LoadImage.image = hermes_vn_outfit/source_silver_bob_neutral.png
```

source PNG가 ComfyUI output 폴더에만 있으면 먼저 input 폴더로 복사한다.

```bash
mkdir -p /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_outfit
cp /mnt/c/Users/Desktop/Documents/ComfyUI/output/{run_folder}/{source_png}.png \
  /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_outfit/
```

## Prompt structure

Positive prompt는 아래 구조로 작성한다.

```text
[quality block], [identity lock], [framing], [outfit preset], [pose/background/style]
```

### Quality block

```text
masterpiece, best quality, very aesthetic, newest
```

### Identity lock

소스 캐릭터에 맞춰 구체적으로 바꾼다.

```text
1girl, solo, anime style, same hair, same eye color, same face
```

더 안정적으로 잠그고 싶으면 실제 캐릭터 태그를 쓴다.

```text
same silver bob hair, same blue eyes, same face
```

### Framing block

```text
upper body character portrait, full head visible, complete hair visible, large centered character
```

### Pose/background/style block

```text
relaxed standing pose, hands near chest, clean sharp anime lineart, flat medium gray background
```

배경은 source/alpha 후처리를 위해 단순 회색 계열을 유지한다. outfit workflow에서 화려한 배경을 만들지 않는다.

## Common negative prompt base

```text
text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, extra arms, extra hands, bad hands, deformed fingers, different face, different hairstyle, different eye color, headwear, object above head, printed text, pattern logo, white background, green background, teal background, reference sheet, character sheet, sprite sheet, inset
```

의상별로 이전 의상이나 충돌 의상 태그를 뒤에 추가한다. 예를 들어 hoodie를 만들 때는 `school uniform, blouse, necktie, cardigan`을 negative에 넣는다.

## Outfit presets

이 표는 과거 개별 JSON에서 쓰던 값을 단일 workflow용 preset으로 옮긴 것이다. 새 JSON을 만들지 말고 node `8`, `9`, `11`, `13`만 수정한다.

| slug | positive outfit tags | negative additions | denoise | PuLID weight | seed example | status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `lavender_hoodie` | `casual weekend outfit, plain soft lavender hoodie, pullover hoodie, hood resting behind neck, no school uniform, no blouse, no necktie, no cardigan, no front buttons` | `school uniform, blue blouse, collared blouse, necktie, bow tie, blazer, front buttons, cardigan, cable knit cardigan, cream cardigan, beige cardigan` | 0.82 | 1.05 | 62018433 | accepted direction |
| `blue_denim_jacket` | `blue denim jacket with visible denim texture, jean jacket over simple white t-shirt, casual outfit, front metal buttons on denim jacket, no school uniform, no blouse, no necktie, no cardigan, no hoodie` | `cream cardigan, knit cardigan, hoodie, school uniform, blouse, necktie, bow tie` | 0.86 | 1.02 | 62018457 | pass direction |
| `green_field_jacket` | `olive green casual field jacket over black top, utility jacket pockets, outdoor casual outfit, no school uniform, no blouse, no necktie, no cardigan` | `hoodie, cardigan, blazer, school uniform, necktie, bow tie, blue blouse` | 0.83 | 1.05 | 62018453 | pass direction |
| `red_track_jacket` | `red sporty zip-up track jacket with white sleeve stripes, casual athletic wear, simple black inner shirt, no school uniform, no blouse, no necktie, no cardigan` | `hoodie, cardigan, blazer, school uniform, necktie, bow tie, blue blouse` | 0.82 | 1.05 | 62018451 | pass direction |
| `pink_ribbon_blouse` | `soft pink frilly casual blouse, small ribbon at neckline, cute weekend outfit, short puff sleeves, no school uniform, no blue blouse, no necktie, no cardigan, no blazer` | `hoodie, jacket, cardigan, school uniform, blue blouse, navy tie` | 0.80 | 1.05 | 62018454 | pass direction |
| `yellow_summer_dress` | `sunny yellow casual summer dress, short puff sleeves, simple one-piece dress, cute weekend outfit, no school uniform, no blouse, no necktie, no cardigan, no jacket, no hoodie` | `cardigan, hoodie, jacket, blazer, school uniform, blouse, necktie, blue skirt` | 0.86 | 1.02 | 62018458 | pass direction |
| `purple_witchy_capelet` | `purple fantasy casual capelet over black dress, witchy outfit, small cape collar, dark elegant dress, no school uniform, no blouse, no necktie, no cardigan, no hoodie` | `cream cardigan, hoodie, jacket, school uniform, blouse, necktie, blue skirt, tiara, crown, hat` | 0.87 | 1.00 | 62018459 | pass direction, face slightly softer |
| `denim_jacket_white_tee` | `light blue denim jacket over plain white t-shirt, casual weekend outfit, visible denim collar and seams, no school uniform, no blouse, no necktie, no cardigan` | `hoodie, cardigan, blazer, school uniform, necktie, bow tie, blue blouse` | 0.82 | 1.05 | 62018452 | usable but may collapse to tee/shorts |
| `black_bomber_jacket` | `black cropped bomber jacket over plain white t-shirt, casual streetwear, ribbed cuffs, zipper jacket, no school uniform, no blouse, no necktie, no cardigan` | `hoodie, drawstrings, cardigan, blazer, school uniform, necktie, bow tie, blue blouse` | 0.82 | 1.05 | 62018450 | pass-ish; color drift risk |
| `black_leather_jacket` | `black leather biker jacket, black zipper jacket over dark gray shirt, edgy casual outfit, shiny leather sleeves, no school uniform, no blouse, no necktie, no cardigan, no hoodie` | `white cardigan, cream cardigan, hoodie, track jacket, school uniform, blouse, necktie, bow tie` | 0.86 | 1.02 | 62018456 | rejected for default safe set; revealing/crop risk |

## Output naming

권장 prefix:

```text
hermes_vn_outfit_variation/outfit_{character_slug}_{preset_slug}_seed{seed}
```

예:

```text
hermes_vn_outfit_variation/outfit_silver_bob_lavender_hoodie_seed62018433
```

ComfyUI는 실제 파일명 뒤에 `_00001_.png` 같은 suffix를 붙인다.

## Agent recipe: single outfit

1. root `AGENTS.md`와 `WORKFLOW_INDEX.json`을 확인한다.
2. 01 또는 승인된 source PNG를 고른다. alpha PNG보다 원본/source PNG를 우선 사용한다.
3. source PNG가 ComfyUI input 폴더에 없으면 복사한다.
4. `workflow_api/06_outfit_pulid_i2i_canonical_api.json`을 로드한다.
5. node `3` `LoadImage.image`를 input-relative source path로 바꾼다.
6. preset 표에서 outfit slug를 고른다.
7. node `8` positive prompt를 `[quality block], [identity lock], [framing], [preset positive outfit tags], [pose/background/style]`로 만든다.
8. node `9` negative prompt를 `[common negative prompt base], [preset negative additions]`로 만든다.
9. node `7` PuLID `weight`, node `11` `seed`/`denoise`를 preset 값으로 설정한다.
10. node `13` `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
11. ComfyUI `/queue`가 비어 있는지 확인한다. 공유 Windows ComfyUI를 함부로 interrupt/clear하지 않는다.
12. `POST /prompt`로 실행한다.
13. `/history/{prompt_id}`에서 output path를 확인한다.
14. 후보가 마음에 들면 02 expression 또는 03 alpha 단계로 넘긴다.

## Batch use

여러 의상을 만들 때도 workflow JSON을 복제하지 않는다.

- canonical JSON을 메모리에서 deep-copy한다.
- 각 item마다 node `8`, `9`, `11`, `13`만 다르게 설정한다.
- 같은 source image를 쓰되 output prefix는 outfit slug/seed를 포함해 충돌을 피한다.
- batch 결과와 contact sheet는 reusable pack 안이 아니라 ComfyUI output run folder에 저장한다.

## QA checklist

06 outfit source 후보는 contact sheet 또는 실제 출력 비교로 확인한다.

필수 확인:

- 같은 인물로 보이는가
- 얼굴/눈색/헤어 길이/헤어 실루엣이 유지되는가
- 의상 변화가 명확한가
- 이전 의상 잔재가 과하게 남지 않았는가
- 손/팔/어깨가 깨지지 않았는가
- 머리/얼굴이 잘리거나 crop되지 않았는가
- 배경이 alpha 후처리에 적합한 단순 회색 계열인가
- 02 alpha 후 밝은/어두운 배경에서 edge/halo가 허용 가능한가
- Ren'Py 대사창/배경 위에서 sprite로 사용할 수 있는가

## Known limitations

- 이 route는 full-image img2img이므로 의상 변화는 강하지만 원본 픽셀 보존형 workflow가 아니다.
- `denoise`를 높이면 의상은 잘 바뀌지만 얼굴/헤어가 부드러워지거나 drift할 수 있다.
- `denoise`를 낮추면 identity는 잘 유지되지만 기존 의상 잔재가 남을 수 있다.
- leather/revealing 계열은 default safe set에서 제외한다. 필요하면 별도 사용자 QA 후 사용한다.
- 최종 game-ready 승격 전에는 반드시 02 alpha와 Ren'Py placement QA를 거친다.

## Notes for agents

- README는 사용법 문서다. 새 의상마다 JSON을 추가하지 않는다.
- 새 의상 preset이 반복적으로 유용하면 README preset 표에만 추가한다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
- 상태, 대표 output, 승인 여부는 필요할 때 `WORKFLOW_INDEX.json`에 짧게 둔다.
