# 06 outfit bilateral hand fallback candidate — 2026-05-14

Purpose: test user-reported issue that left/right hands are not masked together in 06 outfit workflow.

Base:

```text
00_experiment_sandbox/06_outfit_handgrow2_candidate_2026-05-14/06_outfit_pulid_i2i_handgrow2_candidate_api.json
```

Graph changes:

```text
node 50 GrowMask.expand remains 2 from handgrow2 candidate
new node 60 VN_AutoHandFallbackProtectionMask
node 52 full protection mask2: 51 -> 60 enhanced_hand_mask
node 53 edit-nohands subtraction mask2: 51 -> 60 enhanced_hand_mask
node 54/56 protecthands preview: 51 -> 60 enhanced_hand_mask
new debug saves:
  node 63 handfallback_roi_*
  node 64 handfallback_added_*
  node 65 handfallback_debug_*
```

Node intent:

```text
existing_hand_mask = Florence union hand/both hands/fingers after GrowMask+blur
if one lower-side band has near-zero existing hand coverage,
search only that side ROI inside/near character alpha for skin-tone hand-like pixels,
grow/blur conservatively,
union with existing hand mask.
```

Important:

- This requires the new custom node `VN_AutoHandFallbackProtectionMask` in Windows ComfyUI `custom_nodes/ComfyUI-VN-AutoMasks`.
- The backend must be restarted before `/object_info` can expose a changed node implementation.
- Do not promote to canonical until live t5 and pink-twin smokes show both hands protected in `protecthands_*`, both hands black/protected in `mask_*_edit_nohands_*`, then 06 opaque and 06→03 alpha pass.

## Live smoke notes

After user restarted ComfyUI, `/object_info` exposed `VN_AutoHandFallbackProtectionMask` and the t5 candidate ran.

v1 default fallback:

```text
prompt_id: 477bddcb-0e80-4497-af42-9904439de9d7
output folder: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_t5_handfallback
result: rejected — fallback over-masked the lower-right clothing/body region, not only the missed hand.
```

v2 stricter runtime params:

```text
prompt_id: b5dd72f9-4ac8-4ca9-9bf8-59fa1eda05e5
output folder: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_t5_handfallback_v2
params: start_y_ratio=0.76, side_width_ratio=0.30, skin_lum_max=0.76, skin_sat_min=0.13, max_added_coverage=0.006
result: rejected/no-op — fallback added no pixels; original one-hand-only protection remained.
```

Follow-up implementation patch:

```text
VN_AutoHandFallbackProtectionMask now adds a mirror-prior step:
if one side is captured and the opposite lower-side band is missing,
mirror the captured hand mask across the character bbox center and use that as a tight spatial prior before skin-tone fallback.
```

This patch compiled but requires another ComfyUI restart before live testing.

Current offline evidence from t5 existing output:

```text
protecthands component: one component bbox [263,1320,348,1449], area 6254
left lower-side coverage: 3307 px / 2.208%
right lower-side coverage: 0 px / 0.000%
edit_nohands left lower-side editable: 94.668%
edit_nohands right lower-side editable: 100.000%
```

Interpretation: current hand protection captures only one lower-side hand; the opposite side remains fully editable.
