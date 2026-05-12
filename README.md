# vn-demo

새 Ren'Py 프로젝트 `demo/`의 기획/제작 루트입니다.

현재 제작 방식은 **scene-flow-first, scene-by-scene production**입니다.
먼저 데모 전체 장면 흐름과 최소 에셋 범위를 문서로 잠그고, 실제 제작은 S01부터 한 장면씩 구현/에셋/QA로 진행합니다.

## 현재 프로젝트 위치

- Ren'Py 프로젝트: `demo/`
- 게임 스크립트: `demo/game/script.rpy`
- GUI 설정: `demo/game/gui.rpy`
- 옵션 설정: `demo/game/options.rpy`
- 기획 문서: `docs/`
- 에셋 범위 문서: `docs/assets/asset_manifest.yaml`

## 현재 플레이 가능 범위

- `ch01_s01_summoning_measurement`: 구현됨, placeholder-safe
- `ch01_s02_artifact_lab`: 구현됨, placeholder-safe
- `ch01_s03_special_observation`: 구현됨, placeholder-safe
- `ch01_s04_harin_watch`: scene card 작성됨, 아직 미구현
- `ch01_s05_demo_ending_hook`: scene card 작성됨, 아직 미구현

## 문서 읽는 순서

1. `docs/00_document_index.md` — 문서 목록과 현재 승인 상태
2. `docs/01_project_brief.md` — 게임 한 줄 콘셉트, 톤, 핵심 약속
3. `docs/story/characters/character_sheets.md` — 캐릭터 설정 시트
4. `docs/story/synopsis_and_plot.md` — 시놉시스와 플롯
5. `docs/story/routes/main_route_blueprint.md` — 데모 전체 장면 흐름
6. `docs/assets/asset_manifest.yaml` — 최소 데모 에셋 범위와 제작 우선순위
7. `docs/systems/variable_list.md` — 변수/플래그/분기 목록
8. `docs/design/scope_and_scale.md` — 데모 스케일과 제작 범위
9. `docs/design/system_ui_resolution.md` — 시스템 UI와 해상도 규칙

## 현재 Ren'Py 기본값 확인

- `config.name`: `demo`
- `build.name`: `demo`
- 해상도: `1920x1080` (`demo/game/gui.rpy`의 `gui.init(1920, 1080)`)
- 한국어 폰트: `SourceHanSansLite.ttf`
- 현재 스크립트: 이세계 왕립 마법 학원 착각물 S01~S03 구현

## 운영 규칙

- 이 문서들은 초안입니다. 사용자가 승인하거나 수정한 내용만 canon으로 승격합니다.
- 스토리/캐릭터/변수는 먼저 문서에서 안정화한 뒤 `script.rpy`에 반영합니다.
- 플레이어에게 보이는 배경/캐릭터/CG는 ComfyUI 산출물 + contact sheet review + Ren'Py screenshot QA 후 승격합니다.
- 초반 목표는 거대한 완성작이 아니라 10~15분 안팎의 PC용 vertical slice입니다.
- GitHub 업로드는 private repo 기준이며, 루트 `.gitignore`가 Ren'Py 캐시/세이브/비밀 파일/로컬 생성물을 제외합니다.

## 검증 명령

```bash
cd /home/jisub-lee/workspace/vn-demo
python3 tools/run_static_tests.py
/mnt/c/Users/Desktop/Documents/Renpy/renpy-8.5.2-sdk/renpy.sh /home/jisub-lee/workspace/vn-demo/demo lint
```

## 다음 작업

1. `ch01_s04_harin_watch`를 TDD로 실제 Ren'Py 장면으로 구현합니다.
2. S04 구현 후 정적 테스트와 Ren'Py lint를 통과시킵니다.
3. 그다음 S01 에셋 제작을 시작합니다.
   - `sprite_harin_neutral`
   - `sprite_harin_suspicious`
   - `bg_summoning_hall`
   - `cg_measurement_orb`
