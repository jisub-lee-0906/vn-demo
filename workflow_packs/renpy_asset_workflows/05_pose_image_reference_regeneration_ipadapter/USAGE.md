# 05 Pose image-reference regeneration / IPAdapter identity + pose donor img2img 사용법

목적: text-only pose donor를 단순 후보로 끝내지 않고, 승인 캐릭터 identity/style reference와 결합해서 같은 캐릭터에 가까운 pose variant 후보를 만든다.

## 이번 검증 판정

- Workflow verdict: PASS as production-direction workflow candidate
- 기존 post-alpha composite보다 확실히 좋음
- arms-crossed / one-hand-on-hip 모두 후보 PASS
- 아직 최종 game-ready / promotion-ready는 아님
- 다음 게이트: Ren'Py screen-fit QA + 손/edge 최종 검토

## 기본 노드 구성

- `CheckpointLoaderSimple(novaAnimeXL_ilV125.safetensors)`
- `CLIPSetLastLayer(-2)`
- pose donor `LoadImage -> VAEEncode`
- approved identity/reference `LoadImage`
- `IPAdapterModelLoader(ip-adapter-plus_sdxl_vit-h.safetensors)`
- `CLIPVisionLoader(clip-vision_vit-h.safetensors)`
- `IPAdapterAdvanced`
- `KSampler(euler_ancestral, normal, steps=28, cfg=6.0)`
- `VAEDecode -> SaveImage`
- selected outputs -> `BiRefNetRMBG(model=BiRefNet_toonout, mask_offset=0, mask_blur=0, refine_foreground=false, background=Alpha)`

## 재사용 기본 패턴

1. text-only pose donor를 먼저 만든다.
2. pose donor를 img2img latent source로 사용한다.
3. 승인된 캐릭터 소스를 IPAdapter identity/style reference로 사용한다.
4. 아래 두 세팅을 기본 sweep으로 돌린다.

```text
denoise=0.42, IPAdapter weight=0.60
denoise=0.50, IPAdapter weight=0.55
```

5. selected source를 `BiRefNet_toonout offset=0 blur=0 refine=false`로 alpha 처리한다.
6. full/head + dark/checker QA sheet를 만든다.
7. Ren'Py screen-fit QA를 통과해야 promotion한다.

## 이번 선택 결과

### arms-crossed

Best source:
- `arms_refregen_d0p42_w0p6_00001_.png`

Alternative source:
- `arms_refregen_d0p5_w0p55_00001_.png`

Best transparent PNG:
- `alpha_arms_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`

Alternative transparent PNG:
- `alpha_arms_refregen_d0p5_w0p55_toonout_o0_b0_ref0_00001_.png`

### one-hand-on-hip

Best source:
- `hip_refregen_d0p42_w0p6_00001_.png`

Alternative source:
- `hip_refregen_d0p5_w0p55_00001_.png`

Best transparent PNG:
- `alpha_hip_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`

Alternative transparent PNG:
- `alpha_hip_refregen_d0p5_w0p55_toonout_o0_b0_ref0_00001_.png`

## QA files

Arms:
- `refregen_arms_contact_full.png`
- `refregen_arms_contact_head.png`
- `refregen_alpha_full_dark.png`
- `refregen_alpha_full_checker.png`
- `refregen_alpha_head_dark.png`
- `refregen_alpha_head_checker.png`

Hip:
- `refregen_hip_contact_full.png`
- `refregen_hip_contact_head.png`
- `refregen_hip_alpha_full_dark.png`
- `refregen_hip_alpha_full_checker.png`
- `refregen_hip_alpha_head_dark.png`
- `refregen_hip_alpha_head_checker.png`

Verdict:
- `refregen_ipadapter_pose_donor_verdict.md`

Manifests/stats:
- `refregen_ipadapter_pose_manifest.json`
- `refregen_hip_ipadapter_pose_manifest.json`
- `refregen_alpha_manifest.json`
- `refregen_hip_alpha_manifest.json`
- `refregen_alpha_stats.json`
- `refregen_hip_alpha_stats.json`

## PASS 기준

- pose donor의 제스처가 유지됨
- 승인 캐릭터와 hair/outfit/face direction이 가까워짐
- post-alpha composite처럼 손/소매/가디건 ghost가 붙지 않음
- dark/checker alpha QA에서 큰 matte failure가 없음
- Ren'Py 화면에서 크기/대사창/배경/edge가 통과함

## 주의점

- `d0.42/w0.60`이 현재 가장 안전한 균형점입니다.
- `d0.50/w0.55`는 cardigan/style pull이 더 강할 수 있지만 표정/pose drift가 커질 수 있습니다.
- 이 workflow는 production-direction candidate이지, Ren'Py QA 전 최종 완성은 아닙니다.
- pointing은 아직 약하므로 이 route에 넣기 전 더 좋은 pointing donor가 필요합니다.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
