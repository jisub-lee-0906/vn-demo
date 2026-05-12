# 10 — 의상/코스튬 변형

Category: `character`

## Purpose

기존 캐릭터에 hoodie/jacket/dress 등 의상 차이를 준다.

## Output

outfit variant/alpha

## API templates

- `workflow_api/10_outfit_alpha_toonout_api.json` — toonout alpha for selected outfit variation source | inputs: hermes_outfit_casual_SOURCE_TO_PROCESS.png | status: AVAILABLE for selected outfit candidates; alpha/RenPy QA required for any game-promoted outfit
- `workflow_api/10_outfit_masked_torso_tight_inpaint_api.json` — preferred tight-mask torso inpaint route for casual pullover/sweater | inputs: hermes_outfit_identity_source.png | status: SMOKE PASS direction candidate; preserves face/hair and improves outfit change; collar/tie remnants and RenPy QA remain
- `workflow_api/10_outfit_pulid_i2i_lavender_hoodie_api.json` — PuLID face-anchored full-image i2i for distinct hoodie costume target | inputs: hermes_outfit_identity_source.png | status: USER-ACCEPTED COMPLETE direction: PuLID+i2i face retention is acceptable for workflow 10; final outfit use still needs alpha/RenPy QA before game promotion
- `workflow_api/10_outfit_pulid_i2i_variety2_black_leather_jacket_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: REJECT for VN safe/default set: leather jacket obeyed partly but became overly revealing crop/bikini-like; identity also softer.
- `workflow_api/10_outfit_pulid_i2i_variety2_blue_denim_jacket_strong_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: actual blue denim jacket + white tee, good candidate; face/hair acceptable.
- `workflow_api/10_outfit_pulid_i2i_variety2_purple_witchy_capelet_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: fantasy capelet/dress vibe; face slightly softer but acceptable.
- `workflow_api/10_outfit_pulid_i2i_variety2_yellow_summer_dress_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: clear yellow dress/top; lower skirt layering remains but outfit change is strong.
- `workflow_api/10_outfit_pulid_i2i_variety_black_bomber_jacket_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS-ish but prompt drift: became cream/white puffer/bomber, not black; face/hair close, school feel mostly gone.
- `workflow_api/10_outfit_pulid_i2i_variety_denim_jacket_white_tee_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS for casual outfit but denim jacket prompt collapsed to white tee + denim shorts; strong outfit change, face close.
- `workflow_api/10_outfit_pulid_i2i_variety_green_field_jacket_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: clear green jacket, strong clothing change, face/hair acceptable.
- `workflow_api/10_outfit_pulid_i2i_variety_pink_ribbon_blouse_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: distinct cute pink blouse/dress-like top, face/hair acceptable; hands changed but usable.
- `workflow_api/10_outfit_pulid_i2i_variety_red_track_jacket_api.json` — PuLID+i2i outfit variety batch candidate | inputs: hermes_outfit_identity_source.png | status: PASS direction: clear sporty track jacket, good face/hair retention, clean silhouette.

## Editable fields

Usually safe to edit only: prompt, negative prompt, seed, input filename, output prefix. If changing node structure, save a new JSON with a clear name.

## Inputs

Check each API JSON `LoadImage` filename and ensure the file exists in the active ComfyUI input directory. Required inputs are listed above when known.

## Test / QA

얼굴/헤어 유지, torso mask 경계, 의상 오염 확인

For game-ready promotion, verify actual outputs with contact sheet or RenPy screenshot. Do not rely on workflow theory alone.

## Extra files

- none
