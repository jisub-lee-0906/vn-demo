# 04 original-style preservation pivot — 2026-05-13

User QA rejected the previous low-denoise refine family:

> 다별로야 원본을 전혀못살려

Interpretation: routes based on 04 OpenPose/IPAdapter output plus img2img refine do not preserve the accepted 01 source look enough. Do not treat `04_lowdenoise_refine` as a promotion candidate.

Immediate pivot tested: keep the exact 01 txt2img graph/checkpoint/sampler/quality style and change only prompt pose/expression, then seed-hunt.

Run:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513
```

Script:

```text
00_experiment_sandbox/scripts/run_04_promptonly_original_style_seedhunt.py
```

Contact sheet:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/contact_sheet_original_vs_promptonly_seedhunt.png
```

Outputs:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251035_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251136_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251237_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251338_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251439_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_promptonly_original_style_20260513/promptonly_arms_crossed_happy_seed719251540_00001_.png
```

Observation from contact sheet:

- Prompt-only preserves the accepted 01 rendering family better than the previous 04/refine pipeline.
- Arms-crossed is readable in most seeds.
- Identity/outfit still drift across seeds, and some seeds add unwanted details/hearts/badges.
- This route is seed-hunting, not a deterministic pose-control solution.

Potential next direction: if user prefers this visual family, run larger seed batches with stricter negative tags for `heart, badge, emblem, sticker, chibi, super_deformed, white_outline` and pick a usable seed, then alpha smoke. If user requires exact 01 identity/pixels, pose-change generation may need a different model/edit route rather than more IPAdapter/refine tuning.
