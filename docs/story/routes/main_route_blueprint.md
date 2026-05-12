# 메인 루트 블루프린트

상태: DRAFT

## 제작 방식

현재 제작 방식은 `scene-flow-first, scene-by-scene production`입니다.

1. 데모 전체 장면 흐름과 에셋 범위를 먼저 문서로 잠근다.
2. 실제 대사/연출/에셋 제작은 S01부터 한 장면씩 진행한다.
3. 각 장면은 scene card → Ren'Py 구현 → 정적 테스트/lint → 가능하면 스크린샷 QA 순서로 검증한다.
4. 플레이어에게 보이는 최종 배경/CG/스프라이트는 ComfyUI 후보 생성 + contact sheet review + Ren'Py screenshot QA 후 승격한다.

## 루트 목표

주인공이 왕립 마법 학원에 전이/편입되고, 측정구 오류와 봉인 마도구 사고를 통해 “숨겨진 대현자”로 오해받기 시작하는 10~15분 데모 루트. 초반에는 운 좋은 평범한 사람처럼 보이되, 후반에는 작은 숨은 재능의 떡밥을 남긴다.

## 확정된 방향

- 주인공: 초반은 평범/운 중심, 후반에 작은 숨은 재능 떡밥.
- 하린: 학생회 감찰 담당. 기존의 차갑기만 한 감시자보다, 작고 야무진 귀여운 츤데레 감찰관으로 재정의한다.
- 첫 사건: 측정구 오류 + 봉인 마도구 사고.
- 톤: 착각 코미디를 유지하되, 공식 감시/파벌 압박/봉인 기록이라는 진지한 비용을 남긴다.

## 데모 장면 흐름

| Scene ID | 상태 | 목적 | 주인공 실제 의도 | 주변 해석 | 선택지/변수 | 주요 에셋 |
|---|---|---|---|---|---|---|
| `ch01_s01_summoning_measurement` | PLAYABLE DRAFT | 이세계 학원 도입 + 측정 불능 | 상황 파악, 시키는 대로 손 올림 | 침착한 등장, 대마력 은폐 | `choice_measurement_reaction` | `bg_summoning_hall`, `cg_measurement_orb`, 하린 neutral_pout/suspicious_blush |
| `ch01_s02_artifact_lab` | PLAYABLE DRAFT | 봉인 마도구 폭주와 우연한 정지 | 위험에서 벗어나기 | 고대 봉인식 해석 | `choice_artifact_action` | `bg_artifact_lab`, `cg_sealed_artifact` |
| `ch01_s03_special_observation` | PLAYABLE DRAFT | 특별 관찰 대상 공식 지정 | 오해를 풀거나 조용히 넘어가기 | 위험 인물의 계산된 대응 | `choice_final_response` | 보고실/인장, 특별 관찰 문서 CG |
| `ch01_s04_harin_watch` | PLANNED CARD | 하린 감시 관계와 일상 정보 비대칭 | 학원 규칙을 배우기 | 규칙/소문 통제 전략 | `choice_harin_answer` | 학원 복도, 하린 당황/삐짐/작은 미소 표정 |
| `ch01_s05_demo_ending_hook` | PLANNED CARD | 데모 종료 후크와 다음 챕터 압박 | 하루를 끝내고 싶음 | 대현자 후보/파벌 견제 대상 | `choice_demo_ending_attitude` | 게시판/공지 CG, 엔딩 후크 음악 |

## 장면 카드 파일

- `docs/story/scenes/ch01_s01_summoning_measurement.yaml`
- `docs/story/scenes/ch01_s02_artifact_lab.yaml`
- `docs/story/scenes/ch01_s03_special_observation.yaml`
- `docs/story/scenes/ch01_s04_harin_watch.yaml`
- `docs/story/scenes/ch01_s05_demo_ending_hook.yaml`

## 에셋 범위

최소 데모 에셋과 제작 우선순위는 `docs/assets/asset_manifest.yaml`을 따른다.

핵심 원칙:

- 하린 neutral_pout/suspicious_blush 스프라이트가 최우선이다.
- 그다음 강당 배경, 실습동 배경, 측정구 CG, 봉인 마도구 CG를 만든다.
- S03~S05 배경/문서 CG는 S01~S02 시각 품질이 확인된 뒤 제작한다.
- 생성 이미지에 가짜 한글/가짜 UI가 보이면 Ren'Py 텍스트박스로 의미를 전달하고, 이미지 안 글자는 피한다.

## 엔딩 초안

### `ending_great_sage_rumor`

조건: `reputation >= 3` 또는 `misunderstanding_score >= 3`

학생들 사이에 “측정 불능 편입생이 고대 마도구를 해제했다”는 소문이 퍼진다. 주인공은 그냥 운이 좋았다고 생각하지만, 학원장은 특별 관찰을 명한다.

### `ending_harin_suspicion`

조건: `harin_suspicion >= 2` 또는 `reputation < 3`

하린은 주변의 과대평가를 그대로 믿지 않는다. 하지만 주인공이 너무 허술하게 위험에 휘말리는 모습을 보고, “감찰일 뿐”이라고 우기며 직접 따라붙는다.

### `ending_balanced_hook`

조건: `harin_trust >= 1`, `reputation >= 2`, `harin_suspicion <= 1`

하린은 주인공이 수상하지만 악의는 없다고 판단한다. 다만 그걸 인정하기 싫어서 “보고서 작성을 줄이기 위한 조치”라며 옆에 서겠다고 말한다.

## 변수 흐름

- 착각이 커질수록 `misunderstanding_score` 증가.
- 공식 평판/소문은 `reputation` 증가.
- 하린이 “정말 모르는 사람 같다/혼자 두면 위험하다”고 느끼면 `harin_trust` 증가.
- 하린이 “연기일 수 있다/수상하지만 신경 쓰인다”고 느끼면 `harin_suspicion` 증가.
- 파벌/귀족반의 견제는 `rival_pressure` 증가.
- 작은 진짜 재능 떡밥은 `hidden_talent_hint` 증가.

## 다음 구현 단계

1. S04 `ch01_s04_harin_watch`를 TDD로 실제 Ren'Py 장면으로 확장.
2. S04 구현 후 정적 테스트와 Ren'Py lint 실행.
3. S01 시각화용 에셋 제작 시작: 하린 neutral_pout/suspicious_blush 스프라이트, 강당 배경, 측정구 CG.
4. S01 screenshot QA 후 S02 에셋으로 이동.
