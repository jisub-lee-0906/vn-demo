#!/usr/bin/env python3
"""Regenerate S01 VN asset candidates from the canonical Ren'Py ComfyUI workflow pack.

This script intentionally derives every executable workflow from:
C:\\Users\\Desktop\\Documents\\ComfyUI\\workflow_packs\\renpy_asset_workflows

The generated outputs are candidate/contact-sheet QA only. They are not semantic
Ren'Py assets until user selection and screenshot QA.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = Path("/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows")
PACK_API = PACK_ROOT / "api_workflows"
OUT_ROOT = ROOT / "generated" / "comfyui" / "s01_asset_candidates_2026-05-12"
QA_DOC = ROOT / "docs" / "assets" / "s01_asset_candidate_qa_2026-05-12.md"


@dataclass(frozen=True)
class DerivedJob:
    asset_id: str
    base_template: str
    base_workflow_id: str
    purpose: str
    positive: str
    negative: str
    seeds: tuple[int, ...]
    filename_prefix: str
    width: int | None = None
    height: int | None = None
    steps: int | None = None
    cfg: float | None = None
    ckpt_name: str | None = None


def default_host() -> str:
    if os.environ.get("COMFY_HOST"):
        return os.environ["COMFY_HOST"].rstrip("/")
    gw = subprocess.check_output("ip route | awk '/default/ {print $3; exit}'", shell=True, text=True).strip()
    return f"http://{gw}:8000"


def http_json(method: str, url: str, payload: dict | None = None, timeout: int = 30) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8")) if raw else {}


def load_template(filename: str) -> dict:
    path = PACK_API / filename
    if not path.exists():
        raise FileNotFoundError(f"Canonical workflow template not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def derive_workflow(job: DerivedJob, seed: int, variant_index: int) -> dict:
    workflow = load_template(job.base_template)
    workflow["3"]["inputs"]["text"] = job.positive
    workflow["4"]["inputs"]["text"] = job.negative
    workflow["6"]["inputs"]["seed"] = seed
    workflow["5"]["inputs"]["batch_size"] = 1
    workflow["8"]["inputs"]["filename_prefix"] = f"{job.filename_prefix}_s{variant_index:02d}"
    if job.width is not None:
        workflow["5"]["inputs"]["width"] = job.width
    if job.height is not None:
        workflow["5"]["inputs"]["height"] = job.height
    if job.steps is not None:
        workflow["6"]["inputs"]["steps"] = job.steps
    if job.cfg is not None:
        workflow["6"]["inputs"]["cfg"] = job.cfg
    if job.ckpt_name is not None:
        workflow["1"]["inputs"]["ckpt_name"] = job.ckpt_name
    return workflow


def wait_for_history(host: str, prompt_id: str, timeout_s: int = 900) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        hist = http_json("GET", f"{host}/history/{prompt_id}", timeout=10)
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")


def download_outputs(host: str, history_entry: dict, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for node in history_entry.get("outputs", {}).values():
        for img in node.get("images", []):
            params = urllib.parse.urlencode(
                {
                    "filename": img["filename"],
                    "subfolder": img.get("subfolder", ""),
                    "type": img.get("type", "output"),
                }
            )
            url = f"{host}/view?{params}"
            out = dest / img["filename"]
            with urllib.request.urlopen(url, timeout=60) as resp, out.open("wb") as f:
                shutil.copyfileobj(resp, f)
            saved.append(out)
    return saved


def make_contact_sheet(paths: list[Path], out_path: Path, label: str) -> None:
    """Create a simple contact sheet using ffmpeg only.

    The repo's system Python does not always have Pillow installed, so keep this
    script dependency-light. Filenames and template provenance are recorded in
    RUN_MANIFEST.json; the sheet is for quick visual comparison.
    """
    if not paths:
        raise ValueError(f"No image paths for contact sheet: {label}")
    cols = 2 if len(paths) <= 4 else 3
    rows = (len(paths) + cols - 1) // cols
    cell_w, cell_h = 420, 430
    inputs: list[str] = []
    filters: list[str] = []
    stack_inputs: list[str] = []
    for i, path in enumerate(paths):
        inputs.extend(["-i", str(path)])
        filters.append(
            f"[{i}:v]scale=360:360:force_original_aspect_ratio=decrease,"
            f"pad={cell_w}:{cell_h}:(ow-iw)/2:(oh-ih)/2:white[v{i}]"
        )
        stack_inputs.append(f"[v{i}]")
    while len(stack_inputs) < cols * rows:
        filters.append(f"color=c=white:s={cell_w}x{cell_h}:d=0.1[v{len(stack_inputs)}]")
        stack_inputs.append(f"[v{len(stack_inputs)}]")
    positions = []
    for i in range(cols * rows):
        positions.append(f"{(i % cols) * cell_w}_{(i // cols) * cell_h}")
    filters.append(
        "".join(stack_inputs)
        + f"xstack=inputs={cols * rows}:layout={'|'.join(positions)}:fill=white[out]"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[out]",
        "-frames:v",
        "1",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def jobs() -> list[DerivedJob]:
    return [
        DerivedJob(
            asset_id="harin_anchor_candidates",
            base_template="01_character_anchor_seed719238043_api.json",
            base_workflow_id="01_character_anchor_and_prompt",
            purpose="Harin design/neutral anchor candidates derived from canonical character anchor workflow",
            seeds=(719238043, 719238044, 719238045, 719238046),
            width=1152,
            height=1536,
            steps=28,
            cfg=6.0,
            ckpt_name="novaAnimeXL_ilV125.safetensors",
            filename_prefix="vn_demo_s01_workflowpack/harin_anchor_candidate",
            positive=(
                "masterpiece, best quality, very aesthetic, newest, 1girl, solo, anime style, "
                "cowboy shot, upper body character portrait, waist-up to upper-thigh visible, "
                "full head visible, complete hair visible, large centered character, hands inside canvas, "
                "student council audit officer, composed suspicious expression, calm sharp blue eyes, "
                "short auburn brown hair, clean face, neat navy and white royal magic academy uniform, "
                "white blouse, navy necktie, navy pleated skirt, restrained academy fantasy design, "
                "holding one slim clipboard, clean sharp anime lineart, flat solid medium gray background, "
                "plain uniform gray backdrop"
            ),
            negative=(
                "text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, "
                "cropped arms, cropped hands, out of frame, extra arms, extra hands, bad hands, low quality, "
                "worst quality, full body, tiny character, chibi, feet visible, shoes, white background, "
                "bright background, gradient background, green background, teal background, green clothes, "
                "green uniform, green hair, teal hair, green highlights, background color bleeding into hair, "
                "headwear, object above head, crown, tiara, large ribbon, bow on head, hair ornament, "
                "reference sheet, character sheet, sprite sheet, inset, profile card, fantasy armor, revealing outfit"
            ),
        ),
        DerivedJob(
            asset_id="bg_summoning_hall_candidates",
            base_template="06_background_generation_no_text_api.json",
            base_workflow_id="06_background_generation_no_text",
            purpose="S01 summoning/measurement hall backgrounds derived from canonical no-text background workflow",
            seeds=(812345101, 812345102, 812345103, 812345104),
            width=1024,
            height=576,
            steps=24,
            cfg=5.5,
            filename_prefix="vn_demo_s01_workflowpack/bg_summoning_hall",
            positive=(
                "empty anime royal magic academy ceremonial hall, no people, clean lower third, "
                "wide 16:9 interior background, large magic measurement circle on the floor, "
                "single crystal measurement pedestal near center, tall arched windows, formal academy ceremony atmosphere, "
                "architectural environment only, no readable writing"
            ),
            negative=(
                "text, ui, people, watermark, logo, dialogue box, textbox, subtitles, captions, letters, words, "
                "readable writing, fake glyphs, signs, nameplate, interface, overlay, visual novel screenshot, "
                "game screenshot, students, crowd, face, character, hands, messy lower third, book titles"
            ),
        ),
        DerivedJob(
            asset_id="cg_measurement_orb_candidates",
            base_template="08_event_cg_no_text_story_beat_api.json",
            base_workflow_id="08_event_cg_no_text_story_beat",
            purpose="S01 measurement orb event CG derived from canonical no-text story-beat CG workflow",
            seeds=(812347501, 812347502, 812347503, 812347504),
            width=1536,
            height=864,
            steps=30,
            cfg=5.5,
            filename_prefix="vn_demo_s01_workflowpack/cg_measurement_orb",
            positive=(
                "masterpiece, best quality, very aesthetic, newest, anime event CG, "
                "single dark crystal magic measurement orb on a bronze pedestal, blue light fading out, "
                "one thin golden crack line inside the dark crystal, royal magic academy ceremony table, "
                "quiet suspense, dramatic but restrained, large empty clean foreground in the bottom third for dialogue box, "
                "no people, no hands, 16:9 background art, no readable writing"
            ),
            negative=(
                "text, watermark, logo, letters, words, readable writing, fake glyphs, handwriting, printed lines, "
                "document, notice, poster, sign, label, book page, subtitles, captions, dialogue box, textbox, "
                "nameplate, ui, interface, overlay, visual novel screenshot, game screenshot, people, person, "
                "girl, boy, face, hand, fingers, multiple orbs, extra crystal, floating paper, blood, horror, "
                "bright starburst, messy lower third, impossible perspective"
            ),
        ),
    ]


def write_qa_doc(manifest: dict) -> None:
    lines = [
        "# S01 asset candidate QA (workflow-pack derived)",
        "",
        "Status: GENERATED_UNREVIEWED_CANDIDATES",
        "",
        "This replaces the earlier ad-hoc S01 candidate batch. The previous generated assets were discarded, and this run was regenerated from the canonical Windows ComfyUI workflow pack.",
        "",
        "Workflow pack source:",
        "- Windows: `C:\\Users\\Desktop\\Documents\\ComfyUI\\workflow_packs\\renpy_asset_workflows`",
        "- WSL: `/mnt/c/Users/Desktop/Documents/ComfyUI/workflow_packs/renpy_asset_workflows`",
        "",
        "Run manifest:",
        f"- `{Path(manifest['manifest_path']).relative_to(ROOT)}`",
        "",
        "Contact sheets:",
    ]
    for job in manifest["jobs"]:
        lines.append(f"- `{job['asset_id']}`: `{job['contact_sheet']}`")
    lines.extend(
        [
            "",
            "Derived templates:",
        ]
    )
    for job in manifest["jobs"]:
        lines.append(
            f"- `{job['asset_id']}` derived from `{job['base_workflow_id']}` / `{job['base_template']}`"
        )
    lines.extend(
        [
            "",
            "QA gate:",
            "- Candidate/contact-sheet review only.",
            "- Do not promote any file into `demo/game/images/...` before user selection and Ren'Py screenshot QA.",
            "- Character candidates are design/anchor candidates, not expression/pose-ready sprites yet.",
            "- Background and CG candidates still need textbox readability and fake-text inspection at full size.",
            "",
            "Next step:",
            "1. User selects a Harin anchor direction from the contact sheet.",
            "2. Generate transparent neutral/suspicious sprite candidates from the chosen anchor using the workflow pack's alpha/expression route.",
            "3. Select a summoning hall and measurement-orb candidate, then run Ren'Py screenshot QA before semantic promotion.",
            "",
        ]
    )
    QA_DOC.parent.mkdir(parents=True, exist_ok=True)
    QA_DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    host = default_host()
    print(f"host={host}")
    print(f"workflow_pack={PACK_ROOT}")
    if not PACK_ROOT.exists():
        raise SystemExit(f"Missing canonical workflow pack: {PACK_ROOT}")
    queue = http_json("GET", f"{host}/queue")
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise SystemExit(f"Refusing to submit: ComfyUI queue is not empty: {queue}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "api_workflows").mkdir(exist_ok=True)
    (OUT_ROOT / "contact_sheets").mkdir(exist_ok=True)

    manifest = {
        "run_id": "s01_asset_candidates_2026-05-12",
        "status": "GENERATED_UNREVIEWED_CANDIDATES",
        "host": host,
        "workflow_pack_wsl": str(PACK_ROOT),
        "workflow_pack_windows": "C:\\Users\\Desktop\\Documents\\ComfyUI\\workflow_packs\\renpy_asset_workflows",
        "policy": "All executable workflows are derived from canonical workflow-pack API templates; outputs are candidate QA only.",
        "jobs": [],
    }

    for job in jobs():
        all_files: list[Path] = []
        derived_workflows: list[str] = []
        prompt_ids: list[str] = []
        for i, seed in enumerate(job.seeds, start=1):
            workflow = derive_workflow(job, seed=seed, variant_index=i)
            workflow_path = OUT_ROOT / "api_workflows" / f"{job.asset_id}_s{i:02d}_derived_from_{job.base_workflow_id}.json"
            workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            derived_workflows.append(str(workflow_path.relative_to(ROOT)))
            print(f"submit {job.asset_id} seed={seed} template={job.base_template}")
            res = http_json("POST", f"{host}/prompt", {"prompt": workflow, "client_id": str(uuid4())}, timeout=30)
            prompt_id = res["prompt_id"]
            prompt_ids.append(prompt_id)
            hist = wait_for_history(host, prompt_id, timeout_s=900)
            files = download_outputs(host, hist, OUT_ROOT / job.asset_id)
            all_files.extend(files)
        sheet = OUT_ROOT / "contact_sheets" / f"{job.asset_id}_sheet.jpg"
        make_contact_sheet(all_files, sheet, f"{job.asset_id} derived from {job.base_workflow_id}")
        manifest["jobs"].append(
            {
                "asset_id": job.asset_id,
                "purpose": job.purpose,
                "base_template": job.base_template,
                "base_workflow_id": job.base_workflow_id,
                "seeds": list(job.seeds),
                "prompt_ids": prompt_ids,
                "positive": job.positive,
                "negative": job.negative,
                "derived_api_workflows": derived_workflows,
                "files": [str(p.relative_to(ROOT)) for p in all_files],
                "contact_sheet": str(sheet.relative_to(ROOT)),
            }
        )
        print(f"done {job.asset_id}: {len(all_files)} files -> {sheet}")

    manifest_path = OUT_ROOT / "RUN_MANIFEST.json"
    manifest["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_qa_doc(manifest)
    final_queue = http_json("GET", f"{host}/queue")
    if final_queue.get("queue_running") or final_queue.get("queue_pending"):
        raise SystemExit(f"Generation completed but queue is not empty: {final_queue}")
    print(json.dumps({"manifest": str(manifest_path), "qa_doc": str(QA_DOC), "jobs": len(manifest["jobs"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
