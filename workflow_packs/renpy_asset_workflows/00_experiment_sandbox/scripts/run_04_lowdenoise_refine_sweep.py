#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import time
import urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_04_lowdenoise_refine_20260513'
OUTDIR = COMFY / 'output' / RUN
INDIR = COMFY / 'input' / RUN
OUTDIR.mkdir(parents=True, exist_ok=True)
INDIR.mkdir(parents=True, exist_ok=True)

# Best known 04 direct pose+expression draft from the previous quality/style sweep.
DRAFT04 = COMFY / 'output/hermes_vn_04_quality_style_sweep_20260513/04_q01_crisp_ip065_seed719252501_00001_.png'

CHAR_TAGS = 'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_EXPR = 'arms_crossed, crossed_arms, folded_arms, smile, happy, open_mouth, cheerful'
QUALITY_01_STYLE = 'masterpiece, best_quality, amazing_quality, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit'
POSITIVE = f'{QUALITY_01_STYLE}, 1girl, solo, cowboy_shot, standing, looking_at_viewer, {CHAR_TAGS}, {POSE_EXPR}, clean_lineart, crisp_lineart, clean_outline, anime_coloring, detailed_anime_coloring, grey_background'
NEGATIVE = 'lowres, low_quality, worst_quality, bad_quality, very_displeasing, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, fused_fingers, extra_arms, extra_hands, long_body, deformed, mutated, disfigured, ugly, cropped, cropped_head, cropped_hair, out_of_frame, multiple_girls, duplicate_character, text, signature, watermark, username, logo, frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed, large_breasts, huge_breasts, cleavage, nude, nipples, badge, emblem, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, vignette, spotlight, dramatic_lighting, rim_lighting, headwear, hair_ornament, object_above_head'


def http_json(path: str, payload=None, timeout=30):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(ENDPOINT + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def submit(prompt: dict, timeout_s=1200):
    q = http_json('/queue', timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(f'queue busy: {q}')
    pid = http_json('/prompt', {'prompt': prompt}, timeout=30)['prompt_id']
    start = time.time()
    while time.time() - start < timeout_s:
        h = http_json(f'/history/{pid}', timeout=30)
        if pid in h:
            st = h[pid].get('status', {})
            if not st.get('completed'):
                raise RuntimeError(f'failed {pid}: {st}')
            return pid, h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def outputs(hist: dict):
    arr = []
    for nid, node in hist.get('outputs', {}).items():
        for img in node.get('images', []):
            arr.append({'node': nid, 'path': str(COMFY / 'output' / (img.get('subfolder') or '') / img['filename'])})
    return arr


def first(hist: dict, nid: str):
    for item in outputs(hist):
        if item['node'] == nid:
            return item['path']
    raise RuntimeError(outputs(hist))


def make_prompt(input_rel: str, denoise: float, seed: int, prefix_slug: str) -> dict:
    return {
        '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'novaAnimeXL_ilV190.safetensors'}},
        '2': {'class_type': 'CLIPTextEncode', 'inputs': {'clip': ['1', 1], 'text': POSITIVE}},
        '3': {'class_type': 'CLIPTextEncode', 'inputs': {'clip': ['1', 1], 'text': NEGATIVE}},
        '4': {'class_type': 'LoadImage', 'inputs': {'image': input_rel}},
        '5': {'class_type': 'VAEEncode', 'inputs': {'pixels': ['4', 0], 'vae': ['1', 2]}},
        '6': {'class_type': 'KSampler', 'inputs': {
            'model': ['1', 0],
            'positive': ['2', 0],
            'negative': ['3', 0],
            'latent_image': ['5', 0],
            'seed': seed,
            'steps': 28,
            'cfg': 5.0,
            'sampler_name': 'euler_ancestral',
            'scheduler': 'normal',
            'denoise': denoise,
        }},
        '7': {'class_type': 'VAEDecode', 'inputs': {'samples': ['6', 0], 'vae': ['1', 2]}},
        '8': {'class_type': 'SaveImage', 'inputs': {'images': ['7', 0], 'filename_prefix': f'{RUN}/{prefix_slug}'}},
    }


def main():
    if not DRAFT04.exists():
        raise FileNotFoundError(DRAFT04)
    input_name = '04_draft_q01_crisp_ip065.png'
    dst = INDIR / input_name
    shutil.copy2(DRAFT04, dst)
    input_rel = f'{RUN}/{input_name}'
    manifest = {
        'run': RUN,
        'endpoint': ENDPOINT,
        'purpose': '04 direct pose+expression draft -> low-denoise img2img refine sweep, no extra ControlNet. Tests whether 01-like quality prompt can restore finish while preserving pose/expression.',
        'draft04': str(DRAFT04),
        'input_rel': input_rel,
        'positive': POSITIVE,
        'negative': NEGATIVE,
        'variants': [],
    }
    for denoise in [0.25, 0.35, 0.45]:
        seed = 719253000 + int(denoise * 100)
        slug = f'refine_d{int(denoise*100):02d}_seed{seed}'
        prompt = make_prompt(input_rel, denoise, seed, slug)
        wf_path = ROOT / '00_experiment_sandbox' / 'workflow_api' / f'00_04_lowdenoise_refine_{slug}_api.json'
        wf_path.write_text(json.dumps(prompt, indent=2, ensure_ascii=False), encoding='utf-8')
        pid, hist = submit(prompt)
        manifest['variants'].append({
            'slug': slug,
            'denoise': denoise,
            'seed': seed,
            'prompt_id': pid,
            'workflow_api': str(wf_path),
            'output': first(hist, '8'),
        })
    mp = OUTDIR / 'manifest_04_lowdenoise_refine.json'
    mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
