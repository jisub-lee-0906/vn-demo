# 04 Pose source generation / text-only donor 사용법

목적: arms-crossed, one-hand-on-hip 같은 큰 팔/제스처 변화의 pose donor/source를 만든다.

## 이번 검증 판정

- Text-only pose source generation: PASS
- Direct same-character production pose: FAIL
- IPAdapter img2img large-pose change: FAIL / over-preserves clasped-hands pose

## 방법 구분

### 실패한 방법: IPAdapter img2img로 큰 pose 변경

- `denoise=0.58/ipadapter=0.46`
- `denoise=0.68/ipadapter=0.36`

결과: 얼굴/의상은 잘 보존하지만 원래 clasped/prayer hands 포즈에 묶임.

### 통과한 방법: text-only pose source

- `CheckpointLoaderSimple(novaAnimeXL_ilV125.safetensors)`
- `CLIPSetLastLayer(-2)`
- 기준 캐릭터와 비슷한 prompt를 text-only로 작성
- pose phrase를 명확히 입력
- IPAdapter/reference image 없이 생성
- 선택 후보만 `BiRefNet_toonout offset=0 blur=0 refine=false`로 alpha 처리

## 이번 선택 pose donor

소스:

- hand-to-chest: `artifacts/source_hand_chest_txt_s1_00001_.png`
- one-hand-on-hip: `artifacts/source_hip_txt_s0_00001_.png`
- arms-crossed: `artifacts/source_cross_txt_s0_00001_.png`
- pointing: `artifacts/source_point_txt_s1_00001_.png`

투명 PNG:

- hand-to-chest: `artifacts/alpha_hand_chest_toonout_o0_b0_ref0_00001_.png`
- one-hand-on-hip: `artifacts/alpha_one_hand_hip_toonout_o0_b0_ref0_00001_.png`
- arms-crossed: `artifacts/alpha_arms_crossed_toonout_o0_b0_ref0_00001_.png`
- pointing: `artifacts/alpha_pointing_toonout_o0_b0_ref0_00001_.png`

## 제스처별 판정

- hand-to-chest: pose-source PASS
- one-hand-on-hip: pose-source PASS, 제스처 가장 명확
- arms-crossed: pose-source PASS, 다음 refinement에 가장 좋은 후보
- pointing: weak pose-source, leaning/crop/scale/outfit drift가 커서 production 아님

## Prompt 팁

기존 clasped/prayer pose를 피하려면 negative에 아래를 넣습니다.

```text
hands clasped together, prayer hands, both hands on chest
```

pointing은 추가로 아래를 피합니다.

```text
leaning forward, bent over, crouching, dynamic action pose, huge hand, close-up hand
```

## 다음 production route

이 workflow는 production-ready pose가 아니라 pose donor 생성용입니다.

production-ready로 가려면 다음 중 하나 이상이 필요합니다.

1. donor에서 pose guide/control 추출 후 기준 캐릭터로 다시 생성
2. 기준 캐릭터 얼굴/머리 composite
3. character LoRA 또는 더 강한 identity adapter
4. outfit/detail cleanup/inpaint
5. 다시 `BiRefNet_toonout` alpha
6. Ren'Py screen-fit QA

## QA

- pose 후보 contact: `artifacts/pose_source_contact.png`
- alpha dark/checker: `artifacts/pose_alpha_full_dark.png`, `artifacts/pose_alpha_full_checker.png`
- head crop: `artifacts/pose_alpha_head_dark.png`, `artifacts/pose_alpha_head_checker.png`

## API templates now available

Replay templates were added under `../api_workflows/`:
- `04_pose_textonly_source_*_api.json` for text-only pose donor/source generation.
- `04_pose_alpha_*_toonout_o0_b0_ref0_api.json` for selected pose-source alpha conversion.

These are pose donors, not final same-character pose sprites. Use good donors as geometry/source images for `05_pose_image_reference_regeneration_ipadapter`.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
