# 06 — 의상/코스튬 변형

Category: `character`

## Purpose

06은 승인된 `01` featureless mannequin/body-template source PNG를 입력으로 받아, Nova Anime XL IL v19 + Depth ControlNet + PuLID + face-only protected inpaint로 의상 variant source PNG를 만든다.

현재 canonical은 ROI 후처리 보정 단계를 제거한 base-only workflow다. hoodie 전용으로 추가했던 hood/shoulder, hand/wrist, between-legs ROI postpass는 다른 의상에서 치마/소매/티셔츠를 흔들 수 있어 canonical에서 제외했다. 이전 ROI postpass 버전은 아래에 백업했다.

```text
00_experiment_sandbox/06_outfit_canonical_archive_20260516/06_outfit_pulid_i2i_canonical_with_roi_postpasses_before_remove_20260516.json
```

```text
01 featureless mannequin source
→ 06 face-only protected outfit generation
→ final opaque outfit source PNG
```

06은 투명 PNG를 직접 만들지 않는다. Ren'Py sprite용 alpha가 필요하면 final output을 `03_toonout_transparency_alpha` workflow로 후처리한다.

## Active API template

Active `workflow_api/`에는 하나의 canonical JSON만 둔다.

- `workflow_api/06_outfit_pulid_i2i_canonical_api.json`
  - route: featureless source → BiRefNet character alpha → Florence face protect → body edit mask → Depth ControlNet + PuLID inpaint → final opaque source
  - checkpoint: `novaAnimeXL_ilV190.safetensors`
  - ControlNet: `SDXL\control-lora-depth-rank256.safetensors`
  - PuLID: `ip-adapter_pulid_sdxl_fp16.safetensors`
  - Florence model: `Florence-2-large`
  - character alpha: `BiRefNet_toonout`
  - legacy hand-protection: disabled for featureless source
  - ROI postpasses: disabled/removed from canonical

## Output nodes

| Prefix | Node | Meaning |
| --- | ---: | --- |
| `final_*_baseonly_seed_*` | `35` | canonical base-only outfit source candidate |

## Editable nodes

Normally edit only these nodes at runtime.

| Node | Class | Field | What to edit |
| ---: | --- | --- | --- |
| `3` | `LoadImage` | `inputs.image` | ComfyUI input-relative 01 featureless source PNG |
| `23` | `CLIPTextEncode` | positive text | quality + character tags + target full outfit tags |
| `24` | `CLIPTextEncode` | negative text | common negative + old/source/preset conflict tags |
| `27` | `KSampler` | seed/cfg/denoise | base outfit generation |
| `35` | `SaveImage` | filename_prefix | output label |

Do not change unless debugging:

- checkpoint / CLIP layer / PuLID model nodes
- BiRefNet character alpha node `4`
- Florence face protect node `8`
- base face-only edit mask route `15` → `16` → `17` → `18` → `53`
- Depth ControlNet nodes `900`-`902`

## Fixed canonical settings

```text
checkpoint: novaAnimeXL_ilV190.safetensors
clip last layer: -2
source contract: 1152x1536 front-facing featureless mannequin/body-template from workflow 01
base edit mask: character alpha - Florence face, grown/blurred, constrained to character alpha, then face subtracted again
legacy hand protection: disabled for featureless source
ROI postpasses: removed from canonical
sampler: seed TEMPLATE_seed, euler_ancestral, normal, steps 28, cfg 4.5, denoise 1.0
```

## Input rules

ComfyUI `LoadImage` paths are relative to the Windows ComfyUI `input` folder.

WSL path:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input
```

Recommended input location:

```text
ComfyUI/input/hermes_vn_outfit_featureless_base/{source_character}.png
```

JSON node `3` example:

```text
LoadImage.image = hermes_vn_outfit_featureless_base/pink_twintails_featureless_mannequin_base_seed719251139.png
```

## QA checklist

Required before using as production source:

- face/hair remain stable enough for the intended character
- target outfit reads clearly
- shoulder/collar/neck seam is acceptable without ROI postpass
- hands/wrists are acceptable; if poor, debug upstream generation/prompt before adding ROI repair
- skirt/lower-body area is acceptable; if a white gap appears, debug prompt/seed first before adding ROI repair
- run 03 alpha after accepted final and check light/dark halo before Ren'Py use

## Notes for agents

- Keep exactly one active canonical JSON in this folder.
- Do not store generated PNGs/contact sheets in the reusable pack.
- Do not reintroduce ROI postpasses into canonical without user approval; keep such experiments in `00_experiment_sandbox/`.
- For different outfits, patch prompt/negative/seed/output prefix at runtime from this one JSON.
