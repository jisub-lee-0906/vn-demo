# VN demo workflow packs

이 저장소는 Ren'Py용 에셋 workflow pack의 데모 보관소입니다. canonical pack은 `workflow_packs/renpy_asset_workflows/`에 있으며, 해당 폴더의 `AGENTS.md`와 README가 사용 규칙 및 workflow 역할의 기준입니다.

## 공개 준비 상태 (2026-09-23)

- **이번 환경에서 확인한 것:** README와 canonical JSON workflow pack의 정적 구조만 검토했습니다. 애플리케이션, ComfyUI backend, 모델, GPU, 외부 API는 실행하지 않았습니다.
- **과거 기록:** `.analysis/`의 smoke 보고서는 당시 실행 기록이며 현재 환경의 성공 증거가 아닙니다. 해당 스크립트에는 당시 개인별 WSL/ComfyUI 경로와 backend 주소가 남아 있어, 일반 복제본에서 그대로 실행하는 안내로 사용하면 안 됩니다.
- **미검증:** ComfyUI queue 제출, 모델/노드 호환성, 생성 이미지, 출력 품질, Ren'Py 런타임 통합.

## 구조

- `workflow_packs/renpy_asset_workflows/`: 현재 canonical workflow README와 `*_workflow_api.json`.
- `workflow_packs/workflow_backup/`: 이전 workflow 사본. 호환성·비교·복구 근거로 보존하며 자동 실행 대상이 아닙니다.
- `.analysis/`: 과거 smoke 실행 스크립트와 보고서. 이 스크립트들은 live ComfyUI backend와 환경별 input/output 경로를 필요로 합니다.

## 로컬 점검 범위

로컬에서 안전하게 할 수 있는 점검은 JSON parse 및 Python 문법 검사입니다. `.analysis` smoke 스크립트는 ComfyUI queue에 제출하고 생성 결과를 확인하는 live 검증용이므로, backend·모델·GPU를 사용하지 않는 점검에서는 실행하지 마십시오.

workflow 원본, backup, 과거 smoke 보고서는 보존했습니다. 이 공개 준비 정리에서는 live smoke를 실행하지 않았습니다. 과거 성공 보고서를 현재 환경의 실행 성공으로 해석하지 마십시오.

## 자동 검증 현황 (2026-09-23)

GitHub Actions 워크플로와 실행 기록은 없습니다. 위 로컬 테스트·빌드 기록을 원격 CI 통과로 해석하지 마세요.
