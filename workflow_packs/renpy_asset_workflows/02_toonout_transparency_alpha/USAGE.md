# 02 Toonout transparency / alpha 사용법

목적: 선택한 캐릭터 소스 이미지를 Ren'Py에서 쓸 수 있는 투명 PNG로 만든다.

## 이번 검증 소스

- 원본 기준 이미지: `../01_character_anchor_and_prompt/artifacts/source_auburn_719238043_00001_.png`
- 선택 투명 PNG: `artifacts/alpha_toonout_offp0_b0_ref0_00001_.png`

## 권장 ComfyUI 노드/설정

- Node/model: `BiRefNet_toonout`
- `mask_offset=0`
- `mask_blur=0`
- `refine_foreground=false`
- background/output: Alpha / transparent PNG

## 왜 offset=0인가

이번 auburn/high-contrast hair 캐릭터는 positive offset을 쓰면 회색 배경 edge가 더 보존되어 dark background에서 halo가 커졌습니다.

현재 규칙:

- auburn/dark/high-contrast hair: `offset=0 blur=0 refine=false`부터 시작
- silver/pale hair: hair detail 보존 때문에 `offset=+1 blur=0 refine=false`도 후보

## QA 방법

반드시 white background가 아니라 아래를 봅니다.

- full dark: `artifacts/qa_alpha_full_dark.png`
- full checker: `artifacts/qa_alpha_full_checker.png`
- head dark: `artifacts/qa_alpha_head_dark.png`
- head checker: `artifacts/qa_alpha_head_checker.png`
- edge head dark: `artifacts/qa_alpha_edge_head_dark.png`

## PASS 기준

- PNG alpha min=0, max=255
- 배경이 실제 투명함
- dark/checker에서 큰 회색/흰색 halo가 없음
- 머리카락 끝과 curl이 과도하게 잘리지 않음
- 의도된 검은 anime lineart는 제거하지 않음

## 주의점

- halo가 보이면 먼저 matting/edge 문제로 봅니다. 소스 캐릭터를 다시 생성하지 않습니다.
- green/chroma background는 BiRefNet에서 초록 spill을 남길 수 있으므로 기본값은 neutral gray입니다.

## API templates now available

Replay templates were added under `../api_workflows/`:
- `02_alpha_toonout_o0_b0_ref0_api.json` — selected setting
- `02_alpha_toonout_o1_b0_ref0_api.json`
- `02_alpha_toonout_o2_b0_ref0_api.json`
- `02_alpha_toonout_o1_b1_ref0_api.json`
- `02_alpha_toonout_o1_b0_ref1_api.json`

Required input image in ComfyUI input folder: `hermes_other_auburn_seed719238043.png`.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
