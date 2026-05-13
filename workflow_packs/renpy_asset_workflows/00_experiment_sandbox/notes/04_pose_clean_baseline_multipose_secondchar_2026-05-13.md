# 00 experiment — 04 clean baseline multi-pose and second-character smoke

Date: 2026-05-13
Status: executed; clean masked-IPAdapter OpenPose baseline generalizes across multiple poses and a second character, with remaining color/style drift.

## Baseline under test

```text
Checkpoint: novaAnimeXL_ilV190.safetensors
Latent: EmptyLatentImage 1152x1536
Sampler: euler_ancestral, normal, 28 steps, cfg 5.0, denoise 1.0
Pose: OpenposePreprocessor -> SDXL Union ControlNet type=openpose
ControlNet strength: 1.0, start 0.0, end 0.8
Identity/style: IPAdapterAdvanced with character attn_mask from BiRefNet, weight 0.65, style transfer, end_at 0.75
PuLID: disabled
Prompt: clean Danbooru tags; no dark_background/depth_of_field/volumetric_lighting in positive; negative bans dark/vignette/dramatic lighting.
```

## Silver-bob multi-pose batch

Input identity:

```text
ComfyUI/input/hermes_identity_silver_bob_anchor_v190.png
```

Pose refs:

```text
ComfyUI/input/hermes_pose_ref_silver_bob_arms_crossed.png
ComfyUI/input/hermes_pose_ref_silver_bob_pointing.png
ComfyUI/input/hermes_pose_ref_multi04b_silver_bob_hand_chest.png
ComfyUI/input/hermes_pose_ref_merge04_one_hand_hip.png
```

Outputs/contact sheets:

```text
ComfyUI/output/hermes_vn_pose_clean_multi_pose/contact_batch1_clean_multi_pose_outputs.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/contact_batch1_clean_multi_pose_controls.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/batch1_manifest.json
```

Individual outputs:

```text
ComfyUI/output/hermes_vn_pose_clean_multi_pose/arms_crossed_clean_ip065_cn100_seed719252601_00001_.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/pointing_clean_ip065_cn100_seed719252602_00001_.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/hand_chest_clean_ip065_cn100_seed719252603_00001_.png
ComfyUI/output/hermes_vn_pose_clean_multi_pose/one_hand_hip_clean_ip065_cn100_seed719252604_00001_.png
```

Prompt IDs:

```text
arms_crossed: 4a462977-8742-4527-889c-78b2591deb2f
pointing: 9ac3c08f-b21a-48a3-bfc9-f8cbcab40d58
hand_chest: 2313ccdd-aa35-4b63-ac13-3cbdb4078852
one_hand_hip: 209f6c64-4d8b-4497-9637-032f21d975c8
```

### Silver-bob QA

- `arms_crossed`: pass. Pose clear, identity/outfit readable, clean background. Similar to previous best.
- `pointing`: pass with caution. Pose is readable and hand points forward. Identity/hair/outfit preserved enough, but hand is large and color saturation is higher.
- `hand_chest`: pass. Gesture is readable, identity/outfit stable, clean background.
- `one_hand_hip`: pass with caution. Pose readable, but outfit/line color drift is stronger and silhouette is more stylized. Use as a weaker pass, not the best demonstration case.

OpenPose controls were valid for all four. The one-hand-hip control came from a different donor character but still transferred pose without donor hair contamination because only OpenPose conditioning was used.

## Second-character batch — pink twin-braids

Input identity:

```text
ComfyUI/input/hermes_identity_multi04b_pink_twinbraids.png
```

Pose refs:

```text
ComfyUI/input/hermes_pose_ref_multi04b_pink_twinbraids_arms_crossed.png
ComfyUI/input/hermes_pose_ref_multi04b_pink_twinbraids_pointing.png
ComfyUI/input/hermes_pose_ref_multi04b_pink_twinbraids_hand_chest.png
```

Outputs/contact sheets:

```text
ComfyUI/output/hermes_vn_pose_clean_second_character/contact_batch1_second_character_outputs.png
ComfyUI/output/hermes_vn_pose_clean_second_character/contact_batch1_second_character_controls.png
ComfyUI/output/hermes_vn_pose_clean_second_character/batch1_manifest.json
```

Individual outputs:

```text
ComfyUI/output/hermes_vn_pose_clean_second_character/pink_arms_crossed_clean_ip065_cn100_seed719252701_00001_.png
ComfyUI/output/hermes_vn_pose_clean_second_character/pink_pointing_clean_ip065_cn100_seed719252702_00001_.png
ComfyUI/output/hermes_vn_pose_clean_second_character/pink_hand_chest_clean_ip065_cn100_seed719252703_00001_.png
```

Prompt IDs:

```text
pink_arms_crossed: 7eeffcd2-ab36-4e55-996a-7697ce92627d
pink_pointing: 939bc013-3d2d-4431-915f-5e9555bb6f33
pink_hand_chest: 09cca3c1-8369-41dd-bd4a-e454a8ebb7b6
```

### Pink twin-braids QA

- `arms_crossed`: pass. Pose clear, pink twin-braid identity preserved. Outfit colors shift brighter/saturated, but recognizable.
- `pointing`: pass with caution. Gesture is readable, but arm/hand is large and outfit becomes brighter blue; still a usable route smoke.
- `hand_chest`: pass. Gesture readable, hair/identity retained, outfit recognizable, clean background.

OpenPose controls were valid for all three.

## Current conclusion

The clean prompt + masked IPAdapter + OpenPose baseline is now a real 04 candidate. It successfully transfers multiple poses and generalizes to a second character.

Remaining weaknesses:

1. Pointing poses can produce large/overemphasized hands.
2. Outfit color saturation can drift brighter, especially blue skirt/sailor colors.
3. One-hand-hip works but has stronger style/line drift than arms-crossed/hand-chest.
4. This is still not exact outfit pixel preservation; it is a pose-regeneration route.

## Next recommended gates

1. Run 02 alpha smoke on accepted outputs, preferably:

```text
silver arms_crossed
silver hand_chest
pink arms_crossed
pink hand_chest
```

2. If alpha passes, promote a clean 04 canonical API using the baseline settings and README preset table for pose-specific positive/negative tag swaps.

3. Keep pointing and one-hand-hip as supported-but-cautious presets. If production needs them, test a low-strength hand/anatomy fix or generate multiple seeds per pose.

4. Do not reintroduce PuLID, full-strength Canny, or dirty lighting tags into the canonical candidate.
