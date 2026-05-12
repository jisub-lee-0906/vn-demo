#!/usr/bin/env python3
"""Generate small S01 VN asset candidate batches through the Windows ComfyUI API.

This is intentionally a tiny diagnostic batch, not final asset promotion.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "generated" / "comfyui" / "s01_asset_candidates_2026-05-12"


@dataclass(frozen=True)
class Job:
    asset_id: str
    width: int
    height: int
    batch_size: int
    steps: int
    cfg: float
    sampler: str
    scheduler: str
    positive: str
    negative: str


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


def build_workflow(job: Job, seed: int, prefix: str) -> dict:
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "novaAnimeXL_ilV180.safetensors"},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": job.positive},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": job.negative},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": job.width, "height": job.height, "batch_size": job.batch_size},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": job.steps,
                "cfg": job.cfg,
                "sampler_name": job.sampler,
                "scheduler": job.scheduler,
                "denoise": 1.0,
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0], "filename_prefix": prefix},
        },
    }


def wait_for_history(host: str, prompt_id: str, timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            hist = http_json("GET", f"{host}/history/{prompt_id}", timeout=10)
            if prompt_id in hist:
                return hist[prompt_id]
        except Exception:
            pass
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
    from PIL import Image, ImageDraw, ImageFont

    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((360, 360))
        thumbs.append((p, im.copy()))
    cols = 2 if len(thumbs) <= 4 else 3
    rows = (len(thumbs) + cols - 1) // cols
    cell_w, cell_h = 420, 430
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h + 46), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 12), label, fill=(0, 0, 0))
    for i, (p, im) in enumerate(thumbs):
        x = (i % cols) * cell_w
        y = 46 + (i // cols) * cell_h
        sheet.paste(im, (x + (cell_w - im.width) // 2, y + 8))
        draw.text((x + 10, y + 374), p.name, fill=(0, 0, 0))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def main() -> int:
    host = default_host()
    print(f"host={host}")
    queue = http_json("GET", f"{host}/queue")
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise SystemExit(f"Refusing to submit: ComfyUI queue is not empty: {queue}")

    jobs = [
        Job(
            asset_id="harin_design_candidates",
            width=832,
            height=1216,
            batch_size=4,
            steps=24,
            cfg=6.0,
            sampler="euler_ancestral",
            scheduler="normal",
            positive=(
                "masterpiece, best quality, very aesthetic, newest, 1girl, solo, anime style, "
                "large centered upper body portrait, cowboy shot, full head visible, complete hair visible, "
                "student council audit officer, royal magic academy uniform, neat navy and white academy uniform, "
                "short auburn brown hair, calm sharp blue eyes, composed suspicious expression, serious but attractive, "
                "holding a slim clipboard, restrained fantasy academy design, simple neutral gray background"
            ),
            negative=(
                "text, watermark, logo, ui, dialogue box, multiple girls, duplicate character, character sheet, reference sheet, "
                "sprite sheet, inset, thumbnail portrait, tiny full body, chibi, cropped head, head cut off, huge bow, crown, tiara, "
                "fantasy armor, revealing outfit, extra arms, bad hands, green clothing, fake writing"
            ),
        ),
        Job(
            asset_id="bg_summoning_hall_candidates",
            width=1024,
            height=576,
            batch_size=4,
            steps=22,
            cfg=5.5,
            sampler="euler_ancestral",
            scheduler="normal",
            positive=(
                "empty anime royal magic academy ceremonial hall, no people, wide interior background, "
                "large magic measurement circle on the floor, crystal measurement pedestal near center, tall arched windows, "
                "formal school ceremony atmosphere, clean lower third for dialogue box, no readable writing"
            ),
            negative=(
                "text, watermark, logo, ui, dialogue box, subtitles, captions, readable writing, fake letters, people, students, faces, "
                "crowd, character, messy lower third, book titles, signs"
            ),
        ),
        Job(
            asset_id="cg_measurement_orb_candidates",
            width=1024,
            height=576,
            batch_size=4,
            steps=22,
            cfg=5.5,
            sampler="euler_ancestral",
            scheduler="normal",
            positive=(
                "anime event cg, close view of a crystal magic measurement orb on a pedestal, blue light suddenly going dark, "
                "thin golden line inside the crystal, royal magic academy ceremony table, dramatic but restrained, no people, "
                "clean lower third for dialogue box, no readable writing"
            ),
            negative=(
                "text, watermark, logo, ui, dialogue box, subtitles, captions, readable writing, fake letters, people, hands, faces, "
                "extra objects, messy lower third, horror, blood"
            ),
        ),
        Job(
            asset_id="cg_measurement_orb_dark_refine_candidates",
            width=1024,
            height=576,
            batch_size=4,
            steps=22,
            cfg=5.5,
            sampler="euler_ancestral",
            scheduler="normal",
            positive=(
                "single black crystal orb on a bronze pedestal, unlit magic measurement device, thin golden crack line inside the dark crystal, "
                "faint blue glow fading out, royal magic academy ceremony prop, empty scene, no people, no hands, no interface, "
                "cinematic object close-up, clean lower third, plain background, no readable writing"
            ),
            negative=(
                "text, watermark, logo, ui, interface, dialogue box, subtitle, caption, readable writing, fake letters, game screenshot, "
                "people, hands, face, character, multiple orbs, bright star, glowing blue starburst, messy lower third, blood, horror"
            ),
        ),
    ]

    manifest = {
        "run_id": "s01_asset_candidates_2026-05-12",
        "status": "GENERATED_UNREVIEWED_CANDIDATES",
        "host": host,
        "model": "novaAnimeXL_ilV180.safetensors",
        "note": "Small candidate batch for visual direction only. Do not promote to Ren'Py semantic assets before contact-sheet QA and screenshot QA.",
        "jobs": [],
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "api_workflows").mkdir(exist_ok=True)
    (OUT_ROOT / "contact_sheets").mkdir(exist_ok=True)

    for job in jobs:
        seed = random.randrange(1, 2**31 - 1)
        prefix = f"vn_demo_s01/{job.asset_id}"
        workflow = build_workflow(job, seed, prefix)
        workflow_path = OUT_ROOT / "api_workflows" / f"{job.asset_id}.json"
        workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
        payload = {"prompt": workflow, "client_id": str(uuid4())}
        print(f"submit {job.asset_id} seed={seed}")
        res = http_json("POST", f"{host}/prompt", payload, timeout=30)
        prompt_id = res["prompt_id"]
        hist = wait_for_history(host, prompt_id, timeout_s=900)
        dest = OUT_ROOT / job.asset_id
        files = download_outputs(host, hist, dest)
        sheet = OUT_ROOT / "contact_sheets" / f"{job.asset_id}_sheet.jpg"
        make_contact_sheet(files, sheet, f"{job.asset_id} seed={seed}")
        manifest["jobs"].append(
            {
                "asset_id": job.asset_id,
                "prompt_id": prompt_id,
                "seed": seed,
                "size": [job.width, job.height],
                "batch_size": job.batch_size,
                "steps": job.steps,
                "cfg": job.cfg,
                "sampler": job.sampler,
                "scheduler": job.scheduler,
                "positive": job.positive,
                "negative": job.negative,
                "api_workflow": str(workflow_path.relative_to(ROOT)),
                "files": [str(p.relative_to(ROOT)) for p in files],
                "contact_sheet": str(sheet.relative_to(ROOT)),
            }
        )
        print(f"done {job.asset_id}: {len(files)} files -> {sheet}")

    manifest_path = OUT_ROOT / "RUN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "jobs": len(jobs)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
