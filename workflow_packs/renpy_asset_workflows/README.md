# RenPy ComfyUI workflow pack

Minimal reusable workflow pack for making RenPy visual-novel assets with ComfyUI.

Primary WSL path: `/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows`

Old Windows reference path: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`

## For AI agents

Read `AGENTS.md` first, then `WORKFLOW_INDEX.json`, then the target numbered folder README.

This pack is intentionally small. Historical/ambiguous workflows were removed or moved to backup; active `workflow_api/` folders should contain only the currently usable template(s).

## Workflow order

- Character base: `01_character_anchor_and_prompt`
- Expressions: `02_expression_variation_face_composite`
- Alpha/transparent sprite: `03_toonout_transparency_alpha`
- Backgrounds: `04_background_generation_no_text`
- Event CG: `05_event_cg_no_text_story_beat`
- Outfit/costume: `06_outfit_costume_variation`

## Index

| id | folder | category | purpose | API JSONs |
|---|---|---|---|---:|
| 01 | `01_character_anchor_and_prompt/` | character | 캐릭터 기준 앵커/source 생성 | 1 |
| 02 | `02_expression_variation_face_composite/` | character | 표정 변형 source 생성 | 1 |
| 03 | `03_toonout_transparency_alpha/` | character | 투명 스프라이트 알파/매팅 | 1 |
| 04 | `04_background_generation_no_text/` | background | 텍스트 없는 배경 생성 | 1 |
| 05 | `05_event_cg_no_text_story_beat/` | cg | 스토리 이벤트 CG | 1 |
| 06 | `06_outfit_costume_variation/` | character | 의상/코스튬 변형 | 1 |

## Test

ComfyUI may be off. When it is running at `172.28.224.1:8000`:

```bash
python3 scripts/run_workflow_smoke_tests.py --endpoint http://172.28.224.1:8000
```

The default command validates index paths and JSON syntax, then probes ComfyUI. Actual execution of workflows with `LoadImage` TEMPLATE placeholders requires preparing real input images first or using a specialized smoke script that patches inputs at runtime.

No generated PNG/contact sheets/audio dumps should be stored in this reusable pack.
