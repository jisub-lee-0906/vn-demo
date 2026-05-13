#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_04_promptonly_original_style_20260513'
OUTDIR = COMFY / 'output' / RUN
OUTDIR.mkdir(parents=True, exist_ok=True)

BASE = ROOT / '01_character_anchor_and_prompt/workflow_api/01_character_anchor_apose_neutral_api.json'
POS = (
    'masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, '
    'ultra-detailed, absurdres, newest, rating_explicit, '
    '1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, '
    'smile, happy, open_mouth, arms_crossed, crossed_arms, folded_arms, '
    'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, '
    'navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, '
    'thick_outline, grey_background'
)
NEG = (
    'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, '
    'deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, '
    'extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, '
    'username, conjoined, bad_ai-generated, expressionless, closed_mouth, frown, angry, annoyed, serious, '
    'stern, pouting, sad, crying, tears, scared, disgusted, surprised, arms_at_sides, hands_on_hips, '
    'hands_in_pockets, hands_near_face, hand_on_chest, large_breasts, huge_breasts, cleavage, nsfw, nude, '
    'nipples, badge, emblem, logo, (worst quality, bad quality:1.2), white_background, bright_background, '
    'gradient_background, patterned_background, black_background, dark_background, vignette'
)
SEEDS = [719251035, 719251136, 719251237, 719251338, 719251439, 719251540]


def http_json(path: str, payload=None, timeout=30):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT + path, data=data, headers=headers), timeout=timeout) as r:
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


def first(hist: dict, nid: str):
    for node_id, node in hist.get('outputs', {}).items():
        for img in node.get('images', []):
            if node_id == nid:
                return str(COMFY / 'output' / (img.get('subfolder') or '') / img['filename'])
    raise RuntimeError(hist.get('outputs', {}))


def main():
    base = json.loads(BASE.read_text(encoding='utf-8'))
    manifest = {
        'run': RUN,
        'endpoint': ENDPOINT,
        'purpose': 'User rejected 04/IPAdapter/low-denoise routes as not preserving original. This test keeps the exact 01 txt2img graph/model/sampler/quality style and changes only pose/expression prompt plus seed hunting.',
        'base_workflow': str(BASE),
        'positive': POS,
        'negative': NEG,
        'variants': [],
    }
    for seed in SEEDS:
        p = json.loads(json.dumps(base))
        p['3']['inputs']['text'] = POS
        p['4']['inputs']['text'] = NEG
        p['6']['inputs']['seed'] = seed
        p['8']['inputs']['filename_prefix'] = f'{RUN}/promptonly_arms_crossed_happy_seed{seed}'
        wf = ROOT / '00_experiment_sandbox/workflow_api' / f'00_04_promptonly_original_style_arms_crossed_seed{seed}_api.json'
        wf.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding='utf-8')
        pid, hist = submit(p)
        manifest['variants'].append({
            'seed': seed,
            'prompt_id': pid,
            'workflow_api': str(wf),
            'output': first(hist, '8'),
        })
    mp = OUTDIR / 'manifest_promptonly_original_style.json'
    mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
