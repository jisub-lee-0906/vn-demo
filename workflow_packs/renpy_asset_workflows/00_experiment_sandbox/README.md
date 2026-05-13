# 00 — Experiment Sandbox

Non-canonical lab for VN/ComfyUI workflow experiments before touching numbered canonical folders.

Current active experiments:

- `workflow_api/00_nova_t2i_basic_direct_clip_api.json` — Nova Anime XL IL v19 direct-CLIP T2I baseline used during 01 prompt tuning.
- `workflow_api/00_03_expression_florence2_inpaint_design_api.json` — design/skeleton for 03 expression test using Florence-2 face mask + DifferentialDiffusion + InpaintModelConditioning + SDXL Union ControlNet repaint.
- `workflow_api/00_03_expression_florence2_face_composite_smoke_api.json` — executed 03 expression sandbox candidate using maintained kijai Florence2Run face mask, raw inpaint, and final `ImageCompositeMasked` over the original to preserve non-face pixels. Promoted into `03_expression_variation_face_composite/` as the canonical 03 template after silver-bob smoke tests.
- `workflow_api/00_04_pose_openpose_ipadapter_txt2img_smoke_api.json` — executed 04 pose sandbox candidate using `EmptyLatentImage` + denoise 1.0 + anchor IPAdapter + OpenPose Union ControlNet. Promising for arms-crossed pose transfer; not canonical yet.
- `notes/03_florence2_face_inpaint_expression_design.md` — node-by-node design and run cautions for the Florence-2 inpaint expression route.
- `notes/04_openpose_ipadapter_txt2img_pose_smoke.md` — node design, batch settings, evidence, and next gates for the 04 OpenPose/IPAdapter pose route.
- `notes/04_pose_method_sweep_depth_canny_mask_pulid_2026-05-13.md` — executed comparison of Depth/Canny replacement, IPAdapter attention mask, and PuLID/IPAdapter role split for 04 pose drift reduction.
- `notes/04_pose_combo_masked_ipadapter_pulid_2026-05-13.md` — executed combination test of masked IPAdapter plus PuLID; PuLID combo did not beat mask-only baseline.
- `notes/04_pose_prompt_audit_2026-05-13.md` — prompt cleanliness/conflict audit for 04 pose sandbox; recommends a Danbooru-clean background-lock prompt for the next test.
- `notes/04_pose_clean_prompt_masked_ipadapter_2026-05-13.md` — executed clean Danbooru prompt on the mask-only 04 baseline; fixed dark/vignette drift and produced the current best sandbox candidate.
- `notes/04_pose_clean_baseline_multipose_secondchar_2026-05-13.md` — executed clean baseline across multiple poses and a second character; supports 04 canonical candidacy with caveats for pointing/one-hand-hip drift.
- `notes/04_pose_alpha_gate_2026-05-13.md` — executed 02 alpha gate on accepted 04 pose outputs; four alpha/light/dark composites passed and 04 is ready for canonical promotion pending user approval.
- `notes/04_pose_background_tag_sweep_2026-05-13.md` — same-seed background tag sweep; selected positive `grey_background` only for 04 canonical to avoid simple/flat/dark background conflicts.
- `notes/02_alpha_white_edge_diagnosis_2026-05-13.md` — diagnosed white/light sprite edge after 02 alpha; root is semi-transparent edge RGB from BiRefNetRMBG feathering plus light source colors, not mainly unremoved background.
- `workflow_api/legacy_04_pose_precanonical_2026-05-13/` — archived old 04 text-only and img2img/IPAdapter JSONs after OpenPose masked-IPAdapter became the only active numbered-04 canonical.

Rules:

- Keep new exploratory variants in sandbox first; only promote to numbered folders after real output QA.
- Current smoke evidence favors face-mask composite over raw inpaint for non-face color preservation; keep raw inpaint only as a diagnostic output.
- Use 01 source/anchor PNG before 02 alpha for expression testing.
- Keep prompt content Danbooru tag-only.
- Generated PNG/contact sheets stay under ComfyUI output folders, not inside this reusable pack.
