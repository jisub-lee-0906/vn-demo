# S01 Asset Candidate QA — 2026-05-12

상태: GENERATED_CANDIDATES / NOT PROMOTED

이번 작업은 최종 에셋 승격이 아니라 S01 비주얼 방향 확인용 소량 후보 생성입니다. 모든 PNG/contact sheet는 `generated/` 아래에 있으며 gitignored 상태입니다. Ren'Py semantic asset으로 복사하거나 품질 PASS를 주장하지 않습니다.

## 실행 정보

- ComfyUI endpoint: `http://172.28.224.1:8000`
- Queue state before submit: empty
- Model: `novaAnimeXL_ilV180.safetensors`
- Runner: `tools/generate_s01_asset_candidates.py`
- Run manifest: `generated/comfyui/s01_asset_candidates_2026-05-12/RUN_MANIFEST.json`
- API workflow templates: `generated/comfyui/s01_asset_candidates_2026-05-12/api_workflows/`

## Contact sheets

- Harin design: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/harin_design_candidates_sheet.jpg`
- Summoning hall: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/bg_summoning_hall_candidates_sheet.jpg`
- Measurement orb first batch: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/cg_measurement_orb_candidates_sheet.jpg`
- Measurement orb dark refine: `generated/comfyui/s01_asset_candidates_2026-05-12/contact_sheets/cg_measurement_orb_dark_refine_candidates_sheet.jpg`

## Quick visual QA notes

### `sprite_harin_neutral` / `sprite_harin_suspicious` direction

Second-run contact sheet files: `harin_design_candidates_00005.png` through `00008.png`.

- `00005`: strong audit-officer read, clipboard works, mature enough; white-heavy uniform may feel more formal officer than student council, but it is a good base direction.
- `00006`: best serious side-profile/inspection mood, clean mature tone; side angle is less ideal as the neutral master but useful as a suspicious/inspection pose direction.
- `00007`: less suitable; pose reads softer/younger and the clipboard/framing is less stable for a main sprite.
- `00008`: front-facing and route-friendly, good uniform silhouette; expression is slightly softer/younger, but useful as a neutral master candidate if refined.

Recommended next direction: use `00005` or `00008` as the main visual direction, then regenerate a stricter front-facing neutral/suspicious pair. `00006` can inform the suspicious pose but should not be the first neutral master.

### `bg_summoning_hall`

Second-run contact sheet files: `bg_summoning_hall_candidates_00005.png` through `00008.png`.

- `00005`: strong blue measurement-circle mood, clean no-people read, good ceremony focus. Lower third appears usable but should be checked in Ren'Py with the textbox.
- `00006`: warm and formal, clear platform/circle, no obvious text/people; slightly less distinctive than `00005`.
- `00007`: clean empty hall, but weaker measurement-circle/event identity.
- `00008`: balanced composition with circle and pedestal, clean no-people read, good route background candidate.

Recommended next direction: keep `00005` and `00008` as S01 background direction candidates. Before promotion, pre-scale/copy only one semantic PNG and run actual Ren'Py screenshot QA with dialogue box and Harin sprite.

### `cg_measurement_orb`

First orb batch had strong blue orb visuals but failed the no-text/no-UI requirement in some candidates (`00001`, `00004` showed generated textbox/subtitle contamination), and most candidates did not clearly show the “goes dark / thin golden line” story beat.

Dark-refine contact sheet files: `cg_measurement_orb_dark_refine_candidates_00001.png` through `00004.png`.

- `00001`: clean object read, no fake text/UI; pedestal is strong. Still more glowing than fully dark, but usable direction.
- `00002`: good dark orb mood and ring/crack silhouette; no text/people. Pedestal crop is less elegant but concept is close.
- `00003`: clear dark orb, but blue flame effect may distract from the thin-golden-line requirement.
- `00004`: strongest dark-orb feel and clean close-up, but golden crack is not obvious and crop is tight.

Recommended next direction: use dark-refine `00002` or `00004` as the next prompt/reference direction. Need one more refinement if the script requires a clearly visible thin golden line; otherwise use Ren'Py text to describe the line and keep the CG as the dark measurement device.

## Gate status

- Candidate generation: PASS
- Contact sheets: PASS
- Visual-direction QA: PARTIAL PASS
- Ren'Py semantic asset promotion: NOT STARTED
- Ren'Py screenshot QA: NOT STARTED
- Final art quality claim: NOT ALLOWED YET

## Next recommended step

1. Ask user to choose Harin direction between `00005`, `00008`, and optionally `00006` as suspicious-pose influence.
2. Generate a stricter front-facing Harin neutral master from the chosen direction.
3. Run BiRefNet/alpha QA only after a source sprite is selected.
4. Promote one selected `bg_summoning_hall` candidate into a temporary semantic Ren'Py path and run screenshot QA with text box.
5. Refine `cg_measurement_orb` once more if the golden-line beat must be visible in the image itself.
