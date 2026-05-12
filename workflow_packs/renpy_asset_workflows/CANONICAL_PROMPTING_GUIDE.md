# Canonical prompting guide for the VN auburn ComfyUI workflow pack

Updated: 2026-05-12

This document is the practical production guide for using the kept canonical workflow templates. The pack should preserve the best executable workflow plus the prompting method, not every failed sweep.

Root path:
- WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`
- Windows: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`

ComfyUI API templates:
- `api_workflows/`

## Global prompting rules for this pack

Use short, controlled prompts. Do not grow long negative prompts after every artifact.

Core quality prefix:
```text
masterpiece, best quality, very aesthetic, newest,
```

Core sprite framing language:
```text
1girl, solo, anime style, cowboy shot, upper body character portrait,
waist-up to upper-thigh visible, full head visible, complete hair visible,
large centered character, simple neutral gray background
```

Avoid these early unless deliberately testing them:
```text
visual novel sprite, reference sheet, character sheet, margin above head,
shoes out of frame, head to knees, three-quarter body, full body
```

Why:
- `visual novel sprite` can activate UI/sprite-sheet priors.
- `reference sheet`/`character sheet` can create multiple views or inset figures.
- `margin above head` can make the model fill top space with bows/symbols/flames.
- positive `shoes` wording can activate shoes/feet objects even when asking for them out of frame.
- `full body` often makes the character too small for Ren'Py dialogue use.

Core negative prompt blocks:
```text
text, watermark, logo, multiple girls, duplicate character,
cropped head, cut off hair, out of frame,
extra arms, extra hands, bad hands, fused fingers, missing fingers,
low quality, worst quality, full body, tiny full body, chibi,
character sheet, reference sheet, sprite sheet, inset, floating head,
small extra portrait, profile card, ui, interface, dialogue box
```

Keep changes one-variable-at-a-time:
1. prompt wording,
2. seed,
3. denoise,
4. IPAdapter weight,
5. alpha model/settings.

Do not change all of them at once.

## 01. Character anchor generation

Canonical template:
```text
api_workflows/01_character_anchor_seed719238043_api.json
```

Purpose:
- Create the neutral auburn heroine/source image that later workflows reference.

Canonical settings:
- checkpoint: `novaAnimeXL_ilV125.safetensors`
- canvas: tall dialogue-sprite canvas from the template
- sampler: `euler_ancestral`
- scheduler: `normal`
- steps: `28`
- CFG: `6.0`
- seed: `719238043`
- denoise: `1.0`
- CLIP skip: `CLIPSetLastLayer(-2)`

Prompting method:
1. Start with the quality prefix.
2. Define one character only.
3. Use natural VN dialogue framing: `cowboy shot`, `upper body character portrait`, `waist-up to upper-thigh visible`, `full head visible`, `complete hair visible`.
4. Keep background simple neutral gray for later alpha extraction.
5. Do not mention reference/sprite sheets.
6. Do not force feet/shoes terms.

When adapting to a new character, edit only:
- hair color/style
- eye color
- outfit identity
- small signature accessory if needed
- seed only after prompt is stable

PASS:
- full head and hair visible
- upper body/thigh-up scale suitable for dialogue sprite
- one character only
- no top-head symbols/accessory contamination
- clean neutral background

FAIL:
- cropped head/hair
- tiny full body
- multiple views/insets
- head-object symbols
- outfit/color drift that would poison later expression/pose refs

## 02. Transparent alpha / toonout

Canonical template:
```text
api_workflows/02_alpha_toonout_o0_b0_ref0_api.json
```

Purpose:
- Convert the selected neutral source into transparent Ren'Py PNG.

Required input in ComfyUI input folder:
```text
hermes_other_auburn_seed719238043.png
```

Canonical settings:
- model/node: `BiRefNet_toonout`
- `mask_offset=0`
- `mask_blur=0`
- `refine_foreground=false`

Prompting:
- No creative prompt should be added here. This is a matting step, not regeneration.

Production method:
1. Use the selected source image unchanged.
2. Run the toonout alpha template.
3. QA on dark, checker, and actual Ren'Py background.
4. For auburn/high-contrast hair, do not assume `offset=+1` from pale-hair workflows. Canonical here is `offset=0`.

PASS:
- hair tips retained
- no large gray/white rim on dark background
- no full-canvas alpha remnants
- body edges not visibly chewed

FAIL:
- transparent holes in foreground
- thick source-color halo
- hair detail loss
- alpha looks okay on white but bad on dark/Ren'Py background

## 03. Expression generation

Canonical source templates:
```text
api_workflows/03_expression_source_smile_keep_d0p42_w0p6_api.json
api_workflows/03_expression_source_surprised_move_d0p54_w0p48_api.json
api_workflows/03_expression_source_sad_strong_move_d0p56_w0p45_api.json
api_workflows/03_expression_source_angry_move_d0p54_w0p48_api.json
```

Canonical alpha templates:
```text
api_workflows/03_expression_alpha_smile_toonout_o0_b0_ref0_api.json
api_workflows/03_expression_alpha_surprised_toonout_o0_b0_ref0_api.json
api_workflows/03_expression_alpha_sad_toonout_o0_b0_ref0_api.json
api_workflows/03_expression_alpha_angry_toonout_o0_b0_ref0_api.json
```

Required neutral input:
```text
hermes_expr_auburn_neutral.png
```

Expression source settings:
- smile: denoise `0.42`, IPAdapter weight `0.60`, CFG `6.0`, steps `28`
- surprised: denoise `0.54`, IPAdapter weight `0.48`, CFG `6.0`, steps `28`
- sad: denoise `0.56`, IPAdapter weight about `0.46`, CFG `6.2`, steps `28`
- angry: denoise `0.54`, IPAdapter weight about `0.46`, CFG `6.2`, steps `28`
- IPAdapter weight type: `style and composition`
- IPAdapter range: start `0.0`, end about `0.82`

Prompting method:
1. Keep the identity/framing block almost unchanged from neutral.
2. Add expression phrase near the character description, not buried at the end.
3. For subtle smile, use lower denoise and stronger identity weight.
4. For surprised/sad/angry, use higher denoise and slightly lower IPAdapter weight so the face can move.
5. Add expression-specific negatives against neutral/subtle expression only when needed.

Useful expression phrases:
```text
soft warm smile, gentle smile, clearly smiling, friendly expression
surprised expression, wide eyes, open mouth, startled but cute
sad expression, downturned mouth, worried eyes, about to cry, emotional face
angry expression, serious angry face, furrowed brows, annoyed expression
```

Avoid:
```text
comic symbols, manga anger mark, tears everywhere, screaming, distorted face
```
unless the script explicitly needs comedy exaggeration.

PASS:
- emotion readable at Ren'Py dialogue scale
- same hair/face/outfit family
- no duplicated character/inset portrait
- crop/scale consistent with neutral

FAIL:
- expression too subtle to matter
- identity/outfit drift worse than expression gain
- hands/arms unexpectedly change unless desired
- face becomes melted or over-comic

## 04. Pose donor generation

Canonical pose donor templates:
```text
api_workflows/04_pose_textonly_source_hand_chest_txt_s1_api.json
api_workflows/04_pose_textonly_source_hip_txt_s0_api.json
api_workflows/04_pose_textonly_source_cross_txt_s0_api.json
```

Canonical donor alpha templates:
```text
api_workflows/04_pose_alpha_hand_chest_toonout_o0_b0_ref0_api.json
api_workflows/04_pose_alpha_one_hand_hip_toonout_o0_b0_ref0_api.json
api_workflows/04_pose_alpha_arms_crossed_toonout_o0_b0_ref0_api.json
```

Purpose:
- Generate readable body/arm pose geometry donors.
- These are not final same-character pose sprites by themselves.
- They feed workflow 05.

Canonical settings:
- checkpoint: `novaAnimeXL_ilV125.safetensors`
- sampler: `euler_ancestral`
- scheduler: `normal`
- steps: `30`
- CFG: `6.2`
- denoise: `1.0`

Pose prompting method:
1. Use text-only donor generation because direct IPAdapter img2img over-preserved the original clasped/prayer hands.
2. Keep character description close enough to the target style, but judge this step mainly on pose geometry/readability.
3. Put pose phrase early and clearly.
4. Keep `cowboy shot`, `upper body`, `full head visible`, and `large centered character` to avoid tiny full-body donors.
5. Use strong hand/extra-arm negatives.

Canonical pose phrases:
```text
hand-to-chest pose, one hand placed on chest, gentle worried gesture
one hand on hip, confident standing pose, other arm relaxed
arms crossed, crossed arms in front of chest, confident serious pose
```

Removed/weak:
```text
pointing, pointing gesture, scolding point
```
Pointing was weak in this pack and should not remain as a canonical template until retested successfully.

PASS:
- arm pose readable at a glance
- upper-body/cowboy framing preserved
- hands not catastrophic
- no extra character/inset

FAIL:
- pose unreadable
- tiny full-body framing
- severe hand/arm anatomy failure
- wrong gesture despite good face

## 05. Same-character pose ref-generation

Canonical templates:
```text
api_workflows/05_pose_refregen_arms_crossed_d0p42_w0p60_api.json
api_workflows/05_pose_refregen_one_hand_hip_d0p42_w0p60_api.json
api_workflows/05_alpha_toonout_example_api.json
```

Required inputs:
```text
hermes_refregen_identity_auburn_719238043.png
hermes_refregen_pose_arms_crossed_source.png
hermes_refregen_pose_one_hand_hip_source.png
```

Purpose:
- Use the pose donor as img2img latent source, then use the approved character anchor as IPAdapter identity/style reference.
- This replaced the failed post-alpha face/hair composite direction.

Canonical settings:
- denoise: `0.42`
- IPAdapter weight: `0.60`
- IPAdapter weight type: `style and composition`
- IPAdapter range: start `0.0`, end about `0.85`
- steps: `28`
- CFG: `6.0`
- sampler: `euler_ancestral`
- scheduler: `normal`

Prompting method:
1. Prompt the target as the same character family, not as a brand-new character sheet.
2. Keep the pose phrase from the donor explicit: `arms crossed` or `one hand on hip`.
3. Keep identity locks concise: auburn hair, target eye color, uniform/outfit colors, same anime VN style.
4. Do not add broad compositing instructions like “paste original face/hair”; the workflow uses conditioning, not alpha-paste.
5. If pose obedience is weak, first check donor quality. Do not immediately increase denoise because identity/style may drift.

PASS:
- pose remains readable
- face/hair/outfit closer to canonical anchor than raw donor
- no prayer-hands ghosting or pasted seams
- no duplicate/inset character

FAIL:
- identity not improved over donor
- pose collapses back to neutral/clasped hands
- translucent guide residue or pasted-looking seams
- hands/arms unusable at Ren'Py scale

## 06-08 next templates: not yet canonical successes

These remain because they are the next requested workflow directions, but they are not yet successful artifact-QA workflows.

### 06 Background generation
Template:
```text
api_workflows/06_background_generation_no_text_api.json
```

For day/night sets, keep using 06: generate separate daytime and nighttime base backgrounds directly, then QA them side by side for location similarity, no-text safety, and lower-third readability.

Prompt method:
```text
empty anime background art, [location], architectural environment only,
no people, no characters, clean lower third for dialogue box,
detailed but readable, 16:9 composition
```

Negative block:
```text
text, watermark, logo, letters, words, readable writing,
subtitles, captions, dialogue box, textbox, nameplate,
ui, interface, overlay, visual novel screenshot, game screenshot,
people, person, face, hands
```

### 07 Background variation
Template:
```text
api_workflows/07_background_variation_img2img_layout_lock_api.json
```

Prompt method:
```text
same [location] layout and camera angle,
[rainy/cloudy/weather] atmosphere variation,
preserve windows/doors/desks/chalkboard positions,
empty anime background art, no people
```

Start with denoise `0.38`; sweep only if needed:
```text
0.72 = canonical tested rain setting when paired with Canny/lineart ControlNet
0.55 = weaker weather change, stronger base preservation
Do not use this template for day/night conversion; generate separate day/night bases with 06.
```

### 08 Event CG
Template:
```text
api_workflows/08_event_cg_no_text_story_beat_api.json
```

Prompt method:
```text
story event CG, [specific prop/action], [location], [mood/light],
no readable text, no people/hands unless explicitly needed,
clean focal point, 16:9 composition, lower third readable for dialogue box
```

CG QA must inspect full size, because contact sheets hide fake glyphs.

## Production sequence

For the current canonical chain:
1. Run 01 anchor.
2. Copy selected output to ComfyUI input as `hermes_other_auburn_seed719238043.png`, `hermes_expr_auburn_neutral.png`, and `hermes_refregen_identity_auburn_719238043.png` as needed.
3. Run 02 alpha for neutral.
4. Run 03 expression sources, then copy selected outputs to `hermes_expr_selected_*.png`, then run 03 alpha templates.
5. Run 04 pose donors, then copy selected hand/hip/cross outputs to the required pose input names.
6. Run 05 pose ref-generation, then run `05_alpha_toonout_example_api.json` on selected ref-generated outputs.
7. Only after this, do Ren'Py screen-fit, sprite-set consistency, and background integration QA.

## What not to preserve as canonical

Do not preserve executable templates for:
- alternate seeds that were not selected,
- alpha sweeps that lost to the canonical setting,
- weak pose directions like pointing,
- “maybe useful” alternatives without artifact QA,
- failed post-alpha composite approaches.

Keep those only as short lessons in verdict docs if needed.


## 09-14 generation expansion scaffolds

These extend the asset-generation categories after the completed/smoke-passed 01-08 set. They are not canonical successes until smoke artifacts exist.

### 09 Support character
Templates:
```text
api_workflows/09_support_character_anchor_teacher_api.json
api_workflows/09_support_character_alpha_toonout_api.json
```
Prompt method:
```text
masterpiece, best quality, very aesthetic, newest,
1girl, solo, anime style, cowboy shot, upper body character portrait,
[role], [hair], [eyes], [simple role outfit], relaxed standing pose,
flat solid medium gray background
```
Keep support characters lightweight: one anchor and only the expressions needed by the route.

### 10 Outfit / costume variation
Templates:
```text
api_workflows/10_outfit_casual_img2img_ipadapter_api.json
api_workflows/10_outfit_alpha_toonout_api.json
```
Start with `denoise=0.50`, IPAdapter weight about `0.58`. Lower denoise if identity/style drifts; raise it only if the outfit refuses to change. If this route fails, escalate to masked outfit edit/inpaint rather than over-prompting.

### 11 Prop / effect overlay
Templates:
```text
api_workflows/11_prop_single_object_key_api.json
api_workflows/11_prop_alpha_toonout_api.json
api_workflows/11_effect_magic_shimmer_black_bg_api.json
```
Props should be single centered objects with no text/glyphs. Glow/particle effects may be better as black-background additive overlays than forced alpha PNGs.

### 12 SFX
Use `12_sfx_generation/` for procedural/library/AI SFX design. Short UI/common Foley should be procedural or library-first; reserve AI for unusual ambience/supernatural sounds.

### 13 BGM
Use `13_bgm_generation/` for instrumental, loopable, dialogue-friendly BGM prompt templates. Do not lock a backend until ACE-Step/HeartMuLa/external/library route is chosen and smoke-passed.

### 14 Audio packaging
Use `14_audio_packaging_and_looping/` to convert/normalize/trim generated audio into Ren'Py-friendly `.ogg` files and write an audio manifest.
