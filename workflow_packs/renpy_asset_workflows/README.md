# VN auburn character ComfyUI workflow backup (2026-05-12)

Windows path:
`C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`

WSL path:
`/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`

이 백업은 이미지 파일 보관용이 아니라, 추후 아무 기억이 없는 상태에서도 Ren'Py 게임 에셋을 ComfyUI로 다시 만들 수 있게 하는 재현 가능한 템플릿 팩입니다.

핵심 보존 대상:
- 재사용 가능한 사용법
- ComfyUI `/prompt` API workflow JSON
- prompt/seed/settings/model/node 기록
- PASS/FAIL QA 기준
- Ren'Py 투입 전 검증 절차

PNG 산출물은 예시/QA 참고자료일 뿐이며, 주 목적은 재현 가능한 제작법과 API 템플릿 보존입니다.

상세 의도는 `TEMPLATE_INTENT.md`에 정리했습니다.

## 현재 PASS / 사용 가능 워크플로우

1. `01_character_anchor_and_prompt`
   - NovaAnimeXL 계열 txt2img로 Ren'Py 대화용 auburn 캐릭터 기준 후보 생성.
   - 결과물: 기준 소스 이미지 + 후보 contact sheet + prompt/seed manifest.

2. `02_toonout_transparency_alpha`
   - 선택한 기준 캐릭터를 `BiRefNet_toonout`으로 투명 PNG화.
   - auburn/high-contrast hair 기준 추천값: `mask_offset=0`, `mask_blur=0`, `refine_foreground=false`.
   - 결과물: 투명 PNG + dark/checker/head QA + 판정문.

3. `03_expression_variation_ipadapter_img2img`
   - 기준 캐릭터에서 IPAdapter img2img로 smile/surprised/sad/angry 표정 변형.
   - 결과물: 표정 소스, 표정 투명 PNG, contact/QA, prompt/alpha manifest.
   - 판정: expression workflow candidate PASS. Ren'Py screen-fit은 아직 별도 게이트.

4. `04_pose_source_generation_textonly`
   - 큰 제스처/팔 포즈는 direct IPAdapter img2img보다 text-only pose source가 잘 나옴.
   - hand-to-chest / one-hand-on-hip / arms-crossed는 pose-source PASS.
   - pointing은 weak pose-source.
   - 판정: pose donor/source 생성은 PASS. 최종 same-character pose에는 05번 ref-generation을 사용.

5. `05_pose_image_reference_regeneration_ipadapter`
   - 최신 업데이트: text-only pose donor를 img2img latent source로 쓰고, 승인 캐릭터를 IPAdapter identity/style reference로 넣는 pose ref-generation workflow.
   - 이전 `05_not_completed_pose_identity_refinement` post-alpha composite 방향은 제거했고, 이 방식으로 교체했습니다.
   - arms-crossed / one-hand-on-hip 모두 production-direction workflow candidate PASS.
   - 추천 기본값: `denoise=0.42`, `IPAdapter weight=0.60`; 보조 후보 `denoise=0.50`, `IPAdapter weight=0.55`.
   - alpha: `BiRefNet_toonout mask_offset=0 mask_blur=0 refine_foreground=false`.
   - 결과물: source 후보, transparent PNG 후보, full/head contact, dark/checker alpha QA, manifest/stats, 판정문.
   - 아직 Ren'Py screen-fit / final hand-edge QA 전이므로 최종 promotion-ready는 아님.

## 제거된 이전 방식

- 기존 `05_not_completed_pose_identity_refinement` 폴더는 제거했습니다.
- 제거 이유: broad face/hair 또는 hair-only post-alpha composite는 neutral reference의 손/소매/가디건 조각을 새 포즈에 ghost로 붙여서 production 방향으로 부적합했습니다.
- 대체 방식: `05_pose_image_reference_regeneration_ipadapter`.

## 공통 ComfyUI 접속

현재 WSL에서 Windows ComfyUI는 아래 endpoint가 확인되었습니다.

```text
http://172.28.224.1:8000
```

사용 전 확인:

```bash
curl -fsS http://172.28.224.1:8000/system_stats
curl -fsS http://172.28.224.1:8000/queue
```

공유 ComfyUI이므로 다른 작업 큐가 있으면 interrupt/clear하지 말고 대기하거나 사용자 확인을 받아야 합니다.

## 파일 구성

각 폴더에는 다음이 있습니다.

- `USAGE.md`: 재사용 방법, PASS/FAIL 조건, 주의점
- `artifacts/` 또는 workflow 폴더 내부 manifest/verdict: prompt/seed/settings, 판정문, PASS/FAIL 기록. PNG/contact/QA sheets는 cleanup 후 제거됨
- `api_workflows/`: 01~05 character/source/alpha/expression/pose/ref-generation 재현용 ComfyUI `/prompt` API JSON 템플릿

원본 산출물은 그대로 아래에 남아 있습니다.

```text
C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_toonout_other_character
C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_expression_smoke_auburn
C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_pose_smoke_auburn
```


## API 템플릿 완성 상태

`api_workflows/`에 01~04 API 템플릿을 추가해 현재 캐릭터 스프라이트 제작 체인의 재현성이 보강되었습니다.

현재 API 템플릿 수:
- 01 character anchor: 3
- 02 toonout alpha: 5
- 03 expression source/alpha: 12
- 04 pose text-only source/alpha: 12
- 05 pose ref-generation/alpha example: 5

사용법과 입력 이미지명은 `api_workflows/README.md` 및 `api_workflows/API_TEMPLATE_INDEX.json`을 기준으로 확인합니다.

## Cleanup status (2026-05-12)

This folder has been reduced to reproducibility files only. Generated PNG examples, contact sheets, QA image sheets, and `test_runs/` execution outputs were removed. Keep `CLEANUP_POLICY.md` and `cleanup_manifest.json` as the cleanup record.

New next-workflow templates were added:
- `06_background_generation_no_text/` + `api_workflows/06_background_generation_no_text_api.json`
- `07_background_variation_img2img_layout_lock/` + `api_workflows/07_background_variation_img2img_layout_lock_api.json`
- `08_event_cg_no_text_story_beat/` + `api_workflows/08_event_cg_no_text_story_beat_api.json`

06 and 07 have smoke evidence from 2026-05-12: 06 is a minimal no-text classroom baseline, and 07 is closed as a rain/weather variation template. 07 is not a day/night conversion workflow; generate day/night backgrounds separately through 06. 08 is now smoke-passed as a sealed-envelope hallway hook CG candidate. Run Ren'Py screenshot QA before promotion.

## Canonical-only update (2026-05-12)

Per user correction, the completed 01-05 character/sprite chain now keeps only the most successful canonical API templates. Alternate seeds, alpha sweeps, weaker expression variants, weak pointing pose templates, and ref-generation alternatives were removed.

See:
- `CANONICAL_WORKFLOW_POLICY.md`
- `api_workflows/API_TEMPLATE_INDEX.json`

06 is smoke-passed as a minimal background baseline, 07 is smoke-passed for rain/weather variation, and 08 is smoke-passed as a no-text event-CG candidate. None are game-promotion-ready until Ren'Py screenshot QA passes.

## Canonical prompting guide

실제 제작 시 프롬프트를 어떻게 수정해야 하는지는 `CANONICAL_PROMPTING_GUIDE.md`를 기준으로 합니다. 이 파일에는 01~05 canonical workflow별 prompt block, negative block, denoise/IPAdapter/alpha 설정, PASS/FAIL 기준, 그리고 06~08 다음 템플릿의 프롬프팅 방법이 정리되어 있습니다.

08 update: smoke-passed sealed-envelope hallway hook CG candidate; not game-promotion-ready until RenPy screenshot QA passes.


## Generation expansion scaffold (09-14)

Per the expanded asset-generation scope, scaffold workflows were added after 08:

- `09_support_character_generation/` + `api_workflows/09_support_character_anchor_teacher_api.json` + `api_workflows/09_support_character_alpha_toonout_api.json`
- `10_outfit_costume_variation/` + `api_workflows/10_outfit_casual_img2img_ipadapter_api.json` + `api_workflows/10_outfit_alpha_toonout_api.json`
- `11_effect_prop_overlay_generation/` + prop/effect API templates
- `12_sfx_generation/` procedural/library/AI SFX design + helper script
- `13_bgm_generation/` instrumental BGM mood/prompt design
- `14_audio_packaging_and_looping/` Ren'Py `.ogg` conversion/manifest design

Status distinction: 09-11 now have smoke-passed/current accepted generation directions (09 support teacher, 10 PuLID+i2i outfit, 11 minimal key prop + magic shimmer). 12-14 are design/packaging/audio prototype scaffolds until final audio backend/listening/mastering decisions are made.
