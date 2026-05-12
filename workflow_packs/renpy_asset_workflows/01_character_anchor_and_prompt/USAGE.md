# 01 Character anchor / source generation 사용법

목적: Ren'Py 대화 스프라이트에 쓸 수 있는 단일 캐릭터 기준 소스 이미지를 만든다.

## 사용 모델/핵심 설정

- Checkpoint: `novaAnimeXL_ilV125.safetensors`
- Clip skip: `CLIPSetLastLayer(-2)` 권장
- Canvas: 이번 검증 기준 `1152x1536`
- 배경: `flat solid medium gray background`, `plain uniform gray backdrop`
- 프레이밍: `cowboy shot`, `upper body character portrait`, `waist-up to upper-thigh visible`, `full head visible`, `complete hair visible`, `large centered character`

## 이번 기준 프롬프트

자세한 positive/negative와 seed는 `artifacts/other_character_source_manifest.json`에 보관했습니다.

핵심 positive:

```text
masterpiece, best quality, very aesthetic, newest, 1girl, solo, anime style, cowboy shot, upper body character portrait, waist-up to upper-thigh visible, full head visible, complete hair visible, large centered character, hands inside canvas, auburn medium-length wavy hair, warm brown eyes, clean face, ivory knit cardigan over pale blue blouse, navy pleated skirt, simple school uniform, relaxed standing pose, hands below frame, clean sharp anime lineart, flat solid medium gray background, plain uniform gray backdrop
```

핵심 negative:

```text
text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, cropped arms, cropped hands, out of frame, extra arms, extra hands, bad hands, low quality, worst quality, full body, tiny character, chibi, feet visible, shoes, white background, bright background, gradient background, green background, teal background, green clothes, green cardigan, green uniform, green hair, teal hair, green highlights, green reflection, green rim light, background color bleeding into hair, translucent green edges, headwear, object above head, ribbon on head, bow on head, hair ornament, reference sheet, character sheet, sprite sheet, inset, profile card
```

## 이번 선택 결과

- 선택 소스: `artifacts/source_auburn_719238043_00001_.png`
- 후보 QA: `artifacts/source_candidates_contact.png`

## PASS 기준

- 한 명만 있음
- 머리 전체와 상반신/허벅지 일부가 잘림 없이 들어옴
- 회색 배경이 균일함
- 머리 위 리본/오브젝트/카드/삽입 그림 없음
- 손/팔이 대화용 스프라이트로 크게 망가지지 않음

## 주의점

- `margin above head`, `reference sheet`, `visual novel sprite` 같은 말은 top artifact나 sheet contamination을 부를 수 있어 피합니다.
- `shoes out of frame`처럼 나오면 안 되는 물체를 positive에 넣지 않습니다.

## API templates now available

Replay templates were added under `../api_workflows/`:
- `01_character_anchor_seed719238041_api.json`
- `01_character_anchor_seed719238042_api.json`
- `01_character_anchor_seed719238043_api.json` — selected source seed

These are txt2img NovaAnimeXL /prompt graphs. Edit prompt/seed/output prefix only for first retries.

## Cleanup note (2026-05-12)

PNG/contact/QA sheet paths in this document are historical output filenames, not files preserved in this template pack. Recreate them from the matching `api_workflows/*.json` templates and manifests when visual QA is needed.
