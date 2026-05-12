# Remaining asset workflows to test/build next

Updated: 2026-05-12

Current state:
- 01~08 are usable/smoke-passed workflow templates at the generation/template level.
- 09 support character generation smoke-passed.
- 10 outfit/costume variation is user-accepted complete for the current template scope via PuLID+i2i outfit-source generation.
- 11 magic shimmer effect smoke-passed, but the 11 key/prop route still failed and remains the main unfinished generation-template item.
- API replayability is not the same as Ren'Py game promotion readiness; promotion still requires Ren'Py screenshot QA.

## Highest priority

1. Ren'Py screen-fit QA workflow
   - Purpose: prove neutral/expression/pose sprites work at actual VN resolution with textbox visible.
   - Test: neutral, smile, surprised, sad, angry, hand-to-chest, one-hand-on-hip, arms-crossed.
   - Check: crop, zoom, yalign, face position, body scale, dialogue-box overlap, Korean UI readability.
   - Output to preserve: screenshot set, transform recommendations, pass/fail notes.

2. Sprite-set consistency QA workflow
   - Purpose: evaluate the current sprite family as a set, not as separate good images.
   - Check: same face/hair/uniform, similar scale, lineart sharpness, expression readability, pose readability, alpha edge consistency.
   - Output to preserve: labeled contact sheet plus verdict table.

3. Character-on-background integration QA workflow
   - Purpose: test transparent sprites over real backgrounds, not only dark/checker QA sheets.
   - Check: halo, edge color, scale, color harmony, staging, lower-third readability.
   - Output to preserve: background-specific composite screenshots and fixes.

4. Semantic asset promotion workflow
   - Purpose: define when a candidate is copied into stable Ren'Py paths.
   - Include: naming convention, manifest update, rejected-candidate notes, rollback rules, final screenshot proof.
   - Avoid: promoting questionable pose/alpha candidates just because the API runs.

## Core asset-production workflows still missing

5. Background production workflow
   - Generate classroom/room/street/cafe/location backgrounds.
   - Need no-text/pseudo-glyph screening and textbox readability QA.
   - Better version: Blender blockout/depth/canny guided ComfyUI workflow for stable layout.

6. Background weather variation workflow
   - Same-location rainy/cloudy/weather variants use 07 with Canny/lineart layout lock.
   - Day/night variants are fixed to workflow 06 as separately generated base backgrounds, then QAed as a set.

7. UI/dialogue visual workflow
   - Test textbox/namebox/choice menu over generated background + sprite.
   - Check choice box does not cover heroine face/body or story-critical props.

8. Event CG workflow
   - Generate story-beat CGs: props, actions, hook moments, comedy/action beats.
   - Require no fake text/UI/person contamination.
   - Promote only after full-size inspection and actual route screenshot QA.

9. Support character / effect workflow
   - 09 support character and 11 magic shimmer effect have smoke-passed.
   - Remaining unfinished item here is 11 prop/key generation: current key route failed due to unwanted plate/box/background contamination.
   - Lighter than heroine pipeline, but still needs alpha, scale, and Ren'Py context QA before game promotion.

10. Outfit / costume variation workflow — DONE for current template scope
   - Accepted direction: PuLID+i2i for diverse outfit-source generation with approximate face retention.
   - Best families: hoodie, track jacket, field jacket, denim jacket, blouse, simple dress/capelet.
   - Game use still requires selecting exact outfit(s), alpha extraction, and Ren'Py screenshot QA.

## Optional / later workflows

11. LivePortrait subtle motion workflow
   - Blink, breathing, talking loop from approved sprite.
   - Not ready until LivePortrait nodes/models and Ren'Py WebM/side-mask playback are verified.

12. AnimateDiff / ambient loop workflow
   - Rain, dust, curtain, light shafts, menu background loops.
   - Must prove structure does not swim and loop playback works in Ren'Py.

13. Final packaging workflow
   - Bundle API JSON, required input image list, usage docs, QA sheets, manifests, and Ren'Py promotion docs.
   - Goal: a future zero-memory session can reproduce and promote the asset set without reconstructing decisions from chat.

## Recommended next execution order

1. Build Ren'Py screen-fit QA template first.
2. Run sprite-set consistency contact sheet over current 01~05 outputs.
3. Generate or choose one test background.
4. Run character-on-background integration QA.
5. Only then decide which sprite/expression/pose assets are worth semantic promotion.
6. After that, start background production and event CG workflows.

## Added template stubs (2026-05-12)

The requested next asset-production directions now have starter template folders and `/prompt` API JSON:

- `06_background_generation_no_text`: location background txt2img with no-text/no-UI screening.
- `07_background_variation_img2img_layout_lock`: same-location weather img2img variation with layout-lock QA; smoke PASS for rain, not day/night conversion.
- `08_event_cg_no_text_story_beat`: smoke-passed sealed-envelope hallway hook CG with fake-text/UI/person contamination gates; RenPy screenshot QA remains.

Next execution step: use 06 for separate day/night base candidates as needed; use 07 only for weather variations such as rain; 08 smoke is done for one sealed-envelope hook beat; next verify selected backgrounds/CG in Ren'Py screenshots before semantic promotion.
