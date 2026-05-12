# Pose image-reference regeneration verdict (IPAdapter identity + pose donor img2img)

Directory:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_pose_smoke_auburn/refregen_ipadapter_pose_donor`

Goal:
- Replace failed post-alpha compositing with image-reference regeneration.
- Use the pose donor as img2img latent source, and use the approved auburn neutral source as IPAdapter identity/style reference.
- Then apply `BiRefNet_toonout offset=0 blur=0 refine=false` for transparent PNG QA.

ComfyUI endpoint:
`http://172.28.224.1:8000`

Base nodes:
- `CheckpointLoaderSimple(novaAnimeXL_ilV125.safetensors)`
- `CLIPSetLastLayer(-2)`
- `LoadImage` pose donor -> `VAEEncode`
- `LoadImage` identity reference -> `IPAdapterAdvanced`
- `IPAdapterModelLoader(ip-adapter-plus_sdxl_vit-h.safetensors)`
- `CLIPVisionLoader(clip-vision_vit-h.safetensors)`
- `KSampler(euler_ancestral, normal, steps=28, cfg=6.0)`
- `VAEDecode` -> `SaveImage`
- selected outputs -> `BiRefNetRMBG(model=BiRefNet_toonout, mask_offset=0, mask_blur=0, refine_foreground=false, background=Alpha)`

## Arms-crossed sweep

Pose donor:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_pose_smoke_auburn/source_cross_txt_s0_00001_.png`

Identity reference:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_toonout_other_character/source_auburn_719238043_00001_.png`

Settings tested:
- `denoise=0.32`, `IPAdapter weight=0.65`
- `denoise=0.42`, `IPAdapter weight=0.60`
- `denoise=0.50`, `IPAdapter weight=0.55`

QA sheets:
- `refregen_arms_contact_full.png`
- `refregen_arms_contact_head.png`
- `refregen_alpha_full_dark.png`
- `refregen_alpha_full_checker.png`
- `refregen_alpha_head_dark.png`
- `refregen_alpha_head_checker.png`

Best arms-crossed candidates:
1. `arms_refregen_d0p42_w0p6_00001_.png`
2. `arms_refregen_d0p5_w0p55_00001_.png`

Best transparent candidates:
1. `alpha_arms_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`
2. `alpha_arms_refregen_d0p5_w0p55_toonout_o0_b0_ref0_00001_.png`

Arms-crossed verdict:
- PASS as an image-reference regeneration workflow candidate.
- Much better than post-alpha composite: no prayer-hands ghosting, no pasted seam.
- Arms-crossed pose remains readable across all three settings.
- `d0.42/w0.60` is the best balance: pose readable, cardigan closer to identity prompt, face not too harsh.
- `d0.50/w0.55` has slightly stronger pink cardigan/style pull but face/pose can drift more stylized.
- Not final production-ready yet because face expression still follows the donor's stern look more than the approved neutral, and hand/finger detail needs final QA.

## One-hand-on-hip sweep

Pose donor:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_pose_smoke_auburn/source_hip_txt_s0_00001_.png`

Settings tested:
- `denoise=0.32`, `IPAdapter weight=0.65`
- `denoise=0.42`, `IPAdapter weight=0.60`
- `denoise=0.50`, `IPAdapter weight=0.55`

QA sheets:
- `refregen_hip_contact_full.png`
- `refregen_hip_contact_head.png`
- `refregen_hip_alpha_full_dark.png`
- `refregen_hip_alpha_full_checker.png`
- `refregen_hip_alpha_head_dark.png`
- `refregen_hip_alpha_head_checker.png`

Best one-hand-on-hip candidates:
1. `hip_refregen_d0p42_w0p6_00001_.png`
2. `hip_refregen_d0p5_w0p55_00001_.png`

Best transparent candidates:
1. `alpha_hip_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`
2. `alpha_hip_refregen_d0p5_w0p55_toonout_o0_b0_ref0_00001_.png`

One-hand-on-hip verdict:
- PASS as an image-reference regeneration workflow candidate.
- Gesture remains readable and natural.
- `d0.42/w0.60` is the safest balance.
- `d0.50/w0.55` has a more pink/identity-pulled cardigan and pleasant expression, but may be slightly more stylized and less source-consistent.
- Not final production-ready until Ren'Py screen-fit QA and final hand/edge review.

## Alpha verdict

Alpha settings:
- `BiRefNet_toonout`
- `mask_offset=0`
- `mask_blur=0`
- `refine_foreground=false`

Alpha stats:
- all selected alpha outputs have alpha min=0, max=255.
- transparent ratio around 51-53%, confirming actual transparent background.

Dark-background QA:
- Edges are usable for workflow candidate.
- Hair rim is visible but not worse than the earlier auburn toonout baseline.
- No major full-canvas matte failure.

## Overall result

This confirms the user's proposed direction:
- image-reference regeneration is better than post-alpha compositing for pose variants.

Current best workflow:
1. Generate text-only pose donor.
2. Use pose donor as img2img latent source.
3. Use approved character as IPAdapter identity/style reference.
4. Sweep around:
   - `denoise=0.42`, `IPAdapter weight=0.60`
   - `denoise=0.50`, `IPAdapter weight=0.55`
5. Apply `BiRefNet_toonout offset=0 blur=0 refine=false`.
6. QA on full/head dark/checker sheets.

Status:
- PASS as production-direction workflow candidate.
- Not yet final game-ready/promotion-ready.
- Next gate: Ren'Py screen-fit QA with the two best transparent candidates, then decide whether to promote or run a small near-neighbor refinement around `d0.42/w0.60`.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
