# Automated screenshot QA for promoted prototype assets.
# Generated after user selected Harin redesign s03.

label qa_s01_harin_s03_assets:
    scene bg summoning_hall
    show harin suspicious at right
    with None
    h "감찰 담당 윤하린입니다. 이상한 짓은 하지 마세요."
    return

testcase qa_s01_harin_s03_assets:
    run Start("qa_s01_harin_s03_assets")
    advance
    screenshot "qa_s01_harin_s03_assets.png"
    exit

image qa_harin_neutral = Transform("images/characters/harin/harin_neutral.png", zoom=0.40)
image qa_harin_suspicious = Transform("images/characters/harin/harin_suspicious.png", zoom=0.40)

label qa_harin_suspicious_expression:
    scene bg summoning_hall
    show qa_harin_neutral at left
    show qa_harin_suspicious at right
    with None
    h "수상합니다. 방금 그 표정까지 계산한 건 아니겠죠?"
    return

testcase qa_harin_suspicious_expression:
    run Start("qa_harin_suspicious_expression")
    advance
    screenshot "qa_harin_suspicious_expression.png"
    exit
