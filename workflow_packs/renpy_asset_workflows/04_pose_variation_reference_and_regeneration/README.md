# 04 — 포즈 variation: reference 생성 + 캐릭터 재생성

Category: `character`

## Purpose

기준 캐릭터 anchor를 유지하면서 VN sprite용 포즈 variation source를 만든다.

04는 두 단계를 한 폴더에서 관리한다.

```text
A. pose donor/source 생성        = 포즈 참고 이미지가 없을 때만 사용
B. same-character pose refgen    = 실제 캐릭터 포즈 변경 본체
```

투명 PNG가 필요하면 최종 source를 02 alpha workflow로 후처리한다.

## Output

- pose donor/source PNG 후보
- same-character pose source PNG 후보
- 최종 Ren'Py 투명 PNG는 02 alpha workflow output

## API templates

- `workflow_api/04_pose_textonly_source_canonical_api.json`
  - role: text-only pose donor/source generation
  - use when: 원하는 포즈 reference가 없을 때
  - input: none
  - output node: `SaveImage.filename_prefix`
  - status: canonical template from archived text-only pose variants

- `workflow_api/04_pose_refregen_ipadapter_canonical_api.json`
  - role: same-character pose regeneration from pose reference + character anchor
  - use when: 04 donor 또는 외부 pose reference를 기존 캐릭터로 재생성할 때
  - pose reference node: `LoadImage.image = TEMPLATE_pose_reference.png`
  - character anchor node: `LoadImage.image = TEMPLATE_character_anchor.png`
  - output node: `SaveImage.filename_prefix`
  - status: canonical template from archived 05 ref-generation variants

## Role in the pack

```text
01 = 캐릭터 기준 anchor 생성
02 = source 이미지를 Ren'Py용 투명 PNG로 변환
03 = 표정 source variation 생성
04 = 포즈 donor 생성 + 같은 캐릭터 포즈 재생성
```

04는 source PNG 생성까지만 담당한다. alpha workflow는 중복 유지하지 않고 02를 기본으로 사용한다.

## When to use which workflow

| Situation | Use | Judge |
|---|---|---|
| 원하는 포즈 reference가 없다 | `04_pose_textonly_source_canonical_api.json` | 포즈가 읽히는지만 확인 |
| 이미 좋은 포즈 reference가 있다 | `04_pose_refregen_ipadapter_canonical_api.json` | 캐릭터 일관성 + 포즈 확인 |
| 04 donor를 기존 캐릭터로 바꾸고 싶다 | `04_pose_refregen_ipadapter_canonical_api.json` | 얼굴/헤어/의상/손/팔 확인 |
| 투명 PNG가 필요하다 | `../02_toonout_transparency_alpha/` | edge/halo/잘림 확인 |

## What the agent should edit

### Text-only pose donor workflow

기본 생성에서는 아래 항목만 수정한다.

1. positive prompt의 character block
2. positive prompt의 pose block
3. negative prompt의 pose-conflict block
4. seed
5. `SaveImage.filename_prefix`

보통 node 구조, checkpoint, 해상도는 바꾸지 않는다. 구조 변경 실험은 새 JSON으로 저장하거나 archive에 별도 보관한다.

### Same-character pose refgen workflow

기본 생성에서는 아래 항목만 수정한다.

1. pose reference `LoadImage.image`
2. character anchor / identity `LoadImage.image`
3. positive prompt의 character block
4. positive prompt의 pose block
5. negative prompt의 pose-conflict block
6. `KSampler.denoise`
7. `IPAdapterAdvanced.weight`
8. `SaveImage.filename_prefix`
9. seed

사용자 QA 후에만 아래 고급 항목을 한 변수씩 조정한다.

10. `KSampler.cfg`
11. `KSampler.steps`
12. `IPAdapterAdvanced.end_at`
13. sampler

## Input rules

ComfyUI input 폴더 기준:

```text
ComfyUI/input/{filename}.png
```

WSL 경로:

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/input/{filename}.png
```

권장 input naming:

```text
hermes_pose_ref_{pose_slug}.png
hermes_identity_{character_slug}_anchor.png
```

`04_pose_refregen_ipadapter_canonical_api.json`의 template filename은 실행 전에 실제 파일명으로 교체한다.

```text
TEMPLATE_pose_reference.png
TEMPLATE_character_anchor.png
```

## Pose presets

하나의 canonical workflow를 사용하고, 포즈별 차이는 prompt block과 filename prefix만 바꾼다.

| Pose slug | Korean label | Positive pose block | Negative pose-conflict additions | Use when |
|---|---|---|---|---|
| `arms_crossed` | 팔짱 | `arms crossed, crossed arms, both arms folded across chest, readable folded arms pose, natural elbows, sleeves visible` | `hands clasped together, prayer hands, one hand on hip, hand on chest, arms relaxed down, extra arms, fused arms` | 방어적/화난/자신감 있는 standing sprite |
| `one_hand_hip` | 한 손 허리 | `one hand on hip, hand-on-hip pose, other arm relaxed at side, confident standing pose, readable gesture, natural elbow` | `arms crossed, both hands on chest, hands clasped together, prayer hands, both arms folded, extra arms` | 당당한 대화/장난스러운 반응 |
| `hand_chest` | 손 가슴 위 | `right hand touching chest, hand on chest pose, left hand relaxed at side, shy modest gesture, readable hand-to-chest gesture` | `arms crossed, one hand on hip, hands clasped together, prayer hands, both hands on chest, fingers touching in front of face` | 놀람/부끄러움/진심 고백 |
| `arms_relaxed` | 기본 팔 내림 | `both arms relaxed at sides, relaxed neutral standing pose, open readable silhouette, hands visible` | `arms crossed, hand on hip, hand on chest, hands clasped, hidden hands` | 01 A-pose보다 자연스러운 기본 standing pose |
| `pointing` | 손가락으로 가리킴 | `one hand pointing to the side, clear pointing gesture, other arm relaxed, visible index finger, natural wrist` | `arms crossed, hand on hip, hands clasped, hidden hands, extra fingers, fused fingers` | 설명/지적/선택지 안내 |

새 포즈를 추가할 때는 JSON을 복제하지 말고 이 표에 preset을 추가한다.

## Strength tuning rules

## Pose reference identity contamination

`04_pose_refregen_ipadapter_canonical_api.json` is img2img-based. A pose donor with strong hair/color/outfit identity can leak into the refgen result, especially at the default `denoise 0.42`.

Preferred rule:

- For each target character, generate or choose a pose reference that is already close to that character's hair length/color and outfit silhouette.
- Do not reuse one auburn/orange donor across silver, pink, green, or other strongly different characters unless you are intentionally testing failure modes.
- If an external pose reference has a very different identity, treat it as risky. Expect hair color/outfit contamination unless the graph is changed to a stronger pose-only route such as OpenPose/ControlNet.

If contamination appears:

1. Regenerate the donor with the target character's identity block.
2. Add wrong hair/outfit terms to negative prompt.
3. If still contaminated, raise identity strength or lower `denoise`, but watch for weaker pose transfer.
4. For production, prefer character-specific donor -> refgen -> 02 alpha.

2026-05-13 smoke note: reusing auburn donors across `silver_bob`, `pink_twinbraids`, and `green_glasses` preserved the pose but contaminated all results toward auburn/orange hair. Character-specific donors fixed identity preservation much better.

### Refgen에서 캐릭터가 무너지면

- `denoise`를 낮춘다.
- `IPAdapterAdvanced.weight`를 올린다.
- character block에 헤어 길이, 색, 눈 색, 의상 핵심 단어를 보강한다.
- 한 번에 하나만 바꾼다.

### Refgen에서 포즈가 안 따라오면

- pose block을 더 직접적으로 쓴다.
- pose-conflict negative를 추가한다.
- 그래도 부족하면 `denoise`를 조금 올린다.
- `IPAdapterAdvanced.weight`를 너무 높이면 identity는 강해지지만 포즈가 약해질 수 있다.

### 손/팔이 깨지면

- 후보를 여러 seed로 뽑고 contact sheet로 고른다.
- `extra arms`, `extra hands`, `bad hands`, `fused fingers`, `missing fingers`는 negative에 유지한다.
- 팔짱/가슴 손/포인팅처럼 손이 중요한 포즈는 한 번에 2~4개 후보만 만들고 사용자 QA를 받는다.

## Output naming

Text-only pose donor:

```text
hermes_vn_pose/source_{character_slug}_{pose_slug}
```

Same-character refgen:

```text
hermes_vn_pose/refgen_{character_slug}_{pose_slug}
```

Alpha 후처리 결과는 02 naming 규칙을 따른다.

```text
hermes_vn_sprite/{character_slug}_{pose_slug}_alpha
```

## Agent recipe: pose reference가 없을 때

1. 01에서 통과한 캐릭터 anchor/source를 확인한다.
2. 만들 포즈를 pose preset에서 고른다.
3. `04_pose_textonly_source_canonical_api.json`을 로드한다.
4. character block과 pose block을 교체한다.
5. `SaveImage.filename_prefix`를 `hermes_vn_pose/source_{character_slug}_{pose_slug}`로 바꾼다.
6. 실행 전 ComfyUI `/queue`가 비어 있는지 확인한다.
7. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
8. 포즈가 읽히는지 확인한다. 이 단계에서 캐릭터 일관성은 판정하지 않는다.
9. 통과한 donor를 ComfyUI input 폴더로 복사한다.
10. 아래 refgen recipe로 이어간다.

## Agent recipe: 실제 캐릭터 포즈 변경

1. pose reference를 준비한다.
   - 04 donor output 또는 외부 pose reference
2. 01에서 통과한 character anchor/source를 준비한다.
3. 둘 다 ComfyUI input 폴더에 있어야 한다.
4. `04_pose_refregen_ipadapter_canonical_api.json`을 로드한다.
5. pose reference `LoadImage.image`를 실제 파일명으로 바꾼다.
6. character anchor `LoadImage.image`를 실제 파일명으로 바꾼다.
7. character block과 pose block을 맞춘다.
8. preset 기준으로 `denoise`와 `IPAdapterAdvanced.weight`를 조정한다.
   - 기본 출발점: `denoise 0.42`, `IPAdapter weight 0.60`
9. `SaveImage.filename_prefix`를 `hermes_vn_pose/refgen_{character_slug}_{pose_slug}`로 바꾼다.
10. 실행 전 ComfyUI `/queue`가 비어 있는지 확인한다.
11. 실행 후 사용자에게 `prompt_id`와 output path를 전달한다.
12. contact sheet 또는 직접 비교로 QA한다.
13. 통과하면 02 alpha workflow로 넘긴다.

## QA checklist

Text-only donor 단계:

- 포즈가 작은 썸네일에서도 읽히는가
- 머리/몸이 크게 잘리지 않았는가
- 손/팔이 너무 심하게 깨지지 않았는가
- 배경이 단순한 source 배경인가
- refgen 단계에서 pose reference로 쓸 만큼 실루엣이 명확한가

Same-character refgen 단계:

- 01 anchor와 같은 인물로 보이는가
- 헤어 길이/색/실루엣이 유지되는가
- 눈 색과 얼굴 인상이 유지되는가
- 의상 핵심 형태와 색이 유지되는가
- 의도한 포즈가 읽히는가
- 손/팔/어깨가 새로 망가지지 않았는가
- crop/head/hair가 잘리지 않았는가
- alpha가 필요하면 02 workflow 결과까지 따로 확인했는가

## Archive policy

기존 04/05 개별 JSON은 삭제하지 않고 archive에 보관한다.

```text
archive/old_04_pose_source_generation_textonly/
archive/old_05_pose_image_reference_regeneration_ipadapter/
```

Archive 파일은 과거 통과 후보/설정 참고용이다. 새 작업에서는 전면의 canonical JSON 2개와 preset table을 먼저 사용한다.

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
- 포즈별 JSON을 늘리지 않는다. 같은 node graph라면 canonical JSON + preset table로 운영한다.
- 최종 투명 PNG는 기본적으로 02 alpha workflow를 사용한다.
