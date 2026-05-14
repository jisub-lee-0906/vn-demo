# 06 outfit handgrow2 candidate — 2026-05-14

Purpose: test whether 06 hand/wrist/cuff artifacts come from over-protecting the hand mask boundary before final original-hand composite.

Base: `06_outfit_costume_variation/workflow_api/06_outfit_pulid_i2i_canonical_api.json`

Single graph change:

```text
node 50 GrowMask.expand: 5 -> 2
```

Runtime smoke input:

```text
ComfyUI/input/hermes_identity_multi04b_pink_twinbraids.png
```

ComfyUI prompt IDs:

```text
exp15 handgrow10: bf635a17-c289-4ac7-8b9d-429b53d68dfc
exp16 handgrow2: 49009bef-6e05-4019-9f77-ab271d03ee80
exp16 03 alpha: 4bf131af-226f-4637-8009-275b695255cb
```

Key outputs:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_variation/contact_exp14_vs_exp16_handgrow2.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_variation/crop_exp14_vs_exp16_wrists_hands.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_variation/exp16_handgrow2_pinktwin_lavenderhoodie_final_autoclean_seed62018571_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_alpha_gate/alpha_exp16_handgrow2_pinktwin_lavenderhoodie_00001_.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_alpha_gate/contact_alpha_exp16_light_dark.png
```

Findings:

- `expand=10` did not improve the wrist/cuff seam and made sleeve generation more constrained.
- `expand=2` kept hands/fingers intact while allowing more cuff/sleeve detail near wrists.
- 03 alpha smoke on the exp16 final had no severe halo/rim at review scale.
- This is a candidate, not canonical promotion. Before changing canonical node 50, run at least one new-character 01 -> 06 -> 03 smoke and user visual QA.


## Second-character t5 smoke

01 source generated from canonical 01:

```text
prompt_id: 28fca6c7-92d0-479c-b680-e48f1374c6d7
source: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_character_anchor/t5_green_glasses_01_seed719260141_00001_.png
```

06 handgrow2 run:

```text
prompt_id: 27b95730-d965-4819-95a2-5a95d3aecd9f
active-chain sheet: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_t5/contact_t5_green_06_handgrow2_active_chain.png
final: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_t5/t5_green_glasses_handgrow2_lavenderhoodie_final_autoclean_seed62019141_00001_.png
```

03 alpha gate:

```text
prompt_id: 00386ccc-f41a-49b6-a4ac-d93b68cddb95
alpha: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_alpha_gate/alpha_t5_green_glasses_handgrow2_lavenderhoodie_00001_.png
light/dark sheet: /mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_alpha_gate/contact_alpha_t5_green_handgrow2_light_dark.png
```

Findings:

- Hand/wrist/cuff handling stayed stable on the second character; no obvious hand breakage from reducing hand GrowMask to 2.
- 03 alpha edge gate passed at review scale.
- The main remaining blocker was a black bow/ribbon-like remnant at the neck/chest in the 06 opaque final. This is upstream 06 content, not an alpha problem. The current `VN_AutoCollarCleanupMask(mode=blue_bow_only)` did not remove it, so cleanup/prompt/mask handling needs a separate one-variable investigation before canonical promotion.
