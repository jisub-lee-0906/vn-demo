# 10 outfit / costume variation

Status: USER-ACCEPTED COMPLETE for current workflow-template scope. Plain IPAdapter i2i failed, masked inpaint was a partial direction, and PuLID+i2i is the accepted practical route for diverse outfit-source generation with approximate face retention.

Purpose:
- Change the approved character outfit while preserving face, hair silhouette, eye color, crop scale, and VN sprite style.
- First smoke target: school-uniform auburn character -> casual beige sweater outfit.

API templates:
- `../api_workflows/10_outfit_casual_img2img_ipadapter_api.json`
- `../api_workflows/10_outfit_alpha_toonout_api.json`

Required inputs:
- Copy the approved identity/source sprite to ComfyUI input as `hermes_outfit_identity_source.png`.
- Copy selected outfit output for alpha as `hermes_outfit_casual_SOURCE_TO_PROCESS.png`.

Baseline settings:
- IPAdapter weight around `0.58`
- denoise around `0.50`
- lower denoise if face/style drift is too strong,
- higher denoise only if outfit refuses to change.

Design rule:
- Treat outfit variation as harder than expression variation. Do not call it canonical until a real artifact proves both outfit change and identity retention.

PASS for generation workflow candidate:
- target outfit visibly changed,
- same face/hair/eye family,
- no duplicate or inset character,
- crop scale remains dialogue-sprite usable,
- source background remains suitable for alpha.

FAIL:
- outfit barely changes,
- face/hair identity drifts more than the outfit improves,
- generated logos/text/patterns appear,
- hand/body artifacts dominate.

Next escalation if this fails:
- masked outfit edit / inpaint route that protects head/hair and changes torso/clothes only.


## 2026-05-12 masked inpaint smoke update

Status: MASKED INPAINT SMOKE PASS DIRECTION CANDIDATE, not final costume promotion-ready.

New API templates:
- `../api_workflows/10_outfit_masked_torso_inpaint_api.json`
- `../api_workflows/10_outfit_masked_torso_tight_inpaint_api.json`

Preferred current smoke output:
- Source: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\masked_torso_tight_pullover_d0p76_seed62018422_00001_.png`
- Alpha: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\alpha_masked_tight_pullover_toonout_o0_b0_ref0_00001_.png`
- Alpha QA: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\qa_alpha_masked_tight_black_gray_white.jpg`

Verdict:
- Better than the earlier full-image IPAdapter img2img route.
- Face/hair/crop remain stable because the final output composites only the masked clothing region over the original source.
- Tight mask is better than broad mask; broad mask caused an obvious lower horizontal seam.
- Remaining caveats: blue collar/tie remnants near clasped hands, school skirt still remains, and alpha QA shows gray hair-edge halo on black.
- Do not fall back to plain i2i yet; masked route is viable. Next improvement should use a better clothing mask, a source/pose with hands away from the collar, or a true inpaint/edit model/costume reference.


## 2026-05-12 PuLID + i2i outfit smoke update

Status: MIXED, but useful. PuLID+i2i can make a stronger costume change than the earlier IPAdapter i2i when the target outfit is visually distinct.

New API templates:
- `../api_workflows/10_outfit_pulid_i2i_casual_sweater_api.json`
- `../api_workflows/10_outfit_pulid_i2i_lavender_hoodie_api.json`

Smoke outputs:
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\pulid_i2i_casual_sweater_d0p68_w0p95_seed62018431_00001_.png`: weak/fail. Face stayed close, but cardigan/blouse/tie stayed.
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\pulid_i2i_casual_sweater_d0p78_w1p05_seed62018432_00001_.png`: mixed/fail for sweater. More drift, still cardigan/school-like.
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\pulid_i2i_lavender_hoodie_d0p82_w1p05_seed62018433_00001_.png`: PASS direction candidate. Distinct hoodie achieved, but face/hair/style drift is visible and skirt remains.
- Alpha: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\alpha_pulid_i2i_hoodie_toonout_o0_b0_ref0_00001_.png`
- Alpha QA: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\qa_alpha_pulid_i2i_hoodie_black_gray_white.jpg`

Lesson:
- PuLID is better than full-image IPAdapter i2i for allowing costume change while preserving a broad face family.
- PuLID does not lock exact original identity/style/hair; final VN use likely needs user selection plus face/hair composite or mask-protected refinement.
- Beige sweater is too close to the original cardigan, so the model collapses back into school/cardigan structure. Distinct targets like hoodie are better for proving outfit-change ability.


## 2026-05-12 Two identity-recovery methods after PuLID hoodie

User requested trying both follow-up ideas after the PuLID+i2i hoodie candidate:
1. post-composite the original face/hair onto the PuLID hoodie candidate,
2. run a face/hair-protected masked inpaint/refine route.

Outputs:
- Method 1 composite: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\composite_original_facehair_on_pulid_hoodie_v1.png`
- Method 1 mask: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\mask_composite_original_facehair_v1.png`
- Method 2 rectangular protected inpaint: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\facehair_protected_hoodie_inpaint_d0p82_seed62018441_00001_.png`
- Method 2 custom-mask attempt: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\facehair_hand_protect_custommask_hoodie_d0p78_seed62018442_00001_.png`
- QA sheet: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\qa_two_methods_all_original_hoodie_composite_masked.jpg`

Verdict:
- Method 1 is not production-ready: identity/hair moved closer to original, but faint original hands/cardigan texture leaked into lower face/neck/hoodie because the source has hands very close to the face.
- Method 2 rectangular inpaint is a better direction than method 1 for preserving original head while changing clothing, but it produced a large horizontal seam/gray block under the face.
- Method 2 custom non-rect mask reduced the hard rectangle but failed worse visually, creating transparent/ghosted old-cardigan remnants.

Lesson:
- Do not use broad face/hair composite from this original source because the clasped hands/cuffs are too close to the chin and leak into the result.
- The promising direction is not the current artifact, but a stricter face-only/hair-safe pipeline: clean no-hand identity reference, tight face/hair masks, and a true edit/inpaint workflow or sharper binary mask with seam QA.


## User direction after two-method test

User accepted the PuLID+i2i level as the practical target for this workflow: face retention was good enough, and stronger outfit change matters more than exact original-pixel identity lock. Treat `10_outfit_pulid_i2i_lavender_hoodie_api.json` as the preferred workflow-10 direction candidate. The composite/protected-inpaint experiments remain negative lessons, not the default route.

Preferred candidate:
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\pulid_i2i_lavender_hoodie_d0p82_w1p05_seed62018433_00001_.png`

Remaining gates before any game promotion:
- user visual pick of exact outfit candidate,
- alpha halo cleanup,
- Ren'Py screenshot QA.


## 2026-05-12 PuLID+i2i outfit diversity batch

Using the user-preferred fixed PuLID+i2i direction, 10 outfit variants were generated to test how broadly clothing can change while keeping approximate face/hair identity.

Contact sheet:
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_outfit_variation\contact_sheet_pulid_i2i_outfit_variety_10x_20260512.jpg`

Best direction candidates:
- red track jacket: clear sporty outfit, good face/hair retention.
- green field jacket: clear jacket/outdoor outfit, good face/hair retention.
- blue denim jacket strong: actual denim jacket + white tee; better than the first denim attempt.
- pink ribbon blouse: cute/pink outfit change, usable direction.
- yellow summer dress: clear brighter dress/top direction.
- purple witchy capelet: fantasy/capelet direction, slightly softer face but acceptable.

Mixed / reject:
- black bomber target became cream/white bomber/puffer rather than black, but still shows non-school outfit change.
- black gothic target became cream cardigan + black lace collar; visually okay but target-inaccurate.
- black leather jacket became too revealing/bikini-like and should be rejected for default VN route use.

Conclusion:
- Workflow 10 is complete for the current template pack: PuLID+i2i proves broad outfit variation with acceptable approximate face retention.
- Prompt obedience is stronger for semantically simple, visible garments: track jacket, field jacket, denim jacket, hoodie, blouse, dress.
- For leather/goth/dark styles, add stronger safe negatives (`bikini`, `bra`, `bare midriff`, `cleavage`, `underboob`) before retrying.
- Not yet game-promoted: final selected outfit(s) still need alpha extraction and Ren'Py screenshot QA if/when used in the actual route.
