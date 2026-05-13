#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_expr_retest_20260513'

SOURCES = {
    '01_fixed': COMFY/'output/hermes_vn_chain_retest_20260513/01_no_depth_volumetric_source_00001_.png',
    '04_arms_crossed': COMFY/'output/hermes_vn_chain_retest_20260513/no_thick_arms_crossed_src_00001_.png',
}
PRESETS = {
    'happy': {
        'tags': 'smile, open_mouth, happy',
        'neg': 'sad, angry, crying, tears, surprised, disgusted, fearful',
        'seed': 719251301,
        'denoise': 0.40,
    },
    'surprised': {
        'tags': 'surprised, wide_eyes, open_mouth, raised_eyebrows',
        'neg': 'smile, happy, angry, disgusted, sad, crying, tears',
        'seed': 719251305,
        'denoise': 0.40,
    },
}
QUALITY = 'masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest'
CHAR = 'rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background'
COMMON_NEG = 'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, dynamic_pose, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, vignette, changed_clothes, different_clothes, different_hair, (worst quality, bad quality:1.2)'
# Note: intentionally removed crossed_arms from negative for 04 compatibility; this is still the same canonical graph/settings, only source-compatible negatives.

def http_json(path: str, payload=None, timeout=30):
    data = None; headers = {}
    if payload is not None:
        data = json.dumps(payload).encode(); headers['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT + path, data=data, headers=headers), timeout=timeout) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}

def submit(prompt: dict, timeout_s=900):
    q = http_json('/queue', timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(f'queue busy: {q}')
    pid = http_json('/prompt', {'prompt': prompt})['prompt_id']
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
    out = []
    for node_id, node in hist.get('outputs', {}).items():
        for img in node.get('images', []):
            out.append({'node': node_id, 'path': str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return out

template = json.loads((ROOT/'03_expression_variation_face_composite/workflow_api/03_expression_source_canonical_api.json').read_text(encoding='utf-8'))
manifest = []
for source_slug, src in SOURCES.items():
    input_rel = f'{RUN}/{src.name}'
    dst = COMFY/'input'/input_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    for expr, preset in PRESETS.items():
        p = json.loads(json.dumps(template))
        p['1']['inputs']['image'] = input_rel
        p['4']['inputs']['seed'] = preset['seed']
        p['6']['inputs']['text'] = f"{QUALITY}, {CHAR}, {preset['tags']}, BREAK depth_of_field, volumetric_lighting"
        p['7']['inputs']['text'] = f"{COMMON_NEG}, {preset['neg']}"
        p['13']['inputs']['seed'] = preset['seed']
        p['13']['inputs']['denoise'] = preset['denoise']
        prefix = f'{RUN}/{source_slug}_{expr}_seed{preset["seed"]}'
        p['15']['inputs']['filename_prefix'] = prefix + '_raw_inpaint'
        p['17']['inputs']['filename_prefix'] = prefix + '_mask_preview'
        p['19']['inputs']['filename_prefix'] = prefix + '_composited'
        pid, hist = submit(p)
        manifest.append({
            'source_slug': source_slug,
            'source_path': str(src),
            'input_image': input_rel,
            'expression': expr,
            'prompt_id': pid,
            'positive': p['6']['inputs']['text'],
            'negative': p['7']['inputs']['text'],
            'denoise': preset['denoise'],
            'seed': preset['seed'],
            'outputs': outputs(hist),
        })
mp = COMFY/'output'/RUN/'manifest_current_03_smoke.json'
mp.parent.mkdir(parents=True, exist_ok=True)
mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'manifest': str(mp), 'items': manifest}, indent=2, ensure_ascii=False))
