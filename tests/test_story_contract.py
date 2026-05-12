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


def test_demo_route_has_complete_scene_flow_cards_before_asset_production():
    manifest = read(DOCS / "project_manifest.json")
    blueprint = read(DOCS / "story" / "routes" / "main_route_blueprint.md")

    required_scenes = [
        "ch01_s01_summoning_measurement",
        "ch01_s02_artifact_lab",
        "ch01_s03_special_observation",
        "ch01_s04_harin_watch",
        "ch01_s05_demo_ending_hook",
    ]

    for scene_id in required_scenes:
        assert scene_id in blueprint
        assert scene_id in manifest

    for filename in [
        "ch01_s04_harin_watch.yaml",
        "ch01_s05_demo_ending_hook.yaml",
    ]:
        scene = read(DOCS / "story" / "scenes" / filename)
        assert "status: DRAFT" in scene
        assert "required_beats:" in scene
        assert "asset_needs:" in scene
        assert "tone_guardrails:" in scene
        assert "next_hook:" in scene or "demo_end:" in scene

    assert "scene-flow-first, scene-by-scene production" in manifest
    assert "status: PLAYABLE DRAFT" in read(DOCS / "story" / "scenes" / "ch01_s03_special_observation.yaml")


def test_asset_manifest_defines_minimum_demo_asset_scope_and_priorities():
    asset_manifest = read(DOCS / "assets" / "asset_manifest.yaml")
    project_manifest = read(DOCS / "project_manifest.json")
    readme = read(ROOT / "README.md")

    for asset_id in [
        "bg_summoning_hall",
        "bg_artifact_lab",
        "cg_measurement_orb",
        "cg_sealed_artifact",
        "sprite_harin_neutral",
        "sprite_harin_suspicious",
        "sprite_harin_surprised",
        "sfx_measurement_overflow",
        "sfx_artifact_shutdown",
        "bgm_academy_tension",
    ]:
        assert asset_id in asset_manifest

    assert "minimum_demo_assets" in asset_manifest
    assert "production_priority" in asset_manifest
    assert "ComfyUI" in asset_manifest
    assert "placeholder_ok_until_scene_lock" in asset_manifest
    assert "docs/assets/asset_manifest.yaml" in project_manifest
    assert "docs/assets/asset_manifest.yaml" in readme


def test_special_observation_scene_is_playable_and_connected_from_artifact_lab():
    text = read(SCRIPT)

    assert "label ch01_s03_special_observation:" in text
    assert "jump ch01_s03_special_observation" in text
    assert "return\n" not in text.split("label ch01_s02_artifact_lab:", 1)[1].split("label ch01_s03_special_observation:", 1)[0]
    assert "bg report_room_placeholder" in text
    assert "cg special_observation_seal_placeholder" in text
    assert "choice_final_response" in text
    assert "event_special_observation = True" in text
    assert "특별 관찰 대상" in text
    assert "학원장 직인" in text
    assert "귀족반" in text
    assert "ch01_s04_harin_watch" in text


def test_special_observation_scene_card_manifest_and_readme_are_updated_after_playable_promotion():
    scene = read(DOCS / "story" / "scenes" / "ch01_s03_special_observation.yaml")
    manifest = read(DOCS / "project_manifest.json")
    blueprint = read(DOCS / "story" / "routes" / "main_route_blueprint.md")
    readme = read(ROOT / "README.md")

    assert "status: PLAYABLE DRAFT" in scene
    assert "ch01_s03_special_observation implemented" in manifest
    assert "ch01_s03_special_observation" in manifest
    assert "S01~S03 구현" in readme
    assert "`ch01_s03_special_observation`: 구현됨" in readme
    assert "| `ch01_s03_special_observation` | PLAYABLE DRAFT" in blueprint
    assert "S04 `ch01_s04_harin_watch`" in blueprint
