# Ren'Py VN Asset ComfyUI Workflow Pack

This folder is the repo-local source of truth for reusable ComfyUI API workflows used to create visual-novel / dating-sim assets for `vn-demo`.

Windows path:
`\\wsl.localhost\Ubuntu-24.04\home\jisub-lee\workspace\vn-demo\workflow_packs\renpy_asset_workflows`

WSL path:
`/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows`

## Current structure

The current pack uses flat, named workflow folders. It no longer uses the old numbered `01_*`, `02_*`, `03_*` folder contract.

Each workflow folder should contain:

- `README.md` — human/agent operating notes for that workflow.
- `*_workflow_api.json` — the canonical ComfyUI API graph template.

Current canonical folders:

| Folder | Purpose | Main API JSON |
|---|---|---|
| `character_anchor_base` | Generate base character/source images. | `character_anchor_base/character_anchor_base_workflow_api.json` |
| `expression_variations` | Generate expression variants from a character source image using face/mask inpaint/composite. | `expression_variations/expression_variations_workflow_api.json` |
| `transparency_alpha` | Convert a source character image to transparent PNG / alpha output. | `transparency_alpha/transparency_alpha_workflow_api.json` |
| `background_art` | Generate 16:9 VN background art. | `background_art/background_art_workflow_api.json` |
| `prop_closeup_cg` | Generate 16:9 close-up prop / clue / cut-in CG images. | `prop_closeup_cg/prop_closeup_cg_workflow_api.json` |
| `outfit_variations` | Generate outfit/costume variants from a featureless or source character image. | `outfit_variations/outfit_variations_workflow_api.json` |
| `event_cg` | Generate 16:9 character event CG from a character reference; background is generated from the prompt with pose LoRA support. | `event_cg/event_cg_workflow_api.json` |

## Recommended agent entrypoint

When an AI agent starts work in this pack:

1. Read this `README.md`.
2. Read `WORKFLOW_INDEX.json`.
3. Read `AGENTS.md`.
4. Read the target workflow folder's `README.md`.
5. Load the target `*_workflow_api.json` and runtime-patch only the editable fields listed in the index.

## Workflow role split

A typical asset flow is:

1. `character_anchor_base` — produce an opaque base/source character.
2. `transparency_alpha` — convert an accepted character source to transparent PNG when needed.
3. `expression_variations` — create expression variants from a source character image.
4. `outfit_variations` — create outfit variants, especially from featureless/source character images.
5. `background_art` — create 16:9 scene backgrounds.
6. `prop_closeup_cg` — create separate 16:9 prop/clue cut-ins for Ren'Py staging.
7. `event_cg` — create full 16:9 event CGs from a character reference only; background/composition are prompt-generated with pose LoRA support. Use this for special pose/action illustration needs instead of the removed `pose_variations` sprite route.

The folders are reusable tools, not a mandatory linear pipeline. Choose the smallest workflow that matches the asset being created.

## Canonical JSON handling

Do not overwrite canonical API JSONs during normal generation.

Preferred pattern:

1. Deep-copy the canonical `*_workflow_api.json` into a temporary runtime/sandbox path outside the canonical workflow folder.
2. Patch only the intended runtime fields: prompts, seed, input image names, output prefix, and any explicitly approved parameters.
3. Submit the runtime copy to ComfyUI.
4. Save generated outputs under ComfyUI output folders, not inside this reusable pack.
5. Promote changes back into canonical JSON only after explicit user QA/approval.

## Placeholders and input files

Some templates intentionally contain placeholders such as:

- `TEMPLATE_character_anchor_source.png`
- `TEMPLATE_source_image.png`
- `TEMPLATE_featureless_mannequin_source.png`
- `TEMPLATE_character_reference.png`
- `TEMPLATE_*` output prefix fragments
- Korean prompt placeholders such as `{감정표현}` or `{배경 테마 및 장소}`

Before live ComfyUI submission, agents must replace these with real ComfyUI `input/` filenames, prompt text, seeds, and output prefixes.

## Quality and promotion rule

A workflow being runnable is not the same as being production-approved.

Only call an output canonical/approved after the user or agent has checked the actual generated artifact/contact sheet/Ren'Py screenshot. If the user says they will visually QA the image themselves, report only the prompt id, seed, runtime JSON path, and output path; do not invent quality claims.

## 고정 상태

현재 canonical pack은 위에 적힌 7개 workflow 폴더로 의도적으로 제한합니다. `pose_variations`는 canonical pack에서 제거되었으므로, 포즈/액션이 필요한 경우 dialogue sprite 재생성이 아니라 16:9 `event_cg`로 처리합니다.

고정 전 audit 상태:

- 7개 canonical API JSON 파일 모두 정상 파싱됩니다.
- `WORKFLOW_INDEX.json`은 실제 존재하는 workflow 폴더와 API 파일만 가리킵니다.
- 각 그래프를 출력 노드에서 역방향으로 추적했을 때 미사용/분리 노드는 발견되지 않았습니다.
- 존재하지 않는 노드를 참조하는 dangling reference는 발견되지 않았습니다.
- `WORKFLOW_INDEX.json`은 editable field, primary node, placeholder, observed default의 machine-readable 기준 문서입니다.
- 각 workflow README는 간결한 운영 가이드로 유지합니다. 실험 이력이나 일시적인 튜닝 노트를 넣기 위해 수정하지 않습니다.

최신 audit report:
`/home/jisub-lee/workspace/vn-demo/.analysis/workflow_pack_freeze_audit_20260517.md`

## 현재 주의사항

- 현재 폴더명은 번호식 이름이 아니라 flat semantic name입니다. 예전 `01_*`부터 `07_*`까지의 참조는 stale일 수 있습니다.
- `background_art`와 `prop_closeup_cg`는 이미지 입력이 없는 16:9 txt2img 계열 workflow입니다.
- `expression_variations`, `transparency_alpha`, `outfit_variations`, `event_cg`는 런타임 이미지 입력이 필요합니다.
- `pose_variations`는 pose/action sprite 테스트에서 색감/의상/구도/해부학 drift가 커서 canonical pack에서 제거했습니다. 포즈/액션 CG는 `event_cg`로 처리하고, dialogue sprite는 fixed outfit/expression/alpha 경로를 유지합니다.
- 일부 README의 prompt 텍스트는 사람이 읽기 위한 안내라 canonical JSON prompt와 정확히 일치하지 않을 수 있습니다. 실행 기준은 `WORKFLOW_INDEX.json`과 실제 JSON입니다.
- 루트 `danbooru_tag.csv`는 README tag note의 로컬 검증 기준입니다. 해당 CSV에 존재하거나 실제 생성물로 테스트된 태그가 아니라면, 기억이나 실패한 web fetch 기반으로 tag guidance를 추가하지 않습니다.
