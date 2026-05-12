from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "demo" / "game" / "script.rpy"
DOCS = ROOT / "docs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_script_replaces_default_renpy_template_with_academy_misunderstanding_opening():
    text = read(SCRIPT)

    assert "아이린" not in text
    assert "새로운 렌파이 게임" not in text
    assert "label start:" in text
    assert "왕립 마법 학원" in text
    assert "측정 불능" in text
    assert "학생회 감찰 담당" in text
    assert "윤하린" in text


def test_script_declares_core_misunderstanding_variables_and_first_choice_effects():
    text = read(SCRIPT)

    for variable in [
        "player_name",
        "reputation",
        "misunderstanding_score",
        "harin_trust",
        "harin_suspicion",
        "faculty_interest",
        "rival_pressure",
        "hidden_talent_hint",
    ]:
        assert f"default {variable}" in text

    assert "choice_measurement_reaction" in text
    assert "misunderstanding_score += 1" in text
    assert "reputation += 1" in text
    assert "harin_suspicion += 1" in text
    assert "faculty_interest += 1" in text
    assert "hidden_talent_hint += 1" in text


def test_scene_card_and_manifest_record_selected_direction():
    scene = read(DOCS / "story" / "scenes" / "ch01_s01_summoning_measurement.yaml")
    manifest = read(DOCS / "project_manifest.json")

    assert "측정구" in scene
    assert "봉인 마도구" in scene
    assert "학생회 감찰 담당" in scene
    assert "hidden_talent_hint" in scene
    assert "protagonist_hidden_talent" in manifest
    assert "heroine_role" in manifest
    assert "first_incident" in manifest


def test_artifact_lab_scene_is_playable_and_not_a_stub():
    text = read(SCRIPT)

    assert "label ch01_s02_artifact_lab:" in text
    assert "label ch01_s02_artifact_lab_stub:" not in text
    assert "다음 장면:" not in text
    assert "bg artifact_lab_placeholder" in text
    assert "봉인 마도구" in text
    assert "안전선" in text
    assert "event_artifact_stopped = True" in text
    assert "clue_artifact_safety_line_seen = True" in text
    assert "choice_artifact_action" in text
    assert "harin_trust += 1" in text
    assert "rival_pressure += 1" in text


def test_artifact_lab_scene_card_and_manifest_are_linked():
    scene = read(DOCS / "story" / "scenes" / "ch01_s02_artifact_lab.yaml")
    manifest = read(DOCS / "project_manifest.json")

    assert "봉인 마도구" in scene
    assert "고대 봉인식" in scene
    assert "choice_artifact_action" in scene
    assert "ch01_s02_artifact_lab.yaml" in manifest
    assert "ch01_s02_artifact_lab implemented" in manifest
