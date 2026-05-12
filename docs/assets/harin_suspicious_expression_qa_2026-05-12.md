# Harin suspicious expression QA (2026-05-12)

Status: prototype expression promoted / Ren'Py screenshot QA PASS.

## Goal

Replace the temporary neutral reuse for `sprite_harin_suspicious` with a distinct Harin suspicious/tsundere expression while preserving the user-selected s03 cute-tsundere anchor.

## Source and workflow provenance

- Neutral source anchor: `generated/comfyui/harin_tsundere_candidates_20260512_215310/s03_harin_tsundere.png`
- Candidate run: `generated/comfyui/harin_suspicious_expression_20260512_222032/`
- Contact sheet: `generated/comfyui/harin_suspicious_expression_20260512_222032/harin_suspicious_source_contact_sheet.png`
- Source workflow base: `workflow_packs/renpy_asset_workflows/api_workflows/03_expression_source_angry_move_d0p54_w0p48_api.json`
- Alpha workflow base: `workflow_packs/renpy_asset_workflows/api_workflows/03_expression_alpha_angry_toonout_o0_b0_ref0_api.json`
- Run manifest: `generated/comfyui/harin_suspicious_expression_20260512_222032/RUN_MANIFEST.json`

Policy: derived from repo-local canonical workflow pack 03. Edited only the input image, expression prompt phrase, seed, denoise/IPAdapter weight/CFG, and output prefix.

## Candidate QA

Generated four candidates:

- `suspicious_a`: basic suspicious/pout with blush.
- `suspicious_b`: conservative side-eye/small pout, selected for first route prototype.
- `suspicious_c`: stronger puffed-cheek tsundere expression, but more drift risk.
- `suspicious_d`: stricter auditor expression.

Selected candidate: `suspicious_b`.

Selection reason: it keeps crop/outfit/identity closest to the s03 anchor while giving a readable but not over-comic suspicious/pouting expression. The expression is subtler than `suspicious_c`, but safer for immediate route use.

## Alpha proof

- Alpha output: `generated/comfyui/harin_suspicious_expression_20260512_222032/suspicious_b_alpha.png`
- Semantic promoted path: `demo/game/images/characters/harin/harin_suspicious.png`
- Alpha stats: min=0 max=255 transparent=1045603 opaque=706136 semi=17733
- Dark alpha sheet: `generated/comfyui/harin_suspicious_expression_20260512_222032/harin_suspicious_alpha_dark_sheet.png`

Visual alpha QA: on a dark sheet, no large full-canvas alpha failure was visible. Hair tips and lineart are preserved well enough for prototype use. Minor edge polish may still be final-art debt.

## Ren'Py screenshot QA

- Testcase: `qa_harin_suspicious_expression`
- Screenshot: `generated/renpy_harin_suspicious_expression_qa_2026-05-12/qa_harin_suspicious_expression.png`
- Result: PASS.

Screenshot QA notes:

- Both neutral and suspicious QA sprites are visible over the summoning hall background.
- Korean dialogue text is readable.
- Sprites do not block the textbox.
- Suspicious expression is visibly distinct at VN scale, mainly through narrower eyes, blush, and small pout, though it remains conservative.

## Verification

- RED contract test first: `test_harin_suspicious_expression_is_distinct_alpha_promoted_and_qa_recorded` failed before implementation because QA doc/manifest/distinct file did not exist.
- Static tests: PASS `python3 tools/run_static_tests.py` — 12 passed.
- Ren'Py lint: PASS `renpy.sh demo lint` exit 0.
- Ren'Py testcase screenshot: PASS `qa_harin_suspicious_expression`.

## Remaining caveats

- This is a prototype expression, not final expression-sheet quality.
- If later scenes need a stronger comic 츤데레 reaction, use `suspicious_c` as a direction candidate or regenerate a stronger expression pass.
