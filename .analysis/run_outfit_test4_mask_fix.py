#!/usr/bin/env python3
import json
import os
import shutil
import time
import urllib.request
import urllib.error
import uuid
from pathlib import Path

BASE = 'http://172.28.224.1:8001'
REPO = Path('/home/jisub-lee/workspace/vn-demo')
WF = REPO / 'workflow_packs/renpy_asset_workflows/outfit_variations/outfit_variations_workflow_api.json'
OUT_DIR = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
INPUT_DIR = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
SRC = OUT_DIR / 'hermes_vn_character_anchor/source_featureless_mannequin_base_seed719251139_00001_.png'
RUNTIME_DIR = REPO / '.analysis/comfyui_runtime/outfit_variations_test4_mask_fix'
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
(INPUT_DIR / 'hermes_runtime').mkdir(parents=True, exist_ok=True)

input_name = 'hermes_runtime/source_featureless_mannequin_base_seed719251139_test4.png'
input_path = INPUT_DIR / input_name
shutil.copy2(SRC, input_path)

with WF.open('r', encoding='utf-8') as f:
    base_prompt = json.load(f)

positive_text = (
    'masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, '
    '1girl, solo, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
    'arms_at_sides, straight_posture, pink twin braids, twin braids, long hair, pink hair, pink eyes, '
    'fully clothed, Japanese school uniform, sailor collar, white blouse, navy pleated skirt, red neck ribbon, '
    'long sleeves, knee socks, loafers, coordinated_outfit, highly detailed clothes, opaque clothing, cloth folds, grey_background'
)
negative_text = (
    'nude, nipples, bare chest, bare torso, see-through, transparent clothes, body paint, painted clothes, swimsuit, underwear, '
    'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, '
    'disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digits, fewer digits, different_face, different_hair, '
    'different_hairstyle, different_eye_color, changed_face, changed_hair, cropped, very displeasing, sketch, jpeg artifacts, '
    'signature, watermark, username, conjoined, bad ai-generated, (worst quality, bad quality:1.2), vignette, shadow, depth of field, rim lighting'
)

def post_json(path, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def get_json(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def make_prompt(label, denoise, seed):
    p = json.loads(json.dumps(base_prompt))
    p['3']['inputs']['image'] = input_name
    p['16']['inputs']['expand'] = 24
    p['53']['inputs']['mask1'] = ['17', 0]
    p['23']['inputs']['text'] = positive_text
    p['24']['inputs']['text'] = negative_text
    p['27']['inputs']['seed'] = seed
    p['27']['inputs']['denoise'] = denoise
    p['35']['inputs']['filename_prefix'] = f'hermes_vn_outfit_variation/test4_maskfix_{label}_school_uniform_seed{seed}'
    # Add final edit mask preview for QA.
    p['950'] = {'class_type': 'MaskToImage', 'inputs': {'mask': ['53', 0]}}
    p['951'] = {'class_type': 'SaveImage', 'inputs': {'images': ['950', 0], 'filename_prefix': f'hermes_vn_outfit_variation/test4_maskfix_{label}_editmask_seed{seed}'}}
    # Add source/person alpha mask preview for comparing expanded mask bounds.
    p['952'] = {'class_type': 'MaskToImage', 'inputs': {'mask': ['4', 1]}}
    p['953'] = {'class_type': 'SaveImage', 'inputs': {'images': ['952', 0], 'filename_prefix': f'hermes_vn_outfit_variation/test4_maskfix_{label}_sourcealpha_seed{seed}'}}
    return p

def queue_and_wait(prompt, label):
    client_id = 'hermes-vn-test4-' + uuid.uuid4().hex
    resp = post_json('/prompt', {'prompt': prompt, 'client_id': client_id})
    prompt_id = resp['prompt_id']
    print(f'QUEUED {label} prompt_id={prompt_id}', flush=True)
    start = time.time()
    while True:
        hist = get_json('/history/' + prompt_id)
        if prompt_id in hist:
            item = hist[prompt_id]
            status = item.get('status', {})
            print(f'DONE {label} status={status}', flush=True)
            outputs = []
            for node_id, node_out in item.get('outputs', {}).items():
                for im in node_out.get('images', []):
                    sub = im.get('subfolder') or ''
                    fname = im.get('filename')
                    typ = im.get('type') or 'output'
                    root = OUT_DIR if typ == 'output' else INPUT_DIR
                    outputs.append(str(root / sub / fname))
            return prompt_id, outputs, status
        if time.time() - start > 900:
            raise TimeoutError(f'timeout waiting for {prompt_id}')
        time.sleep(2)

runs = [
    ('A_expand24_bypass18_den100', 1.0, 62019301),
    ('B_expand24_bypass18_den092', 0.92, 62019302),
]
summary = {'source_anchor': str(SRC), 'input_copy': str(input_path), 'workflow_source': str(WF), 'runs': []}
for label, denoise, seed in runs:
    prompt = make_prompt(label, denoise, seed)
    runtime_json = RUNTIME_DIR / f'{label}.json'
    runtime_json.write_text(json.dumps(prompt, indent=2, ensure_ascii=False), encoding='utf-8')
    pid, outputs, status = queue_and_wait(prompt, label)
    summary['runs'].append({'label': label, 'denoise': denoise, 'seed': seed, 'prompt_id': pid, 'runtime_json': str(runtime_json), 'outputs': outputs, 'status': status})

summary_path = RUNTIME_DIR / 'run_summary.json'
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print('\nSUMMARY_JSON')
print(json.dumps(summary, indent=2, ensure_ascii=False))
