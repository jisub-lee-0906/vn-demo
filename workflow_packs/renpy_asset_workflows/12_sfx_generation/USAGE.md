# 12 SFX generation

Status: scaffold template with procedural prototype artifacts generated; not final listened/mastered audio.

Purpose:
- Build reusable VN sound effects: UI click/confirm, paper rustle, door slide, school bell, magic shimmer, tension hit.
- Prefer library/procedural SFX for short UI and common Foley; use AI only for unusual supernatural or ambience sounds.

When to use:
- Use this workflow when a Ren'Py route needs short reusable SFX assets before final audio production.
- Use procedural/library routes first for UI and common Foley where consistency matters more than AI novelty.
- Use AI generation only for unusual supernatural, ambience, or texture sounds that are hard to source procedurally.
- Do not treat the included prototype WAV/OGG files as final mastered game audio without listening QA.

Inputs / sources:
- SFX need list from the script or UI event map.
- Route choice per sound: procedural, licensed library, or AI-generated.
- Target semantic filenames such as `ui_click`, `ui_confirm`, `paper_rustle`, `door_slide`, `magic_shimmer`.
- For procedural prototypes: `scripts/generate_ui_sfx.py` and optional ffmpeg conversion to OGG.
- For library/AI sources: original license/source notes, source WAV/MP3, trim points, and intended loop/one-shot behavior.

Recommended first smoke pack:
- `ui_click.ogg`
- `ui_confirm.ogg`
- `paper_rustle.ogg`
- `door_slide.ogg`
- `magic_shimmer.ogg`

Workflow routes:
1. Procedural route: synthesize short UI/tone/noise effects, then normalize and convert to `.ogg`.
2. Library route: import licensed SFX, trim silence, normalize, and rename semantically.
3. AI route: generate rare ambience/supernatural SFX, then trim/normalize like all others.

Output target:
- `game/audio/sfx/*.ogg`

Format rules:
- short UI SFX: about 0.05-0.4 sec,
- foley SFX: about 0.3-3 sec,
- ambience SFX: about 5-30 sec if looping,
- no long silent tails,
- loudness/peak normalized consistently.

Included helper:
- `scripts/generate_ui_sfx.py` creates simple WAV prototypes; use ffmpeg to convert to ogg if needed.
