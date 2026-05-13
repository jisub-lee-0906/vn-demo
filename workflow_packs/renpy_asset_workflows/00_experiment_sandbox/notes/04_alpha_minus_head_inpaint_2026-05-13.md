# 04 alpha-minus-head body inpaint test — 2026-05-13

Purpose: test and refine the user-proposed route: start from a transparent 02 sprite, use its alpha as the character silhouette, protect the head/hair/face with Florence-2, subtract that protection inside/near the alpha, and inpaint the remaining body for `arms_crossed`.

## Inputs

```text
RGB source 01:
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png

Transparent alpha source for character silhouette:
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png

Pose reference:
/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png
```

## Mask formula

Base:

```text
head_protect = dilate/blur(Florence(head) OR Florence(hair) OR Florence(face))
edit_mask = alpha(character silhouette from transparent 02) - head_protect
```

Best current practical variant:

```text
edit_mask = grow(alpha(character silhouette), 28px) - dilated(Florence head/hair/face)
final mask: small post-subtract grow + hard-ish blur
```

Important: do not use a full-image inverse head mask. The edit mask must be constrained by the character alpha/grown-alpha so the background is not broadly regenerated.

## Runs and contact sheets

Initial denoise/grow test:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_inpaint_20260513/contact_alpha_minus_head_inpaint.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_inpaint_20260513/contact_alpha_minus_head_inpaint_expanded_compare.png
```

Grow/denoise refinement sweep:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_sweep2_20260513/contact_alpha_minus_head_sweep2.png
```

Upper-clipped mask test:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_upperclip_20260513/contact_upperclip.png
```

Seed hunt:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/contact_seedhunt.png
```

02 alpha gate:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_02_gate_20260513/contact_02_light_dark_candidates.png
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_02_gate_20260513/contact_02_seed291_vs_292.png
```

## Scripts

```text
00_experiment_sandbox/scripts/run_04_alpha_minus_head_inpaint.py
00_experiment_sandbox/scripts/run_04_alpha_minus_head_sweep2.py
00_experiment_sandbox/scripts/run_04_alpha_minus_head_upperclip.py
00_experiment_sandbox/scripts/run_04_alpha_minus_head_seedhunt.py
00_experiment_sandbox/scripts/run_02_after_04_alpha_minus_head_gate.py
```

## Main findings

### Initial alpha-minus-head

- Technically works: head/hair/face remained original-looking; body regenerated into crossed arms.
- Plain `alpha - head` left faint old side-arm/side-hand ghosting because the edit mask stayed too close to the original A-pose silhouette.
- Growing the alpha silhouette outward before subtracting head protection solved most side-hand remnants.

### Grow/denoise refinement

Tested grow 16/24/28/32 and denoise 0.86/0.88/0.90.

- Lower grow values preserve the old silhouette more but risk side ghost lines.
- Grow 32 removes side ghosts strongly but slightly increases body/outfit redraw.
- Grow 28 at denoise 0.88 gave the best balance in the second sweep: clear crossed arms, little/no old side-hand ghost after 02, and slightly less aggressive body redraw than grow 32 d90.

### Upper-clipped mask test

Attempted to clip the edit mask below y=1180/1240/1320 to preserve skirt/legs.

Result: reject. Clipping the lower mask preserved parts of the original lower body, but also preserved the original A-pose hands at skirt level, causing obvious side hands. This route is not viable unless paired with separate hand-specific cleanup masks.

### Seed hunt

Using current best settings (`grow(alpha)=28`, `denoise=0.88`), tested seeds 719254291-719254296.

- 719254291: safest/cleanest overall; balanced arms, cardigan, skirt, and 02 edge.
- 719254292: also good; slightly stronger/larger crossed arms, acceptable 02 edge; may read a bit bulkier.
- 719254293: usable but less balanced body/arms.
- 719254294: reject due to skirt/detail drift (white stripe-like artifacts).
- 719254295: usable but cardigan/button line/body drift stronger.
- 719254296: reject/weak due to framing/body balance drift.

### 02 alpha gate

Ran canonical 02 ToonOut alpha on top candidates and composited onto white/dark backgrounds.

Results:

- `g28_d88_seed719254291` passes first 02 edge smoke: no severe halo/rim, no obvious old side-hand after alpha, hair edges acceptable.
- `g28_d88_seed719254292` also passes first 02 edge smoke and is a close alternate.
- Earlier `g32_d90` and `g24_d90` are technically okay after 02, but g28/d88 is the better balance.

## Current best candidate

Primary:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254291_00001_.png
```

02 alpha output:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_02_gate_20260513/alpha_g28_d88_b1_ref1_00001_.png
```

02 light/dark preview:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_02_gate_20260513/preview_g28_d88_white_dark.png
```

Close alternate:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254292_00001_.png
```

02 alpha output:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_alpha_minus_head_02_gate_20260513/alpha_seed719254292_b1_ref1_00001_.png
```

## Current conclusion

This branch is now the best 04 preservation-first pose-change route tested so far.

It solves the prior major failure better than the rectangular/wide mask route:

```text
old problem: readable arms crossed, but obvious side/old hands
new result: readable arms crossed, head/hair preserved, side/old hands mostly gone, 02 alpha edge smoke passes
```

Remaining imperfection: the torso/cardigan/skirt are still regenerated rather than pixel-faithfully preserved. That is expected because arms-crossed necessarily replaces most of the upper body. The next quality ceiling likely requires either:

1. a second localized cleanup/details pass on the selected candidate, or
2. manual/Krita mask correction for outfit details, then SD seam repair, or
3. accepting a generated-body route for 04 pose while preserving only head/hair/identity exactly.

Do not promote to canonical until user visual QA accepts the outfit/body drift and at least one second-character smoke passes.
