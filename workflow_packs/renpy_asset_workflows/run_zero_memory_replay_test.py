#!/usr/bin/env python3
"""Zero-memory replay smoke for VN auburn ComfyUI template pack.

Runs a chained, representative replay from API templates only:
01 selected anchor -> 02 alpha -> 03 expressions+alpha -> 04 pose donors+alpha -> 05 pose ref-generation+alpha.

The script intentionally does not interrupt or clear the shared ComfyUI queue.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
API = BASE / "api_workflows"
COMFY = Path("/mnt/c/Users/Desktop/Documents/ComfyUI")
COMFY_INPUT = COMFY / "input"
COMFY_OUTPUT = COMFY / "output"
RUN_ROOT = BASE / "test_runs"
TIMEOUT_PER_JOB = 900
CLIENT_ID = "zero-memory-replay-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def default_host() -> str:
    gw = subprocess.check_output(
        ["bash", "-lc", "ip route | awk '/default/ {print $3; exit}'"],
        text=True,
    ).strip()
    return f"http://{gw}:8000"


HOST = os.environ.get("COMFY_HOST", default_host()).rstrip("/")


def api_get(path: str, timeout: int = 20):
    with urllib.request.urlopen(HOST + path, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def api_post(path: str, payload: dict, timeout: int = 20):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        HOST + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def load_template(name: str) -> dict:
    with open(API / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def output_paths_from_history(prompt_id: str) -> list[Path]:
    hist = api_get(f"/history/{prompt_id}", timeout=30)
    rec = hist[prompt_id]
    out_paths: list[Path] = []
    for _node_id, node_out in rec.get("outputs", {}).items():
        for img in node_out.get("images", []):
            typ = img.get("type", "output")
            root = COMFY_OUTPUT if typ == "output" else COMFY_INPUT
            sub = img.get("subfolder") or ""
            out_paths.append(root / sub / img["filename"])
    return out_paths


def queue_template(name: str, label: str, run_dir: Path, edits=None) -> dict:
    prompt = load_template(name)
    if edits:
        edits(prompt)
    client_id = CLIENT_ID + "-" + label
    resp = api_post("/prompt", {"prompt": prompt, "client_id": client_id}, timeout=30)
    prompt_id = resp["prompt_id"]
    start = time.time()
    while time.time() - start < TIMEOUT_PER_JOB:
        try:
            hist = api_get(f"/history/{prompt_id}", timeout=20)
            if prompt_id in hist:
                paths = output_paths_from_history(prompt_id)
                record = {
                    "label": label,
                    "template": name,
                    "prompt_id": prompt_id,
                    "client_id": client_id,
                    "outputs": [str(p) for p in paths],
                    "elapsed_sec": round(time.time() - start, 1),
                }
                save_json(run_dir / "history" / f"{label}_{prompt_id}.json", hist)
                print("DONE", label, prompt_id, len(paths), flush=True)
                return record
        except Exception as e:
            print("WAIT_ERR", label, repr(e), flush=True)
        time.sleep(3)
    raise TimeoutError(f"Timed out waiting for {label} {prompt_id}")


def copy_to_input(src: Path, input_name: str, run_dir: Path) -> Path:
    if not src.exists():
        raise FileNotFoundError(src)
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)
    dst = COMFY_INPUT / input_name
    shutil.copy2(src, dst)
    copied = run_dir / "inputs_copied" / input_name
    copied.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, copied)
    print("COPY_INPUT", src, "->", dst, flush=True)
    return dst


def make_contact_sheet(image_paths: list[Path], out: Path, title: str):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        print("CONTACT_SKIP", title, repr(e), flush=True)
        return
    thumbs = []
    cell_w, cell_h = 360, 520
    label_h = 40
    for p in image_paths:
        if not p.exists():
            continue
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (235, 235, 235, 255))
        bg.alpha_composite(im)
        bg.thumbnail((cell_w, cell_h - label_h), Image.LANCZOS)
        canvas = Image.new("RGB", (cell_w, cell_h), "white")
        x = (cell_w - bg.width) // 2
        y = label_h + (cell_h - label_h - bg.height) // 2
        canvas.paste(bg.convert("RGB"), (x, y))
        d = ImageDraw.Draw(canvas)
        label = p.name[:48]
        d.text((8, 8), label, fill=(0, 0, 0))
        thumbs.append(canvas)
    if not thumbs:
        return
    cols = min(4, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h + 40), "white")
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), title, fill=(0, 0, 0))
    for i, im in enumerate(thumbs):
        x = (i % cols) * cell_w
        y = 40 + (i // cols) * cell_h
        sheet.paste(im, (x, y))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print("CONTACT", out, flush=True)


def edit_prefix(prefix: str):
    def _edit(prompt: dict):
        for node in prompt.values():
            if node.get("class_type") == "SaveImage":
                node["inputs"]["filename_prefix"] = prefix
    return _edit


def main():
    run_dir = RUN_ROOT / ("zero_memory_replay_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "host": HOST,
        "client_id_base": CLIENT_ID,
        "run_dir": str(run_dir),
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "jobs": [],
        "notes": [],
    }
    print("HOST", HOST, flush=True)
    stats = api_get("/system_stats", timeout=10)
    queue = api_get("/queue", timeout=10)
    manifest["system_stats_probe"] = stats
    manifest["initial_queue"] = queue
    if queue.get("queue_running") or queue.get("queue_pending"):
        save_json(run_dir / "run_manifest_partial.json", manifest)
        raise SystemExit("Shared ComfyUI queue is not empty; refusing to start without interrupting/clearing.")

    # 01 selected anchor
    rec = queue_template(
        "01_character_anchor_seed719238043_api.json",
        "01_anchor_seed719238043",
        run_dir,
        edit_prefix("hermes_vn_zero_memory_replay/01_anchor_seed719238043"),
    )
    manifest["jobs"].append(rec)
    anchor = Path(rec["outputs"][0])
    copy_to_input(anchor, "hermes_other_auburn_seed719238043.png", run_dir)
    copy_to_input(anchor, "hermes_expr_auburn_neutral.png", run_dir)
    copy_to_input(anchor, "hermes_refregen_identity_auburn_719238043.png", run_dir)

    # 02 alpha selected
    rec = queue_template(
        "02_alpha_toonout_o0_b0_ref0_api.json",
        "02_alpha_anchor_o0_b0_ref0",
        run_dir,
        edit_prefix("hermes_vn_zero_memory_replay/02_alpha_anchor_o0_b0_ref0"),
    )
    manifest["jobs"].append(rec)

    # 03 expressions selected set
    expr_templates = [
        ("03_expression_source_smile_keep_d0p42_w0p6_api.json", "smile", "hermes_expr_selected_smile.png"),
        ("03_expression_source_surprised_move_d0p54_w0p48_api.json", "surprised", "hermes_expr_selected_surprised.png"),
        ("03_expression_source_sad_strong_move_d0p56_w0p45_api.json", "sad", "hermes_expr_selected_sad.png"),
        ("03_expression_source_angry_move_d0p54_w0p48_api.json", "angry", "hermes_expr_selected_angry.png"),
    ]
    expr_sources = []
    for tpl, expr, input_name in expr_templates:
        rec = queue_template(
            tpl,
            f"03_expr_source_{expr}",
            run_dir,
            edit_prefix(f"hermes_vn_zero_memory_replay/03_expr_source_{expr}"),
        )
        manifest["jobs"].append(rec)
        p = Path(rec["outputs"][0])
        expr_sources.append(p)
        copy_to_input(p, input_name, run_dir)
    expr_alpha_templates = [
        ("03_expression_alpha_smile_toonout_o0_b0_ref0_api.json", "smile"),
        ("03_expression_alpha_surprised_toonout_o0_b0_ref0_api.json", "surprised"),
        ("03_expression_alpha_sad_toonout_o0_b0_ref0_api.json", "sad"),
        ("03_expression_alpha_angry_toonout_o0_b0_ref0_api.json", "angry"),
    ]
    expr_alphas = []
    for tpl, expr in expr_alpha_templates:
        rec = queue_template(
            tpl,
            f"03_expr_alpha_{expr}",
            run_dir,
            edit_prefix(f"hermes_vn_zero_memory_replay/03_expr_alpha_{expr}"),
        )
        manifest["jobs"].append(rec)
        expr_alphas.append(Path(rec["outputs"][0]))

    # 04 pose donors selected set
    pose_templates = [
        ("04_pose_textonly_source_hand_chest_txt_s1_api.json", "hand_chest", "hermes_pose_selected_hand_chest.png"),
        ("04_pose_textonly_source_hip_txt_s0_api.json", "one_hand_hip", "hermes_pose_selected_one_hand_hip.png"),
        ("04_pose_textonly_source_cross_txt_s0_api.json", "arms_crossed", "hermes_pose_selected_arms_crossed.png"),
    ]
    pose_sources = []
    for tpl, pose, input_name in pose_templates:
        rec = queue_template(
            tpl,
            f"04_pose_source_{pose}",
            run_dir,
            edit_prefix(f"hermes_vn_zero_memory_replay/04_pose_source_{pose}"),
        )
        manifest["jobs"].append(rec)
        p = Path(rec["outputs"][0])
        pose_sources.append(p)
        copy_to_input(p, input_name, run_dir)
        if pose == "one_hand_hip":
            copy_to_input(p, "hermes_refregen_pose_one_hand_hip_source.png", run_dir)
        if pose == "arms_crossed":
            copy_to_input(p, "hermes_refregen_pose_arms_crossed_source.png", run_dir)
    pose_alpha_templates = [
        ("04_pose_alpha_hand_chest_toonout_o0_b0_ref0_api.json", "hand_chest"),
        ("04_pose_alpha_one_hand_hip_toonout_o0_b0_ref0_api.json", "one_hand_hip"),
        ("04_pose_alpha_arms_crossed_toonout_o0_b0_ref0_api.json", "arms_crossed"),
    ]
    pose_alphas = []
    for tpl, pose in pose_alpha_templates:
        rec = queue_template(
            tpl,
            f"04_pose_alpha_{pose}",
            run_dir,
            edit_prefix(f"hermes_vn_zero_memory_replay/04_pose_alpha_{pose}"),
        )
        manifest["jobs"].append(rec)
        pose_alphas.append(Path(rec["outputs"][0]))

    # 05 best pose ref-generation + alpha for two production-direction poses
    ref_templates = [
        ("05_pose_refregen_arms_crossed_d0p42_w0p60_api.json", "arms_crossed"),
        ("05_pose_refregen_one_hand_hip_d0p42_w0p60_api.json", "one_hand_hip"),
    ]
    ref_sources = []
    for tpl, pose in ref_templates:
        rec = queue_template(
            tpl,
            f"05_refgen_{pose}",
            run_dir,
            edit_prefix(f"hermes_vn_zero_memory_replay/05_refgen_{pose}"),
        )
        manifest["jobs"].append(rec)
        p = Path(rec["outputs"][0])
        ref_sources.append(p)
        copy_to_input(p, f"hermes_zero_replay_05_{pose}_source.png", run_dir)
        def edit_alpha(prompt, image_name=f"hermes_zero_replay_05_{pose}_source.png", pose=pose):
            for node in prompt.values():
                if node.get("class_type") == "LoadImage":
                    node["inputs"]["image"] = image_name
                if node.get("class_type") == "SaveImage":
                    node["inputs"]["filename_prefix"] = f"hermes_vn_zero_memory_replay/05_alpha_{pose}_toonout_o0_b0_ref0"
        rec = queue_template(
            "05_alpha_toonout_example_api.json",
            f"05_alpha_{pose}",
            run_dir,
            edit_alpha,
        )
        manifest["jobs"].append(rec)

    all_outputs = [Path(o) for j in manifest["jobs"] for o in j.get("outputs", [])]
    make_contact_sheet([anchor], run_dir / "contact_01_anchor.png", "01 anchor replay")
    make_contact_sheet([Path(manifest["jobs"][1]["outputs"][0])], run_dir / "contact_02_alpha.png", "02 alpha replay")
    make_contact_sheet(expr_sources, run_dir / "contact_03_expression_sources.png", "03 expression source replay")
    make_contact_sheet(expr_alphas, run_dir / "contact_03_expression_alphas.png", "03 expression alpha replay")
    make_contact_sheet(pose_sources, run_dir / "contact_04_pose_sources.png", "04 pose source replay")
    make_contact_sheet(pose_alphas, run_dir / "contact_04_pose_alphas.png", "04 pose alpha replay")
    make_contact_sheet(ref_sources, run_dir / "contact_05_refgen_sources.png", "05 ref-generation replay")
    make_contact_sheet(all_outputs, run_dir / "contact_all_outputs.png", "zero-memory replay all outputs")

    manifest["finished_at"] = datetime.now().isoformat(timespec="seconds")
    manifest["contact_sheets"] = [str(p) for p in sorted(run_dir.glob("contact_*.png"))]
    save_json(run_dir / "run_manifest.json", manifest)
    print("RUN_DIR", run_dir, flush=True)
    print("MANIFEST", run_dir / "run_manifest.json", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FATAL", repr(e), file=sys.stderr, flush=True)
        raise
