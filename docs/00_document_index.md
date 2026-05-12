# 문서 인덱스

상태 표기:

- `DRAFT`: 제작 방향 제안/초안. 사용자 승인 전.
- `APPROVED`: 현재 canon으로 사용 가능.
- `NEEDS_QA`: 구현 또는 화면 검증 필요.
- `DEFERRED`: 후순위.

| 문서 | 목적 | 상태 |
|---|---|---|
| `01_project_brief.md` | 게임 콘셉트, 톤, 핵심 약속 | DRAFT |
| `story/characters/character_sheets.md` | 주요 캐릭터 설정 시트 | DRAFT |
| `story/synopsis_and_plot.md` | 시놉시스, 3막 플롯, 데모 장면 구성 | DRAFT |
| `systems/variable_list.md` | Ren'Py 변수, 선택지, 플래그 목록 | DRAFT |
| `design/scope_and_scale.md` | 제작 스케일, 에셋/음성/시나리오 범위 | DRAFT |
| `design/system_ui_resolution.md` | 1920x1080 UI/폰트/화면 구성 규칙 | DRAFT |

## 다음 작업 순서

1. 사용자가 콘셉트/톤을 확인한다.
2. 캐릭터 이름, 성격, 관계성을 승인 또는 수정한다.
3. 변수 목록을 실제 `script.rpy` 분기에 맞게 축소한다.
4. `label start`부터 1개 루트의 10~15분 데모를 TDD/스모크 테스트 기반으로 구현한다.
5. 캐릭터/배경/CG 에셋은 문서상 필요한 목록을 먼저 확정한 뒤 ComfyUI 워크플로우팩으로 생성한다.
