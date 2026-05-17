# Final asset workflow smoke test — 2026-05-17

Scope: canonical VN/ComfyUI asset workflow pack after freeze/documentation pass.

Run id: `hermes_vn_final_smoke_20260517_150645`

Backend: `http://172.28.224.1:8001`

Rules:
- canonical API JSON files were not edited
- prompts were patched in runtime payload only
- generated files went to ComfyUI output/input runtime folders, not canonical pack folders

Technical verification:
- `/system_stats`, `/queue`, `/object_info` accessible
- missing class types: none
- all 7 workflows submitted successfully
- queue empty after run
- report: `/home/jisub-lee/workspace/vn-demo/.analysis/final_asset_workflow_smoke_report.json`
- quick HTML contact sheet: `/home/jisub-lee/workspace/vn-demo/.analysis/final_asset_workflow_smoke_contact_sheet.html`

Prompt ids and outputs:

1. `character_anchor_base`
   - prompt id: `1330ed49-ecbc-4cbc-979f-eabbf842e148`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/01_anchor_00001_.png`
   - QA note: character source generated; major workflow failure not observed. Minor issue: prompt produced a small chibi/thumbnail-like extra figure in the upper-left, so production anchor prompts may need stronger negatives if this repeats.

2. `expression_variations`
   - prompt id: `ce36643d-e386-4f21-9ed4-00e0c550caf0`
   - mask/debug/final outputs:
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/02_expression_00001_.png`
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/02_expression_00002_.png`
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/02_expression_00003_.png`
   - QA note: face/expression changed on the same source; no major mask/composite failure observed.

3. `transparency_alpha`
   - prompt id: `aaac3125-ac2a-4b33-b07a-79e598213dbc`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/03_alpha_anchor_00001_.png`
   - QA note: character cutout produced; no blank/wrong-subject failure observed. Edge/hair cleanup still requires user QA for production.

4. `background_art`
   - prompt id: `428be237-e88b-42a7-a365-97ada6d2f30b`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/04_background_00001_.png`
   - QA note: 16:9 classroom background, no character/text failure observed.

5. `prop_closeup_cg`
   - prompt id: `3a0615c5-132f-4110-a68f-5100ed5153bc`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/05_prop_00001_.png`
   - QA note: brass key close-up generated; no text/logo or blank failure observed.

6. `outfit_variations`
   - prompt id: `9209c447-66cb-47e9-a434-a2dfec9e891a`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/06_outfit_00001_.png`
   - QA note: outfit/source-character variant generated; no severe face/body corruption observed. Identity/outfit drift still needs user QA.

7. `event_cg`
   - prompt id: `122d5a7c-aa65-47c9-8182-db29c5ccd032`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_final_smoke_20260517_150645/07_event_cg_00001_.png`
   - QA note: 16:9 event CG generated with character/background; no blank/unusable-frame failure observed. Identity/outfit drift visible enough that this should be treated as event-CG reinterpretation, not dialogue sprite preservation.

Conclusion:
- Technical smoke pass for all 7 canonical workflows.
- Treat pack as ready for game-time asset generation.
- Continue using artifact QA before promoting individual generated assets.
