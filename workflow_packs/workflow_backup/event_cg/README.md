### 🖼️ 0. 이벤트 CG 제작 워크플로우

이 워크플로우는 **캐릭터 reference 1장만 입력**하고, 배경/구도는 프롬프트로 새로 생성합니다. 현재 canonical JSON에는 자연스러운 작은 연출을 보조하기 위한 pose LoRA가 기본 적용되어 있습니다.

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, cinematic_visual_novel_event_CG, same_character_as_reference, preserve_original_face, preserve_original_facial_features, preserve_original_hairstyle, preserve_original_hair_color, preserve_original_eye_color, preserve_original_school_uniform_design, preserve_original_outfit_colors, preserve_original_body_proportions, minimal_character_redesign, 1girl, solo, {캐릭터 핵심 특징}, {원본 의상 디테일}, {카메라 구도}, {원본 포즈를 크게 바꾸지 않는 자연스러운 작은 연출}, {감정표현}, {배경 테마 및 장소}, {시간대 및 조명}, small_natural_pose_change_only, coherent_perspective, character_integrated_with_background_lighting, natural_pose, depth_of_field, detailed_background

```

*(※ 원본 캐릭터/의상 유지를 우선합니다. 캐릭터가 화면에 가깝게 나오도록 `{카메라 구도}`에는 `upper_body`, `waist_up`, `medium_shot`, `close-up` 등을 넣으면 됩니다.)*

**Negative prompt:**

```text
different_character, different_face, different_facial_features, different_hair, different_hairstyle, different_hair_color, different_eye_color, different_clothes, changed_uniform, outfit_redesign, different_body_type, changed_body_proportions, extreme_action_pose, acrobatics, large_pose_change, tiny_character, far_away_character, empty_room, crowd, multiple_girls, duplicate_person, bad_hands, extra_fingers, missing_fingers, fewer_digits, bad_anatomy, long_body, deformed, mutated, cropped_head, lowres, blurry, text, watermark, signature, simple_background, white_background, (worst_quality, bad_quality:1.2)

```

#### 2. 이벤트 CG 프롬프트 작성 팁 및 활용 가이드

**1) 카메라 구도 (Camera Angle)**

* **위에서 내려다보기:** `from_above, high_angle` (약해 보이거나 올려다보는 귀여운 연출)
* **아래서 올려다보기:** `from_below, low_angle` (웅장하거나 위압감 있는 연출)
* **초근접/얼굴 중심:** `close-up, face_focus` (감정선이 극에 달했을 때)
* **등장인물 어깨너머:** `over_the_shoulder` (플레이어와 마주 보는 듯한 1인칭 시점 연출)

**2) 상황 및 자연스러운 작은 연출 (Staging & Pose)**

* **권장 예시:** `standing_beside_classroom_window`, `sitting_at_a_classroom_desk`, `elbows_gently_resting_on_desk`, `one_hand_lightly_near_chest`, `slight_body_turn` 등 원본 포즈를 크게 바꾸지 않는 자연스러운 연출
* **주의:** `reaching_out_to_viewer`, `hugging_knees`, `looking_back_over_shoulder`처럼 큰 포즈 변화는 이벤트 CG 재해석이 커질 수 있으므로 필요할 때만 사용합니다.

**3) 배경 및 조명 연출 보강**

* **예시 (창가에서 햇빛을 받는 씬):** `{배경 테마 및 장소}` 자리에 `warm_sunset_classroom, sunlight_through_window, dust_motes` 등을 넣고, `{시간대 및 조명}` 자리에 `golden_hour_rim_light, soft_orange_sunlight` 등을 넣으면 캐릭터와 배경 조명이 함께 맞춰집니다.
