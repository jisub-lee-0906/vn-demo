### 🖼️ 0. 이벤트 CG 제작 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, cinematic_angle, dramatic_lighting, 1girl, solo, {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}, {캐릭터 의상/특징}, upper_body, {카메라 구도}, {상황 및 역동적인 포즈}, {감정표현}, {배경 테마}, BREAK, depth_of_field, volumetric_lighting, light_rays, detailed_background

```

*(※ 캐릭터가 화면에 가깝게 나오도록 `upper_body`(상반신) 태그를 기본적으로 추가했습니다. 얼굴을 더 크게 잡고 싶다면 `{카메라 구도}`에 `close-up`을 넣으시면 됩니다.)*

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, simple_background, white_background, (worst_quality, bad_quality:1.2)

```

#### 2. 이벤트 CG 프롬프트 작성 팁 및 활용 가이드

**1) 카메라 구도 (Camera Angle)**

* **위에서 내려다보기:** `from_above, high_angle` (약해 보이거나 올려다보는 귀여운 연출)
* **아래서 올려다보기:** `from_below, low_angle` (웅장하거나 위압감 있는 연출)
* **초근접/얼굴 중심:** `close-up, face_focus` (감정선이 극에 달했을 때)
* **등장인물 어깨너머:** `over_the_shoulder` (플레이어와 마주 보는 듯한 1인칭 시점 연출)

**2) 상황 및 역동적인 포즈 (Action & Pose)**

* **예시:** `reaching_out_to_viewer` (화면 쪽으로 손을 뻗음), `sitting_on_bed, hugging_knees` (침대에 앉아 무릎을 끌어안음), `looking_back_over_shoulder` (뒤돌아봄)

**3) 배경 및 조명 연출 보강**

* **예시 (창가에서 햇빛을 받는 씬):** `{배경 테마}` 자리에 `sunlight_through_window, dust_motes, beautiful_bedroom` 등을 넣으면 빛 갈라짐과 먼지 입자 효과가 어우러져 아주 환상적인 분위기가 연출됩니다.