# 00 — Experiment Sandbox

Non-canonical lab for VN/ComfyUI workflow experiments before touching numbered canonical folders.

Current active experiments:

- `workflow_api/00_nova_t2i_basic_direct_clip_api.json` — Nova Anime XL IL v19 direct-CLIP T2I baseline used during 01 prompt tuning.
- `workflow_api/00_03_expression_florence2_inpaint_design_api.json` — design/skeleton for 03 expression test using Florence-2 face mask + DifferentialDiffusion + InpaintModelConditioning + SDXL Union ControlNet repaint.
- `workflow_api/00_03_expression_florence2_face_composite_smoke_api.json` — executed 03 expression sandbox candidate using maintained kijai Florence2Run face mask, raw inpaint, and final `ImageCompositeMasked` over the original to preserve non-face pixels. Promoted into `03_expression_variation_face_composite/` as the canonical 03 template after silver-bob smoke tests.
- `notes/03_florence2_face_inpaint_expression_design.md` — node-by-node design and run cautions for the Florence-2 inpaint expression route.

Rules:

- Keep new exploratory variants in sandbox first; only promote to numbered folders after real output QA.
- Current smoke evidence favors face-mask composite over raw inpaint for non-face color preservation; keep raw inpaint only as a diagnostic output.
- Use 01 source/anchor PNG before 02 alpha for expression testing.
- Keep prompt content Danbooru tag-only.
- Generated PNG/contact sheets stay under ComfyUI output folders, not inside this reusable pack.
