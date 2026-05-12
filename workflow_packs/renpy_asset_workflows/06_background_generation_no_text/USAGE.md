# 06 Background generation: no-text VN location

Purpose: generate reusable Ren'Py 16:9 location backgrounds without fake UI/text contamination.

Scope note fixed on 2026-05-12:
- Use this workflow for separate day/night base backgrounds.
- Do not rely on 07 img2img weather variation to convert a bright daytime background into a true night background.
- For a day/night set, generate `empty anime classroom, daytime...` and `empty anime classroom, night...` as separate 06 base candidates, then QA them together for location similarity.

API template: `../api_workflows/06_background_generation_no_text_api.json`

Default target after minimal smoke on 2026-05-12:
- classroom day background
- 1024x576 diagnostic draft canvas, 16:9
- `novaAnimeXL_ilV180.safetensors`
- `CLIPSetLastLayer(-2)`
- Euler ancestral / normal / 24 steps / CFG 5.5
- minimal positive: `empty anime classroom, no people, clean lower third`
- minimal negative: `text, ui, people`

Workflow:
1. Start with a minimal location prompt, not a long story prompt.
2. Minimal diagnostic baseline is intentionally short: location + `no people` + `clean lower third`.
3. Keep the negative prompt short first (`text, ui, people`) so failures can be attributed before adding suppression tokens.
4. Generate a 3-6 seed contact sheet.
5. Inspect likely winners full-size for pseudo-glyphs on boards, signs, posters, books, labels, and lower-third clutter.
6. Only if a specific failure appears, add one targeted token at a time, e.g. `letters`, `dialogue box`, `subtitles`, `book titles`, `poster text`.
7. Promote only after a Ren'Py screenshot with textbox proves readability.

PASS criteria:
- no characters/people
- no fake text or UI overlay
- stable readable lower third
- clear scene identity as a repeatable VN location
- plausible room perspective and props

FAIL criteria:
- generated dialogue boxes/nameplates/subtitles
- readable or glyph-like board/poster/book text
- people/hands/faces
- too much foreground clutter behind the textbox
- composition cannot be reused for dialogue scenes

Next upgrade:
- For layout-critical locations, replace pure txt2img with Blender blockout + depth/canny ControlNet template.
