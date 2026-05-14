# v4f prompt-knowledge extraction for 06 outfit canonical

Source: `workflow_packs/docs/noobai-generation-guide.md` plus direct probes of linked Civitai pages on 2026-05-15.

Key points to apply cautiously to `novaAnimeXL_ilV190.safetensors` 06 outfit inpaint:

- Nova/Illustrious/NoobAI family should prefer Danbooru-style comma-separated tags, lowercase, ordered by generation logic.
- Recommended generation baseline from Crody: Euler a, CFG 3.0-5.0 (practical 4.5), around 20 steps. Current 06 uses Euler ancestral but CFG 6.0 / 28 steps because it is a masked inpaint route; test lower CFG before canonical change.
- Long vanilla CLIP prompts can degrade beyond the 75/77-token region. Current 06 positive+negative are long and no ADV_CLIP node is present, so shorter conflict-free prompts are a plausible improvement.
- For inpainting, prompt should describe the edited region more than the whole character. Since 06 composites original head/hair/hands back, prioritize outfit/body/pose tags and avoid over-constraining face/hair in the inpaint prompt.
- Negative prompt must not contain target outfit tags. Current canonical negative accidentally includes `lavender_hoodie, hoodie, hood, drawstring, pullover_hoodie` in the base negative, which conflicts with the hoodie preset and can weaken cuff/hoodie generation.
- Avoid broad negative overload where possible; put specific old outfit conflict tags first, then generic image-quality/anatomy/text terms.
- Keep `grey_background` positive for this workflow. Avoid `simple_background` in negative if it conflicts with plain/grey background goals; current README and earlier 04/01 tests also warn about background-tag conflicts.

v4f test hypothesis:

1. Remove target hoodie tags from negative prompt.
2. Shorten negative prompt and remove duplicates.
3. Keep Danbooru target outfit tags top-to-bottom.
4. Test CFG 4.5 while retaining denoise 0.92 and 28 steps, because mask/composite route is already stable and the first variable should be prompt/CFG conflict reduction, not mask code.

Promotion criteria remains visual, not theory: t5 + pink01 must pass fullfit/foregroundcut/hand-cuff/mask QA without hoodie overcut, old cuff sliver, or hand damage.
