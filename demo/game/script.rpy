# vn-demo: 이세계 학원 판타지 착각물 첫 장면 초안
# 기본 Ren'Py 예시를 제거하고, 프리프로덕션 문서의 선택 사항을 반영한 시작 장면입니다.

# 캐릭터 정의
# 주인공은 1인칭 시점이므로 대사명은 player_name을 사용합니다.
define p = Character("[player_name]", color="#d8e8ff")
define h = Character("윤하린", color="#b7d7ff")
define prof = Character("교수", color="#e8d8b0")
define stu = Character("학생들", color="#d0d0d0")
define seal = Character("봉인 인장", color="#c9b37a")

# Placeholder-safe 이미지 정의.
# S01 선택 에셋은 후보 승격 상태이며, 최종 품질은 Ren'Py 스크린샷 QA 후 판단합니다.
image bg summoning_hall = "images/backgrounds/bg_summoning_hall.png"
image cg measurement_orb = "images/cg/cg_measurement_orb.png"
image harin neutral = "images/characters/harin/harin_neutral.png"
image harin suspicious = "images/characters/harin/harin_suspicious.png"
image bg summoning_hall_placeholder = Solid("#1b2038")
image bg artifact_lab_placeholder = Solid("#141a24")
image bg report_room_placeholder = Solid("#202436")
image cg sealed_artifact_placeholder = Solid("#3f2f5f")
image cg special_observation_seal_placeholder = Solid("#4a3a2a")
image harin neutral_placeholder = Solid("#334c7a")
image harin suspicious_placeholder = Solid("#26395f")

# 핵심 변수
default player_name = "서진"
default reputation = 0
default misunderstanding_score = 0
default harin_trust = 0
default harin_suspicion = 0
default faculty_interest = 0
default rival_pressure = 0
default hidden_talent_hint = 0

# 사건/선택 기록
default event_measurement_overflow = False
default event_artifact_stopped = False
default event_special_observation = False
default clue_measurement_error_known = False
default clue_artifact_safety_line_seen = False
default clue_academy_legend_heard = False
default choice_measurement_reaction = None
default choice_harin_answer = None
default choice_artifact_action = None
default choice_final_response = None


label start:

    scene bg summoning_hall
    with fade

    "눈을 뜨자, 천장 대신 거대한 마법진이 보였다."

    "낯선 문양들이 강당 바닥을 따라 빛났고, 제복을 입은 학생 수십 명이 나를 보고 있었다."

    p "...여긴 어디죠?"

    stu "방금 소환진에서 나온 거야?"

    stu "편입생 측정식 중에 사람이 떨어졌다고?"

    prof "조용히. 왕립 마법 학원의 편입 측정은 중단하지 않는다."

    "교수라 불린 남자가 내 앞에 수정구 같은 물건을 밀어 놓았다."

    prof "손을 올리게. 마력 계통과 위험 등급만 확인하면 된다."

    "마력. 계통. 위험 등급."

    "아는 단어가 하나도 없었다."

    "그래도 여기서 모른다고 버티면 더 위험해질 것 같았다. 나는 시키는 대로 손을 올렸다."

    $ event_measurement_overflow = True
    $ clue_measurement_error_known = True

    "수정구 안쪽에서 푸른 빛이 돌았다. 한 번, 두 번."

    show cg measurement_orb
    with dissolve

    "그리고 갑자기 빛이 꺼졌다."

    prof "...측정 불능?"

    stu "측정 불능이라고?"

    stu "전설 속 대현자 판정 아니야?"

    "아니었다."

    "나는 그냥 아무것도 모르는 사람이다."

    hide cg measurement_orb
    show harin suspicious at right
    with dissolve

    h "학생회 감찰 담당 윤하린입니다."

    h "측정 불능 판정은 기록상 세 번뿐입니다. 그리고 세 번 모두 학원 재난으로 이어졌죠."

    "하린은 다른 학생들처럼 들떠 있지 않았다."

    "오히려 내가 정말 아무것도 모른다는 표정을 놓치지 않은 것 같았다."

    h "당신, 방금 결과를 예상했나요?"

    menu:
        "침묵한다.":
            $ choice_measurement_reaction = "silent"
            $ misunderstanding_score += 1
            $ reputation += 1

            "나는 대답할 말을 찾지 못했다."

            stu "대답하지 않는군."

            stu "자기 힘을 숨길 생각인가 봐."

            h "...침묵으로 상황을 통제하겠다는 건가요?"

            "아니다. 그냥 모르는 것이다."

        "저도 잘 모르겠습니다.":
            $ choice_measurement_reaction = "explain"
            $ harin_suspicion += 1
            $ misunderstanding_score += 1

            p "저도 잘 모르겠습니다. 정말로요."

            h "그렇게 평범하게 당황하는 사람치고는 결과가 너무 비정상적이군요."

            stu "정체를 숨기려고 일부러 모른 척하는 거야?"

            "솔직하게 말했는데 상황이 더 이상해졌다."

        "측정구를 다시 만져본다.":
            $ choice_measurement_reaction = "retry"
            $ reputation += 1
            $ faculty_interest += 1
            $ hidden_talent_hint += 1

            "나는 혹시 고장이라도 난 건가 싶어 수정구에 손을 다시 올렸다."

            "그 순간, 수정구 안쪽에 아주 가느다란 금빛 선이 스쳤다."

            prof "방금... 측정식의 역류를 손으로 눌렀나?"

            stu "재측정이 아니라 측정구를 시험한 거였어?"

            h "잠깐만요. 당신, 지금 뭘 한 거죠?"

            "나도 알고 싶었다."

    "강당의 웅성거림은 더 커졌다."

    prof "편입생 서진. 임시 등급은 보류한다."

    prof "학생회 감찰 담당은 이 학생을 실습동까지 안내하도록. 봉인 마도구 반응도 확인해야겠군."

    h "...제가요?"

    prof "감찰 담당이라면 가장 적합하겠지."

    hide harin suspicious
    show harin neutral at right

    h "좋습니다. 대신 제 질문에는 전부 대답해 주세요."

    p "제가 대답할 수 있는 거라면요."

    h "그 말도 애매하군요."

    "하린의 눈빛은 여전히 차가웠다."

    "하지만 그 안에는 단순한 적의보다 더 복잡한 의심이 섞여 있었다."

    "나는 이제야 깨달았다."

    "이 세계에서 조용히 넘어가는 방법은, 어쩌면 처음부터 없었을지도 모른다."

    jump ch01_s02_artifact_lab


label ch01_s02_artifact_lab:

    scene bg artifact_lab_placeholder
    with dissolve

    "실습동은 강당보다 훨씬 조용했다."

    "벽마다 낡은 마법진이 금속판처럼 박혀 있었고, 중앙에는 검은 천으로 덮인 봉인 마도구가 놓여 있었다."

    show harin suspicious_placeholder at right
    with dissolve

    h "여기부터는 장난으로 넘어갈 수 없습니다."

    h "측정 불능 판정 뒤에 바로 봉인 마도구 반응까지 확인하는 건, 원래 금지된 절차예요."

    p "그럼 하지 않으면 안 되나요?"

    h "그 말을 교수님 앞에서 했으면, 더 수상해졌을 겁니다."

    "나는 입을 다물었다."

    "하린의 말투는 차가웠지만, 적어도 내가 뭘 모르는지 확인하려는 눈빛이었다."

    h "마지막으로 묻겠습니다. 측정구가 꺼지기 직전, 무언가 보였나요?"

    if choice_measurement_reaction == "retry":
        p "금빛 선 같은 게 잠깐 보였습니다."
        $ clue_artifact_safety_line_seen = True
        $ harin_suspicion += 1
        h "그걸 보고도 다시 손을 올렸다고요?"
        "하린의 의심이 한층 날카로워졌다."
    else:
        p "솔직히 정신이 없어서 잘 모르겠습니다."
        $ harin_trust += 1
        h "...거짓말이라기엔 너무 그대로군요."

    prof "기록석을 켠다. 훈련용 3호 봉인 마도구, 반응 확인."

    hide harin suspicious_placeholder
    show harin neutral_placeholder at right

    "검은 천이 걷히자, 둥근 금속 장치가 모습을 드러냈다."

    show cg sealed_artifact_placeholder
    with dissolve

    "표면에는 낡은 문자와 푸른 선이 얽혀 있었다."

    "처음에는 조용히 빛나던 선들이 갑자기 빠르게 돌기 시작했다."

    prof "반응 수치가 오른다. 모두 물러서!"

    stu "봉인 마도구가 편입생 쪽으로 향하고 있어!"

    "마도구에서 나온 빛이 바닥을 훑었다. 그 아래로 희미한 원형 안전선이 떠올랐다."

    "나는 머리로 생각하기 전에 몸이 먼저 움직였다."

    menu:
        "뒤로 물러난다.":
            $ choice_artifact_action = "step_back"
            $ clue_artifact_safety_line_seen = True
            $ event_artifact_stopped = True
            $ misunderstanding_score += 1
            $ reputation += 1

            "나는 겁이 나서 한 걸음 뒤로 물러났다."

            "발뒤꿈치가 바닥의 희미한 안전선에 닿는 순간, 빛의 원이 딱 맞물렸다."

            stu "방금 마지막 좌표를 밟았어!"

            prof "고대 봉인식의 안전선을 눈으로 읽었다는 건가?"

            "아니다. 그냥 도망치려던 것이다."

        "하린에게 피하라고 외친다.":
            $ choice_artifact_action = "warn_harin"
            $ harin_trust += 1
            $ event_artifact_stopped = True
            $ reputation += 1

            p "하린 씨, 옆으로!"

            "하린이 반사적으로 몸을 틀었다. 그녀가 있던 자리로 푸른 빛이 지나가고, 곧바로 바닥의 안전선에 흡수됐다."

            h "방향을... 읽은 건가요?"

            stu "폭주 궤도를 먼저 봤어!"

            "나는 그냥 위험해 보여서 외쳤을 뿐이다."

        "바닥의 빛나는 선을 건드린다.":
            $ choice_artifact_action = "touch_line"
            $ clue_artifact_safety_line_seen = True
            $ hidden_talent_hint += 1
            $ faculty_interest += 1
            $ event_artifact_stopped = True

            "나는 출구처럼 보이는 빛을 더듬었다."

            "손끝이 바닥의 선에 닿자, 내 안쪽에서 아주 작은 열감이 올라왔다."

            "푸른 회로가 금빛으로 한 번 바뀌더니, 마도구의 회전이 멈췄다."

            prof "잔여 회로를 직접 닫았다?"

            h "방금 건... 모른 척으로 설명하기 어렵습니다."

            "나도 그렇게 생각했다. 그래서 더 무서웠다."

    hide cg sealed_artifact_placeholder
    show harin suspicious_placeholder at right
    with dissolve

    prof "봉인 마도구 반응 정지. 사고 등급은 보류한다."

    prof "하지만 이건 단순한 편입 절차가 아니다. 학원장 보고가 필요하겠군."

    $ rival_pressure += 1

    stu "측정 불능 편입생이 마도구까지 멈췄대."
    stu "귀족반 쪽에서 가만히 있지 않겠는데?"
    h "축하한다고 해야 할지 모르겠군요."
    p "저는 그냥 집에 가고 싶은데요."
    h "그 말이 진심이라면, 더더욱 혼자 두면 안 되겠습니다."
    "하린은 기록판을 닫고 나를 똑바로 보았다."
    h "윤하린, 학생회 감찰 담당 권한으로 임시 감시를 신청하겠습니다."
    "그 순간, 실습동 문 너머에서 낮은 종소리가 울렸다."

    jump ch01_s03_special_observation


label ch01_s03_special_observation:

    scene bg report_room_placeholder
    with dissolve

    "임시 보고실의 공기는 실습동보다 더 무거웠다."
    "벽면의 기록석에는 방금 전 사건 두 줄이 이미 떠 있었다."

    show harin suspicious_placeholder at right
    with dissolve

    prof "편입 측정식 결과, 측정 불능."
    prof "훈련용 3호 봉인 마도구 반응, 외부 개입 없이 정지."
    p "외부 개입이 없었다면 그냥 사고가 멈춘 거 아닌가요?"
    h "그렇게 기록하면 더 위험합니다."
    h "학원은 원인을 모르는 안전보다, 원인을 아는 위험을 선호하니까요."

    "나는 그 말이 무슨 뜻인지 바로 이해하지 못했다."
    "그러나 교수의 펜끝은 이미 나를 원인 쪽에 놓고 있었다."

    show cg special_observation_seal_placeholder
    with dissolve

    seal "학원장 직인 확인."
    seal "측정 불능 편입생 서진을 임시 특별 관찰 대상으로 지정한다."

    $ event_special_observation = True
    $ rival_pressure += 1

    "갈색 봉인 문장이 문서 아래에 찍히자, 방 안의 공기가 한 번 더 가라앉았다."
    "내가 이 세계에서 얻은 첫 공식 신분은 학생도, 손님도 아니었다."
    "특별 관찰 대상."

    hide cg special_observation_seal_placeholder
    show harin suspicious_placeholder at right
    with dissolve

    prof "귀족반에도 사고 보고가 공유될 거다. 소문보다 문서가 먼저 도착하길 바라야겠군."
    p "그럼 저는 이제 어떻게 하면 되나요?"
    h "대답 하나를 고르셔야 합니다."
    h "공식 기록은 당신의 의도보다, 당신이 남긴 결과를 먼저 읽습니다."

    menu:
        "일단 시키는 대로 하겠습니다.":
            $ choice_final_response = "comply"
            $ reputation += 1
            $ misunderstanding_score += 1

            p "일단 시키는 대로 하겠습니다."
            "나는 괜히 일을 키우지 않으려고 최대한 얌전히 말했다."
            prof "상황 판단이 빠르군. 자신의 위치를 알고 움직인다는 뜻인가."
            h "...순응도 전략일 수 있습니다."
            "아니다. 그냥 더 혼나기 싫을 뿐이다."

        "저는 정말 아무것도 모릅니다.":
            $ choice_final_response = "deny_knowledge"
            $ harin_suspicion += 1
            $ harin_trust += 1

            p "저는 정말 아무것도 모릅니다."
            h "그 말이 거짓이라면 너무 어설프고, 진실이라면 너무 위험합니다."
            prof "정보 공개 범위를 제한한다고 기록하지."
            "솔직하게 말했는데 문장이 점점 더 딱딱해졌다."

        "하린 씨가 봐주시면 안 되나요?":
            $ choice_final_response = "ask_harin_help"
            $ harin_trust += 1
            $ rival_pressure += 1

            p "하린 씨가 봐주시면 안 되나요?"
            "내가 보기에는 이 방에서 그나마 말이 통하는 사람이 하린뿐이었다."
            h "감찰 담당을 사적으로 지명하는 발언은 기록에 남습니다."
            prof "벌써 담당자를 자기 편으로 끌어들이는 건가. 흥미롭군."
            "도움을 요청했을 뿐인데 협상처럼 번역됐다."

    hide harin suspicious_placeholder
    show harin neutral_placeholder at right
    with dissolve

    h "임시 감시는 제가 맡겠습니다."
    h "다만 믿어서가 아닙니다. 혼자 두는 쪽이 더 위험하다고 판단했을 뿐이에요."
    p "그 차이가 큰가요?"
    h "네. 아주 큽니다."

    "보고실 문이 열리자, 복도 너머에서 학생들의 낮은 웅성거림이 흘러들어왔다."
    "다음 장면 후보: ch01_s04_harin_watch. 하린의 감시 아래 학원 복도로 나간다."

    return
