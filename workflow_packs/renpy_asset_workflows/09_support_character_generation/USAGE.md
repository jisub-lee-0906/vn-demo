# 09 support character generation

Status: SMOKE PASS candidate for revised teacher anchor + toonout alpha. Not game-promotion-ready.

Purpose:
- Generate lighter-weight VN support characters such as teacher, friend, clerk, classmate, silhouette NPC.
- This is intentionally lighter than the main heroine pipeline: anchor + optional small expression set + alpha.

Canonical first smoke target:
- young female homeroom teacher
- neutral upper-body/cowboy framing
- simple medium-gray background
- transparent PNG via BiRefNet_toonout

API templates:
- `../api_workflows/09_support_character_anchor_teacher_api.json`
- `../api_workflows/09_support_character_alpha_toonout_api.json`

Required input for alpha:
- Copy selected support source to ComfyUI input as `hermes_support_teacher_SOURCE_TO_PROCESS.png`.

Generation rules:
1. Keep one character only.
2. Do not use `character sheet`, `reference sheet`, `sprite sheet`, or inset wording.
3. Use neutral gray background for alpha extraction.
4. For support characters, make 1 anchor and at most 1-2 expressions before expanding.
5. If the support character becomes story-important, promote them to the full 01-05 character workflow instead of overloading this lightweight route.

PASS for generation workflow candidate:
- role reads clearly at a glance,
- full head/hair visible,
- dialogue-sprite scale is usable,
- no duplicate/inset character,
- neutral background suitable for alpha.

FAIL:
- looks like main heroine clone when a different role is needed,
- too small/full-body/chibi,
- sheet/inset/multiple-view contamination,
- role-defining costume or age is wrong.
