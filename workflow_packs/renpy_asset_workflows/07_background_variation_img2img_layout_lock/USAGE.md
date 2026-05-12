# 07 Background variation: same-location weather/layout-locked variation

Purpose: create same-location weather variants, especially rainy-day versions, while preserving the base location layout.

API template: `../api_workflows/07_background_variation_img2img_layout_lock_api.json`

Scope fixed on 2026-05-12:
- This workflow is now closed as a weather-variation workflow.
- Day/night conversion is intentionally excluded from 07.
- For day/night assets, use workflow 06 to generate separate base backgrounds for each time of day, then QA them as a set.
- Reason: smoke tests showed bright classroom/window/daylight priors survived even strong img2img + ControlNet night prompts, while rain variation passed with readable weather change and acceptable layout lock.

Required input image:
- Copy the selected base background to ComfyUI input as `TEMPLATE_bg_base_location.png`, or edit the `LoadImage.image` field in the API JSON.

Default settings after smoke test on 2026-05-12:
- img2img with VAEEncode of the base background
- Canny/lineart ControlNet layout lock using `xinsir-controlnet-union-sdxl-1.0-promax.safetensors`
- checkpoint: `novaAnimeXL_ilV180.safetensors`
- canonical tested prompt: `same classroom rainy day, gray sky, rain outside windows, no people`
- negative: `text, ui, people, layout change`
- denoise 0.72 / ControlNet strength 0.65 / end 0.75
- Euler ancestral / normal / 24 steps / CFG 5.0

Workflow:
1. Generate/choose a base location from workflow 06.
2. Use the base as the img2img input.
3. Change only weather/atmosphere in the positive prompt, not the structural room description.
4. Keep the prompt minimal for diagnosis: `same classroom rainy day, gray sky, rain outside windows, no people`.
5. Use Canny/lineart ControlNet for layout lock when the change must be readable.
6. Use plain low-denoise img2img only for very subtle color shifts; it preserved layout but did not make rain/night readable enough in smoke tests.
7. Compare variants against the base, not just by beauty.
8. Promote as a set only if background furniture/window/door/chalkboard positions still match well enough for scene continuity.

PASS criteria:
- same room/location identity
- major layout landmarks preserved
- weather/atmosphere change is readable, especially rainy-day outside-window cues
- no text/UI/people contamination
- lower third remains textbox-readable

FAIL criteria:
- camera angle or room layout changes
- important props disappear/move
- fake text appears due to posters/boards/signs
- denoise too low to show variation or too high to preserve layout
- attempted day/night conversion still looks like the original time of day

Known non-goal / routed elsewhere:
- Night/day swaps are not solved by 07. Use workflow 06 to generate separate day/night base backgrounds directly, then apply the same no-text, lower-third, and Ren'Py textbox QA gates. If exact one-to-one layout continuity is required later, open a separate 07-night-extension using masked window/light editing or post color-grade; do not reopen the rain/weather template by default.
