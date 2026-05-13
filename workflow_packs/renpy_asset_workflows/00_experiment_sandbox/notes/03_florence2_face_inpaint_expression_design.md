# 00 experiment — 03 Florence-2 face inpaint expression workflow design

Status: promoted to `03_expression_variation_face_composite/` after silver-bob smoke tests; keep this file as sandbox history/design notes.
Date: 2026-05-13

Purpose: test a new 03 expression route for Nova Anime XL IL v19.0 where the approved 01 anchor/source image keeps pose, outfit, body, and background, while only the face expression changes.

This started in `00_experiment_sandbox/` and was promoted after batch1-3 silver-bob source tests plus 02 alpha smoke. New unproven variants should still start in the sandbox before changing the numbered 03 folder.

## 2026-05-13 smoke result summary

Use the executed sandbox workflow:

```text
workflow_api/00_03_expression_florence2_face_composite_smoke_api.json
```

Do not use raw inpaint as the final output. Save three outputs per run:

1. mask preview
2. raw inpaint diagnostic
3. final composited image: `ImageCompositeMasked(destination=original, source=raw_inpaint, mask=face_mask)`

Observed result on the accepted silver-bob v19 anchor:

- `face` mask + final composite preserves non-face pixels very well.
- Face-mask coverage was about `1.9%` of pixels.
- Composite outside-mask mean RGB delta was about `0.0003`; changed outside-mask pixels were about `0.0002%`.
- `happy_open` and `surprised` were visibly distinct and usable candidates.
- `sad` and `fearful` were readable but need tuning.
- `disgusted` was weak/overlapped with neutral/angry.
- `mouth, eyes` mask was too small on this character (`~0.218%`) and produced almost no expression change.

Evidence files:

```text
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch1_composites.png
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch1_masks.png
ComfyUI/output/hermes_vn_expression_florence2_composite/batch1_manifest.json
ComfyUI/output/hermes_vn_expression_florence2_composite/batch1_metrics.json
```

Promotion status: batch1 was not enough by itself; later batch2/batch3 plus 02 alpha smoke led to promotion into the numbered 03 folder. Second-character smoke is still recommended before broad production use.

## 2026-05-13 additional tuning + alpha smoke

Batch2 tuned the weak expressions while keeping the same face-mask composite route.

Evidence files:

```text
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch2_tuned_composites.png
ComfyUI/output/hermes_vn_expression_florence2_composite/batch2_manifest.json
ComfyUI/output/hermes_vn_expression_florence2_composite/batch2_metrics.json
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/contact_batch2_alpha_light_dark.png
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/batch2_alpha_manifest.json
```

Batch2 findings:

- Non-face preservation stayed strong: face mask coverage about `1.9%`; outside-mask RGB delta remained around `0.0003`.
- `sad_crying` is the best sad candidate; readable as sad/worried but still not a strong crying expression.
- `fearful_wide_open` is the best fear candidate; readable but overlaps with surprised.
- `angry` is readable and usable as a mild angry/annoyed expression.
- `disgusted_frown_halfclosed` and `disgusted_uneasy` still read closer to annoyed/angry than disgusted; disgusted remains unresolved.
- Alpha smoke passed technically for `happy_open`, `surprised`, `sad_crying`, `fearful_wide_open`, and `angry`. Light/dark previews showed no obvious severe clipping; silver hair edges retain a visible light rim on dark background consistent with the current 02 alpha behavior.

Current candidate set for user QA:

- `happy_open`
- `surprised`
- `sad_crying`
- `fearful_wide_open`
- `angry`

Still useful after promotion:

1. User visual QA on the candidate set.
2. A second-character smoke to confirm Florence face masks generalize beyond silver-bob.
3. If stronger disgust is required, use a separate mouth/eye edit route or manual correction rather than more prompt-only stacking.


## Current live-node mapping

The user-provided spec names `Florence2Run` and `MaskBlur`. On the live ComfyUI backend, exact available nodes differ:

- Preferred Florence segmentation route: maintained kijai `ComfyUI-Florence2`
  - `DownloadAndLoadFlorence2Model` or `Florence2ModelLoader` → `Florence2Run`
  - `Florence2Run` task: `referring_expression_segmentation`
  - `text_input`: `face` first; `mouth, eyes` was too small in the first smoke.
- Avoid `AILab_Florence2` from ComfyUI-RMBG for this route if it fails with:
  - `Florence2LanguageConfig object has no attribute forced_bos_token_id`
- Mask blur/grow nodes available:
  - preferred for one-node face mask cleanup: `AILab_MaskEnhancer`
  - alternate: `GrowMask` then `ImpactGaussianBlurMask`
- Differential diffusion node available: `DifferentialDiffusion`
- Inpaint conditioning node available: `InpaintModelConditioning`
- SDXL Union ControlNet model available:
  - `xinsir-controlnet-union-sdxl-1.0-promax.safetensors`
- Union ControlNet type node available: `SetUnionControlNetType`
  - live options include `repaint`, not literal `inpaint`; use `repaint` for inpaint-style Union ControlNet.
- ControlNet apply node available: `ControlNetApplyAdvanced`
  - optional alternate for explicit mask-aware inpaint ControlNet: `ControlNetInpaintingAliMamaApply`.

## Design principle

Do not feed the 02 alpha PNG into 03. Use the approved 01 source/anchor PNG before transparency.

Reason: alpha edge artifacts can contaminate img2img/inpaint conditioning. After expression source passes QA, send the accepted source through 02 alpha.

## Recommended input anchor

Use the accepted dark-gray v19 01 source candidate:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_experiments/nova_t2i_il_v190_background_test/source_grey_dark_neg_gradient_seed719251035_00001_.png
```

Copy it to ComfyUI input before running, for example:

```text
ComfyUI/input/hermes_vn_expression/source_silver_bob_v190_darkgrey_anchor_seed719251035.png
```

Workflow JSON should reference the input-relative path:

```text
hermes_vn_expression/source_silver_bob_v190_darkgrey_anchor_seed719251035.png
```

## Node graph, target API node IDs

The exact IDs below are proposed for the 00 sandbox workflow. They are intentionally not the old 03 canonical IDs.

### 1. Load anchor image

Node `1`: `LoadImage`

Inputs:

```json
{
  "image": "hermes_vn_expression/source_silver_bob_v190_darkgrey_anchor_seed719251035.png"
}
```

Outputs:

- `1.IMAGE` → Florence-2 segmentation
- `1.IMAGE` → InpaintModelConditioning pixels
- `1.IMAGE` → ControlNet apply image
- `1.IMAGE` → optional preview/contact sheet
- `1.MASK` unused

### 2. Load Nova Anime XL IL v19 checkpoint

Node `2`: `CheckpointLoaderSimple`

Inputs:

```json
{
  "ckpt_name": "novaAnimeXL_ilV190.safetensors"
}
```

Outputs:

- `2.MODEL` → DifferentialDiffusion
- `2.CLIP` → positive/negative CLIPTextEncode
- `2.VAE` → InpaintModelConditioning and VAEDecode

### 3. Florence-2 automatic face mask

Node `3`: `AILab_Florence2`

Inputs:

```json
{
  "image": ["1", 0],
  "model_name": "microsoft/Florence-2-large",
  "task": "Polygon Mask (text prompt)",
  "precision": "fp16",
  "attention": "sdpa",
  "fill_mask": true,
  "text_prompt": "face",
  "output_mask_select": "",
  "keep_model_loaded": false
}
```

Prompt candidates:

- first test: `face`
- if mouth/eye change is too weak or too broad: `mouth, eyes`
- do not use natural-language generation prompt here; this is segmentation text only.

Outputs:

- `3.MASK` → mask cleanup
- `3.IMAGE` optional mask overlay/preview only
- `3.JSON` optional diagnostics; can feed `AILab_Florence2ToCoordinates` if coordinates are needed later.

### 4. Mask cleanup

Preferred single-node cleanup:

Node `4`: `AILab_MaskEnhancer`

Inputs:

```json
{
  "mask": ["3", 1],
  "sensitivity": 1.0,
  "mask_blur": 8,
  "mask_offset": 8,
  "smooth": 2.0,
  "fill_holes": true,
  "invert_output": false
}
```

Outputs:

- `4.MASK` → InpaintModelConditioning mask
- `4.MASK` → optional `MaskToImage` preview

Alternate cleanup if AILab_MaskEnhancer misbehaves:

```text
3.MASK -> GrowMask(expand 6~12) -> ImpactGaussianBlurMask(kernel_size 8~12, sigma 4~8) -> InpaintModelConditioning.mask
```

Mask rule:

- Too small: expression barely changes.
- Too large: hair/face shape/background/outfit may drift.
- The first useful target is face-only, not whole head/hair.

### 5. Positive prompt conditioning

Node `5`: `CLIPTextEncode`

Input `clip`: `["2", 1]`

Base positive should preserve the 01 identity/style and add only expression tags.

For happy first smoke:

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, thick_outline, simple_background, grey_background, dark_background, smile, closed_mouth, happy, BREAK depth_of_field, volumetric_lighting
```

Danbooru-only rule:

- Use tags like `smile`, `closed_mouth`, `open_mouth`, `frown`, `angry`, `crying`, `tears`, `surprised`, `wide-eyed`, `raised_eyebrows` only if confirmed to behave.
- Remove any tag that produces no visible change.
- Do not add natural-language phrases such as `same outfit`, `preserve background`, etc. Preserve those via mask/control/image path, not text.

### 6. Negative prompt conditioning

Node `6`: `CLIPTextEncode`

Input `clip`: `["2", 1]`

Base negative:

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, dynamic_pose, crossed_arms, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, gradient_background, patterned_background, changed_clothes, different_clothes, different_hair, (worst quality, bad quality:1.2)
```

Expression-specific negative examples:

- happy: remove `smile`/`happy` from negative; optionally add `sad, angry, crying, tears, surprised`.
- sad: add `smile, happy, angry, surprised`.
- angry: add `smile, happy, sad, surprised`.
- surprised: add `smile, angry, sad, crying`.

Important: never leave the target expression banned in the negative prompt.

### 7. Differential diffusion model wrapper

Node `7`: `DifferentialDiffusion`

Inputs:

```json
{
  "model": ["2", 0],
  "strength": 1.0
}
```

Outputs:

- `7.MODEL` → KSampler model

Role:

- Apply inpaint-friendly differential diffusion to soften boundary transitions and reduce visible face-mask seams.

### 8. Inpaint model conditioning

Node `8`: `InpaintModelConditioning`

Inputs:

```json
{
  "positive": ["5", 0],
  "negative": ["6", 0],
  "vae": ["2", 2],
  "pixels": ["1", 0],
  "mask": ["4", 0],
  "noise_mask": true
}
```

Outputs:

- `8.positive` → ControlNet apply positive input, or directly to KSampler if ControlNet disabled
- `8.negative` → ControlNet apply negative input, or directly to KSampler if ControlNet disabled
- `8.latent` → KSampler latent_image

Data flow:

- Anchor image pixels are VAE-encoded into latent space.
- Face mask becomes the sampling/noise mask.
- Only masked face area should receive meaningful denoise; unmasked body/outfit/background should remain intact.

### 9. Load Union ControlNet SDXL

Node `9`: `ControlNetLoader`

Inputs:

```json
{
  "control_net_name": "xinsir-controlnet-union-sdxl-1.0-promax.safetensors"
}
```

Outputs:

- `9.CONTROL_NET` → SetUnionControlNetType

### 10. Set Union ControlNet type

Node `10`: `SetUnionControlNetType`

Inputs:

```json
{
  "control_net": ["9", 0],
  "type": "repaint"
}
```

Notes:

- User spec says Type `inpaint`.
- Live node options do not include literal `inpaint`; they include `repaint`.
- Treat `repaint` as the installed Union-ControlNet inpaint/repaint route.

Outputs:

- `10.CONTROL_NET` → ControlNetApplyAdvanced

### 11. Apply ControlNet

Node `11`: `ControlNetApplyAdvanced`

Inputs:

```json
{
  "positive": ["8", 0],
  "negative": ["8", 1],
  "control_net": ["10", 0],
  "image": ["1", 0],
  "strength": 0.55,
  "start_percent": 0.0,
  "end_percent": 0.85,
  "vae": ["2", 2]
}
```

Outputs:

- `11.positive` → KSampler positive
- `11.negative` → KSampler negative

Role:

- Keep global structure, pose, outfit, and background locked to the original anchor while the masked face changes.

Conservative strength candidates:

- first smoke: `0.55`
- if expression too weak: `0.45` controlnet + more prompt, or denoise adjustment, not both at once
- if face/identity drifts: `0.70` and/or lower denoise to `0.35`

### 12. KSampler

Node `12`: `KSampler`

Inputs:

```json
{
  "model": ["7", 0],
  "positive": ["11", 0],
  "negative": ["11", 1],
  "latent_image": ["8", 2],
  "seed": 719251035,
  "steps": 28,
  "cfg": 5.0,
  "sampler_name": "euler_ancestral",
  "scheduler": "karras",
  "denoise": 0.45
}
```

Required setting from spec:

- `denoise: 0.45` fixed for first test.
- `seed: 719251035`, same as the accepted 01 source seed.
- Scheduler: test `karras` first, then `sgm_uniform` only if karras gives seams/noisy face.

Caution:

- `denoise 0.45` is high enough to change expression, but may alter eyes/face shape if mask is too large.
- If expression is readable but identity drifts, change mask size or denoise, not prompt length first.

### 13. Decode and save

Node `13`: `VAEDecode`

Inputs:

```json
{
  "samples": ["12", 0],
  "vae": ["2", 2]
}
```

Outputs:

- `13.IMAGE` → SaveImage

Node `14`: `SaveImage`

Inputs:

```json
{
  "images": ["13", 0],
  "filename_prefix": "hermes_vn_expression_florence2_inpaint/source_silver_bob_happy_seed719251035"
}
```

## End-to-end data flow

```text
LoadImage.IMAGE
  ├─> Florence2 face segmentation
  │     └─> MaskEnhancer / blur+grow
  │           └─> InpaintModelConditioning.mask
  ├─> InpaintModelConditioning.pixels
  │     └─> InpaintModelConditioning.latent
  └─> ControlNetApplyAdvanced.image

CheckpointLoaderSimple.MODEL
  └─> DifferentialDiffusion
        └─> KSampler.model

CheckpointLoaderSimple.CLIP
  ├─> Positive CLIPTextEncode
  └─> Negative CLIPTextEncode

Positive/Negative CONDITIONING
  └─> InpaintModelConditioning
        └─> ControlNetApplyAdvanced
              └─> KSampler conditioning

KSampler latent output
  └─> VAEDecode
        └─> SaveImage
```

## First smoke preset

Use one expression first, not a full batch.

Recommended first expression: `happy` because it is easy to see while still safe for identity testing.

```text
expression positive delta: smile, closed_mouth, happy
expression negative additions: sad, angry, crying, tears, surprised
seed: 719251035
steps: 28
cfg: 5.0
sampler: euler_ancestral
scheduler: karras
Denoise: `0.38` for first happy smoke, `0.40` for batch1 face-mask expressions
ControlNet strength: 0.55
ControlNet type: repaint
Florence prompt: face
MaskEnhancer: mask_blur 3, mask_offset 0, smooth 1, fill_holes true
```

If the first output changes outfit/background:

1. Inspect the mask preview first.
2. Reduce mask offset/blur.
3. Increase ControlNet strength.
4. Lower denoise to `0.35` only after mask/control are checked.

If expression is too weak:

1. Prefer tuning Danbooru expression tags first while keeping `face` mask.
2. Keep denoise near `0.40` and change one variable at a time.
3. Do not switch to `mouth, eyes` unless the face mask causes unacceptable face-shape/skin drift; first smoke showed `mouth, eyes` was too small.
4. Do not stack long natural-language prompts.

## QA gates used for promotion to 03 folder

These gates were used before promoting this route into `03_expression_variation_face_composite/`. Reuse them for future major changes:

1. Source output keeps original body, clothing, bowtie, cardigan, skirt, pantyhose, and dark gray background.
2. Only face/mouth/eyes/eyebrows visibly change.
3. No badge/emblem/logo drift returns.
4. No face shape change or hair color change.
5. At least 3 expressions are readable with the same graph:
   - happy
   - sad or angry
   - surprised or fearful
6. Accepted expression source still passes 02 alpha.
7. Before broad production use, run a second-character smoke to ensure Florence face masking generalizes.

## Known risks

- Florence face mask may include hair; if so, use `mouth, eyes` or shrink mask.
- Union ControlNet type is `repaint` on this backend, not literal `inpaint`.
- `denoise 0.45` may be too high for identity if mask is broad.
- Danbooru expression tags can be weaker than natural language; keep the prompt short and verify visually.
- ControlNet may fight expression changes if strength is too high.


## 2026-05-13 disgusted retry batch3

Disgusted-specific batch3 ran seven face-mask composite variants.

Evidence files:

```text
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch3_disgust_composites.png
ComfyUI/output/hermes_vn_expression_florence2_composite/contact_batch3_disgust_masks.png
ComfyUI/output/hermes_vn_expression_florence2_composite/batch3_disgust_manifest.json
ComfyUI/output/hermes_vn_expression_florence2_composite/batch3_disgust_metrics.json
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/contact_batch3_disgust_alpha_light_dark.png
ComfyUI/output/hermes_vn_expression_florence2_alpha_smoke/batch3_disgust_alpha_manifest.json
```

Findings:

- Mask stayed face-only with no outfit/body/background spill; coverage remained about `1.9%`.
- Outside-mask RGB delta remained near `0.0003`, so composite preservation still works.
- Best candidate is `disgust_nauseated` (`disgusted, nauseated, wavy_mouth, half-closed_eyes, furrowed_brow`, denoise `0.45`, seed `719251505`). It reads as mild disgust/unease, not strong repulsion.
- Alternate candidates: `disgust_averted` reads avoidant/annoyed, and `disgust_strong_scowl` reads more angry than disgusted.
- Alpha smoke for `disgust_nauseated`, `disgust_averted`, and `disgust_strong_scowl` passed technically; no severe clipping, same mild silver-hair rim behavior as other 02 alpha outputs.

Decision: keep `disgust_nauseated` as the provisional disgusted candidate if a default 7-expression set requires disgusted. Do not spend more prompt-only cycles on disgusted unless user rejects it; further improvement likely needs a different image signal or manual/keyframed mouth-eye edit rather than more tag stacking.
