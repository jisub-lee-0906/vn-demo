# 02 — 표정 변형

Category: `character`

## Purpose

01에서 승인된 character source/anchor PNG를 기준으로 VN용 표정 source PNG를 만든다.

02의 현재 canonical route는 Florence-2 face segmentation + face-local inpaint + masked composite 방식이다.

목표:

- 얼굴 표정만 바꾼다.
- 머리카락, 옷, 리본, 치마, 몸, 배경은 원본을 최대한 보존한다.
- 최종 투명 PNG가 필요하면 02 결과를 03 alpha workflow로 후처리한다.

```text
01 character anchor/source PNG
→ 02 expression source PNG, gray/dark-gray background preserved
→ 03 transparent alpha sprite
```

02는 alpha를 만들지 않는다. 03 alpha workflow를 중복하지 않는다.

## Output

02 workflow는 한 번 실행할 때 3종류를 저장한다.

| Output | Meaning | Use |
| --- | --- | --- |
| `*_mask_preview_00001_.png` | Florence face mask preview | mask가 얼굴만 잡혔는지 QA |
| `*_raw_inpaint_00001_.png` | inpaint raw output | 디버깅용; final로 쓰지 않음 |
| `*_composited_00001_.png` | original 위에 face mask 영역만 합성한 최종 source | 02의 실제 후보 output |

중요: raw inpaint는 얼굴 밖 색감도 바뀔 수 있으므로 final로 쓰지 않는다. 실제 후보는 항상 `*_composited_00001_.png`다.

## API template

- `workflow_api/02_expression_source_canonical_api.json`
  - role: runnable generic expression source workflow
  - route: Florence-2 face mask → inpaint → `ImageCompositeMasked`
  - checkpoint: `novaAnimeXL_ilV190.safetensors`
  - Florence node: kijai `DownloadAndLoadFlorence2Model` + `Florence2Run`
  - mask node: `AILab_MaskEnhancer`
  - inpaint conditioning: `DifferentialDiffusion`, `InpaintModelConditioning`, SDXL Union ControlNet `repaint`
  - final node: `ImageCompositeMasked(destination=original, source=raw_inpaint, mask=face_mask)`
  - status: not production-ready after 04; full-chain QA on 2026-05-13 showed happy expression change was too weak on a 04 posed source

## Editable nodes

보통 아래만 바꾼다.

| Node | Class | Field | What to edit |
| --- | --- | --- | --- |
| `1` | `LoadImage` | `inputs.image` | ComfyUI input 기준 source image path |
| `4` | `Florence2Run` | `inputs.text_input` | 보통 `face` 유지 |
| `4` | `Florence2Run` | `inputs.seed` | mask generation seed; 보통 sampler seed와 맞춤 |
| `6` | `CLIPTextEncode` positive | `inputs.text` | base prompt + character tags + expression tags |
| `7` | `CLIPTextEncode` negative | `inputs.text` | common negative + expression-specific negatives |
| `13` | `KSampler` | `inputs.seed` | expression seed |
| `13` | `KSampler` | `inputs.denoise` | expression strength |
| `15` | `SaveImage` | `inputs.filename_prefix` | raw inpaint output prefix |
| `17` | `SaveImage` | `inputs.filename_prefix` | mask preview output prefix |
| `19` | `SaveImage` | `inputs.filename_prefix` | composited final output prefix |

특별한 이유가 없으면 아래는 바꾸지 않는다.

- node graph structure
- checkpoint
- Florence model/task
- mask enhancer values
- ControlNet type/strength
- sampler type/steps/cfg/scheduler
- final `ImageCompositeMasked` route

## Fixed canonical settings

현재 silver-bob 테스트에서 통과한 기준값이다.

```text
checkpoint: novaAnimeXL_ilV190.safetensors
Florence model: microsoft/Florence-2-large
Florence precision: fp16
Florence task: referring_expression_segmentation
Florence text_input: face
MaskEnhancer sensitivity: 1.0
MaskEnhancer mask_blur: 3
MaskEnhancer mask_offset: 0
MaskEnhancer smooth: 1.0
MaskEnhancer fill_holes: true
ControlNet: xinsir-controlnet-union-sdxl-1.0-promax.safetensors
Union ControlNet type: repaint
ControlNet strength: 0.55
ControlNet start/end: 0.0 / 0.85
sampler: euler_ancestral
scheduler: karras
steps: 26
cfg: 5.0
```

## Input rules

02는 03 alpha PNG가 아니라 01 source/anchor PNG를 입력으로 사용한다.

권장 입력:

```text
ComfyUI/input/hermes_vn_expression/{source_character_anchor}.png
```

WSL에서 보이는 input root:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

예시:

```text
LoadImage.image = hermes_vn_expression/{source_character_anchor}.png
```

실제 파일:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_expression/{source_character_anchor}.png
```

source PNG가 ComfyUI output 폴더에만 있으면 먼저 input 폴더로 복사한다.

```bash
mkdir -p /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_expression
cp /mnt/c/Users/Desktop/Documents/ComfyUI/output/{run_folder}/{source_png}.png \
  /mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_expression/
```

## Prompt structure

Positive prompt는 Danbooru-style comma-separated tags만 사용한다.

```text
[quality block], [character/source tags], [expression tags], BREAK depth_of_field, volumetric_lighting
```

### 1. Fixed quality block

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest
```

### 2. Character/source tags

01 source/anchor를 만든 prompt의 identity/outfit/background tags를 최대한 그대로 사용한다.

현재 silver-bob 기준 예시:

```text
rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, thick_outline, grey_background
```

다른 캐릭터를 실행할 때는 hair/eyes/outfit tags를 해당 01 source에 맞게 교체한다. 표정 preset만 바꾸고 캐릭터 tags를 silver-bob 그대로 두면 얼굴/눈 색 drift가 생길 수 있다.

### 3. Expression tags

아래 preset 표의 `positive expression tags`를 character/source tags 뒤에 붙인다.

### 4. Fixed tail

```text
BREAK depth_of_field, volumetric_lighting
```

## Common negative prompt base

아래 common negative를 먼저 넣고, 표정별 negative additions를 뒤에 붙인다.

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, dynamic_pose, crossed_arms, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, gradient_background, patterned_background, changed_clothes, different_clothes, different_hair, (worst quality, bad quality:1.2)
```

주의:

- target expression을 negative에 넣지 않는다.
- 02도 01과 맞춰 positive background는 `grey_background`만 사용한다. `simple_background`, `flat_background`, `plain_background`, `dark_background`는 positive에서 제외한다.
- `white_background`, `bright_background`, `gradient_background`, `patterned_background`, `black_background`, `dark_background`, `vignette`는 background-only negative로 유지한다.
- `changed_clothes`, `different_clothes`, `badge`, `emblem`, `logo`는 outfit/badge drift 방지용이다.
- 다른 캐릭터가 badge/logo를 실제로 가져야 한다면 이 negative는 별도 검토한다.

## Expression presets

기본 VN 표정 세트는 `neutral, happy, sad, angry, disgusted, surprised, fearful`이다.

`neutral`은 02에서 새로 생성하지 말고 01 source/anchor를 그대로 사용한다. 표정 변형이 필요한 6개만 02를 실행한다.

| slug | positive expression tags | negative additions | denoise | seed example | status |
| --- | --- | --- | ---: | ---: | --- |
| `neutral` | no 03 run; use 01 source | no 03 run | n/a | n/a | use source directly |
| `happy` | `smile, open_mouth, happy` | `sad, angry, crying, tears, surprised, disgusted, fearful` | `0.40` | `719251301` | usable candidate |
| `sad` | `crying, tears, sad, open_mouth` | `smile, happy, angry, surprised, disgusted` | `0.40` | `719251402` | usable but mild/worried |
| `angry` | `angry, frown, furrowed_brow` | `smile, happy, sad, surprised, crying, tears` | `0.40` | `719251407` | usable mild angry/annoyed |
| `disgusted` | `disgusted, nauseated, wavy_mouth, half-closed_eyes, furrowed_brow` | `smile, happy, sad, surprised, crying, tears, open_mouth` | `0.45` | `719251505` | provisional; mild disgust/unease |
| `surprised` | `surprised, wide_eyes, open_mouth, raised_eyebrows` | `smile, happy, angry, disgusted, sad, crying, tears` | `0.40` | `719251305` | usable candidate |
| `fearful` | `fearful, scared, wide-eyed, open_mouth` | `smile, happy, angry, disgusted` | `0.40` | `719251405` | usable but overlaps surprised |

Preset notes:

- `happy` and `surprised` are the strongest tested candidates on 01 source images.
- After 04 pose regeneration, `happy` at denoise `0.40` can be too weak. On the fixed no-`thick_outline` arms-crossed 04 source, a denoise sweep found `0.55` as a usable mild-smile candidate and `0.65` as a slightly stronger smile candidate. Treat these as post-04 sandbox candidates pending user QA; do not change the default table globally without checking other expressions/characters.
- `sad` reads as sad/worried, not dramatic crying.
- `angry` reads as mild angry/annoyed.
- `fearful` reads as anxious/scared but can overlap with surprised.
- `disgusted` is the weakest default expression. Current best is `disgusted, nauseated, wavy_mouth, half-closed_eyes, furrowed_brow`; further prompt-only tag stacking gave diminishing returns.

## Output naming

권장 prefix:

```text
hermes_vn_expression/source_{character_slug}_{expression}_facecomp_seed{seed}
```

이 workflow는 3개 SaveImage node가 있으므로 같은 prefix stem을 쓰되 suffix를 구분한다.

```text
node 15 raw:        hermes_vn_expression/source_{character_slug}_{expression}_facecomp_seed{seed}_raw_inpaint
node 17 mask:       hermes_vn_expression/source_{character_slug}_{expression}_facecomp_seed{seed}_mask_preview
node 19 composited: hermes_vn_expression/source_{character_slug}_{expression}_facecomp_seed{seed}_composited
```

ComfyUI는 실제 파일명 뒤에 `_00001_.png` 같은 suffix를 붙인다.

실제 후보로 다음 단계에 넘기는 파일은 node `19`의 `*_composited_00001_.png`다.

## Agent recipe: single expression

1. root `AGENTS.md`와 `WORKFLOW_INDEX.json`을 확인한다.
2. 01에서 통과한 source/anchor PNG를 선택한다.
3. source PNG가 ComfyUI input 폴더에 없으면 복사한다.
4. `workflow_api/02_expression_source_canonical_api.json`을 로드한다.
5. node `1` `LoadImage.image`를 input-relative source path로 바꾼다.
6. node `4` `Florence2Run.text_input`은 `face`로 둔다.
7. node `4` `Florence2Run.seed`와 node `13` `KSampler.seed`를 preset seed 또는 새 seed로 맞춘다.
8. node `6` positive prompt를 `[quality block], [character/source tags], [expression tags], BREAK depth_of_field, volumetric_lighting`로 만든다.
9. node `7` negative prompt를 `[common negative prompt base], [expression negative additions]`로 만든다.
10. node `13` `denoise`를 preset 값으로 설정한다.
11. node `15`, `17`, `19`의 `SaveImage.filename_prefix`를 output naming 규칙에 맞춘다.
12. ComfyUI `/queue`가 비어 있는지 확인한다. 공유 Windows ComfyUI를 함부로 interrupt/clear하지 않는다.
13. `POST /prompt`로 실행한다.
14. `/history/{prompt_id}`에서 node `19` composited output path를 확인한다.
15. 사용자에게 `prompt_id`, mask preview, raw inpaint, composited final output path를 전달한다.
16. 투명 PNG가 필요하면 node `19` output을 ComfyUI input으로 복사한 뒤 03 alpha workflow를 실행한다.

## Agent recipe: default expression batch

1. `neutral`은 01 source를 그대로 후보로 둔다.
2. 같은 source image로 `happy, sad, angry, disgusted, surprised, fearful` 6개를 실행한다.
3. workflow JSON은 복제 파일로 저장하지 않는다. 메모리에서 deep-copy한 뒤 각 item의 editable fields만 바꿔 submit한다.
4. 각 item은 seed와 output prefix를 다르게 둔다.
5. batch 결과는 reusable pack 안이 아니라 ComfyUI output run folder에 저장한다.
6. contact sheet가 필요하면 pack 밖 output folder에 만든다.
7. 후보가 승인되면 composited outputs만 02 alpha로 후처리한다.

## QA checklist

02 source 후보는 contact sheet 또는 실제 출력 비교로 확인한다.

필수 확인:

- 표정이 작은 썸네일에서도 구분되는가
- 같은 인물로 보이는가
- 눈 색/눈매/얼굴형이 과하게 바뀌지 않았는가
- 헤어 색/길이/실루엣이 유지되는가
- 옷, 리본, 치마, 몸, 배경이 원본과 거의 같은가
- mask preview가 얼굴만 잡고 머리카락/옷/몸/배경으로 크게 번지지 않았는가
- raw inpaint가 아니라 composited output을 후보로 보고 있는가
- 03 alpha 후 light/dark background에서 edge/halo가 허용 가능한가

수치 검증이 필요하면 원본과 composited output을 비교한다.

권장 기준:

```text
mask coverage: about 1.9% on silver-bob test image
mean RGB delta outside mask: near 0.0003
changed outside-mask pixels: near zero
```

## Known limitations

- Florence face mask route는 얼굴 영역만 편집하므로 옷/배경 보존은 강하지만, 강한 표정은 제한될 수 있다.
- `mouth, eyes` mask는 silver-bob 테스트에서 coverage가 너무 작아 표정 변화가 약했다. 기본값으로 쓰지 않는다.
- `disgusted`는 prompt-only로 강한 혐오 표현이 잘 나오지 않았다. 기본 세트가 필요하면 `disgust_nauseated` preset을 사용하되, 강한 repulsion이 필요하면 별도 mouth/eye edit route나 수동 보정이 필요할 수 있다.
- 다른 캐릭터에서는 character/source tags를 반드시 해당 캐릭터에 맞춰 바꾸고, 최소 happy/surprised smoke로 mask와 identity를 확인한다.

## Accepted smoke evidence

대표 silver-bob source:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_vn_expression/source_silver_bob_v190_darkgrey_anchor_seed719251035.png
```

대표 evidence:

```text
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch1_composites.png
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch2_tuned_composites.png
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch3_disgust_composites.png
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/contact_batch2_alpha_light_dark.png
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/contact_batch3_disgust_alpha_light_dark.png
```

요약:

- face mask composite route는 silver-bob에서 비얼굴 영역을 거의 원본 그대로 보존했다.
- `happy`, `surprised`, `sad`, `fearful`, `angry` 후보가 생성됐다.
- `disgusted`는 `disgust_nauseated`를 provisional best로 둔다.
- 후보들의 02 alpha smoke는 기술적으로 통과했다.

## Notes for agents

- README는 사용법 문서다. 긴 테스트 보고서를 계속 누적하지 않는다.
- 표정별 workflow JSON을 만들지 않는다. 항상 `02_expression_source_canonical_api.json` 하나를 deep-copy해서 preset 값만 바꾼다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
- 상태, 대표 output, 승인 여부는 `WORKFLOW_INDEX.json`에 짧게 둔다.
