# VN auburn workflow final inspection and folder cleanup checklist

Updated: 2026-05-12

Purpose: final pass before treating `vn_auburn_workflows_2026-05-12` as a clean reusable Ren'Py/ComfyUI template pack.

Scope rule:
- This pack is a reusable workflow/template pack, not an image archive.
- Keep replayable API JSON, usage docs, manifests, QA verdicts, and tiny proof/QA references only when they explain a PASS/FAIL decision.
- Generated bulk outputs should live in ComfyUI `output/`, not inside the backup pack.
- Smoke PASS is not the same as game promotion. Ren'Py screenshot QA remains a separate later stage.

## 0. Pre-check

- [ ] Confirm backup root:
  - Windows: `C:\Users\Desktop\Documents\ComfyUI\workflow_packs\renpy_asset_workflows`
  - WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`
- [ ] Confirm ComfyUI output references are external, mainly under:
  - `C:\Users\Desktop\Documents\ComfyUI\output\...`
- [ ] Do not delete current ComfyUI output artifacts unless explicitly doing output cleanup, because docs point to those paths.

## 1. Core document sanity

Required root docs:
- [ ] `README.md`
- [ ] `TEMPLATE_INTENT.md`
- [ ] `CANONICAL_WORKFLOW_POLICY.md`
- [ ] `CANONICAL_PROMPTING_GUIDE.md`
- [ ] `CLEANUP_POLICY.md`
- [ ] `CURRENT_STATUS_AND_GAPS.md`
- [ ] `NEXT_ASSET_WORKFLOWS.md`
- [ ] `FINAL_PACK_MANIFEST.json`
- [ ] `WORKFLOW_FINAL_INSPECTION_AND_FOLDER_CLEANUP_CHECKLIST.md`

Check:
- [ ] Root docs no longer say 09/10/11 are untested scaffolds without the later smoke updates.
- [ ] Root docs clearly distinguish:
  - generation/template smoke PASS,
  - not-yet Ren'Py/game promoted,
  - optional/deferred work.
- [ ] No stale statement says 10 outfit is still the main remaining workflow.
- [ ] No stale statement says 11 key/prop is still failed after the minimal retry.

## 2. API template index sanity

Files:
- [ ] `api_workflows/README.md`
- [ ] `api_workflows/API_TEMPLATE_INDEX.json`

Checks:
- [ ] `API_TEMPLATE_INDEX.json` parses as JSON.
- [ ] Every file listed in `API_TEMPLATE_INDEX.json.templates[].file` exists under `api_workflows/`.
- [ ] Every API JSON under `api_workflows/` is either listed in the index or intentionally documented as deprecated/negative lesson.
- [ ] Status labels are current:
  - [ ] 01-05: canonical/pass direction as appropriate.
  - [ ] 06: smoke PASS no-text background baseline.
  - [ ] 07: smoke PASS rain/weather variation; not day/night conversion.
  - [ ] 08: smoke PASS event CG candidate; Ren'Py route QA pending.
  - [ ] 09: smoke PASS teacher support-character candidate.
  - [ ] 10: user-accepted complete as PuLID+i2i outfit direction.
  - [ ] 11 key: original over-constrained key template marked negative lesson.
  - [ ] 11 key minimal: smoke PASS preferred route.
  - [ ] 11 magic shimmer: smoke PASS effect overlay.
  - [ ] 12-14: documented audio scaffolds, not ComfyUI API templates.

## 3. Workflow folder-by-folder inspection

### 01 character anchor
- [ ] `USAGE.md` exists.
- [ ] Selected anchor seed/settings are documented.
- [ ] API template exists and is indexed.
- [ ] No bulk generated image archive is stored inside backup.

### 02 transparency alpha
- [ ] `USAGE.md` exists.
- [ ] Best alpha setting is documented: `BiRefNet_toonout`, `mask_offset=0`, `mask_blur=0`, `refine_foreground=false` for auburn/high-contrast hair.
- [ ] API template exists and is indexed.
- [ ] Halo/Ren'Py QA caveat remains visible.

### 03 expression variation
- [ ] `USAGE.md` exists.
- [ ] smile/surprised/sad/angry source and alpha templates exist and are indexed.
- [ ] Denoise/IPAdapter setting differences are documented.
- [ ] Ren'Py scale/readability caveat remains visible.

### 04 pose donor generation
- [ ] `USAGE.md` exists.
- [ ] hand-to-chest, one-hand-on-hip, arms-crossed donors are documented.
- [ ] pointing weakness is documented.
- [ ] API templates exist and are indexed.

### 05 pose image-reference regeneration
- [ ] `USAGE.md` exists.
- [ ] Replaces old post-alpha composite direction.
- [ ] Best setting `denoise=0.42`, `IPAdapter weight=0.60` documented.
- [ ] Caveat remains: not final until Ren'Py screen-fit/hand/edge QA.

### 06 background generation
- [ ] `USAGE.md` exists.
- [ ] Minimal no-text prompt documented.
- [ ] `novaAnimeXL_ilV180.safetensors` baseline documented.
- [ ] Day/night rule documented: use separate 06 base generations, not 07 conversion.
- [ ] Ren'Py textbox/sprite screenshot QA caveat remains.

### 07 background weather variation
- [ ] `USAGE.md` exists.
- [ ] Rain/weather variation scope documented.
- [ ] Day/night conversion explicitly excluded.
- [ ] Canny/lineart ControlNet + SDXL Union smoke PASS settings documented.

### 08 event CG
- [ ] `USAGE.md` exists.
- [ ] Sealed-envelope/hallway hook smoke PASS documented.
- [ ] Fake text/UI/person/hands/blood screening documented.
- [ ] Exact under-door geometry caveat documented.
- [ ] Ren'Py route screenshot QA pending.

### 09 support character
- [ ] `USAGE.md` exists.
- [ ] Teacher source and alpha smoke PASS documented.
- [ ] Not game-promotion-ready caveat remains.
- [ ] API templates exist and are indexed.

### 10 outfit/costume variation
- [ ] `USAGE.md` status says user-accepted complete for current template scope.
- [ ] Plain IPAdapter i2i failure remains as negative lesson.
- [ ] Masked inpaint partial direction remains as lesson, not default.
- [ ] PuLID+i2i is documented as accepted practical route.
- [ ] 10-variant outfit diversity batch is documented.
- [ ] Black leather/revealing output is explicitly rejected.
- [ ] Final game promotion caveat remains: select exact outfit, alpha, Ren'Py QA.
- [ ] API templates for selected/lesson routes are indexed.

### 11 effect / prop overlay
- [ ] `USAGE.md` status says smoke PASS after minimal prop retry.
- [ ] Original key route failure is preserved as negative lesson: plate/box/background contamination.
- [ ] Minimal key prompt is documented.
- [ ] `11_prop_single_object_key_minimal_api.json` exists and is indexed.
- [ ] Preferred key candidate seed `61124024` documented.
- [ ] Alternate key seed `61124021` documented.
- [ ] QA sheet path documented.
- [ ] Magic shimmer black-background effect remains PASS candidate.
- [ ] Game promotion/Ren'Py placement caveat remains.

### 12 SFX generation
- [ ] `USAGE.md` exists.
- [ ] `sfx_taxonomy.md` exists.
- [ ] `scripts/generate_ui_sfx.py` exists.
- [ ] Prototype `.wav`/`.ogg` files are either intentionally kept as tiny examples or documented as removable examples.
- [ ] Manifest says prototypes are not final listened/mastered audio.

### 13 BGM generation
- [ ] `USAGE.md` exists.
- [ ] `bgm_prompt_templates.md` exists.
- [ ] Backend not selected caveat remains.

### 14 audio packaging and looping
- [ ] `USAGE.md` exists.
- [ ] `audio_manifest_template.json` exists and parses.
- [ ] Looping/normalization/package intent documented.

## 4. Artifact policy check

Keep:
- [ ] `USAGE.md` in every workflow folder.
- [ ] `api_workflows/*.json` replay templates.
- [ ] `artifacts/*manifest*.json` and small verdict JSON/MD files.
- [ ] QA sheets only when they are direct evidence for a documented PASS/FAIL decision.
- [ ] Scripts/templates needed to reproduce workflow behavior.

Remove or consider removing:
- [ ] `__pycache__/`
- [ ] `.pyc` files
- [ ] stale `backup_manifest*.json` snapshots if superseded by `FINAL_PACK_MANIFEST.json`
- [ ] temporary scratch outputs copied into backup by accident
- [ ] duplicate/generated PNGs inside backup that are not referenced by docs
- [ ] test-run directories that no longer explain a kept verdict

Do not remove without explicit decision:
- [ ] Current ComfyUI `output/` artifacts referenced by docs.
- [ ] Source images required as `LoadImage` inputs unless docs say they are external prerequisites.
- [ ] Tiny SFX prototype files if they are intentionally kept as packaging examples.

## 5. JSON and path validation

Run/verify:
- [ ] `FINAL_PACK_MANIFEST.json` parses.
- [ ] `api_workflows/API_TEMPLATE_INDEX.json` parses.
- [ ] All `api_workflows/*.json` parse.
- [ ] `14_audio_packaging_and_looping/audio_manifest_template.json` parses.
- [ ] No Windows path strings accidentally use WSL-only paths for user-facing docs unless both are provided.
- [ ] No doc points to removed backup-internal generated images.

Suggested command from WSL:

```bash
cd /mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows
python3 - <<'PY'
import json, pathlib
root=pathlib.Path('.')
for p in [root/'FINAL_PACK_MANIFEST.json', root/'api_workflows/API_TEMPLATE_INDEX.json', root/'14_audio_packaging_and_looping/audio_manifest_template.json'] + sorted((root/'api_workflows').glob('*.json')):
    json.load(open(p, encoding='utf-8'))
print('JSON parse PASS')
PY
```

## 6. Status truth-sync checklist

The final pack should truthfully say:
- [ ] 01-05 character/sprite workflows are replay-template/canonical direction complete, but not necessarily game-promoted.
- [ ] 06-08 are smoke-passed generation templates.
- [ ] 09 support character smoke-passed.
- [ ] 10 outfit is user-accepted complete as PuLID+i2i direction.
- [ ] 11 minimal key prop smoke-passed.
- [ ] 11 magic shimmer effect smoke-passed.
- [ ] 12 SFX has procedural prototype artifacts, not final audio production.
- [ ] 13 BGM backend is not selected.
- [ ] 14 audio packaging is a template/scaffold.
- [ ] Remaining major work is game integration: Ren'Py screen-fit QA, semantic asset promotion, sprite/background/UI screenshot QA.

## 7. Folder cleanup execution checklist

Before deletion:
- [ ] Make a dry-run file list of deletion candidates.
- [ ] Check whether each candidate is referenced by any `.md`/`.json` file.
- [ ] If referenced, either keep it or update the reference first.
- [ ] Prefer moving uncertain files to a temporary `_cleanup_review/` folder before permanent deletion.

Deletion candidates to inspect:
- [ ] `*/__pycache__/`
- [ ] `*.pyc`
- [ ] stale verification snapshots superseded by final manifest
- [ ] abandoned scratch contact sheets not referenced by docs
- [ ] duplicate API templates that are neither indexed nor documented as negative lessons

After cleanup:
- [ ] Re-run JSON parse validation.
- [ ] Re-run index-vs-files validation.
- [ ] Re-run doc reference grep for deleted filenames.
- [ ] Update `FINAL_PACK_MANIFEST.json` counts if file count/bytes changed materially.
- [ ] Update this checklist status or add a short cleanup manifest.

## 8. Final acceptance checklist

The folder can be considered clean when:
- [ ] A future no-memory session can understand the workflow sequence from docs alone.
- [ ] Every runnable API template is indexed with purpose, inputs, and status.
- [ ] Negative lessons are clearly labeled and not mistaken for preferred workflows.
- [ ] No bulk image archive is mixed into the reusable template pack.
- [ ] Remaining work is framed as Ren'Py/game QA, not unfinished ComfyUI generation-template work.
