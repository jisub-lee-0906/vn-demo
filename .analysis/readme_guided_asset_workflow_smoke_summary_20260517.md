# README-guided asset workflow smoke test — 2026-05-17

Scope: final live smoke test using each workflow README's prompting method/template and runtime placeholder substitutions.

Run id: `hermes_vn_readme_guided_smoke_20260517_153253`

Backend: `http://172.28.224.1:8001`

Rules:
- canonical API JSON files were not edited
- prompts were patched in runtime payload only
- generated files went to ComfyUI output/input runtime folders, not canonical pack folders
- README templates were followed for placeholder substitution
- safety adjustment: README `nude` token in `character_anchor_base` and `expression_variations` live smoke prompts was replaced with `fully_clothed, school_uniform`

Technical verification:
- `/system_stats`, `/queue`, `/object_info` accessible
- missing class types: none
- all 7 workflows submitted successfully
- queue empty after run
- report: `/home/jisub-lee/workspace/vn-demo/.analysis/readme_guided_asset_workflow_smoke_report.json`
- quick HTML contact sheet: `/home/jisub-lee/workspace/vn-demo/.analysis/readme_guided_asset_workflow_smoke_contact_sheet.html`

Prompt ids and outputs:

1. `character_anchor_base`
   - prompt id: `dfa50bea-166c-4336-9ae3-a536bdb22898`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/01_anchor_readme_00001_.png`
   - QA note: no blank/wrong-subject/placeholder/duplicate-chibi failure observed. Framing is upper/cowboy-ish rather than full body; production anchor prompt may need stricter full-body framing if needed.

2. `expression_variations`
   - prompt id: `f2be1869-8512-464c-85b6-07349b95a537`
   - outputs:
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/02_expression_readme_00001_.png`
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/02_expression_readme_00002_.png`
     - `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/02_expression_readme_00003_.png`
   - QA note: expression changed; no major mask/composite failure observed.

3. `transparency_alpha`
   - prompt id: `5d24d8a2-735c-4714-a6d4-765c96d9406a`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/03_alpha_readme_00001_.png`
   - QA note: alpha/cutout generated; no obvious blank/background-removal failure observed. Edge cleanup remains per-asset QA.

4. `background_art`
   - prompt id: `07135fac-81a4-4c64-b9a4-0262eab1b9f3`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/04_background_readme_00001_.png`
   - QA note: 16:9 classroom background; no characters or placeholder text observed.

5. `prop_closeup_cg`
   - prompt id: `52aed920-08c1-4123-8ef3-9b22d5dcf3a1`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/05_prop_readme_00001_.png`
   - QA note: key close-up generated; no readable text/logo/placeholder failure observed.

6. `outfit_variations`
   - prompt id: `c09f151a-c0c3-46d5-ac0f-abd53bedaae7`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/06_outfit_readme_00001_.png`
   - QA note: blazer/cardigan outfit variant generated; no severe face/body corruption or obvious face-protect failure observed.

7. `event_cg`
   - prompt id: `4fedd306-a20b-4ae3-a1cb-c8622a59a8f4`
   - output: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_readme_guided_smoke_20260517_153253/07_event_cg_readme_00001_.png`
   - QA note: 16:9 classroom event CG generated; no blank/no-character/unusable-frame failure observed. As expected for event CG, identity/outfit can reinterpret.

Conclusion:
- README-guided technical smoke pass for all 7 canonical workflows.
- The pack can now be treated as ready for game-time asset generation, with per-output visual QA before promotion.
