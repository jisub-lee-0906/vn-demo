# VN auburn workflow current status and missing workflows

Updated: 2026-05-12

Backup root:
- Windows: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`
- WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`

## Current completed / usable workflows

Template intent:
- This folder is a reusable Ren'Py asset-production template pack, not an image archive.
- PNGs are examples/QA references.
- The main deliverables are usage docs, ComfyUI `/prompt` API workflow JSON, manifests, and QA/promotion gates.
- See `TEMPLATE_INTENT.md`.

### 01_character_anchor_and_prompt

Status: PASS as character-anchor/source workflow.

Purpose:
- Create a single auburn VN dialogue character anchor on neutral gray background.

Historical selected output filename (removed from backup; recreate via API):
- `source_auburn_719238043_00001_.png`

Still missing before game final:
- Ren'Py screen-fit and semantic asset promotion.

### 02_toonout_transparency_alpha

Status: PASS as auburn/high-contrast hair alpha workflow.

Purpose:
- Convert the selected character source into a transparent PNG.

Best setting:
- `BiRefNet_toonout`
- `mask_offset=0`
- `mask_blur=0`
- `refine_foreground=false`

Historical selected output filename (removed from backup; recreate via API):
- `alpha_toonout_offp0_b0_ref0_00001_.png`

Still missing before game final:
- Background-specific halo check inside Ren'Py screenshots.

### 03_expression_variation_ipadapter_img2img

Status: PASS as expression workflow candidate.

Purpose:
- Generate smile/surprised/sad/angry variants while keeping identity mostly stable.

Best pattern:
- Conservative smile: `denoise=0.42`, `IPAdapter weight=0.60`
- Stronger expression: `denoise=0.54-0.56`, `IPAdapter weight=0.45-0.48`
- Alpha: `BiRefNet_toonout offset=0 blur=0 refine=false`

Still missing before game final:
- Expression readability at actual Ren'Py scale.
- Expression-set consistency QA against neutral and pose variants.

### 04_pose_source_generation_textonly

Status: PASS as pose-donor/source workflow, not final same-character pose workflow by itself.

Purpose:
- Generate readable large-arm gesture donors.

Good donors:
- hand-to-chest: PASS pose source
- one-hand-on-hip: PASS pose source
- arms-crossed: PASS pose source

Weak donor:
- pointing: weak / not production source yet

Important lesson:
- Direct IPAdapter img2img was too conservative for large pose changes and preserved the original clasped/prayer hands.
- Use these text-only donors as geometry sources for `05_pose_image_reference_regeneration_ipadapter`.

### 05_pose_image_reference_regeneration_ipadapter

Status: latest update; PASS as production-direction pose workflow candidate.

Purpose:
- Use text-only pose donor as img2img latent source, then use the approved auburn reference as IPAdapter identity/style reference.

This replaces the removed old `05_not_completed_pose_identity_refinement` post-alpha composite direction.

Best base setting:
- `denoise=0.42`
- `IPAdapter weight=0.60`

Alternative:
- `denoise=0.50`
- `IPAdapter weight=0.55`

Best arms-crossed transparent candidate filename (removed from backup; recreate via API):
- `alpha_arms_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`

Best one-hand-on-hip transparent candidate filename (removed from backup; recreate via API):
- `alpha_hip_refregen_d0p42_w0p6_toonout_o0_b0_ref0_00001_.png`

Verdict:
- Better than post-alpha composite.
- No prayer-hands ghosting or pasted seam.
- Not final promotion-ready until Ren'Py screen-fit and hand/edge QA.


### 06_background_generation_no_text

Status: SMOKE PASS as minimal no-text classroom background baseline.

Purpose:
- Generate reusable 16:9 VN location backgrounds without fake UI/text/people contamination.
- Day/night backgrounds are fixed to this route: generate separate base backgrounds directly rather than converting day to night through 07.

Default:
- `novaAnimeXL_ilV180.safetensors`
- prompt: `empty anime classroom, no people, clean lower third`
- negative: `text, ui, people`

Still missing before game final:
- Ren'Py textbox/sprite screenshot QA and semantic background promotion.

### 07_background_variation_img2img_layout_lock

Status: SMOKE PASS for rainy/weather variation; closed as not responsible for day/night conversion.

Purpose:
- Use a workflow-06 base background as img2img input and create layout-locked weather variants, especially rain.

Canonical result:
- Rain variation with Canny/lineart ControlNet + SDXL Union at denoise 0.72, strength 0.65, end 0.75.

Fixed non-goal:
- Day/night swaps are handled by separate workflow-06 base generations. Night conversion through 07 remains a known gap only if exact pixel/layout continuity is required later.

Still missing before game final:
- Ren'Py textbox/sprite screenshot QA for the selected rain/weather background.



### 08_event_cg_no_text_story_beat

Status: SMOKE PASS as a no-text event-CG workflow candidate.

Purpose:
- Generate story-beat prop/action CGs with no fake text/UI/person contamination.

Selected smoke candidate:
- sealed-envelope / hallway hook CG
- seed `812347402`, candidate `uppermid_s2`

Verdict:
- No fake text/UI/people/hands/blood on selected candidate.
- Works as a mysterious sealed-envelope hook CG.
- Exact under-door-gap action remains a caveat; use later inpaint/control refinement if mandatory.

Still missing before game final:
- Ren'Py route screenshot QA with dialogue box and semantic CG promotion.

## API template coverage update

Status: 01~05 current character/sprite workflow chain now has reusable ComfyUI `/prompt` API templates.

Coverage:
- 01 character anchor/source generation: 3 API templates.
- 02 toonout transparency alpha: 5 API templates.
- 03 expression source/alpha: 12 API templates.
- 04 text-only pose donor/source + alpha: 12 API templates.
- 05 pose image-reference regeneration + alpha example: 5 API templates.

Reference files:
- `api_workflows/README.md`
- `api_workflows/API_TEMPLATE_INDEX.json`

Important caveat:
- API replayability is not the same as game promotion readiness.
- Remaining QA gates still include Ren'Py screen-fit, background-specific halo/readability checks, and sprite-set consistency.

## Removed / superseded workflow

### 05_not_completed_pose_identity_refinement

Status: removed.

Reason:
- The workflow direction changed.
- Broad face/hair or hair-only post-alpha composite copied unwanted hand/sleeve/cardigan fragments from the neutral reference into new poses.
- The replacement is `05_pose_image_reference_regeneration_ipadapter`.

## Missing / next workflows

### A. Ren'Py screen-fit QA workflow

Priority: highest.

Need:
- Place neutral, expression, arms-crossed, and one-hand-on-hip transparent PNGs over real VN backgrounds with dialogue box visible.
- Check scale, anchor, crop, textbox collision, halo, gesture readability, and expression readability.

Completion condition:
- Screenshots prove the assets work inside the actual game frame.

### B. Semantic asset promotion workflow

Priority: high, after screen-fit.

Need:
- Copy selected candidates from ComfyUI backup/output into stable game paths.
- Create/clean Ren'Py image declarations.
- Remove experimental paths from scripts.
- Update asset manifest and QA docs.

Completion condition:
- Game uses semantic asset paths, not ComfyUI experiment paths.

### C. Sprite set consistency QA workflow

Priority: high.

Need:
- Compare neutral + expressions + pose variants as one set.
- Verify head size, eye height, body scale, hair silhouette, cardigan/skirt color, and alpha edge consistency.

Completion condition:
- Switching expressions/poses in Ren'Py does not visibly jump or drift.

### D. Background production workflow

Priority: high; currently missing.

Need:
- Location list: classroom, hallway, protagonist room, school gate, cafe, rooftop, etc.
- Generate or derive VN backgrounds at project resolution.
- Prefer layout/Blender/blockout/control route for reusable locations.
- Avoid text/UI/people contamination.
- Check dialogue-box readability and character placement space.

Completion condition:
- At least one production-candidate background is integrated with the character sprite in Ren'Py screenshot QA.

### E. Character-on-background integration QA workflow

Priority: high after first background.

Need:
- Test sprite alpha and color contrast over the actual background, not only dark/checker sheets.
- Check whether hair/edge/lineart remain readable and whether character lighting clashes with background.

Completion condition:
- Character + background + dialogue UI work as a coherent VN screen.

### F. UI/dialogue box visual workflow

Priority: medium-high.

Need:
- Dialogue box, nameplate, choice menu, title/save/load/settings style pass.
- Ensure UI supports the new art direction rather than looking like default Ren'Py placeholder.

Completion condition:
- Core gameplay screen no longer feels like placeholder UI.

### G. Event CG workflow

Priority: medium.

Current status:
- 08 smoke PASS exists for a sealed-envelope hallway hook CG, but it is not semantically promoted into a Ren'Py route yet.

Still needed:
- Promote selected CG to a semantic game path only after route context is chosen.
- Run Ren'Py screenshot QA with dialogue box.
- If exact under-door-gap action is mandatory, refine with inpaint/control first.

Completion condition:
- One story beat uses a semantic CG path and screenshot proof.

### H. Better pointing / additional gesture workflow

Priority: medium.

Need:
- Generate better pointing/scolding donor before running the 05 IPAdapter ref-generation route.
- Add relaxed arms down / arms-behind-back / shy hand-near-face only after current two pose variants pass Ren'Py QA.

Completion condition:
- New gestures pass pose-source QA and then identity-refgeneration QA.

### I. Reproducible workflow JSON/template packaging

Priority: medium.

Current status:
- Partially done.
- Latest 05 pose ref-generation API templates were added under `api_workflows/`.
- Included: best/alternative arms-crossed, best/alternative one-hand-on-hip, and a reusable BiRefNet_toonout alpha example.

Still needed if full automation is required:
- Add complete replay API templates for 01 character anchor, 02 alpha source, 03 expression generation, and 04 text-only pose donor generation.
- Parameterize source image, pose donor, prompt, denoise, IPAdapter weight, seed, and output prefix.

Completion condition:
- Future variants can be queued from templates without reconstructing node graphs manually.

## Recommended next sequence

1. Run Ren'Py screen-fit QA for current best neutral/expression/pose transparent candidates.
2. Promote only assets that pass to semantic game paths.
3. Start background production with one core location, preferably the most-used first scene location.
4. Run character-on-background integration QA.
5. Only then expand pose/expression/background sets.


## Remaining additional asset workflows to test/build

These are the next workflows that are not yet fully proven or packaged in this backup:

1. Background production workflow
   - Generate reusable VN backgrounds: classroom/room/street/cafe.
   - Day/night sets are produced as separate workflow-06 base backgrounds, not 07 conversions.
   - Need no-text/pseudo-glyph QA and lower-third textbox readability QA.
   - Stronger version should use Blender blockout/depth/canny guides for stable layouts.

2. Ren'Py screen-fit QA workflow
   - Place neutral/expression/pose sprites at actual VN resolution with textbox visible.
   - Verify crop, zoom, yalign, face position, dialogue-box overlap, and Korean UI readability.

3. Semantic asset promotion workflow
   - Define how a candidate moves from ComfyUI output to stable Ren'Py paths.
   - Include naming, manifest update, rejected-candidate notes, and rollback rules.

4. Sprite-set consistency QA workflow
   - Compare neutral, smile, surprised, sad, angry, hand-to-chest, one-hand-on-hip, arms-crossed.
   - Check face/hair/uniform continuity, scale, lineart sharpness, expression readability, and alpha edges.

5. Character-on-background integration QA workflow
   - Test transparent PNGs over real backgrounds, not only dark/checker sheets.
   - Check halo visibility, color harmony, scale, text readability, and staging transforms.

6. UI/dialogue visual workflow
   - Verify textbox/namebox/choice UI with the generated sprite and background.
   - Tune choice width/alignment so it does not cover the heroine face/body or story-critical props.

7. Event CG workflow
   - Generate story-beat CGs with no fake text/UI/person contamination.
   - Promote only after full-size inspection and actual route screenshot QA.

8. Support character / effect workflow
   - 09 support character smoke passed; 11 magic shimmer effect smoke passed.
   - Remaining gap in this bucket is the 11 prop/key route, which failed due to object/background contamination.
   - Keep lighter than main heroine pipeline but still require alpha/screen-fit QA before game use.

9. Background weather variation workflow
   - Rain/cloudy/weather variants of the same base location use 07.
   - Day/night variants use separate workflow-06 base generations.
   - Need layout lock and text readability checks for 07 weather outputs.

10. LivePortrait / subtle motion workflow
   - Blink/breath/talk loops from approved sprites.
   - Not ready until live nodes/models and Ren'Py WebM/side-mask playback are verified.

12. AnimateDiff / ambient loop workflow
   - Rain, dust, light shafts, curtains, menu background loops.
   - Must prove structure does not swim and Ren'Py playback loops cleanly.

13. Final packaging workflow
   - Bundle API templates, input image prerequisites, QA sheets, manifests, and Ren'Py promotion docs so a zero-memory future session can reproduce the asset set.


## 2026-05-12 generation expansion scaffold update

Added generation-category scaffolds after 08:

- 09 support character generation: teacher anchor + alpha API scaffold; smoke PASS after later retry.
- 10 outfit/costume variation: original casual IPAdapter scaffold failed, then user-accepted complete via PuLID+i2i diversity batch.
- 11 prop/effect overlay: original over-constrained key route failed, then minimal key prop retry smoke PASS; magic shimmer effect smoke PASS.
- 12 SFX generation: procedural/library/AI SFX design and helper script; tiny prototype artifacts exist but are not final mastered audio.
- 13 BGM generation: instrumental loopable VN BGM prompt/mood design, backend not selected yet.
- 14 audio packaging/looping: `.ogg` conversion/normalization/manifest design.

Scope note: these are asset-generation workflow expansions, not Ren'Py promotion/QA completion. 09-11 now have smoke-passed/current accepted generation directions; 12-14 remain audio/design/packaging scaffolds pending backend/final audio decisions.


## 2026-05-12 smoke results for 09-11 expansion

09 support character generation:
- Revised teacher anchor `source_teacher_neutral_seed91420932_00001_.png` smoke-passed as an adult teacher/NPC source candidate.
- Alpha `alpha_teacher_toonout_o0_b0_ref0_00002_.png` smoke-passed as a toonout alpha candidate with dark/gray/light QA sheet.
- Still not Ren'Py promotion-ready; this is generation-workflow smoke only.

10 outfit/costume variation:
- USER-ACCEPTED COMPLETE for the current workflow-template scope.
- Plain IPAdapter i2i failed, masked inpaint was partial, and PuLID+i2i became the accepted practical route.
- The 10-variant PuLID+i2i batch proved usable outfit families: red track jacket, green field jacket, denim jacket, pink blouse, yellow dress, purple capelet; black leather is rejected for the default safe VN route.
- Final game use still requires selecting exact outfit(s), alpha extraction, and Ren'Py screenshot QA.

11 effect/prop overlay:
- Magic shimmer black-background additive overlay smoke-passed as an effect candidate.
- Key prop txt2img route failed because it generated unwanted plate/box/background objects. Do not canonicalize this prop route yet.


### 10_outfit_costume_variation

Status: USER-ACCEPTED COMPLETE as PuLID+i2i outfit-variation workflow direction; not final game-promotion-ready.

Earlier plain full-image IPAdapter img2img route failed because it over-drifted hair/color while preserving too much school/cardigan structure. The new masked torso inpaint route is materially better: it preserves face/hair/crop by compositing only the masked clothing region back over the original source.

Preferred smoke candidate:
- `masked_torso_tight_pullover_d0p76_seed62018422_00001_.png`
- alpha candidate: `alpha_masked_tight_pullover_toonout_o0_b0_ref0_00001_.png`

Caveats before promotion:
- blue collar/tie remnants remain near clasped hands,
- school skirt remains, so this is top-outfit variation rather than full costume change,
- alpha has visible gray hair-edge halo on black QA,
- Ren'Py screen-fit/screenshot QA has not been run.

Next improvement:
- better clothing mask or a source pose with hands away from collar, then masked inpaint again; plain i2i fallback is not needed yet.


#### PuLID+i2i outfit addendum

A PuLID SDXL + full-image i2i route was also smoke-tested for workflow 10.

Results:
- Beige/ivory sweater targets at `denoise=0.68/0.78` preserved too much cardigan/blouse/tie structure, so they are weak/fail for true outfit change.
- A visually distinct hoodie target at `denoise=0.82`, `PuLID weight=1.05` achieved a clear non-school hoodie outfit:
  - source: `pulid_i2i_lavender_hoodie_d0p82_w1p05_seed62018433_00001_.png`
  - alpha: `alpha_pulid_i2i_hoodie_toonout_o0_b0_ref0_00001_.png`

Verdict:
- PASS as outfit-change direction candidate, stronger than the sweater attempts.
- Caveats: exact original identity/style/hair are not fully locked, skirt remains, alpha halo remains on black, and Ren'Py QA is not done.
- Use PuLID+i2i for coarse costume-source generation; use mask/composite/refinement if exact final VN identity must be preserved.


#### Two-method identity recovery after PuLID hoodie

Tried both requested follow-ups:
- Original face/hair post-composite onto PuLID hoodie: closer identity but not usable; old hands/cardigan texture ghosts into the lower face/neck/hoodie.
- Face/hair-protected masked inpaint: original head preserved and hoodie can be generated, but current rectangular mask creates a visible horizontal seam/gray block; custom soft clothing mask produced transparent/ghosted cardigan remnants and failed.

Current decision: no final/promotion-ready output. Best future direction is a stricter face-only/hair-safe route with a clean no-hand identity reference or a true edit/inpaint workflow, not broad copying from the clasped-hands source.


#### User-selected outfit direction

User judged the PuLID+i2i level as appropriate: face preservation is acceptable enough, and exact original identity lock is not necessary for this outfit-variation workflow. Preferred direction is now PuLID+i2i using the distinct hoodie-style target; keep composite/protected-inpaint attempts as negative/secondary lessons only.


#### 2026-05-12 user acceptance update for workflow 10 and minimal key prop retry

Workflow 10 is now treated as complete for the current reusable-template scope. The accepted canonical direction is PuLID+i2i for outfit-source generation with approximate face retention, backed by the 10-variant diversity batch. Remaining workflow-11 work is specifically the failed key/prop route; the magic shimmer effect half of 11 already smoke-passed.
