# 04 direct expression happy test

Date: 2026-05-13
Status: executed; sandbox evidence. Promising enough to reconsider whether 03 is needed for simple pose+expression combinations.

## Question

Can workflow 04 generate pose and expression together, so that a separate 03 expression pass is not needed for happy arms-crossed sprites?

## Setup

Source 01:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png`

Pose reference:
`/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png`

Workflow:
`04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json`

Change from current canonical arms_crossed preset:

- Added happy expression tags directly to 04 positive pose block.
- Removed `smile` / `open_mouth` from expression-conflict negatives.
- Added stern-expression negatives: `frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted`.
- Kept OpenPose + masked IPAdapter structure unchanged.

Run folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513`

Manifest:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/manifest_04_direct_expression_happy_test.json`

Script:
`/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows/00_experiment_sandbox/scripts/run_04_direct_expression_happy_test.py`

## Outputs

### Candidate A — mild smile, closed mouth

04 source:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/04_direct_happy_smile_no_openmouth_seed719252501_00001_.png`

02 alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/02_alpha_after_04_direct_happy_smile_no_openmouth_b1_ref1_00001_.png`

Prompt expression tags:
`smile, happy, gentle_smile, soft_smile`

QA:
- Arms-crossed pose works.
- Face reads as clear gentle happy smile.
- Better than previous 04→03 d0.65 result, which stayed stern.
- Outfit/identity are acceptable for this route, though still 04-style regenerated rather than exact 01 preservation.
- 02 output is PNG 1152x1536 RGBA color type 6. Dark preview shows no severe old white sticker rim; minor dark antialias outline only.

### Candidate B — open-mouth happy

04 source:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/04_direct_happy_openmouth_seed719252501_00001_.png`

02 alpha:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/02_alpha_after_04_direct_happy_openmouth_b1_ref1_00001_.png`

Prompt expression tags:
`smile, happy, open_mouth, cheerful`

QA:
- Arms-crossed pose works.
- Face reads as clear happy/open-mouth smile.
- This is the strongest evidence that 04 can perform pose+expression directly.
- Outfit/identity are acceptable for this route, with same caveat: regenerated 04 styling, not pixel-locked 01 identity.
- 02 output is PNG 1152x1536 RGBA color type 6. Dark preview shows no severe old white sticker rim; minor dark antialias outline only.

### Candidate C — mild smile alt seed

04 source:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/04_direct_happy_smile_altseed_seed719252777_00001_.png`

QA:
- Arms-crossed pose works.
- Face reads as happy/gentle smile.
- Different crop/pose feel; useful as seed fallback, but Candidate A/B are enough for the direct-expression proof.

## Conclusion

Direct 04 pose+expression works for happy arms_crossed when `smile/open_mouth` are not suppressed and stern-expression negatives are used.

For simple sprite variants, the chain can likely be simplified from:

`01 -> 04 neutral pose -> 03 expression -> 02 alpha`

to:

`01 -> 04 pose+expression -> 02 alpha`

This does not eliminate 03 completely. 03 may still be useful when:

- reusing the exact same posed body while swapping only face variants,
- needing many expressions from one pose without regenerating clothing/hands/body each time,
- preserving an already-approved 04 body exactly,
- fixing only the face after a good pose output.

But for generating a new pose+expression source from 01, direct 04 is currently the better path than 04→03 for happy arms_crossed.

## Recommended next canonical experiment

Make a sandbox 04 preset table with expression-aware variants:

- `arms_crossed_happy_smile`
- `arms_crossed_happy_openmouth`
- later: `arms_crossed_angry`, `arms_crossed_surprised`, `hand_chest_happy`

Key rule: expression tags requested in positive must not appear in the 04 expression-conflict negatives.
