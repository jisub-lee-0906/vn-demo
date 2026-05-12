# 변수 리스트

상태: DRAFT

이 문서는 이세계 마법 학원 착각물 구조를 `demo/game/script.rpy`에 구현하기 위한 Ren'Py 변수 설계표입니다. 구현 전까지는 초안입니다.

## 명명 규칙

- 플레이어/캐릭터 ID: snake_case
- 평판/착각 수치: `reputation`, `misunderstanding_score`
- 히로인 관계 수치: `<character>_trust`, `<character>_suspicion`
- 사건 플래그: `event_<name>_resolved`
- 단서/정보 플래그: `clue_<name>_known`
- 선택지 기록: `choice_<scene>_<decision>`

## 기본 변수

| 변수 | 타입 | 초기값 | 목적 | 저장 여부 |
|---|---:|---:|---|---|
| `player_name` | str | `"서진"` | 주인공 표시명 | save |
| `reputation` | int | `0` | 학원 내 공식/비공식 명성 | save |
| `misunderstanding_score` | int | `0` | 주인공 의도가 과대해석된 정도 | save |
| `harin_trust` | int | `0` | 하린이 주인공의 선의를 믿는 정도 | save |
| `harin_suspicion` | int | `0` | 하린이 주인공을 의심하는 정도 | save |
| `faculty_interest` | int | `0` | 교수/학원장의 관심도 | save |
| `rival_pressure` | int | `0` | 귀족/라이벌 파벌의 견제 강도 | save |
| `hidden_talent_hint` | int | `0` | 주인공의 작은 숨은 재능 떡밥 누적. 1차 데모에서는 확정 공개하지 않음 | save |

## 사건 플래그

| 변수 | 타입 | 초기값 | 켜지는 조건 | 사용처 |
|---|---:|---:|---|---|
| `event_measurement_overflow` | bool | `False` | 측정구가 측정 불능/오류 판정 | 첫 명성 사건 |
| `event_artifact_stopped` | bool | `False` | 마도구 폭주가 멈춤 | 데모 후반 |
| `event_special_observation` | bool | `False` | 특별 관찰 대상으로 지정됨 | 엔딩/다음 장면 |

## 정보/단서 플래그

| 변수 | 타입 | 초기값 | 의미 |
|---|---:|---:|---|
| `clue_measurement_error_known` | bool | `False` | 측정구 오류 가능성을 주인공/하린이 인식 |
| `clue_artifact_safety_line_seen` | bool | `False` | 바닥 안전선/봉인 좌표를 봄 |
| `clue_academy_legend_heard` | bool | `False` | 측정 불능 전설/소문을 들음 |

## 선택지 기록 플래그

| 변수 | 타입 | 초기값 | 선택지 | 효과 |
|---|---:|---:|---|---|
| `choice_measurement_reaction` | str/null | `None` | `silent` / `explain` / `retry` | 평판/의심 조정 |
| `choice_harin_answer` | str/null | `None` | `honest` / `ambiguous` / `deflect` | 신뢰/착각 조정 |
| `choice_artifact_action` | str/null | `None` | `step_back` / `freeze` / `touch` | 마도구 사건 결과 |
| `choice_final_response` | str/null | `None` | `accept_watch` / `deny_power` | 엔딩 톤 |

## 변수 변화 예시

| 상황 | 변화 |
|---|---|
| 측정구 앞에서 침묵 | `misunderstanding_score += 1`, `reputation += 1` |
| “저도 잘 모르겠습니다”라고 해명 | `harin_suspicion += 1`, `misunderstanding_score += 1` |
| 측정구 재시도 | `reputation += 1`, `faculty_interest += 1` |
| 하린에게 솔직히 모른다고 말함 | `harin_trust += 1`, `harin_suspicion += 1` |
| 애매한 대답으로 넘김 | `misunderstanding_score += 1` |
| 위험해서 뒤로 물러남 | `event_artifact_stopped = True`, `reputation += 1`, 조건부 `hidden_talent_hint += 1` |
| 마도구를 직접 만짐 | `faculty_interest += 1`, 실패 시 `harin_suspicion += 1` |

## 분기 기준 초안

### 대현자 소문 엔딩

```renpy
if reputation >= 3 or misunderstanding_score >= 3:
    jump ending_great_sage_rumor
```

### 하린 의심 엔딩

```renpy
if harin_suspicion >= 2 and harin_trust < 2:
    jump ending_harin_suspicion
```

### 균형 후크 엔딩

```renpy
if harin_trust >= 1 and reputation >= 2 and harin_suspicion <= 1:
    jump ending_balanced_hook
```

## 착각물 시스템 원칙

- `reputation`은 외부 평판입니다. 높을수록 주변이 주인공을 크게 봅니다.
- `misunderstanding_score`는 코미디/오해 누적입니다. 높을수록 설명해도 더 오해받습니다.
- `harin_trust`와 `harin_suspicion`은 동시에 오를 수 있습니다. 하린은 “악의는 없어 보이지만 정체는 수상하다”고 느낄 수 있습니다.
- 1차 데모에서는 화면에 수치를 직접 표시하지 않습니다. 대사/연출로만 보여줍니다.
- `hidden_talent_hint`는 후반 떡밥용입니다. 데모 안에서는 “우연만은 아닐지도 모른다” 정도로만 암시합니다.
- 변수를 너무 늘리지 않습니다. 실제 구현 첫 버전은 위 목록 중 8~10개만 사용합니다.
