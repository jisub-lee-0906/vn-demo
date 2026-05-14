# 06 mask node QA sandbox

Purpose: inspect the 06 outfit hand/cuff masks node-by-node before merging changes back into the canonical 06 workflow.

This sandbox is intentionally mask-only. It does not run KSampler or generate outfit images.

Active API template:

- `workflow_api/06_outfit_mask_node_qa_api.json`

Runtime placeholders:

- `TEMPLATE_identity_source.png` in node `3` (`LoadImage.image`)
- `TEMPLATE_run_slug` and `TEMPLATE_character_slug` in `SaveImage.filename_prefix`

Saved stages:

1. `00_source_*`
2. `01_char_alpha_*`
3. `02_florence_hand_*`
4. `03_florence_both_hands_*`
5. `04_florence_fingers_*`
6. `05_union_hand_both_*`
7. `06_union_plus_fingers_*`
8. `07_grow2_*`
9. `08_blur_existing_hand_*`
10. `09_handfallback_final_enhanced_*`
11. `10_handfallback_roi_*`
12. `11_handfallback_added_*`
13. `12_handfallback_debug_*`
14. `13_refined_existing_skinfiltered_*`
15. `14_skin_candidate_*`
16. `15_wrist_bridge_*`
17. `16_pretrim_before_cuff_trim_*`

QA rule: final/composite images do not matter here. A stage passes only if the mask itself is anatomically plausible and does not include old outfit cuff/sleeve fabric.

Run helper:

```bash
python3 workflow_packs/renpy_asset_workflows/00_experiment_sandbox/06_mask_node_qa_2026-05-14/scripts/run_mask_node_qa.py \
  --character t5=hermes_vn_outfit_t5/t5_green_glasses_01_seed719260141.png \
  --character pink01=source_pink_twinbraids_seed719251102_00001_.png
```
