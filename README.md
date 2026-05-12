# vn-demo

새 Ren'Py 프로젝트 `demo/`의 기획/제작 루트입니다.

현재 단계는 **게임 제작 전 프리프로덕션 문서화 단계**입니다. 아래 문서를 먼저 읽고, 승인된 항목만 실제 `demo/game/*.rpy` 구현으로 옮깁니다.

## 현재 프로젝트 위치

- Ren'Py 프로젝트: `demo/`
- 게임 스크립트: `demo/game/script.rpy`
- GUI 설정: `demo/game/gui.rpy`
- 옵션 설정: `demo/game/options.rpy`
- 기획 문서: `docs/`

## 문서 읽는 순서

1. `docs/00_document_index.md` — 문서 목록과 현재 승인 상태
2. `docs/01_project_brief.md` — 게임 한 줄 콘셉트, 톤, 핵심 약속
3. `docs/story/characters/character_sheets.md` — 캐릭터 설정 시트
4. `docs/story/synopsis_and_plot.md` — 시놉시스와 플롯
5. `docs/systems/variable_list.md` — 변수/플래그/분기 목록
6. `docs/design/scope_and_scale.md` — 데모 스케일과 제작 범위
7. `docs/design/system_ui_resolution.md` — 시스템 UI와 해상도 규칙

## 현재 Ren'Py 기본값 확인

현재 생성된 `demo` 프로젝트는 Ren'Py 기본 템플릿 상태입니다.

- `config.name`: `demo`
- `build.name`: `demo`
- 해상도: `1920x1080` (`demo/game/gui.rpy`의 `gui.init(1920, 1080)`)
- 한국어 폰트: `SourceHanSansLite.ttf`
- 현재 스크립트: 기본 아이린 예시 문장만 있음

## 운영 규칙

- 이 문서들은 초안입니다. 사용자가 승인하거나 수정한 내용만 canon으로 승격합니다.
- 스토리/캐릭터/변수는 먼저 문서에서 안정화한 뒤 `script.rpy`에 반영합니다.
- 플레이어에게 보이는 배경/캐릭터/CG는 나중에 ComfyUI 산출물 + Ren'Py 스크린샷 QA 후 승격합니다.
- 초반 목표는 거대한 완성작이 아니라 10~15분 안팎의 PC용 세로 조각(vertical slice)입니다.
