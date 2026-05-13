# 04 low-denoise refine smoke — 2026-05-13

Purpose: test whether a 04 direct pose+expression draft can be used as an img2img source and refined at low denoise to recover a more polished 01-like finish while preserving arms-crossed happy/open-mouth pose.

Input draft:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_quality_style_sweep_20260513/04_q01_crisp_ip065_seed719252501_00001_.png
```

Run folder:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513
```

Workflow/script:

```text
00_experiment_sandbox/scripts/run_04_lowdenoise_refine_sweep.py
00_experiment_sandbox/workflow_api/00_04_lowdenoise_refine_refine_d25_seed719253025_api.json
00_experiment_sandbox/workflow_api/00_04_lowdenoise_refine_refine_d35_seed719253035_api.json
00_experiment_sandbox/workflow_api/00_04_lowdenoise_refine_refine_d45_seed719253045_api.json
```

Outputs:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/refine_d25_seed719253025_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/refine_d35_seed719253035_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/refine_d45_seed719253045_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/contact_sheet_draft_vs_lowdenoise_refine.png
```

Observed result from contact sheet:

- All three low-denoise variants preserved the arms-crossed pose and happy/open-mouth expression.
- `denoise=0.25` is closest to the draft, with only mild polish change.
- `denoise=0.35` is the best current balance: cleaner/sharper perceived finish without obvious pose/expression loss.
- `denoise=0.45` still preserves the pose but starts to show stronger style/line/color reinterpretation risk.

02 alpha smoke on provisional best `denoise=0.35`:

```text
source: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/refine_d35_seed719253035_00001_.png
alpha:  /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/02_alpha_after_refine_d35_b1_ref1_00001_.png
QA sheet: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_lowdenoise_refine_20260513/qa_alpha_refine_d35_light_dark_composite.png
prompt_id: 553c46d6-2226-4747-a304-64ea8f83e661
```

Alpha QA observation:

- Output is RGBA 1152x1536.
- No obvious severe gray-background residue.
- No obvious white sticker rim on dark composite.
- Hair, hands, sleeves, and skirt edges appear intact at contact-sheet scale.

Status: promising sandbox candidate only. Do not promote canonical 04/05 until user visual QA and at least multi-pose + second-character retest pass.
