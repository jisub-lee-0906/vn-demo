# 하린 귀여운 츤데레 재디자인 후보 QA (2026-05-12)

상태: DRAFT / candidate only / not promoted

## 요청

기존 하린 디자인과 대사가 매력이 부족하므로, 하린을 더 귀여운 츤데레 감찰 담당으로 재정의하고 캐릭터 후보 여러 장을 생성해 사용자 선택을 받는다.

## 문서/대사 변경

- `docs/story/characters/character_sheets.md`: 차갑기만 한 감시자에서 작고 야무진 귀여운 츤데레 감찰관으로 재정의.
- `docs/story/routes/main_route_blueprint.md`: 하린 관계 축을 “감찰이라고 우기지만 챙겨주는” 방향으로 수정.
- `docs/story/synopsis_and_plot.md`: 데모 후크 대사를 츤데레 톤으로 수정.
- `demo/game/script.rpy`: 하린 주요 대사를 더 귀엽고 당황/삐짐이 보이는 톤으로 수정.
- 기존 semantic PNG 참조는 재디자인 선택 전까지 placeholder-safe Solid로 되돌림.

## 생성 런

- Run dir: `/home/jisub-lee/workspace/vn-demo/generated/comfyui/harin_tsundere_candidates_20260512_215310`
- Contact sheet: `/home/jisub-lee/workspace/vn-demo/generated/comfyui/harin_tsundere_candidates_20260512_215310/harin_tsundere_contact_sheet.png`
- Manifest: `/home/jisub-lee/workspace/vn-demo/generated/comfyui/harin_tsundere_candidates_20260512_215310/RUN_MANIFEST.json`
- Workflow base: `workflow_packs/renpy_asset_workflows/api_workflows/01_character_anchor_seed719238043_api.json`
- Policy: prompt/seed/output prefix만 수정. 사용자 선택 전 alpha/semantic promotion 금지.

## 후보 메모

- s01: 밝은 단발/큰 눈/오버핏 가디건. 귀여움 강함. 머리 옆 리본처럼 보이는 장식 확인 필요.
- s02: 낮은 양갈래/단정한 감찰관. 손/허리 디테일 확인 필요.
- s03: 강한 홍조/선명한 히로인감. 빨간 머리와 장식이 커서 큰 방향 전환.
- s04: 한 손 허리 + 삐진 표정. 츤데레 감정이 직접적으로 읽힘.
- s05: 팔짱 + 삐진 표정. 감찰/츤데레 캐릭터성이 또렷함. 제복이 회색 재킷 쪽으로 변형.
- s06: 보고서 폴더를 든 감찰 담당 느낌. 차분하고 fake text 없음.

## 다음 게이트

1. 사용자가 s01~s06 중 후보를 선택한다.
2. 선택 후보만 workflow 02 `BiRefNet_toonout` alpha로 처리한다.
3. alpha min/max/count + dark/checker/contact QA를 기록한다.
4. Ren'Py semantic path에 neutral/suspicious 후보를 승격한다.
5. lint/tests/screenshot QA 후 `docs/assets/asset_manifest.yaml` status를 갱신한다.


## 사용자 선택 및 s03 승격 메모

- User selection: `s03`
- Source: `generated/comfyui/harin_tsundere_candidates_20260512_215310/s03_harin_tsundere.png`
- Alpha workflow: repo-local workflow 02 `02_alpha_toonout_o0_b0_ref0_api.json`
- Alpha output: `generated/comfyui/harin_tsundere_candidates_20260512_215310/alpha_s03_toonout/s03_harin_tsundere_alpha.png`
- Alpha stats: min=0, max=255, transparent=1045771, opaque=705440, semi=18261
- QA sheets:
  - `generated/comfyui/harin_tsundere_candidates_20260512_215310/alpha_s03_toonout/s03_alpha_full_dark.png`
  - `generated/comfyui/harin_tsundere_candidates_20260512_215310/alpha_s03_toonout/s03_alpha_full_gray.png`
  - `generated/comfyui/harin_tsundere_candidates_20260512_215310/alpha_s03_toonout/s03_alpha_full_checker.png`
- Semantic promotion:
  - `demo/game/images/characters/harin/harin_neutral.png`
  - `demo/game/images/characters/harin/harin_suspicious.png`
  - `demo/game/images/backgrounds/bg_summoning_hall.png`
  - `demo/game/images/cg/cg_measurement_orb.png`

Caveat: `harin_suspicious`는 현재 distinct expression이 아니라 선택된 s03 neutral anchor를 임시 재사용합니다. 다음 표현 workflow에서 별도 suspicious/tsundere expression을 만들어야 합니다.

## Verification after promotion

- Static tests: PASS `python3 tools/run_static_tests.py` — 11 passed.
- Ren'Py lint: PASS `/mnt/c/Users/Desktop/Documents/Renpy/renpy-8.5.2-sdk/renpy.sh /home/jisub-lee/workspace/vn-demo/demo lint`.
- Ren'Py testcase screenshot: PASS `qa_s01_harin_s03_assets`.
- Screenshot path: `generated/renpy_s01_asset_promotion_qa_2026-05-12/qa_s01_harin_s03_assets.png`.
- Screenshot QA: background fills the screen after scaling, Harin s03 sprite appears on the right, Korean dialogue is readable, and sprite does not block the textbox.
- Remaining caveat: distinct suspicious expression has now been generated/promoted separately; see `docs/assets/harin_suspicious_expression_qa_2026-05-12.md`.
