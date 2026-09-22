# VN demo workflow packs

이 저장소는 Ren'Py용 에셋 workflow pack의 데모 보관소입니다. canonical pack은 `workflow_packs/renpy_asset_workflows/`에 있으며, 해당 폴더의 `AGENTS.md`와 README가 사용 규칙 및 workflow 역할의 기준입니다.

## 구조

- `workflow_packs/renpy_asset_workflows/`: 현재 canonical workflow README와 `*_workflow_api.json`.
- `workflow_packs/workflow_backup/`: 이전 workflow 사본. 호환성·비교·복구 근거로 보존하며 자동 실행 대상이 아닙니다.
- `.analysis/`: 과거 smoke 실행 스크립트와 보고서. 이 스크립트들은 live ComfyUI backend와 환경별 input/output 경로를 필요로 합니다.

## 로컬 점검 범위

로컬에서 안전하게 할 수 있는 점검은 JSON parse 및 Python 문법 검사입니다. `.analysis` smoke 스크립트는 ComfyUI queue에 제출하고 생성 결과를 확인하는 live 검증용이므로, backend·모델·GPU를 사용하지 않는 점검에서는 실행하지 마십시오.

workflow 원본, backup, 과거 smoke 보고서는 보존했습니다. 이번 점검에서 live smoke의 초기 연결 시도는 실패했으며, 이미지 생성·출력 품질은 검증하지 못했습니다. 과거 성공 보고서를 현재 환경의 실행 성공으로 해석하지 마십시오.
