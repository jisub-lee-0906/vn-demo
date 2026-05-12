# S01 asset candidate QA (workflow-pack derived)

Status: USER_SELECTED_CANDIDATES_PENDING_PROMOTION_QA

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
- Outputs remain candidate QA artifacts only; none were promoted into `demo/game/images/...`.


User selection (2026-05-12):
- Harin anchor: s04
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/harin_anchor_candidates/harin_anchor_candidate_s04_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/harin_anchor_selected_s04.png`
  - Gate: use as anchor direction/source for transparent neutral/suspicious sprite generation, then alpha QA and Ren'Py screenshot QA.
- Summoning hall: s03
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/bg_summoning_hall_candidates/bg_summoning_hall_s03_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/bg_summoning_hall_selected_s03.png`
  - Gate: full-size fake-text inspection plus Ren'Py textbox screenshot QA before semantic promotion.
- Measurement orb: s03
  - Source: `generated/comfyui/s01_asset_candidates_2026-05-12/cg_measurement_orb_candidates/cg_measurement_orb_s03_00001_.png`
  - Selected copy: `generated/comfyui/s01_asset_candidates_2026-05-12/selected/cg_measurement_orb_selected_s03.png`
  - Caveat: contact-sheet QA noted small fake-glyph/text-like marks near the lower pedestal area. User selection is recorded, but this needs full-size contamination inspection and likely crop/cleanup before promotion.

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
- Candidate/contact-sheet review only.
- Do not promote any file into `demo/game/images/...` before user selection and Ren'Py screenshot QA.
- Character candidates are design/anchor candidates, not expression/pose-ready sprites yet.
- Background and CG candidates still need textbox readability and fake-text inspection at full size.

Next step:
1. Generate transparent neutral/suspicious sprite candidates from Harin s04 using the workflow pack alpha/expression route.
2. Run full-size inspection and Ren'Py textbox screenshot QA for summoning hall s03.
3. Run full-size contamination inspection for measurement-orb s03; crop/clean the lower pedestal marks if needed, then run Ren'Py screenshot QA.
4. Promote only after those artifact/screenshot gates pass.
