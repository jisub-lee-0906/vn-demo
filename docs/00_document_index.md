# 문서 인덱스

상태 표기:

- `DRAFT`: 제작 방향 제안/초안. 사용자 승인 전.
- `APPROVED`: 현재 canon으로 사용 가능.
- `PLAYABLE_DRAFT`: Ren'Py에 구현되어 lint/test는 통과했지만, 최종 에셋/수동 QA 전.
- `PLANNED_CARD`: 장면 카드가 작성되었고, 아직 실제 Ren'Py 구현 전.
- `NEEDS_QA`: 구현 또는 화면 검증 필요.
- `DEFERRED`: 후순위.

## 핵심 문서

| 문서 | 목적 | 상태 |
|---|---|---|
| `01_project_brief.md` | 게임 콘셉트, 톤, 핵심 약속 | DRAFT |
| `story/characters/character_sheets.md` | 주요 캐릭터 설정 시트 | DRAFT |
| `story/synopsis_and_plot.md` | 시놉시스, 3막 플롯, 데모 장면 구성 | DRAFT |
| `story/routes/main_route_blueprint.md` | 데모 전체 장면 흐름과 제작 순서 | DRAFT |
| `assets/asset_manifest.yaml` | 최소 데모 에셋 범위와 제작 우선순위 | DRAFT |
| `systems/variable_list.md` | Ren'Py 변수, 선택지, 플래그 목록 | DRAFT |
| `design/scope_and_scale.md` | 제작 스케일, 에셋/음성/시나리오 범위 | DRAFT |
| `design/system_ui_resolution.md` | 1920x1080 UI/폰트/화면 구성 규칙 | DRAFT |

## 장면 카드

| 문서 | 목적 | 상태 |
|---|---|---|
| `story/scenes/ch01_s01_summoning_measurement.yaml` | 소환/측정 불능/하린 첫 등장 | PLAYABLE_DRAFT |
| `story/scenes/ch01_s02_artifact_lab.yaml` | 봉인 마도구 폭주와 우연한 정지 | PLAYABLE_DRAFT |
| `story/scenes/ch01_s03_special_observation.yaml` | 특별 관찰 대상 공식 지정 | PLAYABLE_DRAFT |
| `story/scenes/ch01_s04_harin_watch.yaml` | 하린 감시 관계와 일상 정보 비대칭 | PLANNED_CARD |
| `story/scenes/ch01_s05_demo_ending_hook.yaml` | 데모 엔딩 후크와 다음 챕터 압박 | PLANNED_CARD |

## 현재 작업 순서

1. 전체 데모 장면 흐름과 최소 에셋 범위를 문서로 잠근 상태를 유지한다.
2. `ch01_s04_harin_watch`를 TDD로 실제 Ren'Py 장면으로 구현한다.
3. S01 에셋 제작을 시작한다: 하린 기본/의심, 강당 배경, 측정구 CG.
4. S01 screenshot QA 후 S02 에셋으로 이동한다.
5. 이후 S05를 한 장면씩 구현/에셋/QA한다.
