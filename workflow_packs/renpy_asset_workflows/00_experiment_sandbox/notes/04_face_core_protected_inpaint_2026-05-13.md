# 04 face-core protected inpaint test — 2026-05-13

Purpose: test the middle route after full-character inpaint failed identity preservation and alpha-minus-head had a mild head/body seam.

Route:
- source: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png`
- pose: `/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png`
- alpha mask source: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png`
- base graph: alpha-minus-head inpaint graph, but change protection from `head OR hair OR face` to smaller face-core/front-hair protection.
- edit mask: `grow(character alpha, 28) - protected face/core`, then blur/grow and composite back onto the original source.

Run folder:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_face_core_protected_inpaint_20260513`

Contact sheet:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_face_core_protected_inpaint_20260513/contact_face_core_protected_inpaint.png`

Manifest:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_face_core_protected_inpaint_20260513/manifest_face_core_protected_inpaint.json`

Variants:

| slug | protection | denoise | result |
|---|---:|---:|---|
| `face_o08_g28_d88_s291` | face, offset 8 | 0.88 | readable arms-crossed and integrated neck/body, but face/hair drift is obvious. |
| `face_o14_g28_d88_s291` | face, offset 14 | 0.88 | similar; slightly more protected face area, still hair/identity drift. |
| `face_o20_g28_d88_s291` | face, offset 20 | 0.88 | face area protected more, but hair/upper head still redraws too much; not 01-faithful. |
| `face_bangs_o12_g28_d88_s291` | face + bangs/front hair | 0.88 | best middle-route balance; readable pose and better hair silhouette than face-only, but still does not match original 01 look closely enough for promotion. |
| `face_o14_g28_d82_s291` | face, offset 14 | 0.82 | lower denoise preserves slightly more but pose/body result is not a clear improvement; still not production-ready. |

Conclusion:
- The middle route confirmed the expected tradeoff: allowing neck/shoulders/collar/body to regenerate together improves cohesion, but once hair/head area is not strongly protected, Nova redraws too much of the 01 look.
- `face_bangs_o12_g28_d88_s291` is the best from this run, but it still does not beat the previous alpha-minus-head best for original 01 identity/fidelity.
- Do not promote face-core protected route as canonical yet.

Current best remains:
`/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254291_00001_.png`

Recommended next route:
- Return to head/hair/face protection for identity.
- Instead of freeing the whole head/hair, do a second, very local neck/shoulder/collar cleanup pass on the current best, with a small mask around collar/neck seam only.
- Keep the face and hair fully untouched; do not ask the model to redraw the upper head again.
