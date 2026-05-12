# 13 BGM generation

Status: scaffold template, not smoke-passed yet.

Purpose:
- Generate or curate instrumental VN background music by mood/scene role.
- Keep BGM dialogue-friendly: no vocals by default, no aggressive lead melody fighting the text, loopable structure.

Initial BGM slots:
- `bgm_school_day_loop`
- `bgm_mystery_letter_loop`
- `bgm_soft_romance_loop`
- `bgm_lonely_night_loop`
- `bgm_comic_light_loop`

Generation routes:
1. ComfyUI/ACE-Step route if the local audio workflow is recovered and smoke-passed.
2. HeartMuLa/open-source route if local GPU/dependencies are approved.
3. External generator route such as Suno/Udio only with license/reproducibility notes.
4. Licensed library/composer route for production-safe final music.

Output target:
- `game/audio/bgm/*.ogg`

BGM rules:
- instrumental unless a vocal insert is explicitly desired,
- 30-90 sec loop candidates,
- short/no intro for frequently repeated tracks,
- no long silence at tail,
- normalize consistently after generation,
- document source/generator/prompt/license.

This folder is design-only until one audio generation backend is chosen and smoke-passed.
