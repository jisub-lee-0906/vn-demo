# RenPy ComfyUI workflow pack

Minimal reusable workflow pack for making RenPy visual-novel assets with ComfyUI.

Primary WSL path: `/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows`

Old Windows reference path: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`

## For AI agents

Read `AGENTS.md` first, then `WORKFLOW_INDEX.json`, then the target numbered folder.

## Workflow order

- Character base: 01 -> 02
- Expressions: 03
- Poses: 04 pose donor/reference -> same-character regeneration
- Backgrounds: 06 base -> 07 variation
- Event CG: 08
- Support character: 09
- Outfit: 10
- Prop/effect: 11
- Audio: 12 SFX -> 13 BGM -> 14 packaging

## Index

| id | folder | category | purpose | API JSONs |
|---|---|---|---|---:|
| 01 | `01_character_anchor_and_prompt/` | character | 캐릭터 기준 앵커 생성 | 1 |
| 02 | `02_toonout_transparency_alpha/` | character | 투명 스프라이트 알파/매팅 | 1 |
| 03 | `03_expression_variation_face_composite/` | character | 표정 변형 | 1 |
| 04 | `04_pose_variation_reference_and_regeneration/` | character | 포즈 reference 생성 + 캐릭터 재생성 | 2 |
| 06 | `06_background_generation_no_text/` | background | 텍스트 없는 배경 생성 | 1 |
| 07 | `07_background_variation_img2img_layout_lock/` | background | 레이아웃 고정 배경 변형 | 1 |
| 08 | `08_event_cg_no_text_story_beat/` | cg | 스토리 이벤트 CG | 1 |
| 09 | `09_support_character_generation/` | character | 서포트 캐릭터 생성 | 2 |
| 10 | `10_outfit_costume_variation/` | character | 의상/코스튬 변형 | 12 |
| 11 | `11_effect_prop_overlay_generation/` | prop_effect | 소품/효과 오버레이 | 3 |
| 12 | `12_sfx_generation/` | audio | SFX 생성 | 0 |
| 13 | `13_bgm_generation/` | audio | BGM 프롬프트 설계 | 0 |
| 14 | `14_audio_packaging_and_looping/` | audio | 오디오 패키징/루프 | 0 |

## Test

ComfyUI may be off. When it is running at `172.28.224.1:8000`:

```bash
python3 scripts/run_workflow_smoke_tests.py --endpoint http://172.28.224.1:8000
python3 scripts/run_workflow_smoke_tests.py --endpoint http://172.28.224.1:8000 --execute --one-per-workflow
```
