# 시스템 UI 및 해상도 문서

상태: DRAFT / 현재 Ren'Py 파일 기반

## 현재 해상도

현재 `demo/game/gui.rpy` 기준:

```renpy
gui.init(1920, 1080)
```

1차 데모 기본 해상도는 **1920x1080, 16:9, PC 기준**으로 고정합니다.

## 폰트

현재 `demo/game/gui.rpy` 기준:

```renpy
define gui.text_font = "SourceHanSansLite.ttf"
define gui.name_text_font = "SourceHanSansLite.ttf"
define gui.interface_text_font = "SourceHanSansLite.ttf"
```

- 한국어 표시 가능 폰트가 이미 프로젝트에 들어 있음.
- 향후 더 보기 좋은 폰트로 교체 가능하지만, 교체 시 라이선스와 Ren'Py lint를 확인해야 함.

## 대사창 기본값

현재 `demo/game/gui.rpy` 기준:

| 항목 | 값 |
|---|---:|
| `gui.textbox_height` | 278 |
| `gui.textbox_yalign` | 1.0 |
| `gui.name_xpos` | 360 |
| `gui.name_ypos` | 0 |
| `gui.dialogue_xpos` | 402 |
| `gui.dialogue_ypos` | 75 |
| `gui.dialogue_width` | 1116 |
| `gui.text_size` | 33 |
| `gui.name_text_size` | 45 |

## 선택지 UI 기본값

| 항목 | 값 |
|---|---:|
| `gui.choice_button_width` | 1185 |
| `gui.choice_button_text_size` | 33 |
| `gui.choice_button_text_xalign` | 0.5 |

주의:

- 하린을 중앙/우측에 크게 배치할 경우 선택지 박스가 얼굴/상체를 가릴 수 있음.
- 중요한 선택지 장면은 반드시 스크린샷으로 확인 후 `choice` 위치/폭 조정.

## 화면 구성 원칙

### 일반 대화

- 배경: 1920x1080 전체 화면
- 캐릭터: 상반신~허벅지 위 스프라이트
- 단일 화자 첫 등장: 중앙 또는 약간 우측, 크게 배치
- 대화 상대 구도: 좌/우 대립 배치
- 대사창: 하단 고정, 얼굴/핵심 손동작을 가리지 않게 조정

### 미스터리 단서 CG

- CG는 대사창을 고려해 하단 25%에 핵심 단서가 오지 않게 제작
- 메모나 글자가 들어간 CG는 AI가 만든 가짜 글자를 피하고, 필요한 글자는 Ren'Py 텍스트나 별도 후편집으로 처리
- 하단 텍스트박스 영역은 깨끗하게 유지

### 메인 메뉴

현재는 Ren'Py 기본 메뉴 이미지 사용.

1차 커스텀 목표:

- 너무 어두운 고대비 UI보다 밝고 읽기 쉬운 VN UI
- 비 오는 창가/교실 분위기를 암시하는 배경
- 버튼은 한국어 기준 충분한 폭 확보

## 스프라이트 제작 규격

권장:

- 투명 PNG RGBA
- 원본 생성/마스터: 896x1280 또는 1024x1536 계열 후보
- 게임 내 배치: Transform zoom/xalign/yalign으로 조정
- 머리 전체와 상반신/허벅지 위가 잘리지 않는 구도

검증:

- 흰 배경뿐 아니라 검정/회색/체커 배경에서 알파 확인
- 실제 1920x1080 Ren'Py 화면에서 머리/대사창/선택지 충돌 확인

## QA 체크리스트

- [ ] 1920x1080으로 실행되는가?
- [ ] 한국어 글자가 tofu/네모로 깨지지 않는가?
- [ ] 대사창이 단서를 가리지 않는가?
- [ ] 선택지가 캐릭터 얼굴/핵심 포즈를 가리지 않는가?
- [ ] 배경 하단 25%가 텍스트를 읽기 좋게 비어 있는가?
- [ ] 저장/불러오기/환경설정 화면에서 한국어가 정상 표시되는가?
