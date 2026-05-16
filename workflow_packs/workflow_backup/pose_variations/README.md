### 🧍‍♀️ 0. 동작 변화 워크#### 1. 프롬프팅 방법

*(※ 주의: 긍정 프롬프트에서 기본 앵커에 있던 `arms_at_sides(차렷 자세)`, `straight_posture(꼿꼿한 자세)`는 반드시 삭제해야 새 동작이 적용됩니다.)*

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, medium_breasts, cowboy_shot, front_view, looking_at_viewer, expressionless, closed_mouth, {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}, fully_clothed, {의상 디테일}, {동작 및 포즈 태그}, highly_detailed, grey_background

```

**Negative prompt:**

```text
nude, nipples, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, different_face, different_hair, different_hairstyle, different_eye_color, changed_face, changed_hair, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), vignette, shadow, depth_of_field, rim_lighting, {상극 동작 태그}

```

#### 2. 동작/포즈 프롬프트 리스트 (단부루 표준 규격)

비주얼 노벨 스탠딩(상반신/무릎 위)에서 가장 자주 쓰이는 팔과 상체 위주의 동작 세트입니다.

*(※ Positive prompt의 `{동작 및 포즈 태그}`와 Negative prompt의 `{상극 동작 태그}` 자리에 아래 세트를 복사해서 넣으세요.)*

**1) 팔짱 끼기 (도도함, 방어적, 화남)**

* **Positive:** `crossed_arms`
* **Negative:** `arms_at_sides, hands_on_hips, reaching_out`

**2) 허리에 손 얹기 (자신감, 따짐, 활기참)**

* **양손:** * **Positive:** `hands_on_hips`
* **Negative:** `arms_at_sides, crossed_arms, hands_in_pockets`


* **한 손만:** * **Positive:** `hand_on_own_hip, one_arm_at_side`
* **Negative:** `hands_on_hips, crossed_arms`



**3) 얼굴/머리에 손 대기 (고민, 부끄러움, 당황)**

* **턱에 손 (고민/추리):** * **Positive:** `hand_on_own_chin`
* **뺨에 손 (놀람/부끄러움):** * **Positive:** `hand_on_own_cheek`
* **머리 쓸어넘기기:** * **Positive:** `adjusting_hair, hand_in_own_hair`
* **공통 Negative:** `arms_at_sides, crossed_arms, hands_on_hips`

**4) 앞으로 손 뻗기 / 가리키기 (역동적, 지적, 권유)**

* **손 내밀기 (권유/잡아달라):** * **Positive:** `reaching_out, reaching_towards_viewer`
* **손가락으로 가리키기:** * **Positive:** `pointing, pointing_at_viewer`
* **공통 Negative:** `arms_at_sides, crossed_arms, hands_on_hips, hands_clasped`

**5) 두 손 모으기 (소심, 간절함, 긴장)**

* **가슴/배 앞에 두 손 모으기:** * **Positive:** `hands_clasped, hands_together`
* **꼼지락거리기 (긴장):** * **Positive:** `fidgeting`
* **공통 Negative:** `arms_at_sides, crossed_arms, hands_on_hips, reaching_out`

**6) 상체 기울이기 (감정 강조)**

* **앞으로 기울이기 (호기심/위협):**
* **Positive:** `leaning_forward`


* **뒤로 기대기/젖히기 (거만함/회피):**
* **Positive:** `leaning_back`


* *(※ 상체 기울이기는 위 1~5번의 팔 동작 태그들과 섞어서 사용하면 아주 자연스럽습니다. 예: `crossed_arms, leaning_forward`)*

#### 3. 동작 프롬프팅 및 워크플로우 추가 팁

* **마스크 영역 확장 (매우 중요):** 표정이나 의상 변경은 기존 실루엣 안에서 해결되는 경우가 많지만, '동작 변화'는 팔이 몸통 밖으로 크게 움직입니다. 따라서 인페인트 마스크를 생성할 때 팔이 움직일 예상 궤적(화면 양옆 허공)까지 넉넉하게 마스크 칠을 해주거나, `GrowMask` 수치를 대폭 올려주어야 팔이 잘리거나 뭉개지지 않습니다.
* **손(Hands) 퀄리티 방어:** 팔이 움직이면 필연적으로 손이 화면에 노출됩니다. 부정 프롬프트에 있는 `bad_anatomy, bad_hands, missing_fingers` 등이 손가락 기형을 막아주는 핵심 방어벽 역할을 하므로 절대 지우지 마세요.
* **의상 프롬프트 유지:** 동작이 바뀌면서 옷의 주름이나 형태도 팔의 움직임에 맞춰 새로 그려져야 자연스럽습니다. 따라서 긍정 프롬프트의 `{의상 디테일}` 부분은 기존 스탠딩과 똑같이 상세하게 적어두어야 옷의 일관성이 유지됩니다.