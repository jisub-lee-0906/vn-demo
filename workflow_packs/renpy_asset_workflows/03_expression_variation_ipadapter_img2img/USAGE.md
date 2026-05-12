# 03 Expression variation / IPAdapter img2img 사용법

목적: 기준 캐릭터의 얼굴/의상/프레이밍을 유지하면서 표정만 바꾼다.

## 이번 검증 판정

- Workflow verdict: PASS as expression-variation workflow candidate
- 아직 Ren'Py screen-fit proof는 별도 필요

## 기본 노드 구성

- `CheckpointLoaderSimple(novaAnimeXL_ilV125.safetensors)`
- `CLIPSetLastLayer(-2)`
- 기준 이미지 `LoadImage`
- 기준 이미지 `VAEEncode`로 img2img latent 생성
- `IPAdapterModelLoader(ip-adapter-plus_sdxl_vit-h.safetensors)`
- `CLIPVisionLoader(clip-vision_vit-h.safetensors)`
- `IPAdapterAdvanced`
- `KSampler`
- 선택 결과에 `BiRefNet_toonout offset=0 blur=0 refine=false`

## 설정 패턴

보수적 표정, 예: smile:

```text
denoise=0.42
IPAdapter weight=0.60
```

강한 표정, 예: surprised/sad/angry:

```text
denoise=0.54-0.56
IPAdapter weight=0.45-0.48
```

## 이번 선택 결과

표정 소스:

- smile: `artifacts/source_smile_keep_d0p42_w0p6_00001_.png`
- surprised: `artifacts/source_surprised_move_d0p54_w0p48_00001_.png`
- sad: `artifacts/source_sad_strong_move_d0p56_w0p45_00001_.png`
- angry: `artifacts/source_angry_move_d0p54_w0p48_00001_.png`

투명 PNG:

- smile: `artifacts/alpha_smile_toonout_o0_b0_ref0_00001_.png`
- surprised: `artifacts/alpha_surprised_toonout_o0_b0_ref0_00001_.png`
- sad: `artifacts/alpha_sad_toonout_o0_b0_ref0_00001_.png`
- angry: `artifacts/alpha_angry_toonout_o0_b0_ref0_00001_.png`

## QA

- 후보 contact: `artifacts/expression_source_contact.png`
- alpha full dark/checker: `artifacts/expression_alpha_full_dark.png`, `artifacts/expression_alpha_full_checker.png`
- alpha head dark/checker: `artifacts/expression_alpha_head_dark.png`, `artifacts/expression_alpha_head_checker.png`

## PASS 기준

- 표정이 VN 화면 크기에서 읽힐 정도로 명확함
- 같은 캐릭터로 보임
- 의상/머리 실루엣이 크게 변하지 않음
- 투명 PNG alpha가 실제로 존재함

## 주의점

- 큰 포즈 변화에는 이 방식이 약합니다. 표정 전용으로 사용하세요.
- sad는 route에서 극적인 울음이 필요하면 더 강하게 재시도해야 합니다.
- 최종 promotion 전에는 Ren'Py 배경/텍스트박스 위 screen-fit QA가 필요합니다.

## API templates now available

Replay templates were added under `../api_workflows/`:
- `03_expression_source_*_api.json` for IPAdapter img2img expression source generation.
- `03_expression_alpha_*_toonout_o0_b0_ref0_api.json` for selected expression alpha conversion.

Required source input for expression generation: `hermes_expr_auburn_neutral.png`.
Required alpha inputs: `hermes_expr_selected_smile.png`, `hermes_expr_selected_surprised.png`, `hermes_expr_selected_sad.png`, `hermes_expr_selected_angry.png`.

Use the conservative smile setting (`denoise=0.42`, IPAdapter `weight=0.60`) and stronger emotion settings (`denoise≈0.54-0.56`, IPAdapter `weight≈0.45-0.48`) as the first sweep.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
