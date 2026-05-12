#!/usr/bin/env python3
"""Canonical reset generation for vn-demo visible VN assets.

Generates fresh candidate batches from the repo-local Ren'Py ComfyUI workflow pack.
No semantic promotion is done here; this script writes generated/comfyui/canonical_reset_YYYYMMDD_HHMMSS.
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
from datetime import datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "workflow_packs" / "renpy_asset_workflows"
API = PACK / "api_workflows"
COMFY_INPUT = Path(os.environ.get("COMFY_INPUT_DIR", "/mnt/c/Users/Desktop/Documents/ComfyUI/input"))
RUN_ID = os.environ.get("RUN_ID") or "canonical_reset_" + datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "generated" / "comfyui" / RUN_ID

QUALITY = "masterpiece, best quality, very aesthetic, newest"
CHAR_NEG = (
    "text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, "
    "out of frame, extra arms, extra hands, bad hands, fused fingers, missing fingers, low quality, "
    "worst quality, full body, tiny full body, tiny character, chibi, character sheet, reference sheet, "
    "sprite sheet, inset, floating head, small extra portrait, profile card, ui, interface, dialogue box, "
    "headwear, object above head, crown, tiara, large ribbon, bow on head, hair ornament, revealing outfit"
)
BG_NEG_BASE = (
    "text, watermark, logo, letters, words, readable writing, fake glyphs, subtitles, captions, "
    "dialogue box, textbox, nameplate, ui, interface, overlay, visual novel screenshot, game screenshot, "
    "people, person, face, hands, students, crowd, messy lower third"
)

@dataclass(frozen=True)
class Txt2ImgJob:
    asset_id: str
    template: str
    workflow_id: str
    positive: str
    negative: str
    seeds: tuple[int, ...]
    width: int | None
    height: int | None
    steps: int | None
    cfg: float | None
    ckpt: str | None
    prefix: str


def host() -> str:
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


def load_template(name: str) -> dict:
    p = API / name
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def apply_txt2img(job: Txt2ImgJob, seed: int, idx: int) -> dict:
    wf = load_template(job.template)
    wf["3"]["inputs"]["text"] = job.positive
    wf["4"]["inputs"]["text"] = job.negative
    wf["6"]["inputs"]["seed"] = seed
    wf["5"]["inputs"]["batch_size"] = 1
    wf["8"]["inputs"]["filename_prefix"] = f"{RUN_ID}/{job.prefix}_s{idx:02d}"
    if job.width is not None:
        wf["5"]["inputs"]["width"] = job.width
    if job.height is not None:
        wf["5"]["inputs"]["height"] = job.height
    if job.steps is not None:
        wf["6"]["inputs"]["steps"] = job.steps
    if job.cfg is not None:
        wf["6"]["inputs"]["cfg"] = job.cfg
    if job.ckpt is not None:
        wf["1"]["inputs"]["ckpt_name"] = job.ckpt
    return wf


def wait_history(h: str, prompt_id: str, timeout_s: int = 900) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        hist = http_json("GET", f"{h}/history/{prompt_id}", timeout=10)
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError(prompt_id)


def download_outputs(h: str, hist: dict, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for node in hist.get("outputs", {}).values():
        for img in node.get("images", []):
            params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
            url = f"{h}/view?{params}"
            out = dest / img["filename"]
            with urllib.request.urlopen(url, timeout=60) as resp, out.open("wb") as f:
                shutil.copyfileobj(resp, f)
            saved.append(out)
    return saved


def contact_sheet(paths: list[Path], out: Path) -> None:
    if not paths:
        return
    cols = 2 if len(paths) <= 4 else 3
    rows = (len(paths) + cols - 1) // cols
    cell_w, cell_h = 520, 560
    args = []
    filters = []
    labels = []
    for i, p in enumerate(paths):
        args += ["-i", str(p)]
        filters.append(f"[{i}:v]scale=480:500:force_original_aspect_ratio=decrease,pad={cell_w}:{cell_h}:(ow-iw)/2:(oh-ih)/2:white[v{i}]")
        labels.append(f"[v{i}]")
    while len(labels) < cols * rows:
        n = len(labels)
        filters.append(f"color=c=white:s={cell_w}x{cell_h}:d=0.1[v{n}]")
        labels.append(f"[v{n}]")
    layout = "|".join(f"{(i%cols)*cell_w}_{(i//cols)*cell_h}" for i in range(cols*rows))
    filters.append("".join(labels) + f"xstack=inputs={cols*rows}:layout={layout}:fill=white[out]")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", *args, "-filter_complex", ";".join(filters), "-map", "[out]", "-frames:v", "1", str(out)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def jobs() -> list[Txt2ImgJob]:
    harin_core = (
        f"{QUALITY}, 1girl, solo, anime style, cowboy shot, upper body character portrait, "
        "waist-up to upper-thigh visible, full head visible, complete hair visible, large centered character, "
        "student council audit officer, composed serious expression, calm sharp blue eyes, "
        "short auburn brown hair, clean face, neat navy and white royal magic academy uniform, "
        "white blouse, navy necktie, navy pleated skirt, restrained academy fantasy design, "
        "relaxed standing pose, clean sharp anime lineart, flat solid medium gray background, plain uniform gray backdrop"
    )
    return [
        Txt2ImgJob("harin_anchor", "01_character_anchor_seed719238043_api.json", "01_character_anchor_and_prompt", harin_core, CHAR_NEG, (719238043,719238047,719238051,719238055), 1152, 1536, 30, 6.0, "novaAnimeXL_ilV125.safetensors", "harin_anchor"),
        Txt2ImgJob("bg_summoning_hall", "06_background_generation_no_text_api.json", "06_background_generation_no_text", "empty anime royal magic academy summoning and measurement hall, no people, clean lower third, wide 16:9 interior background, polished stone floor, large magic measurement circle pattern on the floor, single crystal measurement pedestal near center, tall arched windows, restrained ceremonial academy atmosphere", BG_NEG_BASE + ", readable magic text, posters, signs", (812345211,812345212,812345213,812345214), 1024, 576, 26, 5.5, "novaAnimeXL_ilV180.safetensors", "bg_summoning_hall"),
        Txt2ImgJob("bg_artifact_lab", "06_background_generation_no_text_api.json", "06_background_generation_no_text", "empty anime royal magic academy artifact storage laboratory, no people, clean lower third, wide 16:9 interior background, sealed magical device containment room, stone walls, glass cases, brass instruments, blue safety glow, restrained mysterious academy atmosphere", BG_NEG_BASE + ", labels, book titles, posters, readable runes", (812345321,812345322,812345323,812345324), 1024, 576, 26, 5.5, "novaAnimeXL_ilV180.safetensors", "bg_artifact_lab"),
        Txt2ImgJob("bg_report_room", "06_background_generation_no_text_api.json", "06_background_generation_no_text", "empty anime academy council report room, no people, clean lower third, wide 16:9 interior background, formal desk, high shelves, official seal motif without letters, warm lamplight, quiet serious administrative atmosphere", BG_NEG_BASE + ", documents with readable text, labels, book titles, posters", (812345431,812345432,812345433,812345434), 1024, 576, 26, 5.5, "novaAnimeXL_ilV180.safetensors", "bg_report_room"),
        Txt2ImgJob("cg_measurement_orb", "08_event_cg_no_text_story_beat_api.json", "08_event_cg_no_text_story_beat", f"{QUALITY}, anime event CG, single dark crystal magic measurement orb on a bronze pedestal, blue light fading out, one thin golden crack line inside the dark crystal, royal magic academy ceremony table, quiet suspense, dramatic but restrained, large empty clean foreground in the bottom third for dialogue box, no people, no hands, 16:9 background art, no readable writing", BG_NEG_BASE + ", fake glyphs, handwriting, printed lines, document, notice, poster, sign, label, book page, people, person, girl, boy, face, hand, fingers, multiple orbs, extra crystal, floating paper, blood, horror, bright starburst", (812347511,812347512,812347513,812347514), 1536, 864, 30, 5.5, "novaAnimeXL_ilV180.safetensors", "cg_measurement_orb"),
        Txt2ImgJob("cg_sealed_artifact", "08_event_cg_no_text_story_beat_api.json", "08_event_cg_no_text_story_beat", f"{QUALITY}, anime event CG, sealed ancient magical artifact resting in a containment frame, cracked golden seal ring, blue magic sparks fading, academy artifact laboratory background, quiet danger after an accident, large empty clean foreground in the bottom third for dialogue box, no people, no hands, 16:9 background art, no readable writing", BG_NEG_BASE + ", fake glyphs, handwriting, printed lines, labels, book page, people, person, face, hand, fingers, blood, horror, gore, unreadable runic text", (812347621,812347622,812347623,812347624), 1536, 864, 30, 5.5, "novaAnimeXL_ilV180.safetensors", "cg_sealed_artifact"),
        Txt2ImgJob("cg_special_observation_seal", "08_event_cg_no_text_story_beat_api.json", "08_event_cg_no_text_story_beat", f"{QUALITY}, anime event CG, official magical academy seal stamp glowing on a blank parchment folder, abstract crest with no letters, formal report room desk, warm lamplight, ominous administrative decision, large empty clean foreground in the bottom third for dialogue box, no people, no hands, 16:9 background art, no readable writing", BG_NEG_BASE + ", Korean text, fake glyphs, handwriting, printed lines, readable document, notice, poster, sign, label, book page, face, hand, fingers, blood", (812347731,812347732,812347733,812347734), 1536, 864, 30, 5.5, "novaAnimeXL_ilV180.safetensors", "cg_special_observation_seal"),
    ]


def main() -> int:
    h = host()
    print("host", h)
    print("run", OUT)
    if not PACK.exists():
        raise SystemExit(f"missing workflow pack {PACK}")
    q = http_json("GET", f"{h}/queue", timeout=10)
    if q.get("queue_running") or q.get("queue_pending"):
        raise SystemExit(f"ComfyUI queue not empty: {q}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"api_workflows").mkdir(exist_ok=True)
    (OUT/"contact_sheets").mkdir(exist_ok=True)
    manifest = {"run_id": RUN_ID, "status": "GENERATED_CANDIDATES_PENDING_SELECTION", "host": h, "workflow_pack": str(PACK.relative_to(ROOT)), "jobs": []}
    for job in jobs():
        files=[]; apis=[]; pids=[]
        for idx, seed in enumerate(job.seeds, 1):
            wf = apply_txt2img(job, seed, idx)
            api_path = OUT/"api_workflows"/f"{job.asset_id}_s{idx:02d}_derived_from_{job.workflow_id}.json"
            api_path.write_text(json.dumps(wf, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            apis.append(str(api_path.relative_to(ROOT)))
            print("submit", job.asset_id, seed)
            r = http_json("POST", f"{h}/prompt", {"prompt": wf, "client_id": str(uuid4())}, timeout=30)
            pid = r["prompt_id"]; pids.append(pid)
            hist = wait_history(h, pid)
            files.extend(download_outputs(h, hist, OUT/job.asset_id))
        sheet = OUT/"contact_sheets"/f"{job.asset_id}_sheet.jpg"
        contact_sheet(files, sheet)
        manifest["jobs"].append({"asset_id": job.asset_id, "template": job.template, "workflow_id": job.workflow_id, "seeds": list(job.seeds), "prompt_ids": pids, "positive": job.positive, "negative": job.negative, "api_workflows": apis, "files": [str(p.relative_to(ROOT)) for p in files], "contact_sheet": str(sheet.relative_to(ROOT))})
        print("done", job.asset_id, len(files), sheet)
    mp = OUT/"RUN_MANIFEST.json"
    manifest["manifest_path"] = str(mp.relative_to(ROOT))
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"run_id": RUN_ID, "manifest": str(mp), "out": str(OUT)}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
