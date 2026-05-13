# 01 — 캐릭터 기준 앵커 생성

Category: `character`

## Purpose

새 캐릭터의 재사용 가능한 기준 source 이미지를 만든다.

이 workflow의 목적은 “가장 화려한 일러스트”가 아니라 후속 workflow에서 안정적으로 재사용하기 쉬운 `A-pose + neutral expression` character anchor 생성이다.

01에서 만든 source PNG는 다음 단계의 기준 이미지가 된다.

```text
01 source anchor
→ 02 transparent alpha sprite
→ 03 expression variations
→ 04 pose variations
→ 10 outfit/costume variations
```

## Output

- 출력물: 회색 배경의 character source PNG
- 용도: 02/03/04/10에서 얼굴, 헤어, 의상, 기본 체형을 참조하는 기준 이미지
- 아직 Ren'Py 투입용 투명 PNG가 아니다. 투명 PNG가 필요하면 02 workflow로 후처리한다.

## API template

- `workflow_api/01_character_anchor_apose_neutral_api.json`
  - checkpoint: `novaAnimeXL_ilV180.safetensors`
  - role: canonical A-pose neutral character anchor
  - ComfyUI endpoint when running from WSL: usually `http://172.28.224.1:8000`
  - status: user-approved canonical baseline; prompt-ablation kept set applied

## Editable nodes

보통 아래 3가지만 바꾼다.

| Node | Field | What to edit |
| --- | --- | --- |
| `3` CLIPTextEncode positive | `inputs.text` | 캐릭터 정체성 block만 교체 |
| `6` KSampler | `inputs.seed` | 새 후보/새 캐릭터 seed |
| `8` SaveImage | `inputs.filename_prefix` | 출력 prefix |

특별한 이유가 없으면 아래는 유지한다.

- checkpoint: `novaAnimeXL_ilV180.safetensors`
- image size: `1152 x 1536`
- sampler/settings: `steps 28`, `cfg 6.0`, `euler_ancestral`, `normal`, `denoise 1.0`
- A-pose / neutral expression wording
- style/background wording
- negative prompt의 pose/hand/crop/sheet/text 방지 구간

## Positive prompt structure

positive prompt는 세 구간으로 본다.

```text
[fixed composition/pose/expression block], [character identity block], [fixed VN sprite style/background block]
```

### 1. Fixed composition/pose/expression block

이 구간은 01 anchor의 목적을 고정한다. 보통 수정하지 않는다.

```text
masterpiece, best quality, very aesthetic, newest, 1girl, solo, anime style,
cowboy shot, upper body character portrait, waist-up to upper-thigh visible,
full head visible, complete hair visible, whole torso visible, large centered character,
front view, relaxed A-pose, arms naturally down at both sides,
arms slightly away from body, visible open hands at sides,
straight posture, shoulders level,
neutral expression, closed mouth, calm blank face, looking at viewer
```

목표:

- 정면
- 무표정 / 닫힌 입
- 후속 표정/포즈 변형에 방해되지 않는 기준 자세
- 손이 화면 밖으로 잘리지 않는 상반신~허벅지 구도
- full body가 아니라 `cowboy shot / upper body to upper-thigh` 기준

### 2. Character identity block

새 캐릭터를 만들 때는 이 구간만 교체한다.

현재 template 예시:

```text
short silver bob hair, cool blue eyes, clean face,
navy cardigan over white blouse, charcoal pleated skirt,
modest bust, simple school-inspired uniform
```

권장 작성 순서:

```text
[hair color + hairstyle], [eye color/shape], [face feature],
[adult body silhouette only if needed], [outfit], simple school-inspired uniform or outfit descriptor
```

좋은 예:

```text
long straight black hime-cut hair, deep violet eyes, calm clean face,
tall slender build, modest bust, dark navy sailor uniform with white collar,
pleated skirt, simple school-inspired uniform
```

```text
shoulder-length honey blonde wavy hair, emerald green eyes, soft clean face,
average build, medium bust, cream cardigan over white blouse,
plaid pleated skirt, simple school-inspired uniform
```

```text
chin-length dusty blue bob hair, gray blue eyes, cool clean face,
petite build, modest bust, pale gray cardigan over navy blouse,
charcoal pleated skirt, simple school-inspired uniform
```

주의:

- `novaAnimeXL_ilV180`은 프롬프트에 민감하다. 한 번에 많은 문구를 추가하지 않는다.
- 여러 캐릭터용 template에서는 특정 머리색/옷색을 negative에 넣지 않는다. 예: `green hair`, `teal clothes` 같은 색상 금지어는 다른 캐릭터를 막을 수 있다.
- 01에서는 표정을 바꾸지 않는다. smile/happy/sad/angry/surprised/fearful은 03에서 만든다.
- 01에서는 포즈를 바꾸지 않는다. crossed arms/hand on hip/pointing 등은 04에서 만든다.
- 의상 variation은 10에서 만든다. 01에서는 기준 의상만 정한다.

### 3. Fixed VN sprite style/background block

현재 user-approved 01 상태에서는 아래 style block을 유지한다.

```text
consistent modern visual novel sprite style,
simple anime cel shading,
polished visual novel character sprite,
delicate clean face, symmetrical eyes, detailed irises,
refined hair strands, clean sharp anime lineart,
soft cel shading, clean color separation,
flat solid medium gray background, plain uniform gray backdrop
```

프롬프트 ablation 결과 유지된 문구:

- `consistent modern visual novel sprite style`
- `simple anime cel shading`

이 두 문구는 5-character fixed-seed test에서 baseline 대비 큰 변화는 아니지만 평균적으로 같거나 조금 더 안정적인 VN/cel rendering을 보여서 유지한다.

Reject했던 문구는 다시 넣지 않는다. 특히 아래는 무의미하거나 작은 drift만 만들었다.

```text
medium eye size
thin consistent lineart
clean flat colors
low detail uniform design
same face proportion style
centered full body sprite
same camera distance
high resolution anime game sprite
```

negative 쪽에서도 아래는 거의 no-op이라 기본 template에 넣지 않는다.

```text
painterly shading
semi-realistic face
```

## Negative prompt rules

A-pose neutral 기준에서는 아래 계열을 유지한다.

```text
smile, smiling, open mouth,
dynamic pose, tilted body, crossed arms,
hands together, hands near face,
hands on hips, hands on waist, hands in pockets,
akimbo, elbows bent, hidden hands, cropped hands,
clenched fists, fist, dramatic pose, sassy pose, leaning,
three-quarter view,
text, watermark, logo,
multiple girls, duplicate character,
cropped head, cut off hair, cropped arms, out of frame,
extra arms, extra hands, bad hands,
asymmetrical eyes, deformed face, blurry face,
muddy shading, overrendered,
low quality, worst quality,
full body, tiny character, chibi, feet visible, shoes,
white background, bright background, gradient background,
background color bleeding into hair, color cast on character edges,
headwear, object above head, ribbon on head, bow on head, hair ornament,
reference sheet, character sheet, sprite sheet, inset, profile card
```

색상별 금지어는 넣지 않는다.

## Output naming

권장 prefix:

```text
hermes_vn_toonout_other_character/source_{character_slug}_apose_neutral_ilV180_{seed}
```

예시:

```text
hermes_vn_toonout_other_character/source_silver_bob_apose_neutral_ilV180_719242400
```

실험/ablation이면 별도 run folder를 쓴다.

```text
hermes_vn_prompt_ablation_01/{test_id}/source_{character_slug}_{test_id}_{seed}
```

## Agent recipe

1. root `AGENTS.md`와 `WORKFLOW_INDEX.json`을 먼저 확인한다.
2. `workflow_api/01_character_anchor_apose_neutral_api.json`을 로드한다.
3. ComfyUI `/queue`가 비어 있는지 확인한다. 공유 Windows ComfyUI를 함부로 interrupt/clear하지 않는다.
4. positive prompt에서 character identity block만 교체한다.
5. seed와 `SaveImage.filename_prefix`를 변경한다.
6. style block과 negative prompt는 유지한다.
7. `POST /prompt`로 실행하고 `/history/{prompt_id}`에서 output path를 확인한다.
8. 사용자에게 `prompt_id`, seed, output path를 전달한다.
9. 사용자가 QA를 맡겠다고 했으면 자동 vision QA를 하지 않는다.
10. 사용자가 후보를 승인하면 `WORKFLOW_INDEX.json`에는 대표 상태/output만 짧게 반영한다.

## Multi-character prompt check recipe

새 prompt가 다양한 캐릭터에 일반화되는지 볼 때는 아래처럼 한다.

1. character identity block만 다른 5개 이상 캐릭터를 준비한다.
2. seed를 고정 목록으로 둔다.
3. 한 번에 prompt phrase를 1개만 추가한다.
4. 각 후보마다 전체 캐릭터를 생성한다.
5. previous-kept top row / candidate bottom row contact sheet를 만든다.
6. 평균적으로 유의미한 개선이 없거나 identity/A-pose/neutral이 흔들리면 reject한다.
7. 최종 kept set만 workflow JSON에 반영한다.

현재 01의 최종 kept set은 위 style block의 두 문구다.

## QA checklist

생성 결과가 아래 기준을 만족해야 한다.

- 단일 캐릭터인가
- 무표정/닫힌 입인가
- 정면 기준인가
- A-pose 또는 팔 내림 reference pose인가
- 양손이 보이고 크게 깨지지 않았는가
- 머리/얼굴/손/치마가 잘리지 않았는가
- 상반신~허벅지 구도가 유지되는가
- 배경, 글자, 로고, 워터마크가 없는가
- 과한 headwear/object/ribbon/hair ornament가 생기지 않았는가
- 02/03/04/10의 기준 이미지로 재사용하기 쉬운가

## Notes for agents

- README는 사용법 문서다. 긴 테스트 결과나 보고서는 여기에 누적하지 않는다.
- 승인 상태, 대표 prompt_id, 대표 output은 `WORKFLOW_INDEX.json`에 짧게 둔다.
- 생성된 PNG/contact sheet는 reusable pack 안에 저장하지 않는다.
- detailed ablation artifacts were saved outside the reusable pack under Windows ComfyUI output, not in this folder.
