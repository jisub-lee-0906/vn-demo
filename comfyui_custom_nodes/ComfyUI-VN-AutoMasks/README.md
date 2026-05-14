# ComfyUI-VN-AutoMasks

Deterministic custom mask nodes for the vn-demo ComfyUI workflow pack.

## Node

### VN_AlphaEdgeRefine

Purpose: refine the RGBA output of `BiRefNetRMBG(background=Alpha)` when close-up QA finds tiny exterior residue, detached alpha islands, or faint edge speckles.

Inputs:
- `image`: RGBA IMAGE from BiRefNet alpha output
- `alpha_threshold`: minimum alpha considered foreground for analysis
- `edge_alpha_cut`: faint boundary alpha below this value is trimmed inside the exterior edge band
- `island_min_area`: detached components smaller than this are removed unless they are the largest silhouette
- `bridge_radius`: small close/open radius used before component filtering so hair/clothing edges are not fragmented too aggressively
- `edge_width`: width of the boundary band where faint-alpha trimming is allowed
- `max_removed_coverage`: fail-closed limit; if removal is too broad, the node returns the original alpha

Outputs:
- `refined_image`: RGBA image with cleaned alpha
- `refined_alpha`: final alpha mask
- `removed_mask`: pixels removed by the cleanup
- `debug_overlay`: green=kept alpha, red=removed residue
- `removed_coverage`: removed pixel fraction

Recommended conservative settings for 03 alpha detailed-edge smoke:
- `alpha_threshold=0.015`
- `edge_alpha_cut=0.045`
- `island_min_area=96`
- `bridge_radius=1`
- `edge_width=2`
- `max_removed_coverage=0.030`

Design notes:
- This is not a replacement for fixing source-side sticker rims. If the source PNG already has a bright outline attached to the character, fix 01/02/06 source generation or mask/inpaint settings first.
- This node targets alpha-matte residue: tiny detached islands and very faint boundary alpha.
- It is intentionally conservative and should be promoted only after light/dark composite QA.

### VN_AutoCollarCleanupMask

Purpose: create a fail-closed local cleanup mask for old collar/bow/shirt remnants after 06 outfit replacement.

Inputs:
- `image`: final outfit candidate image
- `character_mask`: character silhouette mask, used to prevent background edits
- `protect_mask`: head/hair/face protection mask, used to derive the dynamic neck/chest ROI and prevent face/hair edits

Outputs:
- `cleanup_mask`: use this for local inpaint/composite
- `roi_mask`: debug region only
- `candidate_mask`: raw color/shape candidate before grow/blur
- `debug_overlay`: yellow=ROI, red=raw candidate, green=final cleanup mask
- `coverage`: final cleanup mask coverage fraction

Design notes:
- This node is deterministic: same image/masks/settings -> same mask.
- It does not call an LLM or segmentation model internally.
- It intentionally fails closed when candidates are too small, too large, or too broad relative to the neck/chest ROI.
- It should be driven by upstream BiRefNet/Florence masks inside a reproducible ComfyUI workflow.

Recommended current conservative settings for VN sprites after cross-character smoke:
- `mode=blue_bow_only`
- `roi_top_pad=24`
- `roi_height=170`
- `roi_width_scale=0.42`
- `candidate_threshold=0.50`
- `max_coverage=0.025`
- `min_coverage=0.003`
- `grow=8`
- `blur=7`

Verification note:
- Dirty source `hermes_06_cleanup_stage_d22_source.png`: earlier broad settings produced a non-empty local cleanup mask around the old bow/collar.
- Clean hoodie source: empty final cleanup mask, because raw candidate coverage stayed below `min_coverage`.
- Pink twin-braids denim smoke exposed the broad settings as too permissive on shirt/torso shadows; the current canonical workflow uses the stricter ROI/coverage/grow settings above.
- Avoid the broad `hoodie_collar_bow` default for production until it is retuned; it can confuse normal hoodie shading/bright fabric with remnants.
