# S01 asset candidate QA (workflow-pack derived)

Status: S01_SELECTED_ASSETS_PROMOTED_PROTOTYPE_PENDING_IN_GAME_QA

This replaces the earlier ad-hoc S01 candidate batch. The previous generated assets were discarded, and this run was regenerated from the canonical Windows ComfyUI workflow pack.

Workflow pack source:
- Windows: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`
- WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`

Run manifest:
- `generated/comfyui/s01_asset_candidates_2026-05-12/RUN_MANIFEST.json`

Contact sheets:
- `harin_anchor_candidates`: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/harin_anchor_candidates_sheet.jpg`
- `bg_summoning_hall_candidates`: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/bg_summoning_hall_candidates_sheet.jpg`
- `cg_measurement_orb_candidates`: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/cg_measurement_orb_candidates_sheet.jpg`

Derived templates:
- `harin_anchor_candidates` derived from `01_character_anchor_and_prompt` / `01_character_anchor_seed719238043_api.json`
- `bg_summoning_hall_candidates` derived from `06_background_generation_no_text` / `06_background_generation_no_text_api.json`
- `cg_measurement_orb_candidates` derived from `08_event_cg_no_text_story_beat` / `08_event_cg_no_text_story_beat_api.json`

Generation result:
- 3 jobs, 12 candidate images, 12 derived API workflow JSON files.
- Contact sheets were generated locally from downloaded ComfyUI outputs.
- Selected S01 assets are now promoted as prototype game assets under `demo/game/images/...`; final quality still requires in-game screenshot/manual QA.


User selection (2026-05-12):
- Harin anchor: s04
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/harin_anchor_candidates/harin_anchor_candidate_s04_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/harin_anchor_selected_s04.png`
  - Gate: use as anchor direction/source for transparent neutral/suspicious sprite generation, then alpha QA and Ren'Py screenshot QA.
- Summoning hall: s03
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/bg_summoning_hall_candidates/bg_summoning_hall_s03_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/bg_summoning_hall_selected_s03.png`
  - Gate: full-size fake-text inspection plus Ren'Py textbox screenshot QA before semantic promotion.
- Measurement orb: s01
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/cg_measurement_orb_candidates/cg_measurement_orb_s01_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/cg_measurement_orb_selected_s01.png`
  - Correction: replaces the prior s03 selection after user reviewed the contact sheet.
  - Gate: full-size contamination/story-beat inspection, then Ren'Py screenshot QA before semantic promotion.



Prototype game promotion (2026-05-12):
- Background promoted from summoning hall s03:
  - `demo/game/images/backgrounds/bg_summoning_hall.png`
  - scaled to 1920x1080 and wired as `image bg summoning_hall`.
- Measurement orb CG promoted from s01:
  - `demo/game/images/cg/cg_measurement_orb.png`
  - scaled to 1920x1080 and wired as `image cg measurement_orb` during the S01 measurement beat.
- Harin anchor s04 promoted through the workflow-pack transparency route:
  - `demo/game/images/characters/harin/harin_neutral.png`
  - `demo/game/images/characters/harin/harin_suspicious.png`
  - wired as `image harin neutral` and `image harin suspicious`.
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/harin_anchor_selected_s04.png`.
  - Transparency node: Windows ComfyUI `BiRefNetRMBG`, model `BiRefNet_toonout`, `mask_offset=0`, `mask_blur=0`, `refine_foreground=false`, `background=Alpha`.
  - Output: `C:\Users\Desktop\Documents\ComfyUI\output\vn_demo_s01_harin_alpha\harin_s04_toonout_o0_b0_ref0_00001_.png` (`/mnt/c/Users/Desktop/Documents/ComfyUI/output/vn_demo_s01_harin_alpha/harin_s04_toonout_o0_b0_ref0_00001_.png`).
  - Alpha proof after promotion: PNG color type RGBA, alpha min/max `(0, 255)`, transparent pixels `1,134,471`, opaque pixels `617,267`, semi-transparent matte pixels `17,734`.
  - Expression caveat: `harin_suspicious.png` currently reuses the transparent neutral anchor as a route/staging prototype; a distinct suspicious expression still requires expression-generation QA.
- Approximate composition previews:
  - `generated/renpy_s01_asset_promotion_qa_2026-05-12/s01_hall_harin_textbox_preview.png`
  - `generated/renpy_s01_asset_promotion_qa_2026-05-12/s01_measurement_orb_textbox_preview.png`

Contact-sheet review notes:

## `harin_anchor_candidates`

Files:
- `harin_anchor_candidate_s01_00001_.png`
- `harin_anchor_candidate_s02_00001_.png`
- `harin_anchor_candidate_s03_00001_.png`
- `harin_anchor_candidate_s04_00001_.png`

Observed:
- No obvious cropped head/hair problem in the contact sheet.
- No duplicate/inset/reference-sheet contamination visible.
- No UI/text/watermark contamination visible in the character art itself.
- Clipboard/hand details are still candidate-grade: s01 has a pen/clipboard pose that may need hand cleanup; s02 shows fake document lines on the clipboard and should not be used directly if fake text is disallowed; s03 and s04 have simpler clipboard silhouettes.
- s04 is the cleanest restrained uniform direction but has a less formal jacket silhouette; s03 is a usable stern/audit-officer direction with simpler fake-text risk; s01 has strong student-council energy but a busier pose.

Candidate note:
- Best anchor-direction candidates for the next iteration: s03 or s04.
- Not final sprite quality. A chosen anchor still needs transparent sprite generation, expression consistency, alpha QA, and Ren'Py screenshot QA.

## `bg_summoning_hall_candidates`

Files:
- `bg_summoning_hall_s01_00001_.png`
- `bg_summoning_hall_s02_00001_.png`
- `bg_summoning_hall_s03_00001_.png`
- `bg_summoning_hall_s04_00001_.png`

Observed:
- s01, s03, and s04 have no visible people in the contact sheet.
- s02 contains a dark human-like statue/figure silhouette near the center; reject for no-people policy unless the concept is intentionally revised.
- No obvious fake text/UI is visible at contact-sheet scale.
- Lower-third textbox readability: s01 and s03 have bright/simple lower areas; s04 is darker but visually strong and may still work with textbox overlay; s02 is rejected due to the figure.

Candidate note:
- Best summoning-hall direction candidates: s03 for warm ceremonial hall readability, s04 for stronger magical pedestal mood.
- Full-size inspection and Ren'Py textbox screenshot QA are still required before semantic promotion.

## `cg_measurement_orb_candidates`

Files:
- `cg_measurement_orb_s01_00001_.png`
- `cg_measurement_orb_s02_00001_.png`
- `cg_measurement_orb_s03_00001_.png`
- `cg_measurement_orb_s04_00001_.png`

Observed:
- Measurement orb/pedestal concept reads clearly in all four candidates.
- No people/hands/UI visible in the contact sheet.
- s03 has small fake-glyph/text-like marks near the lower pedestal area; reject unless cropped/cleaned.
- s01/s02/s04 avoid obvious text contamination at contact-sheet scale, but all are more blue-glowing than the intended 'going dark / thin golden crack' beat.
- s02 has the cleanest centered pedestal/table staging; s04 has a clean orb silhouette; s01 has a strong magical-circle read.

Candidate note:
- Best candidates for temporary direction: s02 or s04.
- Story-beat accuracy still needs refinement if the image itself must show the darkened orb and thin golden crack clearly.

QA gate:
- Prototype game asset promotion completed for S01 selected assets.
- Current Harin sprite is a temporary card-style prototype, not a final transparent sprite.
- Background/CG are wired for in-game QA but still need real Ren'Py screenshot/manual review before final-quality claims.

Next step:
1. Run actual Ren'Py play/screenshot QA for S01 with the promoted prototype assets.
2. Check textbox overlap, Harin card-style limitation, background readability, and measurement-orb beat timing.
3. Replace Harin card-style prototype with a proper transparent sprite/alpha workflow before calling sprite quality final.
