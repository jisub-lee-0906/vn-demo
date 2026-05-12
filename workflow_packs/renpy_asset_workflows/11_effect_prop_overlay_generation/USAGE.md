# 11 effect / prop overlay generation

Status: smoke PASS after minimal-prompt retry. Magic shimmer black-bg effect PASS candidate; original over-constrained key prop route failed due plate/box contamination, but minimal single-key route produced usable transparent prop candidates.

Purpose:
- Create single prop overlays and visual effect overlays for VN scenes.
- Split into two routes: solid prop alpha PNGs and additive black-background effects.

API templates:
- `../api_workflows/11_prop_single_object_key_api.json` (negative lesson / over-constrained v2, failed)
- `../api_workflows/11_prop_single_object_key_minimal_api.json` (preferred minimal key prop smoke)
- `../api_workflows/11_prop_alpha_toonout_api.json`
- `../api_workflows/11_effect_magic_shimmer_black_bg_api.json`

Route A: prop alpha
1. Generate one centered prop on neutral gray background.
2. Avoid text/glyphs/logos/labels.
3. Copy selected output to `hermes_prop_key_SOURCE_TO_PROCESS.png`.
4. Run toonout alpha.

Route B: additive effect
1. Generate effect on black background.
2. Use in Ren'Py as a screen/additive-style overlay or convert to alpha later if needed.
3. This is often safer for glow/particle effects than forcing semantic alpha extraction.

PASS for prop:
- one object only,
- clear silhouette,
- no fake text/glyphs,
- alpha extraction likely clean.

PASS for effect:
- effect has readable focal shape,
- no character/hand/object contamination,
- black background can be blended or keyed,
- not full-frame noise that blocks the scene.

FAIL:
- generated labels/text,
- hands/people included unintentionally,
- effect looks like a full background instead of overlay,
- prop is cropped or duplicated.


## 2026-05-12 minimal key prop retry

User suggestion: keep the prop route small by generating a single prop with a minimal prompt, then run transparency only if the source is clean.

Minimal prompt smoke:
- positive: `masterpiece, best quality, single old brass key, isolated object, plain gray background`
- negative: `text, watermark, logo, people, hands, box, plate, tray, table, book, duplicate, cropped`
- seeds tested: `61124021`, `61124022`, `61124023`, `61124024`

Verdict:
- `61124022` failed because it generated multiple keys/keyring objects.
- `61124023` is a usable single perspective key source, but has a stronger painted shadow/perspective.
- `61124021` is a usable ornate single-key alternate.
- `61124024` is the cleanest simple vertical single-key prop candidate.

Selected transparent candidates:
- Preferred seed `61124024` for the clean simple vertical key.
- `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_prop_overlay\alpha_minimal_key_seed61124024_toonout_o0_b0_ref0_00001_.png`
- alternate: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_prop_overlay\alpha_minimal_key_seed61124021_toonout_o0_b0_ref0_00001_.png`
- QA sheet: `C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_prop_overlay\qa_alpha_minimal_key_black_gray_checker_20260512.jpg`

PASS scope:
- This proves the prop/key workflow does not need a complicated prompt. Minimal source generation + toonout alpha is enough for a simple prop-overlay template.
- Still not semantically promoted into a game route; use only after scene placement/Ren'Py screenshot QA.
