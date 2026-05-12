# 08 Event CG generation: story-beat no-text CG

Purpose: generate story-specific CGs for route beats while avoiding fake text/UI/person contamination.

API template: `../api_workflows/08_event_cg_no_text_story_beat_api.json`

Smoke status fixed on 2026-05-12:
- Status: SMOKE PASS as a no-text prop/action event-CG workflow candidate.
- Selected smoke candidate: `uppermid_s2`, seed `812347402`.
- Model: `novaAnimeXL_ilV180.safetensors`.
- Output reference, not archived in this template pack:
  - WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_event_cg_smoke_20260512/cg_letter_hook_uppermid_s2_seed_812347402_00001_.png`
  - Windows: `C:/Users/Desktop/Documents/ComfyUI/output/hermes_vn_event_cg_smoke_20260512/cg_letter_hook_uppermid_s2_seed_812347402_00001_.png`

Default tested beat:
- mysterious blank sealed envelope / letter hook in a warm school hallway near classroom doors
- no readable text on paper
- no people/hands/faces
- 16:9 event CG with a cleaner foreground/lower-third area for dialogue UI

Important caveat:
- The selected smoke candidate works as a mysterious sealed-envelope hallway hook CG.
- It is not a perfect "envelope physically protruding from the gap under the door" proof. Attempts to force exact under-door geometry often made the envelope stick to the door, moved it into the lower textbox zone, or produced worse compositions.
- If the script absolutely requires "slid under the door" in close-up, treat that as a later inpaint/control/masked-edit refinement, not a blocker for closing the 08 no-text event-CG smoke.

Canonical prompt pattern:
```text
masterpiece, best quality, very aesthetic, newest, anime event CG, long school hallway with classroom doors, one small blank sealed envelope on the wooden floor in the upper middle of the image near a classroom door, simple red wax seal, quiet suspense, warm afternoon light, large empty clean foreground floor in the bottom third for dialogue box, no people, no hands, 16:9 background art
```

Canonical negative pattern:
```text
text, watermark, logo, letters, words, readable writing, fake glyphs, handwriting, printed lines, ruled paper, document, notice, poster, sign, label, book page, subtitles, captions, dialogue box, textbox, nameplate, ui, interface, overlay, visual novel screenshot, game screenshot, people, person, girl, boy, face, hand, fingers, envelope stuck to door, paper on wall, extra envelope, floating paper, blood, blood splatter, red liquid, impossible perspective
```

Workflow:
1. Write the exact story beat first: object/action/location/emotion.
2. Prefer prop/action composition over generic pretty scenery.
3. Use the selected template for letter/envelope hook beats, or replace only the prop/action/location block for a new CG.
4. Keep direct negatives for `readable writing`, `fake glyphs`, `ui`, `dialogue box`, `people`, `hands`, `faces`, and prop-specific contamination.
5. Generate 2-4 candidates only.
6. Inspect likely winners full-size for tiny fake glyphs, hands, extra people, UI overlays, or contradiction with the script line.
7. Promote to semantic Ren'Py path only after actual route screenshot QA.

PASS criteria:
- clearly supports the story beat
- no fake text/glyphs/UI overlay
- no unintended people/hands/faces
- no blood/red-liquid contamination unless the script explicitly calls for it
- focal point remains visible or at least readable with the intended dialogue-box treatment
- composition matches the script action closely enough for the current route beat

FAIL criteria:
- prettier image contradicts the line action
- unreadable/fake text on letter/sign/book/poster
- unexpected hand/person appears
- blood/red splatter appears from wax-seal prompting
- lower third hides the focal point too much for the intended dialogue UI

Promotion gate:
- `scene cg <id>` screenshot in Ren'Py with dialogue visible, not just a ComfyUI contact sheet.
